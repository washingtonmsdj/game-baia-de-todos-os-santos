"""Diagnóstico read-only da transição crítica da Rua da Misericórdia B41."""
import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2]; scene=bpy.context.scene
registry=json.loads((root/"world/areas/mvp-centro-lacerda/blender-revisions.json").read_text(encoding="utf8")); src=registry["authoring_source"]
assert src["revision"]=="R30B.41"; assert Path(bpy.data.filepath).resolve()==(root/src["file"]).resolve()
contract=json.loads((root/"world/areas/mvp-centro-lacerda/production.json").read_text(encoding="utf8"))
ground=scene.objects[contract["export"]["road_object"]]; road=scene.objects["R30A7 | ROAD | 803899198"]
me=ground.data; me.calc_loop_triangles()
verts=[ground.matrix_world@v.co for v in me.vertices]; tris=[list(t.vertices) for t in me.loop_triangles]
pm=[p.material_index for p in me.polygons]; tm=[pm[t.polygon_index] for t in me.loop_triangles]; tree=BVHTree.FromPolygons(verts,tris,all_triangles=True)
def hit(x,y):
 p,n,i,_=tree.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),500)
 if p is None:return None
 mi=tm[i]; mat=me.materials[mi].name if mi<len(me.materials) and me.materials[mi] else None
 return {"z":float(p.z),"normal_z":float(n.z),"material":mat}
pts=[road.matrix_world@Vector(p.co[:3]) for sp in road.data.splines for p in sp.points]
rows=[]
for i in range(115,min(180,len(pts))):
 p=pts[i]; q=pts[i+1] if i+1<len(pts) else None
 dxy=(q.to_2d()-p.to_2d()).length if q else None; grade=(q.z-p.z)/dxy if q and dxy else None
 rows.append({"i":i,"point":[float(p.x),float(p.y),float(p.z)],"surface":hit(p.x,p.y),"next_grade":grade})
out=root/"artifacts/roads/rondesp/misericordia_surface_b41.json"
out.write_text(json.dumps({"schema":"boas/misericordia-surface-probe-b41-v2","source":src,"rows":rows,"geometry_changed":False,"saved_session":False},ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps({"rows":len(rows),"max_abs_grade":max(abs(r["next_grade"]) for r in rows if r["next_grade"] is not None),"sample":[rows[i] for i in (0,5,10,11,12,13,15,20,30,40,50,60) if i<len(rows)]},ensure_ascii=False))
