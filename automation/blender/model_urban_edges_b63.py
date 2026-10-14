"""B63: fecha piso até o cais e modela bordas pedonais/canteiros com controles existentes."""
import bpy,json,math,hashlib,runpy,numpy as np
from pathlib import Path
from collections import defaultdict
from mathutils import Vector,Euler,geometry
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];scene=bpy.context.scene
catpath=root/'world/areas/mvp-centro-lacerda/blender-revisions.json';cat=json.loads(catpath.read_text(encoding='utf8'));src=cat['validation_source'];assert src['revision']=='R30B.62'
out=root/'blender/salvador_lacerda_r30b63_orla_bordas_canteiros.blend';assert not out.exists()
assert Path(bpy.data.filepath).resolve()==(root/src['file']).resolve()
signature=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'))['signature']
core=scene.objects['MVP | terreno corrigido | colisão estática'];hq=scene.objects['B62 | GAMEPLAY TERRAIN HQ | pavimento e costura limpa'];quay=scene.objects['CAIS | contenção costeira alinhada à linha de costa']
protected={o.name:signature(o) for o in [core,hq,quay,scene.objects['BAÍA DE TODOS-OS-SANTOS | superfície e recorte costeiro']]+[o for o in scene.objects if o.name.startswith(('B56 | COLLISION | PIER |','B57 | PIER VISUAL |'))]}
for stale in list(bpy.data.collections):
 if stale.name.startswith(('39.6 GAMEPLAY | B63 ORLA E BORDAS','39.6 NAVIGATION_HINTS | B63 ORLA')) and not stale.objects and not stale.children:bpy.data.collections.remove(stale)
col=bpy.data.collections.new('39.6 GAMEPLAY | B63 ORLA E BORDAS');scene.collection.children.link(col)
navcol=bpy.data.collections.new('39.6 NAVIGATION_HINTS | B63 ORLA');scene.collection.children.link(navcol);navcol.hide_render=True;navcol.hide_viewport=True

def tree_of(o):
 me=o.data;me.calc_loop_triangles();tri=list(me.loop_triangles)
 return BVHTree.FromPolygons([o.matrix_world@v.co for v in me.vertices],[list(t.vertices) for t in tri],all_triangles=True),[me.polygons[t.polygon_index].material_index for t in tri]
ct,cm=tree_of(core);ht,hm=tree_of(hq)
def hit(tree,x,y):return tree.ray_cast(Vector((float(x),float(y),200)),Vector((0,0,-1)),400)
def support(x,y):
 for tree,mis in ((ct,cm),(ht,hm)):
  p,n,i,d=hit(tree,x,y)
  if p is not None:return float(p.z),mis[i]
 return None,None

def inside(p,poly):
 x,y=p;yes=False
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:yes=not yes
 return yes

def closest(p,line):
 best=(1e30,None)
 for a,b in zip(line,line[1:]):
  dx,dy=b[0]-a[0],b[1]-a[1];d2=dx*dx+dy*dy
  t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/max(d2,1e-15)))
  q=[a[k]+t*(b[k]-a[k]) for k in range(len(a))];d=math.hypot(p[0]-q[0],p[1]-q[1])
  if d<best[0]:best=d,q
 return best

def make_mesh(name,verts,faces,materials,mis=None,role='sidewalk_walkable'):
 me=bpy.data.meshes.new(name+' | malha');me.from_pydata(verts,[],faces);me.update();me.calc_loop_triangles()
 assert all(math.isfinite(c) for v in me.vertices for c in v.co)
 assert all(t.area>1e-9 for t in me.loop_triangles),(name,'triângulo degenerado')
 o=bpy.data.objects.new(name,me);col.objects.link(o)
 for m in materials:me.materials.append(m)
 if mis is not None:
  for p,m in zip(me.polygons,mis):p.material_index=m
 o['boas_revision']='R30B.63';o['boas_runtime_role']=role;o['boas_gameplay_approved']=False;o['boas_real_dimensions_verified']=False
 return o

