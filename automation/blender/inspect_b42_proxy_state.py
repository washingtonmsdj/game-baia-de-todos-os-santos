import bpy,json
from pathlib import Path
root=Path(__file__).resolve().parents[2]
c=json.loads((root/"world/areas/mvp-centro-lacerda/production.json").read_text(encoding="utf8"))
p=bpy.context.scene.objects[c["export"]["terrain_proxy"]]
print(json.dumps({"file":bpy.data.filepath,"dirty":bpy.data.is_dirty,"proxy_vertices":len(p.data.vertices),"proxy_faces":len(p.data.polygons)},ensure_ascii=False))
