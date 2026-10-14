"""B91: corrigir regressões de montagem/malha, sem certificar a instalação.

Buffers são verificados antes da atribuição; não há fill-holes, offset mundial
ou redução da cápsula. Espessuras herdadas continuam explicitamente candidatas.
"""
import bpy,bmesh,json,math,hashlib,runpy,os,shutil
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.geometry import delaunay_2d_cdt
root=Path(__file__).resolve().parents[2];out=root/'docs/reports/blender/lacerda-mesh-b91'
base=Path(bpy.data.filepath);scene=bpy.context.scene
assert base.name=='salvador_lacerda_r30b90_cotas_exteriores_consolidadas.blend'
assert scene.name=='SALVADOR | ESBOCO OFICIAL' and os.getpid()==16912
assert not bpy.app.is_job_running('RENDER')
dest=root/'blender/salvador_lacerda_r30b91_integridade_malha_e_apoios.blend';assert not dest.exists()
assert shutil.disk_usage(root).free>base.stat().st_size*1.5
catpath=root/'world/areas/mvp-centro-lacerda/blender-revisions.json';cat=json.loads(catpath.read_text())
with base.open('rb') as f:base_hash=hashlib.file_digest(f,'sha256').hexdigest()
assert base_hash==cat['authoring_source']['sha256']
audit=json.loads((out/'before.json').read_text());rows={r['object']:r for r in audit['rows']}
cfg=json.loads((root/'docs/reports/blender/lacerda-massing-b88/architectural-controls.json').read_text())
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));wm=h['world_matrix'];sig=h['signature']
M=Matrix(json.loads((root/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text())['measurement_frame']);inv=M.inverted()
ssot=hashlib.sha256((root/'world/geographic-reference.json').read_bytes()).hexdigest();assert ssot==cfg['ssot_sha256']
proxy={o.name:sig(o) for o in bpy.data.collections['GAMEPLAY_PROXY | Lacerda B82'].objects}
terrain_name='MVP | terreno corrigido | colisão estática';terrain=sig(scene.objects[terrain_name])
clean_names=[r['object'] for r in audit['rows'] if r['visible'] and r['duplicate_face_groups'] and 'COLLISION' not in r['object'] and r['object']!='TORRE | corpo tecnico superior']
clean_names+=['FACHADA SUPERIOR | corpo elevado','SUPERIOR | lateral corpo elevado','SUPERIOR | lateral corpo elevado.001']
core_names=['CASCA | parede lateral','CASCA | parede lateral.001','CASCA | fachada poço','CASCA | fachada poço.002']
retire=core_names[1:]+['TORRE | corpo tecnico superior','EDIFICIO | cobertura']
slab_name='CALIBRADO | passarela piso 28.71 x 6.00m';primary=core_names[0]
changed=set(clean_names+[primary,slab_name]+retire)
protected={o.name:(o.data.as_pointer() if o.data else None,[list(r) for r in o.matrix_basis],o.hide_get(),o.hide_render,o.parent.name if o.parent else None) for o in scene.objects if o.name not in changed}
for n in changed:assert sig(scene.objects[n])==rows[n]['signature'],n
def area(p):return sum(a.x*b.y-a.y*b.x for a,b in zip(p,p[1:]+p[:1]))/2
def poly(key):
 p=[Vector(v) for v in cfg['polygons'][key]['points_local']]
 if area(p)<0:p.reverse()
 return p
core=poly('new_core');head=poly('new_gallery');bridge=poly('bridge')
def inset(p,t):
 q=[]
 for i,b in enumerate(p):
  u=(b-p[i-1]).normalized();v=(p[(i+1)%len(p)]-b).normalized();n=Vector((-u.y,u.x));nv=Vector((-v.y,v.x));a=b+n*t;d=b+nv*t;cross=u.x*v.y-u.y*v.x
  q.append(b+(n+nv)*(.5*t) if abs(cross)<1e-6 else a+u*(((d-a).x*v.y-(d-a).y*v.x)/cross))
 return q
inner=inset(core,.18)
def inside(p,loop):
 hit=False
 for a,b in zip(loop,loop[1:]+loop[:1]):
  if (a.y>p.y)!=(b.y>p.y) and p.x<(b.x-a.x)*(p.y-a.y)/(b.y-a.y)+a.x:hit=not hit
 return hit
def stats(mesh):
 bm=bmesh.new();bm.from_mesh(mesh);bm.verts.ensure_lookup_table();seen=set();components=0
 for v in bm.verts:
  if v.index in seen:continue
  components+=1;todo=[v]
  while todo:
   a=todo.pop()
   if a.index in seen:continue
   seen.add(a.index);todo.extend(e.other_vert(a) for e in a.link_edges)
 d={'vertices':len(bm.verts),'faces':len(bm.faces),'components':components,'degenerate_faces':sum(f.calc_area()<1e-9 for f in bm.faces),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'wire_edges':sum(e.is_wire for e in bm.edges),'signed_volume':bm.calc_volume(signed=True)}
 bm.free();return d
def closed(mesh,label):
 d=stats(mesh)
 assert d['degenerate_faces']==d['nonmanifold_edges']==d['wire_edges']==0,(label,d)
 assert d['components']==1 and d['signed_volume']>0,(label,d)
 return d
def geometry(o,verts,faces,label):
 mesh=bpy.data.meshes.new(label);back=wm(o).inverted()@M
 mesh.from_pydata([tuple(back@Vector(v)) for v in verts],[],faces)
 for mat in o.data.materials:mesh.materials.append(mat)
 bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();mesh.update()
 closed(mesh,label);return mesh
def ring(o,outer,inside_loop,z0,z1):
 n=len(outer);assert n==len(inside_loop);v=[];f=[]
 for z in (z0,z1):v.extend((p.x,p.y,z) for p in outer+inside_loop)
 for i in range(n):
  j=(i+1)%n;f.extend([(i,j,j+2*n,i+2*n),(n+j,n+i,3*n+i,3*n+j),(j,i,n+i,n+j),(2*n+i,2*n+j,3*n+j,3*n+i)])
 return geometry(o,v,f,'B91 | núcleo estrutural contínuo')
buffers={};changes=[];cleanup=[]
for n in clean_names:
 o=scene.objects[n];bm=bmesh.new();bm.from_mesh(o.data);bm.faces.ensure_lookup_table()
 before=stats(o.data);groups={}
 for face in bm.faces:
  key=tuple(sorted(tuple(round(float(x),6) for x in v.co) for v in face.verts));groups.setdefault(key,[]).append(face)
 remove=[]
 for fs in groups.values():
  if len(fs)>1:
   assert len(fs)==2 and fs[0].normal.dot(fs[1].normal)<-.999,(n,'face coincidente ambígua')
   remove.extend(fs)
 if remove:bmesh.ops.delete(bm,geom=remove,context='FACES_ONLY')
 bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-5)
 wires=[e for e in bm.edges if e.is_wire]
 if wires:bmesh.ops.delete(bm,geom=wires,context='EDGES')
 loose=[v for v in bm.verts if not v.link_edges]
 if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));mesh=o.data.copy();bm.to_mesh(mesh);bm.free();after=closed(mesh,n)
 relative=abs(after['signed_volume']-before['signed_volume'])/max(1.,abs(before['signed_volume']))
 assert relative<1e-5,(n,'volume alterado por limpeza',relative)
 tr=inv@wm(o);p=[tr@v.co for v in mesh.vertices];bb=[[min(v[i] for v in p),max(v[i] for v in p)] for i in range(3)]
 assert max(abs(bb[i][j]-rows[n]['bounds'][i][j]) for i in range(3) for j in range(2))<1e-4,n
 buffers[n]=mesh;cleanup.append({'object':n,'removed_internal_faces':len(remove),'before':before,'after':after,'relative_volume_change':relative,'max_merge_distance_m':1e-5,'reason':'Faces internas opostas e vértices coincidentes; sem preencher abertura arquitetônica'})
