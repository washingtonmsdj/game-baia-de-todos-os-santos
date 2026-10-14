import bpy,json,math
from pathlib import Path
r=Path(__file__).resolve().parents[2];rows=json.loads((r/'docs/reports/blender/pier_gap_diagnosis_b69.json').read_text());reg=json.loads((r/'artifacts/waterfront/pier_land_region_b67.json').read_text())
out=[]
def cross(a,b):return a[0]*b[1]-a[1]*b[0]
for row in rows[:3]:
 q=row['q'];found={}
 for name,tris in reg['meshes'].items():
  found[name]=[]
  for tri in tris:
   a,b,c=tri;d=[b[k]-a[k] for k in range(2)];e=[c[k]-a[k] for k in range(2)];p=[q[k]-a[k] for k in range(2)];den=cross(d,e)
   if abs(den)<1e-10:continue
   u=cross(p,e)/den;v=cross(d,p)/den
   if u>=-1e-8 and v>=-1e-8 and u+v<=1+1e-8:found[name].append({'tri':tri,'barycentric':[u,v]})
 out.append({'q':q,'contains':found})
(r/'docs/reports/blender/pier_gap_xy_b69.json').write_text(json.dumps(out,indent=2),encoding='utf8')
