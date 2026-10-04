"""R30B.52: materializa superfície costeira integrada de 2 m com vias incorporadas e colisão idêntica."""
import bpy,json,hashlib,math,runpy,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

root=Path(__file__).resolve().parents[2]
scene=bpy.context.scene
reg=json.loads((root/"world/areas/mvp-centro-lacerda/blender-revisions.json").read_text(encoding="utf8"))
src=reg["validation_source"]
assert src["revision"]=="R30B.51"
assert Path(bpy.data.filepath).resolve()==(root/src["file"]).resolve()
out=root/"blender/salvador_lacerda_r30b52_gameplay_integrado.blend"
assert not out.exists()

data=np.load(root/"artifacts/waterfront/coastal_integrated_surface_b52.npz")
meta=json.loads((root/"artifacts/waterfront/coastal_integrated_surface_b52.json").read_text(encoding="utf8"))
contract=json.loads((root/"world/areas/mvp-centro-lacerda/coastal-gameplay-b51.json").read_text(encoding="utf8"))
gx=data["gx"]; gy=data["gy"]; H=data["H"]; mask=data["mask"]
surface=data["surface"]; under=data["underwater"]; waymap=data["waymap"]
ny,nx=H.shape

api=runpy.run_path(str(root/"automation/blender/component_fingerprint.py"))
sig=api["signature"]
ground=scene.objects["MVP | terreno corrigido | colisão estática"]
water=scene.objects["BAÍA DE TODOS-OS-SANTOS | superfície e recorte costeiro"]
quay=scene.objects["CAIS | contenção costeira alinhada à linha de costa"]
piers=[o for o in scene.objects if o.name.startswith("PIER OSM |")]
protected={o.name:sig(o) for o in [ground,water,quay,*piers]}

c_visual=bpy.data.collections["38.1 GAMEPLAY | TERRAIN"]
c_collision=bpy.data.collections["38.2 GAMEPLAY | TERRAIN COLLISION"]
c_graph=bpy.data.collections["38.5 GAMEPLAY | ROAD GRAPH"]

index=np.full((ny,nx),-1,dtype=np.int64)
coords=[]
for j in range(ny):
    for i in range(nx):
        if mask[j,i] and np.isfinite(H[j,i]):
            index[j,i]=len(coords)
            coords.append((float(gx[i]),float(gy[j]),float(H[j,i])))

faces=[]; mat_idx=[]; roles=[]; face_way=[]
stone_way=154743329
for j in range(ny-1):
    for i in range(nx-1):
        ids=[index[j,i],index[j,i+1],index[j+1,i+1],index[j+1,i]]
        if min(ids)<0:
            continue
        faces.append(tuple(int(x) for x in ids))
        typ=int(surface[j,i]); uw=int(under[j,i])
        ways=[int(waymap[j,i]),int(waymap[j,i+1]),int(waymap[j+1,i]),int(waymap[j+1,i+1])]
        wid=max(set(ways),key=ways.count) if ways else 0
        if typ==2:
            mi=3; role=2
        elif typ==1 and wid==stone_way:
            mi=2; role=1
        elif typ==1:
            mi=1; role=1
        else:
            mi=0; role=3 if uw else 0
        mat_idx.append(mi); roles.append(role); face_way.append(wid)

me=bpy.data.meshes.new("B52 | superficie integrada costeira 2m")
me.from_pydata(coords,[],faces)
me.update()

terrain_mat=next((m for m in scene.objects["EXPANSAO B49 | terra emersa costeira | candidata"].data.materials if m),None)
road_mat=bpy.data.materials.get("MVP | asfalto da ladeira")
stone_mat=bpy.data.materials.get("VIAS | pavimento de pedra Rua Chile") or road_mat
walk_mat=bpy.data.materials.get("MVP | percurso pedonal") or stone_mat
assert terrain_mat and road_mat and stone_mat and walk_mat
for m in (terrain_mat,road_mat,stone_mat,walk_mat):
    me.materials.append(m)
for p,mi in zip(me.polygons,mat_idx):
    p.material_index=int(mi)

attr=me.attributes.new(name="boas_surface_role",type="INT",domain="FACE")
for d,v in zip(attr.data,roles):
    d.value=int(v)
wattr=me.attributes.new(name="boas_osm_way_id",type="INT",domain="FACE")
for d,v in zip(wattr.data,face_way):
    d.value=int(v) if -(2**31)<=int(v)<2**31 else 0

ob=bpy.data.objects.new("B52 | GAMEPLAY TERRAIN | costa integrada + vias",me)
c_visual.objects.link(ob)
ob["boas_revision"]="R30B.52"
ob["boas_runtime_role"]="gameplay_terrain_integrated_candidate"
ob["boas_gameplay_surface"]=True
ob["boas_grid_m"]=float(meta["step_m"])
ob["boas_collision_required"]=True
ob["boas_road_platform_method"]="Aleph continuous-surface adapted"
ob["boas_vehicle_grade_limit"]=float(meta["vehicle_grade_limit"])
ob["boas_pedestrian_grade_limit"]=float(meta["pedestrian_grade_limit"])
ob["boas_gameplay_approved"]=False

