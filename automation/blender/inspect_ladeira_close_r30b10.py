"""Aproxima o viewport da contenção sem alterar geometria."""
import bpy, json
from pathlib import Path
from mathutils import Matrix, Vector

root=Path(__file__).resolve().parents[2]
rot=Matrix.Rotation(bpy.data.objects['CASCA | parede lateral'].rotation_euler.z,4,'Z')
terrain=bpy.data.objects['MVP | terreno corrigido | colisão estática']
index=next(i for i,m in enumerate(terrain.data.materials) if m and m.name=='LAC R30B09 | pedra irregular da contenção')
points=[rot.inverted() @ terrain.matrix_world @ p.center for p in terrain.data.polygons if p.material_index==index]
bounds=[[round(min(p[i] for p in points),2),round(max(p[i] for p in points),2)] for i in range(3)]
eye=rot @ Vector((-49,-5,42))
target=rot @ Vector((-29,1,42))
for area in bpy.context.screen.areas:
    if area.type!='VIEW_3D':continue
    space=area.spaces.active
    space.region_3d.view_perspective='PERSP'
    space.region_3d.view_location=target
    space.region_3d.view_rotation=(target-eye).to_track_quat('-Z','Y')
    space.region_3d.view_distance=38
(root/'artifacts/lacerda/r30b10_stone_bounds.json').write_text(json.dumps({'faces':len(points),'bounds_local':bounds},indent=2),encoding='utf8')
print(json.dumps({'faces':len(points),'bounds_local':bounds}))
