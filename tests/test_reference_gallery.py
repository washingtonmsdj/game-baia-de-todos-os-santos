import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("build_gallery", ROOT / "tools" / "references" / "build_gallery.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class ReferenceGalleryTests(unittest.TestCase):
    def test_gallery_includes_primary_secondary_and_candidate_coverage(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            area_dir = root / "world" / "areas" / "test-area"
            media_root = root / "world-reference"
            area_dir.mkdir(parents=True)
            (media_root / "test-area" / "a").mkdir(parents=True)
            (media_root / "test-area" / "a" / "ref.jpg").write_bytes(b"not-an-image-but-present")
            (area_dir / "area.json").write_text(json.dumps({"area_id": "test-area", "name": "Teste"}), encoding="utf-8")
            (area_dir / "locations.json").write_text(json.dumps({
                "locations": [
                    {"location_id": "a", "name": "A", "priority": 5, "fidelity_class": "A", "model_status": "blockout", "reference_status": "partial", "required_views": ["front"]},
                    {"location_id": "b", "name": "B", "priority": 4, "fidelity_class": "A", "model_status": "proxy", "reference_status": "partial", "required_views": ["waterfront_context"]}
                ]
            }), encoding="utf-8")
            (area_dir / "media-manifest.json").write_text(json.dumps({
                "media": [{
                    "media_id": "m1", "location_id": "a", "view": "front", "usage_class": "REFERENCIA_INTERNA",
                    "coverage": [{"location_id": "b", "view": "waterfront_context"}],
                    "storage": {"logical_path": "test-area/a/ref.jpg", "sha256": "a" * 64},
                    "provenance": {"license_status": "verified", "license": "CC BY 4.0", "source_url": "https://example.org"}
                }]
            }), encoding="utf-8")
            (area_dir / "reference-candidates.json").write_text(json.dumps({
                "candidates": [{
                    "candidate_id": "c1", "location_id": "a", "suggested_view": "detail", "status": "candidate",
                    "file_title": "File:X.jpg", "page_url": "https://commons.wikimedia.org/wiki/File:X.jpg", "expected_license": "CC BY 4.0",
                    "coverage": [{"location_id": "b", "view": "waterfront_context"}]
                }]
            }), encoding="utf-8")
            output = root / "artifacts" / "gallery.html"
            result = MODULE.build_gallery(root, "test-area", media_root, output)
            text = output.read_text(encoding="utf-8")
            self.assertIn("A", text)
            self.assertIn("B", text)
            self.assertIn("m1", text)
            self.assertIn("c1", text)
            self.assertIn("cobertura adicional", text)
            summaries = {item["location_id"]: item for item in result["locations"]}
            self.assertEqual(summaries["a"]["missing_views"], [])
            self.assertEqual(summaries["b"]["missing_views"], [])


if __name__ == "__main__":
    unittest.main()
