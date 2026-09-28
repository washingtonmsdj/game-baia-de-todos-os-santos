from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "compare_dem_osm_coverage", ROOT / "tools/terrain/compare_dem_osm_coverage.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def dem(bounds, pixel=10.0):
    return {
        "schema": "bay-of-all-saints/dem-audit-v2",
        "metadata": {
            "bounds": {"left": bounds[0], "bottom": bounds[1], "right": bounds[2], "top": bounds[3]},
            "pixel_size": {"x": pixel, "y": pixel},
        },
    }


def osm(bounds):
    return {
        "schema": "bay-of-all-saints/osm-structure-v2",
        "bounds_epsg3857": {"min_x": bounds[0], "min_y": bounds[1], "max_x": bounds[2], "max_y": bounds[3]},
    }


class DEMOSMCoverageTests(unittest.TestCase):
    def test_full_coverage_with_margin(self):
        result = MODULE.compare(dem((0, 0, 1000, 1000)), osm((100, 100, 900, 900)), 20)
        self.assertEqual(result["status"], "covered_with_margin")
        self.assertAlmostEqual(result["areas_projected"]["target_bbox_coverage_ratio"], 1.0)
        self.assertEqual(result["margins"]["west_m_projected"], 100.0)
        self.assertEqual(result["margins_in_pixels_approx"]["west_pixels_approx"], 10.0)
        self.assertEqual(result["target"]["kind"], "full_osm_bounds")

    def test_inside_but_edge_sensitive(self):
        result = MODULE.compare(dem((0, 0, 1000, 1000)), osm((5, 100, 900, 900)), 20)
        self.assertEqual(result["status"], "covered_edge_sensitive")
        self.assertTrue(result["warnings"])

    def test_partial_coverage_is_insufficient(self):
        result = MODULE.compare(dem((0, 0, 1000, 1000)), osm((-100, 100, 900, 900)), 20)
        self.assertEqual(result["status"], "insufficient")
        self.assertLess(result["areas_projected"]["target_bbox_coverage_ratio"], 1.0)
        self.assertLess(result["margins"]["west_m_projected"], 0)

    def test_non_overlapping(self):
        result = MODULE.compare(dem((0, 0, 100, 100)), osm((200, 200, 300, 300)), 0)
        self.assertEqual(result["status"], "insufficient")
        self.assertEqual(result["areas_projected"]["intersection_m2"], 0.0)

    def test_capture_window_can_be_covered_even_when_full_osm_bbox_is_huge(self):
        result = MODULE.compare(
            dem((0, 0, 1000, 1000)),
            osm((-10000, -10000, 10000, 10000)),
            20,
            target_bounds_epsg3857={"min_x": 100, "min_y": 100, "max_x": 900, "max_y": 900},
            target_metadata={"source_kind": "aleph_manifest"},
        )
        self.assertEqual(result["status"], "covered_with_margin")
        self.assertEqual(result["target"]["kind"], "capture_bounds")
        self.assertAlmostEqual(result["areas_projected"]["target_bbox_coverage_ratio"], 1.0)
        self.assertGreater(result["areas_projected"]["full_osm_bbox_m2"], result["areas_projected"]["target_bbox_m2"])
        self.assertTrue(any("ways completos" in warning for warning in result["warnings"]))

    def test_extract_manifest_bounds_and_projection(self):
        parsed = MODULE.extract_wgs84_bounds({"bounds": [-12.977, -38.5155, -12.969, -38.508]})
        self.assertEqual(parsed["source_kind"], "aleph_manifest")
        projected = MODULE.project_wgs84_bounds(parsed["wgs84"])
        self.assertLess(projected["min_x"], projected["max_x"])
        self.assertLess(projected["min_y"], projected["max_y"])

    def test_extract_source_summary_bounds(self):
        parsed = MODULE.extract_wgs84_bounds({"geografia": {"bounds": [-12.977, -38.5155, -12.969, -38.508]}})
        self.assertEqual(parsed["source_kind"], "aleph_source_summary")


if __name__ == "__main__":
    unittest.main()
