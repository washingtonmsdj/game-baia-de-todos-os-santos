# Bay of All Saints — extrator de pistas de georreferenciamento
# Uso:
# blender cena.blend --background --python tools/blender/extract_georef_hints.py -- --output docs/reports/blender/georef_hints.json

import argparse
import json
import math
import os
import re
import sys
from datetime import datetime, timezone

import bpy
from mathutils import Vector

KEYWORDS = ("aleph", "osm", "epsg", "terrain", "terreno", "source", "fonte", "mercator", "geo", "dem")
OSM_ID_RE = re.compile(r"(?:OSM\D*|(?:way|node|relation)/)(\d{5,})", re.IGNORECASE)


def json_value(value):
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if hasattr(value, "to_list"):
        return value.to_list()
    try:
        return list(value)
    except Exception:
        return str(value)


def interesting_properties(block):
    found = {}
    for key in block.keys():
        if key == "_RNA_UI":
            continue
        value = json_value(block[key])
        text = f"{key} {value}".lower()
        if any(token in text for token in KEYWORDS):
            found[key] = value
    return found


def world_bounds(obj):
    if obj.type not in {"MESH", "CURVE", "SURFACE", "META", "FONT"}:
        return None
    try:
        points = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    except Exception:
        return None
    mins = [min(p[i] for p in points) for i in range(3)]
    maxs = [max(p[i] for p in points) for i in range(3)]
    return {
        "min": [round(v, 6) for v in mins],
        "max": [round(v, 6) for v in maxs],
        "center": [round((a + b) / 2, 6) for a, b in zip(mins, maxs)],
        "size": [round(b - a, 6) for a, b in zip(mins, maxs)],
    }


def osm_ids(obj):
    values = set()
    candidates = [obj.name]
    for key in obj.keys():
        value = json_value(obj[key])
        candidates.append(f"{key}={value}")
        if str(key).lower() in {"osm_id", "osmid", "osm_way_id", "way_id"}:
            try:
                values.add(str(int(value)))
            except Exception:
                pass
    for text in candidates:
        for match in OSM_ID_RE.finditer(str(text)):
            values.add(match.group(1))
    return sorted(values)


def parse_args():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="georef_hints.json")
    return parser.parse_args(argv)


def main():
    args = parse_args()
    scene = bpy.context.scene
    unit = scene.unit_settings

    objects = []
    source_paths = set()
    for obj in bpy.data.objects:
        props = interesting_properties(obj)
        ids = osm_ids(obj)
        if not props and not ids and not any(token in obj.name.lower() for token in KEYWORDS):
            continue
        for value in props.values():
            if isinstance(value, str) and ("aleph" in value.lower() or "map.osm" in value.lower()):
                source_paths.add(value)
        objects.append({
            "name": obj.name,
            "type": obj.type,
            "osm_ids": ids,
            "properties": props,
            "location_world": [round(v, 6) for v in obj.matrix_world.translation],
            "bounds_world": world_bounds(obj),
            "collections": [c.name for c in obj.users_collection],
        })

    collections = []
    for collection in bpy.data.collections:
        props = interesting_properties(collection)
        if props:
            for value in props.values():
                if isinstance(value, str) and ("aleph" in value.lower() or "map.osm" in value.lower()):
                    source_paths.add(value)
            collections.append({"name": collection.name, "properties": props})

    scene_props = interesting_properties(scene)
    for value in scene_props.values():
        if isinstance(value, str) and ("aleph" in value.lower() or "map.osm" in value.lower()):
            source_paths.add(value)

    payload = {
        "schema": "bay-of-all-saints/blender-georef-hints-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "blend_file": bpy.data.filepath,
        "blender_version": bpy.app.version_string,
        "units": {
            "system": unit.system,
            "scale_length": unit.scale_length,
            "length_unit": unit.length_unit,
        },
        "scene_properties": scene_props,
        "source_paths": sorted(source_paths),
        "collections": collections,
        "objects": objects,
        "notes": [
            "Este relatório contém pistas, não uma origem geográfica certificada.",
            "OSM IDs e bounds permitem reconstruir/validar uma transformação usando o map.osm original.",
            "Não assumir norte, escala ou offset como definitivos sem validação contra múltiplos anchors.",
        ],
    }

    output = os.path.abspath(args.output)
    os.makedirs(os.path.dirname(output) or ".", exist_ok=True)
    with open(output, "w", encoding="utf-8") as stream:
        json.dump(payload, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(f"[georef] relatório salvo em: {output}")
    print(f"[georef] objetos com pistas: {len(objects)}")
    print(f"[georef] caminhos-fonte detectados: {len(source_paths)}")


if __name__ == "__main__":
    main()
