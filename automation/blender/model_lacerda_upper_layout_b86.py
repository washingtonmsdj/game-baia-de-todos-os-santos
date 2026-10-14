"""B86: conjunto superior em planta; implantação e instalação permanecem candidatas."""
import bpy,bmesh,json,hashlib,os,runpy
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.geometry import tessellate_polygon

root=Path(__file__).resolve().parents[2];out=root/'docs/reports/blender/lacerda-layout-b86'
control_path=out/'application-control.json'
control=json.loads(control_path.read_text(encoding='utf8'))
assert control.get('execution_enabled') is True, 'Aplicação suspensa: recuperar e confirmar a sessão visível antes de executar B86.'
assert control.get('expected_session_pid')==os.getpid(), 'Sessão diferente da autorizada para a aplicação.'
base=Path(bpy.data.filepath);assert base.name=='salvador_lacerda_r30b85_apoio_encosta_proporcoes.blend'
scene=bpy.context.scene;assert scene.name=='SALVADOR | ESBOCO OFICIAL';assert not bpy.data.is_dirty
# Uma tentativa interrompida pode deixar cópias sem vínculo; não são arquitetura.
for previous in list(bpy.data.objects):
    if previous.name.startswith('B86_STAGING | ') and not previous.users_scene:
        data=previous.data;bpy.data.objects.remove(previous,do_unlink=True)
        if data is not None and data.users==0:bpy.data.meshes.remove(data)
dest=root/'blender/salvador_lacerda_r30b86_saguao_superior_planta.blend';assert not dest.exists()
catalog_path=root/'world/areas/mvp-centro-lacerda/blender-revisions.json';catalog=json.loads(catalog_path.read_text(encoding='utf8'))
with base.open('rb') as f:base_hash=hashlib.file_digest(f,'sha256').hexdigest()
assert base_hash==catalog['authoring_source']['sha256']
config=json.loads((out/'layout_source.json').read_text(encoding='utf8'))
deps=json.loads((out/'dependencies_before.json').read_text(encoding='utf8'))['rows']
assert not bpy.app.driver_namespace.get('boas_proxy_operator')
frame=Matrix(json.loads((root/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text(encoding='utf8'))['measurement_frame']);inverse=frame.inverted()
helpers=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));wm=helpers['world_matrix'];signature=helpers['signature']
ssot_hash=hashlib.sha256((root/'world/geographic-reference.json').read_bytes()).hexdigest()
proxy_before={o.name:signature(o) for o in bpy.data.collections['GAMEPLAY_PROXY | Lacerda B82'].objects}
terrain=scene.objects['MVP | terreno corrigido | colisão estática'];terrain_before=signature(terrain)

def shallow(obj):
    return {'data':obj.data.as_pointer() if obj.data else None,'basis':[list(r) for r in obj.matrix_basis], 'parent':obj.parent.name if obj.parent else None,'hide_render':obj.hide_render,'modifiers':[(m.name,m.type) for m in obj.modifiers]}

def bounds(obj):
    p=[inverse@wm(obj)@v.co for v in obj.data.vertices]
    return [[min(v[i] for v in p),max(v[i] for v in p)] for i in range(3)] if p else None

def classify(row):
    name=row['name'];low=name.casefold();bb=row['bounds']
    if not row['visible'] or row['animated'] or row['constraints']:return None
    if name.startswith('NAV |'):return None
    if name.startswith('LAC R30B08 | apoio oposto') or name.startswith('LAC R35 |'):
        return 'OLD_TOWER_ENVELOPE' if bb[0][0]>-8 else None
    if any(t in name for t in ('SUPERIOR |','FACHADA SUPERIOR |','EDIFICIO |','LAC R30B03 | Cidade Alta |')) and bb[0][0]>-7 and bb[1][0]<7:
        return 'BUILDING' if bb[1][2]>75.8 else 'STATION'
    if 'passarela' in low and bb[0][0]>-62 and bb[1][0]<6 and bb[0][2]>68 and bb[1][2]<75.5 and bb[0][1]>-3.4 and bb[1][1]<3.4:
        return 'BRIDGE'
    return None

