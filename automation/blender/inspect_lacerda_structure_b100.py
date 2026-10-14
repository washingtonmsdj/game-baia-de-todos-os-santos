"""Conferência dimensional da B100 visível; não altera a geometria."""
import bpy, json, os, runpy
from pathlib import Path
from mathutils import Matrix

root = Path(__file__).resolve().parents[2]
scene = bpy.context.scene
assert Path(bpy.data.filepath).name == 'salvador_lacerda_r30b100_corpo_superior_cobertura.blend'
prior = json.loads((root / 'docs/reports/blender/lacerda-upper-body-b100/application.json').read_text())
expected = dict(prior['preserved_signatures'])
for row in prior['changes'] + prior['added']:
    expected[row['object']] = row['after']['signature']
for row in prior['archived']:
    expected[row['object']] = row['before']
h = runpy.run_path(str(root / 'automation/blender/component_fingerprint.py'))
sig, wm = h['signature'], h['world_matrix']
inv = Matrix(json.loads((root / 'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text())['measurement_frame']).inverted()
delta = [n for n, s in expected.items() if n not in scene.objects or sig(scene.objects[n]) != s]
rows = []
for name in expected:
    if name not in scene.objects:
        continue
    o = scene.objects[name]
    if o.type != 'MESH' or not o.visible_get():
        continue
    p = [list(inv @ wm(o) @ v.co) for v in o.data.vertices]
    bounds = [[min(v[i] for v in p), max(v[i] for v in p)] for i in range(3)]
    if any(word in name.lower() for word in ('piso', 'laje', 'cobertura', 'envoltória', 'casca', 'núcleo', 'core', 'torre', 'corpo superior')):
        rows.append({'object': name, 'bounds': bounds, 'signature': sig(o), 'vertices_local': p,
                     'faces': [list(f.vertices) for f in o.data.polygons], 'collections': [c.name for c in o.users_collection],
                     'materials': [m.name if m else None for m in o.data.materials]})
out = root / 'docs/reports/blender/lacerda-floors-b101'
out.mkdir(parents=True, exist_ok=True)
r = {'file': Path(bpy.data.filepath).relative_to(root).as_posix(), 'scene': scene.name,
     'pid': os.getpid(), 'dirty': bpy.data.is_dirty, 'session_geometry_delta': delta,
     'preserved_signatures': expected, 'rows': rows}
(out / 'before.json').write_text(json.dumps(r, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
assert not delta, delta
print(json.dumps({'file': r['file'], 'pid': r['pid'], 'dirty': r['dirty'], 'compared': len(expected),
                  'structural_dimensions': [{'object': v['object'], 'bounds': v['bounds']} for v in rows]}, ensure_ascii=False))
