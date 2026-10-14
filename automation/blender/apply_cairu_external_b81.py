"""B81: papéis físicos comprovados e guia OSM externo parcial; sem editar arquitetura."""
import bpy,json,hashlib,runpy,os,shutil
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/reports/blender/cairu-market-b81'
catalog_path=ROOT/'world/areas/mvp-centro-lacerda/blender-revisions.json'
catalog=json.loads(catalog_path.read_text(encoding='utf8'));source=catalog['validation_source']
assert source['revision']=='R30B.80'
assert Path(bpy.data.filepath).resolve()==(ROOT/source['file']).resolve() and not bpy.data.is_dirty
assert os.getpid()==json.loads((ROOT/'artifacts/blender-sessions/current-session.json').read_text())['pid']
destination=ROOT/'blender/salvador_lacerda_r30b81_cairu_colisao_e_rota_parcial.blend'
assert not destination.exists()
assert shutil.disk_usage(ROOT).free>2*(ROOT/source['file']).stat().st_size,'Espaço insuficiente; nenhuma mutação aplicada'
route=json.loads((OUT/'route_candidate.json').read_text(encoding='utf8'))
sig=runpy.run_path(str(ROOT/'automation/blender/component_fingerprint.py'))['signature']
def snapshot():
 result={}
 for ob in bpy.context.scene.objects:
  try:result[ob.name]=sig(ob)
  except RuntimeError:result[ob.name]={'type':ob.type,'matrix_world':[list(r) for r in ob.matrix_world],'constraints':[(c.name,c.type) for c in ob.constraints]}
 return result
before=snapshot();before_frame=bpy.context.scene.frame_current
(ROOT/'artifacts/lacerda-controller/b81_original_signatures.json').write_text(json.dumps(before,ensure_ascii=False),encoding='utf8')
profile=json.loads((ROOT/'world/areas/mvp-centro-lacerda/cairu-market-pedestrian.json').read_text(encoding='utf8'))
base=json.loads((ROOT/'world/areas/mvp-centro-lacerda/corridor-slice.json').read_text(encoding='utf8'))
paint=bpy.data.objects['LAC R30B06 | fundo verde travessia 3178050253']
assert paint['boas_role']=='visual_environment' and paint['osm_node_id']=='3178050253' and paint['surface_separation_m']==.003
paint['boas_collision_role']='RENDER_ONLY';paint['boas_collision_enabled']=False
bindings=[];modified_metadata=[paint.name]
for name in ['INFERIOR | piso do saguão','INFERIOR R21 | passeio da entrada','INFERIOR R21 | rebaixo acessível']:
 ob=bpy.data.objects[name];assert ob.get('game_role')=='walkable_surface'
 bind=next(b for b in base['collision_bindings'] if b.get('source')==name and b['role']=='WALKABLE_FLOOR')
 assert bpy.data.objects.get(bind['object']) is not None
 ob['boas_collision_role']='WALKABLE_FLOOR';modified_metadata.append(name);bindings.append(bind)
curb=bpy.data.objects['B63 | VISUAL | meios-fios das vias existentes'];assert abs(curb['boas_design_height_m']-.12)<1e-6
curb['boas_collision_role']='PHYSICAL_CURB_STEP';modified_metadata.append(curb.name)
dg=bpy.context.evaluated_depsgraph_get();ev=curb.evaluated_get(dg);m=ev.to_mesh()
try:
 m.calc_loop_triangles();verts=[ev.matrix_world@v.co for v in m.vertices]
 points=[Vector(p) for p in route['points']];lo=[min(p[i] for p in points)-1.5 for i in range(3)];hi=[max(p[i] for p in points)+1.5 for i in range(3)]
 faces=[]
 for tri in m.loop_triangles:
  ps=[verts[i] for i in tri.vertices]
  if any(max(p[i] for p in ps)<lo[i] or min(p[i] for p in ps)>hi[i] for i in range(3)):continue
  faces.append(tuple(tri.vertices))
 used=sorted({i for f in faces for i in f});lookup={old:i for i,old in enumerate(used)}
 mesh=bpy.data.meshes.new('B81 physical curb patch');mesh.from_pydata([verts[i] for i in used],[],[tuple(lookup[i] for i in f) for f in faces]);mesh.update()
