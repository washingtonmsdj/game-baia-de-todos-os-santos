"""B42: insere suportes no proxy somente nos apoios de roda ainda divergentes nos cinco segmentos afetados."""
import bpy,bmesh,json,hashlib,runpy,math,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];s=bpy.context.scene
registry_path=root/"world/areas/mvp-centro-lacerda/blender-revisions.json";reg=json.loads(registry_path.read_text(encoding="utf8"));src=reg["validation_source"]
assert src["revision"]=="R30B.42";assert Path(bpy.data.filepath).resolve()==(root/src["file"]).resolve()
rp=root/"docs/reports/blender/misericordia_surface_r30b42.json";report=json.loads(rp.read_text(encoding="utf8"))
c=json.loads((root/"world/areas/mvp-centro-lacerda/production.json").read_text(encoding="utf8"));wm=runpy.run_path(str(root/"automation/blender/component_fingerprint.py"))["world_matrix"]
audit=json.loads((root/"artifacts/roads/rondesp/rondesp_network_b42_candidate.json").read_text(encoding="utf8"));gph=json.loads((root/c["staging"]["roads"]).read_text(encoding="utf8"));ways={w["osm_way_id"]:w for w in gph["ways"]};edges={e["id"]:e for e in gph["edges"]}
ground=s.objects[c["export"]["road_object"]];proxy=s.objects[c["export"]["terrain_proxy"]]
affected={"way-803899198-seg-0","way-803899198-seg-1","way-103595139-seg-0","way-103595139-seg-1","way-231091548-seg-0"}
# Vehicle contacts.
vehicle=next(v for v in json.loads((root/"world/vehicles/catalog.json").read_text(encoding="utf8"))["vehicles"] if v["asset_id"]=="vehicle-rondesp-pickup")["authoring_base"]
before=set(bpy.data.objects)
with bpy.data.libraries.load(str(root/vehicle["file"]),link=True) as (available,requested):requested.objects=[n for n in available.objects if "Eixo giro roda" in n]
contacts=[list(wm(o).translation) for o in requested.objects];assert len(contacts)==4
for ob in set(bpy.data.objects)-before:
 if not ob.users_scene:bpy.data.objects.remove(ob,do_unlink=True)
midy=(max(x[1] for x in contacts)+min(x[1] for x in contacts))/2
# Trees.
def make_tree(ob):
 me=ob.data;me.calc_loop_triangles();tri=list(me.loop_triangles)
 return BVHTree.FromPolygons([wm(ob)@v.co for v in me.vertices],[list(t.vertices) for t in tri],all_triangles=True),tri
gtree,gtris=make_tree(ground);slots={i for i,m in enumerate(ground.data.materials) if m and m.name in c["export"]["road_materials"]}
def ground_hit(x,y,z):
 p,n,i,_=gtree.ray_cast(Vector((x,y,z+2)),Vector((0,0,-1)),4)
 return None if p is None or n.z<=.70 or gtris[i].material_index not in slots else p
roads={int(o["boas_osm_way_id"]):o for o in s.objects if o.name.startswith("R30A7 | ROAD |") and "boas_osm_way_id" in o}
def edge_poly(edge):
 way=ways[edge["osm_way_id"]];k=int(edge["id"].rsplit("-",1)[-1]);pts=[wm(roads[edge["osm_way_id"]])@Vector(p.co[:3]) for sp in roads[edge["osm_way_id"]].data.splines for p in sp.points]
 a=Vector(way["blender_xy"][k]);b=Vector(way["blender_xy"][k+1]);ia=[i for i,p in enumerate(pts) if (p.to_2d()-a).length<.02];ib=[i for i,p in enumerate(pts) if (p.to_2d()-b).length<.02];found=[]
 for i in ia:
  for j in ib:
   if i<j:found.append(pts[i:j+1])
   elif j<i:found.append(list(reversed(pts[j:i+1])))
 return found[0] if len(found)==1 else [pts[k],pts[k+1]]
def tangent(poly,q):
 best=None
 for a,b in zip(poly,poly[1:]):
  d=(b-a).to_2d();L2=d.length_squared
  if L2<1e-9:continue
  t=max(0,min(1,(q.to_2d()-a.to_2d()).dot(d)/L2));p=a.to_2d()+d*t;dist=(q.to_2d()-p).length
  if best is None or dist<best[0]:best=(dist,d.normalized())
 return best[1]