# As quatro cascas e o corpo técnico usam o mesmo contorno. A lacuna vertical
# foi produzida pela seleção/montagem B88, não é porta ou abertura documental.
upper=cfg['levels']['upper_walkable'];core_bottom=rows[primary]['bounds'][2][0];consolo_bottom=rows[primary]['bounds'][2][1]
core_top=rows['TORRE | capeamento tecnico']['bounds'][2][0]
assert abs(core_top-(upper+13.8))<1e-4 and abs(rows['TORRE | corpo tecnico superior']['bounds'][2][0]-(upper+4))<1e-4
buffers[primary]=ring(scene.objects[primary],core,inner,core_bottom,core_top)
# Laje legada ficou fora da seleção B88. Seu contorno agora é exatamente o
# mesmo CAD da ponte; contatos Z derivam das superfícies já existentes.
finish_bottom=rows['LAC R30B | Passarela | piso paginado visual']['bounds'][2][0]
intradorso_top=rows['LAC R30B08 | passarela | intradorso continuo']['bounds'][2][1]
n=len(bridge);vs=[(p.x,p.y,z) for z in (intradorso_top,finish_bottom) for p in bridge]
fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
buffers[slab_name]=geometry(scene.objects[slab_name],vs,fs,'B91 | laje da ponte vinculada ao contorno documental')
# As duas coberturas são volumes integralmente sobrepostos, mesma função,
# mesmo topo +14 e sem bindings. Preservar o detalhe legado fora da camada ativa.
outer=rows['SUPERIOR | cobertura corpo elevado']['bounds'];roof=rows['EDIFICIO | cobertura']['bounds']
assert all(outer[i][0]<=roof[i][0]+1e-5 and outer[i][1]>=roof[i][1]-1e-5 for i in range(3))
assert abs(outer[2][1]-roof[2][1])<1e-6
# Consolo: presença/formato alargado evidenciados pelo corte 23 e fotografias.
# XY superior vem da planta 17. Base usa envoltória convexa do núcleo; espessura
# e início Z herdados são aproximação declarada, não cota/as-built.
pts=sorted(set((float(p.x),float(p.y)) for p in core))
def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
lo=[];hi=[]
for p in pts:
 while len(lo)>1 and cross(lo[-2],lo[-1],p)<=1e-8:lo.pop()
 lo.append(p)
