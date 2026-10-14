"""Remove a sobreposição da verga herdada com os retornos prolongados da B78."""
import bpy, bmesh, json, hashlib, runpy
from pathlib import Path
from mathutils import Matrix
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'docs/reports/blender/lacerda-corridor'
report = json.loads((OUT/'scene_b78.json').read_text(encoding='utf8'))
assert Path(bpy.data.filepath).resolve() == (ROOT/report['source_after']['file']).resolve()
assert not any(c['object'] == 'SUPERIOR | posterior sobre passarela' for c in report['changed_meshes'])
scene = bpy.context.scene; scene.frame_set(report['baseline_frame'])
matrix = Matrix(report['measurement_frame']); inverse = matrix.inverted()
bridge = scene.objects['CALIBRADO | passarela piso 28.71 x 6.00m']
points = [inverse @ bridge.matrix_world @ v.co for v in bridge.data.vertices]
edges = [min(p.y for p in points), max(p.y for p in points)]
ob = scene.objects['SUPERIOR | posterior sobre passarela']
helpers = runpy.run_path(str(ROOT/'automation/blender/component_fingerprint.py'))
sig = helpers['signature']; world_matrix = helpers['world_matrix']
before = sig(ob)
points = [inverse @ ob.matrix_world @ v.co for v in ob.data.vertices]
old_edges = [min(p.y for p in points), max(p.y for p in points)]
assert abs(old_edges[0]+4.8) < 1e-4 and abs(old_edges[1]-4.8) < 1e-4
mesh = ob.data.copy(); mesh.name = ob.name+' | encontro B78'; ob.data = mesh
local_to_frame = inverse @ world_matrix(ob); back = local_to_frame.inverted()
for vertex in mesh.vertices:
    p = local_to_frame @ vertex.co
    p.y = edges[0]+(p.y-old_edges[0])*(edges[1]-edges[0])/(old_edges[1]-old_edges[0])
    vertex.co = back @ p
mesh.update(); bm = bmesh.new(); bm.from_mesh(mesh)
bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces)); bm.to_mesh(mesh); bm.free(); mesh.update()
ob['boas_revision'] = 'R30B.78'; ob['boas_location_id'] = 'elevador-lacerda'
ob['boas_provenance_ids'] = json.dumps(['derived:lacerda-junction-b78'])
ob['boas_geographic_ssot_id'] = scene['boas_geographic_ssot_id']
ob['classification'] = 'ERROR'; ob['reference_status'] = 'partial'
ob['boas_b78_reason'] = 'Verga limitada ao vão existente da passarela; elimina faces coplanares sobrepostas aos retornos.'
after = sig(ob); assert before['transform'] == after['transform'] and before['materials'] == after['materials']
report['changed_meshes'].append({'object': ob.name, 'side': 'lintel', 'edges_before': old_edges,
                                'edges_after': edges, 'mesh_before': before['geometry_sha256'],
                                'mesh_after': after['geometry_sha256']})
# Novos objetos podem expor matrix_world em cache antes da avaliação. Derivar
# dos transforms persistentes e gravar proxies em coordenadas mundo/identity.
# Não aplicar offset manual nem reutilizar uma matriz ainda não avaliada.
for name in ('SUPERIOR | posterior lateral', 'SUPERIOR | posterior lateral.001'):
    visual = scene.objects[name]
    collider = scene.objects['B78 | COLLISION | '+name]
    mesh = visual.data.copy(); mesh.name = collider.name+' | mundo verificado'
    transform = world_matrix(visual)
    for vertex in mesh.vertices: vertex.co = transform @ vertex.co
    mesh.update(); collider.data = mesh; collider.matrix_basis = Matrix.Identity(4)
    collider['boas_transform_derivation'] = 'Vértices do retorno em mundo pelo matrix_basis/hierarquia persistente; proxy identity'
report['collider_transform_correction'] = 'Auditoria detectou matriz em cache inválida nos proxies intermediários; malha final derivada deterministicamente em mundo, transform identity.'
bpy.context.view_layer.update()
scene.frame_set(65024)
destination = ROOT/report['source_after']['file']
# B78 ainda é candidata não validada; B77B continua preservada. Não gerar .blend1 redundante.
save_versions = bpy.context.preferences.filepaths.save_version
try:
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(destination), compress=True)
finally:
    bpy.context.preferences.filepaths.save_version = save_versions
with destination.open('rb') as stream: report['source_after']['sha256'] = hashlib.file_digest(stream, 'sha256').hexdigest()
(OUT/'scene_b78.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
print(json.dumps({'saved': report['source_after'], 'edited_meshes': len(report['changed_meshes'])}))
