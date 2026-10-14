"""Valida integridade da pesquisa; não aprova registro ou física."""
import ast
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/reports/research/lacerda-b80-installation-xy"


def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def digest(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def main():
    prefix = "docs/reports/research/lacerda-b80-installation-xy/"
    result = read(prefix + "result.json")
    assert result["decision"] == "NO_SCENE_CHANGE"
    for key in ["ORIGIN_OF_3_709_FOUND", "SEMOB_INSTALLATION_DATA_FOUND", "XY_REGISTRATION_ACCEPTED", "B81_created", "CCD_repeated", "production_exported"]:
        assert result[key] is False
    controls = read(prefix + "xy_controls_round2.json")
    assert controls["transform"] is None and len(controls["controls"]) == 9
    for c in controls["controls"]:
        assert c["scene_object"] is None and c["scene_point"] is None and c["residual"] is None
        assert c["accepted_for_registration"] is False
    assert all(c["non_collinear_document_points"] and c["accepted_scene_correspondences"] == 0 for c in controls["non_collinearity"])
    snapshots = read(prefix + "genealogy_snapshots_readonly.json")
    assert snapshots["read_only"] and not snapshots["saved"]
    assert [len(r["shared_exact_world_offset"]) for r in snapshots["sources"]] == [54, 54, 56]
    for r in snapshots["sources"]:
        assert digest(r["file"]) == r["sha256"]
    baseline = read("docs/reports/research/lacerda-issue22/reconciliation.json")
    for r in baseline["protected_revisions"]:
        assert digest(r["file"]) == r["expected_sha256"]
    assert digest("world/geographic-reference.json") == baseline["ssot_sha256"]
    for r in baseline["canonical_local_reports"]:
        assert digest(r["file"]) == r["sha256"]
    triage = read("docs/reports/research/lacerda-registration-b80/witness_reclassification.json")
    assert len(triage["witnesses"]) == 27 and not triage["movement_enabled"]
    assert all(w["registration_classification"] == "UNRESOLVED" and w["authorized_correction"] is None for w in triage["witnesses"])
    records = read(prefix + "source_summary.json")["records"]
    raw_count = 0
    for r in records:
        assert not r["technical_installation_document"]
        if "raw_file" in r:
            assert digest(r["raw_file"]) == r["sha256"]
            assert subprocess.run(["git", "check-ignore", "--quiet", r["raw_file"]], cwd=ROOT).returncode == 0
            raw_count += 1
    paths = ["automation/blender/inspect_lacerda_genealogy_readonly.py", "tools/references/trace_lacerda_b80_genealogy.py", "tools/references/acquire_lacerda_semob_locators.py", "tools/references/document_lacerda_b80_installation_xy.py", "tools/references/validate_lacerda_b80_installation_xy.py"]
    for path in paths:
        ast.parse((ROOT / path).read_text(encoding="utf-8"), filename=path)
    verified = {"status": "passed", "protected_snapshots": 5, "historical_snapshots_readonly": 3, "ssot_and_canonical_reports_unchanged": True, "document_points_non_collinear": 9, "accepted_scene_controls": 0, "witnesses_UNRESOLVED": 27, "raw_locator_files_hashed_and_git_ignored": raw_count, "python_syntax_checked": len(paths), "CCD_repeated": False, "scene_changed": False, "architectural_registration_approved": False, "installation_dimensions_verified": False}
    (OUT / "validation.json").write_text(json.dumps(verified, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(verified, ensure_ascii=False))


if __name__ == "__main__":
    main()
