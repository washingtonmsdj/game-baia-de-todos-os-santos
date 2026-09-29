import bpy
from pathlib import Path
s=bpy.context.scene
assert s.name=='ONIBUS | Torino 31065 v02'
for a in bpy.context.screen.areas:
    if a.type=='VIEW_3D':
        a.spaces.active.use_local_camera=False
        a.spaces.active.camera=s.camera
        a.spaces.active.region_3d.view_perspective='CAMERA'
old=s.render.engine
s.render.engine='CYCLES'
s.cycles.samples=12
s.cycles.use_denoising=True
s.render.resolution_x=1200
s.render.resolution_y=800
s.render.resolution_percentage=100
s.render.filepath=str(Path(bpy.data.filepath).parent/'assets'/'onibus_torino_31065_v02.png')
bpy.ops.render.render(write_still=True)
s.render.engine=old
print(s.render.filepath)
