"""B69: recortar o domínio terrestre por subtração de triângulos e CDT local; fechar frestas B68."""
import bpy,bmesh,json,hashlib,math,shutil,runpy
from types import SimpleNamespace
from pathlib import Path
from collections import Counter
from mathutils import Vector,geometry
from mathutils.bvhtree import BVHTree
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
cp=r/'world/areas/mvp-centro-lacerda/blender-revisions.json';cat=json.loads(cp.read_text(encoding='utf-8'));src=cat['validation_source']
assert src['revision']=='R30B.68' and Path(bpy.data.filepath).resolve()==(r/src['file']).resolve()
with (r/src['file']).open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==src['sha256']
out=r/'blender/salvador_lacerda_r30b69_encontros_sem_frestas.blend';assert not out.exists()
reserve=2*(r/src['file']).stat().st_size+150*1024**2
assert shutil.disk_usage(r).free>reserve
probe=json.loads((r/'docs/reports/blender/pier_shore_contacts_b68_probe.json').read_text(encoding='utf-8'))
region_path=r/'artifacts/waterfront/pier_land_region_b67.json'
region=json.loads(region_path.read_text(encoding='utf-8'));assert region['source']['sha256']=='e0fcda84e28adaf3161da7458195471511b00c2ef9e70fd42f6edc555188b412'
sig=runpy.run_path(str(r/'automation/blender/component_fingerprint.py'))['signature']
protected_names=['MVP | terreno corrigido | colisão estática','B62 | GAMEPLAY TERRAIN HQ | pavimento e costura limpa','B63 | VISUAL | piso contínuo até o cais','CAIS | contenção costeira alinhada à linha de costa','BAÍA DE TODOS-OS-SANTOS | superfície e recorte costeiro','BAÍA | volume de água no limite do recorte','R30A8 | FOAM | linha costeira','R30A8 | FOAM | halo costeiro']
protected_names += [o.name for o in s.objects if o.name.startswith(('B56 | COLLISION | PIER |','B57 | PIER VISUAL |','B67 |'))]
protected={n:sig(s.objects[n]) for n in protected_names}
ground=[];ground_edges=[];water_tri=[]
def key(p):return tuple(round(float(c),6) for c in p)
for name,triangles in region['meshes'].items():
 if name.startswith('BAÍA'):water_tri=triangles;continue
 ec=Counter();coords={}
 for tri in triangles:
  a,b,c=map(Vector,tri)
  if abs((b-a).cross(c-a).z)<1e-8:continue
  ground.append(tri)
  for p,q in ((a,b),(b,c),(c,a)):
   ka,kb=key(p),key(q);coords[ka]=p;coords[kb]=q;ec[tuple(sorted((ka,kb)))]+=1
 for (ka,kb),count in ec.items():
  if count==1:ground_edges.append((coords[ka],coords[kb]))
def tree(triangles):
 vv=[Vector(p) for tri in triangles for p in tri]
 return BVHTree.FromPolygons(vv,[(i,i+1,i+2) for i in range(0,len(vv),3)],all_triangles=True,epsilon=1e-7)
gt=tree(ground);wt=tree(water_tri)
def floor(p):return gt.ray_cast(Vector((p.x,p.y,150)),Vector((0,0,-1)),300)[0]
def wet(p):
 # Limite XY exato da superfície: raio 3D gerava falsos positivos na margem.
 x,y=float(p.x),float(p.y)
 for a,b,c in water_tri:
  dx,dy=b[0]-a[0],b[1]-a[1];ex,ey=c[0]-a[0],c[1]-a[1];px,py=x-a[0],y-a[1];den=dx*ey-dy*ex
  if abs(den)<1e-12:continue
  u=(px*ey-py*ex)/den;v=(dx*py-dy*px)/den
  if u>=-1e-10 and v>=-1e-10 and u+v<=1+1e-10:return True
 return False
