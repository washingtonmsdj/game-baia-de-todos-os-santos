"""Reconcilia collider com piso visual; não corta/redimensiona arquitetura."""
import bpy,json,hashlib,runpy
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/reports/blender/lacerda-controller-b80'
scene=bpy.context.scene;catalog=json.loads((ROOT/'world/areas/mvp-centro-lacerda/blender-revisions.json').read_text(encoding='utf8'))
source=catalog['validation_source'];assert source['revision']=='R30B.79'
assert Path(bpy.data.filepath).resolve()==(ROOT/source['file']).resolve()
destination=ROOT/'blender/salvador_lacerda_r30b80_piso_e_embarque_superior.blend';assert not destination.exists()
scene.frame_set(31978);bpy.context.view_layer.update()
sig=runpy.run_path(str(ROOT/'automation/blender/component_fingerprint.py'))['signature']
baseline={}
for o in scene.objects:
    try:s=sig(o)
    except RuntimeError:s={'type':o.type,'transform':[list(r) for r in o.matrix_world],'constraints':[(c.name,c.type) for c in o.constraints]}
    baseline[o.name]={'signature':s,'parent':o.parent.name if o.parent else None,'collections':[c.name for c in o.users_collection],
        'hide_render':o.hide_render,'visible':o.visible_get(),'action':o.animation_data.action.name if o.animation_data and o.animation_data.action else None}
(ROOT/'artifacts/lacerda-controller/protected_b79_b80.json').write_text(json.dumps(baseline,ensure_ascii=False),encoding='utf8')
scene.frame_set(65024);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
name='LAC R30B | Passarela | piso paginado visual';ob=scene.objects[name];ev=ob.evaluated_get(dg);m=ev.to_mesh()
try:
    m.calc_loop_triangles();vertices=[ev.matrix_world@v.co for v in m.vertices];faces=[tuple(t.vertices) for t in m.loop_triangles]
    tree=BVHTree.FromPolygons(vertices,faces,all_triangles=True);top=max(v.z for v in vertices);bottom=min(v.z for v in vertices);selected=[]
    for face in faces:
        p=[vertices[i] for i in face];n=(p[1]-p[0]).cross(p[2]-p[0])
        if n.length<1e-10 or abs(n.z)/n.length<.7:continue
        center=sum(p,Vector())/3;hit=tree.ray_cast(Vector((center.x,center.y,top+1)),Vector((0,0,-1)),top-bottom+2)[0]
        if hit is not None and abs(hit.z-center.z)<1e-4:selected.append(face if n.z>0 else tuple(reversed(face)))
    used=sorted({i for f in selected for i in f});lookup={old:i for i,old in enumerate(used)}
    mesh=bpy.data.meshes.new('B80 piso visual surface');mesh.from_pydata([vertices[i] for i in used],[],[tuple(lookup[i] for i in f) for f in selected]);mesh.update()
finally:ev.to_mesh_clear()
assert selected
col=bpy.data.collections['33.3 RUNTIME | WALKABLE'];proxy=bpy.data.objects.new('B80 | COLLISION | passarela piso visual',mesh);col.objects.link(proxy)
proxy.hide_render=True;proxy.hide_set(True);proxy['boas_role']='COLLISION_WALKABLE_CANDIDATE';proxy['boas_derived_from_object']=name
proxy['boas_provenance_ids']=json.dumps(['derived:upper-ground-b80']);proxy['boas_production_ready']=False
proxy['boas_geographic_ssot_id']=scene['boas_geographic_ssot_id'];proxy['boas_source_blend']=source['file'];proxy['boas_source_sha256']=source['sha256']
profile_path=ROOT/'world/areas/mvp-centro-lacerda/corridor-slice.json';profile=json.loads(profile_path.read_text(encoding='utf8'))
old_binding=next(x for x in profile['collision_bindings'] if x['object']=='B77 | COLLISION | NAV | passarela superior')
old_binding['enabled']=False;old_binding['status']='superseded_floor_plane';old_binding['replaced_by']=proxy.name
profile['collision_bindings'].append({'object':proxy.name,'source':name,'role':'WALKABLE_FLOOR','moving':False,'enabled':True,'triangles':len(selected),'vertices':len(used),'status':'candidate','representation':'actual_visual_top_surface'})
qa=json.loads((OUT/'walkability_candidate_b80.json').read_text(encoding='utf8'))
curve=bpy.data.curves.new('B80 upper ground route candidate','CURVE');curve.dimensions='3D';spline=curve.splines.new('POLY');points=qa['routes']['upper']['points'];spline.points.add(len(points)-1)
for p,co in zip(spline.points,points):p.co=(*co,1)
route=bpy.data.objects.new('B80 | NAV | superior ground-following candidato',curve);bpy.data.collections['37.1 NAV | PEDESTRIAN PATHS'].objects.link(route)
route.hide_render=True;route.hide_set(True);route['boas_role']='NAVIGATION_HINT_CANDIDATE';route['boas_provenance_ids']=json.dumps(['derived:upper-ground-b80']);route['boas_production_ready']=False
profile['route_evidence']='docs/reports/blender/lacerda-controller-b80/walkability_candidate_b80.json'
profile['upper_ground_following']={'route_object':route.name,'evidence':'docs/reports/blender/lacerda-controller-b80/ground_following_b80.json','controller_verified':False,'architecture_changed':False}
profile['validation']='docs/reports/blender/lacerda-controller-b80/validation_b80.json'
profile['status']='upper_ground_reconciled_shaft_blocked';profile['production_ready']=False
profile_path.write_text(json.dumps(profile,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
scene['boas_slice_controller_status']='shaft_solid_intersections_blocked_not_engine_verified'
scene.frame_set(65024)
report={'revision':'R30B.80','source_before':source,'baseline_frame':31978,'objects_before':len(baseline),'objects_after':len(scene.objects),
 'added_objects':[proxy.name,route.name],'changed_original_objects':[],'superseded_binding':old_binding,'new_floor_source':name,
 'new_floor_triangles':len(selected),'architecture_changed':False,'B78_merge_applied':False,'terrain_changed':False,
 'ssot_sha256':hashlib.sha256((ROOT/'world/geographic-reference.json').read_bytes()).hexdigest(),'engine_verified':False,'movement_enabled':False}
bpy.ops.wm.save_as_mainfile(filepath=str(destination),compress=True)
with destination.open('rb') as stream:sha=hashlib.file_digest(stream,'sha256').hexdigest()
report['source_after']={'file':destination.relative_to(ROOT).as_posix(),'revision':'R30B.80','sha256':sha}
(OUT/'scene_b80.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'saved':report['source_after'],'floor_triangles':len(selected),'added_objects':2}))
