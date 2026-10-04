"""Promove R30B.41 a fonte de autoria candidata após validação geométrica, sem alterar runtime."""
import hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parents[2]
blend=root/"blender/salvador_lacerda_r30b41_perfil_misericordia.blend"
report_path=root/"docs/reports/blender/misericordia_profile_r30b41.json"
catalog_path=root/"world/areas/mvp-centro-lacerda/blender-revisions.json"
baseline_path=root/"artifacts/roads/rondesp/rondesp_network_current_pre_profile_audit.json"
candidate_path=root/"artifacts/roads/rondesp/rondesp_network_b41_candidate.json"

report=json.loads(report_path.read_text(encoding="utf8"))
sha=hashlib.sha256(blend.read_bytes()).hexdigest()
assert sha==report["source_after"]["sha256"]
baseline=json.loads(baseline_path.read_text(encoding="utf8"))
candidate=json.loads(candidate_path.read_text(encoding="utf8"))
old={x["edge_id"]:x for x in baseline["segments"]}
new={x["edge_id"]:x for x in candidate["segments"]}
target="way-803899198-seg-1"
assert old[target]["issues"].get("center_support_missing")==20
assert new[target]["issues"].get("center_support_missing",0)==0
assert new[target]["issues"].get("unresolved_endpoint_binding",0)==0
assert candidate["issue_counts"]["center_support_missing"]==baseline["issue_counts"]["center_support_missing"]-20
assert candidate["issue_counts"]["unresolved_endpoint_binding"]==baseline["issue_counts"]["unresolved_endpoint_binding"]
changed=[k for k in old if old[k].get("issues",{})!=new[k].get("issues",{})]
assert changed==[target],changed

report["validation"]={
    "method":"auditoria integral da rede com perfil derivado seguido como polilinha e quatro apoios reais da Rondesp",
    "graph_edges":candidate["graph_edges"],
    "changed_issue_segments":changed,
    "target_before":old[target]["issues"],
    "target_after":new[target]["issues"],
    "network_center_support_missing_before":baseline["issue_counts"]["center_support_missing"],
    "network_center_support_missing_after":candidate["issue_counts"]["center_support_missing"],
    "unresolved_endpoint_binding_before":baseline["issue_counts"]["unresolved_endpoint_binding"],
    "unresolved_endpoint_binding_after":candidate["issue_counts"]["unresolved_endpoint_binding"],
    "geometric_clear_segments_before":baseline["geometric_clear_segments"],
    "geometric_clear_segments_after":candidate["geometric_clear_segments"],
    "candidate_report":"artifacts/roads/rondesp/rondesp_network_b41_candidate.json",
    "binding_error_resolved":True,
    "full_gameplay_approved":False
}
report["pending"]=[
    "Grade/crossfall elevados na própria superfície funcional da Misericórdia exigem revisão geométrica separada",
    "Envelope/obstáculos e física dinâmica ainda não aprovados",
    "Largura real continua não verificada",
    "Runtime permanece na fonte registrada B30"
]
report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")

catalog=json.loads(catalog_path.read_text(encoding="utf8"))
before=catalog["authoring_source"]
assert before["revision"]=="R30B.40"
for row in catalog["revisions"]:
    if row.get("revision")=="R30B.40":
        assert row["status"]=="authoring_candidate"
        row["status"]="historical"
        row["notes"]="Substituída como fonte de autoria pela R30B.41; continua preservada e não foi promovida a runtime."
assert not any(row.get("revision")=="R30B.41" for row in catalog["revisions"])
entry={
    "file":"blender/salvador_lacerda_r30b41_perfil_misericordia.blend",
    "revision":"R30B.41",
    "status":"authoring_candidate",
    "parent_file":"blender/salvador_lacerda_r30b40_fluxos_e_colisao.blend",
    "evidence":"docs/reports/blender/misericordia_profile_r30b41.json",
    "sha256":sha,
    "notes":"Corrige somente o perfil derivado da Rua da Misericórdia; OSM, XY, largura, pavimento visual, colisor e runtime preservados. Gameplay continua não aprovado."
}
catalog["revisions"].append(entry)
catalog["authoring_source"]=entry.copy()
catalog_path.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps({"authoring_source":catalog["authoring_source"],"validation":report["validation"]},ensure_ascii=False))