domains={r['name']:classify(r) for r in deps if classify(r)}
floor_name='SUPERIOR | piso saguão';roof_name='SUPERIOR | cobertura saguão'
assert domains[floor_name]=='STATION' and domains[roof_name]=='STATION'
assert any(n.startswith('PASSARELA |') for n in domains)
# Bindings explícitos: fonte e derivado recebem a mesma operação geométrica.
binding_keys=('boas_derived_from_object','boas_source_object','boas_collision_source_object','source_object')
bindings=[]
for obj in scene.objects:
    if obj.type!='MESH' or obj.name in domains:continue
    src=next((obj.get(k) for k in binding_keys if isinstance(obj.get(k),str) and obj.get(k) in domains),None)
    if src:domains[obj.name]=domains[src];bindings.append({'collider':obj.name,'source':src})
binding_sources={row['collider']:row['source'] for row in bindings}
protected={o.name:shallow(o) for o in scene.objects if o.name not in domains}
old={n:{'signature':signature(scene.objects[n]),'bounds':bounds(scene.objects[n])} for n in domains}
station_x=config['main_station_x'];station_y=config['main_station_y'];building_x=config['upper_building_x'];building_y=config['upper_building_y']
outline=[Vector((*p,0)) for p in config['outline_local']]
# Contorno oeste do piso: plano comum para parede/ponte/piso, sem bloco invisível.
north,south=config['outline_local'][0],config['outline_local'][-1]
back_slope=(north[0]-south[0])/(north[1]-south[1]);back_zero=north[0]-back_slope*north[1]
def map_point(p,domain):
    q=p.copy()
    if domain=='STATION':
        knots=[-9.3,-3.,3.,9.3];targets=[station_y[0],*config['bridge_opening_y'],station_y[1]]
        segment=next((i for i in range(3) if p.y<=knots[i+1]),2)
        q.y=targets[segment]+(p.y-knots[segment])/(knots[segment+1]-knots[segment])*(targets[segment+1]-targets[segment])
        west=back_zero+back_slope*q.y
        q.x=west+(p.x+5.5)/11*(5.5-west)
    elif domain in ('BUILDING','OLD_TOWER_ENVELOPE'):
        q.x=building_x[0]+(p.x+5.5)/11*(building_x[1]-building_x[0])
        q.y=building_y[0]+(p.y+5.7)/11.4*(building_y[1]-building_y[0])
        if domain=='OLD_TOWER_ENVELOPE':
            q.x+=config['old_tower_envelope_center'][0]-sum(building_x)/2
            q.y+=config['old_tower_envelope_center'][1]-sum(building_y)/2
    return q

def prism(obj,polygon,z0,z1):
    vertices=[Vector((p.x,p.y,z)) for z in (z0,z1) for p in polygon];n=len(polygon)
    lookup={(round(p.x,7),round(p.y,7)):i for i,p in enumerate(polygon)}
    triangles=tessellate_polygon([polygon]);faces=[]
    planar=abs(z1-z0)<1e-6
    for tri in triangles:
        ids=[v if isinstance(v,int) else lookup[(round(v.x,7),round(v.y,7))] for v in tri]
        if planar:
            if (polygon[ids[1]]-polygon[ids[0]]).cross(polygon[ids[2]]-polygon[ids[0]]).z<0:ids.reverse()
            faces.append(tuple(ids))
        else:
            faces.append(tuple(reversed(ids)));faces.append(tuple(i+n for i in ids))
    if planar:vertices=vertices[:n]
    else:faces.extend((i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n))
    inverse_object=wm(obj).inverted();obj.data.clear_geometry();obj.data.from_pydata([tuple(inverse_object@frame@p) for p in vertices],[],faces)

