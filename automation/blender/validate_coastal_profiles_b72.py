"""B72: perfis de apoio das vias costeiras e encontros das malhas atuais."""
import bpy,json,hashlib,numpy as np,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
src=json.loads((r/'world/areas/mvp-centro-lacerda/blender-revisions.json').read_text(encoding='utf8'))['validation_source']
assert src['revision']=='R30B.72' and Path(bpy.data.filepath).resolve()==(r/src['file']).resolve()
assert hashlib.sha256((r/src['file']).read_bytes()).hexdigest()==src['sha256']
names=['MVP | terreno corrigido | colisão estática','B62 | GAMEPLAY TERRAIN HQ | pavimento e costura limpa','B63 | VISUAL | piso contínuo até o cais'];trees=[]
for name in names:
 ob=s.objects[name];ob.data.calc_loop_triangles();triangles=list(ob.data.loop_triangles)
 tree=BVHTree.FromPolygons([ob.matrix_world@v.co for v in ob.data.vertices],[list(t.vertices) for t in triangles],all_triangles=True)
 trees.append((ob,tree,triangles))
def support(xy):
 hits=[]
 for ob,tree,tris in trees:
  p,n,index,d=tree.ray_cast(Vector((float(xy[0]),float(xy[1]),150)),Vector((0,0,-1)),300)
  if p is not None:
   polygon=ob.data.polygons[tris[index].polygon_index];role=ob.data.attributes.get('boas_surface_role')
   hits.append({'z':float(p.z),'object':ob.name,'triangle':index,'material':polygon.material_index,'role':role.data[polygon.index].value if role else None,'material_name':ob.data.materials[polygon.material_index].name,'osm_way_id':ob.data.attributes['boas_osm_way_id'].data[polygon.index].value if ob.data.attributes.get('boas_osm_way_id') else None})
 return max(hits,key=lambda x:x['z']) if hits else None
contract=json.loads((r/'world/areas/mvp-centro-lacerda/coastal-gameplay-b51.json').read_text(encoding='utf8'))
rows=[]
for rec in contract['roads']:
 if rec['role']!='road_driveable':continue
 samples=[];station=0
 for a,b in zip(rec['blender_xy'],rec['blender_xy'][1:]):
  a=np.array(a);b=np.array(b);d=b-a;length=float(np.linalg.norm(d))
  if length<1e-8:continue
  normal=np.array([-d[1],d[0]])/length;count=max(1,math.ceil(length/.5))
  for k in range(count):
   xy=a+d*k/count
   center=support(xy)
   if not (-560<=xy[0]<=60 and -700<=xy[1]<=620):continue
   left=support(xy-normal*.825);right=support(xy+normal*.825)
   samples.append({'station':station+k*length/count,'xy':xy.tolist(),'center':center,'left':left,'right':right,'crossfall':abs(left['z']-right['z'])/1.65 if left and right else None})
  station+=length
 pairs=[]
 for a,b in zip(samples,samples[1:]):
  if a['center'] is None or b['center'] is None:continue
  distance=math.dist(a['xy'],b['xy'])
  if distance>1 or distance<1e-8:continue
  delta=b['center']['z']-a['center']['z'];grade=abs(delta)/distance
  pairs.append({'from_xy':a['xy'],'to_xy':b['xy'],'from':a['center'],'to':b['center'],'grade':grade,'delta_z_m':delta,'distance_m':distance,'object_transition':a['center']['object']!=b['center']['object']})
 rows.append({'osm_way_id':rec['osm_way_id'],'name':rec['name'],'existing_gameplay_width_m':rec['gameplay_width_m'],'width_status':rec['gameplay_width_status'],'source_width_m':rec.get('source_width_m'),'samples':samples,'missing_supports':sum(x[k] is None for x in samples for k in ['center','left','right']),'max_grade':max((p['grade'] for p in pairs),default=None),'max_crossfall':max((x['crossfall'] for x in samples if x['crossfall'] is not None),default=None),'worst_pairs':sorted(pairs,key=lambda x:x['grade'],reverse=True)[:6],'transitions':sorted((p for p in pairs if p['object_transition']),key=lambda x:x['grade'],reverse=True)})
out={'schema':'boas/coastal-road-profiles-b72-v1','source':src,'vehicle_probe_track_m':1.65,'probe_spacing_max_m':.5,'roads':rows,'geometry_changed':False,'traffic_approved':False}
(r/'docs/reports/blender/coastal_road_profiles_b72_after.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps([{k:v for k,v in row.items() if k not in ['samples','worst_pairs','transitions']} for row in rows]))
