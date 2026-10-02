import bpy,json,runpy
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];R=Matrix(json.loads((root/'artifacts/palacio-rio-branco/alignment_controls_r35.json').read_text(encoding='utf8'))['rotation'])
o=bpy.context.scene.objects['MVP | terreno corrigido | colisão estática'];o.data.calc_loop_triangles()
bvh=BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(t.vertices) for t in o.data.loop_triangles],all_triangles=True);rows=[]
for y in (0.63,4.245,7.87):
    samples=[]
    for x in (-40,-35,-30,-25,-22,-20,-18,-16,-14,-12,-11.51,-10,-6,-2):
        w=R@Vector((x,y,140));h=bvh.ray_cast(w,Vector((0,0,-1)),220)
        samples.append({'x':x,'z':h[0].z if h[0] else None,'material':o.data.materials[o.data.polygons[o.data.loop_triangles[h[2]].polygon_index].material_index].name if h[0] else None})
    rows.append({'y':y,'samples':samples})
(root/'artifacts/palacio-rio-branco/support_ground_r35.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(rows,ensure_ascii=False))
