# Bay of All Saints — exportador de relatórios do Blender
# Exemplo:
#   blender cena_r29.blend --background \
#     --python tools/blender/export_revision_reports.py \
#     -- --output-dir docs/reports/blender/r29

import bpy
import json
import os
import re
import sys
from collections import Counter


def cli_args():
    if "--" not in sys.argv:
        return []
    return sys.argv[sys.argv.index("--") + 1 :]


def arg_value(name, default=None):
    args = cli_args()
    if name not in args:
        return default
    index = args.index(name)
    if index + 1 >= len(args):
        raise RuntimeError(f"Argumento sem valor: {name}")
    return args[index + 1]


def safe_name(name):
    value = re.sub(r"[^A-Za-z0-9._-]+", "_", name.strip())
    return value.strip("._") or "unnamed"


def default_output_dir():
    blend = bpy.data.filepath
    if blend:
        base = os.path.dirname(blend)
        stem = os.path.splitext(os.path.basename(blend))[0]
        return os.path.join(base, "blender_reports", safe_name(stem))
    return os.path.join(os.path.expanduser("~"), "bay_of_all_saints_blender_reports")


def collect_summary():
    type_counts = Counter(obj.type for obj in bpy.data.objects)
    class_counts = Counter(
        str(obj.get("allsaints_r28_class", "UNCLASSIFIED"))
        for obj in bpy.data.objects
    )

    mesh_objects = [
        obj for obj in bpy.data.objects
        if obj.type == "MESH" and obj.data
    ]

    summary = {
        "project": "Bay of All Saints",
        "blend_file": bpy.data.filepath,
        "scene": bpy.context.scene.name if bpy.context.scene else None,
        "counts": {
            "objects": len(bpy.data.objects),
            "meshes": len(bpy.data.meshes),
            "materials": len(bpy.data.materials),
            "collections": len(bpy.data.collections),
            "curves": len(bpy.data.curves),
            "lights": len(bpy.data.lights),
            "cameras": len(bpy.data.cameras),
            "texts": len(bpy.data.texts),
        },
        "object_types": dict(sorted(type_counts.items())),
        "r28_classes": dict(sorted(class_counts.items())),
        "mesh_totals": {
            "object_vertices": sum(len(obj.data.vertices) for obj in mesh_objects),
            "object_polygons": sum(len(obj.data.polygons) for obj in mesh_objects),
            "unique_mesh_vertices": sum(len(mesh.vertices) for mesh in bpy.data.meshes),
            "unique_mesh_polygons": sum(len(mesh.polygons) for mesh in bpy.data.meshes),
        },
        "revision_properties": {},
    }

    scene = bpy.context.scene
    if scene:
        for key in scene.keys():
            if key == "_RNA_UI":
                continue
            if str(key).startswith("allsaints_"):
                value = scene[key]
                try:
                    json.dumps(value)
                    summary["revision_properties"][key] = value
                except TypeError:
                    summary["revision_properties"][key] = str(value)

    return summary


def export_textblocks(output_dir):
    exported = []

    for text in bpy.data.texts:
        name_upper = text.name.upper()
        if not (
            re.match(r"R\d+A?_", name_upper)
            or "AUDIT" in name_upper
            or "REPORT" in name_upper
            or "README" in name_upper
        ):
            continue

        filename = safe_name(text.name) + ".txt"
        path = os.path.join(output_dir, filename)
        with open(path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text.as_string())

        exported.append({
            "textblock": text.name,
            "file": filename,
            "characters": len(text.as_string()),
        })

    return exported


def main():
    output_dir = arg_value("--output-dir", default_output_dir())
    output_dir = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    summary = collect_summary()
    exported = export_textblocks(output_dir)
    summary["exported_textblocks"] = exported

    summary_path = os.path.join(output_dir, "scene_summary.json")
    with open(summary_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2)

    print("[REPORT EXPORT] Pasta:", output_dir)
    print("[REPORT EXPORT] Textblocks:", len(exported))
    print("[REPORT EXPORT] Summary:", summary_path)


if __name__ == "__main__":
    main()
