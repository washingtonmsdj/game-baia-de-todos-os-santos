"""Passe candidato de carroceria V09, exclusivamente na janela Blender visível.

Aplicado em 03/10/2026; continuar pelo catálogo, não reaplicar na revisão atual.
Não executa renders nem exporta runtime. Não reaplicar sobre o resultado.
"""
import ast
import hashlib
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector

repo = Path(__file__).resolve().parents[2]
scene = bpy.context.scene
catalog = json.loads((repo / 'world/vehicles/catalog.json').read_text(encoding='utf-8'))
vehicle = next(v for v in catalog['vehicles'] if v['asset_id'] == 'vehicle-rondesp-pickup')
source = repo / vehicle['authoring_base']['file']
out = repo / 'blender/assets/vehicles/rondesp-pickup/marrom_v09.blend'
assert not bpy.app.background, 'Somente na instância visível.'
assert source.name == 'marrom_v08.blend'
assert Path(bpy.data.filepath).resolve() == source.resolve()
assert hashlib.sha256(source.read_bytes()).hexdigest() == vehicle['authoring_base']['sha256']
assert not out.exists(), 'Não sobrescrever revisão existente.'

prefix = 'RDP01 | HILUX06 | '
hood = scene.objects[prefix + 'Capô e ombros estampados']
fenders = [scene.objects[prefix + 'Para-lama dianteiro ' + str(s)] for s in (-1, 1)]
assert len(hood.data.vertices) == 67 * 73
assert all(len(o.data.vertices) == 73 * 31 for o in fenders)
for fn in ast.parse((repo / 'automation/blender/rebuild_hilux_reference_v06.py').read_text(encoding='utf-8')).body:
    if isinstance(fn, ast.FunctionDef) and fn.name in ('interp', 'sidewidth', 'arch'):
        exec(compile(ast.Module(body=[fn], type_ignores=[]), '<secoes-v06>', 'exec'), globals())

def signature(o):
    """Geometria base e transforms: controle das peças fora do escopo."""
    data = {'matrix': [list(r) for r in o.matrix_world], 'type': o.type}
    if o.type == 'MESH':
        data['vertices'] = [tuple(v.co) for v in o.data.vertices]
        data['faces'] = [tuple(p.vertices) for p in o.data.polygons]
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

changed_names = {hood.name, *(o.name for o in fenders)}
seams = [scene.objects[prefix + 'Junta capô ' + str(s)] for s in (-1, 1)]
changed_names.update(o.name for o in seams)
protected = {o.name: signature(o) for o in scene.objects if o.name not in changed_names}
before = {o.name: signature(o) for o in [hood, *fenders]}

# O companion pode marcar a apresentação como suja ao iniciar. Conservar a sessão
# integral antes de mutar, inclusive eventuais alterações manuais ainda não salvas.
recovery = repo / 'artifacts/vehicles/rondesp/pre-v09-visible-session.blend'
assert not recovery.exists(), 'Checkpoint já existe: inspecionar antes de repetir.'
bpy.data.libraries.write(str(recovery), {scene}, path_remap='RELATIVE', fake_user=True, compress=True)

def upper(u, v):
    """Chapa abaulada; borda frontal mantida para encaixe de faróis/máscara.

    Parâmetros autorais interpretados das fotos, não medidas da Toyota.
    O centro ganha coroa, e o ombro cai até o para-lama sem quina rígida.
    """
    f = 2 * v - 1
    w = .9275 - .093 * u**3 - .032 * math.sin(math.pi * u)
    yf = -2.435 + .49 * abs(f)**3.5
    y = yf + (-.975 - yf) * u
    old_z = (1.137 + .10 * abs(f)**2.8) * (1-u) + 1.303*u
    old_z += .025 * math.sin(math.pi*u) + .024 * (1-f*f)*u
    old_z += .008 * math.exp(-((abs(f)-.63)/.12)**2)*math.sin(math.pi*u)
    old_z -= .025 * abs(f)**8 * math.sin(math.pi*u)
    # Envelope nulo nos extremos: preserva frente e ligação com o cowl.
    dome = .075 * math.sin(math.pi*u)**.85 * (1-f*f)
    return Vector((w*f, y, old_z + dome))

