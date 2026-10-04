"""Diagnóstico read-only de crossfall e rodas no início do segmento 1 da Misericórdia B45."""
import bpy,json,runpy
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2]; s=bpy.context.scene
assert Path(bpy.data.filepath).name=="salvador_lacerda_r30b45_proxy_misericordia_final.blend"
c=json.loads((root/"world/areas/mvp-centro-lacerda/production.json").read_text(encoding="utf8"))
audit=json.loads((root/"artifacts/roads/rondesp/rondesp_network_b45_candidate.json").read_text(encoding="utf8"))
wm=runpy.run_path(str(root/"automation/blender/component_fingerprint.py"))["world_matrix"]
ground=s.objects[c["export"]["road_object"]]; me=ground.data; me.calc_loop_triangles()
tri=list(me.loop_triangles); tree=BVHTree.FromPolygons([wm(ground)@v.co for v in me.vertices],[list(t.vertices) for t in tri],all_triangles=True)
roadslots={i for i,m in enumerate(me.materials) if m and m.name in c["export"]["road_materials"]}
vehicle=next(v for v in json.loads((root/"world/vehicles/catalog.json").read_text(encoding="utf8"))["vehicles"] if v["asset_id"]=="vehicle-rondesp-pickup")["authoring_base"]
before=set(bpy.data.objects)
with bpy.data.libraries.load(str(root/vehicle["file"]),link=True) as (a,r): r.objects=[n for n in a.objects if "Eixo giro roda" in n]
contacts=[list(wm(o).translation) for o in r.objects]
for ob in set(bpy.data.objects)-before:
    if not ob.users_scene:bpy.data.objects.remove(ob,do_unlink=True)
midy=(max(x[1] for x in contacts)+min(x[1] for x in contacts))/2
rec=next(x for x in audit["segments"] if x["edge_id"]=="way-803899198-seg-1")
road=s.objects["R30A7 | ROAD | 803899198"]; pts=[wm(road)@Vector(p.co[:3]) for sp in road.data.splines for p in sp.points]
def hit(x,y,z):
 p,n,i,_=tree.ray_cast(Vector((x,y,z+2)),Vector((0,0,-1)),4)
 if p is None:return None
 mi=tri[i].material_index; mat=me.materials[mi].name if mi<len(me.materials) and me.materials[mi] else None
 return {"z":float(p.z),"material":mat,"road":mi in roadslots,"normal_z":float(n.z)}
rows=[]
for sm in rec["samples"]:
 if "crossfall_review" not in sm.get("issues",[]):continue
 q=Vector(sm["point"]); best=None
 for a,b in zip(pts,pts[1:]):
  d=(b-a).to_2d(); L2=d.length_squared
  if L2<1e-9:continue
  t=max(0,min(1,(q.to_2d()-a.to_2d()).dot(d)/L2)); p=a.to_2d()+d*t; dist=(q.to_2d()-p).length
  if best is None or dist<best[0]:best=(dist,d.normalized())
 f=best[1]; sx=Vector((-f.y,f.x)); center=hit(q.x,q.y,q.z); wheels=[]
 for wi,(px,py,pz) in enumerate(contacts):
  xy=q.to_2d()+sx*px-f*(py-midy); wheels.append({"wheel":wi,"offset_lateral_m":px,"offset_longitudinal_m":-(py-midy),"xy":[float(xy.x),float(xy.y)],"hit":hit(xy.x,xy.y,center["z"])})
 rows.append({"fraction":sm["fraction"],"center":center,"grade":sm.get("grade"),"bank":sm.get("bank"),"wheels":wheels})
out=root/"artifacts/roads/rondesp/misericordia_crossfall_b45.json";out.write_text(json.dumps({"schema":"boas/misericordia-crossfall-b45-v1","rows":rows,"geometry_changed":False},ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps(rows,ensure_ascii=False))
