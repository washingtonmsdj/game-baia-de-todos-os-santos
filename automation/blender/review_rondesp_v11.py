"""Vistas de modelagem na sessão visível, sem executar build ou testes."""
import bpy
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
assert not bpy.app.background and Path(bpy.data.filepath).name=='marrom_v11.blend'
engine=s.render.engine;matrix=s.camera.matrix_world.copy();frame=s.frame_current
s.render.engine='BLENDER_WORKBENCH'
sh=s.display.shading;sh.color_type='MATERIAL';sh.light='STUDIO';sh.studio_light='paint.sl';sh.show_cavity=False;sh.studiolight_rotate_z=.5
s.render.resolution_x=1200;s.render.resolution_y=800;s.render.resolution_percentage=100
views=[('frente',(-7,-8,3.2),(0,.16,1.03),6.3),('encaixe',(-6,4,2.2),(0,.87,1.25),3.3)]
if s.get('boas_v11_rig'):
    views=[('portas-esq',(-7,-7,4.5),(0,.16,1.03),6.8),('portas-dir',(7,7,4.5),(0,.16,1.03),6.8),('direcao',(-7,-8,1.8),(0,.16,1.03),6.3),('encaixe-final',(-6,4,2.2),(0,.87,1.25),3.3)]
for name,pos,target,scale in views:
    if s.get('boas_v11_rig'):s.frame_set(55 if name.startswith('portas') else 115 if name=='direcao' else 1)
    s.camera.location=pos;s.camera.rotation_euler=(Vector(target)-s.camera.location).to_track_quat('-Z','Y').to_euler()
    s.camera.data.type='ORTHO';s.camera.data.ortho_scale=scale
    s.render.filepath=str(r/f'artifacts/vehicles/rondesp/v11-{name}.png');bpy.ops.render.render(write_still=True)
s.render.engine=engine;s.camera.matrix_world=matrix;s.frame_set(frame)
