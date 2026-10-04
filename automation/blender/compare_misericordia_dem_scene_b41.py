"""Compara perfil DEM relativo ancorado na superfície B41, sem modificar a cena."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];scene=bpy.context.scene
reg=json.loads((root/"world/areas/mvp-centro-lacerda/blender-revisions.json").read_text(encoding="utf8"));src=reg["authoring_source"]
assert src["revision"]=="R30B.41";assert Path(bpy.data.filepath).resolve()==(root/src["file"]).resolve()
contract=json.loads((root/"world/areas/mvp-centro-lacerda/production.json").read_text(encoding="utf8"))
ground=scene.objects[contract["export"]["road_object"]]
me=ground.data;me.calc_loop_triangles();verts=[ground.matrix_world@v.co for v in me.vertices];tris=[list(t.vertices) for t in me.loop_triangles]
pm=[p.material_index for p in me.polygons];tm=[pm[t.polygon_index] for t in me.loop_triangles];tree=BVHTree.FromPolygons(verts,tris,all_triangles=True)
def hit(x,y):
 p,n,i,_=tree.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),500)
 if p is None:return None
 mi=tm[i];return float(p.z),(me.materials[mi].name if mi<len(me.materials) and me.materials[mi] else None),float(n.z)
dem=json.loads((root/"artifacts/roads/rondesp/misericordia_dem_profile.json").read_text(encoding="utf8"))
rows=[x for x in dem["rows"] if x["segment"]==1 and x["dem_m"] is not None]
z0,z1=rows[0]["dem_m"],rows[-1]["dem_m"];L=rows[-1]["distance_m"]-rows[0]["distance_m"]
h0=hit(*rows[0]["blender_xy"]);h1=hit(*rows[-1]["blender_xy"]);assert h0 and h1
scene0,scene1=h0[0],h1[0]
outrows=[]
for r in rows:
 t=(r["distance_m"]-rows[0]["distance_m"])/L
 target=r["dem_m"]+(scene0-z0)*(1-t)+(scene1-z1)*t
 h=hit(*r["blender_xy"]);current=h[0] if h else None
 outrows.append({"t":t,"xy":r["blender_xy"],"target_z":target,"current_z":current,"delta_m":None if current is None else target-current,"material":h[1] if h else None,"normal_z":h[2] if h else None})
valid=[r for r in outrows if r["delta_m"] is not None]; active=[r for r in valid if abs(r["delta_m"])>.10]; peak=max(valid,key=lambda r:r["delta_m"])
summary={"surface_anchor_start_z":scene0,"surface_anchor_end_z":scene1,"max_raise_m":peak["delta_m"],"peak_t":peak["t"],"peak_xy":peak["xy"],"max_lower_m":min(r["delta_m"] for r in valid),"rms_delta_m":math.sqrt(sum(r["delta_m"]**2 for r in valid)/len(valid)),"active_t_min":min(r["t"] for r in active),"active_t_max":max(r["t"] for r in active),"active_samples":len(active)}
report={"schema":"boas/misericordia-dem-scene-compare-b41-v2","source":src,"method":"DEM relativo com correção linear ancorada no pavimento dos dois endpoints topológicos","rows":outrows,"summary":summary,"geometry_changed":False,"saved_session":False}
(root/"artifacts/roads/rondesp/misericordia_dem_scene_compare_b41.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps(summary,ensure_ascii=False))
