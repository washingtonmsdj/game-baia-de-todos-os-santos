"""Inspeção visual da carroceria na sessão visível, sem exportar runtime."""
import bpy, json
from pathlib import Path
from mathutils import Vector

r = Path(__file__).resolve().parents[2]
s = bpy.context.scene
assert not bpy.app.background
assert Path(bpy.data.filepath).name == 'hilux_carroceria_v16.blend'
body = s.objects['HILUX | CARROCERIA PRINCIPAL']
old_engine = s.render.engine
old_camera = s.camera.matrix_world.copy()
old_type, old_scale = s.camera.data.type, s.camera.data.ortho_scale
old_res = (s.render.resolution_x, s.render.resolution_y, s.render.resolution_percentage)
s.render.engine = 'BLENDER_WORKBENCH'
sh = s.display.shading
sh.color_type = 'OBJECT'
sh.light = 'STUDIO'
sh.studio_light = 'paint.sl'
sh.show_cavity = False
sh.show_shadows = False
sh.background_type = 'WORLD'
s.world.color = (.08, .08, .10)
s.render.resolution_x = 1400
s.render.resolution_y = 950
s.render.resolution_percentage = 100
views = [
    ('cacamba', (7, 8, 4.8), (0, .17, 1.03), 6.1),
    ('encontro-cabine', (5, 5, 3.2), (0, 1.10, 1.32), 2.65),
    ('frente', (-7, -8, 3.6), (0, .17, 1.03), 6.1),
    ('batente-dianteiro', (5, -5, 2.8), (.3, -.83, .98), 2.6),
    ('interior-cacamba', (4, 7, 6), (0, 1.87, .9), 2.65),
    ('tampa', (4, 7, 2.9), (0, 2.62, .99), 2.8),
    ('arco-traseiro', (7, 3, 1.6), (.4, 1.80, .86), 2.5),
    ('lateral', (8, .10, 1.45), (0, .10, 1.05), 6.1),
]
views = [v for v in views if v[0] in ('frente', 'batente-dianteiro')]
for name, pos, target, zoom in views:
    s.camera.location = pos
    s.camera.rotation_euler = (Vector(target) - s.camera.location).to_track_quat('-Z', 'Y').to_euler()
    s.camera.data.type = 'ORTHO'
    s.camera.data.ortho_scale = zoom
    s.render.filepath = str(r / f'artifacts/vehicles/rondesp/v16-carroceria-{name}.png')
    bpy.ops.render.render(write_still=True)
s.render.engine = old_engine
s.camera.matrix_world = old_camera
s.camera.data.type, s.camera.data.ortho_scale = old_type, old_scale
s.render.resolution_x, s.render.resolution_y, s.render.resolution_percentage = old_res
rp = r / 'docs/reports/blender/hilux_carroceria_v16.json'
report = json.loads(rp.read_text(encoding='utf-8'))
report['scene_observation'] = {
    'file': Path(bpy.data.filepath).relative_to(r).as_posix(),
    'visible_meshes': [o.name for o in s.objects if o.type == 'MESH' and o.visible_get()],
    'body_base_vertices': len(body.data.vertices),
    'body_base_faces': len(body.data.polygons),
    'modifiers': [(m.name, m.type) for m in body.modifiers],
}
rp.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
