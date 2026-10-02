"""Vista diagonal da borda da Ladeira, no Blender visível."""
import bpy
from mathutils import Matrix,Vector
rot=Matrix.Rotation(bpy.data.objects['CASCA | parede lateral'].rotation_euler.z,4,'Z')
target=rot @ Vector((-35,4,45))
eye=rot @ Vector((-115,70,12))
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type!='VIEW_3D':continue
        sp=area.spaces.active
        sp.region_3d.view_perspective='PERSP'
        sp.region_3d.view_rotation=(target-eye).to_track_quat('-Z','Y')
        sp.region_3d.view_location=target
        sp.region_3d.view_distance=(target-eye).length
        sp.shading.type='MATERIAL'
print('vista da borda da Ladeira')
