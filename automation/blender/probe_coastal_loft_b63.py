import bpy,json,numpy as np
from pathlib import Path
from mathutils import Vector,geometry
from mathutils.bvhtree import BVHTree
r=Path(__file__).resolve().parents[2]
a=np.load(r/'artifacts/waterfront/urban_core_b62.npz');v=a['vertices'];o=bpy.context.scene.objects['MVP | terreno corrigido | colisão estática'];o.data.calc_loop_triangles()
tree=BVHTree.FromPolygons([Vector(q) for q in v],[list(t.vertices) for t in o.data.loop_triangles],all_triangles=True)
f=[]
for y in [-94.84,-80,-50,-12,0,30,80,100,150,220,280,333]:
 hit=tree.ray_cast(Vector((-285.7014,y,200)),Vector((0,0,-1)),400)[0];f.append([y,hit.z if hit else None])
print(json.dumps({'core_edge_z':f,'cdt_doc':geometry.delaunay_2d_cdt.__doc__[:3900]}))
