"""Planeja subdivisão local do proxy B42 sem mutar."""
import bpy,json,runpy
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];scene=bpy.context.scene
reg=json.loads((root/"world/areas/mvp-centro-lacerda/blender-revisions.json").read_text(encoding="utf8"));src=reg["validation_source"]
assert src["revision"]=="R30B.42";assert Path(bpy.data.filepath).resolve()==(root/src["file"]).resolve()
c=json.loads((root/"world/areas/mvp-centro-lacerda/production.json").read_text(encoding="utf8"));wm=runpy.run_path(str(root/"automation/blender/component_fingerprint.py"))["world_matrix"]
g=scene.objects[c["export"]["road_object"]];p=scene.objects[c["export"]["terrain_proxy"]];road=scene.objects["R30A7 | ROAD | 803899198"]
pts=[wm(road)@Vector(x.co[:3]) for s in road.data.splines for x in s.points]
rep=json.loads((root/"docs/reports/blender/misericordia_profile_r30b41.json").read_text(encoding="utf8"));i0,i1=rep["source_node_profile_indices"][1],rep["source_node_profile_indices"][2]
p0,p1=pts[i0].to_2d(),pts[i1].to_2d();axis=p1-p0;L2=axis.length_squared;unit=axis.normalized()
g.data.calc_loop_triangles();tris=list(g.data.loop_triangles);tree=BVHTree.FromPolygons([wm(g)@v.co for v in g.data.vertices],[list(t.vertices) for t in tris],all_triangles=True)
slots={i for i,m in enumerate(g.data.materials) if m and m.name in c["export"]["road_materials"]}
candidates=[];edges=set()
for f in p.data.polygons:
 center=wm(p)@f.center;q=center.to_2d()-p0;t=q.dot(axis)/L2;lat=abs(q.cross(unit))
 if not(-.03<=t<=1.03 and lat<=4.0):continue
 hit,n,idx,_=tree.ray_cast(Vector((center.x,center.y,center.z+8)),Vector((0,0,-1)),16)
 if hit is None or n.z<=.70 or tris[idx].material_index not in slots:continue
 candidates.append(f.index)
 for e in f.edge_keys:edges.add(tuple(sorted(e)))
print(json.dumps({"candidate_faces":len(candidates),"candidate_edges":len(edges),"proxy_vertices":len(p.data.vertices),"proxy_faces":len(p.data.polygons),"corridor_half_width_m":4.0},ensure_ascii=False))
