"""Somente leitura: apoios locais dos novos contornos OSM."""
import bpy,json,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
r=Path(__file__).resolve().parents[2];sc=bpy.context.scene
assert Path(bpy.data.filepath).name=='salvador_lacerda_r30b66_cais_normais_corrigidas.blend'
data=json.loads((r/'docs/reports/blender/coastal_osm_source_check.json').read_text(encoding='utf-8-sig'))
water=sc.objects['BAÍA DE TODOS-OS-SANTOS | superfície e recorte costeiro'];water.data.calc_loop_triangles()
wt=BVHTree.FromPolygons([water.matrix_world@v.co for v in water.data.vertices],[list(t.vertices) for t in water.data.loop_triangles],all_triangles=True)
hq=sc.objects['B62 | GAMEPLAY TERRAIN HQ | pavimento e costura limpa'];me=hq.data;me.calc_loop_triangles()
a=np.empty((len(me.vertices),3),np.float32);me.vertices.foreach_get('co',a.ravel());mw=np.array(hq.matrix_world);a=a@mw[:3,:3].T+mw[:3,3]
t=np.empty((len(me.loop_triangles),3),np.int32);me.loop_triangles.foreach_get('vertices',t.ravel())
cx=sum(a[t[:,i],0] for i in range(3))/3;cy=sum(a[t[:,i],1] for i in range(3))/3
t=t[(cx>-520)&(cx<-350)&(cy>-250)&(cy<-100)]
ids=np.unique(t);idx=np.full(len(a),-1,np.int32);idx[ids]=np.arange(len(ids));gt=BVHTree.FromPolygons(a[ids].tolist(),idx[t].tolist(),all_triangles=True)
def sample(x,y):
 p=gt.ray_cast(Vector((x,y,150)),Vector((0,0,-1)),300)[0];w=wt.ray_cast(Vector((x,y,150)),Vector((0,0,-1)),300)[0]
 return {'xy':[x,y],'floor_z':p.z if p else None,'water':w is not None}
rows=[]
for f in data['features']:
 if f['osm_id'] not in (609043799,609043801):continue
 corners=[sample(x,y) for x,y in f['blender_xy'][:-1]];near=[]
 for c in corners:
  x,y=c['xy']
  for dx,dy in ((0,0),(1,0),(-1,0),(0,1),(0,-1),(3,0),(-3,0),(0,3),(0,-3)):
   z=sample(x+dx,y+dy)
   if not z['water'] and z['floor_z'] is not None:near.append(z)
 rows.append({'osm_id':f['osm_id'],'corners':corners,'near_land_controls':near})
out={'schema':'boas/pier-land-contacts-b67-probe-v1','source':'blender/salvador_lacerda_r30b66_cais_normais_corrigidas.blend','source_check':'docs/reports/blender/coastal_osm_source_check.json','features':rows,'geometry_changed':False,'height_surveyed':False}
(r/'docs/reports/blender/pier_land_contacts_b67_probe.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(rows))
