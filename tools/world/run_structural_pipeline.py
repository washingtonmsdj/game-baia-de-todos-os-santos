#!/usr/bin/env python3
"""Orquestra o pipeline estrutural sem esconder os artefatos intermediários.

Entrada mínima: map.osm + georef_hints.json.
Opcional: terrain.tif para auditoria DEM, cobertura DEM↔janela da captura e perfis viários.
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


def resolve_capture_bounds_source(osm: Path, explicit: Path | None) -> Path | None:
    if explicit is not None:
        source = explicit.resolve()
        if not source.is_file():
            raise SystemExit(f"fonte de bounds da captura não encontrada: {source}")
        return source
    sibling_manifest = osm.parent / "manifest.json"
    return sibling_manifest if sibling_manifest.is_file() else None


def main() -> int:
    parser = argparse.ArgumentParser(description="Executa OSM -> QA topológico/DEM -> fit geográfico -> referência Blender.")
    parser.add_argument("--osm", type=Path, required=True)
    parser.add_argument("--capture-id", help="ID registrado da captura para proveniência de trânsito")
    parser.add_argument("--hints", type=Path, required=True)
    parser.add_argument("--dem", type=Path)
    parser.add_argument("--capture-bounds-source", type=Path, help="manifest/source_summary/area.json; por padrão usa manifest.json ao lado do map.osm")
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

    capture_bounds_source = resolve_capture_bounds_source(osm, args.capture_bounds_source)

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
    dem_coverage_target_kind = None
    if dem is not None:
        coverage_command = [
            sys.executable,
            str(root / "tools/terrain/compare_dem_osm_coverage.py"),
            "--dem-audit", str(dem_audit),
            "--structure", str(structure),
            "--output", str(dem_osm_coverage),
            "--minimum-margin-m", str(args.dem_osm_minimum_margin_m),
        ]
        if capture_bounds_source is not None:
            coverage_command.extend(["--capture-bounds-source", str(capture_bounds_source)])
        else:
            print("WARNING: manifest/source bounds não encontrados; gate DEM usará bbox OSM completo, que pode ser inflado por ways completos.")

        returncode = run(
            coverage_command,
            "QA de cobertura DEM <-> janela estrutural",
            allowed_returncodes={0, 2} if args.allow_insufficient_dem_coverage else {0},
        )
        coverage_data = json.loads(dem_osm_coverage.read_text(encoding="utf-8"))
        dem_coverage_status = coverage_data.get("status")
        dem_coverage_target_kind = (coverage_data.get("target") or {}).get("kind")
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

    # Expandir a área também exige preservar semântica de trânsito e ônibus.
    # Estes arquivos são referência; não geram faixas ou autorizam geometria.
    road_graph = output_dir / "road_graph.json"
    transport_source = output_dir / "osm_transport_reference.json"
    run([sys.executable, str(root / "tools/world/build_road_graph.py"),
         "--structure", str(structure), "--fit", str(fit),
         "--output", str(road_graph)], "Grafo viário de referência")
    transport_command = [sys.executable, str(root / "tools/world/extract_osm_transport.py"),
                         "--osm", str(osm), "--graph", str(road_graph),
                         "--output", str(transport_source)]
    if args.capture_id:
        transport_command.extend(["--capture-id", args.capture_id])
    run(transport_command, "Sentidos, faixas, restrições e transporte coletivo OSM")

    topology_data = json.loads(topology.read_text(encoding="utf-8"))
    summary = {
        "output_dir": str(output_dir),
        "osm_structure": str(structure),
        "osm_topology_audit": str(topology),
        "georef_fit": str(fit),
        "structural_reference": str(reference),
        "road_graph": str(road_graph),
        "osm_transport_reference": str(transport_source),
        "transport_approval": "reference_only_widths_directions_lanes_and_bus_pending_scene_qa",
        "dem_audit": str(dem_audit) if dem else None,
        "dem_osm_coverage": str(dem_osm_coverage) if dem else None,
        "dem_coverage_status": dem_coverage_status,
        "dem_coverage_target_kind": dem_coverage_target_kind,
        "capture_bounds_source": str(capture_bounds_source) if capture_bounds_source else None,
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
