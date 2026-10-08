import math
import unittest

from tools.terrain.surface_registration import evaluate_samples


class SurfaceRegistrationTests(unittest.TestCase):
    def test_b97_documented_heights_block_route_approval(self):
        heights = [12.051285, 7.255676, 7.255661, 7.255661]
        previous = [12.051284790, 7.255668640, 7.255676269, 7.255668640]
        points = [{"world_xy": [i, i + 1], "terrain_world_z": z,
                   "terrain_world_z_baseline": old}
                  for i, (z, old) in enumerate(zip(heights, previous))]
        report = evaluate_samples(points, 11.113008)
        self.assertEqual(4, report["alerts"])
        self.assertEqual("TERRAIN_ABOVE_FLOOR", report["observations"][0]["state"])
        self.assertEqual("FLOOR_ABOVE_TERRAIN", report["observations"][1]["state"])
        self.assertAlmostEqual(3.857332, report["observations"][1]["height_delta_m"])
        self.assertFalse(report["route_certified"])
        self.assertFalse(report["terrain_modified"])

    def test_near_level_never_implies_route_certification(self):
        r = evaluate_samples([{"world_xy": [2, 3], "terrain_world_z": 9.1}], 9.2)
        self.assertEqual("LOCAL_LEVELS_ONLY_NOT_ROUTE_CERTIFIED", r["status"])
        self.assertFalse(r["route_certified"])

    def test_missing_terrain_hit_fails_closed(self):
        r = evaluate_samples([{"world_xy": [1, 2], "terrain_world_z": None}], 3)
        self.assertEqual("NO_TERRAIN_HIT", r["observations"][0]["state"])
        self.assertEqual("NEEDS_GEOMETRIC_AND_ROUTE_REVIEW", r["status"])

    def test_changed_baseline_must_not_be_ignored(self):
        r = evaluate_samples([{"world_xy": [2, 3], "terrain_world_z": 9.0,
                               "terrain_world_z_baseline": 8.9}], 9.0)
        self.assertEqual("TERRAIN_CHANGED_SINCE_BASELINE", r["observations"][0]["state"])

    def test_invalid_inputs_do_not_silently_pass(self):
        bad = [[], [{"world_xy": [1], "terrain_world_z": 5}],
               [{"world_xy": [2, 2], "terrain_world_z": float("nan")}]]
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
