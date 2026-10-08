import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from tools.blender.audit_authoring_inventory import audit, file_record, safe_path


class AuthoringInventoryTests(unittest.TestCase):
    def setUp(self):
        self.workspace = tempfile.TemporaryDirectory()
        self.addCleanup(self.workspace.cleanup)
        self.root = Path(self.workspace.name)
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        self.area = self.root / "world/areas/mvp-centro-lacerda"
        self.area.mkdir(parents=True)
        (self.root / "blender").mkdir()
        (self.root / "reports").mkdir()
        self.source = b"BLENDER-candidate-scene"
        self.baseline = b"BLENDER-production-scene"
        (self.root / "blender/scene.blend").write_bytes(self.source)
        (self.root / "blender/parent.blend").write_bytes(b"parent")
        (self.root / "blender/production.blend").write_bytes(self.baseline)
        (self.root / "reports/test.json").write_text('{"passed":false}', encoding="utf-8")
        self.revisions = {
            "production_source_reference": "production.json#/world_source",
            "selection_policy": "explicit_pointer_never_filename_mtime_or_open_window",
            "authoring_source": {
                "file": "blender/scene.blend", "revision": "R30B.97",
                "sha256": hashlib.sha256(self.source).hexdigest(),
                "parent_file": "blender/parent.blend", "evidence": "reports/test.json",
                "production_ready": False,
            },
        }
        self.production = {"area_id": "mvp-centro-lacerda",
                           "world_source": {"file": "blender/production.blend",
                                            "revision": "R30B.30",
                                            "sha256": hashlib.sha256(self.baseline).hexdigest()}}
        self.save()
        subprocess.run(["git", "-C", str(self.root), "add", "."], check=True)

    def save(self):
        (self.area / "blender-revisions.json").write_text(
            json.dumps(self.revisions), encoding="utf-8")
        (self.area / "production.json").write_text(
            json.dumps(self.production), encoding="utf-8")

    def test_clean_authoring_and_production_stay_distinct(self):
        result = audit(self.root, require_tracked=True)
        self.assertTrue(result["passed"])
        self.assertEqual("R30B.97", result["authoring_revision"])
        self.assertEqual("R30B.30", result["production_revision"])
        self.assertFalse(result["production_ready"])
        self.assertTrue(result["records"]["authoring"]["sha256_verified"])

    def test_source_hash_changed_fails_closed(self):
        (self.root / "blender/scene.blend").write_bytes(b"changed while app open")
        result = audit(self.root)
        self.assertIn("authoring:sha256_divergente", result["issues"])

    def test_incomplete_evidence_fails_closed(self):
        self.revisions["authoring_source"]["evidence"] = "reports/missing.json"
        self.save()
        result = audit(self.root)
        self.assertIn("authoring:evidence_ausente", result["issues"])

    def test_untracked_candidate_warns_and_strictly_blocks(self):
        (self.root / "blender/scene.blend").rename(self.root / "blender/other.blend")
        self.revisions["authoring_source"]["file"] = "blender/other.blend"
        self.save()
        result = audit(self.root)
        self.assertIn("authoring:nao_versionado_git", result["warnings"])
        self.assertTrue(result["passed"])
        self.assertFalse(audit(self.root, require_tracked=True)["passed"])

    def test_path_traversal_is_rejected(self):
        with self.assertRaises(ValueError):
            safe_path(self.root, "../outside.blend")
        self.revisions["authoring_source"]["file"] = "../outside.blend"
        self.save()
        result = audit(self.root)
        self.assertFalse(result["passed"])
        self.assertTrue(any("inseguro" in issue for issue in result["issues"]))

    def test_lfs_pointer_not_treated_as_real_blend(self):
        pointer = (b"version https://git-lfs.github.com/spec/v1\n"
                   + b"oid sha256:" + b"a"*64 + b"\nsize 14\n")
        (self.root / "blender/scene.blend").write_bytes(pointer)
        result = audit(self.root)
        self.assertIn("authoring:somente_ponteiro_lfs", result["issues"])

    def test_ssot_authority_must_be_explicit(self):
        self.revisions["selection_policy"] = "latest_filename"
        self.save()
        with self.assertRaisesRegex(ValueError, "escolha de revisão"):
            audit(self.root)

    def test_never_marks_unapproved_source_as_production(self):
        self.production["world_source"] = dict(self.revisions["authoring_source"])
        self.save()
        result = audit(self.root)
        self.assertIn("fonte_nao_aprovada_e_igual_a_producao", result["issues"])


if __name__ == "__main__":
    unittest.main()
