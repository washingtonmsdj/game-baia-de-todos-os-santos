from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("audit_osm_topology", ROOT / "tools/world/audit_osm_topology.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class OSMTopologyTests(unittest.TestCase):
    def test_near_miss_detects_distinct_close_endpoints(self):
        endpoints = [
            {"group": "transport", "layer": "roads", "osm_id": 1, "node_ref": 10, "endpoint": "end", "xy": (100.0, 100.0), "tags": {}},
            {"group": "transport", "layer": "roads", "osm_id": 2, "node_ref": 20, "endpoint": "start", "xy": (100.7, 100.0), "tags": {}},
        ]
        near, separated = MODULE.spatial_near_misses(endpoints, tolerance_m=1.5)
        self.assertEqual(len(near), 1)
        self.assertEqual(separated, [])
        self.assertAlmostEqual(near[0]["distance_m_projected"], 0.7)

    def test_grade_separation_is_not_regular_near_miss(self):
        endpoints = [
            {"group": "transport", "layer": "roads", "osm_id": 1, "node_ref": 10, "endpoint": "end", "xy": (0.0, 0.0), "tags": {"bridge": "yes", "layer": "1"}},
            {"group": "transport", "layer": "roads", "osm_id": 2, "node_ref": 20, "endpoint": "start", "xy": (0.5, 0.0), "tags": {}},
        ]
        near, separated = MODULE.spatial_near_misses(endpoints, tolerance_m=1.5)
        self.assertEqual(near, [])
        self.assertEqual(len(separated), 1)
        self.assertEqual(separated[0]["reason"], "possible_grade_separation")

    def test_boundary_detection(self):
        bounds = {"min_x": 0.0, "min_y": 0.0, "max_x": 100.0, "max_y": 100.0}
        self.assertTrue(MODULE.near_boundary((2.0, 50.0), bounds, 5.0))
        self.assertFalse(MODULE.near_boundary((50.0, 50.0), bounds, 5.0))

    def test_connected_components_by_shared_nodes(self):
        features = [
            {"osm_id": 1, "layer": "roads", "node_refs": [1, 2]},
            {"osm_id": 2, "layer": "roads", "node_refs": [2, 3]},
            {"osm_id": 3, "layer": "roads", "node_refs": [10, 11]},
        ]
        components = MODULE.connected_components(features, "transport")
        self.assertEqual(components[0], [1, 2])
        self.assertEqual(components[1], [3])


if __name__ == "__main__":
    unittest.main()
