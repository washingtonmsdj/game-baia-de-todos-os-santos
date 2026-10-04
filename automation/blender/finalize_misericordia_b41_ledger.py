"""Confirma apenas a correção de binding/apoio central da Misericórdia na B41."""
import json,hashlib
from pathlib import Path

root=Path(__file__).resolve().parents[2]
ledger_path=root/"world/areas/mvp-centro-lacerda/road-corrections.json"
network_path=root/"world/areas/mvp-centro-lacerda/transport-network.json"
report_path=root/"docs/reports/blender/misericordia_profile_r30b41.json"
preservation_path=root/"docs/reports/blender/road_width_preservation_b39_b41.json"
audit_path=root/"docs/reports/blender/rondesp_network_current.json"
registry_path=root/"world/areas/mvp-centro-lacerda/blender-revisions.json"

ledger=json.loads(ledger_path.read_text(encoding="utf8"))
network=json.loads(network_path.read_text(encoding="utf8"))
report=json.loads(report_path.read_text(encoding="utf8"))
preservation=json.loads(preservation_path.read_text(encoding="utf8"))
audit=json.loads(audit_path.read_text(encoding="utf8"))
registry=json.loads(registry_path.read_text(encoding="utf8"))

assert ledger["cycle"]=="2026-10-04-B41"
assert registry["authoring_source"]["revision"]=="R30B.41"
assert report["validation"]["binding_error_resolved"] is True
assert report["validation"]["network_center_support_missing_before"]==86
assert report["validation"]["network_center_support_missing_after"]==66
assert report["validation"]["unresolved_endpoint_binding_before"]==89
assert report["validation"]["unresolved_endpoint_binding_after"]==89
assert preservation["source_reopened"] is True
assert preservation["road_object_signature_identical"] is True
assert preservation["maximum_width_delta_m"]==0
assert preservation["road_widths_changed"] is False

edge=next(x for x in audit["segments"] if x["edge_id"]=="way-803899198-seg-1")
assert edge["issues"].get("center_support_missing",0)==0
for still_open in ("vertical_discontinuity","crossfall_review","grade_review","wheel_outside_pavement"):
    assert edge["issues"].get(still_open,0)>0

issue_id="mvp-centro-lacerda/way-803899198/nodes-5436479156-1703384768/center_support_missing"
issue=next(x for x in ledger["issues"] if x["issue_id"]==issue_id)
assert issue["status"]=="not_observed_needs_confirmation"
acceptance={
    "cycle":"2026-10-04-B41",
    "correction_id":"2026-10-04-B41-misericordia-profile-binding",
    "classification":"ERROR",
    "before_occurrences":20,
    "after_occurrences":0,
    "source_reopened":True,
    "full_network_edges_checked":743,
    "unresolved_endpoint_binding_unchanged":89,
    "road_widths_changed":False,
    "visual_geometry_changed":False,
    "evidence":"docs/reports/blender/misericordia_profile_r30b41.json",
    "width_preservation_evidence":"docs/reports/blender/road_width_preservation_b39_b41.json",
    "remaining_segment_issues":edge["issues"],
    "scope":"Resolve apenas o binding/perfil derivado e a ausência de apoio central; não aprova geometria viária, largura, tráfego ou gameplay."
}
issue["status"]="resolved"
issue["acceptance"]=acceptance
issue["last_seen_cycle"]="2026-10-04-B41"
issue["history"].append({"cycle":"2026-10-04-B41","event":"confirmed_resolved","acceptance":acceptance})

correction={
    "correction_id":acceptance["correction_id"],
    "classification":"ERROR",
    "scope":"Rua da Misericórdia OSM 803899198, segmento nós 5436479156-1703384768; perfil derivado do helper R30A7.",
    "root_cause":"Interpolação Z linear entre nós OSM esparsos não acompanhava o perfil vertical não linear do pavimento funcional.",
    "before":{"revision":"R30B.40","source_sha256":report["source_before"]["sha256"],"helper_points":3,"center_support_missing":20},
    "after":{"revision":"R30B.41","source_sha256":report["source_after"]["sha256"],"helper_points":report["new_profile_points"],"center_support_missing":0},
    "method":{"spacing_m":report["spacing_m"],"clearance_m":report["clearance_m"],"source_nodes_preserved":True,"source_xy_preserved":True,"all_samples_road_material":report["all_samples_road_material"]},
    "invariants":{"protected_components":report["protected_components"],"protected_changes":report["protected_changes"],"road_widths_changed":False,"visual_geometry_changed":False,"collision_changed":False,"runtime_exported":False},
    "validation":report["validation"],
    "source_reopened":True,
    "evidence":"docs/reports/blender/misericordia_profile_r30b41.json",
    "width_preservation_evidence":"docs/reports/blender/road_width_preservation_b39_b41.json",
    "status":"verified_binding_only_gameplay_pending"
}
existing=[x for x in ledger.get("applied_corrections",[]) if x.get("correction_id")==correction["correction_id"]]
assert not existing
ledger.setdefault("applied_corrections",[]).append(correction)
ledger["production_ready"]=False
ledger_path.write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps({"resolved_issue":issue_id,"status":issue["status"],"applied_corrections":len(ledger["applied_corrections"]),"remaining_segment_issues":edge["issues"]},ensure_ascii=False))
