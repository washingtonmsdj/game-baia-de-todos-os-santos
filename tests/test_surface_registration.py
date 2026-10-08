import math
import unittest

from tools.terrain.surface_registration import evaluate_samples


class SurfaceRegistrationTests(unittest.TestCase):
    def test_b97_real_floor_hits_override_global_bbox_assumption(self):
        terrain_heights = [12.051285, 7.255676, 7.255661, 7.255661]
        previous = [12.051284790, 7.255668640, 7.255676269, 7.255668640]
        floor_hits = [11.113031, None, None, None]
        points = [
            {"world_xy": [i, i + 1], "terrain_world_z": terrain_z,
             "terrain_world_z_baseline": previous[i],
             "floor_world_z": floor_hits[i]}
            for i, terrain_z in enumerate(terrain_heights)
        ]
        report = evaluate_samples(points, 11.113008)
        self.assertEqual(4, report["alerts"])
        self.assertEqual(1, report["valid_pairs"])
        self.assertEqual(3, report["missing_floor_count"])
        self.assertEqual("TERRAIN_ABOVE_FLOOR", report["observations"][0]["state"])
        self.assertAlmostEqual(-0.938254, report["observations"][0]["height_delta_m"])
        for item in report["observations"][1:]:
            self.assertEqual("NO_FLOOR_HIT", item["state"])
            self.assertIsNone(item["height_delta_m"])
            self.assertFalse(item["floor_hit"])
        self.assertFalse(report["route_certified"])
        self.assertFalse(report["terrain_modified"])

    def test_absent_floor_does_not_fallback_to_reference_top(self):
        report = evaluate_samples(
            [{"world_xy": [1, 2], "floor_world_z": None, "terrain_world_z": 7.255661}],
            11.113008,
        )
        self.assertEqual("NO_FLOOR_HIT", report["observations"][0]["state"])
        self.assertIsNone(report["observations"][0]["height_delta_m"])
        self.assertEqual(0, report["valid_pairs"])

    def test_close_levels_without_certification(self):
        report = evaluate_samples(
            [{"world_xy": [2, 3], "floor_world_z": 9.2, "terrain_world_z": 9.1}],
            9.2,
        )
        self.assertEqual("LOCAL_LEVELS_ONLY_NOT_ROUTE_CERTIFIED", report["status"])
        self.assertFalse(report["route_certified"])

    def test_missing_terrain_hit_fails_closed(self):
        report = evaluate_samples(
            [{"world_xy": [1, 2], "floor_world_z": 3, "terrain_world_z": None}], 3
        )
        self.assertEqual("NO_TERRAIN_HIT", report["observations"][0]["state"])
        self.assertEqual("NEEDS_GEOMETRIC_AND_ROUTE_REVIEW", report["status"])

    def test_missing_both_surfaces_reports_no_delta(self):
        report = evaluate_samples(
            [{"world_xy": [1, 2], "floor_world_z": None, "terrain_world_z": None}], 3
        )
        self.assertEqual("NO_BOTH_SURFACES_HIT", report["observations"][0]["state"])
        self.assertIsNone(report["observations"][0]["height_delta_m"])

    def test_changed_baseline_does_not_hide_missing_floor(self):
        report = evaluate_samples(
            [{"world_xy": [2, 3], "floor_world_z": None, "terrain_world_z": 9,
              "terrain_world_z_baseline": 8.9}], 9
        )
        self.assertEqual("NO_FLOOR_HIT", report["observations"][0]["state"])
        self.assertTrue(report["observations"][0]["baseline_changed"])

    def test_changed_baseline_when_both_hit_is_explicit(self):
        report = evaluate_samples(
            [{"world_xy": [2, 3], "floor_world_z": 9, "terrain_world_z": 9,
              "terrain_world_z_baseline": 8.9}], 9
        )
        self.assertEqual("TERRAIN_CHANGED_SINCE_BASELINE", report["observations"][0]["state"])

    def test_invalid_inputs_do_not_silently_pass(self):
        bad = [[], [{"world_xy": [1], "floor_world_z": 5, "terrain_world_z": 5}],
               [{"world_xy": [2, 2], "floor_world_z": 5, "terrain_world_z": float("nan")}],
               [{"world_xy": [2, math.inf], "floor_world_z": 5, "terrain_world_z": 5}]]
        for case in bad:
            with self.subTest(case=case), self.assertRaises(ValueError):
                evaluate_samples(case, 5)
        with self.assertRaises(ValueError):
            evaluate_samples([{"world_xy": [1, 2], "terrain_world_z": 5}], 5,
                             step_limit_m=0)
        with self.assertRaises(ValueError):
            evaluate_samples([{"world_xy": [1, 2], "terrain_world_z": 5}], math.inf)


if __name__ == "__main__":
    unittest.main()
