"""Verifica cobertura do proxy no encontro sem editar ou renderizar."""
import bpy,json,math
from pathlib import Path
root=Path(__file__).resolve().parents[2];c=json.loads((root/'world/areas/mvp-centro-lacerda/production.json').read_text());o=bpy.context.scene.objects[c['export']['terrain_proxy']];bpy.context.view_layer.update()
ps=[o.matrix_world@v.co for v in o.data.vertices];local=[p for p in ps if math.hypot(p.x+169.42958,p.y+177.65443)<18];nearest=sorted(ps,key=lambda p:math.hypot(p.x+169.42958,p.y+177.65443))[:8]
r={'object':o.name,'matrix':[list(row) for row in o.matrix_world],'vertices_in_local_region':len(local),'local_height_range':[min(p.z for p in local),max(p.z for p in local)] if local else None,'nearest_vertices':[list(p) for p in nearest]};(root/'artifacts/terrain-vehicle/proxy-local.json').write_text(json.dumps(r,indent=2),encoding='utf8');print(json.dumps(r))