for p in reversed(pts):
 while len(hi)>1 and cross(hi[-2],hi[-1],p)<=1e-8:hi.pop()
 hi.append(p)
hull=[Vector(p) for p in lo[:-1]+hi[:-1]];center=Vector(cfg['new_tower_basis']['center_local'])
angles=sorted(set(math.atan2(p.y-center.y,p.x-center.x) for p in hull+head))
def ray(loop,angle):
 d=Vector((math.cos(angle),math.sin(angle)));hits=[]
 for a,b in zip(loop,loop[1:]+loop[:1]):
  v=b-a;w=a-center;den=d.x*v.y-d.y*v.x
  if abs(den)<1e-9:continue
  t=(w.x*v.y-w.y*v.x)/den;u=(w.x*d.y-w.y*d.x)/den
  if t>0 and -1e-6<=u<=1+1e-6:hits.append(t)
 assert hits and max(hits)-min(hits)<1e-4,('Contorno do consolo não é radialmente inequívoco',hits)
 return center+d*(sum(hits)/len(hits))
outer0=[ray(hull,a) for a in angles];outer1=[ray(head,a) for a in angles]
assert all((b-center).length>(a-center).length for a,b in zip(outer0,outer1))
z0=consolo_bottom;z1=rows['TORRE | cornija galeria']['bounds'][2][0];assert z1>z0
N=len(outer0);K=len(inner);layer=N+K;verts=[(p.x,p.y,z) for z,p in [(z0,p) for p in outer0+inner]+[(z1,p) for p in outer1+inner]];faces=[]
def cap(outer_loop,offset,reverse):
 points=outer_loop+inner;ids=list(range(len(points)));loops=[ids[:N],ids[N:]];edges=[]
 for loop in loops:edges.extend((v,loop[(i+1)%len(loop)]) for i,v in enumerate(loop))
 result=delaunay_2d_cdt(points,edges,[loops[0]],1,1e-6)
 assert all(len(orig)==1 for orig in result[3]),'CDT gerou vértice novo na borda'
 total=0
 for f in result[2]:
  pp=[result[0][i] for i in f];mid=sum(pp,Vector((0.,0.)))/len(pp)
  if inside(mid,inner):continue
  indices=[result[3][i][0]+offset for i in f]
  if area(pp)<0:indices.reverse()
  total+=abs(area(pp));faces.append(tuple(reversed(indices)) if reverse else tuple(indices))
 assert abs(total-(abs(area(outer_loop))-abs(area(inner))))<.002,'Área do consolo inconsistente'
