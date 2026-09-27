#!/usr/bin/env python3
"""Converte estrutura OSM projetada para coordenadas Blender usando georef_fit.json.

O resultado continua sendo somente referência. Não altera .blend.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

SUPPORTED_STRUCTURE_SCHEMAS = {
    "bay-of-all-saints/osm-structure-v1",
    "bay-of-all-saints/osm-structure-v2",
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def transform_point(point: list[float], fit: dict) -> list[float]:
    x, y = float(point[0]), float(point[1])
    scale = float(fit["scale_blender_units_per_meter"])
    theta = math.radians(float(fit["rotation_epsg3857_to_blender_deg"]))
    tx, ty = fit["translation_blender"]
    c, s = math.cos(theta), math.sin(theta)
    bx = scale * (c * x - s * y) + tx
    by = scale * (s * x + c * y) + ty
    return [bx, by]


def main() -> int:
    parser = argparse.ArgumentParser(description="Transforma referência estrutural EPSG:3857 para XY do Blender.")
    parser.add_argument("--structure", type=Path, required=True)
    parser.add_argument("--fit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--allow-weak-fit", action="store_true")
    args = parser.parse_args()

    structure = load_json(args.structure)
    if structure.get("schema") not in SUPPORTED_STRUCTURE_SCHEMAS:
        raise SystemExit(f"schema estrutural não suportado: {structure.get('schema')}")
    fit_report = load_json(args.fit)
    robust = fit_report.get("robust_fit")
    quality = fit_report.get("quality")
    if not robust:
        raise SystemExit("georef_fit.json não contém robust_fit")
    if quality not in {"candidate", "strong_candidate"} and not args.allow_weak_fit:
        raise SystemExit(f"fit geográfico fraco/insuficiente: {quality}; use --allow-weak-fit apenas para diagnóstico")

    transformed = []
    for feature in structure.get("features", []):
        item = {
            "osm_type": feature["osm_type"],
            "osm_id": feature["osm_id"],
            "layer": feature["layer"],
            "closed": feature.get("closed", False),
            "node_refs": feature.get("node_refs", []),
            "missing_node_ref_count": feature.get("missing_node_ref_count", 0),
            "blender_xy": [transform_point(p, robust) for p in feature.get("epsg3857", [])],
            "metrics": feature.get("metrics", {}),
            "tags": feature.get("tags", {}),
        }
        for key in ("relation_part_index", "member_way_ids", "relation_hole_count"):
            if key in feature:
                item[key] = feature[key]
        transformed.append(item)

    payload = {
        "schema": "bay-of-all-saints/blender-structure-reference-v2",
        "source_structure": str(args.structure),
        "source_structure_schema": structure.get("schema"),
        "source_fit": str(args.fit),
        "fit_quality": quality,
        "fit_status": fit_report.get("status"),
        "fit_summary": {
            "anchor_count": robust.get("anchor_count"),
            "meters_per_blender_unit": robust.get("meters_per_blender_unit"),
            "rotation_epsg3857_to_blender_deg": robust.get("rotation_epsg3857_to_blender_deg"),
            "rms_residual_blender_units": robust.get("rms_residual_blender_units"),
            "max_residual_blender_units": robust.get("max_residual_blender_units"),
        },
        "features": transformed,
        "notes": [
            "Arquivo de sobreposição estrutural; não é geometria final.",
            "OSM IDs, node_refs e metadados de relações multipolygon são preservados para auditoria/correção rastreável.",
            "Relações com holes não devem ser preenchidas cegamente: relation_hole_count sinaliza necessidade de revisão.",
            "Não promover correções automáticas enquanto o fit não estiver manualmente validado.",
        ],
    }
    write_json(args.output, payload)
    print(json.dumps({"features": len(transformed), "fit_quality": quality, **payload["fit_summary"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
