"""Colisão de pisos e demonstração do serviço existente, na única sessão B76."""
import bpy,json,math,hashlib,runpy
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/reports/blender/lacerda-corridor';scene=bpy.context.scene
catalog=json.loads((ROOT/'world/areas/mvp-centro-lacerda/blender-revisions.json').read_text(encoding='utf8'));source=catalog['validation_source']
assert source['revision']=='R30B.76' and Path(bpy.data.filepath).resolve()==(ROOT/source['file']).resolve()
ssot=ROOT/'world/geographic-reference.json';assert scene['boas_geographic_ssot_sha256']==hashlib.sha256(ssot.read_bytes()).hexdigest()
qa=json.loads((OUT/'walkability_candidate_b77.json').read_text(encoding='utf8'))
assert all(qa['routes'][k]['status']=='sampled_clear' for k in ('upper','lower'))
shaft=json.loads((OUT/'portal_probe_b77.json').read_text(encoding='utf8'))
assert {p['blocker'] for p in shaft['shaft_character_sweep'] if p['blocker']} <= {'LAC R30B07 | galeria | consolo inclinado','FUNCIONAL | 3 teto','FUNCIONAL | 3 iluminação'}
assert not bpy.data.objects.get('B77 | QA | personagem')
frame=scene.frame_current
# Snapshot B76 incluindo Campo, materiais, animação anterior e visibilidade.
sig=runpy.run_path(str(ROOT/'automation/blender/component_fingerprint.py'))['signature'];snapshot={}
for ob in scene.objects:
    try:s=sig(ob)
    except RuntimeError:s={'type':ob.type,'transform':[list(r) for r in ob.matrix_world],'data_name':ob.data.name if ob.data else None,'constraints':[(c.name,c.type) for c in ob.constraints]}
    snapshot[ob.name]={'signature':s,'parent':ob.parent.name if ob.parent else None,'collections':[c.name for c in ob.users_collection],'visible':ob.visible_get(),'hide_render':ob.hide_render,'action':ob.animation_data.action.name if ob.animation_data and ob.animation_data.action else None}
artifact=ROOT/'artifacts/lacerda-corridor';artifact.mkdir(parents=True,exist_ok=True)
def checkpoint(stage):
    (artifact/'model_b77_progress.json').write_text(json.dumps({'stage':stage,'file':bpy.data.filepath}),encoding='utf8')
checkpoint('snapshot')
(artifact/'protected_b76.json').write_text(json.dumps(snapshot,ensure_ascii=False),encoding='utf8')
floor_col=bpy.data.collections['33.3 RUNTIME | WALKABLE'];nav_col=bpy.data.collections['37.1 NAV | PEDESTRIAN PATHS']
floor_col['boas_detail_level']='PLAYABLE_CORE'
resource_ids=json.dumps(['derived:lacerda-corridor-b77'])
added=[];collision_bindings=[];dg=bpy.context.evaluated_depsgraph_get()
def mark(ob,role):
    ob['boas_role']=role;ob['boas_provenance_ids']=resource_ids;ob['boas_geographic_ssot_id']=scene['boas_geographic_ssot_id'];ob['boas_production_ready']=False;ob['boas_generated_revision']='R30B.77';added.append(ob.name)
