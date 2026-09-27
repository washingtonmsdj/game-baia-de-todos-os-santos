# All Saints / Salvador MVP — Revision R27
# Safe, non-destructive QA/review pass for Blender 4.x / 5.x.
# Usage:
#   blender current_scene.blend --python tools/blender/r27_qa_review.py

import bpy
import json
import math
import os
import re
from mathutils import Vector

REV = "R27"
PREFIX = "R27 | "
GUIDE_COLLECTION = "30 MVP | QA E GUIAS R27"
LIGHT_COLLECTION = "31 LUZ | PREVIEW R27"
TEXT_NAME = "R27_README"

# Coordinates are derived from checkpoints already registered in the analyzed scene.
# They are design/QA guides, not certified survey data.
ANCHORS = [
    ("ENTRADA SUPERIOR", (-5.66, -0.67, 70.32), 2.0),
    ("PASSARELA", (-35.43, 39.07, 70.10), 1.8),
    ("CABINES SUPERIORES", (-46.05, 51.32, 71.45), 1.5),
    ("CABINES INFERIORES", (-48.33, 49.00, 12.45), 1.5),
    ("SAIDA INFERIOR", (-57.47, 59.75, 7.41), 1.8),
    ("PRACA CAIRU", (-126.49, 154.29, 10.50), 2.2),
    ("MERCADO MODELO", (-148.95, 172.78, 14.26), 2.5),
]

KNOWN_LIMITATIONS = [
    "Upper entrance footprint still requires stronger reference/survey confirmation.",
    "Slope profile is functional for the MVP and must not be treated as a final road survey.",
    "Praca Castro Alves / Ladeira da Conceicao contain omitted road fragments caused by DEM cliff artifacts.",
    "Lower-exit elevation and local terrain remain MVP approximations.",
    "Facade and street-furniture references are visual references, not fully certified dimensional surveys.",
]


def get_or_create_collection(name):
    collection = bpy.data.collections.get(name)
    if collection is None:
        collection = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(collection)
    return collection


def remove_generated():
    for obj in list(bpy.data.objects):
        if obj.name.startswith(PREFIX):
            bpy.data.objects.remove(obj, do_unlink=True)


def add_empty(collection, label, location, size):
    obj = bpy.data.objects.new(PREFIX + label, None)
    obj.empty_display_type = "SPHERE"
    obj.empty_display_size = size
    obj.location = location
    obj.show_name = True
    obj["allsaints_revision"] = REV
    obj["allsaints_role"] = "qa_anchor"
    collection.objects.link(obj)
    return obj


def point_at(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def add_review_camera(collection):
    data = bpy.data.cameras.new(PREFIX + "REVIEW CAMERA")
    camera = bpy.data.objects.new(PREFIX + "REVIEW CAMERA", data)
    collection.objects.link(camera)
    camera.location = (-80.0, 65.0, 215.0)
    data.lens = 48
    data.sensor_width = 36
    data.clip_start = 0.1
    data.clip_end = 5000.0
    point_at(camera, (-70.0, 75.0, 35.0))
    camera["allsaints_revision"] = REV
    camera["allsaints_role"] = "review_camera"
    return camera


def add_sun(collection):
    data = bpy.data.lights.new(PREFIX + "SUN PREVIEW", type="SUN")
    data.energy = 2.0
    data.angle = math.radians(4.0)
    obj = bpy.data.objects.new(PREFIX + "SUN PREVIEW", data)
    collection.objects.link(obj)
    obj.rotation_euler = tuple(math.radians(v) for v in (28.0, -18.0, -32.0))
    obj.hide_render = True
    obj["allsaints_revision"] = REV
    obj["allsaints_role"] = "optional_preview_light"
    return obj


def add_area(collection, label, location, target, energy, size):
    data = bpy.data.lights.new(PREFIX + label, type="AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    obj = bpy.data.objects.new(PREFIX + label, data)
    collection.objects.link(obj)
    obj.location = location
    point_at(obj, target)
    obj.hide_render = True
    obj["allsaints_revision"] = REV
    obj["allsaints_role"] = "optional_preview_light"
    return obj


def write_readme(scene, counts):
    text = bpy.data.texts.get(TEXT_NAME) or bpy.data.texts.new(TEXT_NAME)
    text.clear()
    lines = [
        "ALL SAINTS / SALVADOR MVP — R27\n",
        "\n",
        "PURPOSE\n",
        "- preserve the existing architecture and historical scene structure;\n",
        "- add QA markers for the current playable corridor;\n",
        "- add a review camera;\n",
        "- add optional preview lighting disabled for render by default;\n",
        "- record known limitations without mass-renaming existing objects.\n",
        "\nCOUNTS OBSERVED BEFORE R27\n",
        json.dumps(counts, ensure_ascii=False, indent=2),
        "\n\nKNOWN LIMITATIONS\n",
    ]
    for item in KNOWN_LIMITATIONS:
        lines.append("- " + item + "\n")
    lines += [
        "\nUSAGE NOTES\n",
        "1. '30 MVP | QA E GUIAS R27' contains only QA markers and a review camera.\n",
        "2. '31 LUZ | PREVIEW R27' contains optional lights with hide_render=True.\n",
        "3. No automatic .001/.002 mass renaming is performed.\n",
        "4. Export optimization belongs in a dedicated later revision.\n",
    ]
    text.write("".join(lines))
    scene["allsaints_r27_status"] = "QA guides + review camera + optional preview lighting"
    scene["allsaints_r27_known_limitations"] = json.dumps(KNOWN_LIMITATIONS, ensure_ascii=False)
    scene["allsaints_r27_anchor_count"] = len(ANCHORS)


def revision_output_path(source_path):
    if not source_path:
        return os.path.join(os.path.expanduser("~"), "salvador_lacerda_mvp_r27.blend")
    root, ext = os.path.splitext(source_path)
    root = re.sub(r"_r\d+$", "", root, flags=re.IGNORECASE)
    return root + "_r27" + (ext or ".blend")


def main():
    scene = bpy.context.scene
    counts = {
        "objects": len(bpy.data.objects),
        "meshes": len(bpy.data.meshes),
        "materials": len(bpy.data.materials),
        "collections": len(bpy.data.collections),
        "curves": len(bpy.data.curves),
        "lights": len(bpy.data.lights),
        "cameras": len(bpy.data.cameras),
    }

    remove_generated()
    guides = get_or_create_collection(GUIDE_COLLECTION)
    lights = get_or_create_collection(LIGHT_COLLECTION)

    guides.hide_viewport = False
    guides.hide_render = True
    lights.hide_viewport = False

    for label, location, size in ANCHORS:
        add_empty(guides, label, location, size)

    add_review_camera(guides)
    add_sun(lights)
    add_area(lights, "AREA CENTRO", (-35.0, 20.0, 135.0), (-35.0, 40.0, 55.0), 1800.0, 45.0)
    add_area(lights, "AREA CIDADE BAIXA", (-110.0, 135.0, 95.0), (-130.0, 165.0, 12.0), 1500.0, 55.0)

    write_readme(scene, counts)

    output = revision_output_path(bpy.data.filepath)
    bpy.ops.wm.save_as_mainfile(filepath=output)
    print("[R27] Saved:", output)


if __name__ == "__main__":
    main()