def height(p):
 hit=floor(p)
 if hit is not None:return float(hit.z)
 found=[]
 for a,b in ground_edges:
  d=b-a;length=d.x*d.x+d.y*d.y
  if length<1e-12:continue
  t=max(0,min(1,((p.x-a.x)*d.x+(p.y-a.y)*d.y)/length))
  q=a+d*t;found.append((math.hypot(p.x-q.x,p.y-q.y),-q.z))
 distance,z=min(found);assert distance<2.01,('Sem borda de apoio',distance)
 return -z
water_ec=Counter();water_coords={}
for tri in water_tri:
 for a,b in zip(tri,tri[1:]+tri[:1]):
  ka,kb=key(a),key(b);water_coords[ka]=Vector(a);water_coords[kb]=Vector(b);water_ec[tuple(sorted((ka,kb)))]+=1
water_edges=[(water_coords[a],water_coords[b]) for (a,b),count in water_ec.items() if count==1]
def cuts(mesh,points,origin):
 xmin=min(p.x for p in points)-1e-5;xmax=max(p.x for p in points)+1e-5
 ymin=min(p.y for p in points)-1e-5;ymax=max(p.y for p in points)+1e-5
 number=0
 for wa,wb in ground_edges+water_edges:
  a=wa-origin;b=wb-origin
  if max(a.x,b.x)<xmin or min(a.x,b.x)>xmax or max(a.y,b.y)<ymin or min(a.y,b.y)>ymax:continue
  d=b-a
  if math.hypot(d.x,d.y)<1e-6:continue
  bmesh.ops.bisect_plane(mesh,geom=list(mesh.verts)+list(mesh.edges)+list(mesh.faces),dist=1e-7,plane_co=Vector((a.x,a.y,0)),plane_no=Vector((-d.y,d.x,0)).normalized(),clear_inner=False,clear_outer=False);number+=1
 return number
def qa(me,closed):
 me.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(me)
 row={'vertices':len(me.vertices),'faces':len(me.polygons),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'degenerate_triangles':sum(t.area<1e-9 for t in me.loop_triangles),'finite':all(math.isfinite(c) for v in me.vertices for c in v.co),'signed_volume':bm.calc_volume(signed=True) if closed else None}
 bm.free();assert row['finite'] and row['degenerate_triangles']==0,('QA',row)
 if closed:assert row['nonmanifold_edges']==0 and row['signed_volume']>0,row
 return row
for orphan in list(bpy.data.meshes):
 if orphan.name.startswith(('B68_LAND_CONTACT_','B68_LAND_VOLUME_')) and orphan.users==0:bpy.data.meshes.remove(orphan)
def split_point_fans(me):
 xyz=[tuple(v.co) for v in me.vertices];faces=[list(f.vertices) for f in me.polygons]
 incident={i:[] for i in range(len(xyz))};links={}
 for fi,face in enumerate(faces):
  for v in face:incident[v].append(fi)
  for a,b in zip(face,face[1:]+face[:1]):links.setdefault(tuple(sorted((a,b))),[]).append(fi)
 assert all(len(items)<=2 for items in links.values()),'Aresta de superfície com mais de duas faces'
 out_xyz=[];mapping={};fans_count=0
 for vi,items in incident.items():
  remaining=set(items)
  while remaining:
   frontier=[remaining.pop()];fan=set(frontier)
   while frontier:
    fi=frontier.pop()
    for a,b in zip(faces[fi],faces[fi][1:]+faces[fi][:1]):
     if vi not in (a,b):continue
     for other in links[tuple(sorted((a,b)))]:
      if other in remaining:remaining.remove(other);fan.add(other);frontier.append(other)
   index=len(out_xyz);out_xyz.append(xyz[vi])
   for fi in fan:mapping[(fi,vi)]=index
  if len(items):fans_count+=1
 out_faces=[[mapping[(fi,vi)] for vi in face] for fi,face in enumerate(faces)]
 split=len(out_xyz)-len(xyz)
 if split:
  me.clear_geometry();me.from_pydata(out_xyz,[],out_faces);me.update()
 return split
