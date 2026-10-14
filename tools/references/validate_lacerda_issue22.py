"""Verifica apenas integridade/rastreabilidade da pesquisa #22, não física."""
from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from reconcile_lacerda_issue22 import ROOT, OUT, digest, read, write


def main():
    reconciliation = read(OUT / "reconciliation.json")
    triage = read(OUT / "witness_triage.json")
    matrix = read(OUT / "unknown_matrix.json")
    registry = read(ROOT / "world/data-provenance.json")
    resources = {r["resource_id"]: r for r in registry["resources"]}
    canonical = read(ROOT / "docs/reports/blender/lacerda-controller-b80/triage_b80.json")["solid_penetration_witnesses"]
    assert reconciliation["decision"] == "NO_SCENE_CHANGE"
    assert reconciliation["authorized_geometry_corrections"] == []
    assert not reconciliation["movement_enabled"] and not reconciliation["B81_created"] and not reconciliation["production_exported"]
    branch = subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip()
    assert branch == reconciliation["branch"]
    for row in reconciliation["protected_revisions"]:
        assert digest(ROOT / row["file"]) == row["expected_sha256"]
    for row in reconciliation["canonical_local_reports"]:
        assert digest(ROOT / row["file"]) == row["sha256"]
    assert digest(ROOT / "world/geographic-reference.json") == reconciliation["ssot_sha256"]
    assert len(triage["witnesses"]) == len(canonical) == 27
    for new, old in zip(triage["witnesses"], canonical):
        for field in ["component", "obstacle", "t_witness"]:
            assert new[field] == old[field]
        assert new["scene_detection_classification"] == old["classification"]
        assert new["independent_correction_classification"] == "NEEDS_REVIEW"
        assert new["authorized_correction"] is None
        assert 0 <= new["surface_contact_interval"]["first"] <= new["t_witness"] <= new["surface_contact_interval"]["last"] <= 1
        assert all(key in resources for key in new["independent_evidence"])
    assert all(r["verified_current_value"] is None for r in matrix["unknowns"])
    for row in read(OUT / "source_summary.json")["resources"]:
        assert row["release_status"] == "DEV_REFERENCE_ONLY" and row["derived_objects"] == []
        for raw in row["raw_files"]:
            assert digest(ROOT / raw["path"]) == raw["sha256"]
            assert subprocess.run(["git", "check-ignore", "--quiet", raw["path"]], cwd=ROOT).returncode == 0
    files = sorted((ROOT / "tools/references").glob("*issue22.py"))
    for file in files:
        ast.parse(file.read_text(encoding="utf-8"), filename=str(file))
    profile = read(ROOT / "world/areas/mvp-centro-lacerda/slice-engine-contract-b80.json")
    assert profile["release_ready"] is False
    result = {"status": "passed", "branch": branch, "protected_revisions": 5, "canonical_reports_unchanged": True, "witnesses_traceable": 27, "resources_hashed_and_excluded_from_git": reconciliation["registered_resources"], "python_syntax_checked": len(files), "engine_physics_tested": False, "CCD_repeated": False, "scene_modified": False}
    write(OUT / "validation.json", result)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
