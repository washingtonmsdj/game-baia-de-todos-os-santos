"""B67: referências reais de píeres, volume e faixa costeira derivados da água atual."""
import bpy,bmesh,json,hashlib,shutil,runpy,statistics,math
from pathlib import Path
from collections import Counter,defaultdict
from mathutils import Vector,Euler
r=Path(__file__).resolve().parents[2];sc=bpy.context.scene
cp=r/'world/areas/mvp-centro-lacerda/blender-revisions.json';cat=json.loads(cp.read_text(encoding='utf-8-sig'));src=cat['validation_source']
assert src['revision']=='R30B.66'
assert Path(bpy.data.filepath).resolve()==(r/src['file']).resolve()
with (r/src['file']).open('rb') as h:assert hashlib.file_digest(h,'sha256').hexdigest()==src['sha256']
out=r/'blender/salvador_lacerda_r30b67_pieres_e_dominio_oceanico.blend';assert not out.exists()
minimum=2*(r/src['file']).stat().st_size+50*1024**2
assert shutil.disk_usage(r).free>minimum,('Disco insuficiente antes de alterar a cena',shutil.disk_usage(r).free,minimum)
source=json.loads((r/'docs/reports/blender/coastal_osm_source_check.json').read_text(encoding='utf-8-sig'))
assert source['local_transform_reuse_checked'] and len(source['same_feature_controls'])>=4
raw=r/source['source_file'];assert hashlib.sha256(raw.read_bytes()).hexdigest()==source['compressed_sha256']
features={f['osm_id']:f for f in source['features']}
contacts=json.loads((r/'docs/reports/blender/pier_land_contacts_b67_probe.json').read_text(encoding='utf-8-sig'))
contacts={f['osm_id']:f for f in contacts['features']}
assert set(contacts)=={609043799,609043801}
water=sc.objects['BAÍA DE TODOS-OS-SANTOS | superfície e recorte costeiro']
volume=sc.objects['BAÍA | volume de água no limite do recorte']
sig=runpy.run_path(str(r/'automation/blender/component_fingerprint.py'))['signature']
protected_names=[water.name,'MVP | terreno corrigido | colisão estática','B62 | GAMEPLAY TERRAIN HQ | pavimento e costura limpa','CAIS | contenção costeira alinhada à linha de costa']+[o.name for o in sc.objects if o.name.startswith(('B56 | COLLISION | PIER |','B57 | PIER VISUAL |'))]
protected={n:sig(sc.objects[n]) for n in protected_names}
level=float(water['boas_water_level_m']);bottom=-16.0
points=[water.matrix_world@v.co for v in water.data.vertices]
polys=[list(f.vertices) for f in water.data.polygons]
usage=Counter(tuple(sorted((a,b))) for ids in polys for a,b in zip(ids,ids[1:]+ids[:1]))
boundary=[e for e,count in usage.items() if count==1]
xmin=min(p.x for p in points);ymin=min(p.y for p in points);ymax=max(p.y for p in points)
def clip_edge(a,b):
 return (abs(a.x-xmin)<1e-5 and abs(b.x-xmin)<1e-5) or (abs(a.y-ymin)<1e-5 and abs(b.y-ymin)<1e-5) or (abs(a.y-ymax)<1e-5 and abs(b.y-ymax)<1e-5)
shore=[e for e in boundary if not clip_edge(points[e[0]],points[e[1]])]
adj=defaultdict(list)
for a,b in shore:adj[a].append(b);adj[b].append(a)
unused=set(tuple(sorted(e)) for e in shore);chains=[]
while unused:
 ends=sorted(i for e in unused for i in e if sum(tuple(sorted((i,n))) in unused for n in adj[i])==1)
 start=ends[0] if ends else min(min(e) for e in unused);chain=[start];cur=start
 while True:
  ns=sorted(n for n in adj[cur] if tuple(sorted((cur,n))) in unused)
  if not ns:break
  n=ns[0];unused.remove(tuple(sorted((cur,n))));chain.append(n);cur=n
  if cur==start:break
 if len(chain)>1:chains.append(chain)
