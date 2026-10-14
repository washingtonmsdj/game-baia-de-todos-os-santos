"""B68: inspecionar contatos costeiros e enquadrar a revisão na única janela."""
import bpy,json,math,numpy as np,shutil
from pathlib import Path
from collections import Counter
from mathutils import Vector,Euler
from mathutils.bvhtree import BVHTree
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
cat=json.loads((r/'world/areas/mvp-centro-lacerda/blender-revisions.json').read_text(encoding='utf-8'))
src=cat['validation_source'];assert src['revision']=='R30B.67' and Path(bpy.data.filepath).resolve()==(r/src['file']).resolve()
features=json.loads((r/'docs/reports/blender/coastal_osm_source_check.json').read_text(encoding='utf-8'))['features']
water=s.objects['BAÍA DE TODOS-OS-SANTOS | superfície e recorte costeiro'];wv=[water.matrix_world@v.co for v in water.data.vertices];water.data.calc_loop_triangles()
wt=BVHTree.FromPolygons(wv,[list(t.vertices) for t in water.data.loop_triangles],all_triangles=True)
ec=Counter(tuple(sorted((a,b))) for f in water.data.polygons for a,b in zip(list(f.vertices),list(f.vertices)[1:]+list(f.vertices)[:1]))
xmin=min(v.x for v in wv);ymin=min(v.y for v in wv);ymax=max(v.y for v in wv)
shore=[]
def wet(p):return wt.ray_cast(Vector((p.x,p.y,100)),Vector((0,0,-1)),200)[0] is not None
for (a,b),n in ec.items():
 if n!=1:continue
 p,q=wv[a],wv[b]
 if (abs(p.x-xmin)<1e-5 and abs(q.x-xmin)<1e-5) or (abs(p.y-ymin)<1e-5 and abs(q.y-ymin)<1e-5) or (abs(p.y-ymax)<1e-5 and abs(q.y-ymax)<1e-5):continue
 d=q-p;normal=Vector((-d.y,d.x,0)).normalized()
 if wet((p+q)/2+normal*.1):normal=-normal
 shore.append((p,q,normal))
def near(p):
 result=[]
 for a,b,n in shore:
  d=b-a;t=max(0,min(1,(p-a).dot(d)/d.length_squared));c=a+d*t
  result.append(((p-c).length,c,n))
 return min(result,key=lambda row:row[0])
trees=[]
names=['MVP | terreno corrigido | colisão estática','B62 | GAMEPLAY TERRAIN HQ | pavimento e costura limpa','B63 | VISUAL | piso contínuo até o cais']
for name in names:
 ob=s.objects[name];me=ob.data;me.calc_loop_triangles()
 a=np.empty((len(me.vertices),3),np.float32);me.vertices.foreach_get('co',a.ravel());mw=np.array(ob.matrix_world);a=a@mw[:3,:3].T+mw[:3,3]
 t=np.empty((len(me.loop_triangles),3),np.int32);me.loop_triangles.foreach_get('vertices',t.ravel())
 tr=a[t];mask=(tr[:,:,0].max(axis=1)>-520)&(tr[:,:,0].min(axis=1)<-350)&(tr[:,:,1].max(axis=1)>-250)&(tr[:,:,1].min(axis=1)<-100)
 ids=np.flatnonzero(mask);t=t[mask];ind=np.unique(t);remap=np.full(len(a),-1,np.int32);remap[ind]=np.arange(len(ind))
 if len(t):trees.append((ob,BVHTree.FromPolygons(a[ind].tolist(),remap[t].tolist(),all_triangles=True),ids))
def floor(p):
 hits=[]
 for ob,tr,ids in trees:
  h,normal,index,distance=tr.ray_cast(Vector((p.x,p.y,150)),Vector((0,0,-1)),300)
  if h is not None:
   face=ob.data.polygons[ob.data.loop_triangles[int(ids[index])].polygon_index];mat=ob.data.materials[face.material_index]
   hits.append({'object':ob.name,'z':float(h.z),'normal':list(normal),'material':mat.name if mat else None})
 return sorted(hits,key=lambda h:h['z'],reverse=True)
rows=[]
for f in features:
 if f['osm_id'] not in (609043799,609043801):continue
 points=[Vector((x,y,.35)) for x,y in f['blender_xy'][:-1]]
 edges=[]
 for i,p in enumerate(points):
  q=points[(i+1)%len(points)];samples=[]
  for t in (0,.25,.5,.75,1):
   pos=p.lerp(q,t);dist,c,n=near(pos);samples.append({'t':t,'gap_xy':math.hypot(pos.x-c.x,pos.y-c.y),'shore_xy':[c.x,c.y],'land_normal_xy':[n.x,n.y],'supports':[{'inset':inset,'xy':[c.x+n.x*inset,c.y+n.y*inset],'hits':floor(c+n*inset)} for inset in (.03,.25,.5,1.0)]})
  edges.append({'edge':i,'start_xy':[p.x,p.y],'end_xy':[q.x,q.y],'length_xy':(q-p).length,'max_gap_xy':max(v['gap_xy'] for v in samples),'samples':samples})
 rows.append({'osm_id':f['osm_id'],'edges':edges})
report={'schema':'boas/pier-shore-contact-b68-probe-v1','source':src,'features':rows,'geometry_changed':False,'height_surveyed':False}
(r/'docs/reports/blender/pier_shore_contacts_b68_probe.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for win in bpy.context.window_manager.windows:
 for ar in win.screen.areas:
  if ar.type=='VIEW_3D':
   sp=ar.spaces.active;sp.shading.type='SOLID';sp.shading.color_type='MATERIAL';sp.overlay.show_extras=False
   sp.region_3d.view_location=Vector((-435,-171,3));sp.region_3d.view_distance=105
   sp.region_3d.view_rotation=Euler((math.radians(60),0,math.radians(38)),'XYZ').to_quaternion();sp.region_3d.view_perspective='ORTHO'
bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP',iterations=2)
folder=r/'artifacts/waterfront';folder.mkdir(parents=True,exist_ok=True)
bpy.ops.screen.screenshot(filepath=str(folder/'b67-new-piers-before.png'))
print(json.dumps({'features':len(rows),'free':shutil.disk_usage(r).free}))
