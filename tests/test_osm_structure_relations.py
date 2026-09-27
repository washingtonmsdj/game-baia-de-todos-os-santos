import importlib.util
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "world" / "extract_osm_structure.py"
spec = importlib.util.spec_from_file_location("extract_osm_structure", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class MultipolygonStructureTests(unittest.TestCase):
    def test_stitches_two_outer_ways_into_building_relation(self):
        xml = """<osm version='0.6'>
        <node id='1' lat='-12.9700' lon='-38.5100'/>
        <node id='2' lat='-12.9700' lon='-38.5090'/>
        <node id='3' lat='-12.9690' lon='-38.5090'/>
        <node id='4' lat='-12.9690' lon='-38.5100'/>
        <way id='10'><nd ref='1'/><nd ref='2'/><nd ref='3'/></way>
        <way id='11'><nd ref='3'/><nd ref='4'/><nd ref='1'/></way>
        <relation id='100'>
          <member type='way' ref='10' role='outer'/>
          <member type='way' ref='11' role='outer'/>
          <tag k='type' v='multipolygon'/>
          <tag k='building' v='yes'/>
        </relation>
        </osm>"""
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "map.osm"
            path.write_text(xml, encoding="utf-8")
            nodes, ways, relations = module.parse_osm(path)
            features, diagnostics = module.build_relation_features(relations[0], ways, nodes)

        self.assertEqual(1, len(features))
        feature = features[0]
        self.assertEqual("relation", feature["osm_type"])
        self.assertEqual(100, feature["osm_id"])
        self.assertEqual("buildings", feature["layer"])
        self.assertTrue(feature["closed"])
        self.assertGreater(feature["metrics"]["area_m2_projected"], 0)
        self.assertEqual([10, 11], feature["member_way_ids"])
        self.assertEqual(1, diagnostics["outer_rings"])
        self.assertEqual(0, diagnostics["incomplete_outer_chains"])

    def test_missing_member_is_reported_not_invented(self):
        nodes = {"1": (-12.97, -38.51), "2": (-12.97, -38.50)}
        ways = {10: {"id": 10, "refs": ["1", "2"], "tags": {}}}
        relation = {
            "id": 200,
            "tags": {"type": "multipolygon", "natural": "water"},
            "members": [
                {"type": "way", "ref": 10, "role": "outer"},
                {"type": "way", "ref": 999, "role": "outer"},
            ],
        }
        features, diagnostics = module.build_relation_features(relation, ways, nodes)
        self.assertEqual([], features)
        self.assertEqual([999], diagnostics["missing_way_members"])
        self.assertEqual(1, diagnostics["incomplete_outer_chains"])

    def test_inner_ring_is_counted_without_becoming_standalone_feature(self):
        nodes = {
            "1": (-12.9700, -38.5100), "2": (-12.9700, -38.5080),
            "3": (-12.9680, -38.5080), "4": (-12.9680, -38.5100),
            "5": (-12.9695, -38.5095), "6": (-12.9695, -38.5085),
            "7": (-12.9685, -38.5085), "8": (-12.9685, -38.5095),
        }
        ways = {
            10: {"id": 10, "refs": ["1", "2", "3", "4", "1"], "tags": {}},
            11: {"id": 11, "refs": ["5", "6", "7", "8", "5"], "tags": {}},
        }
        relation = {
            "id": 300,
            "tags": {"type": "multipolygon", "natural": "water"},
            "members": [
                {"type": "way", "ref": 10, "role": "outer"},
                {"type": "way", "ref": 11, "role": "inner"},
            ],
        }
        features, diagnostics = module.build_relation_features(relation, ways, nodes)
        self.assertEqual(1, len(features))
        self.assertEqual(1, features[0]["relation_hole_count"])
        self.assertEqual(1, diagnostics["inner_rings"])


if __name__ == "__main__":
    unittest.main()
