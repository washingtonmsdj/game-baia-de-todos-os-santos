"""Localiza os vértices sem fonte antes de qualquer recorte do collider."""
import bpy,json
from pathlib import Path
root=Path(__file__).resolve().parents[2];c=json.loads((root/'world/areas/mvp-centro-lacerda/production.json').read_text());r=json.loads((root/'docs/reports/blender/terrain_junction_finish.json').read_text());o=bpy.context.scene.objects[c['export']['terrain_proxy']];ps=[o.matrix_world@o.data.vertices[id].co for id in r['proxy_missing_support_ids']];out={'missing_count':len(ps),'bounds':{'min':[min(p[i] for p in ps) for i in range(3)],'max':[max(p[i] for p in ps) for i in range(3)]},'samples':[list(p) for p in ps[::40]]};(root/'artifacts/terrain-vehicle/proxy-boundary.json').write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(out))
