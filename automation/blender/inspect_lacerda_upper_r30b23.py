import bpy,json
from pathlib import Path
from mathutils import Matrix,Vector
R=Matrix.Rotation(bpy.data.objects['CASCA | parede lateral'].rotation_euler.z,4,'Z');I=R.inverted()
data=[]
for o in bpy.data.objects:
 if o.type!='MESH' or not o.name.startswith(('FACHADA SUPERIOR','EDIFICIO | janela lateral','SUPERIOR | lateral corpo')):continue
 vv=[I@o.matrix_world@v.co for v in o.data.vertices]
 data.append({'name':o.name,'hidden':o.hide_get(),'bounds':[[min(p[k] for p in vv),max(p[k] for p in vv)] for k in range(3)],'materials':[m.name if m else None for m in o.data.materials]})
(Path(__file__).resolve().parents[2]/'artifacts/lacerda/r30b23_upper.json').write_text(json.dumps(data,ensure_ascii=False),encoding='utf8')
target=R@Vector((0,4.245,78));eye=R@Vector((35,18,78))
for a in bpy.context.screen.areas:
 if a.type=='VIEW_3D':
  s=a.spaces.active;r=s.region_3d;r.view_location=target;r.view_rotation=(target-eye).to_track_quat('-Z','Y');r.view_distance=(target-eye).length;r.view_perspective='PERSP';s.shading.type='MATERIAL'
