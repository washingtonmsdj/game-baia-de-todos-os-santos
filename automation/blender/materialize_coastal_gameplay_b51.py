"""R30B.51: transforma expansão costeira em pacote de gameplay com terreno, colisão, vias e navegação."""
import bpy,json,hashlib,math,runpy
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

root=Path(__file__).resolve().parents[2]; scene=bpy.context.scene
reg=json.loads((root/"world/areas/mvp-centro-lacerda/blender-revisions.json").read_text(encoding="utf8")); src=reg["validation_source"]
assert src["revision"]=="R30B.50"; assert Path(bpy.data.filepath).resolve()==(root/src["file"]).resolve()
out=root/"blender/salvador_lacerda_r30b51_gameplay_costeiro.blend"; assert not out.exists()
contract=json.loads((root/"world/areas/mvp-centro-lacerda/coastal-gameplay-b51.json").read_text(encoding="utf8"))
api=runpy.run_path(str(root/"automation/blender/component_fingerprint.py")); sig=api["signature"]; wm=api["world_matrix"]

ground=scene.objects["MVP | terreno corrigido | colisão estática"]
water=scene.objects["BAÍA DE TODOS-OS-SANTOS | superfície e recorte costeiro"]
quay=scene.objects["CAIS | contenção costeira alinhada à linha de costa"]
piers=[o for o in scene.objects if o.name.startswith("PIER OSM |")]
land=scene.objects["EXPANSAO B49 | terra emersa costeira | candidata"]
shore=scene.objects["EXPANSAO B49 | faixa de transicao costeira | candidata"]
seabed=scene.objects["EXPANSAO B49 | fundo submerso DEM relativo | candidato"]
protected={o.name:sig(o) for o in [ground,water,quay,*piers,land,shore,seabed]}

def ensure_collection(name,parent=None):
    c=bpy.data.collections.get(name)
    if not c:
        c=bpy.data.collections.new(name)
        (parent.children if parent else scene.collection.children).link(c)
    return c
parent=ensure_collection("38 GAMEPLAY | EXPANSAO COSTEIRA B51")
c_visual=ensure_collection("38.1 GAMEPLAY | TERRAIN",parent)
c_collision=ensure_collection("38.2 GAMEPLAY | TERRAIN COLLISION",parent)
c_roads=ensure_collection("38.3 GAMEPLAY | ROAD DRIVEABLE",parent)
c_walk=ensure_collection("38.4 GAMEPLAY | WALKABLE",parent)
c_graph=ensure_collection("38.5 GAMEPLAY | ROAD GRAPH",parent)

# Todo terreno gerado passa a pertencer explicitamente ao gameplay.
terrain_rows=[]
for ob,role in [(land,"land"),(shore,"shore_transition"),(seabed,"underwater_seabed")]:
    if c_visual.objects.get(ob.name) is None: c_visual.objects.link(ob)
    ob["boas_gameplay_surface"]=True
    ob["boas_gameplay_role"]=role
    ob["boas_collision_required"]=True
    # colisão dedicada, mesma geometria-base e transform da superfície visual.
    cp=ob.copy(); cp.data=ob.data.copy(); cp.animation_data_clear()
    cp.name=f"B51 | COLLISION | {role}"
    for col in list(cp.users_collection):
        col.objects.unlink(cp)
    c_collision.objects.link(cp)
    cp.hide_render=True; cp.hide_viewport=True
    cp["boas_runtime_role"]="static_collision_candidate"
    cp["boas_collision_role"]=role
    cp["boas_source_visual"]=ob.name
    cp["boas_source_geometry_identical"]=True
    cp["boas_gameplay_approved"]=False
    ob["boas_collision_partner"]=cp.name
    terrain_rows.append({"visual":ob.name,"collision":cp.name,"vertices":len(ob.data.vertices),"polygons":len(ob.data.polygons),"role":role})

# BVHs: expansão primeiro, terreno oficial como continuidade na costura.
def make_tree(ob):
    me=ob.data; me.calc_loop_triangles()
    return BVHTree.FromPolygons([wm(ob)@v.co for v in me.vertices],[list(t.vertices) for t in me.loop_triangles],all_triangles=True)
