import bpy,json
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2]
rows=[]
for o in bpy.context.scene.objects:
    if o.type=='MESH' and any(k in o.name.lower() for k in ['terreno','terrain','encosta','expansao','cais','b57 |','b55 |','b56 |']):
        if not o.visible_get() and not o.name.startswith(('B57 |','EXPANSAO B49 |')):continue
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]
        rows.append({'name':o.name,'visible':o.visible_get(),'hide_viewport':o.hide_viewport,'hide_render':o.hide_render,'vertices':len(o.data.vertices),'faces':len(o.data.polygons),'bounds':[[min(v[k] for v in bb) for k in range(3)],[max(v[k] for v in bb) for k in range(3)]],'materials':[m.name if m else None for m in o.data.materials]})
(root/'artifacts/waterfront/scene_surfaces_b57.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(rows,ensure_ascii=False))
