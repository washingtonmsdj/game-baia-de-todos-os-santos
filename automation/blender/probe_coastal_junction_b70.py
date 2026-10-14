"""B70: diagnóstico de recomposição conjunta terreno/piso usando cais existente."""
import bpy,json,math,numpy as np
from pathlib import Path
from collections import Counter,defaultdict
from mathutils import Vector
from mathutils.bvhtree import BVHTree
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
src=json.loads((r/'world/areas/mvp-centro-lacerda/blender-revisions.json').read_text(encoding='utf8'))['validation_source'];assert src['revision']=='R30B.69'
hq=s.objects['B62 | GAMEPLAY TERRAIN HQ | pavimento e costura limpa'];fill=s.objects['B63 | VISUAL | piso contínuo até o cais'];quay=s.objects['CAIS | contenção costeira alinhada à linha de costa']
hx=np.array([list(v.co) for v in hq.data.vertices],dtype=float);fx=np.array([list(v.co) for v in fill.data.vertices],dtype=float)
locked=set();roles=hq.data.attributes.get('boas_surface_role')
for p in hq.data.polygons:
 if roles and roles.data[p.index].value in (1,2):locked.update(p.vertices)
qe=[]
for e in quay.data.edges:
 a,b=[quay.matrix_world@quay.data.vertices[i].co for i in e.vertices]
 if a.z>.351 and b.z>.351 and max(a.x,b.x)>=fx[:,0].min()-30 and min(a.x,b.x)<=fx[:,0].max()+30 and max(a.y,b.y)>=fx[:,1].min()-30 and min(a.y,b.y)<=fx[:,1].max()+30:qe.append((np.array(a),np.array(b)))
sel=np.where((hx[:,0]>=fx[:,0].min()-30)&(hx[:,0]<=fx[:,0].max())&(hx[:,1]>=fx[:,1].min()-30)&(hx[:,1]<=fx[:,1].max()))[0]
best=np.full(len(sel),np.inf);target=np.zeros(len(sel))
for a,b in qe:
 d=b[:2]-a[:2];ll=float(d@d)
 if ll<1e-10:continue
 t=np.clip(((hx[sel,:2]-a[:2])@d)/ll,0,1);distance=np.linalg.norm(hx[sel,:2]-a[:2]-t[:,None]*d,axis=1);better=distance<best
 best[better]=distance[better];target[better]=a[2]+t[better]*(b[2]-a[2])
u=np.clip((best-2)/28,0,1);w=1-3*u*u+2*u*u*u;hz=hx[:,2].copy()
for index,weight,height in zip(sel,w,target):
 if index not in locked and weight>0:hz[index]=hx[index,2]+weight*(height-hx[index,2])
hq.data.calc_loop_triangles();hfaces=np.array([list(t.vertices) for t in hq.data.loop_triangles]);changed=abs(hz-hx[:,2])>1e-5;changed_faces=np.any(changed[hfaces],axis=1)
hv=hx.copy();hv[:,2]=hz;tree=BVHTree.FromPolygons([Vector(p) for p in hv],[list(map(int,f)) for f in hfaces],all_triangles=True)
fill.data.calc_loop_triangles();ff=np.array([list(t.vertices) for t in fill.data.loop_triangles]);ec=Counter(tuple(sorted((int(a),int(b)))) for f in ff for a,b in zip(f,np.roll(f,-1)))
boundary=sorted({i for e,count in ec.items() if count==1 for i in e});fixed=set(boundary);fz=fx[:,2].copy();boundary_changed=[]
loop_edges=np.empty(len(hq.data.loops),dtype=np.int32);hq.data.loops.foreach_get('edge_index',loop_edges)
edge_counts=np.bincount(loop_edges,minlength=len(hq.data.edges));he=np.array([list(e.vertices) for e in hq.data.edges],dtype=int)[edge_counts==1]
ea=hx[he[:,0],:2];eb=hx[he[:,1],:2];d=eb-ea;ll=np.sum(d*d,axis=1);valid=ll>1e-12;ea=ea[valid];eb=eb[valid];he=he[valid];d=d[valid];ll=ll[valid]
boundary_binding=[]
for i in boundary:
 x,y,z=fx[i]
 t=np.clip(np.sum((fx[i,:2]-ea)*d,axis=1)/ll,0,1);dist=np.linalg.norm(fx[i,:2]-ea-t[:,None]*d,axis=1);j=int(np.argmin(dist))
 if dist[j]<.003:
  height=hz[he[j,0]]*(1-t[j])+hz[he[j,1]]*t[j];fz[i]=height
  boundary_binding.append({'fill_vertex':int(i),'hq_edge':list(map(int,he[j])),'edge_t':float(t[j]),'xy_distance_m':float(dist[j]),'height_candidate':float(height)})
  if abs(height-z)>1e-5:boundary_changed.append(i)
