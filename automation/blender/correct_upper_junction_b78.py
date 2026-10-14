"""Fecha a incompatibilidade medida entre saguão e passarela, na janela MCP."""
import bpy, bmesh, json, hashlib, runpy
from pathlib import Path
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'docs/reports/blender/lacerda-corridor'
scene = bpy.context.scene
source = json.loads((ROOT/'world/areas/mvp-centro-lacerda/blender-revisions.json').read_text(encoding='utf8'))['validation_source']
assert source['revision'] == 'R30B.77B'
assert Path(bpy.data.filepath).resolve() == (ROOT/source['file']).resolve()
destination = ROOT/'blender/salvador_lacerda_r30b78_encontro_saguao_passarela.blend'
assert not destination.exists()
scene.frame_set(31978)
helpers = runpy.run_path(str(ROOT/'automation/blender/component_fingerprint.py'))
signature = helpers['signature']; world_matrix = helpers['world_matrix']

def state(ob):
    try:
        s = signature(ob)
    except RuntimeError:
        s = {'type': ob.type, 'transform': [list(r) for r in ob.matrix_world],
             'data_name': ob.data.name if ob.data else None,
             'constraints': [(c.name, c.type) for c in ob.constraints]}
    return {'signature': s, 'parent': ob.parent.name if ob.parent else None,
            'collections': [c.name for c in ob.users_collection],
            'hide_render': ob.hide_render, 'visible': ob.visible_get(),
            'modifiers': [(m.name, m.type) for m in ob.modifiers],
            'action': ob.animation_data.action.name if ob.animation_data and ob.animation_data.action else None}

snapshot = {ob.name: state(ob) for ob in scene.objects}
protected = ROOT/'artifacts/lacerda-corridor/protected_b77b.json'
protected.write_text(json.dumps(snapshot, ensure_ascii=False), encoding='utf8')
frame = world_matrix(scene.objects['SUPERIOR | piso saguão'])
frame.translation.z = 0
inverse = frame.inverted()
bridge = scene.objects['CALIBRADO | passarela piso 28.71 x 6.00m']
bridge_pts = [inverse @ world_matrix(bridge) @ v.co for v in bridge.data.vertices]
bridge_edges = [min(p.y for p in bridge_pts), max(p.y for p in bridge_pts)]
changed = []
walls = ['SUPERIOR | posterior lateral', 'SUPERIOR | posterior lateral.001']
for side, wall_name in enumerate(walls):
    wall = scene.objects[wall_name]
    pts = [inverse @ world_matrix(wall) @ v.co for v in wall.data.vertices]
    inner = max(p.y for p in pts) if side == 0 else min(p.y for p in pts)
    outer = min(p.y for p in pts) if side == 0 else max(p.y for p in pts)
    target = bridge_edges[side]
    assert 1.69 < abs(inner-target) < 1.71, 'Controle da abertura mudou; não corrigir outra geometria.'
    for name in (wall_name, 'LAC R30B02 | Lambril marmore | '+wall_name,
                 'LAC R30B02 | Rodape escuro | '+wall_name):
        ob = scene.objects[name]
        before = signature(ob)
        mesh = ob.data.copy()
        mesh.name = name+' | encontro B78'
        ob.data = mesh
        local_to_frame = inverse @ world_matrix(ob)
        frame_to_local = local_to_frame.inverted()
        # Prolonga o retorno existente com a borda externa fixa. Lambril e rodapé
        # acompanham a mesma transformação; nenhuma posição do objeto é alterada.
        ratio = (target-outer)/(inner-outer)
        for vertex in mesh.vertices:
            p = local_to_frame @ vertex.co
            p.y = outer+(p.y-outer)*ratio
            vertex.co = frame_to_local @ p
        mesh.update()
        bm = bmesh.new(); bm.from_mesh(mesh)
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        bm.to_mesh(mesh); bm.free(); mesh.update()
        ob['boas_revision'] = 'R30B.78'
        ob['boas_location_id'] = 'elevador-lacerda'
        ob['boas_provenance_ids'] = json.dumps(['derived:lacerda-junction-b78'])
        ob['boas_geographic_ssot_id'] = scene['boas_geographic_ssot_id']
        ob['classification'] = 'ERROR'
        ob['reference_status'] = 'partial'
        ob['boas_b78_reason'] = 'Vão posterior herdado de 9,4 incompatível com passarela de 6,0; bordas conciliadas na malha existente. Dimensões físicas não levantadas.'
        after = signature(ob)
        assert before['transform'] == after['transform'] and before['materials'] == after['materials']
        changed.append({'object': name, 'side': side, 'inner_before': inner,
                        'inner_after': target, 'outer_unchanged': outer,
                        'mesh_before': before['geometry_sha256'],
                        'mesh_after': after['geometry_sha256']})

added = []
col = bpy.data.collections['COLLISION | Galerias Cidade Alta R34']
for name in walls:
    visual = scene.objects[name]
    mesh = visual.data.copy()
    transform = world_matrix(visual)
    for vertex in mesh.vertices: vertex.co = transform @ vertex.co
    mesh.update()
    ob = bpy.data.objects.new('B78 | COLLISION | '+name, mesh)
    col.objects.link(ob)
    ob.matrix_basis = Matrix.Identity(4)
    ob.hide_render = True; ob.hide_set(True)
    ob['boas_role'] = 'static_collider'
    ob['boas_location_id'] = 'elevador-lacerda'
    ob['boas_revision'] = 'R30B.78'
    ob['boas_provenance_ids'] = json.dumps(['derived:lacerda-junction-b78'])
    ob['boas_geographic_ssot_id'] = scene['boas_geographic_ssot_id']
    ob['boas_derived_from_object'] = name
    ob['boas_production_ready'] = False
    added.append(ob.name)

scene.frame_set(65024)
report = {'revision': 'R30B.78', 'source_before': source, 'baseline_frame': 31978,
          'ssot_sha256': hashlib.sha256((ROOT/'world/geographic-reference.json').read_bytes()).hexdigest(),
          'changed_meshes': changed, 'added_objects': added,
          'measurement_frame': [list(r) for r in frame],
          'opening_before_design_units': 9.4,
          'opening_after_design_units': bridge_edges[1]-bridge_edges[0],
          'lateral_gap_before_design_units': 1.7,
          'physical_dimensions_verified': False,
          'classification': 'ERROR', 'construction_detail_verified': False,
          'hero_assets_relocated': False, 'terrain_changed': False,
          'reference_media_ids': ['elevador-lacerda-front-1e24e0731977',
                                 'praca-tome-de-sousa-panorama-6ab5f847ddb9'],
          'evidence_before': 'docs/reports/blender/lacerda-corridor/junction_before_b78.json'}
bpy.ops.wm.save_as_mainfile(filepath=str(destination), compress=True)
with destination.open('rb') as f:
    sha = hashlib.file_digest(f, 'sha256').hexdigest()
report['source_after'] = {'file': destination.relative_to(ROOT).as_posix(),
                          'revision': 'R30B.78', 'sha256': sha}
(OUT/'scene_b78.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
print(json.dumps({'saved': report['source_after'], 'edited_meshes': len(changed),
                  'added_colliders': len(added), 'object_count': len(scene.objects)}))