trees=[(land,make_tree(land)),(shore,make_tree(shore)),(ground,make_tree(ground))]
def surface_hit(x,y,z=100.0):
    origin=Vector((x,y,z+200))
    best=None
    for ob,tree in trees:
        p,n,i,d=tree.ray_cast(origin,Vector((0,0,-1)),500)
        if p is not None and (best is None or p.z>best[0].z):
            best=(p,ob.name)
    return best

road_mat=bpy.data.materials.get("MVP | asfalto da ladeira") or bpy.data.materials.get("VIAS | pavimento de pedra Rua Chile")
walk_mat=bpy.data.materials.get("MVP | percurso pedonal") or bpy.data.materials.get("VIAS | pavimento de pedra Rua Chile") or road_mat
assert road_mat is not None and walk_mat is not None

bbox=contract["bbox_blender"]
road_rows=[]
for rec in contract["roads"]:
    pts=[Vector((float(x),float(y),0)) for x,y in rec["blender_xy"]]
    width=float(rec["gameplay_width_m"]); half=width/2
    samples=[]
    # Amostragem ~2m para superfície dirigível contínua.
    for a,b in zip(pts,pts[1:]):
        d=b-a; L=d.to_2d().length
        if L<0.01: continue
        count=max(1,math.ceil(L/2.0))
        t2=d.to_2d().normalized(); n2=Vector((-t2.y,t2.x))
        for j in range(count+1):
            if samples and j==0: continue
            p=a+d*(j/count)
            # margem curta de conexão com terreno existente
            if not (bbox["min_x"]-5<=p.x<=bbox["max_x"]+20 and bbox["min_y"]-5<=p.y<=bbox["max_y"]+20):
                continue
            left=Vector((p.x+n2.x*half,p.y+n2.y*half,0))
            right=Vector((p.x-n2.x*half,p.y-n2.y*half,0))
            hc=surface_hit(p.x,p.y); hl=surface_hit(left.x,left.y); hr=surface_hit(right.x,right.y)
            if not (hc and hl and hr): continue
            samples.append({
                "center":Vector((p.x,p.y,hc[0].z+0.018)),
                "left":Vector((left.x,left.y,hl[0].z+0.018)),
                "right":Vector((right.x,right.y,hr[0].z+0.018)),
                "source":hc[1],
            })
    # dividir em runs para evitar faces atravessando lacunas
    runs=[]; cur=[]
    for sm in samples:
        if cur and (sm["center"].to_2d()-cur[-1]["center"].to_2d()).length>4.5:
            if len(cur)>=2:runs.append(cur)
            cur=[]
        cur.append(sm)
    if len(cur)>=2:runs.append(cur)
    if not runs:
        road_rows.append({"osm_way_id":rec["osm_way_id"],"status":"no_surface_run","role":rec["role"]}); continue

    built_vertices=built_faces=0
    names=[]
    for ri,run in enumerate(runs):
        verts=[]; faces=[]
        for sm in run:
            verts.extend([tuple(sm["left"]),tuple(sm["right"])])
        for i in range(len(run)-1):
            a=2*i; faces.append((a,a+1,a+3,a+2))
        me=bpy.data.meshes.new(f"B51 ROAD {rec['osm_way_id']} {ri}")
        me.from_pydata(verts,[],faces); me.update()
        me.materials.append(walk_mat if rec["role"]=="walkable" else road_mat)
        prefix="WALK" if rec["role"]=="walkable" else "ROAD"
        ob=bpy.data.objects.new(f"B51 | {prefix} | {rec['osm_way_id']} | {rec['name'] or rec['highway']}",me)
        (c_walk if rec["role"]=="walkable" else c_roads).objects.link(ob)
        ob["boas_revision"]="R30B.51"
        ob["boas_osm_way_id"]=int(rec["osm_way_id"])
        ob["boas_runtime_role"]="walkable_surface_candidate" if rec["role"]=="walkable" else "road_driveable_surface_candidate"
        ob["boas_gameplay_width_m"]=width
        ob["boas_width_status"]=rec["gameplay_width_status"]
        ob["boas_width_basis"]=rec["gameplay_width_basis"]
        ob["boas_access"]=rec["access"] or "candidate"
        ob["boas_direction"]="forward" if rec["oneway"]=="yes" else "both"
        ob["boas_highway"]=rec["highway"]; ob["boas_name"]=rec["name"]
        ob["boas_collision_source"]="terrain_collision_b51"
        ob["boas_gameplay_approved"]=False
        names.append(ob.name); built_vertices+=len(verts); built_faces+=len(faces)

    # Grafo usa o eixo OSM, com Z amostrado na mesma superfície física.
    curve=bpy.data.curves.new(f"B51 GRAPH {rec['osm_way_id']}","CURVE"); curve.dimensions="3D"; curve.resolution_u=1
    sp=curve.splines.new("POLY")
    graphpts=[]
    for p in pts:
        h=surface_hit(p.x,p.y)
        if h and bbox["min_x"]-5<=p.x<=bbox["max_x"]+20 and bbox["min_y"]-5<=p.y<=bbox["max_y"]+20:
            graphpts.append((p.x,p.y,h[0].z+0.05))
    if len(graphpts)>=2:
        sp.points.add(len(graphpts)-1)
        for q,co in zip(sp.points,graphpts): q.co=(*co,1.0)
        gob=bpy.data.objects.new(f"B51 | GRAPH | {rec['osm_way_id']} | {rec['name'] or rec['highway']}",curve); c_graph.objects.link(gob)
        gob.hide_render=True
        gob["boas_osm_way_id"]=int(rec["osm_way_id"]); gob["boas_runtime_role"]="navigation_path"
        gob["boas_direction"]="forward" if rec["oneway"]=="yes" else "both"
        gob["boas_access"]=rec["access"] or "candidate"; gob["boas_role"]=rec["role"]
    else:
        bpy.data.curves.remove(curve); gob=None
    road_rows.append({"osm_way_id":rec["osm_way_id"],"name":rec["name"],"role":rec["role"],"highway":rec["highway"],"runs":len(runs),"objects":names,"vertices":built_vertices,"faces":built_faces,"graph_object":None if gob is None else gob.name,"gameplay_width_m":width,"width_status":rec["gameplay_width_status"],"access":rec["access"],"oneway":rec["oneway"]})

