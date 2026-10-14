"""Diagnóstico B71 do canto norte e vias OSM, sem alterar a cena."""
import bpy,json,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
src=json.loads((r/'world/areas/mvp-centro-lacerda/blender-revisions.json').read_text(encoding='utf8'))['validation_source']
assert src['revision']=='R30B.70' and Path(bpy.data.filepath).resolve()==(r/src['file']).resolve()
assert hashlib.sha256((r/src['file']).read_bytes()).hexdigest()==src['sha256']
names=['B62 | GAMEPLAY TERRAIN HQ | pavimento e costura limpa','B63 | VISUAL | piso contínuo até o cais','CAIS | contenção costeira alinhada à linha de costa','MVP | terreno corrigido | colisão estática']
rows=[];trees={}
for name in names:
 ob=s.objects[name];me=ob.data;me.calc_loop_triangles()
 coords=np.array([list(ob.matrix_world@v.co) for v in me.vertices],dtype=float)
 trees[name]=BVHTree.FromPolygons([Vector(x) for x in coords],[list(t.vertices) for t in me.loop_triangles],all_triangles=True)
 dist=np.linalg.norm(coords[:,:2]-[-285.70343,38.40735],axis=1);indices=np.where(dist<5)[0]
 rows.append({'object':name,'near_vertices':[{'i':int(i),'xyz':coords[i].tolist()} for i in indices[:200]],'properties':dict(ob.items()),'bounds':[coords.min(axis=0).tolist(),coords.max(axis=0).tolist()]})
samples=[]
for x in [-292,-290,-288,-286,-285.70343,-284,-282]:
 for y in [34,36,38.40735,39.4,40,42,44]:
  hits={}
  for name,tree in trees.items():
   hit,normal,index,d=tree.ray_cast(Vector((x,y,100)),Vector((0,0,-1)),200)
   if hit is not None:hits[name]={'z':hit.z,'triangle':index}
  samples.append({'xy':[x,y],'hits':hits})
reference=json.loads((r/'artifacts/structural-pipeline/mvp-centro-lacerda/structural_reference.json').read_text(encoding='utf8'))
out={'schema':'boas/north-junction-b71-probe-v1','source':src,'corner_objects':rows,'samples':samples,'reference_type':type(reference).__name__,'reference_keys':list(reference) if isinstance(reference,dict) else None}
(r/'docs/reports/blender/north_junction_b71_probe.json').write_text(json.dumps(out,ensure_ascii=False,indent=2,default=str)+'\n',encoding='utf8')
print(json.dumps({'objects':[{k:v for k,v in row.items() if k!='near_vertices'} for row in rows]}))
