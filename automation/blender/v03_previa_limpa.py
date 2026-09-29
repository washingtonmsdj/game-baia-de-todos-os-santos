import bpy
from pathlib import Path
from mathutils import Vector
s=bpy.context.scene
old=s.render.engine;s.render.engine='BLENDER_WORKBENCH'
s.display.shading.show_shadows=False;s.display.shading.show_cavity=False
c=s.camera;p=c.location.copy();r=c.rotation_euler.copy();scale=c.data.ortho_scale
for end,label in [(-1,'frente'),(1,'traseira')]:
    c.location=(0,end*12,1.8);c.rotation_euler=(Vector((0,0,1.8))-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=3.9
    s.render.filepath=str(Path(bpy.data.filepath).parent/'assets'/('onibus_v03_'+label+'.png'));bpy.ops.render.render(write_still=True)
c.location=p;c.rotation_euler=r;c.data.ortho_scale=scale;s.render.engine=old
