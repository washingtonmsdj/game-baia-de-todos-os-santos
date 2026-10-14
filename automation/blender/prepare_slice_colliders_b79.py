"""Deriva patches físicos locais da B77B; preserva todas as malhas visuais."""
import bpy,bmesh,json,hashlib,runpy
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/reports/blender/lacerda-controller'
scene=bpy.context.scene;catalog=json.loads((ROOT/'world/areas/mvp-centro-lacerda/blender-revisions.json').read_text(encoding='utf8'))
source=catalog['validation_source'];assert source['revision']=='R30B.77B'
assert Path(bpy.data.filepath).resolve()==(ROOT/source['file']).resolve()
destination=ROOT/'blender/salvador_lacerda_r30b79_contrato_colisao_slice.blend';assert not destination.exists()
g=json.loads((ROOT/'artifacts/lacerda-controller/geometry_b77b.json').read_text(encoding='utf8'))
assert g['source']['sha256']==source['sha256']
scene.frame_set(31978)
helper=runpy.run_path(str(ROOT/'automation/blender/component_fingerprint.py'));signature=helper['signature']
def state(ob):
    try:s=signature(ob)
    except RuntimeError:s={'type':ob.type,'transform':[list(r) for r in ob.matrix_world],'constraints':[(c.name,c.type) for c in ob.constraints]}
    return {'signature':s,'parent':ob.parent.name if ob.parent else None,'collections':[c.name for c in ob.users_collection],
            'hide_render':ob.hide_render,'visible':ob.visible_get(),'action':ob.animation_data.action.name if ob.animation_data and ob.animation_data.action else None}
baseline={o.name:state(o) for o in scene.objects}
(ROOT/'artifacts/lacerda-controller/protected_b77b_b79.json').write_text(json.dumps(baseline,ensure_ascii=False),encoding='utf8')
scene.frame_set(g['states']['closed_upper']['frame']);bpy.context.view_layer.update()
plan=json.loads((ROOT/'artifacts/lacerda-controller/collider_plan_b79.json').read_text(encoding='utf8'))
col=bpy.data.collections.get('COLLISION | Lacerda slice B79')
assert col is None
col=bpy.data.collections.new('COLLISION | Lacerda slice B79')
# Reutiliza a raiz física existente, sem outra organização de mundo.
parent=bpy.data.collections.get('33.3 RUNTIME | WALKABLE')
assert parent;parent.children.link(col);col['boas_detail_level']='PLAYABLE_CORE';col['boas_role']='COLLISION'
added=[];bindings=[]
for spec in plan['patches']:
    source_ob=scene.objects[spec['source']];verts=[Vector(v) for v in spec['vertices']]
    if spec['dynamic']:
        inverse=source_ob.matrix_world.inverted();verts=[inverse@v for v in verts]
    mesh=bpy.data.meshes.new('B79 collider patch');mesh.from_pydata(verts,[],spec['triangles']);mesh.update()
    original_faces=len(mesh.polygons);bm=bmesh.new();bm.from_mesh(mesh)
    bmesh.ops.dissolve_limit(bm,angle_limit=1e-6,verts=list(bm.verts),edges=list(bm.edges),delimit={'NORMAL'})
    bm.to_mesh(mesh);bm.free();mesh.update()
    ob=bpy.data.objects.new('B79 | COLLISION | '+spec['source'],mesh);col.objects.link(ob)
    if spec['dynamic']:
        ob.parent=source_ob;ob.matrix_parent_inverse=Matrix.Identity(4);ob.matrix_basis=Matrix.Identity(4)
    ob.hide_render=True;ob.hide_set(True);ob.display_type='WIRE'
    role='DYNAMIC_DOOR' if spec['door'] else 'DYNAMIC_CABIN' if spec['dynamic'] else 'STATIC_OBSTACLE'
    ob['boas_role']='COLLISION_'+role+'_CANDIDATE';ob['boas_collision_profile_id']='lacerda-corridor-b77'
    ob['boas_derived_from_object']=source_ob.name;ob['boas_source_blend']=source['file'];ob['boas_source_sha256']=source['sha256']
    ob['boas_revision']='R30B.79';ob['boas_provenance_ids']=json.dumps(['derived:lacerda-controller-b79'])
    ob['boas_location_id']='elevador-lacerda';ob['boas_production_ready']=False
    ob['boas_geographic_ssot_id']=scene['boas_geographic_ssot_id']
    binding={'object':ob.name,'source':source_ob.name,'role':role,'moving':spec['dynamic'],
             'input_triangles':original_faces,'simplified_faces':len(mesh.polygons),'representation':'coplanar_surface_patch',
             'two_sided_required':True,'clipped_patch':not spec['dynamic'],'status':'candidate'}
    bindings.append(binding);added.append(ob.name)