def collision(ob):
    checkpoint('collision: '+ob.name)
    ev=ob.evaluated_get(dg);mesh=ev.to_mesh()
    try:
        mesh.calc_loop_triangles();v=[ev.matrix_world@p.co for p in mesh.vertices];polys=[tuple(t.vertices) for t in mesh.loop_triangles]
        tree=BVHTree.FromPolygons(v,polys,all_triangles=True);top=max(p.z for p in v);bottom=min(p.z for p in v);faces=[]
        for f in polys:
            p=[v[i] for i in f];n=(p[1]-p[0]).cross(p[2]-p[0])
            if n.length<1e-9 or abs(n.z)/n.length<.7:continue
            midpoint=sum(p,Vector())/3;hit=tree.ray_cast(Vector((midpoint.x,midpoint.y,top+1)),Vector((0,0,-1)),top-bottom+2)[0]
            if hit is not None and abs(hit.z-midpoint.z)<.0002:faces.append(tuple(f) if n.z>0 else tuple(reversed(f)))
        used=sorted({i for f in faces for i in f});mapping={old:new for new,old in enumerate(used)}
        data=bpy.data.meshes.new('B77 | collision | '+ob.name);data.from_pydata([v[i] for i in used],[],[tuple(mapping[i] for i in f) for f in faces]);data.update()
    finally:ev.to_mesh_clear()
    assert faces, 'Sem superfície superior: '+ob.name
    result=bpy.data.objects.new('B77 | COLLISION | '+ob.name,data);floor_col.objects.link(result);mark(result,'COLLISION_WALKABLE_CANDIDATE')
    result.hide_render=True;result.hide_set(True);result['boas_collision_profile_id']='lacerda-corridor-b77';result['boas_derived_from_object']=ob.name
    result['boas_source_blend']=source['file'];result['boas_source_sha256']=source['sha256']
    if ob.name=='FUNCIONAL | 3 piso':
        result.parent=ob;result.matrix_parent_inverse=ob.matrix_world.inverted()
        result['boas_collision_motion']='inherit_existing_cabin'
    collision_bindings.append({'object':result.name,'source':ob.name,'triangles':len(faces),'vertices':len(used),'moving':ob.name=='FUNCIONAL | 3 piso'})
    return result
for name in qa['collision_sources']:
    if name=='MVP | terreno corrigido | colisão estática':continue # colisor global existente é reaproveitado
    if name=='LAC R30B | Passarela | piso paginado visual':continue # textura/paginação não vira colisor
    if name=='CALIBRADO | passarela piso 28.71 x 6.00m':name='NAV | passarela superior' # proxy simples existente, delta visual 8 mm
    if bpy.data.objects.get(name):collision(bpy.data.objects[name])
platform=collision(bpy.data.objects['FUNCIONAL | 3 piso'])
del dg
checkpoint('consolo')
# Corrigir somente a interseção comprovada: abertura derivada da seção existente
# da cabine, sem alterar posição do consolo, cabine, torre ou geografia.
from mathutils.geometry import convex_hull_2d
floor=bpy.data.objects['FUNCIONAL | 3 piso']
xy=sorted({(round((floor.matrix_world@v.co).x,6),round((floor.matrix_world@v.co).y,6)) for v in floor.data.vertices})
points=[Vector(p) for p in xy];hull=[points[i] for i in convex_hull_2d(points)];n=len(hull)
lo=qa['elevator']['lower_z']-.16;hi=max((bpy.data.objects['FUNCIONAL | 3 teto'].matrix_world@v.co).z for v in bpy.data.objects['FUNCIONAL | 3 teto'].data.vertices)
mesh=bpy.data.meshes.new('B77 | seção cabine 3');mesh.from_pydata([(p.x,p.y,z) for z in (lo,hi) for p in hull],[],[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]);mesh.update()
cutter=bpy.data.objects.new('B77 | REFERENCE | seção vertical cabine 3',mesh);floor_col.objects.link(cutter);mark(cutter,'REFERENCE_SHAFT_ENVELOPE');cutter.hide_render=True;cutter.hide_set(True)
consolo=bpy.data.objects['LAC R30B07 | galeria | consolo inclinado'];modifier=consolo.modifiers.new('B77 | abertura da seção existente cabine 3','BOOLEAN');modifier.operation='DIFFERENCE';modifier.solver='EXACT';modifier.object=cutter
consolo['boas_correction_class']='ERROR';consolo['boas_correction_evidence']='docs/reports/blender/lacerda-corridor/portal_probe_b77.json';consolo['boas_provenance_ids']=resource_ids
# Um volume sem altura de referência não pode tamponar o saguão modelado.
# Conserva malha, XY, Z, nome e coleção. Não identifica nem move um Hero por OSM ID.
proxy=bpy.data.objects['OSM | 1263035777'];assert any(c.name=='20 MVP | edifícios OSM do Aleph' for c in proxy.users_collection)
proxy.hide_render=True;proxy.hide_set(True);proxy['boas_source_reference']=True;proxy['boas_proxy_superseded_for_corridor']=True;proxy['boas_collision_candidate']=False
proxy['boas_provenance_ids']=json.dumps(['source:legacy-lacerda-authoring'])
upper=qa['routes']['upper']['points'];lower=qa['routes']['lower']['points'];fps=scene.render.fps/scene.render.fps_base
start=65000;speed=1.4;arrival=start+math.ceil(qa['routes']['upper']['length_design_units']/speed*fps)
departure=arrival+48;land=departure+round(20*fps);walk_out=land+48
end=walk_out+math.ceil(qa['routes']['lower']['length_design_units']/speed*fps)
trip=qa['elevator']['travel_design_units'];animated=[]
def key_location(ob,index,keys):
    assert not (ob.animation_data and ob.animation_data.action), 'Animação anterior deve ser preservada: '+ob.name
    original=ob.location[index]
    for f,value in keys:ob.location[index]=value;ob.keyframe_insert(data_path='location',index=index,frame=f,group='B77 | elevador existente')
    ob.location[index]=original
    animated.append(ob.name)
