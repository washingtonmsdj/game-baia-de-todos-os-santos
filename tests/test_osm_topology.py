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
    def endpoint(self, osm_id: int, node_ref: int, endpoint: str, xy, tags=None, osm_type="way"):
        return {
            "group": "transport",
            "layer": "roads",
            "osm_type": osm_type,
            "osm_id": osm_id,
            "osm_key": f"{osm_type}/{osm_id}",
            "node_ref": node_ref,
            "endpoint": endpoint,
            "xy": xy,
            "tags": tags or {},
        }

    def test_near_miss_detects_distinct_close_endpoints(self):
        endpoints = [
            self.endpoint(1, 10, "end", (100.0, 100.0)),
            self.endpoint(2, 20, "start", (100.7, 100.0)),
        ]
        near, separated = MODULE.spatial_near_misses(endpoints, tolerance_m=1.5)
        self.assertEqual(len(near), 1)
        self.assertEqual(separated, [])
        self.assertAlmostEqual(near[0]["distance_m_projected"], 0.7)
        self.assertEqual(near[0]["a"]["osm_key"], "way/1")
        self.assertEqual(near[0]["b"]["osm_key"], "way/2")

    def test_grade_separation_is_not_regular_near_miss(self):
        endpoints = [
            self.endpoint(1, 10, "end", (0.0, 0.0), {"bridge": "yes", "layer": "1"}),
            self.endpoint(2, 20, "start", (0.5, 0.0)),
        ]
        near, separated = MODULE.spatial_near_misses(endpoints, tolerance_m=1.5)
        self.assertEqual(near, [])
        self.assertEqual(len(separated), 1)
        self.assertEqual(separated[0]["reason"], "possible_grade_separation")

    def test_same_numeric_id_different_osm_type_does_not_collide(self):
        endpoints = [
            self.endpoint(123, 10, "end", (0.0, 0.0), osm_type="way"),
            self.endpoint(123, 20, "start", (0.5, 0.0), osm_type="relation"),
        ]
        near, separated = MODULE.spatial_near_misses(endpoints, tolerance_m=1.5)
        self.assertEqual(len(near), 1)
        self.assertEqual(separated, [])
        keys = {near[0]["a"]["osm_key"], near[0]["b"]["osm_key"]}
        self.assertEqual(keys, {"way/123", "relation/123"})

    def test_boundary_detection(self):
        bounds = {"min_x": 0.0, "min_y": 0.0, "max_x": 100.0, "max_y": 100.0}
        self.assertTrue(MODULE.near_boundary((2.0, 50.0), bounds, 5.0))
        self.assertFalse(MODULE.near_boundary((50.0, 50.0), bounds, 5.0))

    def test_connected_components_by_shared_nodes(self):
        features = [
            {"osm_type": "way", "osm_id": 1, "osm_key": "way/1", "layer": "roads", "node_refs": [1, 2]},
            {"osm_type": "way", "osm_id": 2, "osm_key": "way/2", "layer": "roads", "node_refs": [2, 3]},
            {"osm_type": "way", "osm_id": 3, "osm_key": "way/3", "layer": "roads", "node_refs": [10, 11]},
        ]
        components = MODULE.connected_components(features, "transport")
        self.assertEqual(components[0], ["way/1", "way/2"])
        self.assertEqual(components[1], ["way/3"])

    def test_connected_components_keep_way_and_relation_ids_distinct(self):
        features = [
            {"osm_type": "way", "osm_id": 123, "osm_key": "way/123", "layer": "roads", "node_refs": [1, 2]},
            {"osm_type": "relation", "osm_id": 123, "osm_key": "relation/123", "layer": "roads", "node_refs": [2, 3]},
        ]
        components = MODULE.connected_components(features, "transport")
        self.assertEqual(components, [["relation/123", "way/123"]])


if __name__ == "__main__":
    unittest.main()
