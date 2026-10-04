"""Diagnóstico read-only de camadas verticais ground/proxy em apoios críticos B42."""
import bpy,json,runpy,math,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];s=bpy.context.scene
c=json.loads((root/"world/areas/mvp-centro-lacerda/production.json").read_text(encoding="utf8"));wm=runpy.run_path(str(root/"automation/blender/component_fingerprint.py"))["world_matrix"]
audit=json.loads((root/"artifacts/roads/rondesp/rondesp_network_b42_candidate.json").read_text(encoding="utf8"));gph=json.loads((root/c["staging"]["roads"]).read_text(encoding="utf8"));ways={w["osm_way_id"]:w for w in gph["ways"]}
ground=s.objects[c["export"]["road_object"]];proxy=s.objects[c["export"]["terrain_proxy"]]
def tree(ob):
 me=ob.data;me.calc_loop_triangles();return BVHTree.FromPolygons([wm(ob)@v.co for v in me.vertices],[list(t.vertices) for t in me.loop_triangles],all_triangles=True),list(me.loop_triangles)
gt,gtis=tree(ground);pt,ptis=tree(proxy)
vehicle=next(v for v in json.loads((root/"world/vehicles/catalog.json").read_text(encoding="utf8"))["vehicles"] if v["asset_id"]=="vehicle-rondesp-pickup")["authoring_base"]
before=set(bpy.data.objects)
with bpy.data.libraries.load(str(root/vehicle["file"]),link=True) as (a,b):b.objects=[n for n in a.objects if "Eixo giro roda" in n]
contacts=[list(wm(o).translation) for o in b.objects]
for ob in set(bpy.data.objects)-before:
 if not ob.users_scene:bpy.data.objects.remove(ob,do_unlink=True)
midy=(max(x[1] for x in contacts)+min(x[1] for x in contacts))/2
road=s.objects["R30A7 | ROAD | 803899198"];way=ways[803899198];pts=[wm(road)@Vector(p.co[:3]) for sp in road.data.splines for p in sp.points]
a=Vector(way["blender_xy"][1]);b=Vector(way["blender_xy"][2]);ia=min(range(len(pts)),key=lambda i:(pts[i].to_2d()-a).length);ib=min(range(len(pts)),key=lambda i:(pts[i].to_2d()-b).length);poly=pts[ia:ib+1]
lens=[(poly[i+1]-poly[i]).to_2d().length for i in range(len(poly)-1)];cum=[0]
for L in lens:cum.append(cum[-1]+L)
total=cum[-1]
def point_t(frac):
 d=total*frac;j=0
 while j<len(lens)-1 and d>cum[j+1]:j+=1
 u=(d-cum[j])/lens[j];q=poly[j].lerp(poly[j+1],u);f=(poly[j+1]-poly[j]).to_2d().normalized();return q,f
def layers(tree,x,y,zmax,zmin):
 out=[];start=zmax
 for _ in range(8):
  p,n,i,_=tree.ray_cast(Vector((x,y,start)),Vector((0,0,-1)),start-zmin)
  if p is None:break
  out.append({"z":float(p.z),"normal_z":float(n.z),"tri":int(i)});start=float(p.z)-.002
 return out
rows=[]
for frac in (0.0,.2448979592,.3469387755,.4081632653,.75):
 q,f=point_t(frac);sx=Vector((-f.y,f.x))
 wheels=[]
 for wi,(px,py,pz) in enumerate(contacts):
  xy=q.to_2d()+sx*px-f*(py-midy)
  wheels.append({"wheel":wi,"xy":[float(xy.x),float(xy.y)],"ground_layers":layers(gt,xy.x,xy.y,q.z+6,q.z-8),"proxy_layers":layers(pt,xy.x,xy.y,q.z+6,q.z-8)})
 rows.append({"fraction":frac,"center":[float(q.x),float(q.y),float(q.z)],"wheels":wheels})
out=root/"artifacts/roads/rondesp/proxy_layers_b42.json";out.write_text(json.dumps({"rows":rows},ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps(rows,ensure_ascii=False))
