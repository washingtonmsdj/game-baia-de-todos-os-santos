"""Vistas de forma da V09, calculadas na mesma instância visível."""
import bpy
from pathlib import Path
from mathutils import Vector

repo = Path(__file__).resolve().parents[2]
s = bpy.context.scene
assert not bpy.app.background
assert Path(bpy.data.filepath).name == 'marrom_v09.blend'
engine = s.render.engine
camera_matrix = s.camera.matrix_world.copy()
old_type, old_scale = s.camera.data.type, s.camera.data.ortho_scale
old_path = s.render.filepath
old_res = (s.render.resolution_x, s.render.resolution_y, s.render.resolution_percentage)
s.render.engine = 'BLENDER_WORKBENCH'
s.display.shading.light = 'STUDIO'
s.display.shading.studio_light = 'paint.sl'
s.display.shading.color_type = 'MATERIAL'
s.display.shading.show_cavity = False
s.display.shading.show_shadows = True
s.render.resolution_x, s.render.resolution_y, s.render.resolution_percentage = 1200, 750, 100
try:
    for name, pos, scale in [('frente',(-7,-8,3.1),6.5),('lateral',(-10,.16,1.1),6.5),('traseira',(-7,8,3.1),6.5)]:
        s.camera.location = pos
        s.camera.rotation_euler = (Vector((0,.16,1.03))-s.camera.location).to_track_quat('-Z','Y').to_euler()
        s.camera.data.type = 'ORTHO'
        s.camera.data.ortho_scale = scale
        s.render.filepath = str(repo / f'artifacts/vehicles/rondesp/v09-{name}.png')
        bpy.ops.render.render(write_still=True)
    s.render.engine = 'CYCLES'
    s.cycles.samples = 24
    s.cycles.device = 'CPU'
    s.cycles.use_denoising = True
    s.render.threads_mode = 'FIXED'; s.render.threads = 8
    s.render.resolution_x, s.render.resolution_y = 1050, 680
    s.camera.location = (-7,-8,3.1)
    s.camera.rotation_euler = (Vector((0,.16,1.03))-s.camera.location).to_track_quat('-Z','Y').to_euler()
    s.render.filepath = str(repo / 'artifacts/vehicles/rondesp/v09-materiais.png')
    bpy.ops.render.render(write_still=True)
finally:
    s.render.engine = engine
    s.camera.matrix_world = camera_matrix
    s.camera.data.type, s.camera.data.ortho_scale = old_type, old_scale
    s.render.filepath = old_path
    s.render.resolution_x, s.render.resolution_y, s.render.resolution_percentage = old_res
