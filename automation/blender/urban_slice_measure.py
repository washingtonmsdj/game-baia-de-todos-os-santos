"""Mede as superfícies existentes no circuito OSM candidato, sem mutação."""
import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2]
d=json.loads((root/'prototypes/threejs-water-lab/public/data/road_graph.json').read_text())
ns={n['id']:n for n in d['nodes']}
ids=['5423989355','5423989361','8243832355','5917201014','7523817810','344571683','1672367520','7520527650','1672367506','7523817812','7523817807','7523817808','7523817809','592378626','592378620','3940312599','1672367592','5423989354']
names=['MVP | terreno corrigido | colisão estática','R30A5 | COLLISION | terrain proxy','OSM | pistas do centro','OSM | calçadas indicativas']
trees=[]
for name in names:
 o=bpy.data.objects[name];ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();m.calc_loop_triangles()
 tree=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[list(t.vertices) for t in m.loop_triangles],all_triangles=True)
 trees.append((name,tree));ev.to_mesh_clear()
out=[]
for id in ids:
 x,y=ns[id]['blender_xy'];heights={}
 for name,t in trees:
  hit=t.ray_cast(Vector((x,y,150)),Vector((0,0,-1)),300)[0]
  heights[name]=list(hit) if hit else None
 out.append({'id':id,'xy':[x,y],'hits':heights})
p=root/'artifacts/urban-slice/measure.json';p.write_text(json.dumps(out,indent=2));print(json.dumps(out))
