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

STRICT_TERRAIN_KEYWORDS = ("terreno", "terrain", "dem")
LEGACY_TERRAIN_KEYWORDS = ("terreno", "relevo", "terrain", "dem", "encosta")
REFERENCE_PREFIX = "SOURCE_GEOREF |"
EXPLICIT_PROPERTY = "boas_terrain_surface"


def parse_args():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--max-points-per-object", type=int, default=5000)
    parser.add_argument("--include-regex", help="regex opcional aplicada ao nome do objeto + coleções; substitui a seleção automática")
    parser.add_argument("--exclude-regex", help="regex opcional para excluir objetos mesmo quando incluídos")
    parser.add_argument(
        "--selection-mode",
        choices=("strict", "legacy"),
        default="strict",
        help="strict usa apenas nome do objeto/boas_terrain_surface; legacy mantém heurística histórica por nome+coleções",
    )
    return parser.parse_args(argv)


def corpus(obj) -> str:
    return " ".join([obj.name] + [collection.name for collection in obj.users_collection])


def is_reference(obj) -> bool:
    if obj.get("boas_reference_only"):
        return True
    return any(collection.name.startswith(REFERENCE_PREFIX) for collection in obj.users_collection)


def explicit_terrain_state(obj):
    if EXPLICIT_PROPERTY not in obj.keys():
        return None
    return bool(obj.get(EXPLICIT_PROPERTY))


def is_terrain(obj, include_re, exclude_re, selection_mode: str) -> tuple[bool, str]:
    if obj.type != "MESH" or not obj.data:
        return False, "not_mesh"
    if is_reference(obj):
        return False, "reference"

    text = corpus(obj)
    if exclude_re is not None and exclude_re.search(text):
        return False, "excluded_by_regex"

    explicit = explicit_terrain_state(obj)
    if explicit is False:
        return False, "explicit_false"
    if explicit is True:
        return True, "explicit_true"

    if include_re is not None:
        return (bool(include_re.search(text)), "include_regex")

    if selection_mode == "legacy":
        folded = text.casefold()
        matched = any(keyword in folded for keyword in LEGACY_TERRAIN_KEYWORDS)
        return matched, "legacy_name_or_collection"

    # Modo padrão: o nome do PRÓPRIO objeto precisa indicar superfície de terreno.
    # Coleções como "TERRENO" podem conter passarela, fachada, colisores, calçadas etc.
    folded_name = obj.name.casefold()
    matched = any(keyword in folded_name for keyword in STRICT_TERRAIN_KEYWORDS)
    return matched, "strict_object_name"


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
    exclude_re = re.compile(args.exclude_regex, re.IGNORECASE) if args.exclude_regex else None

    rows = []
    total_points = 0
    selection_counts: dict[str, int] = {}
    rejected_examples: dict[str, list[str]] = {}

    for obj in sorted(bpy.data.objects, key=lambda value: value.name):
        selected, reason = is_terrain(obj, include_re, exclude_re, args.selection_mode)
        selection_counts[reason] = selection_counts.get(reason, 0) + 1
        if not selected:
            if obj.type == "MESH" and len(rejected_examples.setdefault(reason, [])) < 12:
                rejected_examples[reason].append(obj.name)
            continue
        points = sample_object(obj, args.max_points_per_object)
        if not points:
            continue
        total_points += len(points)
        rows.append({
            "object_name": obj.name,
            "collections": [collection.name for collection in obj.users_collection],
            "selection_reason": reason,
            "explicit_terrain_surface": explicit_terrain_state(obj),
            "vertex_count": len(obj.data.vertices),
            "sample_count": len(points),
            "points_world": points,
        })

    payload = {
        # Mantido em v1 porque os consumidores existentes aceitam campos adicionais e a
        # mudança desta revisão é de política de seleção, não de formato geométrico.
        "schema": "bay-of-all-saints/blender-terrain-samples-v1",
        "blend_file": bpy.data.filepath,
        "blender_version": bpy.app.version_string,
        "scene_units": {
            "system": bpy.context.scene.unit_settings.system,
            "scale_length": bpy.context.scene.unit_settings.scale_length,
            "length_unit": bpy.context.scene.unit_settings.length_unit,
        },
        "selection": {
            "mode": args.selection_mode,
            "include_regex": args.include_regex,
            "exclude_regex": args.exclude_regex,
            "max_points_per_object": args.max_points_per_object,
            "strict_object_name_keywords": list(STRICT_TERRAIN_KEYWORDS),
            "legacy_keywords": list(LEGACY_TERRAIN_KEYWORDS),
            "explicit_property": EXPLICIT_PROPERTY,
            "selection_counts": selection_counts,
            "rejected_examples": rejected_examples,
        },
        "summary": {
            "objects": len(rows),
            "points": total_points,
        },
        "objects": rows,
        "notes": [
            "Amostras são vértices da mesh original transformados para world space.",
            "O exportador não aplica modificadores nem altera a cena.",
            "Modo strict é o padrão porque nomes de coleção históricos podem incluir objetos que não representam superfície de terreno.",
            "boas_terrain_surface=true inclui explicitamente; false exclui explicitamente.",
            "Use --include-regex para uma seleção consciente e reproduzível quando a nomenclatura não for suficiente.",
            "Modo legacy existe apenas para reproduzir auditorias antigas; não deve ser usado para promover calibração vertical sem revisão.",
        ],
    }
    if not rows:
        payload["notes"].append("Nenhum terreno foi encontrado; revisar boas_terrain_surface/--include-regex antes do fit vertical.")

    target = os.path.abspath(args.output)
    os.makedirs(os.path.dirname(target) or ".", exist_ok=True)
    with open(target, "w", encoding="utf-8") as stream:
        json.dump(payload, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(json.dumps(payload["summary"], ensure_ascii=False, indent=2))
    print(json.dumps({"selection_mode": args.selection_mode, "selection_counts": selection_counts}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
