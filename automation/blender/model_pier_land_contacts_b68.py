"""B68: fechar apenas lacunas terrestres nos encontros reais dos píeres."""
import bpy,bmesh,json,hashlib,math,shutil,runpy
from pathlib import Path
from collections import Counter
from mathutils import Vector
from mathutils.bvhtree import BVHTree
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
cp=r/'world/areas/mvp-centro-lacerda/blender-revisions.json';cat=json.loads(cp.read_text(encoding='utf-8'));src=cat['validation_source']
assert src['revision']=='R30B.67' and Path(bpy.data.filepath).resolve()==(r/src['file']).resolve()
with (r/src['file']).open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==src['sha256']
out=r/'blender/salvador_lacerda_r30b68_encontros_terrestres_pieres.blend';assert not out.exists()
reserve=2*(r/src['file']).stat().st_size+150*1024**2
assert shutil.disk_usage(r).free>reserve
probe=json.loads((r/'docs/reports/blender/pier_shore_contacts_b68_probe.json').read_text(encoding='utf-8'))
region_path=r/'artifacts/waterfront/pier_land_region_b67.json'
region=json.loads(region_path.read_text(encoding='utf-8'));assert region['source']['sha256']==src['sha256']
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
def wet(p):return wt.ray_cast(Vector((p.x,p.y,150)),Vector((0,0,-1)),300)[0] is not None
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
def cuts(mesh,points):
 xmin=min(p.x for p in points)-1e-5;xmax=max(p.x for p in points)+1e-5
 ymin=min(p.y for p in points)-1e-5;ymax=max(p.y for p in points)+1e-5
 number=0
 for a,b in ground_edges+water_edges:
  if max(a.x,b.x)<xmin or min(a.x,b.x)>xmax or max(a.y,b.y)<ymin or min(a.y,b.y)>ymax:continue
  d=b-a
  if math.hypot(d.x,d.y)<1e-6:continue
  bmesh.ops.bisect_plane(mesh,geom=list(mesh.verts)+list(mesh.edges)+list(mesh.faces),dist=1e-7,plane_co=Vector((a.x,a.y,0)),plane_no=Vector((-d.y,d.x,0)).normalized(),clear_inner=False,clear_outer=False);number+=1
 return number
def qa(me,closed):
 me.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(me)
 row={'vertices':len(me.vertices),'faces':len(me.polygons),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'degenerate_triangles':sum(t.area<1e-9 for t in me.loop_triangles),'finite':all(math.isfinite(c) for v in me.vertices for c in v.co),'signed_volume':bm.calc_volume(signed=True) if closed else None}
 bm.free();assert row['finite'] and row['degenerate_triangles']==0
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
 points=[a,b,b+n*2,a+n*2]
 assert all(floor(p+n*.001) is not None for p in points[2:]),'Busca terrestre não alcançou apoio'
 bm=bmesh.new();vs=[bm.verts.new(p) for p in points];bm.faces.new(vs)
 count=cuts(bm,points)
 remove=[f for f in bm.faces if f.calc_area()<1e-8 or floor(f.calc_center_median()) is not None or wet(f.calc_center_median())]
 bmesh.ops.delete(bm,geom=remove,context='FACES')
 for v in list(bm.verts):
  if not v.link_faces:bmesh.ops.delete(bm,geom=[v],context='VERTS')
 assert bm.faces,('Nenhuma lacuna real',oid)
 bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
 bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-8)
 bmesh.ops.triangulate(bm,faces=list(bm.faces))
 residual=[f for f in bm.faces if f.calc_area()<1e-8 or floor(f.calc_center_median()) is not None or wet(f.calc_center_median())]
 rejected_area=sum(f.calc_area() for f in residual)
 bmesh.ops.delete(bm,geom=residual,context='FACES')
 for v in list(bm.verts):
  if not v.link_faces:bmesh.ops.delete(bm,geom=[v],context='VERTS')
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 bmesh.ops.reverse_faces(bm,faces=[f for f in bm.faces if f.normal.z<0])
 area=sum(f.calc_area() for f in bm.faces)
 for v in bm.verts:v.co.z=height(v.co)
 top=bpy.data.meshes.new(f'B68_LAND_CONTACT_{oid}');bm.to_mesh(top);bm.free();top.update()
 top.materials.append(bpy.data.materials['CAIS | pedra costeira'])
 point_splits=split_point_fans(top)
 tq=qa(top,False);top.calc_loop_triangles()
 ground_overlap=sum(t.area for t in top.loop_triangles if floor(t.center) is not None);water_overlap=sum(t.area for t in top.loop_triangles if wet(t.center))
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
 prepared.append({'osm_id':oid,'top':top,'solid':solid,'top_qa':tq,'point_contact_vertices_split':point_splits,'solid_qa':sq,'area_m2':area,'cuts':count,'discarded_post_triangulation_area_m2':rejected_area,'water_overlap_area_m2':water_overlap,'ground_overlap_area_m2':ground_overlap,'coast_probes':probes,'max_deck_land_difference_m':max(p['deck_land_z_difference'] for p in probes)})
