"""Refina o proxy B42 somente nos apoios de roda com falha/diferença após a correção da Misericórdia."""
import bpy,bmesh,json,math,hashlib,runpy
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];scene=bpy.context.scene
rp=root/"docs/reports/blender/misericordia_surface_r30b42.json";report=json.loads(rp.read_text(encoding="utf8"))
assert report["source_after"]["revision"]=="R30B.42";assert Path(bpy.data.filepath).resolve()==(root/report["source_after"]["file"]).resolve()
contract=json.loads((root/"world/areas/mvp-centro-lacerda/production.json").read_text(encoding="utf8"))
audit=json.loads((root/"artifacts/roads/rondesp/rondesp_network_b42_candidate.json").read_text(encoding="utf8"))
graph=json.loads((root/contract["staging"]["roads"]).read_text(encoding="utf8"));ways={w["osm_way_id"]:w for w in graph["ways"]}
wm=runpy.run_path(str(root/"automation/blender/component_fingerprint.py"))["world_matrix"]
ground=scene.objects[contract["export"]["road_object"]];proxy=scene.objects[contract["export"]["terrain_proxy"]]
# Quatro apoios reais da Rondesp.
vehicle=next(v for v in json.loads((root/"world/vehicles/catalog.json").read_text(encoding="utf8"))["vehicles"] if v["asset_id"]=="vehicle-rondesp-pickup")["authoring_base"]
before=set(bpy.data.objects)
with bpy.data.libraries.load(str(root/vehicle["file"]),link=True) as (available,requested):
 requested.objects=[n for n in available.objects if "Eixo giro roda" in n or "Pneu 265 65 R17" in n]
pivots=[o for o in requested.objects if "Eixo giro roda" in o.name];contacts=[list(wm(o).translation) for o in pivots];assert len(contacts)==4
for ob in set(bpy.data.objects)-before:
 if not ob.users_scene:bpy.data.objects.remove(ob,do_unlink=True)
midy=(max(p[1] for p in contacts)+min(p[1] for p in contacts))/2
# Ground BVH + materiais.
ground.data.calc_loop_triangles();gtri=list(ground.data.loop_triangles)
gtree=BVHTree.FromPolygons([wm(ground)@v.co for v in ground.data.vertices],[list(t.vertices) for t in gtri],all_triangles=True)
slots={i for i,m in enumerate(ground.data.materials) if m and m.name in contract["export"]["road_materials"]}
def ground_hit(x,y,z):
 p,n,i,_=gtree.ray_cast(Vector((x,y,z+4)),Vector((0,0,-1)),8)
 return None if p is None or n.z<=.70 or gtri[i].material_index not in slots else p
roads={int(o["boas_osm_way_id"]):o for o in scene.objects if o.name.startswith("R30A7 | ROAD |") and "boas_osm_way_id" in o}
def edge_poly(edge):
 way=ways[edge["osm_way_id"]];k=int(edge["id"].rsplit("-",1)[-1]);ob=roads[edge["osm_way_id"]]
 pts=[wm(ob)@Vector(p.co[:3]) for sp in ob.data.splines for p in sp.points]
 a=Vector(way["blender_xy"][k]);b=Vector(way["blender_xy"][k+1]);found=[]
 ia=[i for i,p in enumerate(pts) if (p.to_2d()-a).length<.02];ib=[i for i,p in enumerate(pts) if (p.to_2d()-b).length<.02]
 for i in ia:
  for j in ib:
   if i<j:found.append(pts[i:j+1])
   elif j<i:found.append(list(reversed(pts[j:i+1])))
 return found[0] if len(found)==1 else [pts[k],pts[k+1]]
def tangent_at(poly,q):
 best=None
 for a,b in zip(poly,poly[1:]):
  d=(b-a).to_2d();L2=d.length_squared
  if L2<1e-9:continue
  t=max(0,min(1,(q.to_2d()-a.to_2d()).dot(d)/L2));p=a.to_2d()+d*t;dist=(q.to_2d()-p).length
  if best is None or dist<best[0]:best=(dist,d.normalized())
 return best[1]
