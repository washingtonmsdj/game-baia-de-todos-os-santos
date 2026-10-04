"""R30B.53: materializa hard-boundary costeira e conecta gameplay ao terreno oficial."""
import bpy,json,hashlib,math,runpy,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

root=Path(__file__).resolve().parents[2]; scene=bpy.context.scene
reg=json.loads((root/"world/areas/mvp-centro-lacerda/blender-revisions.json").read_text(encoding="utf8")); src=reg["validation_source"]
assert src["revision"]=="R30B.52"; assert Path(bpy.data.filepath).resolve()==(root/src["file"]).resolve()
out=root/"blender/salvador_lacerda_r30b53_costura_gameplay.blend"; assert not out.exists()
data=np.load(root/"artifacts/waterfront/coastal_integrated_surface_b53.npz")
meta=json.loads((root/"artifacts/waterfront/coastal_integrated_surface_b53.json").read_text(encoding="utf8"))
contract=json.loads((root/"world/areas/mvp-centro-lacerda/coastal-gameplay-b51.json").read_text(encoding="utf8"))
gx=data["gx"];gy=data["gy"];H=data["H"];mask=data["mask"];surface=data["surface"];under=data["underwater"];waymap=data["waymap"]
ny,nx=H.shape

api=runpy.run_path(str(root/"automation/blender/component_fingerprint.py"));sig=api["signature"]
ground=scene.objects["MVP | terreno corrigido | colisão estática"]
water=scene.objects["BAÍA DE TODOS-OS-SANTOS | superfície e recorte costeiro"]
quay=scene.objects["CAIS | contenção costeira alinhada à linha de costa"]
piers=[o for o in scene.objects if o.name.startswith("PIER OSM |")]
protected={o.name:sig(o) for o in [ground,water,quay,*piers]}

c_visual=bpy.data.collections["38.1 GAMEPLAY | TERRAIN"];c_collision=bpy.data.collections["38.2 GAMEPLAY | TERRAIN COLLISION"];c_graph=bpy.data.collections["38.5 GAMEPLAY | ROAD GRAPH"]

index=np.full((ny,nx),-1,dtype=np.int64); coords=[]
for j in range(ny):
    for i in range(nx):
        if mask[j,i] and np.isfinite(H[j,i]):
            index[j,i]=len(coords);coords.append((float(gx[i]),float(gy[j]),float(H[j,i])))
faces=[];mat_idx=[];roles=[];face_way=[]
stone_way=154743329
for j in range(ny-1):
    for i in range(nx-1):
        ids=[index[j,i],index[j,i+1],index[j+1,i+1],index[j+1,i]]
        if min(ids)<0:continue
        faces.append(tuple(int(x) for x in ids))
        typ=int(surface[j,i]);uw=int(under[j,i]);ways=[int(waymap[j,i]),int(waymap[j,i+1]),int(waymap[j+1,i]),int(waymap[j+1,i+1])]
        wid=max(set(ways),key=ways.count) if ways else 0
        if typ==2:mi=3;role=2
        elif typ==1 and wid==stone_way:mi=2;role=1
        elif typ==1:mi=1;role=1
        else:mi=0;role=3 if uw else 0
        mat_idx.append(mi);roles.append(role);face_way.append(wid)

me=bpy.data.meshes.new("B53 | superficie integrada hard-boundary")
me.from_pydata(coords,[],faces);me.update()
terrain_mat=scene.objects["B52 | GAMEPLAY TERRAIN | costa integrada + vias"].data.materials[0]
road_mat=bpy.data.materials.get("MVP | asfalto da ladeira")
stone_mat=bpy.data.materials.get("VIAS | pavimento de pedra Rua Chile") or road_mat
walk_mat=bpy.data.materials.get("MVP | percurso pedonal") or stone_mat
for m in (terrain_mat,road_mat,stone_mat,walk_mat):me.materials.append(m)
for p,mi in zip(me.polygons,mat_idx):p.material_index=int(mi)
attr=me.attributes.new(name="boas_surface_role",type="INT",domain="FACE")
for d,v in zip(attr.data,roles):d.value=int(v)
wattr=me.attributes.new(name="boas_osm_way_id",type="INT",domain="FACE")
for d,v in zip(wattr.data,face_way):d.value=int(v) if -(2**31)<=int(v)<2**31 else 0

ob=bpy.data.objects.new("B53 | GAMEPLAY TERRAIN | costa + vias | hard boundary",me);c_visual.objects.link(ob)
ob["boas_revision"]="R30B.53";ob["boas_runtime_role"]="gameplay_terrain_integrated_candidate";ob["boas_gameplay_surface"]=True
ob["boas_grid_m"]=2.0;ob["boas_collision_required"]=True;ob["boas_boundary_x"]=float(meta["boundary_x"])
ob["boas_existing_ground_owner_east"]=True;ob["boas_gameplay_approved"]=False

