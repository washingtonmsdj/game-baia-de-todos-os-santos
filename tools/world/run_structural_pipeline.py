#!/usr/bin/env python3
"""Orquestra o pipeline estrutural sem esconder os artefatos intermediários.

Entrada mínima: map.osm + georef_hints.json.
Opcional: terrain.tif para auditoria de DEM.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def run(command: list[str], label: str) -> None:
    print(f"\n== {label} ==")
    print("$ " + " ".join(command))
    subprocess.run(command, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Executa extração OSM → fit geográfico → referência Blender.")
    parser.add_argument("--osm", type=Path, required=True)
    parser.add_argument("--hints", type=Path, required=True)
    parser.add_argument("--dem", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/structural-pipeline"))
    parser.add_argument("--min-anchors", type=int, default=4)
    parser.add_argument("--max-residual", type=float, default=8.0)
    parser.add_argument("--target-rms", type=float, default=3.0)
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

    structure = output_dir / "osm_structure.json"
    fit = output_dir / "georef_fit.json"
    reference = output_dir / "structural_reference.json"
    dem_audit = output_dir / "dem_audit.json"

    if args.dem:
        dem = args.dem.resolve()
        if not dem.is_file():
            raise SystemExit(f"terrain.tif/DEM não encontrado: {dem}")
        run([
            sys.executable,
            str(root / "tools/terrain/audit_dem.py"),
            "--dem", str(dem),
            "--output", str(dem_audit),
        ], "Auditoria do DEM")

    run([
        sys.executable,
        str(root / "tools/world/extract_osm_structure.py"),
        "--osm", str(osm),
        "--output", str(structure),
    ], "Extração estrutural OSM")

    run([
        sys.executable,
        str(root / "tools/georef/solve_osm_blender_fit.py"),
        "--hints", str(hints),
        "--osm", str(osm),
        "--output", str(fit),
        "--min-anchors", str(args.min_anchors),
        "--max-residual", str(args.max_residual),
        "--target-rms", str(args.target_rms),
    ], "Fit OSM → Blender")

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

    summary = {
        "output_dir": str(output_dir),
        "osm_structure": str(structure),
        "georef_fit": str(fit),
        "structural_reference": str(reference),
        "dem_audit": str(dem_audit) if args.dem else None,
        "fit_quality": quality,
        "next_step": "importar structural_reference.json com tools/blender/import_structural_reference.py",
    }
    print("\n== Pipeline concluído ==")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
