"""Persistência e relação fonte/collider na B81 visível; sem alteração/salvamento."""
import bpy,json,hashlib,os,runpy
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/reports/blender/cairu-market-b81'
app=json.loads((OUT/'application.json').read_text(encoding='utf8'));source=app['source_after']
assert Path(bpy.data.filepath).resolve()==(ROOT/source['file']).resolve() and not bpy.data.is_dirty
assert os.getpid()==app['pid'] and len(bpy.context.scene.objects)==6296
assert bpy.context.scene['boas_lacerda_vertical_status']=='BLOCKED_EXTERNAL_EVIDENCE'
assert bpy.context.scene['boas_movement_enabled'] is False
sig=runpy.run_path(str(ROOT/'automation/blender/component_fingerprint.py'))['signature']
original=json.loads((ROOT/'artifacts/lacerda-controller/b81_original_signatures.json').read_text(encoding='utf8'))
checked=[]
for name in app['modified_metadata_only']:
 assert sig(bpy.data.objects[name])==original[name],name
 checked.append(name)
curb=bpy.data.objects['B63 | VISUAL | meios-fios das vias existentes'];proxy=bpy.data.objects[app['added_objects'][0]]
dg=bpy.context.evaluated_depsgraph_get();ev=curb.evaluated_get(dg);m=ev.to_mesh()
try:
 m.calc_loop_triangles();v=[ev.matrix_world@x.co for x in m.vertices]
 def key(points):return tuple(sorted(tuple(float(c) for c in p) for p in points))
 source_faces={key([v[i] for i in t.vertices]) for t in m.loop_triangles}
 proxy.data.calc_loop_triangles();pv=[proxy.matrix_world@x.co for x in proxy.data.vertices]
 derived=[key([pv[i] for i in t.vertices]) for t in proxy.data.loop_triangles]
 assert all(t in source_faces for t in derived)
finally:ev.to_mesh_clear()
nav=bpy.data.objects[app['added_objects'][1]];assert not nav['boas_route_enabled'] and not nav['boas_market_entrance_verified']
profile=json.loads((ROOT/'world/areas/mvp-centro-lacerda/cairu-market-pedestrian.json').read_text(encoding='utf8'))
floor_checks=[]
for binding in profile['collision_bindings']:
 if binding['role']!='WALKABLE_FLOOR':continue
 def surfaces(name):
  ob=bpy.data.objects[name];ev=ob.evaluated_get(dg);me=ev.to_mesh()
  try:
   me.calc_loop_triangles();vs=[ev.matrix_world@v.co for v in me.vertices];fs=[tuple(t.vertices) for t in me.loop_triangles]
   return vs,fs,BVHTree.FromPolygons(vs,fs,all_triangles=True)
  finally:ev.to_mesh_clear()
 vs,fs,visual=surfaces(binding['source']);cv,cf,collider=surfaces(binding['object'])
 top=max(p.z for p in vs)+1;residuals=[];missing=0
 probes=list(vs)+[sum((vs[i] for i in f),Vector())/3 for f in fs]
 for p in probes:
  origin=Vector((p.x,p.y,top));a=visual.ray_cast(origin,Vector((0,0,-1)),3)[0];b=collider.ray_cast(origin,Vector((0,0,-1)),3)[0]
  if a is not None:
   if b is None:missing+=1
   else:residuals.append(abs(a.z-b.z))
 maxres=max(residuals,default=None)
 floor_checks.append({'source':binding['source'],'collider':binding['object'],'probes':len(probes),'missing_collider_support':missing,'max_surface_z_residual':maxres,'status':'coincident_sampled_surfaces' if missing==0 and maxres is not None and maxres<1e-5 else 'NEEDS_REVIEW'})
external=json.loads((ROOT/'artifacts/lacerda-controller/external_route_physics_b80.json').read_text(encoding='utf8'))
external['source']={'file':source['file'],'sha256':source['sha256']}
# A fonte visual de meio-fio é substituída somente por seu patch derivado no
# ensaio físico; não remover o obstáculo nem duplicar fonte e collider.
row=next(r for r in external['objects'] if r['name']==curb.name)
external['objects'].remove(row)
row.update({'name':proxy.name,'geometry':{'vertices':[list(p) for p in pv],'triangles':[list(t.vertices) for t in proxy.data.loop_triangles],'complete_mesh':False,'bounds':row['geometry']['bounds']}})
external['objects'].append(row)
(ROOT/'artifacts/lacerda-controller/external_route_physics_b81.json').write_text(json.dumps(external,ensure_ascii=False),encoding='utf8')
with (ROOT/source['file']).open('rb') as f:actual=hashlib.file_digest(f,'sha256').hexdigest()
assert actual==source['sha256']
report={'source':source,'pid':os.getpid(),'reopened_same_window':True,'objects':6296,'checked_original_sources':checked,'floor_collider_comparison':floor_checks,'curb_triangles_faithful':len(derived),'all_derived_triangles_from_source':True,'route_enabled':False,'market_entrance_verified':False,'movement_enabled':False,'LACERDA_VERTICAL':'BLOCKED_EXTERNAL_EVIDENCE','CAIRU_MARKET_PEDESTRIAN':'PARTIAL_ROUTE_APPLIED_BLOCKED','production_exported':False}
(OUT/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'reopened':True,'faithful_curb_triangles':len(derived),'route_enabled':False}))
