import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_module(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


register_media = load_module("register_media", "tools/references/register_media.py")
reference_gaps = load_module("reference_gaps", "tools/references/reference_gaps.py")


class ReferenceCoverageTests(unittest.TestCase):
    def test_parse_coverage_deduplicates_primary_and_repeated_pairs(self):
        result = register_media.parse_coverage(
            ["mercado-modelo:front", "cais-praca-cairu:waterfront_context", "cais-praca-cairu:waterfront_context"],
            {"mercado-modelo", "cais-praca-cairu"},
            ("mercado-modelo", "front"),
        )
        self.assertEqual(result, [{"location_id": "cais-praca-cairu", "view": "waterfront_context", "notes": ""}])

    def test_media_pairs_expose_primary_and_secondary_coverage(self):
        item = {
            "location_id": "mercado-modelo",
            "view": "roof",
            "coverage": [
                {"location_id": "cais-praca-cairu", "view": "waterfront_context"},
                {"location_id": "baia-agua-mvp", "view": "waterfront_context"},
            ],
        }
        self.assertEqual(
            list(reference_gaps.media_pairs(item)),
            [
                ("mercado-modelo", "roof"),
                ("cais-praca-cairu", "waterfront_context"),
                ("baia-agua-mvp", "waterfront_context"),
            ],
        )

    def test_candidate_pairs_expose_primary_and_secondary_coverage(self):
        item = {
            "location_id": "cais-praca-cairu",
            "suggested_view": "waterfront_context",
            "coverage": [{"location_id": "mercado-modelo", "view": "waterfront_context"}],
        }
        self.assertEqual(
            list(reference_gaps.candidate_pairs(item)),
            [("cais-praca-cairu", "waterfront_context"), ("mercado-modelo", "waterfront_context")],
        )


if __name__ == "__main__":
    unittest.main()
