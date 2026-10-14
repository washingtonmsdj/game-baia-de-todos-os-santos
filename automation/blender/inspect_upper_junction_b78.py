"""Mede a junção existente no referencial do saguão; não altera geometria."""
import bpy, json
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
scene = bpy.context.scene
floor = scene.objects['SUPERIOR | piso saguão']
frame = scene.frame_current
scene.frame_set(65024)
matrix = floor.matrix_world.copy()
matrix.translation.z = 0
inverse = matrix.inverted()
rows = []
dg = bpy.context.evaluated_depsgraph_get()
for ob in scene.objects:
    if ob.type != 'MESH' or not ob.visible_get():
        continue
    ev = ob.evaluated_get(dg)
    pts = [inverse @ ev.matrix_world @ Vector(p) for p in ev.bound_box]
    lo = [min(p[i] for p in pts) for i in range(3)]
    hi = [max(p[i] for p in pts) for i in range(3)]
    if hi[0] < -10 or lo[0] > 7 or hi[1] < -10 or lo[1] > 10 or hi[2] < 69.8 or lo[2] > 75.1:
        continue
    if any(c.name.startswith(('SOURCE_GEOREF', 'QA |')) for c in ob.users_collection):
        continue
    exact = {}
    if ob.name.startswith(('SUPERIOR | posterior', 'LAC R30B02 | Lambril marmore | SUPERIOR | posterior', 'LAC R30B02 | Rodape escuro | SUPERIOR | posterior', 'CALIBRADO | passarela piso')):
        mesh_points = [inverse @ ev.matrix_world @ v.co for v in ev.data.vertices]
        exact = {'mesh_min': [min(p[i] for p in mesh_points) for i in range(3)],
                 'mesh_max': [max(p[i] for p in mesh_points) for i in range(3)],
                 'vertices_local': [list(p) for p in mesh_points] if len(mesh_points) < 100 else None}
    rows.append({'name': ob.name, 'local_min': lo, 'local_max': hi, **exact,
                 'collections': [c.name for c in ob.users_collection],
                 'materials': [m.name if m else None for m in ob.data.materials],
                 'modifiers': [(m.name, m.type) for m in ob.modifiers],
                 'properties': {k: ob[k] for k in ob.keys() if isinstance(ob[k], (str, int, float, bool))}})
report = {'source': bpy.data.filepath, 'frame': 65024,
          'measurement_frame': [list(r) for r in matrix], 'objects': rows}
out = ROOT/'docs/reports/blender/lacerda-corridor/junction_before_b78.json'
out.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
scene.frame_set(frame)
print(json.dumps({'inspected': len(rows), 'report': out.relative_to(ROOT).as_posix()}))
