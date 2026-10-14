"""Diagnóstico B72 da divisão física e dos traçados OSM; nenhuma mutação."""
import bpy,json,numpy as np,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
src=json.loads((r/'world/areas/mvp-centro-lacerda/blender-revisions.json').read_text(encoding='utf8'))['validation_source'];assert src['revision']=='R30B.71'
names=['MVP | terreno corrigido | colisão estática','B62 | GAMEPLAY TERRAIN HQ | pavimento e costura limpa','B63 | VISUAL | piso contínuo até o cais'];rows=[];trees=[]
for name in names:
 ob=s.objects[name];me=ob.data;me.calc_loop_triangles();xyz=np.array([list(ob.matrix_world@v.co) for v in me.vertices],float);tris=list(me.loop_triangles)
 tree=BVHTree.FromPolygons([Vector(p) for p in xyz],[list(t.vertices) for t in tris],all_triangles=True)
 trees.append((ob,tree,tris));rows.append({'object':name,'bounds':[xyz.min(axis=0).tolist(),xyz.max(axis=0).tolist()],'attributes':[a.name for a in me.attributes],'materials':[m.name if m else None for m in me.materials],'hidden':ob.hide_viewport,'collections':[c.name for c in ob.users_collection]})
def sample(xy):
 hits=[]
 for ob,tr,tris in trees:
  p,n,index,d=tr.ray_cast(Vector((float(xy[0]),float(xy[1]),150)),Vector((0,0,-1)),300)
  if p is not None:
   poly=ob.data.polygons[tris[index].polygon_index];ids=ob.data.attributes.get('boas_osm_way_id');role=ob.data.attributes.get('boas_surface_role')
   hits.append({'object':ob.name,'z':p.z,'material':poly.material_index,'way_id':ids.data[poly.index].value if ids else None,'surface_role':role.data[poly.index].value if role else None})
 return hits
seam=json.loads((r/'docs/reports/blender/coastal_seam_r30b58.json').read_text(encoding='utf8'))['physical_boundary_xy']
ref=json.loads((r/'artifacts/structural-pipeline/mvp-centro-lacerda/structural_reference.json').read_text(encoding='utf8'))
crossings=[]
for f in ref['features']:
 if f['layer']!='roads':continue
 for a,b in zip(f['blender_xy'],f['blender_xy'][1:]):
  a=np.array(a);b=np.array(b);d=b-a;length=np.linalg.norm(d)
  if length<1e-8:continue
  for axis,key in [(0,'x'),(1,'y')]:
   if abs(d[axis])<1e-9:continue
   t=(seam[key]-a[axis])/d[axis]
   if not 0<=t<=1:continue
   p=a+d*t
   if axis==0 and p[1]<seam['y']:continue
   if axis==1 and p[0]<seam['x']:continue
   tangent=d/length;normal=np.array([-tangent[1],tangent[0]])
   probes=[]
   for offset in [-5,-2,-.25,.25,2,5]:
    xy=p+tangent*offset;probes.append({'offset_along_axis_m':offset,'xy':xy.tolist(),'surfaces':sample(xy)})
   crossings.append({'osm_id':f['osm_id'],'tags':f['tags'],'source_width_m':f['metrics'].get('width_m_tagged'),'crossing_xy':p.tolist(),'boundary_axis':key,'tangent':tangent.tolist(),'normal':normal.tolist(),'probes':probes})
out={'schema':'boas/coastal-city-seam-b72-v1','source':src,'physical_boundary_xy':seam,'objects':rows,'crossings':crossings,'geometry_changed':False,'geographic_fit_status':ref['fit_status'],'geographic_fit_summary':ref['fit_summary']}
(r/'docs/reports/blender/coastal_city_seam_b72_probe.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'objects':rows,'crossings':len(crossings)}))