# Volume de gameplay derivado; não representa batimetria nem colisor rígido.
n=len(points);iv=volume.matrix_world.inverted()
vv=[iv@Vector((p.x,p.y,level)) for p in points]+[iv@Vector((p.x,p.y,bottom)) for p in points]
ff=polys+[[i+n for i in reversed(ids)] for ids in polys]+[[a,b,b+n,a+n] for a,b in boundary]
vm=bpy.data.meshes.new('B67_WATER_VOLUME_DERIVED');vm.from_pydata(vv,[],ff);vm.update()
bm=bmesh.new();bm.from_mesh(vm)
bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7)
bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-8)
loose=[e for e in bm.edges if not e.link_faces]
if loose:bmesh.ops.delete(bm,geom=loose,context='EDGES')
loose=[v for v in bm.verts if not v.link_faces]
if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
nonmanifold=sum(not e.is_manifold for e in bm.edges);assert nonmanifold==0,('Volume aberto',nonmanifold)
bm.to_mesh(vm);bm.free();vm.update();vm.calc_loop_triangles()
assert not any(t.area<1e-9 for t in vm.loop_triangles)
for m in volume.data.materials:vm.materials.append(m)
foam_data={}
for name in ('R30A8 | FOAM | linha costeira','R30A8 | FOAM | halo costeiro'):
 ob=sc.objects[name];cu=ob.data.copy();cu.name='B67_'+name
 for spline in list(cu.splines):cu.splines.remove(spline)
 z=float(next(iter(ob.data.splines)).points[0].co.z)
 inverse=ob.matrix_world.inverted()
 for chain in chains:
  sp=cu.splines.new('POLY');sp.points.add(len(chain)-1)
  for p,i in zip(sp.points,chain):co=inverse@Vector((points[i].x,points[i].y,z));p.co=(*co,1)
 foam_data[name]=cu
def collection(name):
 col=bpy.data.collections.get(name)
 if col is None:col=bpy.data.collections.new(name);sc.collection.children.link(col)
 return col
refcol=collection('SOURCE_GEOREF | WATERFRONT OSM B67')
viscol=collection('ENVIRONMENT | PIERS CANDIDATES B67')
gamecol=collection('GAMEPLAY | PIERS CANDIDATES B67')
mat=bpy.data.materials['CAIS | pedra costeira']
prepared=[]
def mesh(name,xyz,faces):
 me=bpy.data.meshes.new(name);me.from_pydata(xyz,[],faces);me.update()
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 if max(p[2] for p in xyz)-min(p[2] for p in xyz)<1e-6:
  bmesh.ops.reverse_faces(bm,faces=[f for f in bm.faces if f.normal.z<0])
 else:assert not any(not e.is_manifold for e in bm.edges)
 bm.to_mesh(me);bm.free();me.update();me.calc_loop_triangles();assert not any(t.area<1e-9 for t in me.loop_triangles)
 me.materials.append(mat);return me
for oid in (609043799,609043801):
 f=features[oid];assert f['closed'] and f['tags']['man_made']=='pier'
 xy=f['blender_xy'][:-1];controls=contacts[oid]['near_land_controls'];assert controls
 deck=statistics.median(c['floor_z'] for c in controls)
 top=[(x,y,deck) for x,y in xy];count=len(top)
 visual=mesh(f'B67_PIER_{oid}_VISUAL',top+[(x,y,deck-.35) for x,y in xy],[list(range(count)),list(range(2*count-1,count-1,-1))]+[[i,(i+1)%count,(i+1)%count+count,i+count] for i in range(count)])
 surface=mesh(f'B67_PIER_{oid}_TOP',top,[list(range(count))])
 prepared.append({'osm_id':oid,'feature':f,'deck_z_candidate':deck,'land_controls':controls,'visual':visual,'surface':surface,'xy':xy})