def collision(o,role):
 c=bpy.data.objects.new(o.name.replace('VISUAL','COLLISION',1),o.data.copy());col.objects.link(c);c.hide_render=True;c.hide_viewport=True
 c['boas_runtime_role']=role;c['boas_source_surface']=o.name;c['boas_geometry_identical_to_visual']=True;c['boas_gameplay_approved']=False;o['boas_collision_partner']=c.name
 return c
walkmat=bpy.data.materials['VIAS | passeio mineral claro'];curbmat=bpy.data.materials.get('B63 | concreto do meio-fio')
if curbmat is None:
 curbmat=bpy.data.materials.new('B63 | concreto do meio-fio');curbmat.diffuse_color=(.48,.46,.41,1);curbmat.use_nodes=True
 bs=next((n for n in curbmat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None) or curbmat.node_tree.nodes.new('ShaderNodeBsdfPrincipled');bs.inputs['Base Color'].default_value=curbmat.diffuse_color;bs.inputs['Roughness'].default_value=.86
for mat in (curbmat,):
 nodes=mat.node_tree.nodes;bs=next((n for n in nodes if n.type=='BSDF_PRINCIPLED'),None) or nodes.new('ShaderNodeBsdfPrincipled');output=next((n for n in nodes if n.type=='OUTPUT_MATERIAL'),None) or nodes.new('ShaderNodeOutputMaterial');mat.node_tree.links.new(bs.outputs['BSDF'],output.inputs['Surface']);bs.inputs['Base Color'].default_value=mat.diffuse_color;bs.inputs['Roughness'].default_value=.86
# Contorno do cais construído preservado, complementado pela borda física do núcleo.
shore=[list(quay.matrix_world@v.co) for v in quay.data.vertices][1::2]
xcut=min((core.matrix_world@Vector(p)).x for p in core.bound_box);y0=shore[0][1];y1=shore[-1][1]
poly=[p[:2] for p in shore]+[[xcut,y1],[xcut,y0]]
xy=[];constraints=[];lookup={}
def point(p):
 key=(round(float(p[0]),6),round(float(p[1]),6))
 if key not in lookup:lookup[key]=len(xy);xy.append(Vector(key))
 return lookup[key]
def edge(a,b,spacing=1.5):
 length=math.dist(a[:2],b[:2]);n=max(1,math.ceil(length/spacing));prev=point(a)
 for i in range(1,n+1):
  q=[a[k]+(b[k]-a[k])*i/n for k in range(2)];nxt=point(q)
  if prev!=nxt:constraints.append((prev,nxt))
  prev=nxt
for a,b in zip(poly,poly[1:]+poly[:1]):edge(a,b)
# Todas as arestas reais de borda HQ no domínio evitam sobreposição/rachaduras.
a=np.load(root/'artifacts/waterfront/urban_hq_b62.npz');ec=np.bincount(a['loop_edges'],minlength=len(a['edges']))
for e in a['edges'][ec==1]:
 p,q=a['vertices'][e]
 if max(p[1],q[1])>=y0-.1 and min(p[1],q[1])<=y1+.1 and max(p[0],q[0])<=xcut+.01:edge(p,q,.75)
for y in np.arange(y0,y1+.001,2.):
 for x in np.arange(min(p[0] for p in shore),xcut,2.):
  if inside((x,y),poly) and support(x,y)[0] is None:point((x,y))
cdt=geometry.delaunay_2d_cdt(xy,constraints,[],0,1e-6,False);verts2=cdt[0];faces=[];used=set()
for f in cdt[2]:
 p=[sum(verts2[i][k] for i in f)/len(f) for k in range(2)]
 if p[0]>=xcut-1e-6 or not inside(p,poly) or support(*p)[0] is not None:continue
 faces.append(f);used.update(f)
assert faces,'Nenhuma lacuna inequívoca encontrada'
remap={i:j for j,i in enumerate(sorted(used))};verts=[];boundary_errors=[]
for i in sorted(used):
 x,y=verts2[i];existing,_=support(x,y);d,q=closest((x,y),shore)
 if d<1e-4:z=q[2]
 elif existing is not None:z=existing;boundary_errors.append(0.)
 else:
  ce=hit(ct,xcut+.002,y)[0]
  if ce is None:raise RuntimeError(('Sem controle do núcleo',x,y))
  w=max(1e-5,xcut-q[0]);u=max(0,min(1,(x-q[0])/w));blend=u*u*(3-2*u);z=q[2]*(1-blend)+ce.z*blend
 verts.append((x,y,z))
faces=[[remap[i] for i in f] for f in faces]
fill=make_mesh('B63 | VISUAL | piso contínuo até o cais',verts,faces,[walkmat]);fill['boas_classification']='ERROR';fill['boas_correction_reason']='Piso ausente entre limites existentes; interpolação ancorada no cais e no terreno preservados.';fill['boas_source_controls']='cais construído R30A8; limite núcleo; limite HQ B62';fill['boas_location_id']='cais-praca-cairu';fill['boas_surface_design_status']='ADAPT_LOCAL_CANDIDATE'
fc=collision(fill,'terrain_collision');ft,fm=tree_of(fill)
# Meio-fio exclusivamente na borda já compartilhada por pista e superfície pedonal.
a=np.load(root/'artifacts/waterfront/urban_core_b62.npz');vv=a['vertices'];mi=a['materials'];starts=a['starts'];counts=a['counts'];li=a['loop_edges'];ed=a['edges'];idx=a['indices'];lm=np.repeat(mi,counts)
rc=np.bincount(li[np.isin(lm,[2,5])],minlength=len(ed));pc=np.bincount(li[np.isin(lm,[1,3,4,7])],minlength=len(ed));candidates=np.where((rc>0)&(pc>0))[0]
roadcenters={}
for fi in np.where(np.isin(mi,[2,5]))[0]:
 st,n=int(starts[fi]),int(counts[fi]);cent=vv[idx[st:st+n]].mean(axis=0)
 for ei in li[st:st+n]:
  if pc[ei]>0:roadcenters[int(ei)]=cent
normals=defaultdict(lambda:np.zeros(2));valid=[];rejected=defaultdict(int)
for ei in candidates:
 ia,ib=ed[ei];p,q=vv[ia],vv[ib];d=q[:2]-p[:2];length=np.linalg.norm(d)
 if length<.05 or length>5:rejected['length']+=1;continue
 if abs(q[2]-p[2])/length>.30:rejected['grade']+=1;continue
 n=np.array([-d[1],d[0]])/length
 if np.dot(n,roadcenters[int(ei)][:2]-(p[:2]+q[:2])/2)>0:n=-n
 normals[int(ia)]+=n;normals[int(ib)]+=n;valid.append(int(ei))
cv=[];cf=[];curb_length=0;accepted=0
for ei in valid:
 ia,ib=ed[ei];ends=[];bad=False
 for vi in (ia,ib):
  p=vv[vi];n=normals[int(vi)]
  if np.linalg.norm(n)<.1:bad=True;break
  n=n/np.linalg.norm(n);outer=p[:2]+n*.18;h,m=support(*outer)
  if h is None or m not in [1,3,4,7] or abs(h-p[2])>.20:bad=True;break
  ends.append([(p[0],p[1],p[2]),(p[0]+n[0]*.02,p[1]+n[1]*.02,p[2]+.10),(p[0]+n[0]*.04,p[1]+n[1]*.04,p[2]+.12),(outer[0],outer[1],h+.12),(outer[0],outer[1],h)])
 if bad:rejected['outside_pedestrian_surface']+=1;continue
 base=len(cv);cv.extend(ends[0]);cv.extend(ends[1]);
 for j in range(4):cf.append((base+j,base+j+1,base+6+j,base+5+j))
 curb_length+=float(np.linalg.norm(vv[ib]-vv[ia]));accepted+=1
curbs=make_mesh('B63 | VISUAL | meios-fios das vias existentes',cv,cf,[curbmat],role='environment_final');curbs['boas_classification']='ADAPT_LOCAL';curbs['boas_design_width_m']=.18;curbs['boas_design_height_m']=.12;curbs['boas_source_controls']='arestas pista/passeio na malha preservada; dimensões de desenho candidatas';collision(curbs,'curb_collision')
# Jardins/gramados somente com polígono fechado, dimensão limitada e apoio livre.
landscape=json.loads((root/'artifacts/waterfront/urban_landscape_source.json').read_text(encoding='utf8'));gardenmat=bpy.data.materials.get('B63 | solo de canteiro')
if gardenmat is None:
 gardenmat=bpy.data.materials.new('B63 | solo de canteiro');gardenmat.diffuse_color=(.075,.15,.042,1);gardenmat.use_nodes=True;bs=next((n for n in gardenmat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None) or gardenmat.node_tree.nodes.new('ShaderNodeBsdfPrincipled');bs.inputs['Base Color'].default_value=gardenmat.diffuse_color;bs.inputs['Roughness'].default_value=.95
nodes=gardenmat.node_tree.nodes;bs=next((n for n in nodes if n.type=='BSDF_PRINCIPLED'),None) or nodes.new('ShaderNodeBsdfPrincipled');output=next((n for n in nodes if n.type=='OUTPUT_MATERIAL'),None) or nodes.new('ShaderNodeOutputMaterial');gardenmat.node_tree.links.new(bs.outputs['BSDF'],output.inputs['Surface'])
beds=[]
for feat in landscape['features']:
 tags=feat['tags'];p=feat['blender_xy']
 if not feat['closed'] or feat['missing_nodes'] or not (tags.get('landuse')=='grass' or tags.get('leisure')=='garden'):continue
 if p[0]==p[-1]:p=p[:-1]
 area=abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(p,p[1:]+p[:1])))/2
 if area>5000:continue
 points=[Vector(q) for q in p];edges=[(i,(i+1)%len(p)) for i in range(len(p))]
 for y in np.arange(min(q[1] for q in p),max(q[1] for q in p),1.5):
  for x in np.arange(min(q[0] for q in p),max(q[0] for q in p),1.5):
   if inside((x,y),p):points.append(Vector((x,y)))
 gv,ge,gf,*_=geometry.delaunay_2d_cdt(points,edges,[list(range(len(p)))],1,1e-6,False);z=[]
 for v in gv:
  h,m=support(*v);z.append(h+.10 if h is not None and m in (0,9) else None)
 kept=[]
 for f in gf:
  mid=[sum(gv[i][k] for i in f)/len(f) for k in range(2)];h,m=support(*mid)
  if h is not None and m in (0,9) and all(z[i] is not None for i in f):kept.append(f)
 if not kept:continue
 used=sorted({i for f in kept for i in f});mapping={i:j for j,i in enumerate(used)}
 ob=make_mesh(f'B63 | VISUAL | canteiro OSM {feat["osm_id"]}',[(gv[i].x,gv[i].y,z[i]) for i in used],[[mapping[i] for i in f] for f in kept],[gardenmat],role='environment_final');ob['boas_osm_id']=str(feat['osm_id']);ob['boas_osm_type']='way';ob['boas_source_capture']=landscape['source_capture'];ob['boas_classification']='ADAPT_LOCAL';ob['boas_height_design_m']=.10;ob['boas_reference_status']='candidate';collision(ob,'garden_collision');beds.append({'osm_id':feat['osm_id'],'source_area_blender_units2':area,'faces':len(kept),'object':ob.name})
