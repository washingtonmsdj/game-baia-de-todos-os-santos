"""R30B.57: restaura padrão visual alto na expansão costeira sem sacrificar gameplay."""
import bpy,json,hashlib,math,runpy
from pathlib import Path
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

root=Path(__file__).resolve().parents[2]
scene=bpy.context.scene
reg=json.loads((root/"world/areas/mvp-centro-lacerda/blender-revisions.json").read_text(encoding="utf8"))
src=reg["validation_source"]
assert src["revision"]=="R30B.56"
assert Path(bpy.data.filepath).resolve()==(root/src["file"]).resolve()
out=root/"blender/salvador_lacerda_r30b57_visual_hq_gameplay.blend"
assert not out.exists()

rep56=json.loads((root/"docs/reports/blender/pier_gameplay_r30b56.json").read_text(encoding="utf8"))
assert hashlib.sha256((root/src["file"]).read_bytes()).hexdigest()==src["sha256"]
data=np.load(root/"artifacts/waterfront/coastal_visual_hq_b57.npz")
meta=json.loads((root/"artifacts/waterfront/coastal_visual_hq_b57.json").read_text(encoding="utf8"))
gx=np.asarray(data["gx"],dtype=float)
gy=np.asarray(data["gy"],dtype=float)
H=np.asarray(data["H"],dtype=float)
mask=np.asarray(data["mask"],dtype=bool)
under=np.asarray(data["underwater"],dtype=bool)
step=float(meta["step_m"])
ny,nx=H.shape

api=runpy.run_path(str(root/"automation/blender/component_fingerprint.py"))
sig=api["signature"]
protected_names=[
    "MVP | terreno corrigido | colisão estática",
    "BAÍA DE TODOS-OS-SANTOS | superfície e recorte costeiro",
    "CAIS | contenção costeira alinhada à linha de costa",
    "B55 | COLLISION | costa + vias refinadas",
]
protected_names += [o.name for o in scene.objects if o.name.startswith("B56 | COLLISION | PIER |")]
protected={n:sig(scene.objects[n]) for n in protected_names}

col=bpy.data.collections.get("39 GAMEPLAY | B57 HQ")
if not col:
    col=bpy.data.collections.new("39 GAMEPLAY | B57 HQ")
    scene.collection.children.link(col)

# Compacta a grade HQ no polígono válido.
index=np.full((ny,nx),-1,dtype=np.int64)
coords=np.argwhere(mask)
verts=[]
for k,(j,i) in enumerate(coords):
    index[j,i]=k
    verts.append((float(gx[i]),float(gy[j]),float(H[j,i])))

faces=[]
face_mats=[]
# 0 terreno contínuo, 1 solo, 2 rocha.
for j in range(ny-1):
    for i in range(nx-1):
        ids=(index[j,i],index[j,i+1],index[j+1,i+1],index[j+1,i])
        if min(ids)<0:
            continue
        z00=H[j,i];z10=H[j,i+1];z11=H[j+1,i+1];z01=H[j+1,i]
        dzdx=((z10+z11)-(z00+z01))/(2*step)
        dzdy=((z01+z11)-(z00+z10))/(2*step)
        slope=math.degrees(math.atan(math.hypot(float(dzdx),float(dzdy))))
        avgz=float((z00+z10+z11+z01)/4)
        if avgz<0.30:
            mi=1
        elif slope>=35:
            mi=2
        elif slope>=18:
            mi=1
        else:
            mi=0
        faces.append(list(map(int,ids)))
        face_mats.append(mi)

mesh=bpy.data.meshes.new("B57_HQ_TERRAIN_MESH")
mesh.from_pydata(verts,[],faces)
mesh.update()
terrain=bpy.data.objects.new("B57 | GAMEPLAY TERRAIN HQ | Aleph 0.75m",mesh)
col.objects.link(terrain)
materials=[
    bpy.data.materials["GAL R34 | encosta localizada | MVP | terreno contínuo"],
    bpy.data.materials["Terreno | solo encosta"],
    bpy.data.materials["ENV R35 | terreno e rocha junto ao apoio"],
]
for m in materials:
    mesh.materials.append(m)
for p,mi in zip(mesh.polygons,face_mats):
    p.material_index=mi
    p.use_smooth=True
terrain["boas_revision"]="R30B.57"
terrain["boas_runtime_role"]="gameplay_terrain_visual_hq"
terrain["boas_grid_step_m"]=step
terrain["boas_source_dem"]="Aleph terrain.tif"
terrain["boas_gameplay_approved"]=False

