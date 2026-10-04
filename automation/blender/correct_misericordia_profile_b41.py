"""R30B.41: corrige o perfil vertical derivado da Rua da Misericórdia sem alterar OSM, XY ou pavimento."""
import bpy,json,math,hashlib,runpy,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

root=Path(__file__).resolve().parents[2];scene=bpy.context.scene
catalog=json.loads((root/"world/areas/mvp-centro-lacerda/blender-revisions.json").read_text(encoding="utf8"))
source=catalog["authoring_source"];assert source["revision"]=="R30B.40"
src=root/source["file"];assert Path(bpy.data.filepath).resolve()==src.resolve()
out=root/"blender/salvador_lacerda_r30b41_perfil_misericordia.blend";assert not out.exists()
contract=json.loads((root/"world/areas/mvp-centro-lacerda/production.json").read_text(encoding="utf8"))
graph=json.loads((root/"docs/reports/blender/r30a7/road_graph.json").read_text(encoding="utf8"))
way=next(w for w in graph["ways"] if int(w["osm_way_id"])==803899198)
road=scene.objects["R30A7 | ROAD | 803899198"];ground=scene.objects[contract["export"]["road_object"]]
api=runpy.run_path(str(root/"automation/blender/component_fingerprint.py"));signature=api["signature"];wm=api["world_matrix"]
protected={o.name:signature(o) for o in scene.objects if o.type in {"MESH","CURVE","FONT"} and o!=road}
road_before=signature(road)
old_points=[wm(road)@Vector(p.co[:3]) for sp in road.data.splines for p in sp.points]
assert len(old_points)==len(way["node_refs"])==3
assert all(math.dist(list(p)[:2],xy)<.01 for p,xy in zip(old_points,way["blender_xy"]))

me=ground.data;me.calc_loop_triangles()
a=np.empty(len(me.vertices)*3,dtype=np.float32);me.vertices.foreach_get("co",a)
M=np.array(wm(ground));xyz=a.reshape(-1,3)@M[:3,:3].T+M[:3,3]
a=np.empty(len(me.loop_triangles)*3,dtype=np.int32);me.loop_triangles.foreach_get("vertices",a)
tris=a.reshape(-1,3)
polys=np.empty(len(me.loop_triangles),dtype=np.int32);me.loop_triangles.foreach_get("polygon_index",polys)
midx=np.empty(len(me.polygons),dtype=np.int32);me.polygons.foreach_get("material_index",midx)
tri_mats=midx[polys]
tree=BVHTree.FromPolygons(xyz.tolist(),tris.tolist(),all_triangles=True)
road_slots={i for i,m in enumerate(me.materials) if m and m.name in contract["export"]["road_materials"]}

def surface(x,y):
    p,n,idx,_=tree.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),500)
    if p is None:return None
    mi=int(tri_mats[idx]);mat=me.materials[mi].name if mi<len(me.materials) and me.materials[mi] else None
    return {"point":p,"normal_z":float(n.z),"material_index":mi,"material":mat,"road_material":mi in road_slots}

spacing=.5;clearance=.18;profile=[];samples=[];max_local_grade=0.
for k in range(len(way["blender_xy"])-1):
    p0=Vector((float(way["blender_xy"][k][0]),float(way["blender_xy"][k][1])))
    p1=Vector((float(way["blender_xy"][k+1][0]),float(way["blender_xy"][k+1][1])))
    length=(p1-p0).length;steps=math.ceil(length/spacing)
    local=[]
    for i in range(steps+1):
        if k and i==0:continue
        t=i/steps;q=p0.lerp(p1,t);h=surface(q.x,q.y)
        assert h is not None,"Sem superfície na Misericórdia"
        assert h["road_material"],f"Amostra fora do pavimento: edge {k} t={t} material={h['material']}"
        assert h["normal_z"]>.70,f"Superfície quase vertical: edge {k} t={t} normal_z={h['normal_z']}"
        point=Vector((q.x,q.y,h["point"].z+clearance))
        if profile:
            dxy=(point.to_2d()-profile[-1].to_2d()).length
            if dxy>.001:max_local_grade=max(max_local_grade,abs(point.z-profile[-1].z)/dxy)
        profile.append(point);local.append(point)
        samples.append({"edge_index":k,"fraction":t,"xy":[float(q.x),float(q.y)],"surface_z":float(h["point"].z),"helper_z":float(point.z),"normal_z":h["normal_z"],"material":h["material"]})