# Hints novos só nos apoios presentes; nenhum arco atravessa vazio.
ref=json.loads((root/'artifacts/structural-pipeline/mvp-centro-lacerda/structural_reference.json').read_text(encoding='utf8'));hints=[]
for feat in ref['features']:
 if feat['osm_id'] not in (1426173138,1426173325,1426173326,1426173327):continue
 points=[];missing=0
 for p in feat['blender_xy']:
  values=[]
  for tr in (ct,ht,ft):
   h=hit(tr,*p)[0]
   if h is not None:values.append(float(h.z))
  if values:points.append((*p,max(values)))
  else:missing+=1
 if not missing and len(points)>1:
  cu=bpy.data.curves.new(f'B63 | NAV | {feat["osm_id"]}','CURVE');cu.dimensions='3D';sp=cu.splines.new('POLY');sp.points.add(len(points)-1)
  for v,p in zip(sp.points,points):v.co=(*p,1)
  ob=bpy.data.objects.new(cu.name,cu);navcol.objects.link(ob);ob['boas_osm_id']=str(feat['osm_id']);ob['boas_runtime_role']='navigation_hint';ob['boas_status']='candidate_not_navmesh'
 hints.append({'osm_id':feat['osm_id'],'missing_source_nodes_support':missing,'implemented_hint':not missing and len(points)>1})
