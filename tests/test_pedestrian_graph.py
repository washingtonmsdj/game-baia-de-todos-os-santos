import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.world.build_pedestrian_graph import (
    access_for,
    build_graph,
    traversal_for,
    inspect_candidate_route,
)


class PedestrianGraphTests(unittest.TestCase):
    def test_traversal_only_uses_oneway_foot(self):
        self.assertEqual(traversal_for({"oneway": "yes"}), "both")
        self.assertEqual(traversal_for({"oneway:foot": "yes"}), "forward")
        self.assertEqual(traversal_for({"oneway:foot": "-1"}), "reverse")

    def test_access_restrictions(self):
        self.assertEqual(access_for({"foot": "no"}), "restricted")
        self.assertEqual(access_for({"access": "private"}), "restricted")
        self.assertEqual(access_for({"foot": "yes"}), "candidate")

    def test_steps_are_kept_separate(self):
        graph = build_graph(
            {"features": [self._feature("steps", 7, [1, 2])]},
            self._fit(),
        )
        self.assertEqual(graph["stats"]["step_ways"], 1)
        self.assertEqual(graph["ways"][0]["kind"], "steps")


    def _sample_route_graph(self, tags=None):
        feature = self._feature("pedestrian", 88, [1, 2, 3])
        feature["tags"].update(tags or {})
        return build_graph({"features": [feature]}, self._fit())

    def test_shortest_route_is_only_candidate(self):
        result = inspect_candidate_route(self._sample_route_graph(), [0, 0], [2, 0])
        self.assertEqual(3, len(result["waypoint_ids"]))
        self.assertEqual(2, result["graph_path_length_m"])
        self.assertEqual("GRAPH_CANDIDATE_ONLY", result["status"])
        self.assertFalse(result["route_approved"])

    def test_gap_not_connected_by_snapping(self):
        result = inspect_candidate_route(self._sample_route_graph(), [0, 0], [8.7, 0],
                                         max_snap_distance_m=2)
        self.assertAlmostEqual(6.7, result["target_snap_gap_m"])
        self.assertEqual(2, result["graph_path_length_m"])
        self.assertEqual("UNVERIFIED_ENDPOINT_GAP", result["status"])
        self.assertTrue(result["unverified_endpoint_gap"])

    def test_restricted_edge_blocks_path(self):
        graph = self._sample_route_graph()
        graph["edges"][1]["access"] = "restricted"
        self.assertEqual("NO_OSM_GRAPH_PATH",
                         inspect_candidate_route(graph, [0, 0], [2, 0])["status"])

    def test_oneway_foot_direction_respected(self):
        graph = self._sample_route_graph({"oneway:foot": "yes"})
        self.assertFalse(inspect_candidate_route(graph, [2, 0], [0, 0])["osm_graph_path_exists"])
        self.assertTrue(inspect_candidate_route(graph, [0, 0], [2, 0])["osm_graph_path_exists"])

    def test_steps_require_explicit_opt_in(self):
        graph = build_graph({"features": [self._feature("steps", 88, [1, 2])]}, self._fit())
        self.assertFalse(inspect_candidate_route(graph, [0, 0], [1, 0])["osm_graph_path_exists"])
        self.assertTrue(inspect_candidate_route(graph, [0, 0], [1, 0],
                                                allow_steps=True)["osm_graph_path_exists"])

    def test_invalid_input_is_rejected(self):
        graph = self._sample_route_graph()
        for coords in ([float("nan"), 0], [True, 0], [0]):
            with self.subTest(coords=coords), self.assertRaises(ValueError):
                inspect_candidate_route(graph, coords, [1, 0])
        with self.assertRaises(ValueError):
            inspect_candidate_route(graph, [0, 0], [1, 0], max_snap_distance_m=0)
        with self.assertRaises(ValueError):
            inspect_candidate_route(dict(graph, schema="unknown"), [0, 0], [1, 0])
        graph["edges"][0]["to"] = "missing"
        with self.assertRaises(ValueError):
            inspect_candidate_route(graph, [0, 0], [1, 0])

    def test_real_r30a11_candidate_does_not_reach_market_door(self):
        import json
        root = Path(__file__).resolve().parents[1]
        graph = json.loads((root / "docs/reports/blender/r30a11/pedestrian_graph.json").read_text(encoding="utf-8"))
        result = inspect_candidate_route(graph, [-89.289593, 106.561385],
                                         [-126.491974, 154.290283])
        self.assertEqual(6, len(result["waypoint_ids"]))
        self.assertAlmostEqual(72.027, result["graph_path_length_m"], delta=0.05)
        self.assertAlmostEqual(6.712, result["target_snap_gap_m"], delta=0.05)
        self.assertEqual("UNVERIFIED_ENDPOINT_GAP", result["status"])
        self.assertFalse(result["route_approved"])

    @staticmethod
    def _feature(layer, osm_id, refs):
        return {
            "osm_id": osm_id,
            "layer": layer,
            "node_refs": refs,
            "epsg3857": [[float(i), 0.0] for i in range(len(refs))],
            "tags": {"highway": "steps" if layer == "steps" else "footway"},
        }

    @staticmethod
    def _fit():
        return {
            "quality": "candidate",
            "status": "candidate_only",
            "robust_fit": {
                "scale_blender_units_per_meter": 1.0,
                "rotation_epsg3857_to_blender_deg": 0.0,
                "translation_blender": [0.0, 0.0],
            },
        }


if __name__ == "__main__":
    unittest.main()
