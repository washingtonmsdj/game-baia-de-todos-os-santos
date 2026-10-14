"""B64: recorte costeiro pelo limite da água, cais apoiado e volumes fechados nas bordas."""
import bpy,bmesh,json,math,hashlib,runpy,numpy as np
from pathlib import Path
from collections import defaultdict,Counter
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];scene=bpy.context.scene
cp=root/'world/areas/mvp-centro-lacerda/blender-revisions.json';cat=json.loads(cp.read_text(encoding='utf8'));src=cat['validation_source'];assert src['revision']=='R30B.63'
out=root/'blender/salvador_lacerda_r30b64_costa_volumes_corrigidos.blend';assert not out.exists()
sig=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'))['signature']
water=scene.objects['BAÍA DE TODOS-OS-SANTOS | superfície e recorte costeiro'];core=scene.objects['MVP | terreno corrigido | colisão estática'];hq=scene.objects['B62 | GAMEPLAY TERRAIN HQ | pavimento e costura limpa'];fill=scene.objects['B63 | VISUAL | piso contínuo até o cais'];quay=scene.objects['CAIS | contenção costeira alinhada à linha de costa']
protected={o.name:sig(o) for o in [water,hq]+[o for o in scene.objects if o.name.startswith(('B56 | COLLISION | PIER |','B57 | PIER VISUAL |'))]}
col=bpy.data.collections.get('39.7 GAMEPLAY | B64 COSTA CORRIGIDA')
if col is None:col=bpy.data.collections.new('39.7 GAMEPLAY | B64 COSTA CORRIGIDA');scene.collection.children.link(col)
water.data.calc_loop_triangles();wv=[water.matrix_world@v.co for v in water.data.vertices];wt=BVHTree.FromPolygons(wv,[list(t.vertices) for t in water.data.loop_triangles],all_triangles=True)
def wet(x,y):
 h=wt.ray_cast(Vector((float(x),float(y),100)),Vector((0,0,-1)),200)[0]
 return h is not None and abs(h.z-.35)<.001
counts=Counter()
for f in water.data.polygons:
 points=[wv[i] for i in f.vertices]
 if points and all(abs(p.z-.35)<.001 for p in points):
  for a,b in zip(f.vertices,(*f.vertices[1:],f.vertices[0])):counts[tuple(sorted((a,b)))]+=1
xmin=min(v.x for v in wv);ymin=min(v.y for v in wv);ymax=max(v.y for v in wv);shore=[]
for (a,b),n in counts.items():
 if n!=1:continue
 p,q=wv[a],wv[b]
 if (abs(p.x-xmin)<.1 and abs(q.x-xmin)<.1) or (abs(p.y-ymin)<.1 and abs(q.y-ymin)<.1) or (abs(p.y-ymax)<.1 and abs(q.y-ymax)<.1):continue
 shore.append((p.copy(),q.copy()))
assert shore

def cut_coast(o,material_ids=None):
 bm=bmesh.new();bm.from_mesh(o.data);bm.faces.ensure_lookup_table();bm.verts.ensure_lookup_table();mw=o.matrix_world;inv=mw.inverted();cells=defaultdict(set);locations={}
 def center(f):return mw@f.calc_center_median()
 def register(f):
  if not f.is_valid or (material_ids is not None and f.material_index not in material_ids):return
  c=center(f);key=(math.floor(c.x/4),math.floor(c.y/4));old=locations.get(f)
  if old is not None:cells[old].discard(f)
  cells[key].add(f);locations[f]=key
 for f in bm.faces:register(f)
 initial_faces=len(bm.faces);road_faces_before=sum(f.material_index in (2,5) for f in bm.faces) if o==core else None
 original_road_verts={v for f in bm.faces if f.material_index in (2,5) for v in f.verts} if o==core else set();road_coords={v:tuple(v.co) for v in original_road_verts}
 splits=0
 for p,q in shore:
  if (q-p).length<1e-6:continue
  lo=np.minimum(np.array(p[:2]),np.array(q[:2]))-2.;hi=np.maximum(np.array(p[:2]),np.array(q[:2]))+2.;near=set()
  for i in range(math.floor(lo[0]/4),math.floor(hi[0]/4)+1):
   for j in range(math.floor(lo[1]/4),math.floor(hi[1]/4)+1):near.update(cells.get((i,j),()))
  faces=[];d=q-p;length2=d.x*d.x+d.y*d.y
  for f in near:
   if not f.is_valid:continue
   c=center(f);t=max(0,min(1,((c.x-p.x)*d.x+(c.y-p.y)*d.y)/length2));dist=math.hypot(c.x-p.x-t*d.x,c.y-p.y-t*d.y)
   if dist<2. and not any(v in original_road_verts for v in f.verts):faces.append(f)
  if not faces:continue
  geom=set(faces)
  for f in faces:geom.update(f.edges);geom.update(f.verts)
  normal=mw.to_3x3().transposed()@Vector((-d.y,d.x,0));normal.normalize()
  ret=bmesh.ops.bisect_plane(bm,geom=list(geom),dist=1e-6,plane_co=inv@p,plane_no=normal,clear_inner=False,clear_outer=False)
  update=set(faces)
  for element in ret.get('geom_cut',[]):
   if isinstance(element,(bmesh.types.BMVert,bmesh.types.BMEdge)):update.update(element.link_faces)
   elif isinstance(element,bmesh.types.BMFace):update.add(element)
  for f in update:register(f)
  splits+=len(ret.get('geom_cut',[]))
 remove=[]
 for f in bm.faces:
  if material_ids is not None and f.material_index not in material_ids:continue
  c=center(f)
  if wet(c.x,c.y):remove.append(f)
 removed=len(remove);bmesh.ops.delete(bm,geom=remove,context='FACES')
 zero=[f for f in bm.faces if f.calc_area()<1e-10 and (material_ids is None or f.material_index in material_ids)]
 if zero:bmesh.ops.delete(bm,geom=zero,context='FACES')
 assert not any(not v.is_valid or tuple(v.co)!=co for v,co in road_coords.items()),'Pavimento protegido alterado'
 if o==core:assert sum(f.material_index in (2,5) for f in bm.faces)==road_faces_before,'Faces de via alteradas'
 me=o.data.copy();bm.to_mesh(me);bm.free();me.update();o.data=me;o['boas_revision']='R30B.64';o['boas_coastline_control']='limite superior da água preservada B63';o['boas_classification']='ERROR'
 return {'object':o.name,'faces_before':initial_faces,'removed_seaward_faces':removed,'removed_degenerate':len(zero),'cuts':splits,'faces_after':len(me.polygons),'road_faces_preserved':road_faces_before}
