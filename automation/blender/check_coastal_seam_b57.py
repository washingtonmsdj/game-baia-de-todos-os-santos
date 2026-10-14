import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2]
o=bpy.context.scene.objects['MVP | terreno corrigido | colisão estática'];m=o.data;m.calc_loop_triangles()
t=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[list(p.vertices) for p in m.loop_triangles],all_triangles=True)
rows=[]
for y in [-300,-285.26,-285,-280,-250,-200,-150,-100,-50,0,10]:
 r={'y':y,'hits':[]}
 for x in [-285.70,-285.5,-284,-280,-270,-261]:
  p,n,i,d=t.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),400)
  r['hits'].append([x,float(p.z) if p else None])
 rows.append(r)
print(json.dumps(rows))
