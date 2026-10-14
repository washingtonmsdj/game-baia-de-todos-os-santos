"""B94: fechamentos e encontros dos corredores, sem redimensionar o mundo."""
import bpy,bmesh,json,hashlib,os,runpy,shutil
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.geometry import delaunay_2d_cdt
root=Path(__file__).resolve().parents[2];out=root/'docs/reports/blender/lacerda-closure-b94';scene=bpy.context.scene;base=Path(bpy.data.filepath)
assert base.name=='salvador_lacerda_r30b93_estrutura_inferior_documental.blend' and scene.name=='SALVADOR | ESBOCO OFICIAL'
assert os.getpid()==16912 and not bpy.app.is_job_running('RENDER')
dest=root/'blender/salvador_lacerda_r30b94_fechamentos_passarela_tunel.blend';assert not dest.exists()
assert shutil.disk_usage(root).free>base.stat().st_size*1.5
catpath=root/'world/areas/mvp-centro-lacerda/blender-revisions.json';cat=json.loads(catpath.read_text())
with base.open('rb') as f:parenthash=hashlib.file_digest(f,'sha256').hexdigest()
assert parenthash==cat['authoring_source']['sha256']
cfg=json.loads((root/'docs/reports/blender/lacerda-massing-b88/architectural-controls.json').read_text());prior=json.loads((out/'before.json').read_text());rows={v['object']:v for v in prior['rows']}
ssot=hashlib.sha256((root/'world/geographic-reference.json').read_bytes()).hexdigest();assert ssot==cfg['ssot_sha256']
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));wm=h['world_matrix'];sig=h['signature'];M=Matrix(json.loads((root/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text())['measurement_frame']);inv=M.inverted()
poly=lambda k:[Vector(v) for v in cfg['polygons'][k]['points_local']]
upper=poly('upper_floor');bridge=poly('bridge');lower=poly('lower_floor');oldcore=poly('old_core');newcore=poly('new_core')
zupper=cfg['levels']['upper_walkable'];zlower=zupper-59.01;rooflow=zupper-53.17
changed=['SUPERIOR | piso saguão','SUPERIOR | cobertura saguão','INFERIOR | piso do saguão','INFERIOR | cobertura do saguão','INFERIOR | parede lateral','INFERIOR | parede lateral.001']
for n in changed:assert sig(scene.objects[n])==rows[n]['signature'],n
protected={o.name:(o.data.as_pointer() if o.data else None,[list(r) for r in o.matrix_basis],o.hide_get(),o.hide_render,o.parent.name if o.parent else None) for o in scene.objects if o.name not in changed}
proxy={o.name:sig(o) for o in bpy.data.collections['GAMEPLAY_PROXY | Lacerda B82'].objects};terrain=sig(scene.objects['MVP | terreno corrigido | colisão estática'])

def area(p):return sum(a.x*b.y-a.y*b.x for a,b in zip(p,p[1:]+p[:1]))/2
def inside(p,loop):
    hit=False
    for a,b in zip(loop,loop[1:]+loop[:1]):
        if (a.y>p.y)!=(b.y>p.y) and p.x<(b.x-a.x)*(p.y-a.y)/(b.y-a.y)+a.x:hit=not hit
    return hit
def positive(p):return list(reversed(p)) if area(p)<0 else p
def stats(mesh):
    bm=bmesh.new();bm.from_mesh(mesh);d={'vertices':len(bm.verts),'faces':len(bm.faces),'degenerate_faces':sum(f.calc_area()<1e-9 for f in bm.faces),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'inconsistent_winding_edges':sum(e.is_manifold and not e.is_contiguous for e in bm.edges),'signed_volume':bm.calc_volume(signed=True)};bm.free();return d
def mesh(o,verts,faces,label):
    data=bpy.data.meshes.new(label);back=wm(o).inverted()@M;data.from_pydata([tuple(back@Vector(v)) for v in verts],[],faces)
    for mat in o.data.materials:data.materials.append(mat)
    bm=bmesh.new();bm.from_mesh(data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free();data.update()
    q=stats(data);assert q['degenerate_faces']==q['nonmanifold_edges']==q['inconsistent_winding_edges']==0 and q['signed_volume']>0,(label,q)
    return data
def planar_union_slab(o,loops,holes,z0,z1,label):
    points=[];edges=[]
    for loop in loops+holes:
        start=len(points);points.extend(loop);ids=list(range(start,len(points)));edges.extend((v,ids[(i+1)%len(ids)]) for i,v in enumerate(ids))
    result=delaunay_2d_cdt(points,edges,[],0,1e-6);flat=list(result[0]);triangles=[]
    for f in result[2]:
        p=[flat[i] for i in f];mid=sum(p,Vector((0.,0.)))/len(p)
        if not any(inside(mid,l) for l in loops) or any(inside(mid,hole) for hole in holes):continue
        assert abs(area(p))>1e-9,(label,'Triângulo sem área')
        triangles.append(tuple(reversed(f)) if area(p)<0 else tuple(f))
    count={};directed={};faces=[];N=len(flat)
    for tri in triangles:
        faces.extend([tuple(reversed(tri)),tuple(i+N for i in tri)])
        for a,b in zip(tri,tri[1:]+tri[:1]):
            key=tuple(sorted((a,b)));count[key]=count.get(key,0)+1;directed[key]=(a,b)
    for key,c in count.items():
        if c==1:
            a,b=directed[key];faces.append((a,b,b+N,a+N))
    used=sorted({i for f in faces for i in f});verts=[(p.x,p.y,z) for z in (z0,z1) for p in flat];lookup={old:i for i,old in enumerate(used)}
    return mesh(o,[verts[i] for i in used],[tuple(lookup[i] for i in f) for f in faces],label)
def wall_segments(o,segments,z0,z1,label,thickness=.18):
    loops=[];offsets=[]
    for a,b,inward in segments:
        d=b-a;assert d.length>.01;normal=Vector((-d.y,d.x)).normalized()
        if normal.dot(inward)<0:normal=-normal
        offset=normal*thickness;loops.append(positive([a,b,b+offset,a+offset]));offsets.append(offset)
    # União planar antes da extrusão: não soldar caixas que só compartilham
    # uma aresta vertical. Os encontros usam o mesmo limite externo CAD e
    # fecham o canto interno com a espessura herdada, sem faces internas.
    for i,(a,b,_) in enumerate(segments):
        for j,(c,d,_) in enumerate(segments):
            if i!=j and (b-c).length<1e-5:
                corner=[b,b+offsets[i],b+offsets[j]]
                if abs(area(corner))>1e-9:loops.append(positive(corner))
    return planar_union_slab(o,loops,[],z0,z1,label)

# Prancha17: os dois retornos flanqueiam a abertura verdadeira da ponte.
# Usar os endpoints CAD também nas lajes, evitando seam de contornos divergentes.
upper_closed=upper+[bridge[2],bridge[1]]
buffers={}
buffers[changed[0]]=planar_union_slab(scene.objects[changed[0]],[upper_closed],[oldcore],zupper-.33,zupper,'B94 | piso superior com portal CAD')
buffers[changed[1]]=planar_union_slab(scene.objects[changed[1]],[upper_closed],[],zupper+3.75,zupper+4.,'B94 | cobertura superior com portal CAD')

# Face permanente da torre antiga já modelada: reentrância oeste da planta17.
# Encontro local entre contornos existentes, sem mexer no envelope do poço.
scale=cfg['pdf_units_per_m'];anchor=cfg['drawing_to_architecture']['origin_pdf']
local=lambda x,y:Vector((5.5+(x-anchor[0])/scale,-(y-anchor[1])/scale))
station_north=local(2127.96,1036.84);station_south=local(2127.96,1139.20)
assert any((p-station_north).length<1e-5 for p in oldcore) and any((p-station_south).length<1e-5 for p in oldcore)
connector=positive([lower[6],lower[7],station_south,station_north])
assert .1<abs(area(connector))<5.,'Extensão excede o encontro local'
assert not inside(sum(connector,Vector((0.,0.)))/4,oldcore),'Conector invade o núcleo'
for n,z0,z1 in [(changed[2],zlower-.25,zlower),(changed[3],rooflow-.25,rooflow)]:
    buffers[n]=planar_union_slab(scene.objects[n],[lower,connector],[newcore],z0,z1,'B94 | '+n+' | encontro contínuo da torre')
# Manter os limites do túnel/contorno da planta12. O tampão transversal antigo
# termina antes da torre: substituí-lo pelos retornos até a face existente.
# A face da torre permanece intacta; movimento/entrada no poço não aprovados.
north=[(lower[i],lower[i+1],Vector((0.,-1.))) for i in range(6)]+[(lower[6],station_north,Vector((0.,-1.)))]
south=[(lower[i],lower[i+1],Vector((0.,1.))) for i in range(7,18)]+[(station_south,lower[7],Vector((0.,1.)))]
# Inward real do polígono em cada trecho, também nos recortes da edificação.
for segments in (north,south):
    for i,(a,b,_) in enumerate(segments):
        d=(b-a).normalized();normal=Vector((-d.y,d.x));mid=(a+b)/2
        inward=normal if any(inside(mid+normal*.02,p) for p in (lower,connector)) else -normal
        segments[i]=(a,b,inward)
buffers[changed[4]]=wall_segments(scene.objects[changed[4]],south,zlower,rooflow-.25,'B94 | limite sul contínuo do túnel')
buffers[changed[5]]=wall_segments(scene.objects[changed[5]],north,zlower,rooflow-.25,'B94 | limite norte contínuo do túnel')

added=[];collection=bpy.data.collections['HERO | Lacerda | estrutura documental B88'];ivory=scene.objects['CASCA | parede lateral'].data.materials[0];glass=scene.objects['B88 | galeria nova | limite envidraçado'].data.materials[0]
for side,a,b in [('norte',upper[0],bridge[1]),('sul',bridge[2],upper[-1])]:
    for band,z0,z1,mat in [('peitoril',zupper,zupper+.7,ivory),('vidro',zupper+.7,zupper+3.75,glass),('verga',zupper+3.75,zupper+4.,ivory)]:
        name=f'B94 | saguão passarela | retorno {side} | {band}';assert name not in scene.objects
        template=bpy.data.objects.new(name,bpy.data.meshes.new(name));template.matrix_world=M.copy();template.data.materials.append(mat)
        data=wall_segments(template,[(a,b,Vector((1.,0.)))],z0,z1,name);template.data=data
        added.append(template)

before={n:{'signature':sig(scene.objects[n]),'bounds':rows[n]['bounds']} for n in changed}
journal={'file':dest.relative_to(root).as_posix(),'parent_file':base.relative_to(root).as_posix(),'parent_sha256':parenthash,'scene':scene.name,'pid':os.getpid(),'ssot_sha256':ssot,'planned_changes':changed,'planned_added':[o.name for o in added],'before':before,'controls':{'upper_perimeter_with_bridge_portal':[list(p) for p in upper_closed],'upper_returns':[[list(upper[0]),list(bridge[1])],[list(bridge[2]),list(upper[-1])]],'tunnel_connector':[list(p) for p in connector],'station_face':[list(station_north),list(station_south)],'connector_area_m2':abs(area(connector)),'source_refs':['SUCOP17: torre antiga/limite da ponte','SUCOP12: circulação túnel / limites do saguão']},'terrain_signature':terrain,'proxy_signatures':proxy}
(out/'mutation-journal.json').write_text(json.dumps(journal,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
for n,data in buffers.items():scene.objects[n].data=data
for o in added:collection.objects.link(o)
for o in [scene.objects[n] for n in changed]+added:
    for k,v in {'boas_location_id':'elevador-lacerda','boas_role':'ARCHITECTURAL_MODEL_CANDIDATE','boas_generated_revision':'R30B.94','boas_provenance_ids':json.dumps(['derived:lacerda-corridor-closure-b94']),'accuracy':'DOCUMENT_CONTOURS_LOCAL_JUNCTION_INHERITED_THICKNESS','replacement_required':True,'boas_production_ready':False,'boas_pending_gate':'ABSOLUTE_PLACEMENT_AND_INSTALLED_ELEVATORS'}.items():o[k]=v
for n,state in protected.items():
    o=scene.objects[n];assert (o.data.as_pointer() if o.data else None,[list(r) for r in o.matrix_basis],o.hide_get(),o.hide_render,o.parent.name if o.parent else None)==state,n
assert sig(scene.objects['MVP | terreno corrigido | colisão estática'])==terrain and all(sig(bpy.data.objects[n])==s for n,s in proxy.items())
assert hashlib.sha256((root/'world/geographic-reference.json').read_bytes()).hexdigest()==ssot
changes=[{'object':n,'before':before[n],'after':{'signature':sig(scene.objects[n]),'mesh':stats(scene.objects[n].data)}} for n in changed]
new=[{'object':o.name,'signature':sig(o),'mesh':stats(o.data)} for o in added]
profilepath=root/'world/areas/mvp-centro-lacerda/corridor-slice.json';profile=json.loads(profilepath.read_text());invalidated=[]
for binding in profile.get('collision_bindings',[]):
    if binding.get('source') in changed or binding.get('source_object') in changed:
        binding['enabled']=False;binding['validation_status']='INVALIDATED_BY_CORRIDOR_CLOSURE_B94';invalidated.append(binding['object'])
scene['lacerda_revision']='R30B.94 | fechamentos/encontros passarela e túnel';scene['boas_historic_movement_enabled']=False
runpy.run_path(str(root/'automation/blender/present_lacerda_map_b91.py'))
report={**journal,'revision':'R30B.94','changes':changes,'added':new,'invalidated_bindings':invalidated,'protected_object_count':len(protected),'LACERDA_VERTICAL':'BLOCKED_EXTERNAL_EVIDENCE','movement_enabled':False,'historic_witnesses':27,'terrain_changed':False,'proxy_b82_preserved':True,'production_ready':False,'reopened':False}
path=out/'application.json';path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
profile.setdefault('revision_history',[]).append({'revision':'R30B.94','scope':'Encontros e fechamentos dos corredores; poço/terreno intactos, controller não aprovado','movement_enabled':False,'evidence':path.relative_to(root).as_posix()});profilepath.write_text(json.dumps(profile,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
with dest.open('rb') as f:report['sha256']=hashlib.file_digest(f,'sha256').hexdigest()
path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
entry={'file':report['file'],'revision':'R30B.94','parent_file':report['parent_file'],'sha256':report['sha256'],'scene':scene.name,'status':'architectural_structure_candidate','production_ready':False,'evidence':path.relative_to(root).as_posix(),'notes':'Retornos envidraçados e encontro contínuo do túnel; não aprova instalação/implantação/controller.'};cat['revisions'].append(entry)
for k in ('authoring_source','validation_source'):cat[k]=entry.copy()
catpath.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'revision':'B94','changes':len(changes),'added':len(new),'connector_area_m2':abs(area(connector)),'file':report['file'],'sha256':report['sha256']},ensure_ascii=False))
