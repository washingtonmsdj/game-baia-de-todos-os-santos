"""Inventário somente leitura dos encaixes e dos componentes articuláveis."""
import bpy, json
from pathlib import Path
from mathutils import Vector

r = Path(__file__).resolve().parents[2]
s = bpy.context.scene
assert not bpy.app.background
rows = []
for o in s.objects:
    if o.type in {'MESH', 'CURVE'}:
        pts = [o.matrix_world @ Vector(p) for p in o.bound_box]
        lo = [round(min(p[i] for p in pts), 5) for i in range(3)]
        hi = [round(max(p[i] for p in pts), 5) for i in range(3)]
    else:
        lo = hi = list(o.matrix_world.translation)
    rows.append({'name': o.name, 'type': o.type,
                 'parent': o.parent.name if o.parent else None,
                 'lo': lo, 'hi': hi,
                 'modifiers': [(m.name, m.type) for m in o.modifiers],
                 'hidden': o.hide_get(), 'render_hidden': o.hide_render})
(r / 'artifacts/vehicles/rondesp/v11-inventory.json').write_text(
    json.dumps({'file': bpy.data.filepath, 'objects': rows}, ensure_ascii=False, indent=2), encoding='utf-8')
print('Inventário dos encaixes:', len(rows), 'objetos; sem alterar a cena.')