core_row=cut_coast(core,{0,1});fill_row=cut_coast(fill)
fc=scene.objects[fill['boas_collision_partner']];fc.data=fill.data.copy();fc['boas_revision']='R30B.64'
# Volumes contínuos dos meios-fios, sem faces de fundo ausentes ou normais invertidas.
curb=scene.objects['B63 | VISUAL | meios-fios das vias existentes'];old=curb.data;rows=[];profiles=Counter()
for st in range(0,len(old.vertices),10):
 p=[[tuple(old.vertices[st+i].co) for i in range(5)],[tuple(old.vertices[st+5+i].co) for i in range(5)]];keys=[tuple(tuple(round(x,6) for x in v) for v in profile) for profile in p];rows.append((p,keys));profiles.update(keys)
rows=[row for row in rows if all(profiles[k]<=2 for k in row[1])];counts=Counter(k for row in rows for k in row[1]);vv=[];ff=[];lookup={};profile_ids={}
def index(v):
 k=tuple(round(x,6) for x in v)
 if k not in lookup:lookup[k]=len(vv);vv.append(v)
 return lookup[k]
for p,keys in rows:
 ids=[[index(v) for v in pp] for pp in p]
 for key,ii in zip(keys,ids):profile_ids[key]=ii
 for j in range(5):ff.append((ids[0][j],ids[0][(j+1)%5],ids[1][(j+1)%5],ids[1][j]))
for key,n in counts.items():
 if n==1:ff.append(profile_ids[key])
me=bpy.data.meshes.new('B64 | meios-fios fechados');me.from_pydata(vv,[],ff);me.materials.append(old.materials[0]);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));nonmanifold=sum(not e.is_manifold for e in bm.edges);bm.to_mesh(me);bm.free();me.update();me.calc_loop_triangles();assert not any(t.area<1e-9 for t in me.loop_triangles);assert nonmanifold==0,('Meio-fio não manifold',nonmanifold)
curb.data=me;curb['boas_revision']='R30B.64';cc=scene.objects[curb['boas_collision_partner']];cc.data=me.copy();cc['boas_revision']='R30B.64'
# Canteiros ganham base/laterais reais; fragmento sem cobertura suficiente é recusado.
source_report=json.loads((root/'docs/reports/blender/urban_edges_r30b63.json').read_text(encoding='utf8'));garden_rows=[]
for row in source_report['gardens']:
 ob=scene.objects[row['object']];me=ob.data;me.calc_loop_triangles();toparea=sum(t.area for t in me.loop_triangles);coverage=toparea/row['source_area_blender_units2']
 if coverage<.20:
  ob.hide_viewport=True;ob.hide_render=True;ob['boas_status']='SOURCE_LIMITATION_partial_coverage';gc=scene.objects[ob['boas_collision_partner']];gc['boas_status']='excluded_partial_coverage';gc['boas_runtime_role']='reference_only';garden_rows.append({'osm_id':row['osm_id'],'coverage_ratio':coverage,'retained':False});continue
 verts=[tuple(v.co) for v in me.vertices];n=len(verts);verts.extend([(x,y,z-.10) for x,y,z in verts.copy()]);faces=[list(f.vertices) for f in me.polygons];ec=Counter(tuple(sorted((a,b))) for f in faces for a,b in zip(f,f[1:]+f[:1]));top=faces.copy();faces.extend([[i+n for i in reversed(f)] for f in top]);faces.extend([(a,b,b+n,a+n) for (a,b),count in ec.items() if count==1])
 new=bpy.data.meshes.new(f'B64 | canteiro sólido {row["osm_id"]}');new.from_pydata(verts,[],faces);new.materials.append(me.materials[0]);new.update();bm=bmesh.new();bm.from_mesh(new);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));nm=sum(not e.is_manifold for e in bm.edges);bm.to_mesh(new);bm.free();new.update();new.calc_loop_triangles();assert not any(t.area<1e-9 for t in new.loop_triangles)
 ob.data=new;ob['boas_revision']='R30B.64';gc=scene.objects[ob['boas_collision_partner']];gc.data=new.copy();gc['boas_revision']='R30B.64';garden_rows.append({'osm_id':row['osm_id'],'coverage_ratio':coverage,'retained':True,'nonmanifold_edges':nm})
