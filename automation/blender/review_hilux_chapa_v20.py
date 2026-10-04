"""Revisão próxima da superfície externa, neutra e com linhas de reflexo."""
import bpy,json
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
assert not bpy.app.background and Path(bpy.data.filepath).name=='hilux_chapa_v20.blend'
cam=s.camera;old=cam.matrix_world.copy();old_type=cam.data.type;old_scale=cam.data.ortho_scale
old_engine=s.render.engine;old_res=(s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage)
sh=s.display.shading;old_light=sh.light;old_studio=sh.studio_light
s.render.engine='BLENDER_WORKBENCH';s.render.resolution_x=1600;s.render.resolution_y=1100;s.render.resolution_percentage=100
views=[('traseira',(3.5,6,3.65),(0,.72,1.50),2.6,'STUDIO','paint.sl'),('frente',(7,-8,3.7),(0,-.9,1.16),4.3,'STUDIO','paint.sl'),('reflexo-traseira',(3.5,6,3.65),(0,.72,1.50),2.6,'MATCAP','check_reflection_horizontal.exr'),('reflexo-lateral',(8,.1,2.4),(0,.10,1.15),3.2,'MATCAP','check_reflection_vertical.exr')]
try:
 for name,pos,target,scale,light,studio in views:
  sh.light=light;sh.studio_light=studio;sh.show_cavity=False;sh.show_shadows=False
  cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=scale
  s.render.filepath=str(r/f'artifacts/vehicles/rondesp/v20-{name}.png');bpy.ops.render.render(write_still=True)
finally:
 cam.matrix_world=old;cam.data.type=old_type;cam.data.ortho_scale=old_scale
 s.render.engine=old_engine;s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage=old_res
 sh.light=old_light;sh.studio_light=old_studio
print('Vistas de revisão V20 publicadas')
