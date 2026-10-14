"""B71: ensaio sem mutação do encontro norte; terreno existente como controle."""
import bpy,json,hashlib,numpy as np
from pathlib import Path
from collections import Counter,defaultdict
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
src=json.loads((r/'world/areas/mvp-centro-lacerda/blender-revisions.json').read_text(encoding='utf8'))['validation_source']
assert src['revision']=='R30B.70' and Path(bpy.data.filepath).resolve()==(r/src['file']).resolve()
fill=s.objects['B63 | VISUAL | piso contínuo até o cais'];quay=s.objects['CAIS | contenção costeira alinhada à linha de costa'];core=s.objects['MVP | terreno corrigido | colisão estática']
fx=np.array([list(v.co) for v in fill.data.vertices],float);qx=np.array([list(v.co) for v in quay.data.vertices],float);cx=np.array([list(core.matrix_world@v.co) for v in core.data.vertices],float)
origin=cx[525112];assert np.linalg.norm(origin[:2]-fx[1541,:2])<.0001
zcontrol=float(origin[2]);radius=12.0
def fade(xy):
 d=np.linalg.norm(xy-origin[:2],axis=-1);u=np.clip(d/radius,0,1)
 return 1-3*u*u+2*u*u*u
qz=qx[:,2].copy();mask=(qx[:,2]>.351)&(qx[:,0]<=origin[0])
w=fade(qx[:,:2]);qz[mask]=qx[mask,2]+w[mask]*(zcontrol-qx[mask,2])
fill.data.calc_loop_triangles();ff=np.array([list(t.vertices) for t in fill.data.loop_triangles],int)
ec=Counter(tuple(sorted((int(a),int(b)))) for f in ff for a,b in zip(f,np.roll(f,-1)))
boundary=sorted({i for e,count in ec.items() if count==1 for i in e});fixed=set(boundary);fz=fx[:,2].copy()
qe=np.array([list(e.vertices) for e in quay.data.edges if all(qx[i,2]>.351 for i in e.vertices)],int)
ea=qx[qe[:,0],:2];d=qx[qe[:,1],:2]-ea;ll=np.sum(d*d,axis=1);valid=ll>1e-12;ea=ea[valid];d=d[valid];ll=ll[valid];qe=qe[valid]
bindings=[]
for i in boundary:
 if np.linalg.norm(fx[i,:2]-origin[:2])>radius:continue
 if abs(fx[i,0]-origin[0])<1e-4:
  fz[i]=zcontrol;bindings.append({'fill_vertex':int(i),'control':'core_boundary','height':zcontrol})
 else:
  t=np.clip(np.sum((fx[i,:2]-ea)*d,axis=1)/ll,0,1);dist=np.linalg.norm(fx[i,:2]-ea-t[:,None]*d,axis=1);j=int(np.argmin(dist))
  if dist[j]<.003:
   fz[i]=qz[qe[j,0]]*(1-t[j])+qz[qe[j,1]]*t[j];bindings.append({'fill_vertex':int(i),'control':'quay_edge','edge':list(map(int,qe[j])),'edge_t':float(t[j]),'distance_xy_m':float(dist[j]),'height':float(fz[i])})
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
def grades(z):
 p=fx[ff].copy();p[:,:,2]=z[ff];n=np.cross(p[:,1]-p[:,0],p[:,2]-p[:,0]);g=np.linalg.norm(n[:,:2],axis=1)/np.maximum(abs(n[:,2]),1e-10)
 return {'above_200percent':int(np.count_nonzero(g>2)),'maximum':float(g.max()),'p95':float(np.percentile(g,95))}
out={'schema':'boas/north-junction-b71-candidate-v1','source':src,'classification':'ADAPT_LOCAL','binding_error_classification':'ERROR','control_core_vertex':525112,'control_xyz':origin.tolist(),'design_transition_radius_m':radius,'real_transition_length_m':None,'real_altimetry_verified':False,'bindings':bindings,'floor_before':grades(fx[:,2]),'floor_after':grades(fz),'floor_below_nominal_water':int(np.count_nonzero(fz<.35)),'floor_changed_vertices':int(np.count_nonzero(abs(fz-fx[:,2])>1e-5)),'quay_changed_vertices':int(np.count_nonzero(abs(qz-qx[:,2])>1e-5)),'quay_max_z_change_m':float(abs(qz-qx[:,2]).max()),'floor_max_z_change_m':float(abs(fz-fx[:,2]).max()),'finite':bool(np.isfinite(fz).all() and np.isfinite(qz).all()),'geometry_changed':False}
np.savez_compressed(r/'artifacts/waterfront/north_junction_b71.npz',fill_xyz=fx,quay_xyz=qx,fill_z=fz,quay_z=qz)
(r/'docs/reports/blender/north_junction_b71_candidate.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in out.items() if k!='bindings'}))
