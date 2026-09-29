import bpy
from pathlib import Path
from mathutils import Vector
s=bpy.context.scene
for o in s.objects:
    if not o.name.startswith('BUS03 | ') or o.type!='MESH':continue
    if any(t in o.name for t in ['retorno lateral','uniao teto']):continue
    normals=[]
    for v in o.data.vertices:
        x,y,z=v.co
        nx=.8*x**3/(1.25**4)
        normals.append(Vector((nx,-1,.13 if z>1.3 else 0)).normalized() if y<0 else Vector((nx,1,.045 if z>2.25 else 0)).normalized())
    o.data.normals_split_custom_set_from_vertices(normals)
bpy.data.libraries.write(str(Path(bpy.data.filepath).parent/'assets'/'onibus_torino_31065_v03.blend'),{s},fake_user=True,compress=True)
