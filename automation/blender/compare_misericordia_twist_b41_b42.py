"""Compara os quatro apoios do único twist novo da Misericórdia B42 contra B41."""
import bpy,json,runpy,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];s=bpy.context.scene
c=json.loads((root/"world/areas/mvp-centro-lacerda/production.json").read_text(encoding="utf8"));wm=runpy.run_path(str(root/"automation/blender/component_fingerprint.py"))["world_matrix"]
audit=json.loads((root/"artifacts/roads/rondesp/rondesp_network_b42_candidate.json").read_text(encoding="utf8"))
rec=next(r for r in audit["segments"] if r["edge_id"]=="way-803899198-seg-1")
sm=next(x for x in rec["samples"] if "four_wheel_twist" in x.get("issues",[]))
name=c["export"]["road_object"];cur=s.objects[name]
before_o=set(bpy.data.objects);before_m=set(bpy.data.meshes);before_mat=set(bpy.data.materials)
with bpy.data.libraries.load(str(root/"blender/salvador_lacerda_r30b41_perfil_misericordia.blend"),link=False) as (a,b):b.objects=[name]
old=b.objects[0]
M=wm(cur)
def tree_from(ob,use_current_matrix=False):
 me=ob.data;me.calc_loop_triangles();MM=M if use_current_matrix else wm(ob)
 return BVHTree.FromPolygons([MM@v.co for v in me.vertices],[list(t.vertices) for t in me.loop_triangles],all_triangles=True)
t42=tree_from(cur);t41=tree_from(old,True)
vehicle=next(v for v in json.loads((root/"world/vehicles/catalog.json").read_text(encoding="utf8"))["vehicles"] if v["asset_id"]=="vehicle-rondesp-pickup")["authoring_base"]
with bpy.data.libraries.load(str(root/vehicle["file"]),link=True) as (a,b):b.objects=[n for n in a.objects if "Eixo giro roda" in n]
contacts=[list(wm(o).translation) for o in b.objects];midy=(max(x[1] for x in contacts)+min(x[1] for x in contacts))/2
road=s.objects["R30A7 | ROAD | 803899198"];pts=[wm(road)@Vector(p.co[:3]) for sp in road.data.splines for p in sp.points]
q=Vector(sm["point"])
best=None
for a,b in zip(pts,pts[1:]):
 d=(b-a).to_2d();L2=d.length_squared
 if L2<1e-9:continue
 u=max(0,min(1,(q.to_2d()-a.to_2d()).dot(d)/L2));p=a.to_2d()+d*u;dist=(q.to_2d()-p).length
 if best is None or dist<best[0]:best=(dist,d.normalized())
f=best[1];sx=Vector((-f.y,f.x));wheels=[]
for wi,(px,py,pz) in enumerate(contacts):
 xy=q.to_2d()+sx*px-f*(py-midy)
 def hz(tree):
  p=tree.ray_cast(Vector((xy.x,xy.y,q.z+4)),Vector((0,0,-1)),8)[0]
  return None if p is None else float(p.z)
 a,b=hz(t41),hz(t42);wheels.append({"wheel":wi,"xy":[float(xy.x),float(xy.y)],"b41_z":a,"b42_z":b,"delta_m":None if a is None or b is None else b-a})
for ob in list(set(bpy.data.objects)-before_o):
 if ob.name!=cur.name:bpy.data.objects.remove(ob,do_unlink=True)
for me in list(set(bpy.data.meshes)-before_m):
 if me.users==0:bpy.data.meshes.remove(me)
for mat in list(set(bpy.data.materials)-before_mat):
 if mat.users==0:bpy.data.materials.remove(mat)
out={"fraction":sm["fraction"],"center":sm["point"],"grade":sm.get("grade"),"bank":sm.get("bank"),"wheel_residual_m":sm.get("wheel_residual_m"),"wheels":wheels}
(root/"artifacts/roads/rondesp/misericordia_twist_b41_b42.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps(out,ensure_ascii=False))