changes=[];superseded=[];staged=[]
for name,domain in domains.items():
    original=scene.objects[name];assert not original.constraints
    original_bm=bmesh.new();original_bm.from_mesh(original.data)
    baseline_degenerate=sum(f.calc_area()<1e-8 for f in original_bm.faces);original_bm.free()
    obj=original.copy();obj.name='B86_STAGING | '+name
    obj.data=obj.data.copy();matrix=wm(obj);inverse_object=matrix.inverted()
    if domain=='BRIDGE':
        points=[inverse@matrix@v.co for v in obj.data.vertices]
        signed=[p.x-back_zero-back_slope*p.y for p in points]
        if min(signed)>1e-5:
            obj.hide_render=True
            obj['boas_role']='SUPERSEDED_REFERENCE';obj['boas_active_authoring']=False;superseded.append(name)
        elif max(signed)>1e-5:
            bm=bmesh.new();bm.from_mesh(obj.data)
            for v in bm.verts:v.co=inverse@matrix@v.co
            bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-6,plane_co=Vector((back_zero,0,0)),plane_no=Vector((1,-back_slope,0)),clear_outer=True)
            edges=[e for e in bm.edges if e.is_boundary and all(abs(v.co.x-back_zero-back_slope*v.co.y)<1e-4 for v in e.verts)]
            if len(edges)>=3:bmesh.ops.holes_fill(bm,edges=edges,sides=0)
            for v in bm.verts:v.co=inverse_object@frame@v.co
            bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free()
    elif name in (floor_name,roof_name) or binding_sources.get(name) in (floor_name,roof_name):
        z0,z1=old[name]['bounds'][2]
        if binding_sources.get(name)==floor_name:
            thickness=z1-z0;z1=old[floor_name]['bounds'][2][1];z0=z1-thickness
        prism(obj,outline,z0,z1)
    else:
        for v in obj.data.vertices:v.co=inverse_object@frame@map_point(inverse@matrix@v.co,domain)
    obj.data.update();bm=bmesh.new();bm.from_mesh(obj.data)
    bad=[f for f in bm.faces if f.calc_area()<1e-8]
    assert len(bad)<=baseline_degenerate, 'Nova face degenerada: '+name
    removed_degenerate=len(bad)
    if bad:
        # Faces comprovadamente sem área já presentes na malha-base.
        bmesh.ops.delete(bm,geom=bad,context='FACES_ONLY')
        loose_edges=[e for e in bm.edges if not e.link_faces]
        if loose_edges:bmesh.ops.delete(bm,geom=loose_edges,context='EDGES')
        loose_vertices=[v for v in bm.verts if not v.link_edges]
        if loose_vertices:bmesh.ops.delete(bm,geom=loose_vertices,context='VERTS')
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free()
    obj['boas_generated_revision']='R30B.86';obj['boas_provenance_ids']=json.dumps(['derived:lacerda-upper-layout-b86'])
    obj['reference_status']='partial';obj['accuracy']='PROJECT_REFERENCE_DERIVED' if domain=='STATION' else 'APPROXIMATE'
    obj['replacement_required']=True;obj['boas_production_ready']=False
    obj['boas_layout_domain']=domain;obj['boas_pending_gate']='ARCHITECTURAL_SSOT_REGISTRATION_AND_INSTALLED_ELEVATORS'
    after=signature(obj)
    changes.append({'object':name,'domain':domain,'before':old[name],'after':{'signature':after,'bounds':bounds(obj)},'superseded':name in superseded,
                    'baseline_degenerate_faces':baseline_degenerate,'removed_degenerate_faces':removed_degenerate})
    staged.append((original,obj,name in superseded))

