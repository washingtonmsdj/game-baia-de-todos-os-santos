import unittest

from tools.world.build_nav_links import build_contract, crossing_link, step_endpoint_anchors


class NavLinksTests(unittest.TestCase):
    def setUp(self):
        self.nodes = {
            "100": {"id": "100", "blender_xy": [1.0, 2.0]},
            "101": {"id": "101", "blender_xy": [3.0, 4.0]},
        }

    def test_crossing_requires_exact_node_match(self):
        anchor = {
            "source_object": "crossing",
            "osm_node_id": "100",
            "nearest_nav_node_id": "101",
            "nearest_nav_node_distance_m": 1.0,
        }
        link = crossing_link(anchor, self.nodes, 2.5)
        self.assertEqual(link["status"], "blocked")
        self.assertFalse(link["exact_osm_node_match"])

    def test_crossing_requires_distance_threshold(self):
        anchor = {
            "source_object": "crossing",
            "osm_node_id": "100",
            "nearest_nav_node_id": "100",
            "nearest_nav_node_distance_m": 3.0,
        }
        link = crossing_link(anchor, self.nodes, 2.5)
        self.assertEqual(link["status"], "blocked")
        self.assertTrue(link["exact_osm_node_match"])

    def test_step_endpoints_preserve_osm_refs(self):
        graph = {
            "ways": [{
                "osm_way_id": 55,
                "kind": "steps",
                "name": "Escada",
                "node_refs": ["100", "101"],
                "incline": "down",
                "access": "candidate",
            }]
        }
        anchors = step_endpoint_anchors(graph, self.nodes)
        self.assertEqual([item["osm_node_id"] for item in anchors], ["100", "101"])
        self.assertEqual([item["endpoint_role"] for item in anchors], ["start", "end"])

    def test_contract_counts_reviewed_crossing(self):
        graph = {
            "fit_quality": "candidate",
            "nodes": list(self.nodes.values()),
            "ways": [],
        }
        scene = {"crossing_anchors": [{
            "source_object": "crossing",
            "osm_node_id": "100",
            "nearest_nav_node_id": "100",
            "nearest_nav_node_distance_m": 1.25,
        }]}
        contract = build_contract(graph, scene)
        self.assertEqual(contract["stats"]["approved_crossing_links"], 1)
        self.assertEqual(contract["crossing_links"][0]["status"], "reviewed_candidate")


if __name__ == "__main__":
    unittest.main()
