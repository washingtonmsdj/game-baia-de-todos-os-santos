"""R30B.44: corrige somente o proxy de colisão nos apoios divergentes da Misericórdia B43."""
import bpy,bmesh,json,hashlib,runpy,math,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2]; s=bpy.context.scene
srcfile=root/"blender/salvador_lacerda_r30b43_twist_misericordia.blend"
assert Path(bpy.data.filepath).resolve()==srcfile.resolve()
out=root/"blender/salvador_lacerda_r30b44_proxy_misericordia.blend"; assert not out.exists()
report43=json.loads((root/"docs/reports/blender/misericordia_twist_r30b43.json").read_text(encoding="utf8"))
assert hashlib.sha256(srcfile.read_bytes()).hexdigest()==report43["source_after"]["sha256"]
audit=json.loads((root/"artifacts/roads/rondesp/rondesp_network_b43_candidate.json").read_text(encoding="utf8"))
c=json.loads((root/"world/areas/mvp-centro-lacerda/production.json").read_text(encoding="utf8"))
wm=runpy.run_path(str(root/"automation/blender/component_fingerprint.py")); sig=wm["signature"]; world_matrix=wm["world_matrix"]
ground=s.objects[c["export"]["road_object"]]; proxy=s.objects[c["export"]["terrain_proxy"]]
protected_ground=sig(ground); protected_roads={o.name:sig(o) for o in s.objects if o.name.startswith("R30A7 | ROAD |")}
# veículo / contatos
vehicle=next(v for v in json.loads((root/"world/vehicles/catalog.json").read_text(encoding="utf8"))["vehicles"] if v["asset_id"]=="vehicle-rondesp-pickup")["authoring_base"]
before=set(bpy.data.objects)
with bpy.data.libraries.load(str(root/vehicle["file"]),link=True) as (available,requested): requested.objects=[n for n in available.objects if "Eixo giro roda" in n]
contacts=[list(world_matrix(o).translation) for o in requested.objects]; assert len(contacts)==4
for ob in set(bpy.data.objects)-before:
    if not ob.users_scene:bpy.data.objects.remove(ob,do_unlink=True)
midy=(max(x[1] for x in contacts)+min(x[1] for x in contacts))/2

def make_tree(ob):
    me=ob.data; me.calc_loop_triangles(); tri=list(me.loop_triangles)
    return BVHTree.FromPolygons([world_matrix(ob)@v.co for v in me.vertices],[list(t.vertices) for t in tri],all_triangles=True),tri
gtree,gtris=make_tree(ground); slots={i for i,m in enumerate(ground.data.materials) if m and m.name in c["export"]["road_materials"]}
def ghit(x,y,z):
    p,n,i,_=gtree.ray_cast(Vector((x,y,z+2)),Vector((0,0,-1)),4)
    return None if p is None or gtris[i].material_index not in slots else p
# usa exatamente os 3 samples divergentes B43
roads={int(o["boas_osm_way_id"]):o for o in s.objects if o.name.startswith("R30A7 | ROAD |") and "boas_osm_way_id" in o}
gph=json.loads((root/c["staging"]["roads"]).read_text(encoding="utf8")); ways={w["osm_way_id"]:w for w in gph["ways"]}
def tangent_for(rec,sm):
    ob=roads[rec["osm_way_id"]]; pts=[world_matrix(ob)@Vector(p.co[:3]) for sp in ob.data.splines for p in sp.points]
    q=Vector(sm["point"]); best=None
    for a,b in zip(pts,pts[1:]):
        d=(b-a).to_2d(); L2=d.length_squared
        if L2<1e-9: continue
        t=max(0,min(1,(q.to_2d()-a.to_2d()).dot(d)/L2)); pp=a.to_2d()+d*t; dist=(q.to_2d()-pp).length
        if best is None or dist<best[0]: best=(dist,d.normalized())
    return best[1]