changed=[n for n,b in protected.items() if signature(scene.objects[n])!=b];assert not changed,changed
scene['boas_validation_revision']='R30B.63';scene['boas_b63_status']='Candidata: piso da orla e meios-fios; fontes e larguras preservadas; sem aprovação global.'
for o in list(bpy.context.selected_objects):o.select_set(False)
fill.select_set(True);bpy.context.view_layer.objects.active=fill
for win in bpy.context.window_manager.windows:
 for ar in win.screen.areas:
  if ar.type=='VIEW_3D':
   sp=ar.spaces.active;sp.overlay.show_extras=False;sp.shading.type='SOLID';sp.shading.color_type='MATERIAL';sp.region_3d.view_location=Vector((-205,85,20));sp.region_3d.view_distance=680;sp.region_3d.view_rotation=Euler((math.radians(35),0,math.radians(-12)),'XYZ').to_quaternion();sp.region_3d.view_perspective='ORTHO'
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
report={'schema':'boas/urban-edges-b63-v1','source_before':src,'source_after':{'file':out.relative_to(root).as_posix(),'revision':'R30B.63','sha256':hashlib.file_digest(out.open('rb'),'sha256').hexdigest()},'fill':{'vertices':len(verts),'faces':len(faces),'classification':'ERROR','source_controls':'cais/limites existentes; sem fit Z global'},'curbs':{'source_boundary_candidates':len(candidates),'accepted_segments':accepted,'modeled_length_blender_units':curb_length,'rejected':dict(rejected),'design_dimensions_m':{'height':.12,'width':.18},'real_dimensions_verified':False},'gardens':beds,'hints':hints,'protected_changes':changed,'road_width_changed':False,'beach_created':False,'approved':False,'runtime_exported':False,'pending':['Reabertura e inspeção visual','Continuidade pedonal e travessias completas','Física/tráfego e todos os percursos','Cobertura urbana da expansão ao sul; dados adicionais necessários']}
rp=root/'docs/reports/blender/urban_edges_r30b63.json';rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
entry={**report['source_after'],'status':'validation_candidate','parent_file':src['file'],'evidence':rp.relative_to(root).as_posix(),'notes':'Fecha lacuna junto ao cais; meios-fios no limite pista/passeio; canteiros candidatos OSM, sem mudar larguras/fontes ou runtime.'}
for row in cat['revisions']:
 if row['file']==src['file']:row['status']='superseded_validation'
cat['revisions'].append(entry);cat['validation_source']=entry.copy();catpath.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(report,ensure_ascii=False))
