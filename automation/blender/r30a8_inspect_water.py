import bpy
from mathutils import Vector

scene = bpy.context.scene
print('ENGINE', scene.render.engine)
print('FILE', bpy.data.filepath, 'DIRTY', bpy.data.is_dirty)

for cname in ('24 ORLA | Baía de Todos-os-Santos e cais OSM',
              '27 MAR | Forte São Marcelo',
              '32.7 GAMEPLAY | WATER',
              '33.6 RUNTIME | WATER'):
    coll = bpy.data.collections.get(cname)
    print('\nCOLLECTION', cname, bool(coll))
    if coll is None:
        continue
    for obj in coll.objects:
        bounds = None
        if obj.type == 'MESH':
            points = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
            bounds = tuple(round(v, 2) for v in (
                min(p.x for p in points), max(p.x for p in points),
                min(p.y for p in points), max(p.y for p in points),
                min(p.z for p in points), max(p.z for p in points)))
        print('OBJECT', obj.name, obj.type, 'bounds', bounds,
              'mods', [(m.name, m.type) for m in obj.modifiers],
              'mats', [m.name for m in getattr(obj.data, 'materials', []) if m])

import json
from pathlib import Path
report = {'engine': scene.render.engine, 'file': bpy.data.filepath, 'dirty': bpy.data.is_dirty, 'collections': {}}
for cname in ('24 ORLA | Baía de Todos-os-Santos e cais OSM', '27 MAR | Forte São Marcelo', '32.7 GAMEPLAY | WATER', '33.6 RUNTIME | WATER'):
    coll = bpy.data.collections.get(cname)
    items = []
    if coll:
        for obj in coll.objects:
            bounds = None
            if obj.type == 'MESH':
                pts = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
                bounds = [min(p.x for p in pts), max(p.x for p in pts), min(p.y for p in pts), max(p.y for p in pts), min(p.z for p in pts), max(p.z for p in pts)]
            items.append({'name': obj.name, 'type': obj.type, 'bounds': bounds, 'modifiers': [(m.name, m.type) for m in obj.modifiers], 'materials': [m.name for m in getattr(obj.data, 'materials', []) if m]})
    report['collections'][cname] = items
out = Path(bpy.path.abspath('//../docs/reports/blender/r30a8'))
out.mkdir(parents=True, exist_ok=True)
(out / 'water_inspection.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