# Colisão usa geometria idêntica, não uma aproximação invisível.
cmesh=mesh.copy()
collision=bpy.data.objects.new("B57 | COLLISION | terrain HQ 0.75m",cmesh)
col.objects.link(collision)
collision.hide_render=True
collision.hide_viewport=True
collision.display_type="WIRE"
collision["boas_revision"]="R30B.57"
collision["boas_runtime_role"]="terrain_collision"
collision["boas_source_surface"]=terrain.name
collision["boas_geometry_identical_to_visual"]=True
collision["boas_gameplay_approved"]=False

# BVH para vias visuais vetoriais exatamente sobre a superfície HQ.
mesh.calc_loop_triangles()
tree=BVHTree.FromPolygons(
    [terrain.matrix_world@v.co for v in mesh.vertices],
    [list(t.vertices) for t in mesh.loop_triangles],
    all_triangles=True,
)
def hitz(x,y):
    p=tree.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),500)[0]
    return None if p is None else float(p.z)

contract=json.loads((root/"world/areas/mvp-centro-lacerda/coastal-gameplay-b51.json").read_text(encoding="utf8"))
road_objects=[]
for rec in contract["roads"]:
    srcpts=[Vector((float(x),float(y))) for x,y in rec["blender_xy"]]
    samples=[]
    for si,(a,b) in enumerate(zip(srcpts,srcpts[1:])):
        d=b-a
        L=d.length
        if L<.01:
            continue
        count=max(1,math.ceil(L/0.85))
        for q in range(count+1):
            if si>0 and q==0:
                continue
            samples.append(a+d*(q/count))
    if len(samples)<2:
        continue

    sections=[]
    width=float(rec["gameplay_width_m"])
    for k,p in enumerate(samples):
        if k==0:
            t=samples[1]-samples[0]
        elif k==len(samples)-1:
            t=samples[-1]-samples[-2]
        else:
            t=samples[k+1]-samples[k-1]
        if t.length<1e-8:
            sections.append(None)
            continue
        t.normalize()
        n=Vector((-t.y,t.x))
        l=p+n*(width/2)
        r=p-n*(width/2)
        zl=hitz(l.x,l.y)
        zr=hitz(r.x,r.y)
        if zl is None or zr is None:
            sections.append(None)
        else:
            sections.append(((l.x,l.y,zl+0.015),(r.x,r.y,zr+0.015)))

    runs=[]
    current=[]
    for sec in sections:
        if sec is None:
            if len(current)>=2:
                runs.append(current)
            current=[]
        else:
            current.append(sec)
    if len(current)>=2:
        runs.append(current)

    for ri,run in enumerate(runs):
        rv=[]
        rf=[]
        for sec in run:
            rv.extend(sec)
        for q in range(len(run)-1):
            a=2*q
            rf.append((a,a+2,a+3,a+1))
        rmesh=bpy.data.meshes.new(f"B57_ROAD_{rec['osm_way_id']}_{ri}_MESH")
        rmesh.from_pydata(rv,[],rf)
        rmesh.update()
        rob=bpy.data.objects.new(f"B57 | ROAD VISUAL | {rec['osm_way_id']} | run {ri}",rmesh)
        col.objects.link(rob)
        surf=(rec.get("surface") or "").lower()
        if rec["role"]=="walkable":
            mat=bpy.data.materials["MVP | percurso pedonal"]
        elif surf=="sett":
            mat=bpy.data.materials["VIAS | pavimento de pedra Rua Chile"]
        else:
            mat=bpy.data.materials["MVP | asfalto da ladeira"]
        rmesh.materials.append(mat)
        for p in rmesh.polygons:
            p.material_index=0
            p.use_smooth=False
        rob["boas_osm_way_id"]=int(rec["osm_way_id"])
        rob["boas_runtime_role"]="visual_road_surface"
        rob["boas_collision_source"]=collision.name
        rob["boas_visual_offset_m"]=0.015
        rob["boas_width_status"]=rec["gameplay_width_status"]
        rob["boas_gameplay_approved"]=False
        road_objects.append({
            "osm_way_id":int(rec["osm_way_id"]),
            "name":rec["name"],
            "object":rob.name,
            "role":rec["role"],
            "vertices":len(rmesh.vertices),
            "faces":len(rmesh.polygons),
        })

