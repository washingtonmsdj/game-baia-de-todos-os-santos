"""R30B.43: batch único de suportes coplanares na Misericórdia e alinhamento do proxy."""
import bpy,bmesh,json,hashlib,runpy,math,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

root=Path(__file__).resolve().parents[2]
scene=bpy.context.scene
registry_path=root/"world/areas/mvp-centro-lacerda/blender-revisions.json"
reg=json.loads(registry_path.read_text(encoding="utf8"))
src=reg["validation_source"]
assert src["revision"]=="R30B.42"
assert Path(bpy.data.filepath).resolve()==(root/src["file"]).resolve()
out=root/"blender/salvador_lacerda_r30b43_twist_misericordia.blend"
assert not out.exists()

contract=json.loads((root/"world/areas/mvp-centro-lacerda/production.json").read_text(encoding="utf8"))
api=runpy.run_path(str(root/"automation/blender/component_fingerprint.py"))
wm=api["world_matrix"]; signature=api["signature"]
ground=scene.objects[contract["export"]["road_object"]]
proxy=scene.objects[contract["export"]["terrain_proxy"]]
miser=scene.objects["R30A7 | ROAD | 803899198"]
protected={o.name:signature(o) for o in scene.objects if o.type in {"MESH","CURVE","FONT"} and o not in {ground,proxy}}
def degenerate_count(ob):
    ob.data.calc_loop_triangles()
    xyz=np.array([list(v.co) for v in ob.data.vertices],dtype=np.float64)
    tri=np.array([list(t.vertices) for t in ob.data.loop_triangles],dtype=np.int32)
    areas=np.linalg.norm(np.cross(xyz[tri[:,1]]-xyz[tri[:,0]],xyz[tri[:,2]]-xyz[tri[:,0]]),axis=1)*.5
    return int(np.sum(areas<1e-10))
ground_degenerate_before=degenerate_count(ground)
proxy_degenerate_before=degenerate_count(proxy)
audit=json.loads((root/"artifacts/roads/rondesp/rondesp_network_b42_candidate.json").read_text(encoding="utf8"))
rec=next(r for r in audit["segments"] if r["edge_id"]=="way-803899198-seg-1")
sample=next(x for x in rec["samples"] if "four_wheel_twist" in x.get("issues",[]))
q=Vector(sample["point"])
vehicle=next(v for v in json.loads((root/"world/vehicles/catalog.json").read_text(encoding="utf8"))["vehicles"] if v["asset_id"]=="vehicle-rondesp-pickup")["authoring_base"]
before_o=set(bpy.data.objects)
with bpy.data.libraries.load(str(root/vehicle["file"]),link=True) as (available,requested):
    requested.objects=[n for n in available.objects if "Eixo giro roda" in n]
contacts=[list(wm(o).translation) for o in requested.objects]
assert len(contacts)==4
for ob in set(bpy.data.objects)-before_o:
    if not ob.users_scene:bpy.data.objects.remove(ob,do_unlink=True)
midy=(max(x[1] for x in contacts)+min(x[1] for x in contacts))/2
pts=[wm(miser)@Vector(p.co[:3]) for sp in miser.data.splines for p in sp.points]
def tangent_at(point):
    best=None
    for a,b in zip(pts,pts[1:]):
        d=(b-a).to_2d(); L2=d.length_squared
        if L2<1e-9:continue
        t=max(0,min(1,(point.to_2d()-a.to_2d()).dot(d)/L2))
        p=a.to_2d()+d*t; dist=(point.to_2d()-p).length
        if best is None or dist<best[0]:best=(dist,d.normalized())
    return best[1]
forward=tangent_at(q); side=Vector((-forward.y,forward.x))
wheel_xy=[q.to_2d()+side*px-forward*(py-midy) for px,py,pz in contacts]
road_slots={i for i,m in enumerate(ground.data.materials) if m and m.name in contract["export"]["road_materials"]}
def mesh_tree(ob):
    me=ob.data; me.calc_loop_triangles()
    verts=[wm(ob)@v.co for v in me.vertices]
    tris=list(me.loop_triangles)
    tree=BVHTree.FromPolygons(verts,[list(t.vertices) for t in tris],all_triangles=True)
    return tree,tris