assert shutil.disk_usage(r).free>minimum,('Disco insuficiente antes da aplicação',shutil.disk_usage(r).free,minimum)
volume.data=vm;volume['boas_revision']='R30B.67';volume['boas_runtime_role']='water_volume';volume['boas_water_role']='swim_dive_volume'
volume['boas_domain_source']=water.name;volume['boas_bathymetry_verified']=False;volume['boas_volume_depth_status']='legacy_gameplay_range_not_surveyed'
volume['boas_collision_source']=False;volume['boas_export_candidate']=False
for name,cu in foam_data.items():
 ob=sc.objects[name];ob.data=cu;ob['boas_revision']='R30B.67';ob['boas_source']='current_water_surface_boundary';ob['boas_artificial_clip_edges_excluded']=True;ob['boas_runtime_role']='visual_water_reference';ob['boas_export_candidate']=False
water['boas_water_level_status']='candidate_vertical_datum_pending'
created=[]
for row in prepared:
 oid=row['osm_id'];deck=row['deck_z_candidate']
 ob=bpy.data.objects.new(f'B67 | PIER VISUAL | {oid}',row['visual']);viscol.objects.link(ob)
 rb=bpy.data.objects.new(f'B67 | REFERENCE PIER | {oid}',row['surface'].copy());refcol.objects.link(rb);rb.hide_set(True);rb.hide_render=True
 top=bpy.data.objects.new(f'B67 | WALKABLE CANDIDATE | {oid}',row['surface']);gamecol.objects.link(top);top.hide_set(True);top.hide_render=True
 co=bpy.data.objects.new(f'B67 | COLLISION CANDIDATE | PIER | {oid}',row['surface'].copy());gamecol.objects.link(co);co.hide_set(True);co.hide_render=True
 for item in (ob,rb,top,co):
  item['boas_osm_id']=oid;item['boas_osm_type']='way';item['boas_source_report']='docs/reports/blender/coastal_osm_source_check.json';item['boas_source_raw_sha256']=source['raw_sha256'];item['boas_width_status']='closed_footprint_from_osm';item['boas_height_status']='local_land_candidate_not_surveyed';item['boas_deck_z_candidate_m']=deck;item['boas_gameplay_approved']=False;item['boas_export_candidate']=False;item['boas_revision']='R30B.67'
 ob['boas_xy_classification']='KEEP_REAL_REFERENCE';ob['boas_z_classification']='ADAPT_LOCAL';ob['boas_material_status']='candidate_not_photo_verified';ob['boas_runtime_role']='pier_visual_candidate';ob['boas_collision_partner']=co.name;ob['boas_visual_thickness_m']=.35;ob['boas_thickness_status']='existing_visual_design_not_surveyed'
 rb['boas_runtime_role']='reference_surface';top['boas_runtime_role']='walkable_surface_candidate';co['boas_runtime_role']='walkable_collision_candidate';co['boas_source_surface']=top.name
 created.append({'osm_id':oid,'visual':ob.name,'reference':rb.name,'surface':top.name,'collision':co.name,'deck_z_candidate_m':deck,'land_height_spread':max(v['floor_z'] for v in row['land_controls'])-min(v['floor_z'] for v in row['land_controls']),'connection_approved':False,'foundation_verified':False,'xy_footprint_changed':False})
