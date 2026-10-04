"""Compara apoios de roda na Ladeira da Misericórdia entre B41 e B42, read-only."""
import bpy,json,runpy
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];s=bpy.context.scene
c=json.loads((root/"world/areas/mvp-centro-lacerda/production.json").read_text(encoding="utf8"));wm=runpy.run_path(str(root/"automation/blender/component_fingerprint.py"))["world_matrix"]
audit=json.loads((root/"artifacts/roads/rondesp/rondesp_network_b42_candidate.json").read_text(encoding="utf8"));graph=json.loads((root/c["staging"]["roads"]).read_text(encoding="utf8"));ways={w["osm_way_id"]:w for w in graph["ways"]}
name=c["export"]["road_object"];current=s.objects[name]
before_o=set(bpy.data.objects);before_m=set(bpy.data.meshes);before_mat=set(bpy.data.materials)
with bpy.data.libraries.load(str(root/"blender/salvador_lacerda_r30b41_perfil_misericordia.blend"),link=False) as (src,dst):dst.objects=[name]
old=dst.objects[0]
def tree(ob):
 me=ob.data;me.calc_loop_triangles();return BVHTree.FromPolygons([wm(ob)@v.co for v in me.vertices],[list(t.vertices) for t in me.loop_triangles],all_triangles=True)
t42=tree(current);t41=tree(old)
vehicle=next(v for v in json.loads((root/"world/vehicles/catalog.json").read_text(encoding="utf8"))["vehicles"] if v["asset_id"]=="vehicle-rondesp-pickup")["authoring_base"]
with bpy.data.libraries.load(str(root/vehicle["file"]),link=True) as (a,b):b.objects=[n for n in a.objects if "Eixo giro roda" in n]
contacts=[list(wm(o).translation) for o in b.objects];midy=(max(x[1] for x in contacts)+min(x[1] for x in contacts))/2
road=s.objects["R30A7 | ROAD | 103595139"];way=ways[103595139];pts=[wm(road)@Vector(p.co[:3]) for sp in road.data.splines for p in sp.points]
def tangent(q):
 best=None
 for a,b in zip(pts,pts[1:]):
  d=(b-a).to_2d();L2=d.length_squared
  if L2<1e-9:continue
  u=max(0,min(1,(q.to_2d()-a.to_2d()).dot(d)/L2));p=a.to_2d()+d*u;dist=(q.to_2d()-p).length
  if best is None or dist<best[0]:best=(dist,d.normalized())
 return best[1]
rows=[]
for rec in audit["segments"]:
 if rec["edge_id"] not in {"way-103595139-seg-0","way-103595139-seg-1"}:continue
 for sm in rec["samples"]:
  if "four_wheel_twist" not in sm.get("issues",[]):continue
  q=Vector(sm["point"]);f=tangent(q);sx=Vector((-f.y,f.x));ws=[]
  for wi,(px,py,pz) in enumerate(contacts):
   xy=q.to_2d()+sx*px-f*(py-midy)
   def hit(tree):
    p=tree.ray_cast(Vector((xy.x,xy.y,q.z+4)),Vector((0,0,-1)),8)[0];return None if p is None else float(p.z)
   a,b=hit(t41),hit(t42);ws.append({"wheel":wi,"xy":[float(xy.x),float(xy.y)],"b41_z":a,"b42_z":b,"delta_m":None if a is None or b is None else b-a})
  rows.append({"edge":rec["edge_id"],"fraction":sm["fraction"],"center":sm["point"],"wheels":ws})
# clean appended data
for ob in list(set(bpy.data.objects)-before_o):
 if ob.name!=current.name:bpy.data.objects.remove(ob,do_unlink=True)
for me in list(set(bpy.data.meshes)-before_m):
 if me.users==0:bpy.data.meshes.remove(me)
for mat in list(set(bpy.data.materials)-before_mat):
 if mat.users==0:bpy.data.materials.remove(mat)
(root/"artifacts/roads/rondesp/ladeira_wheels_b41_b42.json").write_text(json.dumps({"rows":rows},ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps(rows,ensure_ascii=False))
