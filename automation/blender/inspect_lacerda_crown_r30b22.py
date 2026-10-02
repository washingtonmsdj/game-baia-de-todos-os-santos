import bpy,json
from pathlib import Path
from mathutils import Vector,Matrix
R=Matrix.Rotation(bpy.data.objects['CASCA | parede lateral'].rotation_euler.z,4,'Z');I=R.inverted()
rows=[]
for o in bpy.data.objects:
 if not o.name.startswith(('GALERIA |','TORRE |','FACHADA INFERIOR R22')) or o.hide_get():continue
 vv=[I@o.matrix_world@Vector(p) for p in o.bound_box]
 rows.append({'name':o.name,'type':o.type,'bounds':[[round(min(v[k] for v in vv),3),round(max(v[k] for v in vv),3)] for k in range(3)],'materials':[m.name if m else None for m in o.data.materials] if o.type=='MESH' else []})
(Path(__file__).resolve().parents[2]/'artifacts/lacerda/r30b22_crown.json').write_text(json.dumps(rows,ensure_ascii=False),encoding='utf8')
target=R@Vector((-68.,4.2,73.5));eye=R@Vector((-92.,24.,77.))
for area in bpy.context.screen.areas:
 if area.type=='VIEW_3D':
  s=area.spaces.active;r=s.region_3d;r.view_location=target;r.view_rotation=(target-eye).to_track_quat('-Z','Y');r.view_distance=(target-eye).length;r.view_perspective='PERSP';s.shading.type='MATERIAL'
