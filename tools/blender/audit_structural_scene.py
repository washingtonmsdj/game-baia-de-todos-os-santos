# Bay of All Saints — auditoria estrutural da cena Blender
# Uso:
# blender cena.blend --background --python tools/blender/audit_structural_scene.py -- \
#   --output docs/reports/blender/structural_scene_audit.json

from __future__ import annotations

import argparse
import json
import os
import re
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
OSM_ID_RE = re.compile(r"(?:\bOSM\b\D*|\bway\b\D*|\bnode\b\D*|\brelation\b\D*)(\d{5,})", re.IGNORECASE)
OSM_PROPERTY_KEYS = {"osm_id", "osmid", "osm_way_id", "way_id", "osm_node_id", "node_id", "osm_relation_id", "relation_id"}
REFERENCE_PREFIX = "SOURCE_GEOREF |"


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


def is_reference_object(obj) -> bool:
    if obj.get("boas_reference_only"):
        return True
    return any(collection.name.startswith(REFERENCE_PREFIX) for collection in obj.users_collection)


def json_value(value):
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    try:
        return list(value)
    except Exception:
        return str(value)


def osm_ids(obj) -> list[int]:
    values = set()
    candidates = [obj.name]
    for key in obj.keys():
        if key == "_RNA_UI":
            continue
        if str(key).casefold() in OSM_PROPERTY_KEYS:
            value = json_value(obj[key])
            candidates.append(f"{key}={value}")
            try:
                values.add(int(value))
            except (TypeError, ValueError):
                pass
    for text in candidates:
        for match in OSM_ID_RE.finditer(str(text)):
            values.add(int(match.group(1)))
    return sorted(values)


def world_bounds(obj):
    if obj.type not in {"MESH", "CURVE", "SURFACE", "META", "FONT"}:
        return None
    try:
        points = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    except Exception:
        return None
    return {
        "min": [float(min(point[i] for point in points)) for i in range(3)],
        "max": [float(max(point[i] for point in points)) for i in range(3)],
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
    osm_object_count = 0

    for obj in bpy.data.objects:
        if is_reference_object(obj):
            continue
        ids = osm_ids(obj)
        categories = classify(obj)
        if not categories and not ids:
            continue
        if ids:
            osm_object_count += 1
        row = {
            "name": obj.name,
            "type": obj.type,
            "categories": sorted(categories),
            "osm_ids": ids,
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
    if not osm_object_count:
        warnings.append("Nenhum OSM ID foi detectado em objetos não-reference; comparação por ID ficará indisponível.")

    payload = {
        "schema": "bay-of-all-saints/blender-structural-scene-audit-v2",
        "blend_file": bpy.data.filepath,
        "blender_version": bpy.app.version_string,
        "scene_units": {
            "system": bpy.context.scene.unit_settings.system,
            "scale_length": bpy.context.scene.unit_settings.scale_length,
            "length_unit": bpy.context.scene.unit_settings.length_unit,
        },
        "summary": {
            "matched_objects": len(rows),
            "objects_with_osm_ids": osm_object_count,
            "unique_osm_ids": len({osm_id for row in rows for osm_id in row["osm_ids"]}),
            "object_types": dict(sorted(type_counts.items())),
            "categories": {key: value["object_count"] for key, value in categories.items()},
        },
        "categories": categories,
        "objects": rows,
        "warnings": warnings,
        "notes": [
            "Classificação é baseada em nomes/coleções e serve para auditoria inicial, não para semântica final.",
            "OSM IDs são extraídos somente quando há prefixo/propriedade explícita; sufixos numéricos Blender não são interpretados como OSM.",
            "Objetos SOURCE_GEOREF/boas_reference_only são excluídos para evitar comparar a referência com ela mesma.",
            "Não modifica objetos nem aplica transformações.",
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
