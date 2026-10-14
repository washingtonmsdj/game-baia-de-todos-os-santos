"""Conferência B71 reaberta; metadados de acesso das vias em revisão."""
import bpy,bmesh,json,hashlib,runpy,numpy as np,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
cp=r/'world/areas/mvp-centro-lacerda/blender-revisions.json';cat=json.loads(cp.read_text(encoding='utf8'));src=cat['validation_source']
assert src['revision']=='R30B.71' and Path(bpy.data.filepath).resolve()==(r/src['file']).resolve()
assert hashlib.sha256((r/src['file']).read_bytes()).hexdigest()==src['sha256']
opened=json.loads((r/'artifacts/blender-sessions/last-open.json').read_text(encoding='utf8'));assert opened['load_post_completed'] and opened['sha256']==src['sha256']
rp=r/'docs/reports/blender/north_junction_r30b71.json';report=json.loads(rp.read_text(encoding='utf8'))
sig=runpy.run_path(str(r/'automation/blender/component_fingerprint.py'))['signature']
changed=[n for n,old in report['protected_signatures'].items() if sig(s.objects[n])!=old];assert not changed
data=np.load(r/'artifacts/waterfront/north_junction_b71.npz');qa=[];coords={}
for key,name in [('fill','B63 | VISUAL | piso contínuo até o cais'),('quay','CAIS | contenção costeira alinhada à linha de costa')]:
 ob=s.objects[name];me=ob.data;col=s.objects[ob['boas_collision_partner']]
 assert sig(ob)==sig(col)==report['modified_after'][name]
 xyz=np.array([list(v.co) for v in me.vertices],float);coords[key]=xyz
 assert np.array_equal(xyz[:,:2],data[key+'_xyz'][:,:2])
 assert np.array_equal(xyz[:,2],data[key+'_z'].astype(np.float32).astype(float))
 assert len(me.vertices)==report['modified_before'][name]['vertices'] and len(me.polygons)==report['modified_before'][name]['polygons']
 me.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(me)
 row={'object':name,'degenerate_triangles':sum(t.area<1e-9 for t in me.loop_triangles),'edges_more_than_two_faces':sum(len(e.link_faces)>2 for e in bm.edges),'boundary_edges':sum(e.is_boundary for e in bm.edges),'finite':bool(np.isfinite(xyz).all()),'visual_collision_identical':True,'xy_changed':False,'topology_changed':False}
 bm.free();assert row['degenerate_triangles']==0 and row['edges_more_than_two_faces']==0 and row['finite'];qa.append(row)
core=s.objects['MVP | terreno corrigido | colisão estática'];control=core.matrix_world@core.data.vertices[report['candidate']['control_core_vertex']].co
assert np.linalg.norm(coords['fill'][1541]-np.array(control))<1e-4
bindings=[]
for b in report['candidate']['bindings']:
 if b['control']=='core_boundary':z=control.z
 else:
  a,c=b['edge'];t=b['edge_t'];z=coords['quay'][a,2]*(1-t)+coords['quay'][c,2]*t
 bindings.append(abs(coords['fill'][b['fill_vertex'],2]-z))
assert max(bindings)<1e-5
fill=s.objects['B63 | VISUAL | piso contínuo até o cais'];ff=np.array([list(t.vertices) for t in fill.data.loop_triangles],int);p=coords['fill'][ff];n=np.cross(p[:,1]-p[:,0],p[:,2]-p[:,0]);g=np.linalg.norm(n[:,:2],axis=1)/np.maximum(abs(n[:,2]),1e-10)
floor={'triangles':len(ff),'above_200percent':int(np.count_nonzero(g>2)),'maximum_grade':float(g.max()),'p95_grade':float(np.percentile(g,95)),'below_nominal_water':int(np.count_nonzero(coords['fill'][:,2]<.35))}
assert floor['above_200percent']==0 and floor['maximum_grade']<.65 and floor['below_nominal_water']==0
bottom=data['quay_xyz'][:,2]<=.351;assert np.array_equal(coords['quay'][bottom],data['quay_xyz'][bottom])
out={'schema':'boas/north-junction-b71-validation-v1','source':report['source_after'],'source_reopened':True,'local_geometry_checks_passed':True,'protected_changes':changed,'mesh_qa':qa,'floor':floor,'north_bindings':len(bindings),'north_max_height_difference_m':max(bindings),'core_corner_distance_m':float(np.linalg.norm(coords['fill'][1541]-np.array(control))),'quay_bottom_preserved':True,'real_altimetry_verified':False,'gameplay_approved':False,'runtime_exported':False}
vp=r/'docs/reports/blender/north_junction_r30b71_validation.json';vp.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
report['source_reopened']=True;report['validation_evidence']=vp.relative_to(r).as_posix();rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
for e in [cat['validation_source']]+cat['revisions']:
 if e['file']==src['file']:e.update(source_reopened=True,validation_evidence=vp.relative_to(r).as_posix(),local_geometry_checks_passed=True)