# Eixos e passarela sem largura: referências ocultas, nunca superfícies inventadas.
axes=[]
for oid in (1321555661,1321717133,217677378,1426173324):
 f=features[oid];cu=bpy.data.curves.new(f'B67_SOURCE_AXIS_{oid}','CURVE');cu.dimensions='3D';cu.bevel_depth=.04
 sp=cu.splines.new('POLY');sp.points.add(len(f['blender_xy'])-1)
 for p,(x,y) in zip(sp.points,f['blender_xy']):p.co=(x,y,level,1)
 ob=bpy.data.objects.new(f'B67 | SOURCE AXIS WIDTH UNKNOWN | {oid}',cu);refcol.objects.link(ob);ob.hide_set(True);ob.hide_render=True
 ob['boas_osm_id']=oid;ob['boas_osm_type']='way';ob['boas_source_report']='docs/reports/blender/coastal_osm_source_check.json';ob['boas_runtime_role']='reference_centerline_width_unknown';ob['boas_width_status']='pending';ob['boas_display_plane_z']=level;ob['boas_display_plane_is_deck_height']=False;ob['boas_export_candidate']=False;ob['boas_gameplay_approved']=False
 axes.append({'osm_id':oid,'name':ob.name,'width_m':None,'deck_z_m':None})
# A ligação já existia no OSM; registrar a omissão, sem criar largura falsa.
sc['boas_validation_revision']='R30B.67';sc['boas_coastal_vertical_status']='pending_real_water_and_deck_datum'
changes=[name for name,old in protected.items() if sig(sc.objects[name])!=old];assert not changes,changes
for win in bpy.context.window_manager.windows:
 for ar in win.screen.areas:
  if ar.type=='VIEW_3D':
   sp=ar.spaces.active;sp.shading.type='SOLID';sp.shading.color_type='MATERIAL';sp.overlay.show_extras=False
   sp.region_3d.view_location=Vector((-220,90,12));sp.region_3d.view_distance=490;sp.region_3d.view_rotation=Euler((math.radians(52),0,math.radians(-36)),'XYZ').to_quaternion();sp.region_3d.view_perspective='ORTHO'
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
with out.open('rb') as h:sha=hashlib.file_digest(h,'sha256').hexdigest()
report={'schema':'boas/waterfront-piers-b67-v1','source_before':src,'source_after':{'file':out.relative_to(r).as_posix(),'revision':'R30B.67','sha256':sha},'source_check':'docs/reports/blender/coastal_osm_source_check.json','same_feature_controls':source['same_feature_controls'],'new_closed_piers':created,'new_reference_axes':axes,'water_level_m_preserved':level,'legacy_pier_freeboard_candidate_m':7.255664825439453-level,'absolute_water_datum_verified':False,'water_volume_nonmanifold_edges':nonmanifold,'volume_range_m':[bottom,level],'volume_is_bathymetry':False,'shoreline_segments':len(shore),'shoreline_chains':len(chains),'artificial_boundary_edges_excluded':len(boundary)-len(shore),'foam_source_updated':True,'protected_changes':changes,'terrain_changed':False,'road_width_changed':False,'runtime_exported':False,'real_fidelity_approved':False,'pending':['Altimetria/maré dos píeres antigos e novos sem levantamento','Ligação dos novos decks com a margem e apoios/fundações não aprovados','Eixos de píer/quebra-mar e passarelas sem largura permanecem referência','Fidelidade arquitetônica e percursos de gameplay continuam pendentes']}
rp=r/'docs/reports/blender/waterfront_piers_r30b67.json';rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
entry={**report['source_after'],'status':'validation_candidate','parent_file':src['file'],'evidence':rp.relative_to(r).as_posix(),'notes':'Dois contornos reais de píeres OSM adicionados; volume/espuma derivados do limite atual da água. Nível marítimo, alturas e conexões dos decks continuam candidatos; sem promoção de runtime.'}
(r/'artifacts/waterfront/blender_revisions_before_b67.json').write_bytes(cp.read_bytes())
for old in cat['revisions']:
 if old['file']==src['file']:old['status']='superseded_validation'
cat['revisions'].append(entry);cat['validation_source']=entry.copy()
cp.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert json.loads(cp.read_text(encoding='utf-8'))['validation_source']['sha256']==sha
print(json.dumps({'source_after':report['source_after'],'new_closed_piers':created,'volume_nonmanifold':nonmanifold}))
