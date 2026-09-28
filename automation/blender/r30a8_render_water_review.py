import bpy
from pathlib import Path

scene = bpy.context.scene
camera = bpy.data.objects.get('ORLA | vista aérea Mercado, praça e Baía')
assert camera is not None
old_engine = scene.render.engine
old_camera = scene.camera
old_x = scene.render.resolution_x
old_y = scene.render.resolution_y
old_pct = scene.render.resolution_percentage
old_path = scene.render.filepath

try:
    scene.camera = camera
    camera.hide_render = False
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = 960
    scene.render.resolution_y = 540
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    output = Path(r'C:\Users\TONECOS\AppData\Local\Ordax\DevAgent\artifacts\bay-of-all-saints\r30a8-ocean-render.png')
    scene.render.filepath = str(output)
    bpy.ops.render.render(write_still=True)
    print('RENDERED', output)
finally:
    scene.render.engine = old_engine
    scene.camera = old_camera
    scene.render.resolution_x = old_x
    scene.render.resolution_y = old_y
    scene.render.resolution_percentage = old_pct
    scene.render.filepath = old_path