ptree,ptris=make_tree(proxy); raw=[]
for rec in audit["segments"]:
    if rec["edge_id"] not in {"way-803899198-seg-0","way-803899198-seg-1"}: continue
    for sm in rec.get("samples",[]):
        if "collision_visual_difference" not in sm.get("issues",[]): continue
        q=Vector(sm["point"]); f=tangent_for(rec,sm); sx=Vector((-f.y,f.x)); center=ghit(q.x,q.y,q.z)
        assert center is not None
        for px,py,pz in contacts:
            xy=q.to_2d()+sx*px-f*(py-midy); gp=ghit(xy.x,xy.y,center.z)
            if gp is None: continue
            pp=ptree.ray_cast(Vector((xy.x,xy.y,gp.z+2)),Vector((0,0,-1)),4)[0]
            diff=999 if pp is None else abs(pp.z-gp.z)
            if diff>.05: raw.append((diff,Vector((xy.x,xy.y,gp.z))))
uniq={}
for diff,p in raw:
    key=(round(p.x,3),round(p.y,3)); prev=uniq.get(key)
    if prev is None or diff>prev[0]: uniq[key]=(diff,p)
targets=sorted(uniq.values(),key=lambda x:x[0],reverse=True); assert targets
proxy.data.calc_loop_triangles(); before_v=len(proxy.data.vertices); before_f=len(proxy.data.polygons)
pinv=world_matrix(proxy).inverted(); pokes=splits=skips=0
for initial_diff,point in targets:
    tree,tris=make_tree(proxy); hit,n,idx,_=tree.ray_cast(point+Vector((0,0,4)),Vector((0,0,-1)),8)
    if hit is not None and abs(hit.z-point.z)<=.035: skips+=1; continue
    assert hit is not None
    bm=bmesh.new(); bm.from_mesh(proxy.data); bm.faces.ensure_lookup_table(); face=bm.faces[tris[idx].polygon_index]; local=pinv@point
    candidates=[]
    for e in face.edges:
        a,b=[v.co.to_2d() for v in e.verts]; d=b-a; t=max(0,min(1,(local.to_2d()-a).dot(d)/max(d.length_squared,1e-12))); xy=a+d*t
        candidates.append(((local.to_2d()-xy).length,e,t))
    dist,e,t=min(candidates,key=lambda x:x[0])
    if dist<.002 and .0001<t<.9999:
        _,v=bmesh.utils.edge_split(e,e.verts[0],t); v.co=local; splits+=1
    else:
        created=bmesh.ops.poke(bm,faces=[face],offset=0,use_relative_offset=False); created["verts"][0].co=local; pokes+=1
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces)); bm.to_mesh(proxy.data); bm.free(); proxy.data.update()
# prova invariantes e erros
assert sig(ground)==protected_ground
assert all(sig(s.objects[n])==v for n,v in protected_roads.items())
tree,tris=make_tree(proxy); errors=[]
for _,point in targets:
    hit=tree.ray_cast(point+Vector((0,0,2)),Vector((0,0,-1)),4)[0]; assert hit is not None; errors.append(abs(hit.z-point.z))
assert max(errors)<.051
s["boas_authoring_revision"]="R30B.44"
s["boas_misericordia_proxy_status"]="local_collision_proxy_refined_gameplay_pending"
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
sha=hashlib.sha256(out.read_bytes()).hexdigest()
report={"schema":"boas/misericordia-proxy-r30b44-v1","source_before":report43["source_after"],"source_after":{"file":out.relative_to(root).as_posix(),"revision":"R30B.44","sha256":sha},"classification":"ERROR","scope":"Somente terrain proxy nos apoios da Rua da Misericórdia divergentes após B43","raw_targets":len(raw),"unique_targets":len(targets),"pokes":pokes,"edge_splits":splits,"already_within_35mm":skips,"vertices_before":before_v,"vertices_after":len(proxy.data.vertices),"faces_before":before_f,"faces_after":len(proxy.data.polygons),"maximum_target_error_m":max(errors),"ground_changed":False,"road_helpers_changed":False,"visual_geometry_changed":False,"road_widths_changed":False,"runtime_exported":False,"approved":False,"pending":["Reabrir B44 e repetir auditoria integral de 743 segmentos","Crossfall/grade/largura real continuam gates separados"]}
(root/"docs/reports/blender/misericordia_proxy_r30b44.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps(report,ensure_ascii=False))
