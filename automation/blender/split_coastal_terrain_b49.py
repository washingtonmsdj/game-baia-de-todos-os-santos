"""R30B.49: separa terra emersa, transição costeira e fundo submerso da expansão B48."""
import bpy,json,hashlib,runpy
from pathlib import Path

root=Path(__file__).resolve().parents[2]; scene=bpy.context.scene
reg=json.loads((root/"world/areas/mvp-centro-lacerda/blender-revisions.json").read_text(encoding="utf8")); src=reg["validation_source"]
assert src["revision"]=="R30B.48"; assert Path(bpy.data.filepath).resolve()==(root/src["file"]).resolve()
out=root/"blender/salvador_lacerda_r30b49_costa_e_fundo_candidatos.blend"; assert not out.exists()
source=scene.objects["EXPANSAO B48 | terreno costeiro DEM relativo | candidato"]
water=scene.objects["BAÍA DE TODOS-OS-SANTOS | superfície e recorte costeiro"]
ground=scene.objects["MVP | terreno corrigido | colisão estática"]
quay=scene.objects["CAIS | contenção costeira alinhada à linha de costa"]
piers=[o for o in scene.objects if o.name.startswith("PIER OSM |")]
api=runpy.run_path(str(root/"automation/blender/component_fingerprint.py")); sig=api["signature"]
protected={o.name:sig(o) for o in [ground,water,quay,*piers]}
wl=float(water.get("boas_water_level_m",0.35)); threshold=wl-0.05

verts=[tuple(v.co) for v in source.data.vertices]
groups={"land":[],"transition":[],"submerged":[]}
for p in source.data.polygons:
    zs=[verts[i][2] for i in p.vertices]
    if min(zs)>=threshold: groups["land"].append(list(p.vertices))
    elif max(zs)<threshold: groups["submerged"].append(list(p.vertices))
    else: groups["transition"].append(list(p.vertices))

col=bpy.data.collections.get("EXPANSAO | COSTA E FUNDO | B49")
if not col:
    col=bpy.data.collections.new("EXPANSAO | COSTA E FUNDO | B49"); scene.collection.children.link(col)

def make(name,faces,role):
    used=sorted({i for f in faces for i in f}); remap={old:i for i,old in enumerate(used)}
    nv=[verts[i] for i in used]; nf=[[remap[i] for i in f] for f in faces]
    me=bpy.data.meshes.new(name+"_MESH"); me.from_pydata(nv,[],nf); me.update()
    ob=bpy.data.objects.new(name,me); col.objects.link(ob)
    if source.data.materials:
        for m in source.data.materials: me.materials.append(m)
    ob["boas_revision"]="R30B.49"; ob["boas_classification"]="ADAPT_LOCAL"
    ob["boas_runtime_role"]=role; ob["boas_gameplay_approved"]=False
    ob["boas_water_level_reference_m"]=wl; ob["boas_source_dem_relative_only"]=True
    return ob

land=make("EXPANSAO B49 | terra emersa costeira | candidata",groups["land"],"terrain_land_candidate")
trans=make("EXPANSAO B49 | faixa de transicao costeira | candidata",groups["transition"],"shore_transition_candidate")
sub=make("EXPANSAO B49 | fundo submerso DEM relativo | candidato",groups["submerged"],"underwater_seabed_reference_candidate")

# B48 permanece no arquivo como histórico, mas não renderiza nem aparece no viewport da revisão B49.
source.hide_viewport=True; source.hide_render=True
source["boas_superseded_by"]="R30B.49"

changed=[n for n,b in protected.items() if n not in scene.objects or sig(scene.objects[n])!=b]
assert not changed,changed
scene["boas_validation_revision"]="R30B.49"
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
sha=hashlib.sha256(out.read_bytes()).hexdigest()
def stats(ob):
    zs=[v.co.z for v in ob.data.vertices]
    return {"vertices":len(ob.data.vertices),"faces":len(ob.data.polygons),"z_min":min(zs) if zs else None,"z_max":max(zs) if zs else None}
report={
 "schema":"boas/coast-seabed-r30b49-v1","source_before":src,
 "source_after":{"file":out.relative_to(root).as_posix(),"revision":"R30B.49","sha256":sha},
 "water_level_m":wl,"classification_threshold_m":threshold,
 "land":stats(land),"transition":stats(trans),"submerged":stats(sub),
 "existing_ground_changed":False,"water_changed":False,"quay_changed":False,"piers_changed":False,
 "protected_changes":changed,"runtime_exported":False,"approved":False,
 "notes":["Terra, transição e fundo submerso foram separados semanticamente; nenhuma elevação foi inventada ou achatada.","Fundo submerso é apenas referência candidata para futura batimetria/gameplay de mergulho."],
 "pending":["Validar visualmente a transição costa/água","Batimetria real continua ausente; não tratar o DEM terrestre como fundo final","Refinar encostas e vegetação em revisão posterior","Expandir recorte adicional usando a mesma disciplina"]
}
(root/"docs/reports/blender/coast_seabed_r30b49.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps(report,ensure_ascii=False))
