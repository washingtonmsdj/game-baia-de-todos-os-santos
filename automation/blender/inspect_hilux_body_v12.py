"""Observação read-only das faces com arestas longas no vão da cabine."""
import bpy,json
from pathlib import Path
r=Path(__file__).resolve().parents[2];o=bpy.context.scene.objects['HILUX | CARROCERIA PRINCIPAL']
rows=[]
for p in o.data.polygons:
    pts=[o.data.vertices[i].co for i in p.vertices]
    if not(-1.05<p.center.y<1.16 and .7<p.center.z<1.78):continue
    longest=max((a-b).length for a,b in zip(pts,pts[1:]+pts[:1]))
    if longest<.65:continue
    groups={o.vertex_groups[g.group].name for i in p.vertices for g in o.data.vertices[i].groups}
    rows.append({'face':p.index,'area':p.area,'longest':longest,'groups':list(groups),'vertices':[list(a) for a in pts]})
(r/'artifacts/vehicles/rondesp/v12-face-observation.json').write_text(json.dumps(rows,ensure_ascii=False),encoding='utf-8')
