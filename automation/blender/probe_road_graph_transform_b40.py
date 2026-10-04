"""Mede se helpers R30A7 estão no referencial anterior ao binding B26/B27."""
import bpy,json,statistics
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2]
s=bpy.context.scene
contract=json.loads((root/"world/areas/mvp-centro-lacerda/production.json").read_text(encoding="utf8"))
ground=s.objects[contract["export"]["road_object"]]
me=ground.data
me.calc_loop_triangles()
verts=[ground.matrix_world@v.co for v in me.vertices]
tris=[list(t.vertices) for t in me.loop_triangles]
pm=[poly.material_index for poly in me.polygons]
tm=[pm[t.polygon_index] for t in me.loop_triangles]
tree=BVHTree.FromPolygons(verts,tris,all_triangles=True)
slots={i for i,m in enumerate(me.materials) if m and m.name in contract["export"]["road_materials"]}
def surface(x,y):
    p,n,i,_=tree.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),500)
    if p is None:return None
    return {"z":float(p.z),"road":tm[i] in slots,"normal_z":float(n.z)}
raw=[];mapped=[]
M=ground.matrix_world
for ob in s.objects:
    if not (ob.name.startswith("R30A7 | ROAD |") and ob.type=="CURVE"):
        continue
    for sp in ob.data.splines:
        for cp in sp.points:
            local=Vector(cp.co[:3])
            world=ob.matrix_world@local
            a=surface(world.x,world.y)
            q=M@local
            b=surface(q.x,q.y)
            if a:raw.append((a,world))
            if b:mapped.append((b,q))
def summarize(rows):
    roads=[(h,p) for h,p in rows if h["road"]]
    residual=[abs(p.z-h["z"]) for h,p in roads]
    return {
      "samples":len(rows),
      "road_material_hits":len(roads),
      "road_hit_rate":len(roads)/len(rows) if rows else 0,
      "median_abs_z_residual_m":statistics.median(residual) if residual else None,
      "p95_abs_z_residual_m":sorted(residual)[int(.95*(len(residual)-1))] if residual else None
    }
report={
  "schema":"boas/road-graph-transform-probe-v1",
  "source_file":str(bpy.data.filepath),
  "dirty_before":bool(bpy.data.is_dirty),
  "ground_object":ground.name,
  "ground_matrix_world":[list(r) for r in M],
  "raw":summarize(raw),
  "mapped_through_ground_matrix":summarize(mapped),
  "geometry_changed":False,
  "saved_session":False,
}
out=root/"artifacts/roads/rondesp/road_graph_transform_b40.json"
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps(report,ensure_ascii=False))
