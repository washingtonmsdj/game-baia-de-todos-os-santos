"""Inspecao pontual da torre na janela ativa do Blender."""
import bpy, json
from mathutils import Vector, Matrix
from pathlib import Path

names=[]
for o in bpy.data.objects:
    n=o.name.lower()
    if any(s in n for s in ('torre', 'galeria', 'fachada poço', 'venezian', 'fresta')):
        names.append({'name':o.name,'visible':not o.hide_get(),'materials':[m.name if m else None for m in o.data.materials] if o.type=='MESH' else [],'dimensions':[round(v,2) for v in o.dimensions]})
print('TOWER_INSPECTION '+json.dumps(names[:140],ensure_ascii=False))
out=Path(__file__).resolve().parents[2]/'artifacts/lacerda/r30b19_tower_objects.json'
out.write_text(json.dumps(names,ensure_ascii=False,indent=2),encoding='utf8')

rot=Matrix.Rotation(bpy.data.objects['CASCA | parede lateral'].rotation_euler.z,4,'Z')
target=rot @ Vector((-69.0,4.2,42.0))
eye=rot @ Vector((-110.0,17.0,44.0))
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        r=area.spaces.active.region_3d
        r.view_perspective='PERSP'
        r.view_location=target
        r.view_distance=(target-eye).length
        r.view_rotation=(target-eye).to_track_quat('-Z','Y')
        area.spaces.active.shading.type='MATERIAL'
        break