assert max_local_grade<.75,f"Perfil sugere salto de camada: grade local {max_local_grade}"
node_indices=[]
for xy in way["blender_xy"]:
    matches=[i for i,p in enumerate(profile) if math.dist(list(p)[:2],xy)<.001]
    assert len(matches)==1
    node_indices.append(matches[0])
for old,idx in zip(old_points,node_indices):
    assert abs((profile[idx].z-clearance)-(old.z-clearance))<.01,"Endpoint mudou de superfície"

old_data=road.data;new_data=old_data.copy();new_data.name="R30A7_ROAD_803899198_B41_PROFILE"
for sp in list(new_data.splines):new_data.splines.remove(sp)
sp=new_data.splines.new("POLY");sp.points.add(len(profile)-1)
inv=wm(road).inverted()
for dst,p in zip(sp.points,profile):
    q=inv@p;dst.co=(*q,1.0)
road.data=new_data
road["boas_binding_revision"]="R30B.41"
road["boas_binding_classification"]="ERROR"
road["boas_profile_method"]="drape derivado a cada <=0.5 m no pavimento funcional; nós/XY OSM preservados"
road["boas_profile_spacing_m"]=spacing
road["boas_profile_clearance_m"]=clearance
road["boas_profile_source_nodes_preserved"]=True
road["boas_profile_xy_source_preserved"]=True
road["boas_profile_max_local_grade"]=float(max_local_grade)
road["boas_gameplay_approved"]=False

changed=[name for name,before in protected.items() if name not in scene.objects or signature(scene.objects[name])!=before]
assert not changed,"Componente protegido alterado: "+str(changed)
assert signature(road)!=road_before
scene["boas_authoring_revision"]="R30B.41"
scene["boas_misericordia_profile_status"]="derived_profile_corrected_not_gameplay_approved"

bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
sha=hashlib.sha256(out.read_bytes()).hexdigest()
report={
 "schema":"boas/misericordia-profile-r30b41-v1","source_before":source,
 "source_after":{"file":out.relative_to(root).as_posix(),"revision":"R30B.41","sha256":sha},
 "classification":"ERROR","osm_way_id":803899198,"name":way.get("name"),"node_refs":[str(x) for x in way["node_refs"]],
 "cause":"Helper R30A7 interpolava Z linearmente apenas entre nós OSM esparsos; o pavimento funcional possui perfil vertical intermediário não linear.",
 "old_helper_points":[list(p) for p in old_points],"new_profile_points":len(profile),"source_node_profile_indices":node_indices,
 "spacing_m":spacing,"clearance_m":clearance,"max_local_grade":float(max_local_grade),
 "surface_z_min":min(x["surface_z"] for x in samples),"surface_z_max":max(x["surface_z"] for x in samples),
 "all_samples_road_material":all(x["material"] in contract["export"]["road_materials"] for x in samples),
 "osm_source_changed":False,"source_xy_changed":False,"road_widths_changed":False,"visual_geometry_changed":False,
 "collision_changed":False,"protected_components":len(protected),"protected_changes":changed,
 "runtime_exported":False,"approved":False,
 "pending":["Auditoria completa de quatro apoios na B41","Validação de grade/crossfall e envelope","Largura real continua não verificada"]
}
(root/"docs/reports/blender/misericordia_profile_r30b41.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps({"file":report["source_after"],"old_points":len(old_points),"new_points":len(profile),"max_local_grade":max_local_grade,"protected":len(protected)},ensure_ascii=False))