def hermite(a, b, ma, mb, t):
    return (2*t**3-3*t*t+1)*a + (t**3-2*t*t+t)*ma + (-2*t**3+3*t*t)*b + (t**3-t*t)*mb

for i in range(67):
    for j in range(73):
        hood.data.vertices[i*73+j].co = upper(i/66, j/72)
hood.data.update()

for side, ob in zip((-1, 1), fenders):
    for i in range(73):
        u = i/72
        edge = upper(u, (side+1)/2)
        y = edge.y
        low = arch(y, -1.43)
        # Bordo da caixa de roda permanece; raio nasce no ombro da chapa.
        for j in range(31):
            t = j/30
            z = low + (edge.z-low)*t
            base = Vector((side*sidewidth(y,z), y, z))
            join = .65
            if t <= join:
                co = base
            else:
                zj = low + (edge.z-low)*join
                a = Vector((side*sidewidth(y,zj), y, zj))
                b = edge
                # Tangente transversal do capô, entrando pelo lado externo.
                near = upper(u, .002 if side == -1 else .998)
                tangent = (near-edge).normalized()
                length = max((b-a).length, .025)
                ma = Vector((0, 0, length))
                mb = tangent*length
                co = hermite(a, b, ma, mb, (t-join)/(1-join))
            ob.data.vertices[i*31+j].co = co
    # Remover normais customizadas antigas: eram calculadas para outra superfície.
    if ob.data.has_custom_normals:
        ob.data.normals_split_custom_set([(0, 0, 0)]*len(ob.data.loops))
    ob.data.update()
    seam = scene.objects[prefix + 'Junta capô ' + str(side)]
    points = seam.data.splines[0].points
    for j, p in enumerate(points):
        p.co = (*upper(j/(len(points)-1), (side*.84+1)/2), 1)

for o in [hood, *fenders]:
    o['boas_v09_shape_status'] = 'candidate; coroa do capô e tangência dos ombros interpretadas das fotografias'
    o['boas_reference_ids'] = 'hilux-std-stock-front;hilux-2024-std-dealer-side;rondesp-31110-front'
    for p in o.data.polygons:
        p.use_smooth = True
    assert all(math.isfinite(c) for v in o.data.vertices for c in v.co)

bpy.context.view_layer.update()
assert all(signature(scene.objects[n]) == h for n,h in protected.items()), 'Peça fora do escopo mudou.'
assert all(signature(scene.objects[n]) != h for n,h in before.items())
scene.name = 'VIATURA | Rondesp Hilux marrom v09'
scene['boas_review_status'] = 'candidate; requer comparação visual; catálogo ainda aponta V08'
bpy.data.libraries.write(str(out), {scene}, path_remap='RELATIVE', fake_user=True, compress=True)
report = {
    'asset_id': 'vehicle-rondesp-pickup', 'status': 'candidate_pending_visual_review',
    'file': out.relative_to(repo).as_posix(), 'parent': source.relative_to(repo).as_posix(),
    'sha256': hashlib.sha256(out.read_bytes()).hexdigest(),
    'changes': ['coroa transversal do capô', 'transição tangente entre capô e para-lamas'],
    'changed_objects': sorted(changed_names), 'protected_objects_verified': len(protected),
    'source_reopened': False, 'visual_review': 'pending', 'runtime_exported': False,
    'catalog_promoted': False,
    'pending': ['conferência visual multivista', 'laterais e teto da cabine', 'capota', 'brasão e camuflagem exata'],
}
report_path = repo / 'docs/reports/blender/rondesp_marrom_v09.json'
report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def reopen():
    bpy.ops.wm.open_mainfile(filepath=str(out))
    r = json.loads(report_path.read_text(encoding='utf-8'))
    r['source_reopened'] = Path(bpy.data.filepath).resolve() == out.resolve()
    report_path.write_text(json.dumps(r, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    return None

bpy.app.timers.register(reopen, first_interval=.5)