# Build precise wheel targets only for flagged samples in affected edges.
ptree,ptris=make_tree(proxy);raw=[]
for rec in audit["segments"]:
 if rec["edge_id"] not in affected:continue
 poly=edge_poly(edges[rec["edge_id"]])
 for sm in rec.get("samples",[]):
  if "collision_visual_difference" not in sm.get("issues",[]):continue
  q=Vector(sm["point"]);f=tangent(poly,q);sx=Vector((-f.y,f.x));center=ground_hit(q.x,q.y,q.z)
  if center is None:continue
  for px,py,pz in contacts:
   xy=q.to_2d()+sx*px-f*(py-midy);gp=ground_hit(xy.x,xy.y,center.z)
   if gp is None:continue
   pp=ptree.ray_cast(Vector((xy.x,xy.y,gp.z+2)),Vector((0,0,-1)),4)[0]
   diff=999 if pp is None else abs(pp.z-gp.z)
   if diff>.035:raw.append((diff,Vector((xy.x,xy.y,gp.z))))
uniq={}
for diff,p in raw:
 key=(round(p.x,3),round(p.y,3));prev=uniq.get(key)
 if prev is None or diff>prev[0]:uniq[key]=(diff,p)
targets=sorted(uniq.values(),key=lambda x:x[0],reverse=True);assert targets
# Baseline topology.
proxy.data.calc_loop_triangles();xyz=np.array([list(v.co) for v in proxy.data.vertices],dtype=np.float64);tri=np.array([list(t.vertices) for t in proxy.data.loop_triangles],dtype=np.int32)
areas=np.linalg.norm(np.cross(xyz[tri[:,1]]-xyz[tri[:,0]],xyz[tri[:,2]]-xyz[tri[:,0]]),axis=1)*.5;baseline_lt=int(np.sum(areas<1e-10));before_v=len(proxy.data.vertices);before_f=len(proxy.data.polygons)
pinv=wm(proxy).inverted();pokes=splits=skips=0
for initial_diff,point in targets:
 tree,tris=make_tree(proxy);hit,n,idx,_=tree.ray_cast(point+Vector((0,0,4)),Vector((0,0,-1)),8)
 if hit is not None and abs(hit.z-point.z)<=.035:skips+=1;continue
 if hit is None:raise RuntimeError("Proxy sem face sob target após densificação")
 bm=bmesh.new();bm.from_mesh(proxy.data);bm.faces.ensure_lookup_table();face=bm.faces[tris[idx].polygon_index];local=pinv@point
 candidates=[]
 for e in face.edges:
  a,b=[v.co.to_2d() for v in e.verts];d=b-a;t=max(0,min(1,(local.to_2d()-a).dot(d)/max(d.length_squared,1e-12)));xy=a+d*t;candidates.append(((local.to_2d()-xy).length,e,t))
 dist,e,t=min(candidates,key=lambda x:x[0])
 if dist<.002 and .0001<t<.9999:
  _,v=bmesh.utils.edge_split(e,e.verts[0],t);v.co=local;splits+=1
 else:
  created=bmesh.ops.poke(bm,faces=[face],offset=0,use_relative_offset=False);created["verts"][0].co=local;pokes+=1
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(proxy.data);bm.free();proxy.data.update()
# Verify exact targets and topology before save.
tree,tris=make_tree(proxy);errors=[];missing=0
for _,point in targets:
 hit=tree.ray_cast(point+Vector((0,0,2)),Vector((0,0,-1)),4)[0]
 if hit is None:missing+=1
 else:errors.append(abs(hit.z-point.z))
proxy.data.calc_loop_triangles();xyz=np.array([list(v.co) for v in proxy.data.vertices],dtype=np.float64);tri=np.array([list(t.vertices) for t in proxy.data.loop_triangles],dtype=np.int32);areas=np.linalg.norm(np.cross(xyz[tri[:,1]]-xyz[tri[:,0]],xyz[tri[:,2]]-xyz[tri[:,0]]),axis=1)*.5
after_lt=int(np.sum(areas<1e-10));assert not missing and max(errors,default=0)<.051 and after_lt<=baseline_lt
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True);sha=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()
entry={"method":"targeted wheel supports after batch subdivision","affected_edges":sorted(affected),"raw_targets":len(raw),"unique_targets":len(targets),"pokes":pokes,"edge_splits":splits,"already_within_35mm":skips,"vertices_before":before_v,"vertices_after":len(proxy.data.vertices),"faces_before":before_f,"faces_after":len(proxy.data.polygons),"maximum_target_error_m":max(errors,default=0),"missing_targets":missing,"degenerate_lt_1e10_before":baseline_lt,"degenerate_lt_1e10_after":after_lt}
report["source_after"]["sha256"]=sha;report.setdefault("proxy_refinement_history",[]).append(report.get("proxy_refinement"));report["proxy_target_refinement"]=entry
rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
reg=json.loads(registry_path.read_text(encoding="utf8"));reg["validation_source"]["sha256"]=sha
for row in reg["revisions"]:
 if row.get("revision")=="R30B.42":row["sha256"]=sha
registry_path.write_text(json.dumps(reg,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps({"sha256":sha,**entry},ensure_ascii=False))
