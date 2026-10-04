"""R30B.48: expansão costeira sudoeste candidata, separada do terreno oficial."""
import bpy,json,hashlib,runpy,statistics,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

root=Path(__file__).resolve().parents[2]; scene=bpy.context.scene
reg=json.loads((root/"world/areas/mvp-centro-lacerda/blender-revisions.json").read_text(encoding="utf8"))
src=reg["validation_source"]; assert src["revision"]=="R30B.47"
assert Path(bpy.data.filepath).resolve()==(root/src["file"]).resolve()
out=root/"blender/salvador_lacerda_r30b48_expansao_costeira_dem.blend"; assert not out.exists()
grid=json.loads((root/"artifacts/waterfront/coastal_dem_grid_b48.json").read_text(encoding="utf8"))
c=json.loads((root/"world/areas/mvp-centro-lacerda/production.json").read_text(encoding="utf8"))
api=runpy.run_path(str(root/"automation/blender/component_fingerprint.py")); sig=api["signature"]; wm=api["world_matrix"]
ground=scene.objects[c["export"]["road_object"]]
water=scene.objects["BAÍA DE TODOS-OS-SANTOS | superfície e recorte costeiro"]
quay=scene.objects["CAIS | contenção costeira alinhada à linha de costa"]
piers=[o for o in scene.objects if o.name.startswith("PIER OSM |")]
protected={o.name:sig(o) for o in [ground,water,quay,*piers]}

# BVH do terreno oficial para ancorar a costura no lado já existente.
me=ground.data; me.calc_loop_triangles()
tree=BVHTree.FromPolygons([wm(ground)@v.co for v in me.vertices],[list(t.vertices) for t in me.loop_triangles],all_triangles=True)
def ghit(x,y):
    p,n,i,_=tree.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),500)
    return p

rows=[r for r in grid["grid_points"] if 0.0<=float(r["dem_z"])<=100.0]
by={(int(r["ix"]),int(r["iy"])):r for r in rows}
# Offset vertical local robusto a partir de amostras de sobreposição próximas ao limite oeste do terreno atual.
anchors=[]
for r in rows:
    x,y=map(float,r["xy"])
    if -300.0<=x<=-270.0 and -280.0<=y<=10.0:
        p=ghit(x,y)
        if p is not None:
            anchors.append(float(p.z)-float(r["dem_z"]))
assert len(anchors)>=5, f"Âncoras insuficientes: {len(anchors)}"
offset=statistics.median(anchors)

# Construir apenas a expansão x<=-280; sobreposição curta encaixa na malha existente.
verts=[]; index={}; source_meta=[]
for key,r in sorted(by.items(),key=lambda kv:(kv[0][1],kv[0][0])):
    x,y=map(float,r["xy"])
    if x>-280.0: continue
    z=float(r["dem_z"])+offset
    # na faixa de costura, quando o terreno oficial existe, coincidir exatamente para evitar degrau.
    if x>=-300.0:
        p=ghit(x,y)
        if p is not None:
            w=max(0.0,min(1.0,(x+300.0)/20.0))
            z=z*(1.0-w)+float(p.z)*w
    index[key]=len(verts); verts.append((x,y,z)); source_meta.append((key,float(r["dem_z"])))

faces=[]
for (ix,iy),r in by.items():
    keys=[(ix,iy),(ix+1,iy),(ix+1,iy+1),(ix,iy+1)]
    if all(k in index for k in keys):
        ids=[index[k] for k in keys]
        if len(set(ids))==4: faces.append(ids)
assert len(verts)>100 and len(faces)>100

mesh=bpy.data.meshes.new("B48_COSTA_SUDOESTE_DEM_CANDIDATA")
mesh.from_pydata(verts,[],faces); mesh.update()
obj=bpy.data.objects.new("EXPANSAO B48 | terreno costeiro DEM relativo | candidato",mesh)
col=bpy.data.collections.get("EXPANSAO | COSTA SUDOESTE | B48")
if not col:
    col=bpy.data.collections.new("EXPANSAO | COSTA SUDOESTE | B48"); scene.collection.children.link(col)
col.objects.link(obj)
# material terrestre existente, sem criar linguagem visual nova.
mat=next((m for m in ground.data.materials if m and "terreno" in m.name.lower() and "encosta" in m.name.lower()),None)
if mat is None: mat=next((m for m in ground.data.materials if m and "terreno" in m.name.lower()),None)
if mat: obj.data.materials.append(mat)
obj["boas_revision"]="R30B.48"
obj["boas_classification"]="ADAPT_LOCAL"
obj["boas_runtime_role"]="terrain_expansion_reference_candidate"
obj["boas_source_dem_relative_only"]=True
obj["boas_vertical_absolute_approved"]=False
obj["boas_vertical_local_offset_m"]=float(offset)
obj["boas_gameplay_approved"]=False
obj["boas_osm_coastline_way_id"]=354138561

changed=[n for n,b in protected.items() if n not in scene.objects or sig(scene.objects[n])!=b]
assert not changed, changed
scene["boas_validation_revision"]="R30B.48"
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
sha=hashlib.sha256(out.read_bytes()).hexdigest()
zs=[v[2] for v in verts]
report={
 "schema":"boas/coastal-terrain-r30b48-v1","source_before":src,
 "source_after":{"file":out.relative_to(root).as_posix(),"revision":"R30B.48","sha256":sha},
 "classification":"ADAPT_LOCAL","object":obj.name,"vertices":len(verts),"faces":len(faces),
 "grid_spacing_m":grid["spacing_m"],"dem_points_valid":len(rows),"dem_points_rejected":len(grid["grid_points"])-len(rows),
 "local_anchor_count":len(anchors),"local_vertical_offset_m":float(offset),
 "z_min_m":min(zs),"z_max_m":max(zs),
 "existing_ground_changed":False,"water_changed":False,"quay_changed":False,"piers_changed":False,
 "protected_changes":changed,"runtime_exported":False,"approved":False,
 "pending":["Reabrir e validar costura/topologia B48","Refinar encostas e materiais apenas após revisão visual","Expandir para outros lados somente dentro da cobertura DEM comprovada","Gameplay/runtime continuam bloqueados"]
}
(root/"docs/reports/blender/coastal_terrain_r30b48.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps(report,ensure_ascii=False))
