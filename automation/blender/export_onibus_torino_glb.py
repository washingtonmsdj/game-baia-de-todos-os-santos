"""Exporta apenas a cena ativa e os objetos aprovados do veículo.

O GLB é validado antes de substituir o staging. Nenhuma fonte Blender é salva.
"""
import bpy
import json
import os
import sys
from pathlib import Path

root = next(p for p in Path(bpy.data.filepath).parents
            if (p / "world/areas/mvp-centro-lacerda/production.json").exists())
sys.path.insert(0, str(root))
from tools.runtime.production import load_contract, require_source, resolve, sha256
from tools.runtime.vehicle_staging import inspect_vehicle_glb

contract = load_contract()
require_source(contract["vehicle"]["source"], bpy.data.filepath)
scene = bpy.context.scene
if scene.name != contract["vehicle"]["source"]["scene"]:
    raise RuntimeError("Cena ativa diferente da fonte registrada do ônibus")
if bpy.data.is_dirty:
    raise RuntimeError("Cena do ônibus tem alterações não salvas; não exportar staging")

output = resolve(contract["staging"]["vehicle"])
output.parent.mkdir(parents=True, exist_ok=True)
pending = output.with_name(output.stem + ".pending.glb")
pending_manifest = output.with_suffix(".json.tmp")
old_selection = list(bpy.context.selected_objects)
old_active = bpy.context.view_layer.objects.active

try:
    bpy.ops.object.select_all(action="DESELECT")
    selected = []
    for obj in scene.objects:
        if any("APRESENTACAO" in c.name for c in obj.users_collection):
            continue
        if "estudio" in obj.name.casefold() or "estúdio" in obj.name.casefold():
            continue
        if obj.name.startswith(("BUS02 | ", "BUS03 | ")):
            if obj.type in {"MESH", "CURVE", "FONT", "EMPTY"}:
                obj.select_set(True)
                selected.append(obj)
    if not selected:
        raise RuntimeError("Nenhum objeto do ônibus para exportar")

    bpy.context.view_layer.objects.active = selected[0]
    bpy.ops.export_scene.gltf(
        filepath=str(pending),
        export_format="GLB",
        use_selection=True,
        use_active_scene=True,
        export_apply=True,
        export_yup=True,
        export_materials="EXPORT",
        export_animations=True,
        export_cameras=False,
        export_lights=False,
    )
    inspected = inspect_vehicle_glb(pending, scene.name)
    manifest = {
        "schema": "boas/vehicle-export-v1",
        "vehicle_id": contract["vehicle"]["id"],
        "source_file": contract["vehicle"]["source"]["file"],
        "source_sha256": contract["vehicle"]["source"]["sha256"],
        "source_scene": scene.name,
        "export_sha256": sha256(pending),
        "scene_count": inspected["scene_count"],
        "selected_objects": sorted(obj.name for obj in selected),
    }
    pending_manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                                encoding="utf-8")
    os.replace(pending, output)
    os.replace(pending_manifest, output.with_suffix(".json"))
    print(json.dumps({"vehicle": contract["vehicle"]["id"], "objects": len(selected),
                      "scene": scene.name, "export_sha256": manifest["export_sha256"]},
                     ensure_ascii=False))
finally:
    bpy.ops.object.select_all(action="DESELECT")
    for obj in old_selection:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = old_active
    pending.unlink(missing_ok=True)
    pending_manifest.unlink(missing_ok=True)
