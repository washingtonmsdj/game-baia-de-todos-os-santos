"""R30B.50: oculta blockouts legados de encosta sem apagar geometria."""
import bpy,json,hashlib,runpy
from pathlib import Path
root=Path(__file__).resolve().parents[2]; scene=bpy.context.scene
reg=json.loads((root/"world/areas/mvp-centro-lacerda/blender-revisions.json").read_text(encoding="utf8")); src=reg["validation_source"]
assert src["revision"]=="R30B.49"; assert Path(bpy.data.filepath).resolve()==(root/src["file"]).resolve()
out=root/"blender/salvador_lacerda_r30b50_encosta_sem_blockouts.blend"; assert not out.exists()
api=runpy.run_path(str(root/"automation/blender/component_fingerprint.py")); sig=api["signature"]
protected_names=[
"MVP | terreno corrigido | colisão estática",
"BAÍA DE TODOS-OS-SANTOS | superfície e recorte costeiro",
"CAIS | contenção costeira alinhada à linha de costa",
"EXPANSAO B49 | terra emersa costeira | candidata",
"EXPANSAO B49 | faixa de transicao costeira | candidata",
"EXPANSAO B49 | fundo submerso DEM relativo | candidato"
]
protected_names += [o.name for o in scene.objects if o.name.startswith("PIER OSM |")]
protected={n:sig(scene.objects[n]) for n in protected_names}

legacy=[
"Encosta | fechamento lateral","Encosta | fechamento lateral.001",
"Encosta | faixa 00","Encosta | faixa 01","Encosta | faixa 02","Encosta | faixa 03","Encosta | faixa 04",
"Encosta | coroamento","Encosta | coroamento.001"
]
rows=[]
for name in legacy:
    o=scene.objects[name]
    rows.append({"name":name,"verts":len(o.data.vertices),"polys":len(o.data.polygons),"was_hide_viewport":o.hide_viewport,"was_hide_render":o.hide_render})
    o.hide_viewport=True; o.hide_render=True
    o["boas_status"]="legacy_slope_blockout_hidden_r30b50"
    o["boas_replacement_basis"]="functional_ground_and_coastal_expansion_candidates"
changed=[n for n,b in protected.items() if sig(scene.objects[n])!=b]
assert not changed,changed
scene["boas_validation_revision"]="R30B.50"
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
sha=hashlib.sha256(out.read_bytes()).hexdigest()
report={
 "schema":"boas/legacy-slopes-r30b50-v1","source_before":src,
 "source_after":{"file":out.relative_to(root).as_posix(),"revision":"R30B.50","sha256":sha},
 "classification":"ERROR","hidden_legacy_objects":rows,
 "deleted_objects":0,"existing_ground_changed":False,"coastal_expansion_changed":False,
 "water_changed":False,"quay_changed":False,"piers_changed":False,"protected_changes":changed,
 "runtime_exported":False,"approved":False,
 "notes":["Blockouts de uma única face/baixa topologia foram ocultados, não apagados.","A encosta visível passa a usar superfícies funcionais/contínuas já presentes; não foi inventada nova topografia."],
 "pending":["Revisão visual da encosta sem blockouts","Refino de materiais/vegetação em etapa separada","Gameplay/runtime continuam não promovidos"]
}
(root/"docs/reports/blender/legacy_slopes_r30b50.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps(report,ensure_ascii=False))
