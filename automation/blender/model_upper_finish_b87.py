"""B87: fechamento lateral real e reconciliação de pisos; sem alterar torres/poço."""
import bpy,bmesh,hashlib,json,math,os,runpy
from pathlib import Path
from mathutils import Matrix,Vector

root=Path(__file__).resolve().parents[2];out=root/'docs/reports/blender/lacerda-finish-b87';out.mkdir(parents=True,exist_ok=True)
scene=bpy.context.scene;base=Path(bpy.data.filepath)
assert base.name=='salvador_lacerda_r30b86_saguao_superior_planta.blend' and scene.name=='SALVADOR | ESBOCO OFICIAL'
for abandoned in list(bpy.data.objects):
    if abandoned.name.startswith('B87 | COLLISION | SUPERIOR | parede lateral saguão') and not abandoned.users_scene:
        bpy.data.objects.remove(abandoned,do_unlink=True)
dest=root/'blender/salvador_lacerda_r30b87_pisos_e_fechamentos_superiores.blend';assert not dest.exists()
catalog_path=root/'world/areas/mvp-centro-lacerda/blender-revisions.json';catalog=json.loads(catalog_path.read_text(encoding='utf8'))
with base.open('rb') as f:base_hash=hashlib.file_digest(f,'sha256').hexdigest()
assert base_hash==catalog['authoring_source']['sha256']
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));wm=h['world_matrix'];sig=h['signature']
M=Matrix(json.loads((root/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text(encoding='utf8'))['measurement_frame']);inv=M.inverted()
prior=json.loads((root/'docs/reports/blender/lacerda-layout-b86/application.json').read_text(encoding='utf8'))
for row in prior['changes']:assert sig(scene.objects[row['object']])==row['after']['signature'],row['object']
ssot_hash=hashlib.sha256((root/'world/geographic-reference.json').read_bytes()).hexdigest()
proxy_before={o.name:sig(o) for o in bpy.data.collections['GAMEPLAY_PROXY | Lacerda B82'].objects}
terrain_before=sig(scene.objects['MVP | terreno corrigido | colisão estática'])
profile_path=root/'world/areas/mvp-centro-lacerda/corridor-slice.json';profile=json.loads(profile_path.read_text(encoding='utf8'))
old_binding=next(r for r in profile['collision_bindings'] if r['object']=='B77 | COLLISION | NAV | passarela superior')
assert old_binding['enabled'] is False and old_binding['replaced_by']=='B80 | COLLISION | passarela piso visual'

def bounds(obj):
    transform=inv@wm(obj);points=[transform@v.co for v in obj.data.vertices]
    return [[min(p[i] for p in points),max(p[i] for p in points)] for i in range(3)]

floor=scene.objects['SUPERIOR | piso saguão'];floor_bounds=bounds(floor)
finish=scene.objects['LAC R30B | Passarela | piso paginado visual'];finish_bounds=bounds(finish)
assert finish_bounds[2][1]-finish_bounds[2][0]<1e-4
target_z=finish_bounds[2][1];delta=target_z-floor_bounds[2][1]
assert 0<delta<.10
floor_names=[floor.name]
for obj in scene.objects:
    if obj.type=='MESH' and any(obj.get(k)==floor.name for k in ('boas_derived_from_object','boas_source_object','boas_collision_source_object','source_object')):floor_names.append(obj.name)
assert set(floor_names)=={floor.name,'B77 | COLLISION | SUPERIOR | piso saguão','COLLISION R35 | Laje do saguão superior'}
wall_names=['SUPERIOR | parede lateral saguão','SUPERIOR | parede lateral saguão.001']
trim_names=[r['object'] for r in prior['changes'] if 'peitoril lateral' in r['object']]
obsolete_names=['NAV | passarela superior','B77 | COLLISION | NAV | passarela superior']+trim_names
changed_names=set(floor_names+wall_names+obsolete_names)
protected={o.name:(o.data.as_pointer() if o.data else None,[list(r) for r in o.matrix_basis],o.hide_render,o.parent.name if o.parent else None) for o in scene.objects if o.name not in changed_names}
before={n:{'signature':sig(scene.objects[n]),'bounds':bounds(scene.objects[n]),'properties':{k:str(scene.objects[n][k]) for k in scene.objects[n].keys()},'visible':scene.objects[n].visible_get(),'hide_render':scene.objects[n].hide_render} for n in changed_names}

facespec=[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]
glass=scene.objects['PASSARELA EXTERNA | vidro'].data.materials[0]
frame=scene.objects['PASSARELA EXTERNA | caixilho.012'].data.materials[0]
ivory=scene.objects[wall_names[0]].data.materials[0]
glass_z=bounds(scene.objects['PASSARELA EXTERNA | vidro'])[2]
z_breaks=[glass_z[0],71.60,72.75,glass_z[1]]

def boxes_mesh(obj,boxes,materials,label):
    vs=[];fs=[];material_ids=[];to_local=wm(obj).inverted()@M
    for limits,material in boxes:
        (a,b),(c,d),(e,f)=limits;assert b>a and d>c and f>e
        first=len(vs);vs.extend(tuple(to_local@Vector(p)) for p in [(a,c,e),(a,c,f),(a,d,e),(a,d,f),(b,c,e),(b,c,f),(b,d,e),(b,d,f)])
        fs.extend(tuple(first+i for i in face) for face in facespec);material_ids.extend([material]*6)
    mesh=bpy.data.meshes.new(label);mesh.from_pydata(vs,[],fs);mesh.update()
    for mat in materials:mesh.materials.append(mat)
    for poly,idx in zip(mesh.polygons,material_ids):poly.material_index=idx
    bm=bmesh.new();bm.from_mesh(mesh);assert not any(f.calc_area()<1e-8 for f in bm.faces);assert not any(not e.is_manifold for e in bm.edges)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();return mesh

staged=[];added=[];panels=[]
for name in floor_names:
    original=scene.objects[name];data=original.data.copy();transform=inv@wm(original);inverse_object=wm(original).inverted()@M
    limits=bounds(original);z0,z1=limits[2]
    for vertex in data.vertices:
        p=transform@vertex.co
        p.z=target_z if z1-z0<1e-5 else z0+(p.z-z0)*(target_z-z0)/(z1-z0)
        vertex.co=inverse_object@p
    data.update();staged.append((original,data))

collision_collection=scene.objects['B83 | COLLISION | SUPERIOR | posterior lateral'].users_collection[0]
for name in wall_names:
    original=scene.objects[name];(x0,x1),(y0,y1),(bottom,top)=bounds(original)
    border=.14;start=x0+border;end=x1-border;thick=.04;depth=.10
    # Mesmo vocabulário de travessas/vidro da passarela e retornos B84.
    # Ritmo e seções continuam aproximados, não cotas certificadas.
    count=math.ceil((end-start)/.68);xs=[start+(end-start)*i/count for i in range(count+1)]
    outer=y0 if (y0+y1)/2<0 else y1-depth
    boxes=[(((x0,x1),(y0,y1),(bottom,glass_z[0])),0),(((x0,x1),(y0,y1),(glass_z[1],top)),0),
           (((x0,start),(y0,y1),(glass_z[0],glass_z[1])),0),(((end,x1),(y0,y1),(glass_z[0],glass_z[1])),0)]
    for a,b in zip(xs,xs[1:]):
        for low,high in zip(z_breaks,z_breaks[1:]):boxes.append((((a+thick/2,b-thick/2),(outer+.045,outer+.085),(low+thick/2,high-thick/2)),1))
    for x in xs:boxes.append((((x-thick/2,x+thick/2),(outer,outer+depth),(glass_z[0],glass_z[1])),2))
    for z in z_breaks:boxes.append((((start,end),(outer,outer+depth),(z-thick/2,z+thick/2)),2))
    mesh=boxes_mesh(original,boxes,[ivory,glass,frame],name+' | fechamento envidraçado B87');staged.append((original,mesh))
    collider_name='B87 | COLLISION | '+name
    assert bpy.data.objects.get(collider_name) is None
    assert not any(o.get('boas_derived_from_object')==name for o in scene.objects if o.type=='MESH'), 'Revisar collider existente antes de criar redundância'
    placeholder=bpy.data.meshes.new(collider_name+' | staging')
    collider=bpy.data.objects.new(collider_name,placeholder)
    collider.data=boxes_mesh(collider,[(((x0,x1),(y0,y1),(bottom,top)),0)],[],collider_name+' | envelope')
    if placeholder.users==0:bpy.data.meshes.remove(placeholder)
    collider['boas_derived_from_object']=name;collider['boas_role']='STATIC_OBSTACLE';collider['boas_collision_profile_id']=profile['id'] if 'id' in profile else 'lacerda-corridor-b77'
    added.append(collider)
    panels.append({'object':name,'vertical_bays':count,'glass_panes':count*3,'glass_z':glass_z,'collider':collider_name,'pattern':'Mesmas travessas e materiais da passarela; subdivisão vertical aproximada','printed_dimension':False})

for original,data in staged:original.data=data
for collider in added:
    collision_collection.objects.link(collider);collider.hide_render=True;collider.hide_set(True)
    profile['collision_bindings'].append({'object':collider.name,'source':collider['boas_derived_from_object'],'role':'STATIC_OBSTACLE','moving':False,'enabled':True,
        'representation':'closed_glazing_wall_envelope','status':'candidate','triangles':12,'vertices':8})
for name in obsolete_names:
    obj=scene.objects[name];obj.hide_render=True;obj.hide_set(True)
    obj['boas_role']='SUPERSEDED_REFERENCE';obj['boas_physical_enabled']=False;obj['boas_active_authoring']=False
    if name.startswith('NAV |'):obj['game_role']='superseded_navigation_reference';obj.display_type='WIRE'

for obj in [scene.objects[n] for n in changed_names]+added:
    obj['boas_generated_revision']='R30B.87';obj['boas_provenance_ids']=json.dumps(['derived:lacerda-upper-finish-b87'])
    obj['boas_location_id']='elevador-lacerda';obj['accuracy']='APPROXIMATE';obj['replacement_required']=True;obj['boas_production_ready']=False
    obj['reference_status']='partial';obj['boas_pending_gate']='ARCHITECTURAL_SSOT_REGISTRATION_AND_INSTALLED_ELEVATORS'

assert all((scene.objects[n].data.as_pointer() if scene.objects[n].data else None,[list(r) for r in scene.objects[n].matrix_basis],scene.objects[n].hide_render,scene.objects[n].parent.name if scene.objects[n].parent else None)==state for n,state in protected.items())
assert sig(scene.objects['MVP | terreno corrigido | colisão estática'])==terrain_before
assert all(sig(bpy.data.objects[n])==state for n,state in proxy_before.items())
assert hashlib.sha256((root/'world/geographic-reference.json').read_bytes()).hexdigest()==ssot_hash
changes=[{'object':n,'before':before[n],'after':{'signature':sig(scene.objects[n]),'bounds':bounds(scene.objects[n]),'visible':scene.objects[n].visible_get(),'hide_render':scene.objects[n].hide_render}} for n in sorted(changed_names)]
report={'revision':'R30B.87','pid':os.getpid(),'scene':scene.name,'file':dest.relative_to(root).as_posix(),'parent_file':base.relative_to(root).as_posix(),'parent_sha256':base_hash,
        'changes':changes,'added_colliders':[{'object':o.name,'source':o['boas_derived_from_object'],'signature':sig(o),'bounds':bounds(o)} for o in added],
        'glazing':panels,'floor_level':{'before':floor_bounds[2][1],'after':target_z,'delta':delta,'source':finish.name,
            'independent_evidence':'Prancha SUCOP 17: acesso torre, circulações e salão no nível 0,00; datum global permanece candidato.'},
        'obsolete_nav_evidence':{'binding':old_binding,'source_history':'automation/blender/reconcile_upper_ground_b80.py'},
        'ssot_sha256':ssot_hash,'terrain_preserved':True,'proxy_b82_preserved':True,'protected_objects':len(protected),
        'historic_vertical_gate':'BLOCKED_EXTERNAL_EVIDENCE','historic_witnesses':27,'movement_enabled':False,'production_ready':False,'reopened':False}
scene['lacerda_revision']='R30B.87 | pisos reconciliados e fechamentos superiores envidraçados'
scene['boas_historic_movement_enabled']=False
report_path=out/'application.json';report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
with dest.open('rb') as f:report['sha256']=hashlib.file_digest(f,'sha256').hexdigest()
report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
profile.setdefault('upper_modeling_history',[]).append({'revision':'R30B.87','floor_level_evidence':report['floor_level'],'glazing_evidence':report_path.relative_to(root).as_posix(),'full_route_approved':False})
profile_path.write_text(json.dumps(profile,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
entry={'file':report['file'],'sha256':report['sha256'],'revision':report['revision'],'parent_file':report['parent_file'],'scene':scene.name,'status':'validation_candidate','production_ready':False,
       'evidence':report_path.relative_to(root).as_posix(),'notes':'Pisos e vidro superior reconciliados; dimensões instaladas e implantação das torres pendentes.'}
catalog['revisions'].append(entry)
for key in ('authoring_source','validation_source'):catalog[key]=entry.copy()
catalog_path.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
provenance_path=root/'world/data-provenance.json';provenance=json.loads(provenance_path.read_text(encoding='utf8'))
assert not any(v['resource_id']=='derived:lacerda-upper-finish-b87' for v in provenance['resources'])
provenance['resources'].append({'resource_id':'derived:lacerda-upper-finish-b87','provider':'Bay of All Saints / modelagem autoral','dataset':'Pisos e fechamento superior da planta/fotos',
    'capture_date':'2026-10-07','bounds':None,'raw_files':[],'derived_files':[report['file'],report_path.relative_to(root).as_posix()],
    'usage_class':'PENDENTE_VERIFICACAO','release_status':'REPLACE_BEFORE_RELEASE','purpose':'Continuidade de acabamento e fechamento envidraçado superior; não certifica instalação',
    'dependencies':['derived:lacerda-upper-layout-b86','derived:lacerda-upper-glazing-b84','source:lacerda-issue22-sucop-17','source:lacerda-exterior-photo-139fa6c8d4d1'],
    'kind':'geometry','generation_status':'APPLIED_REOPEN_VALIDATION_PENDING'})
provenance_path.write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'revision':report['revision'],'file':report['file'],'sha256':report['sha256'],'changed':len(changes),'added_colliders':len(added),'floor_delta':delta,'panes':[v['glass_panes'] for v in panels]}))
