"""Verifica apenas as bordas geradas no recorte do poço, sem editar terreno."""
import bpy,json,runpy
import numpy as np
from pathlib import Path
from mathutils import Matrix
root=Path(__file__).resolve().parents[2];out=root/'docs/reports/blender/lacerda-exterior-b102';e=json.loads((out/'excavation.json').read_text())
o=bpy.context.scene.objects[e['source_object']];m=o.data;nold=e['unchanged_source_vertex_coordinates'];poly=np.array(e['footprint_local']);lo=poly.min(axis=0)-.1;hi=poly.max(axis=0)+.1
wm=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'))['world_matrix']
inv=Matrix(json.loads((root/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text())['measurement_frame']).inverted()
raw=np.empty(len(m.vertices)*3,dtype=np.float32);m.vertices.foreach_get('co',raw);A=np.array(inv@wm(o));p=raw.reshape((-1,3))@A[:3,:3].T+A[:3,3]
near=((p[:,:2]>=lo).all(axis=1)&(p[:,:2]<=hi).all(axis=1))
loops=np.empty(len(m.loops),dtype=np.int32);starts=np.empty(len(m.polygons),dtype=np.int32);counts=np.empty(len(m.polygons),dtype=np.int32)
m.loops.foreach_get('vertex_index',loops);m.polygons.foreach_get('loop_start',starts);m.polygons.foreach_get('loop_total',counts)
faceids=np.nonzero(np.add.reduceat(near[loops].astype(np.int32),starts)>0)[0];edges={}
for fi in faceids:
 ids=loops[starts[fi]:starts[fi]+counts[fi]].tolist()
 for a,b in zip(ids,ids[1:]+ids[:1]):
  key=tuple(sorted((a,b)));edges[key]=edges.get(key,0)+1
def distance(v):
 result=1e9
 for a,b in zip(poly,np.roll(poly,-1,axis=0)):
  d=b-a;t=np.clip((v-a).dot(d)/d.dot(d),0.,1.);result=min(result,float(np.linalg.norm(v-(a+t*d))))
 return result
intentional=[];suspect=[]
for (a,b),count in edges.items():
 if count!=1 or max(a,b)<nold or not (near[a] and near[b]):continue
 item={'edge':[a,b],'length_m':float(np.linalg.norm(p[a]-p[b])),'outline_residual_m':[distance(p[a,:2]),distance(p[b,:2])]}
 (intentional if max(item['outline_residual_m'])<5e-5 else suspect).append(item)
r={'source':e['source_object'],'new_cut_boundary_edges':len(intentional),'suspect_crack_edges':suspect,
 'status':'CUT_BOUNDARY_ONLY_NO_NEW_SEAM_CRACK' if not suspect else 'NUMERICAL_SEAM_REQUIRES_REPAIR',
 'method':'Arestas de um único uso contendo vértice novo; limite do núcleo é abertura intencional, demais bordas são suspeitas','scene_changed':False}
(out/'terrain-seam.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'status':r['status'],'intentional_edges':len(intentional),'suspect_edges':len(suspect)}))