# Píeres: troca plano de referência por deck visual sólido; topo continua na colisão B56.
pier_visuals=[]
for pid in (1426173139,1426173140):
    top=scene.objects[f"B56 | WALKABLE PIER | {pid}"]
    assert top.type=="MESH" and len(top.data.polygons)>=1
    poly=top.data.polygons[0]
    order=list(poly.vertices)
    tv=[top.data.vertices[i].co.copy() for i in order]
    n=len(tv)
    thickness=0.35
    pv=[tuple(v) for v in tv]+[(v.x,v.y,v.z-thickness) for v in tv]
    pf=[tuple(range(n)),tuple(range(2*n-1,n-1,-1))]
    for i in range(n):
        j=(i+1)%n
        pf.append((i,j,n+j,n+i))
    pmesh=bpy.data.meshes.new(f"B57_PIER_{pid}_MESH")
    pmesh.from_pydata(pv,[],pf)
    pmesh.update()
    pobj=bpy.data.objects.new(f"B57 | PIER VISUAL | {pid}",pmesh)
    col.objects.link(pobj)
    pobj.matrix_world=top.matrix_world.copy()
    pmesh.materials.append(bpy.data.materials["CAIS | pedra costeira"])
    pobj["boas_osm_id"]=pid
    pobj["boas_runtime_role"]="pier_visual"
    pobj["boas_collision_source"]=f"B56 | COLLISION | PIER | {pid}"
    pobj["boas_visual_thickness_m"]=thickness
    pobj["boas_thickness_status"]="ADAPT_VISUAL_NOT_SURVEYED"
    pobj["boas_gameplay_approved"]=False
    pier_visuals.append({"osm_id":pid,"object":pobj.name,"vertices":len(pmesh.vertices),"faces":len(pmesh.polygons)})

# Não exibir mecanismos/refs de gameplay como arte final.
scene.objects["B55 | GAMEPLAY TERRAIN | costa + vias refinadas"].hide_viewport=True
scene.objects["B55 | GAMEPLAY TERRAIN | costa + vias refinadas"].hide_render=True
for o in scene.objects:
    if o.name.startswith("B55 | GRAPH |") or o.name.startswith("B56 | GRAPH WALK |"):
        o.hide_viewport=True
        o.hide_render=True
    if o.name.startswith("PIER OSM |"):
        o.hide_viewport=True
        o.hide_render=True
    if o.name.startswith("B56 | WALKABLE PIER |"):
        o.hide_viewport=True
        o.hide_render=True
    if o.name.startswith("B56 | COLLISION | PIER |"):
        o.hide_viewport=True
        o.hide_render=True

# Prova de que fontes protegidas não sofreram alteração geométrica.
changed=[n for n,b in protected.items() if sig(scene.objects[n])!=b]
assert not changed,changed
scene["boas_validation_revision"]="R30B.57"
scene["boas_visual_quality_status"]="hq_terrain_075m_vector_roads_pier_decks"
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
sha=hashlib.sha256(out.read_bytes()).hexdigest()

report={
    "schema":"boas/visual-hq-r30b57-v1",
    "source_before":src,
    "source_after":{"file":out.relative_to(root).as_posix(),"revision":"R30B.57","sha256":sha},
    "terrain_visual":terrain.name,
    "terrain_collision":collision.name,
    "grid_step_m":step,
    "vertices":len(mesh.vertices),
    "faces":len(mesh.polygons),
    "visual_collision_identical":True,
    "materials":[m.name for m in materials],
    "road_visual_objects":road_objects,
    "road_visual_count":len(road_objects),
    "pier_visuals":pier_visuals,
    "source_gameplay_surface_hidden":True,
    "source_graphs_hidden_from_art":True,
    "reference_piers_hidden_from_art":True,
    "protected_changes":changed,
    "water_changed":False,
    "official_ground_changed":False,
    "quay_changed":False,
    "runtime_exported":False,
    "approved":False,
    "pending":[
        "Reabrir B57 e auditar grade/crossfall/suporte/colisão na malha HQ",
        "Auditar costura HQ com terreno oficial",
        "Revisar visualmente materiais, estradas e píeres no viewport",
        "Somente depois promover runtime/streaming"
    ],
}
(root/"docs/reports/blender/visual_hq_r30b57.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps({
    "file":report["source_after"],
    "terrain":{"vertices":len(mesh.vertices),"faces":len(mesh.polygons),"step_m":step},
    "roads":len(road_objects),
    "piers":pier_visuals,
    "protected_changes":changed,
},ensure_ascii=False))
