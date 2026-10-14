"""Mede cobertura do terreno denso vs expansão gameplay B55."""
import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2]
assert Path(bpy.data.filepath).name=="salvador_lacerda_r30b56_pieres_gameplay.blend"
dense=bpy.context.scene.objects["MVP | terreno corrigido | colisão estática"]
game=bpy.context.scene.objects["B55 | GAMEPLAY TERRAIN | costa + vias refinadas"]
def bounds(o):
    c=[o.matrix_world@Vector(x) for x in o.bound_box]
    return {"min":[min(p[i] for p in c) for i in range(3)],"max":[max(p[i] for p in c) for i in range(3)]}
me=dense.data; me.calc_loop_triangles()
tree=BVHTree.FromPolygons([dense.matrix_world@v.co for v in me.vertices],[list(t.vertices) for t in me.loop_triangles],all_triangles=True)
inside=outside=0; examples=[]
for v in game.data.vertices:
    p=game.matrix_world@v.co
    h=tree.ray_cast(Vector((p.x,p.y,200)),Vector((0,0,-1)),500)[0]
    if h is None:
        outside+=1
        if len(examples)<20: examples.append([float(p.x),float(p.y),float(p.z)])
    else: inside+=1
print(json.dumps({"dense_bounds":bounds(dense),"gameplay_bounds":bounds(game),"game_vertices":len(game.data.vertices),"inside_dense_xy":inside,"outside_dense_xy":outside,"outside_ratio":outside/max(1,inside+outside),"examples":examples},ensure_ascii=False))
