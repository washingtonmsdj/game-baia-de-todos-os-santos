"""R30B.56: gameplay pedonal dos píeres OSM sem inventar largura."""
import bpy,json,hashlib,runpy
from pathlib import Path
from mathutils import Vector

root=Path(__file__).resolve().parents[2]; scene=bpy.context.scene
reg=json.loads((root/"world/areas/mvp-centro-lacerda/blender-revisions.json").read_text(encoding="utf8")); src=reg["validation_source"]
assert src["revision"]=="R30B.55"; assert Path(bpy.data.filepath).resolve()==(root/src["file"]).resolve()
out=root/"blender/salvador_lacerda_r30b56_pieres_gameplay.blend"; assert not out.exists()
api=runpy.run_path(str(root/"automation/blender/component_fingerprint.py")); sig=api["signature"]

protected_names=[
 "B55 | GAMEPLAY TERRAIN | costa + vias refinadas",
 "B55 | COLLISION | costa + vias refinadas",
 "MVP | terreno corrigido | colisão estática",
 "BAÍA DE TODOS-OS-SANTOS | superfície e recorte costeiro",
 "CAIS | contenção costeira alinhada à linha de costa"
]
protected={n:sig(scene.objects[n]) for n in protected_names}

col=bpy.data.collections.get("GAMEPLAY | PIERS | B56")
if not col:
    col=bpy.data.collections.new("GAMEPLAY | PIERS | B56"); scene.collection.children.link(col)

# Dois footprints OSM podem virar superfície pedonal porque a largura/contorno vem da própria fonte.
footprint_ids={1426173139,1426173140}
walkable=[]
for pid in footprint_ids:
    srcobj=next(o for o in scene.objects if o.name.startswith(f"PIER OSM | {pid} |"))
    assert srcobj.type=="MESH"
    me=srcobj.data.copy(); ob=bpy.data.objects.new(f"B56 | WALKABLE PIER | {pid}",me); col.objects.link(ob)
    ob.matrix_world=srcobj.matrix_world.copy()
    ob["boas_osm_id"]=pid; ob["boas_runtime_role"]="walkable_surface"; ob["boas_collision_required"]=True
    ob["boas_width_status"]="footprint_from_osm"; ob["boas_gameplay_approved"]=False
    # colisão idêntica à superfície walkable
    cme=me.copy(); cob=bpy.data.objects.new(f"B56 | COLLISION | PIER | {pid}",cme); col.objects.link(cob); cob.matrix_world=ob.matrix_world.copy()
    cob.hide_render=True; cob["boas_runtime_role"]="walkable_collision"; cob["boas_source_surface"]=ob.name; cob["boas_gameplay_approved"]=False
    walkable.append({"osm_id":pid,"surface":ob.name,"collision":cob.name,"vertices":len(me.vertices),"faces":len(me.polygons)})

# Footways OSM reais junto aos píeres.
struct=json.loads((root/"artifacts/structural-pipeline/mvp-centro-lacerda/structural_reference.json").read_text(encoding="utf8"))
wanted={1426173138,1426173325,1426173326,1426173327}
records={}
def walk(x):
    if isinstance(x,dict):
        if x.get("layer")=="pedestrian" and x.get("osm_id") in wanted: records[x["osm_id"]]=x
        for v in x.values(): walk(v)
    elif isinstance(x,list):
        for v in x: walk(v)
walk(struct); assert set(records)==wanted

graphs=[]
for wid in sorted(wanted):
    rec=records[wid]; pts=[(float(x),float(y),7.255664825439453) for x,y in rec["blender_xy"]]
    cu=bpy.data.curves.new(f"B56_GRAPH_{wid}","CURVE"); cu.dimensions="3D"; cu.resolution_u=1; cu.bevel_depth=.04; cu.bevel_resolution=0
    sp=cu.splines.new("POLY"); sp.points.add(len(pts)-1)
    for p,co in zip(sp.points,pts): p.co=(co[0],co[1],co[2],1)
    ob=bpy.data.objects.new(f"B56 | GRAPH WALK | {wid}",cu); col.objects.link(ob)
    ob["boas_osm_way_id"]=wid; ob["boas_runtime_role"]="pedestrian_graph"; ob["boas_source"]="Aleph/OSM structural_reference"; ob["boas_gameplay_approved"]=False
    graphs.append({"osm_way_id":wid,"object":ob.name,"points":len(pts)})

# Píeres lineares permanecem somente referência por falta de largura.
linear=[o for o in scene.objects if o.name.startswith("PIER OSM |") and o.type=="CURVE"]
for o in linear:
    o["boas_gameplay_status"]="centerline_only_width_unknown_not_walkable_surface"

changed=[n for n,b in protected.items() if sig(scene.objects[n])!=b]; assert not changed,changed
scene["boas_validation_revision"]="R30B.56"
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
sha=hashlib.sha256(out.read_bytes()).hexdigest()
report={
 "schema":"boas/pier-gameplay-r30b56-v1","source_before":src,
 "source_after":{"file":out.relative_to(root).as_posix(),"revision":"R30B.56","sha256":sha},
 "walkable_pier_footprints":walkable,"pedestrian_graphs":graphs,
 "linear_piers_kept_centerline_only":[o.name for o in linear],
 "linear_width_invented":False,"terrain_changed":False,"water_changed":False,"quay_changed":False,
 "protected_changes":changed,"runtime_exported":False,"approved":False,
 "policy":{"footprint_required_for_walkable_surface":True,"collision_identical_to_walkable_surface":True,"unknown_width_never_invented":True},
 "pending":["Auditar igualdade visual/colisão dos footprints","Validar conectividade dos footways ao terreno/cais","Somente depois promover gameplay/runtime dos píeres"]
}
(root/"docs/reports/blender/pier_gameplay_r30b56.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps(report,ensure_ascii=False))
