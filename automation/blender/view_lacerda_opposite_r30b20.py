"""Posiciona a vista na face oposta da torre principal."""
import bpy
from mathutils import Vector,Matrix
R=Matrix.Rotation(bpy.data.objects['CASCA | parede lateral'].rotation_euler.z,4,'Z')
target=R@Vector((-68.2,4.2,43.0))
eye=R@Vector((-45.0,12.0,45.0))
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type!='VIEW_3D':continue
        s=area.spaces.active;r=s.region_3d
        r.view_perspective='PERSP';r.view_location=target
        r.view_rotation=(target-eye).to_track_quat('-Z','Y')
        r.view_distance=(target-eye).length
        s.shading.type='MATERIAL'
