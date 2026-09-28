#!/usr/bin/env python3
"""Orquestra o pipeline estrutural sem esconder os artefatos intermediários.

Entrada mínima: map.osm + georef_hints.json.
Opcional: terrain.tif para auditoria DEM, cobertura DEM↔OSM e perfis viários.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def run(command: list[str], label: str, allowed_returncodes: set[int] | None = None) -> int:
    print(f"\n== {label} ==")
    print("$ " + " ".join(command))
    completed = subprocess.run(command)
    allowed = allowed_returncodes or {0}
    if completed.returncode not in allowed:
        print(f"ERROR: {label} retornou código {completed.returncode}.", file=sys.stderr)
        raise SystemExit(completed.returncode)
    return completed.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Executa OSM -> QA topológico/DEM -> fit geográfico -> referência Blender.")
    parser.add_argument("--osm", type=Path, required=True)
    parser.add_argument("--hints", type=Path, required=True)
    parser.add_argument("--dem", type=Path)
    parser.add_argument("--dem-statistics", action="store_true", help="calcula estatísticas verticais no audit do DEM")
    parser.add_argument("--audit-road-profiles", action="store_true", help="requer --dem e rasterio")
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/structural-pipeline"))
    parser.add_argument("--min-anchors", type=int, default=4)
    parser.add_argument("--max-residual", type=float, default=8.0)
    parser.add_argument("--target-rms", type=float, default=3.0)
    parser.add_argument("--boundary-margin-m", type=float, default=15.0)
    parser.add_argument("--near-miss-m", type=float, default=1.5)
    parser.add_argument("--dem-osm-minimum-margin-m", type=float, default=20.0)
    parser.add_argument("--allow-insufficient-dem-coverage", action="store_true", help="diagnóstico somente; não transforma falta de cobertura em dado válido")
    parser.add_argument("--allow-weak-fit", action="store_true")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    osm = args.osm.resolve()
    hints = args.hints.resolve()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    if not osm.is_file():
        raise SystemExit(f"map.osm não encontrado: {osm}")
    if not hints.is_file():
        raise SystemExit(f"georef_hints.json não encontrado: {hints}")
    if args.audit_road_profiles and not args.dem:
        raise SystemExit("--audit-road-profiles exige --dem")
    if args.dem_statistics and not args.dem:
        raise SystemExit("--dem-statistics exige --dem")
    if args.dem_osm_minimum_margin_m < 0:
        raise SystemExit("--dem-osm-minimum-margin-m não pode ser negativo")

    structure = output_dir / "osm_structure.json"
    topology = output_dir / "osm_topology_audit.json"
    fit = output_dir / "georef_fit.json"
    reference = output_dir / "structural_reference.json"
    dem_audit = output_dir / "dem_audit.json"
    dem_osm_coverage = output_dir / "dem_osm_coverage.json"
    road_profiles = output_dir / "dem_road_profiles.json"

    dem = None
    if args.dem:
        dem = args.dem.resolve()
        if not dem.is_file():
            raise SystemExit(f"terrain.tif/DEM não encontrado: {dem}")
        command = [
            sys.executable,
            str(root / "tools/terrain/audit_dem.py"),
            "--dem", str(dem),
            "--output", str(dem_audit),
        ]
        if args.dem_statistics:
            command.append("--statistics")
        run(command, "Auditoria do DEM")

    run([
        sys.executable,
        str(root / "tools/world/extract_osm_structure.py"),
        "--osm", str(osm),
        "--output", str(structure),
    ], "Extração estrutural OSM")

    dem_coverage_status = None
    if dem is not None:
        returncode = run([
            sys.executable,
            str(root / "tools/terrain/compare_dem_osm_coverage.py"),
            "--dem-audit", str(dem_audit),
            "--structure", str(structure),
            "--output", str(dem_osm_coverage),
            "--minimum-margin-m", str(args.dem_osm_minimum_margin_m),
        ], "QA de cobertura DEM <-> OSM", allowed_returncodes={0, 2} if args.allow_insufficient_dem_coverage else {0})
        coverage_data = json.loads(dem_osm_coverage.read_text(encoding="utf-8"))
        dem_coverage_status = coverage_data.get("status")
        if returncode == 2:
            print("WARNING: cobertura DEM insuficiente mantida apenas para diagnóstico por opção explícita.")

    run([
        sys.executable,
        str(root / "tools/world/audit_osm_topology.py"),
        "--structure", str(structure),
        "--output", str(topology),
        "--boundary-margin-m", str(args.boundary_margin_m),
        "--near-miss-m", str(args.near_miss_m),
    ], "QA topológico OSM")

    if args.audit_road_profiles and dem is not None:
        if dem_coverage_status == "insufficient" and not args.allow_insufficient_dem_coverage:
            raise SystemExit("Cobertura DEM insuficiente; QA de perfis não deve extrapolar o raster.")
        run([
            sys.executable,
            str(root / "tools/terrain/audit_road_profiles.py"),
            "--dem", str(dem),
            "--structure", str(structure),
            "--output", str(road_profiles),
        ], "QA do DEM sob as vias")

    run([
        sys.executable,
        str(root / "tools/georef/solve_osm_blender_fit.py"),
        "--hints", str(hints),
        "--osm", str(osm),
        "--output", str(fit),
        "--min-anchors", str(args.min_anchors),
        "--max-residual", str(args.max_residual),
        "--target-rms", str(args.target_rms),
    ], "Fit OSM -> Blender")

    fit_data = json.loads(fit.read_text(encoding="utf-8"))
    quality = fit_data.get("quality")
    if quality not in {"candidate", "strong_candidate"} and not args.allow_weak_fit:
        raise SystemExit(f"Fit não atingiu gate mínimo: {quality}. Referência Blender não será gerada.")

    command = [
        sys.executable,
        str(root / "tools/world/build_blender_structure_reference.py"),
        "--structure", str(structure),
        "--fit", str(fit),
        "--output", str(reference),
    ]
    if args.allow_weak_fit:
        command.append("--allow-weak-fit")
    run(command, "Geração da referência estrutural Blender")

    topology_data = json.loads(topology.read_text(encoding="utf-8"))
    summary = {
        "output_dir": str(output_dir),
        "osm_structure": str(structure),
        "osm_topology_audit": str(topology),
        "georef_fit": str(fit),
        "structural_reference": str(reference),
        "dem_audit": str(dem_audit) if dem else None,
        "dem_osm_coverage": str(dem_osm_coverage) if dem else None,
        "dem_coverage_status": dem_coverage_status,
        "dem_road_profiles": str(road_profiles) if args.audit_road_profiles else None,
        "fit_quality": quality,
        "topology_review_items": (topology_data.get("summary") or {}).get("review_items"),
        "next_step": "revisar QA topológico/DEM/fit e importar structural_reference.json no Blender",
    }
    print("\n== Pipeline concluído ==")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
