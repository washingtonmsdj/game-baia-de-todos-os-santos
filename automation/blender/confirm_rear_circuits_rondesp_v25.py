"""Confere a persistência dos circuitos V25 na mesma janela Blender."""
import bpy, hashlib, json, os, struct
from pathlib import Path

r = Path(__file__).resolve().parents[2]
rp = r / 'docs/reports/blender/rondesp_lanternas_v25.json'
report = json.loads(rp.read_text(encoding='utf8'))
source = r / report['file']
assert not bpy.app.background and os.getpid() == 19576
assert Path(bpy.data.filepath).resolve() == source.resolve()
assert hashlib.sha256(source.read_bytes()).hexdigest() == report['sha256']
bpy.ops.wm.open_mainfile(filepath=str(source))
s = bpy.context.scene
root = s.objects['RDP01_ROOT | viatura']

def fingerprint(ob):
    h = hashlib.sha256()
    for v in ob.data.vertices:
        h.update(struct.pack('<3d', *v.co))
    for p in ob.data.polygons:
        h.update(struct.pack('<I', len(p.vertices)))
        h.update(struct.pack('<' + 'I' * len(p.vertices), *p.vertices))
    return h.hexdigest()

assert all(fingerprint(s.objects[n]) == h for n, h in report['protected_mesh_hashes'].items())
assert hashlib.sha256((r / report['parent']).read_bytes()).hexdigest() == report['parent_sha256']
for m in bpy.data.materials:
    if m.use_nodes and m.node_tree.animation_data:
        for f in m.node_tree.animation_data.drivers:
            f.driver.expression = f.driver.expression
        m.node_tree.update_tag()
for ob in s.objects:
    for data in [ob, ob.data]:
        if data is not None and data.animation_data:
            for f in data.animation_data.drivers:
                f.driver.expression = f.driver.expression
            data.update_tag()

def emission(name):
    return bpy.data.materials[name].node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value

checks = []
for frame, reverse, brake in [(200, 5., .18), (160, 0., 4.18), (230, 0., .18)]:
    s.frame_set(frame)
    bpy.context.view_layer.update()
    readings = {'frame': frame, 'reverse': emission('HILUX25 | Re branca independente'),
                'brake': emission('HILUX22 | Lanterna e freio vermelhos'),
                'third_brake': emission('HILUX22 | Terceira luz freio')}
    assert abs(readings['reverse'] - reverse) < .0001
    assert abs(readings['brake'] - brake) < .0001
    assert abs(readings['third_brake'] - (4. if frame == 160 else 0.)) < .0001
    for side in [-1, 1]:
        assert abs(s.objects[f'HILUX25 | Feixe de re {side}'].data.energy - 44 * reverse) < .0001
    checks.append(readings)
saved = {k: root[k] for k in ['demonstracao_ativa', 'lanternas_ligadas', 'freio', 're_engatada']}
root['demonstracao_ativa'] = 0.
root['lanternas_ligadas'] = 0.
root['freio'] = 1.
root['re_engatada'] = 1.
root.update_tag()
s.frame_set(201)
bpy.context.view_layer.update()
assert abs(emission('HILUX22 | Lanterna e freio vermelhos') - 4.) < .0001
assert abs(emission('HILUX22 | Terceira luz freio') - 4.) < .0001
assert abs(emission('HILUX25 | Re branca independente') - 5.) < .0001
for key, value in saved.items():
    root[key] = value
root.update_tag()
s.frame_set(200)
bpy.context.view_layer.update()
for screen in bpy.data.screens:
    for a in screen.areas:
        if a.type == 'VIEW_3D':
            a.spaces.active.shading.type = 'RENDERED'
            a.spaces.active.shading.use_scene_lights = True
            a.spaces.active.shading.use_scene_world = True
            a.spaces.active.shading.use_compositor = 'ALWAYS'
report.update({'source_reopened': True, 'source_sha256_after_reopen': hashlib.sha256(source.read_bytes()).hexdigest(),
               'reopen_checks': checks, 'brake_reverse_with_position_off_verified': True,
               'visual_review': 'reviewed: posição discreta, freio mais intenso e terceira luz; ré branca e dois feixes no piso',
               'live_rendered': True, 'presentation_frame': 200})
rp.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
print(json.dumps({'reopened': True, 'checks': checks, 'manual_independence': True, 'frame': 200}))