prepared=[]
for feature in probe['features']:
 oid=feature['osm_id'];edge=min(feature['edges'],key=lambda row:row['max_gap_xy'])
 assert edge['max_gap_xy']<1e-4
 a=Vector((*edge['samples'][0]['shore_xy'],0));b=Vector((*edge['samples'][-1]['shore_xy'],0))
 d=b-a;n=Vector((-d.y,d.x,0)).normalized()
 assert not wet((a+b)/2+n*.1)
 points=[a-n*.25,b-n*.25,b+n*2,a+n*2] # Busca atravessa a corda; recorte final usa a costa efetiva.
 assert all(floor(p+n*.001) is not None for p in points[2:]),'Busca terrestre não alcançou apoio'

 origin=(a+b)/2
 def cross2(u,v):return u[0]*v[1]-u[1]*v[0]
 def area2(poly):return sum(cross2(p,q) for p,q in zip(poly,poly[1:]+poly[:1]))/2
 def clip(poly,p,q,inside):
  result=[];edge=(q[0]-p[0],q[1]-p[1])
  for u,v in zip(poly,poly[1:]+poly[:1]):
   du=cross2(edge,(u[0]-p[0],u[1]-p[1]));dv=cross2(edge,(v[0]-p[0],v[1]-p[1]))
   iu=du>=-1e-10 if inside else du<=1e-10
   iv=dv>=-1e-10 if inside else dv<=1e-10
   if iu:result.append(u)
   if iu!=iv:
    t=du/(du-dv);result.append((u[0]+t*(v[0]-u[0]),u[1]+t*(v[1]-u[1])))
  return result
 poly=[(float(p.x-origin.x),float(p.y-origin.y)) for p in points]
 if area2(poly)<0:poly.reverse()
 pieces=[poly];count=0
 xmin=min(p[0] for p in poly);xmax=max(p[0] for p in poly);ymin=min(p[1] for p in poly);ymax=max(p[1] for p in poly)
 for tri in ground+water_tri:
  tr=[(float(p[0])-origin.x,float(p[1])-origin.y) for p in tri]
  if max(p[0] for p in tr)<xmin or min(p[0] for p in tr)>xmax or max(p[1] for p in tr)<ymin or min(p[1] for p in tr)>ymax or abs(area2(tr))<1e-10:continue
  if area2(tr)<0:tr.reverse()
  new=[]
  for piece in pieces:
   rest=piece
   for p,q in zip(tr,tr[1:]+tr[:1]):
    if len(rest)<3:break
    outside=clip(rest,p,q,False)
    if len(outside)>2 and abs(area2(outside))>1e-10:new.append(outside)
    rest=clip(rest,p,q,True)
  pieces=new;count+=1
 assert pieces
 xy=[];lookup={};constraints=[]
 for poly in pieces:
  indices=[]
  for p in poly:
   keyxy=(round(p[0],7),round(p[1],7))
   if keyxy not in lookup:lookup[keyxy]=len(xy);xy.append(Vector(keyxy))
   indices.append(lookup[keyxy])
  constraints.extend((i,j) for i,j in zip(indices,indices[1:]+indices[:1]) if i!=j)
 verts2,edges2,faces2,*_=geometry.delaunay_2d_cdt(xy,constraints,[],0,1e-7,False)
 def in_piece(p,poly):
  return all(cross2((q[0]-v[0],q[1]-v[1]),(p[0]-v[0],p[1]-v[1]))>=-1e-7 for v,q in zip(poly,poly[1:]+poly[:1]))
 bm=bmesh.new();vv=[bm.verts.new(Vector((p.x+origin.x,p.y+origin.y,0))) for p in verts2]
 for f in faces2:
  center=(sum(verts2[i].x for i in f)/len(f),sum(verts2[i].y for i in f)/len(f))
  if any(in_piece(center,poly) for poly in pieces):bm.faces.new([vv[i] for i in f])
 for v in list(bm.verts):
  if not v.link_faces:bmesh.ops.delete(bm,geom=[v],context='VERTS')
 bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.delete(bm,geom=[f for f in bm.faces if abs((f.verts[1].co-f.verts[0].co).cross(f.verts[2].co-f.verts[0].co).z)<2e-6 or wet(SimpleNamespace(x=sum(float(v.co.x) for v in f.verts)/len(f.verts),y=sum(float(v.co.y) for v in f.verts)/len(f.verts)))],context='FACES');bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 bmesh.ops.reverse_faces(bm,faces=[f for f in bm.faces if f.normal.z<0])
 area=sum(f.calc_area() for f in bm.faces);rejected_area=0
 for v in bm.verts:v.co.z=height(v.co)
 top=bpy.data.meshes.new(f'B68_LAND_CONTACT_{oid}');bm.to_mesh(top);bm.free();top.update()
 top.materials.append(bpy.data.materials['CAIS | pedra costeira'])
 point_splits=split_point_fans(top)
 tq=qa(top,False);top.calc_loop_triangles()
 from types import SimpleNamespace
 def centroid(t):return SimpleNamespace(x=sum(float(top.vertices[i].co.x) for i in t.vertices)/3,y=sum(float(top.vertices[i].co.y) for i in t.vertices)/3)
 def planar_area(t):
  a,b,c=[top.vertices[i].co for i in t.vertices]
  return abs((b-a).cross(c-a).z)/2
 ground_overlap=sum(planar_area(t) for t in top.loop_triangles if floor(centroid(t)) is not None);water_overlap=sum(planar_area(t) for t in top.loop_triangles if wet(centroid(t)))
 (r/'docs/reports/blender/pier_cut_diagnostics_b69.json').write_text(json.dumps({'osm_id':oid,'pieces':len(pieces),'piece_areas':[area2(p) for p in pieces],'piece_wet_centers':sum(wet(Vector((sum(q[0] for q in p)/len(p)+origin.x,sum(q[1] for q in p)/len(p)+origin.y,0))) for p in pieces),'cdt_faces':len(faces2),'kept_faces':len(top.polygons),'overwater_triangles':[[list(top.vertices[i].co) for i in t.vertices] for t in top.loop_triangles if wet(t.center)]},indent=2),encoding='utf8')
 assert ground_overlap<1e-6 and water_overlap<1e-6,(oid,ground_overlap,water_overlap)
 xyz=[tuple(v.co) for v in top.vertices];length=len(xyz);faces=[list(f.vertices) for f in top.polygons]
 ec=Counter(tuple(sorted((a,b))) for f in faces for a,b in zip(f,f[1:]+f[:1]))
 solid_xyz=xyz+[(x,y,.35) for x,y,z in xyz]
 solid_faces=faces+[[i+length for i in reversed(f)] for f in faces]+[[a,b,b+length,a+length] for (a,b),edge_count in ec.items() if edge_count==1]
 solid=bpy.data.meshes.new(f'B68_LAND_VOLUME_{oid}');solid.from_pydata(solid_xyz,[],solid_faces);solid.materials.append(top.materials[0]);solid.update()
 bm=bmesh.new();bm.from_mesh(solid);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 bm.to_mesh(solid);bm.free();solid.update();sq=qa(solid,True)
 pier=s.objects[f'B67 | PIER VISUAL | {oid}'];deck=float(pier['boas_deck_z_candidate_m'])
 probes=[]
 for k in range(41):
  t=k/40;p=a.lerp(b,t)
  probes.append({'t':t,'xy':[p.x,p.y],'land_top_z':height(p),'deck_z':deck,'deck_land_z_difference':abs(height(p)-deck)})
 top.calc_loop_triangles();tt=tree([[list(top.vertices[i].co) for i in tri.vertices] for tri in top.loop_triangles])
 missing_before=0;missing_after=[]
 for k in range(1,81):
  for j in range(1,101):
   q=a.lerp(b,k/81)+n*(j*.02)
   if floor(q) is not None or wet(q):continue
   missing_before+=1
   if tt.ray_cast(Vector((q.x,q.y,150)),Vector((0,0,-1)),300)[0] is None:missing_after.append([q.x,q.y])
 assert not missing_after,('Lacuna residual',oid,len(missing_after),missing_after[:5])
 prepared.append({'coverage_samples':8000,'terrestrial_missing_before':missing_before,'terrestrial_missing_after':len(missing_after),'osm_id':oid,'top':top,'solid':solid,'top_qa':tq,'point_contact_vertices_split':point_splits,'solid_qa':sq,'area_m2':area,'cuts':count,'discarded_post_triangulation_area_m2':rejected_area,'water_overlap_area_m2':water_overlap,'ground_overlap_area_m2':ground_overlap,'coast_probes':probes,'max_deck_land_difference_m':max(p['deck_land_z_difference'] for p in probes)})
