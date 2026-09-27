# Bay of All Saints — exportador de amostras da geometria de terreno
# Uso:
# blender cena.blend --background --python tools/blender/export_terrain_samples.py -- \
#   --output docs/reports/blender/terrain_samples.json

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys

import bpy

TERRAIN_KEYWORDS = ("terreno", "relevo", "terrain", "dem", "encosta")
REFERENCE_PREFIX = "SOURCE_GEOREF |"


def parse_args():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--max-points-per-object", type=int, default=5000)
    parser.add_argument("--include-regex", help="regex opcional aplicada ao nome do objeto + coleções")
    return parser.parse_args(argv)


def corpus(obj) -> str:
    return " ".join([obj.name] + [collection.name for collection in obj.users_collection])


def is_reference(obj) -> bool:
    if obj.get("boas_reference_only"):
        return True
    return any(collection.name.startswith(REFERENCE_PREFIX) for collection in obj.users_collection)


def is_terrain(obj, include_re) -> bool:
    if obj.type != "MESH" or not obj.data or is_reference(obj):
        return False
    text = corpus(obj)
    if include_re is not None:
        return bool(include_re.search(text))
    folded = text.casefold()
    return any(keyword in folded for keyword in TERRAIN_KEYWORDS)


def sample_object(obj, max_points: int) -> list[list[float]]:
    vertices = obj.data.vertices
    count = len(vertices)
    if not count:
        return []
    stride = max(1, math.ceil(count / max_points))
    indices = list(range(0, count, stride))
    if indices[-1] != count - 1 and len(indices) < max_points:
        indices.append(count - 1)
    points = []
    for index in indices[:max_points]:
        world = obj.matrix_world @ vertices[index].co
        points.append([float(world.x), float(world.y), float(world.z)])
    return points


def main():
    args = parse_args()
    if args.max_points_per_object < 10:
        raise RuntimeError("--max-points-per-object deve ser >= 10")
    include_re = re.compile(args.include_regex, re.IGNORECASE) if args.include_regex else None

    rows = []
    total_points = 0
    for obj in sorted(bpy.data.objects, key=lambda value: value.name):
        if not is_terrain(obj, include_re):
            continue
        points = sample_object(obj, args.max_points_per_object)
        if not points:
            continue
        total_points += len(points)
        rows.append({
            "object_name": obj.name,
            "collections": [collection.name for collection in obj.users_collection],
            "vertex_count": len(obj.data.vertices),
            "sample_count": len(points),
            "points_world": points,
        })

    payload = {
        "schema": "bay-of-all-saints/blender-terrain-samples-v1",
        "blend_file": bpy.data.filepath,
        "blender_version": bpy.app.version_string,
        "scene_units": {
            "system": bpy.context.scene.unit_settings.system,
            "scale_length": bpy.context.scene.unit_settings.scale_length,
            "length_unit": bpy.context.scene.unit_settings.length_unit,
        },
        "selection": {
            "include_regex": args.include_regex,
            "max_points_per_object": args.max_points_per_object,
            "default_keywords": list(TERRAIN_KEYWORDS) if not args.include_regex else None,
        },
        "summary": {
            "objects": len(rows),
            "points": total_points,
        },
        "objects": rows,
        "notes": [
            "Amostras são vértices da mesh original transformados para world space.",
            "O exportador não aplica modificadores nem altera a cena.",
            "Use --include-regex quando a nomenclatura histórica incluir objetos que não representam a superfície principal do terreno.",
        ],
    }
    if not rows:
        payload["notes"].append("Nenhum terreno foi encontrado; revisar --include-regex/nomenclatura antes do fit vertical.")

    target = os.path.abspath(args.output)
    os.makedirs(os.path.dirname(target) or ".", exist_ok=True)
    with open(target, "w", encoding="utf-8") as stream:
        json.dump(payload, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(json.dumps(payload["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