cp=ob.copy();cp.data=me.copy();cp.animation_data_clear();cp.name="B53 | COLLISION | costa + vias | hard boundary";c_collision.objects.link(cp)
cp.hide_render=True;cp.hide_viewport=True;cp["boas_runtime_role"]="static_collision_candidate";cp["boas_source_visual"]=ob.name;cp["boas_geometry_identical"]=True
ob["boas_collision_partner"]=cp.name

sup=[]
for old in scene.objects:
    if old.name.startswith("B52 | GAMEPLAY TERRAIN |") or old.name.startswith("B52 | COLLISION |") or old.name.startswith("B52 | GRAPH |"):
        old.hide_viewport=True;old.hide_render=True;old["boas_superseded_by"]="R30B.53";sup.append(old.name)

def make_tree(o):
    m=o.data;m.calc_loop_triangles()
    return BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[list(t.vertices) for t in m.loop_triangles],all_triangles=True)
newtree=make_tree(ob);oldtree=make_tree(ground)
def hit_union(x,y):
    a=newtree.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),500)[0]
    b=oldtree.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),500)[0]
    if a is None:return b
    if b is None:return a
    return a if a.z>=b.z else b

graph_rows=[]
for rec in contract["roads"]:
    pts=[Vector((float(x),float(y),0)) for x,y in rec["blender_xy"]];samples=[]
    for a,b in zip(pts,pts[1:]):
        d=b-a;L=d.to_2d().length
        if L<.01:continue
        count=max(1,math.ceil(L/2))
        for q in range(count+1):
            if samples and q==0:continue
            p=a+d*(q/count);h=hit_union(p.x,p.y)
            samples.append(Vector((p.x,p.y,h.z+.04)) if h is not None else None)
    runs=[];cur=[]
    for p in samples:
        if p is None:
            if len(cur)>=2:runs.append(cur)
            cur=[];continue
        if cur and (p.to_2d()-cur[-1].to_2d()).length>4.5:
            if len(cur)>=2:runs.append(cur)
            cur=[]
        cur.append(p)
    if len(cur)>=2:runs.append(cur)
    names=[]
    for ri,run in enumerate(runs):
        cu=bpy.data.curves.new(f"B53 GRAPH {rec['osm_way_id']} {ri}","CURVE");cu.dimensions="3D";sp=cu.splines.new("POLY");sp.points.add(len(run)-1)
        for p,co in zip(sp.points,run):p.co=(*co,1)
        go=bpy.data.objects.new(f"B53 | GRAPH | {rec['osm_way_id']} | run {ri}",cu);c_graph.objects.link(go);go.hide_render=True
        go["boas_osm_way_id"]=int(rec["osm_way_id"]);go["boas_runtime_role"]="navigation_path";go["boas_role"]=rec["role"]
        go["boas_direction"]="forward" if rec["oneway"]=="yes" else "both";go["boas_access"]=rec["access"] or "candidate"
        go["boas_surface_union"]="B53 expansion + official terrain";names.append(go.name)
    graph_rows.append({"osm_way_id":rec["osm_way_id"],"runs":len(runs),"objects":names})

changed=[n for n,b in protected.items() if sig(scene.objects[n])!=b];assert not changed,changed
scene["boas_validation_revision"]="R30B.53";scene["boas_all_generated_terrain_gameplay"]=True
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
sha=hashlib.sha256(out.read_bytes()).hexdigest()
report={
 "schema":"boas/coastal-hard-boundary-r30b53-v1","source_before":src,
 "source_after":{"file":out.relative_to(root).as_posix(),"revision":"R30B.53","sha256":sha},
 "surface_object":ob.name,"collision_object":cp.name,"vertices":len(coords),"faces":len(faces),
 "boundary":meta,"graph":graph_rows,"graph_way_count":sum(1 for r in graph_rows if r["runs"]),
 "superseded_objects_hidden":len(sup),"existing_ground_changed":False,"water_changed":False,"quay_changed":False,"piers_changed":False,"protected_changes":changed,
 "runtime_exported":False,"approved":False,
 "pending":["Auditar costura/grade/crossfall com superfície combinada","Validar colisão combinada B53 + proxy oficial","Depois gerar chunks/streaming"]
}
(root/"docs/reports/blender/coastal_hard_boundary_r30b53.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps({"revision":"R30B.53","sha256":sha,"vertices":len(coords),"faces":len(faces),"graph_way_count":report["graph_way_count"],"protected_changes":changed},ensure_ascii=False))