# Trigger de risco, jamais parede física ou chão para tapar o poço.
lo=g['shaft_roi']['min'];hi=g['shaft_roi']['max']
verts=[(x,y,z) for z in (lo[2],hi[2]) for y in (lo[1],hi[1]) for x in (lo[0],hi[0])]
mesh=bpy.data.meshes.new('B79 shaft trigger envelope');mesh.from_pydata(verts,[],[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)])
trigger=bpy.data.objects.new('B79 | TRIGGER | poço proibido sem cabine',mesh);col.objects.link(trigger)
trigger.hide_render=True;trigger.hide_set(True);trigger['boas_role']='FORBIDDEN_SHAFT_TRIGGER_CANDIDATE'
trigger['boas_derived_from_object']='FUNCIONAL | 3 piso';trigger['boas_provenance_ids']=json.dumps(['derived:lacerda-controller-b79'])
trigger['boas_production_ready']=False;trigger['boas_collision_response']='query_only; not a physical wall'
added.append(trigger.name)
profile_path=ROOT/'world/areas/mvp-centro-lacerda/corridor-slice.json';profile=json.loads(profile_path.read_text(encoding='utf8'))
for b in profile['collision_bindings']:
    b['role']='DYNAMIC_CABIN_FLOOR' if b['moving'] else 'WALKABLE_FLOOR'
profile['collision_bindings']+=bindings
profile['shaft_trigger']={'object':trigger.name,'role':'FORBIDDEN_SHAFT','physical_wall':False,'dimensions_status':'conservative_candidate_envelope',
                         'response':'fail-closed boarding gate; ignore for supported cabin occupant; never walkable'}
profile['pending']+=['54 contatos contínuos cabine/estrutura na B77B exigem triagem','passagem da cápsula bloqueada na geometria visual; detalhes no relatório B79']
profile['collision_layers']=['WALKABLE_FLOOR','STATIC_OBSTACLE','DYNAMIC_DOOR','DYNAMIC_CABIN','FORBIDDEN_SHAFT','TERRAIN']
profile_path.write_text(json.dumps(profile,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
text=bpy.data.texts.new('BOAS | contrato slice B79');text.write(json.dumps(profile,ensure_ascii=False,indent=2))
scene['boas_slice_controller_status']='blocked_candidate_not_engine_verified'
scene.frame_set(65024)
report={'revision':'R30B.79','source_before':source,'baseline_frame':31978,'objects_before':len(baseline),'objects_after':len(scene.objects),
        'added_objects':added,'bindings':bindings,'omitted_candidates':plan['omitted'],'visual_geometry_changed':False,
        'terrain_changed':False,'architectural_dimensions_changed':False,'engine_approved':False,
        'ssot_sha256':hashlib.sha256((ROOT/'world/geographic-reference.json').read_bytes()).hexdigest()}
bpy.ops.wm.save_as_mainfile(filepath=str(destination),compress=True)
with destination.open('rb') as stream:sha=hashlib.file_digest(stream,'sha256').hexdigest()
report['source_after']={'file':destination.relative_to(ROOT).as_posix(),'revision':'R30B.79','sha256':sha}
(OUT/'scene_b79.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'saved':report['source_after'],'objects_added':len(added),'proxy_faces':sum(x['simplified_faces'] for x in bindings)}))