free=[i for i in range(len(fx)) if i not in fixed];mapping={i:j for j,i in enumerate(free)};weights=defaultdict(float);xy=fx[:,:2]-fx[:,:2].mean(axis=0)
for f in ff:
 for k in range(3):
  a,b,c=map(int,(f[k],f[(k+1)%3],f[(k+2)%3]));p=xy[a]-xy[c];q=xy[b]-xy[c];area=abs(p[0]*q[1]-p[1]*q[0])
  if area>1e-10:weights[tuple(sorted((a,b)))]+=.5*float(p@q)/area
A=np.zeros((len(free),len(free)));rhs=np.zeros(len(free))
for (a,b),weight in weights.items():
 for i,j in ((a,b),(b,a)):
  if i in fixed:continue
  row=mapping[i];A[row,row]+=weight
  if j in fixed:rhs[row]+=weight*fz[j]
  else:A[row,mapping[j]]-=weight
fz[free]=np.linalg.solve(A,rhs)
def stats(xyz,z,faces):
 p=xyz[faces].copy();p[:,:,2]=z[faces];n=np.cross(p[:,1]-p[:,0],p[:,2]-p[:,0]);g=np.sqrt(n[:,0]**2+n[:,1]**2)/np.maximum(abs(n[:,2]),1e-10)
 return {'faces':len(faces),'grade_over_200percent':int(np.count_nonzero(g>2)),'grade_max':float(g.max()),'grade_p95':float(np.percentile(g,95))}
p=fx[ff].copy();p[:,:,2]=fz[ff];nn=np.cross(p[:,1]-p[:,0],p[:,2]-p[:,0]);gg=np.sqrt(nn[:,0]**2+nn[:,1]**2)/np.maximum(abs(nn[:,2]),1e-10)
worst=[{'triangle':int(i),'indices':list(map(int,ff[i])),'points':p[i].tolist(),'boundary_flags':[int(v) in fixed for v in ff[i]],'grade':float(gg[i])} for i in np.where(gg>2)[0]]
out={'worst_remaining_triangles':worst,'schema':'boas/coastal-junction-b70-probe-v1','source':src,'classification':'ADAPT_LOCAL','method':'local_2m_quay_contact_plus_fade_to_30m; roads/walkable_vertices_locked; interior_floor_parameterized','real_collar_width_m':None,'design_collar_limit_m':30,'design_quay_contact_band_m':2,'quay_control_edges':len(qe),'hq_changed_vertices':int(changed.sum()),'hq_max_z_change_m':float(abs(hz-hx[:,2]).max()),'road_locked_vertices':len(locked),'road_locked_max_change_m':float(abs(hz[list(locked)]-hx[list(locked),2]).max()),'boundary_binding':boundary_binding,'boundary_changed_vertices':len(boundary_changed),'floor_below_water_before':int(np.count_nonzero(fx[:,2]<.35)),'floor_below_water_after':int(np.count_nonzero(fz<.35)),'hq_before':stats(hx,hx[:,2],hfaces[changed_faces]),'hq_after':stats(hx,hz,hfaces[changed_faces]),'floor_before':stats(fx,fx[:,2],ff),'floor_after':stats(fx,fz,ff),'finite':bool(np.isfinite(hz).all() and np.isfinite(fz).all()),'quay_and_source_xy_changed':False,'source_changed':False,'real_altimetry_verified':False}
(r/'docs/reports/blender/coastal_junction_b70_probe.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
np.savez_compressed(r/'artifacts/waterfront/coastal_junction_b70.npz',hq_xyz=hx,hq_z=hz,fill_xyz=fx,fill_z=fz,locked=np.array(sorted(locked)),boundary=np.array(boundary))
print(json.dumps(out))
