"""Verifica persistência, limites de alteração, fechamento e passagem na B78."""
import bpy, bmesh, json, hashlib, math, runpy
from pathlib import Path
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'docs/reports/blender/lacerda-corridor'
report = json.loads((OUT/'scene_b78.json').read_text(encoding='utf8'))
scene = bpy.context.scene
assert Path(bpy.data.filepath).resolve() == (ROOT/report['source_after']['file']).resolve()
frame = scene.frame_current
scene.frame_set(report['baseline_frame'])
signature = runpy.run_path(str(ROOT/'automation/blender/component_fingerprint.py'))['signature']
snapshot = json.loads((ROOT/'artifacts/lacerda-corridor/protected_b77b.json').read_text(encoding='utf8'))
changed = {x['object']: x for x in report['changed_meshes']}
differences = []
for name, old in snapshot.items():
    ob = scene.objects.get(name)
    if ob is None:
        differences.append({'object': name, 'error': 'missing'}); continue
    try:
        s = signature(ob)
    except RuntimeError:
        s = {'type': ob.type, 'transform': [list(r) for r in ob.matrix_world],
             'data_name': ob.data.name if ob.data else None,
             'constraints': [(c.name, c.type) for c in ob.constraints]}
    s = json.loads(json.dumps(s))
    if name in changed:
        assert s['geometry_sha256'] == changed[name]['mesh_after']
        for key in s:
            if key != 'geometry_sha256' and s[key] != old['signature'][key]:
                differences.append({'object': name, 'error': key})
    elif s != old['signature']:
        differences.append({'object': name, 'error': 'geometry_material_transform'})
    current = {'parent': ob.parent.name if ob.parent else None,
               'collections': [c.name for c in ob.users_collection],
               'hide_render': ob.hide_render, 'visible': ob.visible_get(),
               'modifiers': json.loads(json.dumps([(m.name, m.type) for m in ob.modifiers])),
               'action': ob.animation_data.action.name if ob.animation_data and ob.animation_data.action else None}
    for key, value in current.items():
        if value != old[key]: differences.append({'object': name, 'error': key})

walls = ['SUPERIOR | posterior lateral', 'SUPERIOR | posterior lateral.001']
inverse = Matrix(report['measurement_frame']).inverted()
bridge = scene.objects['CALIBRADO | passarela piso 28.71 x 6.00m']
pts = [inverse @ bridge.matrix_world @ v.co for v in bridge.data.vertices]
edges = [min(p.y for p in pts), max(p.y for p in pts)]
seams = []; topology = []; trees = []
for side, name in enumerate(walls):
    ob = scene.objects[name]
    points = [ob.matrix_world @ v.co for v in ob.data.vertices]
    local = [inverse @ p for p in points]
    inner = max(p.y for p in local) if side == 0 else min(p.y for p in local)
    seams.append({'object': name, 'wall_inner': inner, 'bridge_edge': edges[side],
                  'gap_design_units': abs(inner-edges[side])})
    bm = bmesh.new(); bm.from_mesh(ob.data)
    topology.append({'object': name, 'nonmanifold_edges': sum(not e.is_manifold for e in bm.edges),
                     'degenerate_faces': sum(f.calc_area() < 1e-8 for f in bm.faces),
                     'volume': bm.calc_volume(signed=True),
                     'nonfinite': sum(not math.isfinite(v) for p in points for v in p)})
    bm.free()
    ob.data.calc_loop_triangles()
    tree = BVHTree.FromPolygons(points, [tuple(t.vertices) for t in ob.data.loop_triangles], all_triangles=True)
    trees.append((name, tree))
    collider = scene.objects['B78 | COLLISION | '+name]
    assert len(collider.data.vertices) == len(ob.data.vertices)
    assert [tuple(p.vertices) for p in collider.data.polygons] == [tuple(p.vertices) for p in ob.data.polygons]
    collider_error = max(((collider.matrix_world @ a.co)-(ob.matrix_world @ b.co)).length
                         for a, b in zip(collider.data.vertices, ob.data.vertices))
    topology[-1]['collider_max_vertex_error'] = collider_error

lintel = scene.objects['SUPERIOR | posterior sobre passarela']
lintel_points = [inverse @ lintel.matrix_world @ v.co for v in lintel.data.vertices]
lintel_edges = [min(p.y for p in lintel_points), max(p.y for p in lintel_points)]
lintel_error = max(abs(a-b) for a, b in zip(lintel_edges, edges))

probes = []
M = Matrix(report['measurement_frame'])
for side, (name, tree) in enumerate(trees):
    start, end = sorted((edges[side], -4.7 if side == 0 else 4.7))
    for j in range(1, 9):
        y = start+(end-start)*j/9
        for z in (70.4, 71.8, 73.3):
            origin = M @ Vector((-4.0, y, z))
            direction = M.to_3x3() @ Vector((-1, 0, 0))
            hit = tree.ray_cast(origin, direction, 2)
            probes.append({'object': name, 'y': y, 'z': z, 'wall_hit': hit[0] is not None})