# Face visível no limite costeiro registrado; espessura e fundação reais pendentes.
def tree(o):
 o.data.calc_loop_triangles();return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(t.vertices) for t in o.data.loop_triangles],all_triangles=True)
trees=[tree(o) for o in (core,hq,fill)]
def floor(x,y):
 values=[]
 for tr in trees:
  h=tr.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),400)[0]
  if h is not None:values.append(float(h.z))
 return max(values) if values else None
v=[];f=[];wall_segments=0;wall_missing=0;wall_length=0.
for p,q in shore:
 length=math.hypot(q.x-p.x,q.y-p.y);parts=max(1,math.ceil(length/1.));d=q-p;normal=Vector((-d.y,d.x,0));normal.normalize();mid=(p+q)/2
 if wet(mid.x+normal.x*.1,mid.y+normal.y*.1):normal=-normal
 for k in range(parts):
  a=p+d*k/parts;b=p+d*(k+1)/parts;ha=floor(a.x+normal.x*.03,a.y+normal.y*.03);hb=floor(b.x+normal.x*.03,b.y+normal.y*.03)
  if ha is None or hb is None:wall_missing+=1;continue
  st=len(v)
  v.extend([(a.x,a.y,.35),(b.x,b.y,.35),(b.x,b.y,hb),(a.x,a.y,ha)])
  f.append((st,st+1,st+2,st+3));wall_segments+=1;wall_length+=length/parts
assert f
qm=bpy.data.meshes.new('B64 | cais apoiado no piso');qm.from_pydata(v,[],f);qm.materials.append(quay.data.materials[0]);qm.update();bm=bmesh.new();bm.from_mesh(qm);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(qm);bm.free();qm.update();qm.calc_loop_triangles();assert not any(t.area<1e-9 for t in qm.loop_triangles)
# Mantém identidade/parenting do objeto legado para preservar dependências.
inv=quay.matrix_world.inverted();qm.transform(inv);quay.data=qm;quay['boas_revision']='R30B.64';quay['boas_classification']='ERROR';quay['boas_source_controls']='costa da água B63 preservada + apoio atual do piso';quay['boas_real_wall_thickness_status']='pending';quay['boas_real_foundation_status']='pending';quay['boas_geographic_fidelity_status']='candidate_pending_photo_comparison'
wall=bpy.data.objects.new('B64 | COLLISION | cais e borda marítima',qm.copy());col.objects.link(wall);wall.matrix_world=quay.matrix_world.copy();wall.hide_viewport=True;wall.hide_render=True;wall['boas_runtime_role']='coastal_wall_collision';wall['boas_source_surface']=quay.name;wall['boas_gameplay_approved']=False;quay['boas_collision_partner']=wall.name
changed=[n for n,b in protected.items() if sig(scene.objects[n])!=b];assert not changed,changed
scene['boas_validation_revision']='R30B.64';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
report={'schema':'boas/coastal-volumes-b64-v1','source_before':src,'source_after':{'file':out.relative_to(root).as_posix(),'revision':'R30B.64','sha256':hashlib.file_digest(out.open('rb'),'sha256').hexdigest()},'core':core_row,'fill':fill_row,'curbs':{'closed_segments':len(rows),'nonmanifold_edges':nonmanifold,'original_segments':len(old.vertices)//10},'gardens':garden_rows,'quay':{'supported_segments':wall_segments,'unsupported_outside_land_segments':wall_missing,'modeled_length_blender_units':wall_length,'real_thickness_verified':False,'same_object_identity':True},'protected_changes':changed,'approved':False,'runtime_exported':False,'pending':['Reabertura, vista de rua e apoios nas interfaces','Navegação/píeres com nós sem apoio','Expansão sul sem dados urbanos completos','Percursos completos e tráfego na engine']}
rp=root/'docs/reports/blender/coastal_volumes_r30b64.json';rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8');entry={**report['source_after'],'status':'validation_candidate','parent_file':src['file'],'evidence':rp.relative_to(root).as_posix(),'notes':'Recorta apenas solo/pedonal sobre água; pavimento protegido; cais apoiado e volumes fechados; sem promoção runtime.'}
for r in cat['revisions']:
 if r['file']==src['file']:r['status']='superseded_validation'
cat['revisions'].append(entry);cat['validation_source']=entry.copy();cp.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(report,ensure_ascii=False))
