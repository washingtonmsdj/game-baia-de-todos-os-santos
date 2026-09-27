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
        self.assertAlmostEqual(result["areas_projected"]["osm_bbox_coverage_ratio"], 1.0)
        self.assertEqual(result["margins"]["west_m_projected"], 100.0)
        self.assertEqual(result["margins_in_pixels_approx"]["west_pixels_approx"], 10.0)

    def test_inside_but_edge_sensitive(self):
        result = MODULE.compare(dem((0, 0, 1000, 1000)), osm((5, 100, 900, 900)), 20)
        self.assertEqual(result["status"], "covered_edge_sensitive")
        self.assertTrue(result["warnings"])

    def test_partial_coverage_is_insufficient(self):
        result = MODULE.compare(dem((0, 0, 1000, 1000)), osm((-100, 100, 900, 900)), 20)
        self.assertEqual(result["status"], "insufficient")
        self.assertLess(result["areas_projected"]["osm_bbox_coverage_ratio"], 1.0)
        self.assertLess(result["margins"]["west_m_projected"], 0)

    def test_non_overlapping(self):
        result = MODULE.compare(dem((0, 0, 100, 100)), osm((200, 200, 300, 300)), 0)
        self.assertEqual(result["status"], "insufficient")
        self.assertEqual(result["areas_projected"]["intersection_m2"], 0.0)


if __name__ == "__main__":
    unittest.main()
