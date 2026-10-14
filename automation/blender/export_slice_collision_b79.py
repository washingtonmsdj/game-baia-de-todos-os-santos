"""Exporta geometria avaliada da B77B para auditoria volumétrica; não modifica cena."""
import bpy, json, hashlib
from pathlib import Path
from mathutils import Vector
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'artifacts/lacerda-controller'; OUT.mkdir(parents=True, exist_ok=True)
scene = bpy.context.scene
expected_name=globals().get('REVISION_NAME','salvador_lacerda_r30b77b_portas_e_percurso.blend')
output_name=globals().get('OUTPUT_GEOMETRY_NAME','geometry_b77b.json')
assert Path(bpy.data.filepath).name == expected_name
saved_frame = scene.frame_current
qa = json.loads((ROOT/globals().get('QA_PATH','docs/reports/blender/lacerda-corridor/walkability_candidate_b77.json')).read_text(encoding='utf8'))
b77 = json.loads((ROOT/'docs/reports/blender/lacerda-corridor/scene_b77.json').read_text(encoding='utf8'))
floor_names = set(qa['collision_sources']) | {'FUNCIONAL | 3 piso','ESTAÇÃO INFERIOR | plataforma','LAC R30B | Passarela | piso paginado visual'}
poses = {'closed_upper':65000, 'open_upper':b77['timeline']['start'],
         'moving_closed':b77['timeline']['departure']+240,
         'closed_lower':b77['timeline']['landing'], 'open_lower':b77['timeline']['walk_out']}
route_pts = [p for r in qa['routes'].values() for p in r.get('points', [])]
route_lo = [min(p[i] for p in route_pts)-1.8 for i in range(3)]
route_hi = [max(p[i] for p in route_pts)+2.5 for i in range(3)]
rows = []; states = {}; exclusions = []; totals = {'scene_objects':len(scene.objects),'visible_meshes':0}

def moving(ob):
    current = ob
    while current:
        if current.get('elevator_id') == 3 and current.get('elevator_role') in ('cabin','cabin_door'):
            return True
        current = current.parent
    return False

def mechanism(ob):
    current=ob
    while current:
        if current.get('elevator_id')==3 and current.get('elevator_role') in ('cabin','cabin_door','landing_door'):
            return current
        current=current.parent
    return None

def geometry(ob, dg, crop=None):
    ev = ob.evaluated_get(dg); mesh = ev.to_mesh()
    try:
        mesh.calc_loop_triangles()
        points = [ev.matrix_world @ v.co for v in mesh.vertices]
        faces = []
        for tri in mesh.loop_triangles:
            ps = [points[i] for i in tri.vertices]
            if crop and any(max(p[i] for p in ps)<crop[0][i] or min(p[i] for p in ps)>crop[1][i] for i in range(3)):continue
            faces.append(tuple(tri.vertices))
        if not faces:return None
        indices = sorted({i for face in faces for i in face}); lookup = {old:i for i,old in enumerate(indices)}
        return {'vertices':[list(points[i]) for i in indices], 'triangles':[[lookup[i] for i in face] for face in faces],
                'complete_mesh':len(faces)==len(mesh.loop_triangles),
                'bounds':{'min':[min(p[i] for p in points) for i in range(3)],'max':[max(p[i] for p in points) for i in range(3)]}}
    finally:ev.to_mesh_clear()

scene.frame_set(poses['closed_upper']); dg = bpy.context.evaluated_depsgraph_get()
floor = scene.objects['FUNCIONAL | 3 piso']
f = geometry(floor,dg); shaft_lo = [min(p[i] for p in f['vertices'])-.7 for i in range(3)]
shaft_hi = [max(p[i] for p in f['vertices'])+.7 for i in range(3)]
shaft_lo[2] = qa['elevator']['lower_z']-1; shaft_hi[2] = qa['elevator']['upper_z']+4
for ob in scene.objects:
    if ob.type != 'MESH':continue
    cols = [c.name for c in ob.users_collection]
    owner=mechanism(ob)
    role = owner.get('elevator_role') if owner else ob.get('elevator_role'); dynamic = owner is not None
    if not ob.visible_get() or ob.hide_render:
        if dynamic:exclusions.append({'object':ob.name,'reason':'dynamic_hidden_not_exported'})
        continue
    if any(c.startswith(('SOURCE_GEOREF','QA |','33.','34.','37.')) for c in cols) or ob.name.startswith(('NAV |','QA |','B77 | NAV','B77 | REFERENCE')):
        exclusions.append({'object':ob.name,'reason':'semantic_reference_or_existing_proxy_not_visual_obstacle'});continue
    totals['visible_meshes']+=1
    bb = [ob.matrix_world@Vector(p) for p in ob.bound_box]
    intersects_route = all(max(p[i] for p in bb)>=route_lo[i] and min(p[i] for p in bb)<=route_hi[i] for i in range(3))
    intersects_shaft = all(max(p[i] for p in bb)>=shaft_lo[i] and min(p[i] for p in bb)<=shaft_hi[i] for i in range(3))
    if not dynamic and not intersects_route and not intersects_shaft:continue
    crop_lo = [min(route_lo[i],shaft_lo[i]) for i in range(3)]
    crop_hi = [max(route_hi[i],shaft_hi[i]) for i in range(3)]
    g = geometry(ob,dg,None if dynamic else (crop_lo,crop_hi))
    if not g:continue
    row={'name':ob.name,'collections':cols,'parent':ob.parent.name if ob.parent else None,
         'dynamic':dynamic,'cabin_member':moving(ob),'elevator_role':role,
         'landing':owner.get('landing') if owner else ob.get('landing'),'door_side':owner.get('door_side') if owner else ob.get('door_side'),
         'walkable':ob.name in floor_names or ob.name.startswith('B63 | VISUAL | meios-fios'),
         'geometry':g,'properties':{k:ob[k] for k in ob.keys() if isinstance(ob[k],(str,int,float,bool))}}
    rows.append(row)
for label, frame in poses.items():
    scene.frame_set(frame);dg=bpy.context.evaluated_depsgraph_get()
    states[label]={'frame':frame,'objects':{r['name']:geometry(scene.objects[r['name']],dg) for r in rows if r['dynamic']}}
scene.frame_set(saved_frame)
with Path(bpy.data.filepath).open('rb') as stream: sha=hashlib.file_digest(stream,'sha256').hexdigest()
report={'schema':'boas/slice-geometry-audit-v1','source':{'file':Path(bpy.data.filepath).relative_to(ROOT).as_posix(),'sha256':sha},
        'coordinate_reference':'world/geographic-reference.json','coordinate_system':'Blender X,Y,Z local design units',
        'objects':rows,'states':states,'qa':qa,'shaft_roi':{'min':shaft_lo,'max':shaft_hi},
        'route_roi':{'min':route_lo,'max':route_hi},'exclusions':exclusions,'coverage':totals,
        'note':'Malhas avaliadas reais; ROI recorta triângulos de objetos grandes. Não aprova engine ou dimensão física.'}
(OUT/output_name).write_text(json.dumps(report,ensure_ascii=False),encoding='utf8')
summary={'objects':len(rows),'static':sum(not r['dynamic'] for r in rows),'dynamic':sum(r['dynamic'] for r in rows),
         'triangles':sum(len(r['geometry']['triangles']) for r in rows),'file':'artifacts/lacerda-controller/'+output_name}
print(json.dumps(summary))
