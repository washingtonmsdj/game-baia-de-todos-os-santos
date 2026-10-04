"""Vistas leves de modelagem na janela visível, sem build/testes."""
import bpy
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
assert not bpy.app.background and Path(bpy.data.filepath).name=='marrom_v10.blend'
old=s.render.engine;matrix=s.camera.matrix_world.copy()
s.render.engine='BLENDER_WORKBENCH';s.display.shading.color_type='MATERIAL';s.display.shading.light='STUDIO';s.display.shading.studio_light='paint.sl';s.display.shading.show_cavity=False
s.render.resolution_x=1200;s.render.resolution_y=800;s.render.resolution_percentage=100
for name,pos in [('frente',(-7,-8,4.1)),('traseira',(-7,8,3.3))]:
    s.camera.location=pos;s.camera.rotation_euler=(Vector((0,.16,1.04))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=6.5
    s.render.filepath=str(r/f'artifacts/vehicles/rondesp/v10-{name}.png');bpy.ops.render.render(write_still=True)
s.render.engine=old;s.camera.matrix_world=matrix
