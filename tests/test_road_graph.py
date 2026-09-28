import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.world.build_road_graph import build_graph, direction_for, transform_point


class RoadGraphTests(unittest.TestCase):
    def test_transform_point_identity(self):
        fit = {
            "scale_blender_units_per_meter": 1.0,
            "rotation_epsg3857_to_blender_deg": 0.0,
            "translation_blender": [10.0, -5.0],
        }
        self.assertEqual(transform_point([2.0, 3.0], fit), [12.0, -2.0])

    def test_direction_rules(self):
        self.assertEqual(direction_for({"oneway": "yes"}), "forward")
        self.assertEqual(direction_for({"oneway": "-1"}), "reverse")
        self.assertEqual(direction_for({"junction": "roundabout"}), "forward")
        self.assertEqual(direction_for({"oneway": "no", "junction": "roundabout"}), "both")

    def test_shared_node_becomes_junction_candidate(self):
        structure = {
            "features": [
                self._road(1, [10, 11], [[0, 0], [1, 0]]),
                self._road(2, [11, 12], [[1, 0], [2, 0]]),
            ]
        }
        fit_report = {
            "quality": "candidate",
            "status": "candidate_only",
            "robust_fit": {
                "scale_blender_units_per_meter": 1.0,
                "rotation_epsg3857_to_blender_deg": 0.0,
                "translation_blender": [0.0, 0.0],
            },
        }
        graph = build_graph(structure, fit_report)
        node = next(item for item in graph["nodes"] if item["id"] == "11")
        self.assertTrue(node["junction_candidate"])
        self.assertEqual(node["way_ids"], [1, 2])

    @staticmethod
    def _road(osm_id, refs, coords):
        return {
            "osm_type": "way",
            "osm_id": osm_id,
            "layer": "roads",
            "node_refs": refs,
            "epsg3857": coords,
            "metrics": {"lanes_tagged": None, "width_m_tagged": None},
            "tags": {"highway": "residential"},
        }


if __name__ == "__main__":
    unittest.main()