assert shutil.disk_usage(r).free>reserve
def collection(name):
 col=bpy.data.collections.get(name)
 if col is None:col=bpy.data.collections.new(name);s.collection.children.link(col)
 return col
created=[]
for row in prepared:
 oid=row['osm_id'];vo=s.objects[f'B68 | VISUAL | encontro terrestre | {oid}'];to=s.objects[f'B68 | WALKABLE CANDIDATE | encontro terrestre | {oid}'];co=s.objects[f'B68 | COLLISION CANDIDATE | encontro terrestre | {oid}']
 vo.data=row['solid'];to.data=row['top'];co.data=row['solid'].copy()
 for ob in (vo,to,co):
  ob['boas_revision']='R30B.69';ob['boas_geometry_basis']='exact_convex_subtraction_ground_and_water_local_cdt';ob['boas_source_report']='docs/reports/blender/pier_land_contacts_r30b69.json'
 created.append({k:v for k,v in row.items() if k not in ('top','solid')}|{'visual':vo.name,'walkable':to.name,'collision':co.name})
changed=[n for n,old in protected.items() if sig(s.objects[n])!=old];assert not changed,changed
s['boas_validation_revision']='R30B.69';s['boas_coastal_contact_status']='two_land_gaps_closed_absolute_heights_pending'
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
with out.open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
rp=r/'docs/reports/blender/pier_land_contacts_r30b69.json'
report={'schema':'boas/pier-land-contacts-b69-v1','source_before':src,'source_after':{'file':out.relative_to(r).as_posix(),'revision':'R30B.69','sha256':sha},'region_export_sha256':hashlib.sha256(region_path.read_bytes()).hexdigest(),'source_region':'artifacts/waterfront/pier_land_region_b67.json','protected_signatures':protected,'protected_changes':changed,'contacts':created,'water_level_m':.35,'water_changed':False,'terrain_changed':False,'pier_footprints_changed':False,'road_width_changed':False,'runtime_exported':False,'real_fidelity_approved':False,'source_reopened':False,'pending':['Desnível do píer 609043799: não há rampa/ligação aprovada','Altimetria absoluta água/cais/decks e fundações reais','Passarelas sem largura real e navegação/física completas','Conferência visual da janela: captura preta']}
rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(r/'artifacts/waterfront/blender_revisions_before_b69.json').write_bytes(cp.read_bytes())
entry={**report['source_after'],'status':'validation_candidate','parent_file':src['file'],'evidence':rp.relative_to(r).as_posix(),'notes':'Corrige frestas residuais por cortes em coordenadas locais; 16000 probes, sem lacunas terrestres amostradas. Terrenos, costa, mar e decks preservados; alturas e acessibilidade pendentes.'}
for old in cat['revisions']:
 if old['file']==src['file']:old['status']='superseded_validation'
cat['revisions'].append(entry);cat['validation_source']=entry.copy();cp.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'source_after':report['source_after'],'areas_m2':[p['area_m2'] for p in created],'max_steps_m':[p['max_deck_land_difference_m'] for p in created]}))
