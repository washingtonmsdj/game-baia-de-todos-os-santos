"""B88: estrutura arquitetônica relativa derivada dos vetores/cotas SUCOP.

Executado na única janela visível. Não altera SSOT, terreno, B82 ou instalação.
"""
import bpy,bmesh,json,math,hashlib,os,runpy
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.geometry import delaunay_2d_cdt

root=Path(__file__).resolve().parents[2];out=root/'docs/reports/blender/lacerda-massing-b88'
base=Path(bpy.data.filepath);scene=bpy.context.scene
assert base.name=='salvador_lacerda_r30b87_pisos_e_fechamentos_superiores.blend' and scene.name=='SALVADOR | ESBOCO OFICIAL'
assert os.getpid()==16912 and not bpy.app.is_job_running('RENDER')
dest=root/'blender/salvador_lacerda_r30b88_estrutura_arquitetonica_plantas.blend';assert not dest.exists()
cfg=json.loads((out/'architectural-controls.json').read_text(encoding='utf8'))
catalog_path=root/'world/areas/mvp-centro-lacerda/blender-revisions.json';catalog=json.loads(catalog_path.read_text(encoding='utf8'))
with base.open('rb') as f:base_hash=hashlib.file_digest(f,'sha256').hexdigest()
assert base_hash==catalog['authoring_source']['sha256']
ssot_path=root/'world/geographic-reference.json';assert hashlib.sha256(ssot_path.read_bytes()).hexdigest()==cfg['ssot_sha256']
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));wm=h['world_matrix'];sig=h['signature']
M=Matrix(json.loads((root/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text())['measurement_frame']);inv=M.inverted()
polys={k:[Vector(p) for p in v['points_local']] for k,v in cfg['polygons'].items()}
proxy_before={o.name:sig(o) for o in bpy.data.collections['GAMEPLAY_PROXY | Lacerda B82'].objects}
terrain=scene.objects['MVP | terreno corrigido | colisão estática'];terrain_before=sig(terrain)

def area(p):return sum(a.x*b.y-a.y*b.x for a,b in zip(p,p[1:]+p[:1]))/2
def clean(p):
    q=[]
    for v in p:
        if not q or (v-q[-1]).length>.012:q.append(v.copy())
    if (q[-1]-q[0]).length<.012:q.pop()
    if area(q)<0:q.reverse()
    return q
polys={k:clean(v) for k,v in polys.items()}
def bounds(o):
    trans=inv@wm(o);p=[trans@v.co for v in o.data.vertices]
    return [[min(v[i] for v in p),max(v[i] for v in p)] for i in range(3)] if p else None
def inside(p,poly):
    hit=False
    for a,b in zip(poly,poly[1:]+poly[:1]):
        if (a.y>p.y)!=(b.y>p.y) and p.x<(b.x-a.x)*(p.y-a.y)/(b.y-a.y)+a.x:hit=not hit
    return hit
def inset(poly,t):
    result=[]
    for i,b in enumerate(poly):
        a=poly[i-1];c=poly[(i+1)%len(poly)];u=(b-a).normalized();v=(c-b).normalized()
        nu=Vector((-u.y,u.x));nv=Vector((-v.y,v.x));p=b+nu*t;q=b+nv*t
        cross=u.x*v.y-u.y*v.x
        if abs(cross)<1e-6:r=b+(nu+nv)*(.5*t)
        else:
            d=q-p;r=p+u*((d.x*v.y-d.y*v.x)/cross)
        assert (r-b).length<2., 'Inset inválido';result.append(r)
    return result
def mesh_geometry(o,verts,faces,label,material_ids=None,materials=None):
    mesh=bpy.data.meshes.new(label);trans=wm(o).inverted()@M
    mesh.from_pydata([tuple(trans@Vector(v)) for v in verts],[],faces);mesh.update()
    for mat in (materials if materials is not None else list(o.data.materials)):mesh.materials.append(mat)
    if material_ids:
        for f,i in zip(mesh.polygons,material_ids):f.material_index=i
    bm=bmesh.new();bm.from_mesh(mesh);bad=[f for f in bm.faces if f.calc_area()<1e-9]
    assert not bad,'Face sem área: '+o.name
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();return mesh
def slab(o,outer,z0,z1,holes=()):
    loops=[clean(outer)]+[clean(p) for p in holes];v=[];edges=[];loop_ids=[]
    for p in loops:
        start=len(v);v.extend(p);ids=list(range(start,len(v)));loop_ids.append(ids);edges.extend((i,ids[(j+1)%len(ids)]) for j,i in enumerate(ids))
    result=delaunay_2d_cdt(v,edges,[loop_ids[0]],1,1e-6)
    flat=list(result[0]);triangles=[]
    for f in result[2]:
        p=sum((flat[i] for i in f),Vector((0.,0.)))/len(f)
        if not any(inside(p,hole) for hole in loops[1:]):triangles.append(tuple(f))
    measured=sum(abs(area([flat[i] for i in f])) for f in triangles)
    expected=abs(area(loops[0]))-sum(abs(area(p)) for p in loops[1:])
    assert abs(measured-expected)<.02,(o.name,'área triangulada',measured,expected)
    # Identidade das bordas garantida pelo CDT; extrusão usa as arestas externas
    # dos triângulos para incluir recortes/quinas sem faces sobrepostas.
    n=len(flat);verts=[(p.x,p.y,z) for z in (z0,z1) for p in flat];faces=[]
    count={};directed={}
    for tri in triangles:
        if area([flat[i] for i in tri])<0:tri=tuple(reversed(tri))
        faces.extend((tuple(reversed(tri)),tuple(i+n for i in tri)))
        for a,b in zip(tri,tri[1:]+tri[:1]):
            key=tuple(sorted((a,b)));count[key]=count.get(key,0)+1;directed[key]=(a,b)
    for key,c in count.items():
        if c==1:
            a,b=directed[key];faces.append((a,b,b+n,a+n))
    return mesh_geometry(o,verts,faces,'B88 | '+o.name)
def strips(o,outer,inner,z0,z1,which=None):
    vertices=[];faces=[]
    for i,a in enumerate(outer):
        if which and not which(i):continue
        b=outer[(i+1)%len(outer)];c=inner[(i+1)%len(inner)];d=inner[i];k=len(vertices)
        vertices.extend((p.x,p.y,z) for z in (z0,z1) for p in (a,b,c,d))
        faces.extend(tuple(k+j for j in f) for f in [(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
    return mesh_geometry(o,vertices,faces,'B88 | '+o.name)

rows=json.loads((out/'before.json').read_text(encoding='utf8'))['rows'];rows_by_name={r['name']:r for r in rows}
previous=json.loads((root/'docs/reports/blender/lacerda-layout-b86/application.json').read_text())
prior_domains={r['object']:r['domain'] for r in previous['changes'] if not r['superseded']}
domains={};archived=[]
# Inventário delimitado da arquitetura, sem seleção da cidade por nome parecido.
for r in rows:
    if not r['visible'] or r['animated'] or r['constraints']:continue
    n=r['name'];b=r['bounds'];low=n.casefold()
    if n.startswith(('FUNCIONAL |','CABINE |','SALA DE MÁQUINAS |','NAV |','INFERIOR | catraca','INFERIOR | braço','INFERIOR | guia','SUPERIOR | catraca','SUPERIOR | braço','SUPERIOR | guia','REFINO 2025 |')) or 'Vedacao | FUNCIONAL' in n or 'Vedação | FUNCIONAL' in n:
        archived.append(n);continue
    old_domain=prior_domains.get(n)
    if old_domain=='BRIDGE' or ('passarela' in low and b[0][0]>-62 and b[0][1]<-18 and b[1][0]>-3.6 and b[1][1]<3.6 and b[2][0]>67):domains[n]='BRIDGE'
    elif old_domain=='STATION' or n.startswith('B87 | COLLISION | SUPERIOR | parede'):domains[n]='UPPER_STATION'
    elif old_domain=='BUILDING':domains[n]='UPPER_BUILDING'
    elif old_domain=='OLD_TOWER_ENVELOPE':domains[n]='OLD_TOWER'
    elif n.startswith(('GALERIA |','ESTAÇÃO SUPERIOR |','TORRE | cornija','TORRE | teto','LAC R30B | Galeria','LAC R30B07 | galeria')):domains[n]='NEW_GALLERY'
    elif n.startswith(('INFERIOR | piso','INFERIOR | cobertura','INFERIOR | parede','INFERIOR | pilar','INFERIOR | verga')):domains[n]='LOWER_LOBBY'
    elif b[0][0]>-65 and b[0][1]<-60 and b[2][1]>13 and n.startswith(('CASCA |','TORRE |','LAC R30B07 | torre','LAC R30B07 | corpo','LAC R30B07 | continuidade','LAC R30B20 | torre','LAC R30B20 | corpo')):domains[n]='NEW_TOWER'
# Todas as animações históricas continuam intactas e congeladas como referência.
for r in rows:
    if r['animated'] and r['visible'] and r['name'] not in archived:archived.append(r['name'])
bindings=[];binding_keys=('boas_derived_from_object','boas_source_object','boas_collision_source_object','source_object')
for o in scene.objects:
    if o.type!='MESH' or o.name in domains:continue
    src=next((o.get(k) for k in binding_keys if isinstance(o.get(k),str) and o.get(k) in domains),None)
    if src:domains[o.name]=domains[src];bindings.append({'object':o.name,'source':src})
src_by_collider={r['object']:r['source'] for r in bindings}
assert 'LAC R30B | Passarela | piso paginado visual' in domains
assert 'LAC R30B08 | apoio oposto | corpo estrutural afunilado' in domains
assert all(n not in proxy_before for n in domains)
before={n:{'signature':sig(scene.objects[n]),'bounds':bounds(scene.objects[n])} for n in domains}
protected={o.name:(o.data.as_pointer() if o.data else None,[list(r) for r in o.matrix_basis]) for o in scene.objects if o.name not in domains}
zupper=cfg['levels']['upper_walkable'];zlower=cfg['levels']['lower_scene_floor_preserved']
tower_angle=cfg['new_tower_basis']['angle'];ct,st=math.cos(tower_angle),math.sin(tower_angle)
center=Vector(cfg['new_tower_basis']['center_local'])
coords=[Vector((ct*(p.x-center.x)+st*(p.y-center.y),-st*(p.x-center.x)+ct*(p.y-center.y))) for p in polys['new_core']]
limits=[[min(p[i] for p in coords),max(p[i] for p in coords)] for i in (0,1)]
new_size=[b-a for a,b in limits]
core_center_local=Vector((sum(limits[0])/2,sum(limits[1])/2))
def new_tower(p):
    x=(p.x+62.813546)/3.55*new_size[0]+core_center_local.x;y=p.y/7.48*new_size[1]+core_center_local.y
    return Vector((center.x+ct*x-st*y,center.y+st*x+ct*y,p.z))
def gallery(p):
    headcoords=[Vector((ct*(v.x-center.x)+st*(v.y-center.y),-st*(v.x-center.x)+ct*(v.y-center.y))) for v in polys['new_gallery']]
    lo=[min(v[i] for v in headcoords) for i in (0,1)];hi=[max(v[i] for v in headcoords) for i in (0,1)]
    x=lo[0]+(p.x+67.313546)/9*(hi[0]-lo[0]);y=lo[1]+(p.y+5.2)/10.4*(hi[1]-lo[1])
    return Vector((center.x+ct*x-st*y,center.y+st*x+ct*y,zupper+(p.z-70.)*4./4.125))
bridge_points=[Vector(p) for p in cfg['polygons']['bridge']['points_local']]
a,b,c,d=bridge_points
old_west=-61.038545;old_north=-19.810818;old_south=-19.763916
def bridge(p):
    side=(p.y+3.)/6.;end=old_south+(old_north-old_south)*side
    u=(p.x-old_west)/(end-old_west)
    west=d.lerp(a,side);east=c.lerp(b,side);v=west.lerp(east,u)
    return Vector((v.x,v.y,zupper+(p.z-70.12300872802734)))
oldpoly=polys['old_core'];old_center=sum(oldpoly,Vector((0.,0.)))/len(oldpoly)
oldlimits=[[min(p[i] for p in oldpoly),max(p[i] for p in oldpoly)] for i in (0,1)]
def old_tower(p):
    bb=before['LAC R30B08 | apoio oposto | corpo estrutural afunilado']['bounds'];q=p.copy()
    for i in (0,1):q[i]=oldlimits[i][0]+(p[i]-bb[i][0])/(bb[i][1]-bb[i][0])*(oldlimits[i][1]-oldlimits[i][0])
    return q
def upper_station(p):
    q=p.copy();q.z=zupper+(p.z-70.12300872802734)*4./(75.325-70.12300872802734);return q
def upper_building(p):
    q=p.copy();q.z=zupper+4.+(p.z-75.2)*10./12.;return q
def lower_lobby(p):
    # Móveis não são escalados. Somente pilares/verga da fachada documentada.
    t=(p.y+5.1)/10.2;front=Vector(cfg['polygons']['lower_floor']['points_local'][-1]).lerp(Vector(cfg['polygons']['lower_floor']['points_local'][0]),t)
    interior=front.lerp(center,.55);u=(p.x+76.01355)/8.8;v=front.lerp(interior,u)
    return Vector((v.x,v.y,p.z))
mappers={'BRIDGE':bridge,'NEW_TOWER':new_tower,'NEW_GALLERY':gallery,'OLD_TOWER':old_tower,'UPPER_STATION':upper_station,'UPPER_BUILDING':upper_building,'LOWER_LOBBY':lower_lobby}

staged={};superseded=[];notes=[]
floor_name='LAC R30B | Passarela | piso paginado visual';roof_name='CALIBRADO | passarela cobertura 28.71 x 6.00m'
new_outer=polys['new_core'];new_inner=inset(new_outer,.18)
old_outer=polys['old_core'];old_inner=inset(old_outer,.18)
corewall_names=['CASCA | parede lateral','CASCA | parede lateral.001','CASCA | fachada poço','CASCA | fachada poço.002']
for n,domain in domains.items():
    o=scene.objects[n];source=src_by_collider.get(n,n);bb=before[n]['bounds']
    if source in (floor_name,roof_name):
        z0,z1=bb[2];staged[n]=slab(o,polys['bridge'],zupper-.03,zupper) if source==floor_name else slab(o,polys['bridge'],zupper+3.75,zupper+4.)
    elif source=='TORRE | cornija galeria':staged[n]=slab(o,polys['new_gallery'],zupper-.25,zupper,[new_outer])
    elif source=='TORRE | teto galeria':staged[n]=slab(o,polys['new_gallery'],zupper+3.75,zupper+4.,[new_outer])
    elif source=='SUPERIOR | piso saguão':staged[n]=slab(o,polys['upper_floor'],zupper-.33,zupper,[old_outer])
    elif source=='SUPERIOR | cobertura saguão':staged[n]=slab(o,polys['upper_floor'],zupper+3.75,zupper+4.)
    elif source=='INFERIOR | piso do saguão':staged[n]=slab(o,polys['lower_floor'],zlower-.25,zlower,[new_outer])
    elif source=='INFERIOR | cobertura do saguão':staged[n]=slab(o,polys['lower_floor'],zlower+5.51,zlower+5.76,[new_outer])
    elif source in corewall_names:
        index=corewall_names.index(source)
        staged[n]=strips(o,new_outer,new_inner,zlower+5.76,zupper-2.8,lambda i:i%4==index)
    elif source=='TORRE | corpo tecnico superior':staged[n]=strips(o,new_outer,new_inner,zupper+4.,zupper+14.)
    elif source=='TORRE | capeamento tecnico':staged[n]=slab(o,new_outer,zupper+13.8,zupper+14.)
    elif source=='LAC R30B08 | apoio oposto | corpo estrutural afunilado':staged[n]=strips(o,old_outer,old_inner,zlower,zupper-.33)
    elif source in ('LAC R30B08 | apoio oposto | capitel sob passarela','LAC R30B08 | apoio oposto | ressalto transversal'):
        staged[n]=strips(o,old_outer,old_inner,*bb[2])
    elif source.startswith('INFERIOR | parede lateral'):
        # Dois limites físicos contínuos da prancha inferior, incluindo túnel.
        p=polys['lower_floor'];inner=inset(p,.18);north=source.endswith('.001')
        # Fachada externa (última aresta) é aberta; recortes do túnel permanecem.
        staged[n]=strips(o,p,inner,zlower,zlower+5.51,lambda i:(i<7 if north else 7<=i<len(p)-1))
    else:
        mesh=o.data.copy();trans=inv@wm(o);back=wm(o).inverted()@M
        for v in mesh.vertices:v.co=back@mappers[domain](trans@v.co)
        mesh.update();bm=bmesh.new();bm.from_mesh(mesh)
        bad=[f for f in bm.faces if f.calc_area()<1e-9]
        if bad:bmesh.ops.delete(bm,geom=bad,context='FACES_ONLY')
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();staged[n]=mesh

# A galeria escalada por bounding box não representa os retornos da planta.
# Preservar os detalhes antigos como referência e reconstruir somente seu limite.
for n,d in domains.items():
    if d=='NEW_GALLERY' and src_by_collider.get(n,n) not in ('TORRE | cornija galeria','TORRE | teto galeria'):
        superseded.append(n)
# Pilares/verga genéricos da fachada inferior ficam como referência, até layout.
superseded.extend(n for n in domains if n.startswith(('INFERIOR | pilar','INFERIOR | verga')))

collection=bpy.data.collections.get('HERO | Lacerda | estrutura documental B88')
assert collection is None
collection=bpy.data.collections.new('HERO | Lacerda | estrutura documental B88')
added=[]
def add_object(name,geometry_fn,materials):
    empty=bpy.data.meshes.new(name);o=bpy.data.objects.new(name,empty);o.matrix_world=M.copy()
    for m in materials:empty.materials.append(m)
    o.data=geometry_fn(o);added.append(o);return o
ivory=scene.objects['CASCA | parede lateral'].data.materials[0]
glass=scene.objects['GALERIA | vidro lateral'].data.materials[0]
new_head_inner=inset(polys['new_gallery'],.10)
# Sem contagem de janelas/baias fictícia: painel contínuo temporário da envoltória.
add_object('B88 | galeria nova | peitoril estrutural',lambda o:strips(o,polys['new_gallery'],new_head_inner,zupper,zupper+.70,lambda i:i!=3),[ivory])
add_object('B88 | galeria nova | limite envidraçado',lambda o:strips(o,polys['new_gallery'],new_head_inner,zupper+.70,zupper+3.75,lambda i:i!=3),[glass])
add_object('B88 | galeria nova | verga estrutural',lambda o:strips(o,polys['new_gallery'],new_head_inner,zupper+3.75,zupper+4.,lambda i:i!=3),[ivory])
# Alas sob o edifício superior: limites de piso/corte -9,74, diferentes do poço.
bx=sorted(cfg['polygons']['upper_floor']['points_local'][i][0] for i in (1,2))
buildcfg=json.loads((root/'docs/reports/blender/lacerda-layout-b86/layout_source.json').read_text())
x0,x1=buildcfg['upper_building_x'];y0,y1=buildcfg['upper_building_y'];basement=clean([Vector((x0,y0)),Vector((x1,y0)),Vector((x1,y1)),Vector((x0,y1))])
add_object('B88 | cidade alta | alas estruturais sob edifício',lambda o:strips(o,basement,inset(basement,.24),zupper-9.74,zupper-.33),[ivory])

# Conferir todos os buffers antes de alterar a sessão.
for n,mesh in staged.items():
    assert len(mesh.vertices)>0,n
    bm=bmesh.new();bm.from_mesh(mesh);assert not any(f.calc_area()<1e-9 for f in bm.faces),n;bm.free()
for n,mesh in staged.items():
    o=scene.objects[n];o.data=mesh;o['boas_generated_revision']='R30B.88';o['boas_provenance_ids']=json.dumps(['derived:lacerda-massing-b88'])
    o['accuracy']='PROJECT_REFERENCE_DERIVED';o['replacement_required']=True;o['boas_production_ready']=False;o['reference_status']='partial';o['boas_architectural_domain']=domains[n]
    o['boas_pending_gate']='ABSOLUTE_SSOT_PLACEMENT_AND_INSTALLED_ELEVATORS'
    if n in src_by_collider:
        o['boas_collision_validation']='INVALIDATED_BY_ARCHITECTURAL_LAYOUT_B88';o['boas_physical_enabled']=False
for n in set(archived+superseded):
    o=scene.objects[n];o.hide_set(True);o.hide_render=True;o['boas_active_authoring']=False;o['boas_role']='SUPERSEDED_REFERENCE' if n in superseded else 'HISTORICAL_INSTALLATION_REFERENCE'
    o['boas_pending_gate']='FROZEN_INSTALLATION_OR_FINISH_LAYOUT_NOT_IN_STRUCTURE_PREVIEW'
scene.collection.children.link(collection)
for o in added:
    collection.objects.link(o);o['boas_location_id']='elevador-lacerda';o['boas_generated_revision']='R30B.88';o['boas_provenance_ids']=json.dumps(['derived:lacerda-massing-b88']);o['accuracy']='PROJECT_REFERENCE_DERIVED';o['replacement_required']=True;o['boas_production_ready']=False
    o['boas_role']='ARCHITECTURAL_MODEL_CANDIDATE';o['reference_status']='partial'
assert all((scene.objects[n].data.as_pointer() if scene.objects[n].data else None,[list(r) for r in scene.objects[n].matrix_basis])==state for n,state in protected.items())
assert sig(terrain)==terrain_before and all(sig(bpy.data.objects[n])==v for n,v in proxy_before.items())
assert hashlib.sha256(ssot_path.read_bytes()).hexdigest()==cfg['ssot_sha256']
changes=[{'object':n,'domain':domains[n],'before':before[n],'after':{'signature':sig(scene.objects[n]),'bounds':bounds(scene.objects[n])},'visible':scene.objects[n].visible_get()} for n in domains]
report={'revision':'R30B.88','file':dest.relative_to(root).as_posix(),'parent_file':base.relative_to(root).as_posix(),'parent_sha256':base_hash,'pid':os.getpid(),'scene':scene.name,'changes':changes,'added':[{'object':o.name,'signature':sig(o),'bounds':bounds(o)} for o in added],'historical_objects_preserved_as_reference':sorted(set(archived)),'superseded_finish_objects':sorted(set(superseded)),
 'source_controls':'docs/reports/blender/lacerda-massing-b88/architectural-controls.json','bindings_updated':bindings,'ssot_sha256':cfg['ssot_sha256'],'terrain_preserved':True,'proxy_b82_preserved':True,'production_ready':False,'reopened':False,
 'LACERDA_VERTICAL':'BLOCKED_EXTERNAL_EVIDENCE','movement_enabled':False,'historic_witnesses':27,'absolute_xy_status':'CANDIDATE_ARCHITECTURAL_RELATIVE_FIT','absolute_z_status':'LOWER_DATUM_UNRESOLVED_PRESERVED','installation_dimensions':None,'wall_thickness_status':'LEGACY_APPROXIMATION_NOT_SURVEYED','floor_holes':'DOCUMENT_CORE_ENVELOPES_NOT_INSTALLED_SHAFT_CERTIFICATION'}
scene['lacerda_revision']='R30B.88 | estrutura relativa SUCOP; implantação/instalação não certificadas';scene['boas_historic_movement_enabled']=False
profile_path=root/'world/areas/mvp-centro-lacerda/corridor-slice.json';profile=json.loads(profile_path.read_text(encoding='utf8'))
invalidated=[]
for binding in profile.get('collision_bindings',[]):
    if binding['object'] in domains:
        invalidated.append({'object':binding['object'],'previous_enabled':binding.get('enabled')})
        binding['enabled']=False;binding['validation_status']='INVALIDATED_BY_ARCHITECTURAL_LAYOUT_B88'
report['collision_contract_invalidated']=invalidated
profile.setdefault('revision_history',[]).append({'revision':'R30B.88','scope':'arquitetura relativa SUCOP; colisão histórica afetada requer nova validação','movement_enabled':False,'evidence':'docs/reports/blender/lacerda-massing-b88/application.json'})
profile_path.write_text(json.dumps(profile,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
report_path=out/'application.json';report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
with dest.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
report['sha256']=digest;report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
entry={'file':report['file'],'revision':'R30B.88','parent_file':report['parent_file'],'sha256':digest,'scene':scene.name,'status':'architectural_structure_candidate','production_ready':False,'evidence':report_path.relative_to(root).as_posix(),'notes':'Contornos, orientação e proporções relativos às pranchas 12/17/23; implantação/datum inferior/instalação continuam pendentes.'}
catalog['revisions'].append(entry)
for key in ('authoring_source','validation_source'):catalog[key]=entry.copy()
catalog['authoring_scene']=scene.name;catalog_path.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'revision':'B88','changed':len(changes),'added':len(added),'file':report['file'],'sha256':digest,'movement_enabled':False,'ssot_preserved':True},ensure_ascii=False))
