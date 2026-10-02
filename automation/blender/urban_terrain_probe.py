"""Investiga apenas malhas de chão sobrepostas na área da slice."""
import bpy, json, importlib.util
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2]
c=json.loads((root/'prototypes/threejs-water-lab/public/data/urban_slice.json').read_text())
points=c['routes'][1]['points']
out=[]
for o in bpy.context.scene.objects:
    if o.type!='MESH' or not o.visible_get() or o.hide_render: continue
    bb=[o.matrix_world@Vector(p) for p in o.bound_box]
    if min(p.x for p in bb)>110 or max(p.x for p in bb)<-50 or min(p.y for p in bb)>15 or max(p.y for p in bb)<-160: continue
    if max(p.z for p in bb)-min(p.z for p in bb)>12 and 'terreno' not in o.name.lower():continue
    ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();m.calc_loop_triangles()
    tree=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[list(t.vertices) for t in m.loop_triangles],all_triangles=True)
    hits=[]
    for i,p in enumerate(points):
        q=tree.ray_cast(Vector((p[0],-p[2],150)),Vector((0,0,-1)),300)[0]
        if q:hits.append([i,round(q.z,3),round(q.z-p[1],3)])
    ev.to_mesh_clear()
    if hits:out.append({'name':o.name,'hits':hits,'materials':[m.name for m in o.data.materials if m]})
report={'source':bpy.data.filepath,'shapely':bool(importlib.util.find_spec('shapely')),'overlapping_surfaces':out}
(root/'artifacts/urban-slice/terrain_probe.json').write_text(json.dumps(report,ensure_ascii=False))
print(json.dumps(report,ensure_ascii=False))
