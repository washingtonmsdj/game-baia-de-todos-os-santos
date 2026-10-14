"""Cabines candidatas dentro da arquitetura; escavação local pelo núcleo17."""
import bpy,json,runpy,math
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.geometry import delaunay_2d_cdt
from array import array
import numpy as np
root=Path(__file__).resolve().parents[2];out=root/'docs/reports/blender/lacerda-exterior-b102'
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));sig=h['signature'];wm=h['world_matrix']
M=Matrix(json.loads((root/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text())['measurement_frame']);inv=M.inverted()
r=json.loads((out/'application.json').read_text());cp=root/'world/areas/mvp-centro-lacerda/lacerda-four-lifts.json';cfg=json.loads(cp.read_text())
assert not r.get('clearance_reconciled')
for spec in cfg['equipment']:
 shift=-.75 if spec['number']==2 else 0.;factor=.85 if spec['number'] in (3,4) else 1.
 cx,cy=spec['center_local'];ca,sa=math.cos(spec['angle_local']),math.sin(spec['angle_local'])
 for part in spec['parts']:
  o=bpy.data.objects[part['object']]
  # Reinício seguro após guarda read-only: a mesh original dos proxies novos
  # continua no datablock, e não se acumula transformação de uma tentativa.
  original=bpy.data.meshes.get(part['object']);assert original is not None
  o.data=original;mesh=original.copy()
  for v in mesh.vertices:
   x,y=v.co.x-cx,v.co.y-cy;lx=(ca*x+sa*y)*factor;ly=-sa*x+ca*y
   v.co.x=cx+ca*lx-sa*ly;v.co.y=cy+sa*lx+ca*ly+shift
  mesh.update();o.data=mesh;part['center'][0]*=factor;part['size'][0]*=factor
 spec['center_local'][1]+=shift;spec['size'][0]*=factor
 spec['enclosure_size']=[2.12*factor,2.47,2.74]
 spec['candidate_fit_reason']='Cabine provisória ajustada ao espaço livre da envoltória documental existente; não muda arquitetura nem cápsula'

fc=json.loads((root/'docs/reports/blender/lacerda-massing-b88/architectural-controls.json').read_text())
outer=[Vector(v) for v in fc['polygons']['old_core']['points_local']]
area=lambda p:sum(a.x*b.y-a.y*b.x for a,b in zip(p,p[1:]+p[:1]))/2
if area(outer)<0:outer.reverse()
shaft=[]
for i,b in enumerate(outer):
 u=(b-outer[i-1]).normalized();v=(outer[(i+1)%len(outer)]-b).normalized();nu=Vector((-u.y,u.x));nv=Vector((-v.y,v.x));cross=u.x*v.y-u.y*v.x;t=.18
 if abs(cross)<1e-7:q=b+(nu+nv)*(.5*t)
 else:
  d=(nv-nu)*t;q=b+nu*t+u*((d.x*v.y-d.y*v.x)/cross)
 shaft.append(q)
def inside(p,loop):
 hit=False
 for a,b in zip(loop,loop[1:]+loop[:1]):
  if (a.y>p.y)!=(b.y>p.y) and p.x<(b.x-a.x)*(p.y-a.y)/(b.y-a.y)+a.x:hit=not hit
 return hit
terrain=bpy.context.scene.objects['MVP | terreno corrigido | colisão estática'];old=terrain.data
assert sig(terrain)==r['terrain_signature']
trans=inv@wm(terrain);back=wm(terrain).inverted()@M
raw=np.empty(len(old.vertices)*3,dtype=np.float32);old.vertices.foreach_get('co',raw);local=raw.reshape((-1,3)).astype(np.float64)
A=np.array(trans);points=local@A[:3,:3].T+A[:3,3]
totals=np.empty(len(old.polygons),dtype=np.int32);old.polygons.foreach_get('loop_total',totals)
starts=np.empty(len(old.polygons),dtype=np.int32);old.polygons.foreach_get('loop_start',starts)
loops=np.empty(len(old.loops),dtype=np.int32);old.loops.foreach_get('vertex_index',loops)
old.calc_loop_triangles();tri_raw=np.empty(len(old.loop_triangles)*3,dtype=np.int32);old.loop_triangles.foreach_get('vertices',tri_raw);faces=tri_raw.reshape((-1,3))
poly_indices=np.empty(len(old.loop_triangles),dtype=np.int32);old.loop_triangles.foreach_get('polygon_index',poly_indices)
tri_loop_raw=np.empty(len(old.loop_triangles)*3,dtype=np.int32);old.loop_triangles.foreach_get('loops',tri_loop_raw);tri_loops=tri_loop_raw.reshape((-1,3))
poly=np.array([list(p) for p in shaft]);lower=poly.min(axis=0);upper=poly.max(axis=0)
xy=points[faces,:2];candidate=np.nonzero(((xy.max(axis=1)>=lower).all(axis=1)&(xy.min(axis=1)<=upper).all(axis=1)))[0]
candidate_polys=np.unique(poly_indices[candidate]);candidate=np.nonzero(np.isin(poly_indices,candidate_polys))[0]
vertices=[tuple(v) for v in local];replacement=[];changed=[];deleted=[];maps={tuple(np.round(points[i],6)):i for i in np.unique(faces[candidate])}
source_material=np.empty(len(old.polygons),dtype=np.int32);old.polygons.foreach_get('material_index',source_material);materials=[]
uv_sources={};uv_new={}
for uv in old.uv_layers:
 raw_uv=np.empty(len(old.loops)*2,dtype=np.float32);uv.data.foreach_get('uv',raw_uv);uv_sources[uv.name]=raw_uv.reshape((-1,2));uv_new[uv.name]=[]
def key(v):return tuple(round(float(x),6) for x in v)
per_polygon={}
for fi in candidate:
 indices=faces[fi];tri=[Vector(points[i,:2]) for i in indices];signed=area(tri)
 if abs(signed)<1e-8:continue
 vs=tri+shaft;edges=[(0,1),(1,2),(2,0)]+[(3+i,3+(i+1)%len(shaft)) for i in range(len(shaft))]
 result=delaunay_2d_cdt(vs,edges,[[0,1,2]],1,1e-7);kept=[]
 for f in result[2]:
  p=[result[0][i] for i in f];centroid=sum(p,Vector((0.,0.)))/len(p)
  if not inside(centroid,tri) or inside(centroid,shaft):continue
  kept.append(p)
 keptarea=sum(abs(area(p)) for p in kept)
 assert keptarea<=abs(signed)+1e-5
 pi=int(poly_indices[fi]);entry=per_polygon.setdefault(pi,{'removed':0.,'faces':[],'uvs':{k:[] for k in uv_sources}})
 entry['removed']+=max(0.,abs(signed)-keptarea)
 p3=points[indices];mat=np.array([[p3[0,0],p3[0,1],1.],[p3[1,0],p3[1,1],1.],[p3[2,0],p3[2,1],1.]])
 plane=np.linalg.solve(mat,p3[:,2])
 for p in kept:
  if area(p)*signed<0:p.reverse()
  ids=[]
  for v in p:
   q=(v.x,v.y,float(plane[0]*v.x+plane[1]*v.y+plane[2]));k=key(q)
   if k not in maps:maps[k]=len(vertices);vertices.append(tuple(back@Vector(q)))
   ids.append(maps[k])
  triangles=[(0,1,2)] if len(ids)==3 else [(0,j,j+1) for j in range(1,len(ids)-1)]
  for indices_in_polygon in triangles:
   entry['faces'].append(tuple(ids[j] for j in indices_in_polygon))
   for key_uv,values in uv_sources.items():
    planes_uv=np.linalg.solve(mat,values[tri_loops[fi]])
    entry['uvs'][key_uv].extend(tuple(np.array([p[j].x,p[j].y,1.])@planes_uv) for j in indices_in_polygon)
for pi,entry in per_polygon.items():
 if entry['removed']<1e-6:continue
 changed.append(pi);deleted.append(entry['removed']);replacement.extend(entry['faces']);materials.extend([int(source_material[pi])]*len(entry['faces']))
 for key_uv in uv_sources:uv_new[key_uv].extend(entry['uvs'][key_uv])
assert changed and sum(deleted)>5 and sum(deleted)<25,(len(changed),sum(deleted))
mask=np.ones(len(old.polygons),dtype=bool);mask[changed]=False
keptfaces=[loops[start:start+total].tolist() for i,(start,total) in enumerate(zip(starts,totals)) if mask[i]];newfaces=keptfaces+replacement
mesh=bpy.data.meshes.new('B102 | terreno com recorte documental do núcleo antigo');mesh.from_pydata(vertices,[],newfaces);mesh.update()
for mat in old.materials:mesh.materials.append(mat)
newmat=np.r_[source_material[mask],materials].astype(np.int32);mesh.polygons.foreach_set('material_index',newmat)
loop_mask=np.repeat(mask,totals)
for key_uv,values in uv_sources.items():
 uv=mesh.uv_layers.new(name=key_uv);all_uv=np.vstack((values[loop_mask],np.array(uv_new[key_uv]))).astype(np.float32);uv.data.foreach_set('uv',all_uv.ravel())
# Datablock fonte preservado sem objeto/collider físico duplicado.
old.use_fake_user=True;terrain.data=mesh;terrain['boas_source_mesh_before_b102']=old.name
terrain['boas_local_excavation_control']='SUCOP17 old_core inset da casca existente, seção23';terrain['boas_local_excavation_status']='GAMEPLAY_PROXY_REPLACE_BEFORE_RELEASE'
terrain['boas_local_excavation_evidence']='docs/reports/blender/lacerda-exterior-b102/excavation.json'
exc={'source_object':terrain.name,'source_file':r['parent_file'],'source_signature':r['terrain_signature'],
 'after_signature':sig(terrain),'footprint_local':[list(p) for p in shaft],'source':'SUCOP17 núcleo hachurado/ seção23 poço; origem da casca B88',
 'status':'ADAPT_LOCAL_DOCUMENT_CORE_EXCAVATION','accuracy':'APPROXIMATE_EXISTING_WALL_SECTION','replacement_required':True,
 'changed_source_triangles':changed,'removed_surface_area_xy_m2':sum(deleted),'reconstructed_triangles':len(replacement),
 'unchanged_source_faces':int(mask.sum()),'unchanged_source_vertex_coordinates':len(old.vertices),
 'method':'Recorte local CDT; Z de cada novo vértice por interpolação na mesma face fonte. Nenhuma alteração de DEM, escala, datum ou coordenada fora do recorte.',
 'not_cabin_envelope_driven':True,'production_ready':False}
(out/'excavation.json').write_text(json.dumps(exc,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
r['changes'].append({'object':terrain.name,'before':r['terrain_signature'],'after':{'signature':sig(terrain)},'reason':exc['source']})
del r['preserved_signatures'][terrain.name];r['terrain_after_signature']=sig(terrain);r['clearance_reconciled']=True
for row in r['added']:row['after']['signature']=sig(bpy.context.scene.objects[row['object']])
(out/'application.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
cp.write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'terrain_triangles_cut':len(changed),'area_xy_removed':sum(deleted),'unchanged_faces':int(mask.sum()),'no_dem_or_ssot_change':True}))
