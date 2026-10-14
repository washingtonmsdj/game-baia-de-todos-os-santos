import bpy,json
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2]
names=['LAC R30B07 | galeria | consolo inclinado','FUNCIONAL | 3 piso','FUNCIONAL | 3 teto']
names += [o.name for o in bpy.context.scene.objects if 'shaft' in o.name.lower() or 'poço' in o.name.lower()]
data=[]
for name in names:
    o=bpy.data.objects.get(name)
    if not o:continue
    points=[o.matrix_world@Vector(p) for p in o.bound_box]
    data.append({'name':name,'bounds':[[min(p[i] for p in points) for i in range(3)],[max(p[i] for p in points) for i in range(3)]],'vertices':len(o.data.vertices) if o.type=='MESH' else None,'props':dict(o.items()),'modifiers':[(m.name,m.type) for m in o.modifiers],'matrix':[list(r) for r in o.matrix_world]})
(root/'docs/reports/blender/lacerda-corridor/shaft_conflict_b77.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(data,ensure_ascii=False))
