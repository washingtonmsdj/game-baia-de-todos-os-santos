"""Inspeção read-only do proxy B42 vivo versus cópia salva."""
import bpy,json,runpy
from pathlib import Path
root=Path(__file__).resolve().parents[2]
rep=json.loads((root/"docs/reports/blender/misericordia_surface_r30b42.json").read_text(encoding="utf8"))
assert Path(bpy.data.filepath).resolve()==(root/rep["source_after"]["file"]).resolve()
c=json.loads((root/"world/areas/mvp-centro-lacerda/production.json").read_text(encoding="utf8"))
api=runpy.run_path(str(root/"automation/blender/component_fingerprint.py"));name=c["export"]["terrain_proxy"]
live=api["signature"](bpy.context.scene.objects[name])
saved=api["inspect_file"](root/"artifacts/blender-sessions/b42_saved_probe_copy.blend",[name])[name]
print(json.dumps({"dirty":bpy.data.is_dirty,"proxy_vertices_live":len(bpy.context.scene.objects[name].data.vertices),"live_equals_saved":live==saved},ensure_ascii=False))
