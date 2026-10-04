"""R30B.55: aplica o refino local de crossfall da Manoel Vitórino à superfície B54."""
import bpy,json,hashlib,math,runpy,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

root=Path(__file__).resolve().parents[2]; scene=bpy.context.scene
reg=json.loads((root/"world/areas/mvp-centro-lacerda/blender-revisions.json").read_text(encoding="utf8")); src=reg["validation_source"]
assert src["revision"]=="R30B.54"; assert Path(bpy.data.filepath).resolve()==(root/src["file"]).resolve()
out=root/"blender/salvador_lacerda_r30b55_gameplay_costeiro.blend"; assert not out.exists()
data=np.load(root/"artifacts/waterfront/coastal_integrated_surface_b55.npz")
patch=json.loads((root/"artifacts/waterfront/coastal_integrated_surface_b55.json").read_text(encoding="utf8"))
contract=json.loads((root/"world/areas/mvp-centro-lacerda/coastal-gameplay-b51.json").read_text(encoding="utf8"))
gx=data["gx"]; gy=data["gy"]; H=data["H"]; mask=data["mask"]

api=runpy.run_path(str(root/"automation/blender/component_fingerprint.py")); sig=api["signature"]
ground=scene.objects["MVP | terreno corrigido | colisão estática"]
water=scene.objects["BAÍA DE TODOS-OS-SANTOS | superfície e recorte costeiro"]
quay=scene.objects["CAIS | contenção costeira alinhada à linha de costa"]
piers=[o for o in scene.objects if o.name.startswith("PIER OSM |")]
protected={o.name:sig(o) for o in [ground,water,quay,*piers]}

old=scene.objects["B54 | GAMEPLAY TERRAIN | costa + vias refinadas"]
c_visual=bpy.data.collections["38.1 GAMEPLAY | TERRAIN"]; c_collision=bpy.data.collections["38.2 GAMEPLAY | TERRAIN COLLISION"]; c_graph=bpy.data.collections["38.5 GAMEPLAY | ROAD GRAPH"]

ob=old.copy(); ob.data=old.data.copy(); ob.animation_data_clear()
ob.name="B55 | GAMEPLAY TERRAIN | costa + vias refinadas"
c_visual.objects.link(ob)
changed_vertices=0; max_applied=0.0
for v in ob.data.vertices:
    p=ob.matrix_world@v.co
    i=int(round((float(p.x)-float(gx[0]))/2.0)); j=int(round((float(p.y)-float(gy[0]))/2.0))
    assert 0<=i<len(gx) and 0<=j<len(gy) and mask[j,i]
    target=float(H[j,i])
    delta=abs(target-float(p.z))
    if delta>1e-8:
        v.co.z=target
        changed_vertices+=1; max_applied=max(max_applied,delta)
ob.data.update()
ob["boas_revision"]="R30B.55"; ob["boas_crossfall_patch_way_id"]=456471269
ob["boas_crossfall_patch_max_delta_m"]=float(patch["maximum_vertex_delta_m"]); ob["boas_gameplay_approved"]=False

cp=ob.copy(); cp.data=ob.data.copy(); cp.animation_data_clear(); cp.name="B55 | COLLISION | costa + vias refinadas"
c_collision.objects.link(cp); cp.hide_render=True; cp.hide_viewport=True
cp["boas_runtime_role"]="static_collision_candidate"; cp["boas_source_visual"]=ob.name; cp["boas_geometry_identical"]=True
ob["boas_collision_partner"]=cp.name

for oldob in scene.objects:
    if oldob.name.startswith("B54 | GAMEPLAY TERRAIN |") or oldob.name.startswith("B54 | COLLISION |") or oldob.name.startswith("B54 | GRAPH |"):
        oldob.hide_viewport=True; oldob.hide_render=True; oldob["boas_superseded_by"]="R30B.55"

def mk(o):
    m=o.data; m.calc_loop_triangles()
    return BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[list(t.vertices) for t in m.loop_triangles],all_triangles=True)
nt,ot=mk(ob),mk(ground)
def hit_union(x,y):
    a=nt.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),500)[0]
    b=ot.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),500)[0]
    if a is None:return b
    if b is None:return a
    return a if a.z>=b.z else b

graph_rows=[]
for rec in contract["roads"]:
    pts=[Vector((float(x),float(y),0)) for x,y in rec["blender_xy"]]; samples=[]
    for si,(a,b) in enumerate(zip(pts,pts[1:])):
        d=b-a; L=d.to_2d().length
        if L<.01:continue
        count=max(1,math.ceil(L/2))
        for q in range(count+1):
            if si>0 and q==0:continue
            p=a+d*(q/count); h=hit_union(p.x,p.y)
            samples.append(Vector((p.x,p.y,h.z+.04)) if h else None)
    runs=[]; cur=[]
    for p in samples:
        if p is None:
            if len(cur)>=2:runs.append(cur)
            cur=[]; continue
        if cur and (p.to_2d()-cur[-1].to_2d()).length>4.5:
            if len(cur)>=2:runs.append(cur)
            cur=[]
        cur.append(p)
    if len(cur)>=2:runs.append(cur)
    names=[]
    for ri,run in enumerate(runs):
        cu=bpy.data.curves.new(f"B55 GRAPH {rec['osm_way_id']} {ri}","CURVE"); cu.dimensions="3D"
        sp=cu.splines.new("POLY"); sp.points.add(len(run)-1)
        for q,co in zip(sp.points,run): q.co=(*co,1)
        go=bpy.data.objects.new(f"B55 | GRAPH | {rec['osm_way_id']} | run {ri}",cu); c_graph.objects.link(go); go.hide_render=True
        go["boas_osm_way_id"]=int(rec["osm_way_id"]); go["boas_runtime_role"]="navigation_path"; go["boas_role"]=rec["role"]
        go["boas_direction"]="forward" if rec["oneway"]=="yes" else "both"; go["boas_access"]=rec["access"] or "candidate"
        names.append(go.name)
    graph_rows.append({"osm_way_id":rec["osm_way_id"],"runs":len(runs),"objects":names})

changed=[n for n,b in protected.items() if sig(scene.objects[n])!=b]; assert not changed,changed
scene["boas_validation_revision"]="R30B.55"; scene["boas_all_generated_terrain_gameplay"]=True
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
sha=hashlib.sha256(out.read_bytes()).hexdigest()
report={
 "schema":"boas/manoel-vitorino-r30b55-v1","source_before":src,
 "source_after":{"file":out.relative_to(root).as_posix(),"revision":"R30B.55","sha256":sha},
 "surface_object":ob.name,"collision_object":cp.name,
 "changed_vertices_scene":changed_vertices,"maximum_applied_delta_m":max_applied,
 "patch":patch,"graph":graph_rows,"graph_way_count":sum(1 for r in graph_rows if r["runs"]),
 "existing_ground_changed":False,"water_changed":False,"quay_changed":False,"piers_changed":False,"protected_changes":changed,
 "runtime_exported":False,"approved":False,
 "pending":["Auditoria geométrica final B55","Chunking/streaming após gate final"]
}
(root/"docs/reports/blender/manoel_vitorino_r30b55.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps({"revision":"R30B.55","sha256":sha,"changed_vertices":changed_vertices,"max_delta_m":max_applied,"graph_way_count":report["graph_way_count"],"protected_changes":changed},ensure_ascii=False))