cp.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
# Fonte OSM: estas três vias são privadas; não promover a trajetos públicos/ônibus.
ref=json.loads((r/'artifacts/structural-pipeline/mvp-centro-lacerda/structural_reference.json').read_text(encoding='utf8'))
features=[f for f in ref['features'] if f['layer']=='roads' and f['osm_id'] in [778284292,1004133492,1004133493,1004133494]]
trees=[]
for name in ['MVP | terreno corrigido | colisão estática','B62 | GAMEPLAY TERRAIN HQ | pavimento e costura limpa','B63 | VISUAL | piso contínuo até o cais']:
 ob=s.objects[name];ob.data.calc_loop_triangles();triangles=list(ob.data.loop_triangles)
 tr=BVHTree.FromPolygons([ob.matrix_world@v.co for v in ob.data.vertices],[list(t.vertices) for t in triangles],all_triangles=True)
 trees.append((ob,tr,triangles))
roads=[]
for f in features:
 samples=[];points=f['blender_xy']
 for a,b in zip(points,points[1:]):
  a=np.array(a);b=np.array(b);length=np.linalg.norm(b-a)
  for k in range(max(1,math.ceil(length))):
   xy=a+(b-a)*k/max(1,math.ceil(length))
   if not (-560<=xy[0]<=60 and -110<=xy[1]<=620):continue
   hits=[]
   for ob,tr,triangles in trees:
    hit,normal,index,distance=tr.ray_cast(Vector((float(xy[0]),float(xy[1]),150)),Vector((0,0,-1)),300)
    if hit is not None:
     polygon=ob.data.polygons[triangles[index].polygon_index];role=ob.data.attributes.get('boas_surface_role')
     hits.append({'z':hit.z,'object':ob.name,'material_index':polygon.material_index,'surface_role':role.data[polygon.index].value if role else None})
   support=max(hits,key=lambda h:h['z']) if hits else None
   samples.append({'xy':xy.tolist(),'support':support})
 roads.append({'osm_id':f['osm_id'],'tags':f['tags'],'real_width_m':f['metrics'].get('width_m_tagged'),'source_node_refs':f['node_refs'],'classification':'KEEP_REAL_REFERENCE','access_classification':'private' if f['tags'].get('access')=='private' else 'NEEDS_REVIEW','bus_route_approved':False,'axis_samples_1m':samples,'missing_ground_samples':sum(x['support'] is None for x in samples),'sampled_geometry_only':True})
roadout={'schema':'boas/coastal-service-roads-b71-review-v1','source':report['source_after'],'reference':'artifacts/structural-pipeline/mvp-centro-lacerda/structural_reference.json','roads':roads,'geometry_changed':False,'limitations':['Amostragem de eixo não prova largura/ligação/four wheels','Vias privadas não são automaticamente corredores públicos/ônibus','Limites/licença de tráfego sem informação permanecem pendentes'],'approved':False}
(r/'docs/reports/blender/coastal_service_roads_b71_review.json').write_text(json.dumps(roadout,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'floor':floor,'north_max_height_difference_m':max(bindings),'roads':[{k:v for k,v in row.items() if k!='axis_samples_1m'} for row in roads]}))