cap(outer0,0,True);cap(outer1,layer,False)
for i in range(N):
 j=(i+1)%N;faces.extend([(i,j,j+layer),(i,j+layer,i+layer)])
for i in range(K):
 j=(i+1)%K;faces.append((N+j,N+i,layer+N+i,layer+N+j))
new_name='B91 | galeria nova | consolo estrutural documentado'
assert new_name not in scene.objects
# Apenas buffer, objeto criado/linkado após validação de todos os demais.
template=scene.objects[primary];support_mesh=geometry(template,verts,faces,'B91 | consolo com vazio do núcleo preservado')
# A geometria de geometry(template) está no espaço do template; copiar seu
# transform ao novo objeto garante identidade física, sem reparentar hero.
for n,mesh in buffers.items():closed(mesh,n)
before={n:{'signature':sig(scene.objects[n]),'bounds':rows[n]['bounds'],'visible':scene.objects[n].visible_get(),'role':scene.objects[n].get('boas_role')} for n in changed}
for n,mesh in buffers.items():
 o=scene.objects[n];o.data=mesh;o['boas_generated_revision']='R30B.91';o['boas_provenance_ids']=json.dumps(['derived:lacerda-structure-mesh-b91']);o['replacement_required']=True;o['boas_production_ready']=False
 if n==primary:o['boas_mesh_consolidated_sources']=json.dumps(core_names+['TORRE | corpo tecnico superior']);o['boas_structure_continuity']='DOCUMENT_SECTION_23_CORE_CONTINUITY';o['boas_wall_thickness_status']='LEGACY_APPROXIMATION_0.18_NOT_SURVEYED'
 if n==slab_name:
  o['dimensoes_status']='Contorno CAD SUCOP17; espessura de montagem candidata, sem cota própria';o['boas_role']='ARCHITECTURAL_MODEL_CANDIDATE';o['accuracy']='PROJECT_XY_INHERITED_Z_APPROXIMATE';o['boas_pending_gate']='ABSOLUTE_SSOT_PLACEMENT_AND_STRUCTURE_THICKNESS';o['boas_location_id']='elevador-lacerda';o['boas_architectural_domain']='BRIDGE';o['boas_floor_binding']='LAC R30B | Passarela | piso paginado visual'
for n in retire:
 o=scene.objects[n];o.hide_set(True);o.hide_render=True;o['boas_active_authoring']=False;o['boas_role']='SUPERSEDED_REFERENCE';o['boas_superseded_by']=primary if n!='EDIFICIO | cobertura' else 'SUPERIOR | cobertura corpo elevado';o['boas_superseded_reason']='Fonte preservada; um único volume arquitetônico ativo para esta função na B91'
support=bpy.data.objects.new(new_name,support_mesh);support.matrix_basis=template.matrix_basis.copy();support.matrix_parent_inverse=template.matrix_parent_inverse.copy();support.parent=template.parent
bpy.data.collections['HERO | Lacerda | estrutura documental B88'].objects.link(support)
for k,v in {'boas_location_id':'elevador-lacerda','boas_role':'ARCHITECTURAL_MODEL_CANDIDATE','classification':'ADAPT_LOCAL','reference_status':'partial','accuracy':'APPROXIMATE_SECTION_PROFILE_WITH_DOCUMENT_XY','replacement_required':True,'boas_production_ready':False,'boas_generated_revision':'R30B.91','boas_provenance_ids':json.dumps(['derived:lacerda-structure-mesh-b91']),'boas_pending_gate':'CONSOLO_UNCOTED_PROFILE_AND_ABSOLUTE_PLACEMENT','boas_source_object':'LAC R30B07 | galeria | consolo inclinado','boas_support_height_status':'LEGACY_INTERVAL_2.55M_NOT_PRINTED_DIMENSION'}.items():support[k]=v
for name,state in protected.items():
 o=scene.objects[name];assert (o.data.as_pointer() if o.data else None,[list(r) for r in o.matrix_basis],o.hide_get(),o.hide_render,o.parent.name if o.parent else None)==state,name
