"""B70: reconstrução harmônica XY do piso, com todos os controles de fronteira fixos."""
import bpy,json,math,numpy as np,hashlib
from pathlib import Path
from collections import Counter,defaultdict
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
src=json.loads((r/'world/areas/mvp-centro-lacerda/blender-revisions.json').read_text(encoding='utf8'))['validation_source']
assert src['revision']=='R30B.69' and Path(bpy.data.filepath).resolve()==(r/src['file']).resolve()
o=s.objects['B63 | VISUAL | piso contínuo até o cais'];me=o.data;me.calc_loop_triangles()
xyz=np.array([list(v.co) for v in me.vertices],dtype=np.float64);xy=xyz[:,:2]-xyz[:,:2].mean(axis=0)
faces=np.array([list(t.vertices) for t in me.loop_triangles],dtype=int);counts=Counter();weights=defaultdict(float)
for f in faces:
 for a,b in zip(f,np.roll(f,-1)):counts[tuple(sorted((int(a),int(b))))]+=1
 for k in range(3):
  a,b,c=int(f[k]),int(f[(k+1)%3]),int(f[(k+2)%3]);u=xy[a]-xy[c];v=xy[b]-xy[c];area=abs(u[0]*v[1]-u[1]*v[0])
  if area>1e-10:weights[tuple(sorted((a,b)))]+=.5*float(u@v)/area
boundary=sorted({i for edge,count in counts.items() if count==1 for i in edge});fixed=set(boundary)
free=[i for i in range(len(xyz)) if i not in fixed];mapping={i:j for j,i in enumerate(free)}
A=np.zeros((len(free),len(free)));rhs=np.zeros(len(free))
for (a,b),w in weights.items():
 for i,j in ((a,b),(b,a)):
  if i in fixed:continue
  row=mapping[i];A[row,row]+=w
  if j in fixed:rhs[row]+=w*xyz[j,2]
  else:A[row,mapping[j]]-=w
z=xyz[:,2].copy();z[free]=np.linalg.solve(A,rhs)
def stats(z):
 p=xyz[faces].copy();p[:,:,2]=z[faces];n=np.cross(p[:,1]-p[:,0],p[:,2]-p[:,0]);nz=abs(n[:,2]);good=nz>1e-10
 slopes=np.sqrt(n[good,0]**2+n[good,1]**2)/nz[good]
 return {'triangles':len(faces),'projected_degenerate_triangles':int(np.count_nonzero(~good)),'grade_over_200percent':int(np.count_nonzero(slopes>2)),'grade_max':float(slopes.max()),'grade_p95':float(np.percentile(slopes,95))}
before=stats(xyz[:,2]);after=stats(z)
out={'schema':'boas/coastal-floor-parameterized-b70-probe-v1','source':src,'object':o.name,'method':'cotangent_harmonic_xy_with_all_boundary_heights_fixed','classification':'ADAPT_LOCAL','before':before,'after':after,'boundary_vertices':len(boundary),'interior_vertices':len(free),'boundary_max_change_m':float(np.max(abs(z[boundary]-xyz[boundary,2]))),'max_interior_height_change_m':float(np.max(abs(z-xyz[:,2]))),'linear_residual_max':float(np.max(abs(A@z[free]-rhs))),'finite':bool(np.isfinite(z).all()),'source_changed':False,'proposed_gate_passed':bool(np.isfinite(z).all() and after['grade_over_200percent']<before['grade_over_200percent'] and after['grade_p95']<before['grade_p95'] and after['grade_max']<=before['grade_max']*1.001),'pending':['Altimetria/costa e junção B62 continuam candidatos; não é levantamento real']}
(r/'docs/reports/blender/coastal_floor_parameterized_b70_probe.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
np.savez_compressed(r/'artifacts/waterfront/coastal_floor_parameterized_b70.npz',xyz=xyz,z=z,boundary=np.array(boundary),faces=faces)
print(json.dumps(out))
