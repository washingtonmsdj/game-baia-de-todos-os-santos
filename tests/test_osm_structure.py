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


OSM_FIXTURE = """<?xml version='1.0' encoding='UTF-8'?>
<osm version='0.6'>
  <node id='1' lat='-12.9700' lon='-38.5100'/>
  <node id='2' lat='-12.9700' lon='-38.5099'/>
  <node id='3' lat='-12.9699' lon='-38.5099'/>
  <node id='4' lat='-12.9699' lon='-38.5100'/>
  <node id='5' lat='-12.9701' lon='-38.5100'/>
  <way id='100'>
    <nd ref='1'/><nd ref='2'/><nd ref='3'/><nd ref='4'/><nd ref='1'/>
    <tag k='building' v='yes'/>
  </way>
  <way id='101'>
    <nd ref='5'/><nd ref='1'/><nd ref='2'/>
    <tag k='highway' v='primary'/><tag k='lanes' v='2'/><tag k='width' v='7.5'/>
  </way>
  <way id='102'>
    <nd ref='1'/><nd ref='4'/>
    <tag k='natural' v='coastline'/>
  </way>
  <way id='103'>
    <nd ref='2'/><nd ref='3'/>
    <tag k='man_made' v='pier'/>
  </way>
</osm>
"""


class OSMStructureTests(unittest.TestCase):
    def test_classifies_core_structural_layers(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "map.osm"
            path.write_text(OSM_FIXTURE, encoding="utf-8")
            nodes, ways = MODULE.parse_osm(path)
            features = [MODULE.build_feature(way, nodes) for way in ways]
            features = [feature for feature in features if feature]
            by_id = {item["osm_id"]: item for item in features}

            self.assertEqual(by_id[100]["layer"], "buildings")
            self.assertTrue(by_id[100]["closed"])
            self.assertGreater(by_id[100]["metrics"]["area_m2_projected"], 0)
            self.assertEqual(by_id[101]["layer"], "roads")
            self.assertEqual(by_id[101]["metrics"]["lanes_tagged"], 2)
            self.assertAlmostEqual(by_id[101]["metrics"]["width_m_tagged"], 7.5)
            self.assertEqual(by_id[102]["layer"], "coastline")
            self.assertEqual(by_id[103]["layer"], "waterfront")

    def test_does_not_invent_road_width(self):
        feature = MODULE.build_feature(
            {"id": 200, "refs": ["1", "2"], "tags": {"highway": "residential"}, "layer": "roads"},
            {"1": (-12.97, -38.51), "2": (-12.97, -38.5099)},
        )
        self.assertIsNone(feature["metrics"]["width_m_tagged"])
        self.assertIsNone(feature["metrics"]["lanes_tagged"])


if __name__ == "__main__":
    unittest.main()
