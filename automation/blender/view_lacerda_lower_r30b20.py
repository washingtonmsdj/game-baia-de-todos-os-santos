"""Inspecao visual da fachada de acesso na Cidade Baixa."""
import bpy
from mathutils import Vector,Matrix
R=Matrix.Rotation(bpy.data.objects['CASCA | parede lateral'].rotation_euler.z,4,'Z')
target=R@Vector((-82.2,4.2,11.0))
eye=R@Vector((-106.0,4.2,15.0))
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type!='VIEW_3D':continue
        s=area.spaces.active;r=s.region_3d
        r.view_perspective='PERSP';r.view_location=target
        r.view_rotation=(target-eye).to_track_quat('-Z','Y')
        r.view_distance=(target-eye).length
        s.shading.type='MATERIAL'