gtree,gtris=mesh_tree(ground)
wheel_hits=[]
for xy in wheel_xy:
    p,n,idx,_=gtree.ray_cast(Vector((xy.x,xy.y,q.z+4)),Vector((0,0,-1)),8)
    assert p is not None
    poly=ground.data.polygons[gtris[idx].polygon_index]
    assert poly.material_index in road_slots
    wheel_hits.append((xy,float(p.z),gtris[idx].polygon_index))
assert len({x[2] for x in wheel_hits})==4
A=np.array([[xy.x,xy.y,1.0] for xy,z,pi in wheel_hits],dtype=float)
Z=np.array([z for xy,z,pi in wheel_hits],dtype=float)
coef=np.linalg.lstsq(A,Z,rcond=None)[0]
plane=lambda x,y:float(coef[0]*x+coef[1]*y+coef[2])
before_residual=list(Z-A@coef)
before_twist=max(abs(x) for x in before_residual)
targets=[(xy,plane(xy.x,xy.y),pi,z) for xy,z,pi in wheel_hits]

gM=wm(ground); gInv=gM.inverted()
bm=bmesh.new(); bm.from_mesh(ground.data); bm.faces.ensure_lookup_table()
faces=[bm.faces[pi] for xy,tz,pi,z0 in targets]
created=[]
for face,(xy,tz,pi,z0) in zip(faces,targets):
    result=bmesh.ops.poke(bm,faces=[face],offset=0,use_relative_offset=False)
    v=result["verts"][0]
    v.co=gInv@Vector((xy.x,xy.y,tz))
    created.append(v)
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
bm.to_mesh(ground.data); bm.free(); ground.data.update()
gtree,gtris=mesh_tree(ground)
after_ground=[]
for xy,tz,pi,z0 in targets:
    p,n,idx,_=gtree.ray_cast(Vector((xy.x,xy.y,q.z+4)),Vector((0,0,-1)),8)
    assert p is not None
    poly=ground.data.polygons[gtris[idx].polygon_index]
    assert poly.material_index in road_slots
    after_ground.append(float(p.z))
Z2=np.array(after_ground,dtype=float)
coef2=np.linalg.lstsq(A,Z2,rcond=None)[0]
after_residual=list(Z2-A@coef2)
after_twist=max(abs(x) for x in after_residual)
assert after_twist<0.02,(before_twist,after_twist)
ptree,ptris=mesh_tree(proxy)
proxy_candidates={}
for rec2 in audit["segments"]:
    if rec2["edge_id"] not in {"way-803899198-seg-0","way-803899198-seg-1"}:
        continue
    for sm in rec2.get("samples",[]):
        if "collision_visual_difference" not in sm.get("issues",[]):
            continue
        qq=Vector(sm["point"])
        f=tangent_at(qq); sx=Vector((-f.y,f.x))
        for px,py,pz in contacts:
            xy=qq.to_2d()+sx*px-f*(py-midy)
            gp,gn,gidx,_=gtree.ray_cast(Vector((xy.x,xy.y,qq.z+4)),Vector((0,0,-1)),8)
            if gp is None:
                continue
            gpoly=ground.data.polygons[gtris[gidx].polygon_index]
            if gpoly.material_index not in road_slots:
                continue
            pp,pn,pidx,_=ptree.ray_cast(Vector((xy.x,xy.y,gp.z+4)),Vector((0,0,-1)),8)
            if pp is None:
                continue
            diff=abs(pp.z-gp.z)
            if diff<=.035:
                continue
            pi=ptris[pidx].polygon_index
            prev=proxy_candidates.get(pi)
            row=(xy,float(gp.z),float(diff),pi)
            if prev is None or diff>prev[2]:
                proxy_candidates[pi]=row
assert proxy_candidates
pM=wm(proxy); pInv=pM.inverted()
pbm=bmesh.new(); pbm.from_mesh(proxy.data); pbm.faces.ensure_lookup_table()
proxy_rows=list(proxy_candidates.values())
pfaces=[pbm.faces[pi] for xy,tz,diff,pi in proxy_rows]
for face,(xy,tz,diff,pi) in zip(pfaces,proxy_rows):
    result=bmesh.ops.poke(pbm,faces=[face],offset=0,use_relative_offset=False)
    v=result["verts"][0]
    v.co=pInv@Vector((xy.x,xy.y,tz))
