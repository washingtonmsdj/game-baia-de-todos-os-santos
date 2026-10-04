"""Seções transversais read-only na junção crítica da Misericórdia B41."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];scene=bpy.context.scene
reg=json.loads((root/"world/areas/mvp-centro-lacerda/blender-revisions.json").read_text(encoding="utf8"));src=reg["authoring_source"]
assert src["revision"]=="R30B.41"; assert Path(bpy.data.filepath).resolve()==(root/src["file"]).resolve()
contract=json.loads((root/"world/areas/mvp-centro-lacerda/production.json").read_text(encoding="utf8"))
ground=scene.objects[contract["export"]["road_object"]]; road=scene.objects["R30A7 | ROAD | 803899198"]
me=ground.data;me.calc_loop_triangles(); verts=[ground.matrix_world@v.co for v in me.vertices]; tris=[list(t.vertices) for t in me.loop_triangles]
pm=[p.material_index for p in me.polygons];tm=[pm[t.polygon_index] for t in me.loop_triangles];tree=BVHTree.FromPolygons(verts,tris,all_triangles=True)
def hit(x,y):
 p,n,i,_=tree.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),500)
 if p is None:return None
 mi=tm[i]; mat=me.materials[mi].name if mi<len(me.materials) and me.materials[mi] else None
 return {"z":float(p.z),"normal_z":float(n.z),"material":mat}
pts=[road.matrix_world@Vector(p.co[:3]) for sp in road.data.splines for p in sp.points]
sections=[]
for idx in [120,125,128,130,133,135,140,145]:
 p=pts[idx]; a=pts[max(0,idx-1)]; b=pts[min(len(pts)-1,idx+1)]
 t=(b-a).to_2d().normalized(); n=Vector((-t.y,t.x))
 samples=[]
 for off in [x*.5 for x in range(-16,17)]:
  q=p.to_2d()+n*off; h=hit(q.x,q.y); samples.append({"offset_m":off,"xy":[float(q.x),float(q.y)],"hit":h})
 sections.append({"index":idx,"center":[float(p.x),float(p.y),float(p.z)],"tangent":[float(t.x),float(t.y)],"samples":samples})
out=root/"artifacts/roads/rondesp/misericordia_cross_sections_b41.json";out.write_text(json.dumps({"schema":"boas/misericordia-cross-sections-b41-v1","sections":sections,"geometry_changed":False},ensure_ascii=False,indent=2)+"\n",encoding="utf8")
summary=[]
for s in sections:
 mats={}
 for x in s["samples"]:
  h=x["hit"]; 
  if h: mats.setdefault(h["material"],[]).append((x["offset_m"],h["z"]))
 summary.append({"index":s["index"],"materials":{k:{"min_off":min(x[0] for x in v),"max_off":max(x[0] for x in v),"z_min":min(x[1] for x in v),"z_max":max(x[1] for x in v)} for k,v in mats.items()}})
print(json.dumps(summary,ensure_ascii=False))
