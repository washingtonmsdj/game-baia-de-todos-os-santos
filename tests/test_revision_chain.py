import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from tools.blender.audit_revision_chain import AREA, audit_chain


class RevisionChainTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        self.area = self.root / AREA
        self.area.mkdir(parents=True)
        (self.root / "blender").mkdir()
        (self.root / "evidence").mkdir()
        self.entries = []
        for number, parent in [(1, None), (2, "blender/b1.blend"), (3, "blender/b2.blend")]:
            name = f"blender/b{number}.blend"
            body = b"BLENDER" + bytes([number])
            (self.root / name).write_bytes(body)
            evidence = f"evidence/b{number}.json"
            (self.root / evidence).write_text('{"approved":false}', encoding="utf-8")
            self.entries.append({"file": name, "revision": f"R30B.{number}",
                                 "parent_file": parent,
                                 "evidence": evidence,
                                 "status": "authoring_candidate",
                                 "sha256": hashlib.sha256(body).hexdigest(),
                                 "production_ready": False})
        (self.root / "blender/production.blend").write_bytes(b"production")
        self.catalog = {"schema": "boas/blender-revisions-v1",
                        "production_source_reference": "production.json#/world_source",
                        "selection_policy": "explicit_pointer_never_filename_mtime_or_open_window",
                        "authoring_source": dict(self.entries[-1]),
                        "revisions": list(self.entries)}
        self.production = {"world_source": {"file": "blender/production.blend"}}
        self.save()
        subprocess.run(["git", "-C", str(self.root), "add", "."], check=True)

    def save(self):
        (self.area / "blender-revisions.json").write_text(json.dumps(self.catalog), encoding="utf-8")
        (self.area / "production.json").write_text(json.dumps(self.production), encoding="utf-8")

    def test_healthy_chain_and_verified_hash(self):
        result = audit_chain(self.root, verify_sha=True, require_tracked=True)
        self.assertTrue(result["passed"], result["errors"])
        self.assertEqual(3, result["ancestry_count"])
        self.assertEqual(3, result["validated_sha256"])
        self.assertEqual("R30B.3", result["records"][0]["revision"])
        self.assertEqual("R30B.1", result["records"][-1]["revision"])
        self.assertEqual(0, result["source_untracked"])

    def test_detects_modified_file_without_modifying_it(self):
        path = self.root / "blender/b2.blend"
        path.write_bytes(b"changed")
        result = audit_chain(self.root, verify_sha=True)
        self.assertFalse(result["passed"])
        self.assertTrue(any("R30B.2:SHA-256 divergente" == v for v in result["errors"]))
        self.assertEqual(b"changed", path.read_bytes())

    def test_detects_missing_ancestor_file(self):
        (self.root / "blender/b2.blend").unlink()
        result = audit_chain(self.root)
        self.assertIn("R30B.2:Fonte ausente", result["errors"])

    def test_detects_broken_parent_pointer(self):
        self.catalog["authoring_source"]["parent_file"] = "blender/nonexistent.blend"
        self.save()
        result = audit_chain(self.root)
        self.assertFalse(result["passed"])
        self.assertTrue(any("Ancestral ausente" in err for err in result["errors"]))

    def test_detects_cycle_without_infinite_loop(self):
        self.catalog["revisions"][0]["parent_file"] = "blender/b3.blend"
        self.save()
        result = audit_chain(self.root)
        self.assertFalse(result["passed"])
        self.assertTrue(any("circular" in err for err in result["errors"]))

    def test_detects_duplicate_registry_path(self):
        self.catalog["revisions"].append(dict(self.entries[1]))
        self.save()
        self.assertTrue(any("duplicidade" in err for err in audit_chain(self.root)["errors"]))

    def test_detects_evidence_missing(self):
        (self.root / "evidence/b2.json").unlink()
        self.assertTrue(any("Evidência ausente" in err for err in audit_chain(self.root)["errors"]))

    def test_untracked_is_warning_until_strict_mode(self):
        (self.root / "evidence/b1.json").rename(self.root / "evidence/new.json")
        self.catalog["revisions"][0]["evidence"] = "evidence/new.json"
        self.save()
        loose = audit_chain(self.root)
        self.assertTrue(loose["passed"])
        self.assertGreater(loose["evidence_untracked"], 0)
        strict = audit_chain(self.root, require_tracked=True)
        self.assertFalse(strict["passed"])

    def test_rejects_wrong_current_pointer_hash(self):
        self.catalog["authoring_source"]["sha256"] = "b" * 64
        self.save()
        result = audit_chain(self.root)
        self.assertTrue(any("Ponteiro diverge" in err for err in result["errors"]))

    def test_rejects_path_traversal(self):
        self.catalog["authoring_source"]["parent_file"] = "../not-allowed.blend"
        self.save()
        self.assertTrue(any("inseguro" in err for err in audit_chain(self.root)["errors"]))

    def test_requires_authority_and_never_promotes_production(self):
        self.catalog["selection_policy"] = "latest"
        self.save()
        with self.assertRaisesRegex(ValueError, "não explícita"):
            audit_chain(self.root)
        self.catalog["selection_policy"] = "explicit_pointer_never_filename_mtime_or_open_window"
        self.production["world_source"]["file"] = "blender/b3.blend"
        self.save()
        self.assertFalse(audit_chain(self.root)["passed"])


if __name__ == "__main__":
    unittest.main()
