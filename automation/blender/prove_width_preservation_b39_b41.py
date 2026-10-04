"""Prova direta de preservação da superfície/larguras entre B39 e B41."""
import bpy,json,hashlib,math,runpy
from pathlib import Path
root=Path(__file__).resolve().parents[2]
registry=json.loads((root/"world/areas/mvp-centro-lacerda/blender-revisions.json").read_text(encoding="utf8"))
source_after=registry["authoring_source"]
assert source_after["revision"]=="R30B.41"
assert Path(bpy.data.filepath).resolve()==(root/source_after["file"]).resolve()
assert hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()==source_after["sha256"]
source_before=next(x for x in registry["revisions"] if x["revision"]=="R30B.39")

contract=json.loads((root/"world/areas/mvp-centro-lacerda/production.json").read_text(encoding="utf8"))
ground_name=contract["export"]["road_object"]
api=runpy.run_path(str(root/"automation/blender/component_fingerprint.py"))
current_sig=api["signature"](bpy.context.scene.objects[ground_name])
before_sig=api["inspect_file"](root/source_before["file"],[ground_name])[ground_name]
assert current_sig==before_sig,"Superfície viária usada na largura mudou entre B39 e B41"

old=json.loads((root/"docs/reports/blender/road_width_scene_b39.json").read_text(encoding="utf8"))
new=json.loads((root/"artifacts/roads/rondesp/road_width_scene_b41_compare.json").read_text(encoding="utf8"))
A={x["edge_id"]:x for x in old["segments"]};B={x["edge_id"]:x for x in new["segments"]}
assert A.keys()==B.keys()
changed=[];max_width_delta=0.;max_xy_delta=0.;max_z_delta=0.
for eid in A:
    a,b=A[eid],B[eid]
    assert a["osm_way_id"]==b["osm_way_id"]
    assert a.get("binding_status")==b.get("binding_status")
    assert len(a["stations"])==len(b["stations"])
    local=False
    for x,y in zip(a["stations"],b["stations"]):
        assert x["fraction"]==y["fraction"]
        assert x["issues"]==y["issues"]
        wx,wy=x.get("width_m"),y.get("width_m")
        if wx is None or wy is None: assert wx is wy
        else:
            d=abs(wx-wy);max_width_delta=max(max_width_delta,d);assert d<1e-9
        px,py=x["position"],y["position"]
        dxy=math.dist(px[:2],py[:2]);dz=abs(px[2]-py[2])
        max_xy_delta=max(max_xy_delta,dxy);max_z_delta=max(max_z_delta,dz)
        if dxy>1e-9 or dz>1e-9:local=True
    assert a.get("scene_pavement_width_median_m")==b.get("scene_pavement_width_median_m")
    if local:changed.append(eid)
assert max_width_delta==0
assert max_xy_delta<1e-9
assert max_z_delta<0.001
assert changed in ([],["way-803899198-seg-1"])

b40=json.loads((root/"docs/reports/blender/road_transport_b40.json").read_text(encoding="utf8"))
b41=json.loads((root/"docs/reports/blender/misericordia_profile_r30b41.json").read_text(encoding="utf8"))
assert b40["source_before"]["sha256"]==source_before["sha256"]
assert b40["source_after"]["sha256"]==b41["source_before"]["sha256"]
assert b41["source_after"]["sha256"]==source_after["sha256"]
assert not b40["road_widths_changed"] and not b40["protected_visual_differences"]
assert not b41["road_widths_changed"] and not b41["visual_geometry_changed"] and not b41["protected_changes"]

report={
 "schema":"boas/road-width-preservation-v1",
 "source_before":source_before,
 "source_after":source_after,
 "road_object":ground_name,
 "road_object_signature_identical":True,
 "road_widths_changed":False,
 "protected_visual_differences":[],
 "source_reopened":True,
 "width_audit_b39":"docs/reports/blender/road_width_scene_b39.json",
 "width_audit_b41_compare":"artifacts/roads/rondesp/road_width_scene_b41_compare.json",
 "width_segments_compared":len(A),
 "width_summary_identical":old["summary"]==new["summary"],
 "maximum_width_delta_m":max_width_delta,
 "maximum_station_xy_delta_m":max_xy_delta,
 "maximum_station_z_delta_m":max_z_delta,
 "station_position_differences":changed,
 "note":"A única diferença posicional é submilimétrica em Z numa estação já não resolvida da Misericórdia; largura, XY, issues, materiais, malha e transform da superfície viária são idênticos.",
 "chain_evidence":["docs/reports/blender/road_transport_b40.json","docs/reports/blender/misericordia_profile_r30b41.json"],
 "approved_for_real_width_claim":False
}
out=root/"docs/reports/blender/road_width_preservation_b39_b41.json"
out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps({k:report[k] for k in ("road_object_signature_identical","width_segments_compared","width_summary_identical","maximum_width_delta_m","maximum_station_z_delta_m","station_position_differences","source_reopened")},ensure_ascii=False))