# Componentes raiz existentes da cabine 3; filhos visuais acompanham os pais.
moving=[]
checkpoint('cabin animation')
for ob in scene.objects:
    if ob.get('elevator_id')==3 and ob.get('elevator_role') in ('cabin','cabin_door'):
        ancestor=ob.parent;inherited=False
        while ancestor:
            if ancestor.get('elevator_id')==3 and ancestor.get('elevator_role') in ('cabin','cabin_door'):inherited=True;break
            ancestor=ancestor.parent
        if not inherited:moving.append(ob)
for ob in moving:
    key_location(ob,2,[(start,ob.location.z),(departure,ob.location.z),(land,ob.location.z-trip),(end+24,ob.location.z-trip)])
# Abrir os pares existentes na direção real entre suas folhas. Sem nova porta.
doors=[o for o in scene.objects if o.get('elevator_id')==3 and o.get('elevator_role') in ('cabin_door','landing_door')]
groups={}
for ob in doors:
    group=('cabin',ob.get('door_side')) if ob.get('elevator_role')=='cabin_door' else ('station',ob.get('landing'))
    groups.setdefault(group,[]).append(ob)
door_states=[]
for group,objects in groups.items():
    checkpoint('door animation: '+str(group))
    assert len(objects)==2
    objects.sort(key=lambda o:o.get('door_leaf'));a,b=objects
    def geometric_center(ob):return sum((ob.matrix_world@Vector(p) for p in ob.bound_box),Vector())/8
    vector=geometric_center(b)-geometric_center(a);vector.z=0;assert vector.length>.01;vector.normalize()
    is_upper=group[1] in ('upper',1)
    opening=[(start,0),(start+24,1),(arrival+24,1),(departure,0),(end+24,0)] if is_upper else [(start,0),(land,0),(land+24,1),(end+24,1)]
    for ob,sign in ((a,-1),(b,1)):
        # As folhas foram modeladas na orientação global preservada.
        projected=[(ob.matrix_world@Vector(p)).dot(vector) for p in ob.bound_box]
        distance=max(projected)-min(projected)
        local=ob.parent.matrix_world.inverted().to_3x3()@vector if ob.parent else vector
        original=ob.location.copy()
        for f,amount in opening:
            ob.location=original+local*(sign*distance*amount)
            for index in (0,1):ob.keyframe_insert(data_path='location',index=index,frame=f,group='B77 | portas existentes')
        ob.location=original;animated.append(ob.name)
    door_states.append({'group':list(group),'objects':[a.name,b.name],'keys':opening})
for label,points in (('superior',upper),('inferior',lower)):
    data=bpy.data.curves.new('B77 | percurso '+label,'CURVE');data.dimensions='3D';data.bevel_depth=.02
    spline=data.splines.new('POLY');spline.points.add(len(points)-1)
    for p,xyz in zip(spline.points,points):p.co=(xyz[0],xyz[1],xyz[2]+.025,1)
    ob=bpy.data.objects.new('B77 | NAV QA | '+label,data);nav_col.objects.link(ob);mark(ob,'NAVIGATION_QA');ob.hide_render=True