# Todas as malhas são conferidas antes de trocar qualquer malha da cena visível.
assert json.loads(control_path.read_text(encoding='utf8')).get('execution_enabled') is True, 'Aplicação cancelada antes do commit de malhas.'
for original,temporary,is_superseded in staged:
    if original.name in (floor_name,roof_name):
        bm=bmesh.new();bm.from_mesh(temporary.data)
        assert not any(e.is_boundary or not e.is_manifold for e in bm.edges)
        bm.free()
for original,temporary,is_superseded in staged:
    original.data=temporary.data
    for key in ('boas_generated_revision','boas_provenance_ids','reference_status','accuracy','replacement_required','boas_production_ready','boas_layout_domain','boas_pending_gate'):
        original[key]=temporary[key]
    if is_superseded:
        original.hide_set(True,view_layer=scene.view_layers[0]);original.hide_render=True
        original['boas_role']='SUPERSEDED_REFERENCE';original['boas_active_authoring']=False
    bpy.data.objects.remove(temporary,do_unlink=True)

assert all(shallow(scene.objects[n])==state for n,state in protected.items())
assert signature(terrain)==terrain_before
assert all(signature(bpy.data.objects[n])==state for n,state in proxy_before.items())
assert hashlib.sha256((root/'world/geographic-reference.json').read_bytes()).hexdigest()==ssot_hash
for n in (floor_name,roof_name):
    bm=bmesh.new();bm.from_mesh(scene.objects[n].data);assert not any(e.is_boundary or not e.is_manifold for e in bm.edges);bm.free()
scene['lacerda_revision']='R30B.86 | conjunto superior derivado da planta 17; implantação pendente'
scene['lacerda_reference_status']='partial; planta 2023, sem certificação as-built ou da implantação'
scene['boas_historic_movement_enabled']=False
report={'revision':'R30B.86','pid':os.getpid(),'file':dest.relative_to(root).as_posix(),'parent_file':base.relative_to(root).as_posix(),'parent_sha256':base_hash,
        'scene':scene.name,'changes':changes,'superseded_bridge_components':superseded,'collider_bindings_updated':bindings,
        'source_layout':'docs/reports/blender/lacerda-layout-b86/layout_source.json','ssot_sha256':ssot_hash,'protected_objects':len(protected),
        'terrain_preserved':True,'proxy_b82_preserved':True,'low_city_tower_preserved':True,'installed_elevators_preserved':True,
        'historic_vertical_gate':'BLOCKED_EXTERNAL_EVIDENCE','historic_witnesses':27,'movement_enabled':False,
        'placement_gate':'NEEDS_REGISTRATION','bridge_length_gate':'MAP_ANCHOR_DISTANCE_UNRESOLVED','production_ready':False,'reopened':False}
report_path=out/'application.json';report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
with dest.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
report['sha256']=digest;report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
entry={'file':report['file'],'revision':'R30B.86','parent_file':report['parent_file'],'sha256':digest,'status':'validation_candidate','scene':scene.name,'production_ready':False,'evidence':report_path.relative_to(root).as_posix(),'notes':'Conjunto superior derivado da planta; distância/orientação das torres e instalação permanecem pendentes.'}
catalog['revisions'].append(entry)
for key in ('authoring_source','validation_source'):catalog[key]=entry.copy()
catalog['authoring_scene']=scene.name;catalog_path.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
provenance_path=root/'world/data-provenance.json'
provenance=json.loads(provenance_path.read_text(encoding='utf8'))
resource=next(v for v in provenance['resources'] if v['resource_id']=='derived:lacerda-upper-layout-b86')
resource['derived_files']=list(dict.fromkeys(resource['derived_files']+[report['file'],report_path.relative_to(root).as_posix()]))
resource.pop('planned_outputs',None);resource['kind']='geometry';resource['generation_status']='APPLIED_REOPEN_VALIDATION_PENDING'
provenance_path.write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'revision':report['revision'],'changes':len(changes),'superseded':len(superseded),'bindings':len(bindings),'file':report['file'],'sha256':digest,'production_ready':False}))
