"""Diagnóstico read-only de regularidade do piso B63 com fronteira fixa."""
import bpy,bmesh,json,math,numpy as np
from pathlib import Path
from collections import Counter
r=Path(__file__).resolve().parents[2];s=bpy.context.scene;o=s.objects['B63 | VISUAL | piso contínuo até o cais'];me=o.data
xyz=np.array([list(v.co) for v in me.vertices]);me.calc_loop_triangles()
faces=[list(t.vertices) for t in me.loop_triangles];adj=[set() for v in me.vertices];counts=Counter()
for f in faces:
 for a,b in zip(f,f[1:]+f[:1]):
  adj[a].add(b);adj[b].add(a);counts[tuple(sorted((a,b)))]+=1
boundary={v for e,count in counts.items() if count==1 for v in e}
free=[i for i in range(len(xyz)) if i not in boundary];z=xyz[:,2].copy();history=[]
for k in range(2000):
 nz=z.copy()
 for i in free:nz[i]=sum(z[j] for j in adj[i])/len(adj[i])
 delta=float(np.max(abs(nz-z)));z=nz
 if k in (0,99,499,999,1999):history.append([k,delta])
 if delta<1e-6:break
def stats(z):
 slopes=[];worst=[]
 for fi,f in enumerate(faces):
  pts=[np.array((xyz[i,0],xyz[i,1],z[i])) for i in f];n=np.cross(pts[1]-pts[0],pts[2]-pts[0]);L=float(np.linalg.norm(n))
  if L<=1e-9:continue
  grade=math.hypot(float(n[0]),float(n[1]))/max(abs(float(n[2])),1e-10);slopes.append(grade)
  if grade>2:worst.append({'face':fi,'xyz':list(map(float,np.mean(pts,axis=0))),'grade':grade,'boundary_vertices':sum(i in boundary for i in f)})
 return {'triangles':len(slopes),'grade_over_200percent':len(worst),'grade_max':max(slopes),'grade_p95':float(np.percentile(slopes,95)),'worst':sorted(worst,key=lambda x:x['grade'],reverse=True)[:12]}
out={'object':o.name,'boundary_vertices':len(boundary),'interior_vertices':len(free),'before':stats(xyz[:,2]),'relaxation_candidate':stats(z),'iterations':k+1,'max_z_candidate_change':float(np.max(abs(z-xyz[:,2]))),'history':history,'all_boundaries_preserved':True,'below_water_boundary':[list(map(float,xyz[i])) for i in boundary if xyz[i,2]<.35],'source_changed':False,'classification':'ERROR_INTERNAL_INTERPOLATION_CANDIDATE'}
(r/'docs/reports/blender/coastal_floor_fairing_b69_probe.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
np.savez_compressed(r/'artifacts/waterfront/coastal_floor_fairing_b69.npz',xyz=xyz,z=z,boundary=np.array(sorted(boundary)))
print(json.dumps({k:v for k,v in out.items() if k not in ('before','relaxation_candidate','below_water_boundary')}))