cp=ob.copy()
cp.data=me.copy()
cp.animation_data_clear()
cp.name="B52 | COLLISION | costa integrada + vias"
c_collision.objects.link(cp)
cp.hide_render=True
cp.hide_viewport=True
cp["boas_runtime_role"]="static_collision_candidate"
cp["boas_source_visual"]=ob.name
cp["boas_geometry_identical"]=True
cp["boas_gameplay_approved"]=False
ob["boas_collision_partner"]=cp.name

superseded=[]
prefixes=("EXPANSAO B49 |","B51 | COLLISION |","B51 | ROAD |","B51 | WALK |","B51 | GRAPH |")
for old in scene.objects:
    if old is ob or old is cp:
        continue
    if old.name.startswith(prefixes):
        old.hide_viewport=True
        old.hide_render=True
        old["boas_superseded_by"]="R30B.52"
        superseded.append(old.name)

me.calc_loop_triangles()
tree=BVHTree.FromPolygons(
    [ob.matrix_world@v.co for v in me.vertices],
    [list(t.vertices) for t in me.loop_triangles],
    all_triangles=True
)
def hit(x,y):
    return tree.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),500)[0]

graph_rows=[]
for rec in contract["roads"]:
    pts=[Vector((float(x),float(y),0)) for x,y in rec["blender_xy"]]
    samples=[]
    for a,b in zip(pts,pts[1:]):
        d=b-a
        L=d.to_2d().length
        if L<.01:
            continue
        count=max(1,math.ceil(L/2))
        for q in range(count+1):
            if samples and q==0:
                continue
            p=a+d*(q/count)
            h=hit(p.x,p.y)
            samples.append(Vector((p.x,p.y,h.z+.04)) if h is not None else None)
    runs=[]
    cur=[]
    for p in samples:
        if p is None:
            if len(cur)>=2:
                runs.append(cur)
            cur=[]
            continue
        if cur and (p.to_2d()-cur[-1].to_2d()).length>4.5:
            if len(cur)>=2:
                runs.append(cur)
            cur=[]
        cur.append(p)
    if len(cur)>=2:
        runs.append(cur)

    names=[]
    for ri,run in enumerate(runs):
        cu=bpy.data.curves.new(f"B52 GRAPH {rec['osm_way_id']} {ri}","CURVE")
        cu.dimensions="3D"
        sp=cu.splines.new("POLY")
        sp.points.add(len(run)-1)
        for p,co in zip(sp.points,run):
            p.co=(*co,1)
        go=bpy.data.objects.new(f"B52 | GRAPH | {rec['osm_way_id']} | run {ri}",cu)
        c_graph.objects.link(go)
        go.hide_render=True
        go["boas_osm_way_id"]=int(rec["osm_way_id"])
        go["boas_runtime_role"]="navigation_path"
        go["boas_role"]=rec["role"]
        go["boas_direction"]="forward" if rec["oneway"]=="yes" else "both"
        go["boas_access"]=rec["access"] or "candidate"
        go["boas_source_surface"]=ob.name
        names.append(go.name)
    graph_rows.append({"osm_way_id":rec["osm_way_id"],"role":rec["role"],"runs":len(runs),"objects":names})

changed=[n for n,b in protected.items() if sig(scene.objects[n])!=b]
assert not changed,changed

scene["boas_validation_revision"]="R30B.52"
scene["boas_all_generated_terrain_gameplay"]=True
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
sha=hashlib.sha256(out.read_bytes()).hexdigest()

counts={str(i):mat_idx.count(i) for i in set(mat_idx)}
report={
    "schema":"boas/coastal-integrated-r30b52-v1",
    "source_before":src,
    "source_after":{"file":out.relative_to(root).as_posix(),"revision":"R30B.52","sha256":sha},
    "surface_object":ob.name,
    "collision_object":cp.name,
    "vertices":len(coords),
    "faces":len(faces),
    "grid_m":float(meta["step_m"]),
    "material_face_counts":counts,
    "surface_role_codes":{"0":"land","1":"road_driveable","2":"walkable","3":"underwater_seabed"},
    "graph":graph_rows,
    "graph_way_count":sum(1 for r in graph_rows if r["runs"]>0),
    "graph_run_count":sum(r["runs"] for r in graph_rows),
    "superseded_objects_hidden":len(superseded),
    "existing_ground_changed":False,
    "water_changed":False,
    "quay_changed":False,
    "piers_changed":False,
    "protected_changes":changed,
    "runtime_exported":False,
    "approved":False,
    "pending":[
        "Auditar grade/crossfall na superfície integrada B52",
        "Validar igualdade visual/colisão após reabrir",
        "Gerar chunks de streaming após os gates geométricos"
    ]
}
(root/"docs/reports/blender/coastal_integrated_r30b52.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps({
    "revision":"R30B.52",
    "sha256":sha,
    "vertices":len(coords),
    "faces":len(faces),
    "graph_way_count":report["graph_way_count"],
    "graph_runs":report["graph_run_count"],
    "protected_changes":changed
},ensure_ascii=False))
