from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("extract_osm_structure", ROOT / "tools/world/extract_osm_structure.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


OSM_MULTIPOLYGON = """<?xml version='1.0' encoding='UTF-8'?>
<osm version='0.6'>
  <node id='1' lat='-12.9700' lon='-38.5100'/>
  <node id='2' lat='-12.9700' lon='-38.5098'/>
  <node id='3' lat='-12.9698' lon='-38.5098'/>
  <node id='4' lat='-12.9698' lon='-38.5100'/>
  <node id='5' lat='-12.96995' lon='-38.50995'/>
  <node id='6' lat='-12.96995' lon='-38.50985'/>
  <node id='7' lat='-12.96985' lon='-38.50985'/>
  <node id='8' lat='-12.96985' lon='-38.50995'/>

  <way id='200'>
    <nd ref='1'/><nd ref='2'/><nd ref='3'/>
    <tag k='building' v='yes'/>
  </way>
  <way id='201'>
    <nd ref='3'/><nd ref='4'/><nd ref='1'/>
  </way>
  <way id='202'>
    <nd ref='5'/><nd ref='6'/><nd ref='7'/><nd ref='8'/><nd ref='5'/>
  </way>

  <relation id='900'>
    <member type='way' ref='200' role='outer'/>
    <member type='way' ref='201' role='outer'/>
    <member type='way' ref='202' role='inner'/>
    <tag k='type' v='multipolygon'/>
    <tag k='building' v='yes'/>
    <tag k='name' v='Edificio Teste'/>
  </relation>
</osm>
"""


class OSMMultipolygonTests(unittest.TestCase):
    def parse_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "map.osm"
            path.write_text(OSM_MULTIPOLYGON, encoding="utf-8")
            return MODULE.parse_osm_document(path)

    def test_builds_outer_and_inner_rings(self):
        nodes, raw_ways, relations = self.parse_fixture()
        features = MODULE.build_relation_features(relations[0], raw_ways, nodes)
        self.assertEqual(len(features), 2)
        outer = next(item for item in features if item["relation_role"] == "outer")
        inner = next(item for item in features if item["relation_role"] == "inner")

        self.assertEqual(outer["osm_type"], "relation")
        self.assertEqual(outer["osm_key"], "relation/900")
        self.assertEqual(outer["layer"], "buildings")
        self.assertTrue(outer["closed"])
        self.assertEqual(set(outer["member_way_ids"]), {200, 201})
        self.assertEqual(outer["node_refs"][0], outer["node_refs"][-1])
        self.assertGreater(outer["metrics"]["area_m2_projected"], 0)

        self.assertTrue(inner["closed"])
        self.assertEqual(inner["member_way_ids"], [202])
        self.assertGreater(inner["metrics"]["area_m2_projected"], 0)

    def test_closed_relation_suppresses_same_layer_member_way(self):
        nodes, raw_ways, relations = self.parse_fixture()
        features, covered = MODULE.relation_features_and_covered_ways(relations, raw_ways, nodes)
        self.assertEqual(len(features), 2)
        self.assertIn("buildings", covered[200])
        self.assertIn("buildings", covered[201])
        self.assertIn("buildings", covered[202])

    def test_missing_member_is_reported_without_inventing_geometry(self):
        nodes, raw_ways, relations = self.parse_fixture()
        relation = dict(relations[0])
        relation["members"] = list(relation["members"]) + [{"type": "way", "ref": 999, "role": "outer"}]
        features = MODULE.build_relation_features(relation, raw_ways, nodes)
        outer = next(item for item in features if item["relation_role"] == "outer")
        self.assertEqual(outer["missing_member_way_count"], 1)
        self.assertEqual(outer["missing_member_way_ids"], [999])

    def test_assemble_member_rings_reverses_way_when_needed(self):
        raw = {
            1: {"refs": ["1", "2", "3"]},
            2: {"refs": ["1", "4", "3"]},
        }
        rings, missing = MODULE.assemble_member_rings([1, 2], raw)
        self.assertEqual(missing, [])
        self.assertEqual(len(rings), 1)
        self.assertTrue(rings[0]["closed"])
        self.assertEqual(rings[0]["refs"][0], rings[0]["refs"][-1])


if __name__ == "__main__":
    unittest.main()