camera_data=bpy.data.cameras.new('B77 | QA | personagem');camera_data.lens=22
camera=bpy.data.objects.new('B77 | QA | personagem',camera_data);nav_col.objects.link(camera);mark(camera,'QA_CAMERA')
def camera_route(points,first):
    elapsed=0
    for i,p in enumerate(points):
        if i:elapsed+=math.dist(points[i-1],p)/speed*fps
        f=first+round(elapsed);camera.location=(p[0],p[1],p[2]+1.65)
        following=points[min(i+4,len(points)-1)];direction=Vector((following[0]-p[0],following[1]-p[1],0))
        if direction.length>.01:camera.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
        camera.keyframe_insert(data_path='location',frame=f);camera.keyframe_insert(data_path='rotation_euler',frame=f)
checkpoint('camera upper');camera_route(upper,start+24)
for f,z in ((departure,qa['elevator']['upper_z']),(land,qa['elevator']['lower_z']),(walk_out,qa['elevator']['lower_z'])):
    camera.location=(upper[-1][0],upper[-1][1],z+1.65);camera.keyframe_insert(data_path='location',frame=f)
checkpoint('camera lower');camera_route(lower,walk_out)
scene.camera=camera;scene.frame_end=max(scene.frame_end,end+24)
# Linear evita overshoot da cabine/câmera para fora do trajeto medido.
for ob in [camera]+[bpy.data.objects[name] for name in set(animated)]:
    action=ob.animation_data.action
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for curve in bag.fcurves:
                    for key in curve.keyframe_points:key.interpolation='LINEAR'
for name,f in (('B77 | caminhada Tomé-Lacerda',start+24),('B77 | descida',departure),('B77 | saída Cairu-Mercado',walk_out),('B77 | fim',end)):
    scene.timeline_markers.new(name,frame=f)
scene['boas_corridor_profile']='world/areas/mvp-centro-lacerda/corridor-slice.json';scene['boas_provenance_registry']='world/data-provenance.json'
for name,ids in [('SOURCE_GEOREF | CENTRO LAPA TORORO FONTE NOVA',['source:osm-centro-20261005']),('40 | EXPANSAO CENTRO | REFERENCE_TERRAIN',['source:terrarium-centro-20261005'])]:
    col=bpy.data.collections.get(name)
    if col:col['boas_provenance_ids']=json.dumps(ids)
scene.frame_set(frame)
checkpoint('portal verification')
# Repetir a sondagem do poço após o recorte local, ainda na única janela.
runpy.run_path(str(ROOT/'automation/blender/probe_lacerda_portal_b77.py'))
after=json.loads((OUT/'portal_probe_b77.json').read_text(encoding='utf8'));assert after['shaft_character_blocked']==0, 'Poço ainda bloqueado; não salvar/promover'
destination=ROOT/'blender/salvador_lacerda_r30b77_corredor_lacerda_cairu.blend';assert not destination.exists()
checkpoint('save')
bpy.ops.wm.save_as_mainfile(filepath=str(destination),compress=True)
with destination.open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
result={'revision':'R30B.77','source_before':source,'source_after':{'file':destination.relative_to(ROOT).as_posix(),'sha256':sha,'revision':'R30B.77'},'baseline_frame':frame,'added_objects':added,'collision_bindings':collision_bindings,'animated_existing_objects':sorted(set(animated)),'door_states':door_states,'timeline':{'start':start+24,'departure':departure,'landing':land,'walk_out':walk_out,'end':end,'walking_speed_design_units_per_second':speed,'trip_seconds_design':20},'changed_visibility':[proxy.name],'existing_meshes_changed':False,'hero_assets_relocated':False,'terrain_changed':False,'ssot_sha256':hashlib.sha256(ssot.read_bytes()).hexdigest(),'engine_physics_verified':False}
(OUT/'scene_b77.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
result['local_correction']={'object':consolo.name,'modifier':modifier.name,'cutter':cutter.name,'method':'difference da seção XY real da cabine existente, extrudida entre paradas; base mesh e transforms preservados','reference_dimensions_status':'candidate; dimensões históricas da cabine não levantadas','shaft_character_blocked_after':after['shaft_character_blocked']}
result['existing_base_meshes_changed']=result.pop('existing_meshes_changed');result['existing_evaluated_meshes_changed']=[consolo.name]
(OUT/'scene_b77.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'file':result['source_after']['file'],'collision_objects':len(collision_bindings),'animated_objects':len(set(animated)),'timeline':result['timeline']},ensure_ascii=False))
checkpoint('complete')