# Provas: nenhuma geometria existente foi alterada.
changed=[n for n,b in protected.items() if sig(scene.objects[n])!=b]
assert not changed,changed
scene["boas_validation_revision"]="R30B.51"
scene["boas_gameplay_expansion_contract"]="world/areas/mvp-centro-lacerda/coastal-gameplay-b51.json"
scene["boas_all_generated_terrain_gameplay"]=True
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
sha=hashlib.sha256(out.read_bytes()).hexdigest()
report={
 "schema":"boas/coastal-gameplay-r30b51-v1","source_before":src,
 "source_after":{"file":out.relative_to(root).as_posix(),"revision":"R30B.51","sha256":sha},
 "aleph_method_reused":["OSM centerlines","DEM-relative terrain basis","shared terrain/road elevation source","explicit gameplay export semantics"],
 "terrain":terrain_rows,
 "roads":road_rows,
 "road_count_contract":len(contract["roads"]),
 "road_surface_objects":sum(len(r.get("objects",[])) for r in road_rows),
 "road_graph_objects":sum(1 for r in road_rows if r.get("graph_object")),
 "collision_objects":len(terrain_rows),
 "existing_geometry_changed":False,"protected_changes":changed,
 "water_changed":False,"quay_changed":False,"piers_changed":False,
 "runtime_exported":False,"approved":False,
 "policy":contract["policy"],
 "pending":["Auditar cobertura das 9 vias e continuidade com o grafo existente","Validar colisão B51 e contato veículo/terreno","Gerar chunks/streaming da expansão antes de runtime","Larguras de gameplay permanecem adaptações não topográficas"]
}
(root/"docs/reports/blender/coastal_gameplay_r30b51.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps({"revision":"R30B.51","sha256":sha,"terrain_collision":len(terrain_rows),"roads":len(road_rows),"road_surface_objects":report["road_surface_objects"],"road_graph_objects":report["road_graph_objects"],"changed":changed},ensure_ascii=False))
