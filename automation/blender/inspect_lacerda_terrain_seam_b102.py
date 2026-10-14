"""Localiza duplicatas e T-junctions só na emenda do recorte B102."""
import bpy,json,runpy
import numpy as np
from pathlib import Path
root=Path(__file__).resolve().parents[2];out=root/'docs/reports/blender/lacerda-exterior-b102'
e=json.loads((out/'excavation.json').read_text());r=json.loads((out/'terrain-seam.json').read_text())
o=bpy.context.scene.objects[e['source_object']];m=o.data;old=bpy.data.meshes[o['boas_source_mesh_before_b102']]
raw=np.empty(len(m.vertices)*3,dtype=np.float32);m.vertices.foreach_get('co',raw);p=raw.reshape((-1,3)).astype(float)
loops=np.empty(len(m.loops),dtype=np.int32);starts=np.empty(len(m.polygons),dtype=np.int32);counts=np.empty(len(m.polygons),dtype=np.int32)
m.loops.foreach_get('vertex_index',loops);m.polygons.foreach_get('loop_start',starts);m.polygons.foreach_get('loop_total',counts)
ids=sorted({i for row in r['suspect_crack_edges'] for i in row['edge']});near={};source_edges={};n=len(old.vertices)
for i in ids:
 d=np.linalg.norm(p-p[i],axis=1);ix=np.argsort(d)[:4];near[i]={'point':p[i].tolist(),'nearest':[(int(j),float(d[j])) for j in ix]}
selected=np.isin(loops,ids);fs=np.nonzero(np.add.reduceat(selected.astype(np.int32),starts)>0)[0]
faces=[{'index':int(fi),'ids':loops[starts[fi]:starts[fi]+counts[fi]].tolist()} for fi in fs]
oraw=np.empty(len(old.vertices)*3,dtype=np.float32);old.vertices.foreach_get('co',oraw);assert np.array_equal(p[:n].astype(np.float32),oraw.reshape((-1,3)))
for i in ids:
 if i<n:continue
 for face in faces:
  f=face['ids']
  for a,b in zip(f,f[1:]+f[:1]):
   if a>=n or b>=n:continue
   ab=p[b]-p[a];t=np.dot(p[i]-p[a],ab)/np.dot(ab,ab);dist=np.linalg.norm(p[i]-(p[a]+t*ab))
   if 0<t<1 and dist<5e-5:source_edges.setdefault(i,[]).append({'edge':[a,b],'t':float(t),'distance':float(dist)})
result={'points':near,'faces':faces,'split_source_edges':source_edges,'scene_changed':False}
(out/'terrain-seam-diagnosis.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
print(json.dumps(result))