finally:ev.to_mesh_clear()
assert faces
proxy=bpy.data.objects.new('B81 | COLLISION | meios-fios Cairu fonte preservada',mesh);bpy.data.collections['33.3 RUNTIME | WALKABLE'].objects.link(proxy)
proxy.hide_render=True;proxy.hide_set(True)
for key,value in {'boas_role':'COLLISION_CURB_STEP_CANDIDATE','boas_derived_from_object':curb.name,'boas_source_blend':source['file'],'boas_source_sha256':source['sha256'],'boas_production_ready':False,'boas_geographic_ssot_id':bpy.context.scene['boas_geographic_ssot_id'],'boas_provenance_ids':json.dumps(['derived:cairu-external-b81'])}.items():proxy[key]=value
bindings.append({'object':proxy.name,'source':curb.name,'role':'PHYSICAL_CURB_STEP','moving':False,'enabled':True,'status':'candidate','representation':'source triangles in bounded external ROI; no vertex displacement','triangles':len(faces),'source_geometry_sha256':before[curb.name]['geometry_sha256']})
curve=bpy.data.curves.new('B81 OSM external partial route','CURVE');curve.dimensions='3D';spline=curve.splines.new('POLY');spline.points.add(len(route['points'])-1)
for p,co in zip(spline.points,route['points']):p.co=(*co,1)
nav=bpy.data.objects.new('B81 | NAV | Cairu OSM parcial bloqueada',curve);bpy.data.collections['37.1 NAV | PEDESTRIAN PATHS'].objects.link(nav);nav.hide_render=True
nav['boas_role']='NAVIGATION_HINT_CANDIDATE';nav['boas_production_ready']=False;nav['boas_provenance_ids']=json.dumps(['derived:cairu-external-b81']);nav['boas_route_enabled']=False;nav['boas_osm_control_nodes']=json.dumps([n['id'] for n in route['control_nodes']]);nav['boas_terminus_node']='12229090827';nav['boas_market_entrance_verified']=False
profile['collision_bindings']=bindings;profile['collision_role_overrides']=[{'object':paint.name,'role':'RENDER_ONLY','collision_enabled':False,'evidence':'docs/reports/world/cairu-market-pedestrian/collision_role_evidence.json'}]
profile['scene_revision_applied']='R30B.81';profile['CAIRU_MARKET_PEDESTRIAN']='PARTIAL_ROUTE_APPLIED_BLOCKED';profile['scene_route_object']=nav.name
profile['route_evidence']='docs/reports/blender/cairu-market-b81/route_candidate.json';profile['movement_enabled']=False
profile['collider_plan']['applied']=True
profile['controller']['ground_following_candidate']=profile['route_evidence']
profile['controller']['numerical_replay']='docs/reports/blender/cairu-market-b81/controller_replay_b81.json'
profile['validation']='docs/reports/blender/cairu-market-b81/validation.json'
assert profile['LACERDA_VERTICAL']=='BLOCKED_EXTERNAL_EVIDENCE'
bpy.context.scene['boas_lacerda_vertical_status']='BLOCKED_EXTERNAL_EVIDENCE';bpy.context.scene['boas_external_pedestrian_status']='PARTIAL_ROUTE_APPLIED_BLOCKED';bpy.context.scene['boas_movement_enabled']=False
after=snapshot();changed=[name for name,v in before.items() if after.get(name)!=v];assert not changed,changed
assert bpy.context.scene.frame_current==before_frame
bpy.ops.wm.save_as_mainfile(filepath=str(destination),compress=True)
with destination.open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
entry={'file':destination.relative_to(ROOT).as_posix(),'revision':'R30B.81','sha256':sha,'status':'external_partial_route_blocked','parent_file':source['file'],'production_ready':False,'evidence':'docs/reports/blender/cairu-market-b81/application.json','notes':'Papéis físicos comprovados e patch de meio-fio fiel, rota OSM parcial. Vertical B80 bloqueada; acesso Mercado e controller não aprovados.'}
catalog['candidates'].append(entry) if 'candidates' in catalog else catalog['revisions'].append(entry)
catalog['validation_source']=entry;catalog_path.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(ROOT/'world/areas/mvp-centro-lacerda/cairu-market-pedestrian.json').write_text(json.dumps(profile,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
report={'source_before':source,'source_after':entry,'pid':os.getpid(),'objects_before':len(before),'objects_after':len(after),'added_objects':[proxy.name,nav.name],'modified_metadata_only':modified_metadata,'original_geometry_transform_material_changed':changed,'curb_patch_triangles':len(faces),'LACERDA_VERTICAL':'BLOCKED_EXTERNAL_EVIDENCE','CAIRU_MARKET_PEDESTRIAN':'PARTIAL_ROUTE_APPLIED_BLOCKED','movement_enabled':False,'production_exported':False,'ssot_sha256':hashlib.sha256((ROOT/'world/geographic-reference.json').read_bytes()).hexdigest()}
(OUT/'application.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'saved':entry['file'],'sha256':sha,'added_objects':2,'original_geometries_changed':0,'vertical':'BLOCKED_EXTERNAL_EVIDENCE'}))
