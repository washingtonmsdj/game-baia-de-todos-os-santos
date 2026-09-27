from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("audit_road_profiles", ROOT / "tools/terrain/audit_road_profiles.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class TerrainRoadProfileTests(unittest.TestCase):
    def test_densify_respects_spacing(self):
        points = MODULE.densify([[0.0, 0.0], [10.0, 0.0]], spacing_m=3.0)
        self.assertEqual(points[0], (0.0, 0.0))
        self.assertEqual(points[-1], (10.0, 0.0))
        self.assertEqual(len(points), 5)
        distances = [MODULE.distance(a, b) for a, b in zip(points, points[1:])]
        self.assertTrue(all(value <= 3.0 + 1e-9 for value in distances))

    def test_analyze_profile_flags_grade_and_jump(self):
        points = [(0.0, 0.0), (5.0, 0.0), (10.0, 0.0)]
        elevations = [10.0, 11.0, 18.0]
        result = MODULE.analyze_profile(points, elevations, grade_review=0.35, jump_review_m=4.0)
        self.assertIn("grade_review", result["flags"])
        self.assertIn("jump_review", result["flags"])
        self.assertEqual(len(result["flagged_segments"]), 1)
        self.assertAlmostEqual(result["max_abs_grade"], 1.4)
        self.assertAlmostEqual(result["max_abs_jump_m"], 7.0)

    def test_nodata_is_reported_but_not_interpolated(self):
        points = [(0.0, 0.0), (5.0, 0.0), (10.0, 0.0)]
        elevations = [10.0, None, 12.0]
        result = MODULE.analyze_profile(points, elevations, grade_review=0.35, jump_review_m=4.0)
        self.assertEqual(result["nodata_sample_count"], 1)
        self.assertIn("nodata", result["flags"])
        self.assertIsNone(result["max_abs_grade"])
        self.assertEqual(result["flagged_segments"], [])


if __name__ == "__main__":
    unittest.main()
