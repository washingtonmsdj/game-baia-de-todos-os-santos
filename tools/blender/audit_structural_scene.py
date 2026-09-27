# Bay of All Saints — auditoria estrutural da cena Blender
# Uso:
# blender cena.blend --background --python tools/blender/audit_structural_scene.py -- \
#   --output docs/reports/blender/structural_scene_audit.json

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from collections import Counter

import bpy
from mathutils import Vector

CATEGORY_KEYWORDS = {
    "terrain": ("terreno", "relevo", "terrain", "dem", "encosta"),
    "roads": ("rua", "avenida", "via ", "vias", "asfalto", "eixo", "ladeira"),
    "sidewalks": ("calcada", "calçada", "passeio", "travessia", "pedonal", "pedestre"),
    "steps": ("escada", "degrau", "steps"),
    "retaining": ("contencao", "contenção", "muro", "retaining"),
    "waterfront": ("cais", "pier", "píer", "waterfront", "orla"),
    "water": ("mar", "agua", "água", "baia", "baía", "oceano", "water"),
    "buildings": ("edificio", "edifício", "predio", "prédio", "building", "mercado", "palacio", "palácio", "lacerda"),
}


def parse_args():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    return parser.parse_args(argv)


def classify(obj) -> set[str]:
    corpus = " ".join([obj.name] + [collection.name for collection in obj.users_collection]).casefold()
    found = set()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword.casefold() in corpus for keyword in keywords):
            found.add(category)
    return found


def world_bounds(obj):
    if obj.type not in {"MESH", "CURVE", "SURFACE", "META", "FONT"}:
        return None
    try:
        points = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    except Exception:
        return None
    return {
        "min": [min(point[i] for point in points) for i in range(3)],
        "max": [max(point[i] for point in points) for i in range(3)],
    }


def geometry_stats(obj):
    if obj.type == "MESH" and obj.data:
        return {"vertices": len(obj.data.vertices), "edges": len(obj.data.edges), "polygons": len(obj.data.polygons)}
    if obj.type == "CURVE" and obj.data:
        return {"splines": len(obj.data.splines), "points": sum(len(s.points) + len(s.bezier_points) for s in obj.data.splines)}
    return {}


def nonuniform_scale(obj) -> bool:
    values = [abs(float(value)) for value in obj.scale]
    return max(values) - min(values) > 1e-5


def aggregate_bounds(items: list[dict]):
    bounds = [item["bounds"] for item in items if item.get("bounds")]
    if not bounds:
        return None
    return {
        "min": [min(bound["min"][axis] for bound in bounds) for axis in range(3)],
        "max": [max(bound["max"][axis] for bound in bounds) for axis in range(3)],
    }


def main():
    args = parse_args()
    rows = []
    category_rows: dict[str, list[dict]] = {key: [] for key in CATEGORY_KEYWORDS}
    type_counts = Counter()

    for obj in bpy.data.objects:
        categories = classify(obj)
        if not categories:
            continue
        row = {
            "name": obj.name,
            "type": obj.type,
            "categories": sorted(categories),
            "collections": [collection.name for collection in obj.users_collection],
            "location": [float(v) for v in obj.matrix_world.translation],
            "scale": [float(v) for v in obj.scale],
            "nonuniform_scale": nonuniform_scale(obj),
            "bounds": world_bounds(obj),
            "geometry": geometry_stats(obj),
            "modifiers": [modifier.type for modifier in obj.modifiers],
            "hide_render": bool(obj.hide_render),
        }
        rows.append(row)
        type_counts[obj.type] += 1
        for category in categories:
            category_rows[category].append(row)

    categories = {}
    for category, items in category_rows.items():
        categories[category] = {
            "object_count": len(items),
            "bounds_world": aggregate_bounds(items),
            "nonuniform_scale_count": sum(1 for item in items if item["nonuniform_scale"]),
            "mesh_polygons": sum((item.get("geometry") or {}).get("polygons", 0) for item in items),
            "names": [item["name"] for item in items],
        }

    warnings = []
    if not category_rows["terrain"]:
        warnings.append("Nenhum objeto de terreno foi identificado pelos nomes/coleções; revisar nomenclatura ou classificar manualmente.")
    if not category_rows["roads"]:
        warnings.append("Nenhuma via foi identificada pelos nomes/coleções.")
    if not category_rows["water"] and not category_rows["waterfront"]:
        warnings.append("Nenhuma camada de água/waterfront foi identificada pelos nomes/coleções.")

    payload = {
        "schema": "bay-of-all-saints/blender-structural-scene-audit-v1",
        "blend_file": bpy.data.filepath,
        "blender_version": bpy.app.version_string,
        "scene_units": {
            "system": bpy.context.scene.unit_settings.system,
            "scale_length": bpy.context.scene.unit_settings.scale_length,
            "length_unit": bpy.context.scene.unit_settings.length_unit,
        },
        "summary": {
            "matched_objects": len(rows),
            "object_types": dict(sorted(type_counts.items())),
            "categories": {key: value["object_count"] for key, value in categories.items()},
        },
        "categories": categories,
        "objects": rows,
        "warnings": warnings,
        "notes": [
            "Classificação é baseada em nomes/coleções e serve para auditoria inicial, não para semântica final.",
            "Não modifica objetos nem aplica transformações.",
            "Depois de carregar SOURCE_GEOREF, comparar bounds/traçado antes de qualquer correção estrutural.",
        ],
    }

    target = os.path.abspath(args.output)
    os.makedirs(os.path.dirname(target) or ".", exist_ok=True)
    with open(target, "w", encoding="utf-8") as stream:
        json.dump(payload, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(json.dumps(payload["summary"], ensure_ascii=False, indent=2))
    for warning in warnings:
        print(f"WARNING: {warning}")


if __name__ == "__main__":
    main()
