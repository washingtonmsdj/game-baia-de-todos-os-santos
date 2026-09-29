import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.world.build_pedestrian_graph import (
    access_for,
    build_graph,
    traversal_for,
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