bmesh.ops.recalc_face_normals(pbm,faces=list(pbm.faces))
pbm.to_mesh(proxy.data); pbm.free(); proxy.data.update()

ptree,ptris=mesh_tree(proxy)
proxy_after=[]
for xy,tz,diff,pi in proxy_rows:
    pp,pn,pidx,_=ptree.ray_cast(Vector((xy.x,xy.y,tz+4)),Vector((0,0,-1)),8)
    assert pp is not None
    proxy_after.append(abs(pp.z-tz))
assert max(proxy_after,default=0)<.04
def degenerate_count(ob):
    ob.data.calc_loop_triangles()
    xyz=np.array([list(v.co) for v in ob.data.vertices],dtype=np.float64)
    tri=np.array([list(t.vertices) for t in ob.data.loop_triangles],dtype=np.int32)
    areas=np.linalg.norm(np.cross(xyz[tri[:,1]]-xyz[tri[:,0]],xyz[tri[:,2]]-xyz[tri[:,0]]),axis=1)*.5
    return int(np.sum(areas<1e-10))

ground_degenerate=degenerate_count(ground)
proxy_degenerate=degenerate_count(proxy)
assert ground_degenerate<=ground_degenerate_before,(ground_degenerate_before,ground_degenerate)
assert proxy_degenerate<=proxy_degenerate_before,(proxy_degenerate_before,proxy_degenerate)
changed_protected=[n for n,sig in protected.items() if n not in scene.objects or signature(scene.objects[n])!=sig]
assert not changed_protected,changed_protected
scene["boas_authoring_revision"]="R30B.43"
scene["boas_misericordia_twist_status"]="batch_exact_supports_validation_candidate"
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
sha=hashlib.sha256(out.read_bytes()).hexdigest()

report={
 "schema":"boas/misericordia-twist-r30b43-v3",
 "source_before":src,
 "source_after":{"file":out.relative_to(root).as_posix(),"revision":"R30B.43","sha256":sha},
 "classification":"ADAPT_LOCAL",
 "sample_fraction":sample["fraction"],
 "maximum_plane_residual_before_m":float(before_twist),
 "maximum_plane_residual_after_m":float(after_twist),
 "ground_support_moves_m":[float(tz-z0) for xy,tz,pi,z0 in targets],
 "maximum_ground_support_move_m":float(max(abs(tz-z0) for xy,tz,pi,z0 in targets)),
 "proxy_faces_refined":len(proxy_rows),
 "maximum_proxy_error_before_m":float(max((x[2] for x in proxy_rows),default=0)),
 "maximum_proxy_error_after_m":float(max(proxy_after,default=0)),
 "ground_degenerate_triangles_lt_1e10":ground_degenerate,
 "proxy_degenerate_triangles_lt_1e10":proxy_degenerate,
 "source_xy_changed":False,
 "material_assignments_changed":False,
 "road_widths_changed":False,
 "protected_changes":changed_protected,
 "runtime_exported":False,
 "approved":False,
 "pending":["Reabrir B43 e repetir auditoria integral de 743 segmentos","Crossfall continua gate separado","Largura real continua não verificada"]
}
report_path=root/"docs/reports/blender/misericordia_twist_r30b43.json"
report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
reg=json.loads(registry_path.read_text(encoding="utf8"))
assert reg["authoring_source"]["revision"]=="R30B.41"
for row in reg["revisions"]:
    if row.get("revision")=="R30B.42":
        row["status"]="superseded_validation"
        row["notes"]="Substituída em validação pela R30B.43 após regressão local de four-wheel twist; preservada como evidência."
assert not any(row.get("revision")=="R30B.43" for row in reg["revisions"])
entry={
 "file":report["source_after"]["file"],
 "revision":"R30B.43",
 "status":"validation_candidate",
 "parent_file":src["file"],
 "evidence":"docs/reports/blender/misericordia_twist_r30b43.json",
 "sha256":sha,
 "notes":"Batch local de quatro apoios coplanares e proxy alinhado nos pontos afetados; não promovida a autoria/runtime/gameplay."
}
reg["revisions"].append(entry)
reg["validation_source"]=entry.copy()
registry_path.write_text(json.dumps(reg,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps({"file":entry,"before_twist":before_twist,"after_twist":after_twist,"proxy_faces_refined":len(proxy_rows),"max_proxy_after":max(proxy_after,default=0)},ensure_ascii=False))
