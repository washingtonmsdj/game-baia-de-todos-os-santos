# Bay of All Saints — importador não destrutivo de referência estrutural
# Uso:
# blender cena.blend --background --python tools/blender/import_structural_reference.py -- \
#   --reference docs/reports/blender/structural_reference.json --save-as cena_structure_ref.blend

from __future__ import annotations

import argparse
import json
import os
import sys

import bpy

ROOT_COLLECTION = "SOURCE_GEOREF | STRUCTURAL_REFERENCE"
TEXT_INDEX = "STRUCTURAL_REFERENCE_INDEX"

LAYER_SETTINGS = {
    "roads": {"bevel": 0.12, "z": 0.30},
    "pedestrian": {"bevel": 0.09, "z": 0.35},
    "steps": {"bevel": 0.10, "z": 0.40},
    "buildings": {"bevel": 0.06, "z": 0.20},
    "coastline": {"bevel": 0.16, "z": 0.50},
    "waterfront": {"bevel": 0.16, "z": 0.55},
    "retaining_walls": {"bevel": 0.11, "z": 0.45},
    "water": {"bevel": 0.08, "z": 0.10},
    "railways": {"bevel": 0.10, "z": 0.25},
}


def parse_args():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference", required=True)
    parser.add_argument("--save-as")
    parser.add_argument("--replace-existing", action="store_true")
    return parser.parse_args(argv)


def ensure_collection(name: str, parent=None):
    collection = bpy.data.collections.get(name)
    if collection is None:
        collection = bpy.data.collections.new(name)
    parent_collection = parent or bpy.context.scene.collection
    if collection.name not in {child.name for child in parent_collection.children}:
        parent_collection.children.link(collection)
    return collection


def remove_collection_tree(collection):
    for child in list(collection.children):
        remove_collection_tree(child)
    for obj in list(collection.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.collections.remove(collection)


def create_layer_object(layer: str, features: list[dict], parent):
    settings = LAYER_SETTINGS.get(layer, {"bevel": 0.08, "z": 0.0})
    curve = bpy.data.curves.new(f"REF_{layer.upper()}_CURVE", "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 1
    curve.bevel_depth = settings["bevel"]
    curve.bevel_resolution = 0
    curve.fill_mode = "FULL"

    index_rows = []
    spline_index = 0
    for feature in features:
        points = feature.get("blender_xy") or []
        if len(points) < 2:
            continue
        spline = curve.splines.new("POLY")
        spline.points.add(len(points) - 1)
        z = settings["z"]
        for target, point in zip(spline.points, points):
            target.co = (float(point[0]), float(point[1]), z, 1.0)
        spline.use_cyclic_u = bool(feature.get("closed"))
        index_rows.append({
            "layer": layer,
            "spline_index": spline_index,
            "osm_type": feature.get("osm_type"),
            "osm_id": feature.get("osm_id"),
            "tags": feature.get("tags", {}),
            "metrics": feature.get("metrics", {}),
        })
        spline_index += 1

    obj = bpy.data.objects.new(f"REF_{layer.upper()}", curve)
    parent.objects.link(obj)
    obj["boas_reference_layer"] = layer
    obj["boas_reference_only"] = True
    obj["boas_feature_count"] = len(index_rows)
    obj.hide_render = True
    return obj, index_rows


def write_index(payload, rows):
    text = bpy.data.texts.get(TEXT_INDEX) or bpy.data.texts.new(TEXT_INDEX)
    text.clear()
    index_payload = {
        "schema": "bay-of-all-saints/blender-structural-reference-index-v1",
        "source_reference": payload.get("source_structure"),
        "source_fit": payload.get("source_fit"),
        "fit_quality": payload.get("fit_quality"),
        "fit_status": payload.get("fit_status"),
        "fit_summary": payload.get("fit_summary", {}),
        "splines": rows,
        "notes": [
            "Objetos REF_* são somente referência e ficam ocultos no render.",
            "spline_index permite rastrear cada linha/footprint ao OSM ID original.",
        ],
    }
    text.write(json.dumps(index_payload, ensure_ascii=False, indent=2))


def main():
    args = parse_args()
    reference_path = os.path.abspath(args.reference)
    with open(reference_path, "r", encoding="utf-8") as stream:
        payload = json.load(stream)

    if payload.get("schema") != "bay-of-all-saints/blender-structure-reference-v1":
        raise RuntimeError("schema de referência estrutural não suportado")

    existing = bpy.data.collections.get(ROOT_COLLECTION)
    if existing:
        if not args.replace_existing:
            raise RuntimeError(f"coleção {ROOT_COLLECTION} já existe; use --replace-existing para reconstruí-la")
        remove_collection_tree(existing)

    root = ensure_collection(ROOT_COLLECTION)
    root["boas_reference_only"] = True
    root["boas_fit_quality"] = payload.get("fit_quality") or "unknown"
    root["boas_source_reference"] = reference_path

    grouped: dict[str, list[dict]] = {}
    for feature in payload.get("features", []):
        grouped.setdefault(feature.get("layer", "other"), []).append(feature)

    all_rows = []
    for layer in sorted(grouped):
        sub = ensure_collection(f"SOURCE_GEOREF | {layer.upper()}", root)
        obj, rows = create_layer_object(layer, grouped[layer], sub)
        all_rows.extend(rows)
        print(f"[structure] {layer}: {obj.get('boas_feature_count', 0)} features")

    write_index(payload, all_rows)
    bpy.context.scene["boas_structural_reference_loaded"] = True
    bpy.context.scene["boas_structural_reference_fit_quality"] = payload.get("fit_quality") or "unknown"
    bpy.context.scene["boas_structural_reference_feature_count"] = len(all_rows)

    if args.save_as:
        target = os.path.abspath(args.save_as)
        os.makedirs(os.path.dirname(target) or ".", exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=target)
        print(f"[structure] salvo: {target}")

    print(f"[structure] total: {len(all_rows)} features de referência")


if __name__ == "__main__":
    main()