assert sig(scene.objects[terrain_name])==terrain and all(sig(bpy.data.objects[n])==s for n,s in proxy.items())
assert hashlib.sha256((root/'world/geographic-reference.json').read_bytes()).hexdigest()==ssot
for n in sorted(changed):changes.append({'object':n,'before':before[n],'after':{'signature':sig(scene.objects[n]),'visible':scene.objects[n].visible_get(),'mesh':stats(scene.objects[n].data)},'operation':'PRESERVE_AS_REFERENCE' if n in retire else 'CLEAN_MESH' if n in clean_names else 'RECONSTRUCT_DOCUMENT_CONTOUR'})
profilepath=root/'world/areas/mvp-centro-lacerda/corridor-slice.json';profile=json.loads(profilepath.read_text());invalidated=[]
for binding in profile.get('collision_bindings',[]):
 if binding.get('source') in changed or binding.get('source_object') in changed or binding.get('object') in changed:
  binding['enabled']=False;binding['validation_status']='INVALIDATED_BY_STRUCTURE_MESH_B91';invalidated.append(binding['object'])
for o in scene.objects:
 if o.name in changed or o.name==new_name or o.name in proxy:continue
 if any(o.get(k) in changed for k in ('boas_derived_from_object','boas_source_object','boas_collision_source_object','source_object')):
  o['boas_collision_validation']='INVALIDATED_BY_STRUCTURE_MESH_B91';o['boas_physical_enabled']=False
scene['lacerda_revision']='R30B.91 | integridade das malhas/encontros estruturais; implantação/instalação pendentes';scene['boas_historic_movement_enabled']=False
report={'revision':'R30B.91','file':dest.relative_to(root).as_posix(),'parent_file':base.relative_to(root).as_posix(),'parent_sha256':base_hash,'pid':os.getpid(),'scene':scene.name,'changes':changes,'cleanup':cleanup,'added':[{'object':new_name,'signature':sig(support),'mesh':stats(support.data)}],
 'structural_evidence':{'bridge':'SUCOP17 / polygons.bridge; laje legada omitida pela seleção B88','core':'SUCOP17 / polygons.new_core + corte23 mostra continuidade através da galeria','consolo':'Corte23 e fotografias mostram apoio alargado; perfil/espessura/altura sem cota própria continuam candidatos','roof':'Coberturas contidas integralmente uma na outra, mesma função e plano +14; fonte legada preservada'},
 'contact_levels':{'bridge_finish_bottom':finish_bottom,'bridge_structure_bottom':intradorso_top,'core_bottom':core_bottom,'core_top_cap_contact':core_top,'support_bottom_inherited':z0,'support_top_gallery_contact':z1,'support_height_approximate':z1-z0},
 'invalidated_bindings':invalidated,'ssot_sha256':ssot,'terrain_preserved':True,'proxy_b82_preserved':True,'protected_object_count':len(protected),'LACERDA_VERTICAL':'BLOCKED_EXTERNAL_EVIDENCE','historic_witnesses':27,'movement_enabled':False,'production_ready':False,'absolute_ssot_fit':'NOT_ACCEPTED','reopened':False}
path=out/'application.json';path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
profile.setdefault('revision_history',[]).append({'revision':'R30B.91','scope':'Integridade de malha e encontros de arquitetura; nenhuma aprovação de instalação/controller','movement_enabled':False,'evidence':path.relative_to(root).as_posix()})
profilepath.write_text(json.dumps(profile,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
with dest.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
report['sha256']=digest;path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
entry={'file':report['file'],'revision':'R30B.91','parent_file':report['parent_file'],'sha256':digest,'scene':scene.name,'status':'architectural_structure_candidate','production_ready':False,'evidence':path.relative_to(root).as_posix(),'notes':'Malhas limpas e encontros estruturais reconciliados; consolo aproximado declarado, implantação/as-built pendentes.'}
cat['revisions'].append(entry)
for key in ('authoring_source','validation_source'):cat[key]=entry.copy()
catpath.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'revision':'B91','file':report['file'],'sha256':digest,'changed':len(changes),'added':1,'cleanup':len(cleanup),'internal_faces_removed':sum(r['removed_internal_faces'] for r in cleanup),'production_ready':False},ensure_ascii=False))