qa = json.loads((OUT/'walkability_candidate_b77.json').read_text(encoding='utf8'))
blocked = []; samples = 0
for route, data in qa['routes'].items():
    if data.get('status') != 'sampled_clear': continue
    points = data['points']
    for index, (a, b) in enumerate(zip(points, points[1:])):
        count = max(1, math.ceil(math.dist(a, b)/.2))
        for j in range(count+1):
            p = Vector(a).lerp(Vector(b), j/count)
            if p.z < 65: continue
            for height in (.3, .45, .6, .75, .9, 1.05, 1.2, 1.35, 1.5):
                center = p+Vector((0, 0, height)); samples += 1
                for name, tree in trees:
                    hit = tree.find_nearest(center, .3)
                    if hit[0] is not None and hit[3] < .3-1e-4:
                        blocked.append({'route': route, 'segment': index, 'object': name, 'distance': hit[3]})

# Folhas animadas reais: repetir a verificação existente sem substituir evidência B77B.
old = json.loads((OUT/'scene_b77.json').read_text(encoding='utf8'))
door_cases = []
for label, f in (('upper', old['timeline']['start']), ('lower', old['timeline']['walk_out'])):
    scene.frame_set(f); dg = bpy.context.evaluated_depsgraph_get(); door_trees = []
    for ob in scene.objects:
        if ob.get('elevator_id') != 3 or ob.get('elevator_role') not in ('cabin_door', 'landing_door'): continue
        ev = ob.evaluated_get(dg); mesh = ev.to_mesh()
        try:
            mesh.calc_loop_triangles()
            door_trees.append((ob.name, BVHTree.FromPolygons([ev.matrix_world @ v.co for v in mesh.vertices], [tuple(t.vertices) for t in mesh.loop_triangles], all_triangles=True)))
        finally:
            ev.to_mesh_clear()
    errors = []
    for index, p in enumerate(qa['routes'][label]['points']):
        for j in range(9):
            center = Vector((p[0], p[1], p[2]+.3+j*1.2/8))
            for name, tree in door_trees:
                hit = tree.find_nearest(center, .3)
                if hit[0] is not None and hit[3] < .285:
                    errors.append({'point': index, 'door': name})
    door_cases.append({'route': label, 'frame': f, 'blocked': errors})

proof = json.loads((ROOT/'artifacts/blender-sessions/last-open.json').read_text(encoding='utf8'))
assert proof['file'] == report['source_after']['file'] and proof['sha256'] == report['source_after']['sha256'] and proof['load_post_completed']
with (ROOT/report['source_before']['file']).open('rb') as stream:
    before_hash = hashlib.file_digest(stream, 'sha256').hexdigest()
result = {'revision': 'R30B.78', 'source_reopened': True, 'reopen_evidence': proof,
          'object_count': len(scene.objects), 'preserved_objects': len(snapshot),
          'changed_meshes': list(changed), 'added_objects': report['added_objects'],
          'differences_outside_authorized_change': differences, 'seams': seams,
          'closed_wall_probes': probes, 'topology': topology,
          'lintel_edges': lintel_edges, 'lintel_edge_error': lintel_error,
          'route_sphere_samples': samples, 'route_wall_blockers': blocked,
          'door_cases': door_cases,
          'source_before_unchanged': before_hash == report['source_before']['sha256'],
          'ssot_unchanged': hashlib.sha256((ROOT/'world/geographic-reference.json').read_bytes()).hexdigest() == report['ssot_sha256'],
          'physical_dimensions_verified': False, 'engine_physics_verified': False}
result['passed'] = (not differences and not blocked and all(p['wall_hit'] for p in probes)
                    and all(s['gap_design_units'] < 1e-4 for s in seams)
                    and lintel_error < 1e-4
                    and all(not t['nonmanifold_edges'] and not t['degenerate_faces'] and not t['nonfinite'] and t['volume'] > 0 and t['collider_max_vertex_error'] < 1e-5 for t in topology)
                    and all(not d['blocked'] for d in door_cases)
                    and result['source_before_unchanged'] and result['ssot_unchanged']
                    and len(scene.objects) == len(snapshot)+len(report['added_objects']))
(OUT/'validation_b78.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
scene.frame_set(frame)
print(json.dumps({k: result[k] for k in ('passed', 'object_count', 'preserved_objects', 'differences_outside_authorized_change', 'route_sphere_samples', 'route_wall_blockers', 'seams', 'topology')}))
assert result['passed']