assert shutil.disk_usage(r).free>reserve
def collection(name):
 col=bpy.data.collections.get(name)
 if col is None:col=bpy.data.collections.new(name);s.collection.children.link(col)
 return col
vis=collection('ENVIRONMENT | COASTAL CONTACTS B68');game=collection('GAMEPLAY | COASTAL CONTACTS B68')
created=[]
for row in prepared:
 oid=row['osm_id']
 vo=bpy.data.objects.new(f'B68 | VISUAL | encontro terrestre | {oid}',row['solid']);vis.objects.link(vo)
 to=bpy.data.objects.new(f'B68 | WALKABLE CANDIDATE | encontro terrestre | {oid}',row['top']);game.objects.link(to);to.hide_set(True);to.hide_render=True
 co=bpy.data.objects.new(f'B68 | COLLISION CANDIDATE | encontro terrestre | {oid}',row['solid'].copy());game.objects.link(co);co.hide_set(True);co.hide_render=True
 for ob in (vo,to,co):
  ob['boas_revision']='R30B.68';ob['boas_area_id']='mvp-centro-lacerda';ob['boas_parent_pier_osm_id']=oid;ob['boas_classification']='ERROR';ob['boas_source_report']='docs/reports/blender/pier_shore_contacts_b68_probe.json'
  ob['boas_geometry_basis']='real_source_shore_edge_minus_current_land_coverage';ob['boas_gameplay_approved']=False;ob['boas_export_candidate']=False;ob['boas_height_status']='existing_land_edge_not_surveyed';ob['boas_foundation_status']='volume_to_reference_water_plane_not_real_foundation'
 vo['boas_runtime_role']='coastal_ground_visual_candidate';vo['boas_collision_partner']=co.name;vo['boas_material_status']='candidate_existing_quay_material'
 to['boas_runtime_role']='coastal_walkable_candidate';co['boas_runtime_role']='coastal_volume_collision_candidate';co['boas_source_surface']=vo.name
 created.append({k:v for k,v in row.items() if k not in ('top','solid')}|{'visual':vo.name,'walkable':to.name,'collision':co.name})
changed=[n for n,old in protected.items() if sig(s.objects[n])!=old];assert not changed,changed
s['boas_validation_revision']='R30B.68';s['boas_coastal_contact_status']='two_land_gaps_closed_absolute_heights_pending'
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
with out.open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
rp=r/'docs/reports/blender/pier_land_contacts_r30b68.json'
report={'schema':'boas/pier-land-contacts-b68-v1','source_before':src,'source_after':{'file':out.relative_to(r).as_posix(),'revision':'R30B.68','sha256':sha},'region_export_sha256':hashlib.sha256(region_path.read_bytes()).hexdigest(),'source_region':'artifacts/waterfront/pier_land_region_b67.json','protected_signatures':protected,'protected_changes':changed,'contacts':created,'water_level_m':.35,'water_changed':False,'terrain_changed':False,'pier_footprints_changed':False,'road_width_changed':False,'runtime_exported':False,'real_fidelity_approved':False,'source_reopened':False,'pending':['Desnível do píer 609043799: não há rampa/ligação aprovada','Altimetria absoluta água/cais/decks e fundações reais','Passarelas sem largura real e navegação/física completas','Conferência visual da janela: captura preta']}
rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(r/'artifacts/waterfront/blender_revisions_before_b68.json').write_bytes(cp.read_bytes())
entry={**report['source_after'],'status':'validation_candidate','parent_file':src['file'],'evidence':rp.relative_to(r).as_posix(),'notes':'Fecha apenas lacunas terrestres nos dois encontros reais, sem deslocar terreno, costa, píeres ou mar. Desníveis e altimetria continuam pendentes.'}
for old in cat['revisions']:
 if old['file']==src['file']:old['status']='superseded_validation'
cat['revisions'].append(entry);cat['validation_source']=entry.copy();cp.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'source_after':report['source_after'],'areas_m2':[p['area_m2'] for p in created],'max_steps_m':[p['max_deck_land_difference_m'] for p in created]}))