edges={e["id"]:e for e in graph["edges"]};targets=[]
collision_kinds={"collision_support_missing","collision_visual_difference"}
for rec in audit["segments"]:
 if not any(k in rec.get("issues",{}) for k in collision_kinds):continue
 edge=edges[rec["edge_id"]];poly=edge_poly(edge)
 for s in rec.get("samples",[]):
  if not collision_kinds.intersection(s.get("issues",[])):continue
  q=Vector(s["point"]);f=tangent_at(poly,q);sx=Vector((-f.y,f.x))
  center=ground_hit(q.x,q.y,q.z)
  if center is None:continue
  for px,py,pz in contacts:
   xy=q.to_2d()+sx*px-f*(py-midy);p=ground_hit(xy.x,xy.y,center.z)
   if p is not None:targets.append(Vector((xy.x,xy.y,p.z)))
# dedup espacial.
uniq={}
for p in targets:uniq[(round(p.x,3),round(p.y,3))]=p
targets=list(uniq.values())
def proxy_tree():
 proxy.data.calc_loop_triangles();tri=list(proxy.data.loop_triangles)
 return BVHTree.FromPolygons([wm(proxy)@v.co for v in proxy.data.vertices],[list(t.vertices) for t in tri],all_triangles=True),tri
pinv=wm(proxy).inverted();pokes=splits=0;skipped=[];before_vertices=len(proxy.data.vertices)
for point in targets:
 tree,tri=proxy_tree()
 hit,n,idx,_=tree.ray_cast(point+Vector((0,0,8)),Vector((0,0,-1)),16)
 if hit is None:skipped.append({"point":list(point),"reason":"proxy_no_face_in_16m"});continue
 if abs(hit.z-point.z)<=.035:continue
 bm=bmesh.new();bm.from_mesh(proxy.data);bm.faces.ensure_lookup_table();face=bm.faces[tri[idx].polygon_index]
 candidates=[]
 local=pinv@point
 for edge in face.edges:
  a,b=[v.co.to_2d() for v in edge.verts];d=b-a;t=max(0,min(1,(local.to_2d()-a).dot(d)/max(d.length_squared,1e-12)));xy=a+d*t
  candidates.append(((local.to_2d()-xy).length,edge,t,xy))
 distance,edge,t,xy=min(candidates,key=lambda x:x[0])
 if distance<.003 and .0001<t<.9999:
  _,v=bmesh.utils.edge_split(edge,edge.verts[0],t);world=wm(proxy)@v.co;world.z=point.z;v.co=pinv@world;splits+=1
 else:
  created=bmesh.ops.poke(bm,faces=[face],offset=0,use_relative_offset=False);created["verts"][0].co=local;pokes+=1
 bm.to_mesh(proxy.data);bm.free();proxy.data.update()
# Verificação nos mesmos targets com raio amplo.
tree,tri=proxy_tree();errors=[];missing=0
for point in targets:
 hit=tree.ray_cast(point+Vector((0,0,4)),Vector((0,0,-1)),8)[0]
 if hit is None:missing+=1
 else:errors.append(abs(hit.z-point.z))
assert not missing and (not errors or max(errors)<.051)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
sha=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest();report["source_after"]["sha256"]=sha
report["proxy_refinement"]={"targets":len(targets),"pokes":pokes,"edge_splits":splits,"skipped":skipped,"vertices_before":before_vertices,"vertices_after":len(proxy.data.vertices),"maximum_target_error_m":max(errors,default=0.0),"missing_targets":missing}
report["pending"]=["Reabrir/refazer auditoria integral após refino do proxy","Crossfall/envelope/física continuam gates separados","Largura real não verificada"]
rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps({"sha256":sha,**report["proxy_refinement"]},ensure_ascii=False))
