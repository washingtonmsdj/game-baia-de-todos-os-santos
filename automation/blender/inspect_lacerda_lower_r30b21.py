import bpy,json
from pathlib import Path
from mathutils import Matrix,Vector
I=Matrix.Rotation(bpy.data.objects['CASCA | parede lateral'].rotation_euler.z,4,'Z').inverted()
rows=[]
for o in bpy.data.objects:
 if o.type!='MESH' or o.hide_get():continue
 v=[I@o.matrix_world@Vector(p) for p in o.bound_box]
 bb=[[min(p[k] for p in v),max(p[k] for p in v)] for k in range(3)]
 if not all(bb[k][0]<hi and bb[k][1]>lo for k,(lo,hi) in enumerate([(-82.6,-82.0),(-1,9.5),(7.4,11.5)])):continue
 rows.append({'name':o.name,'bounds':[[round(min(p[k] for p in v),3),round(max(p[k] for p in v),3)] for k in range(3)],'materials':[m.name if m else None for m in o.data.materials]})
(Path(__file__).resolve().parents[2]/'artifacts/lacerda/r30b21_lower_objects.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
