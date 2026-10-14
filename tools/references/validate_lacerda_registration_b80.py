"""Integridade do diagnóstico arquitetônico; não certifica arquitetura/colisão."""
import ast
import json
from pathlib import Path

from reconcile_lacerda_issue22 import digest, ROOT


def main():
    out = ROOT / "docs/reports/research/lacerda-registration-b80"
    read = lambda name: json.loads((out / name).read_text(encoding="utf-8"))
    registration = read("vertical_registration.json")
    xy = read("xy_control_attempts.json")
    diagnostic = read("vertical_decomposition.json")
    triage = read("witness_reclassification.json")
    baseline = json.loads((ROOT / "docs/reports/research/lacerda-issue22/witness_triage.json").read_text(encoding="utf-8"))
    assert digest(ROOT / registration["scene_source"]["file"]) == registration["scene_source"]["sha256"]
    assert digest(ROOT / registration["parent_ssot"]) == registration["ssot_sha256"]
    fit = registration["candidate_Z_only"]
    assert fit["scale_fixed"] == 1 and not fit["applied"]
    assert fit["full_transform"] is None and fit["XY_transform"] is None
    required = {"drawing_id", "drawing_point", "scene_object", "scene_point", "source", "confidence", "residual", "reason"}
    for control in registration["controls"] + xy["controls"]:
        assert required <= control.keys()
        assert not control["accepted_for_registration"]
    assert xy["transform_to_ssot"] is None
    assert not xy["physical_dimensions_from_pixels"] and not xy["scale_from_titleblock"]
    assert len(triage["witnesses"]) == len(baseline["witnesses"]) == 27
    for new, old in zip(triage["witnesses"], baseline["witnesses"]):
        for key in ["component", "obstacle", "t_witness", "scene_detection_classification"]:
            assert new[key] == old[key]
        assert new["registration_classification"] == "UNRESOLVED"
        assert new["authorized_correction"] is None
    assert not triage["movement_enabled"] and not diagnostic["correction_authorized"]
    assert abs(diagnostic["decomposition"]["nominal_sum"] - diagnostic["difference_CCD_project"]) < 1e-9
    assert abs(diagnostic["lower_sill"]["local_bottom"] + diagnostic["lower_sill"]["translation_z"] - diagnostic["lower_sill"]["world_bottom"]) < 1e-9
    files = [ROOT / "automation/blender/inspect_architectural_registration_b80.py", ROOT / "tools/references/register_lacerda_drawings_b80.py", Path(__file__)]
    for file in files:
        ast.parse(file.read_text(encoding="utf-8"))
    result = {"status": "passed", "scene_and_ssot_unchanged": True, "controls_schema_checked": len(registration["controls"]) + len(xy["controls"]), "accepted_registration_controls": 0, "witnesses_preserved": 27, "decomposition_verified": True, "scene_modified": False, "CCD_repeated": False, "architectural_registration_approved": False, "engine_physics_tested": False}
    (out / "validation.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
