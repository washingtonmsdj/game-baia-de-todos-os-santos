from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "compare_scene_reference_alignment",
    ROOT / "tools/world/compare_scene_reference_alignment.py",
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class SceneReferenceAlignmentTests(unittest.TestCase):
    def test_reference_schema_v2_is_supported(self):
        self.assertIn("bay-of-all-saints/blender-structure-reference-v2", MODULE.SUPPORTED_REFERENCE_SCHEMAS)

    def test_bounds_and_offset_in_meters(self):
        scene_group = {
            "bounds": {"min": [0.0, 0.0], "max": [10.0, 10.0], "center": [5.0, 5.0], "size": [10.0, 10.0]}
        }
        ref_group = {
            "bounds": {"min": [2.0, 0.0], "max": [12.0, 10.0], "center": [7.0, 5.0], "size": [10.0, 10.0]}
        }
        result = MODULE.compare(scene_group, ref_group, meters_per_unit=1.0, offset_review_m=1.0, size_review_ratio=0.25)
        self.assertAlmostEqual(result["center_offset_m"], 2.0)
        self.assertIn("center_offset_review", result["flags"])
        self.assertNotIn("bounds_size_review", result["flags"])

    def test_size_delta_is_review_only(self):
        scene_group = {
            "bounds": {"min": [0.0, 0.0], "max": [20.0, 10.0], "center": [10.0, 5.0], "size": [20.0, 10.0]}
        }
        ref_group = {
            "bounds": {"min": [5.0, 0.0], "max": [15.0, 10.0], "center": [10.0, 5.0], "size": [10.0, 10.0]}
        }
        result = MODULE.compare(scene_group, ref_group, meters_per_unit=1.0, offset_review_m=3.0, size_review_ratio=0.25)
        self.assertEqual(result["center_offset_m"], 0.0)
        self.assertIn("bounds_size_review", result["flags"])
        self.assertAlmostEqual(result["max_abs_bounds_size_delta_ratio"], 1.0)

    def test_aggregate_scene_unions_multiple_objects_same_osm(self):
        scene = {
            "objects": [
                {"name": "a", "osm_ids": [123], "categories": ["buildings"], "bounds": {"min": [0, 0, 0], "max": [5, 5, 5]}},
                {"name": "b", "osm_ids": [123], "categories": ["buildings"], "bounds": {"min": [5, 0, 0], "max": [10, 5, 5]}},
            ]
        }
        result = MODULE.aggregate_scene_by_osm(scene)[123]
        self.assertEqual(result["bounds"]["min"], [0.0, 0.0])
        self.assertEqual(result["bounds"]["max"], [10.0, 5.0])
        self.assertEqual(result["bounds"]["center"], [5.0, 2.5])

    def test_reference_bounds_from_geometry(self):
        reference = {
            "features": [
                {"osm_id": 321, "layer": "buildings", "blender_xy": [[2, 3], [8, 3], [8, 9], [2, 9], [2, 3]]}
            ]
        }
        result = MODULE.aggregate_reference_by_osm(reference)[321]
        self.assertEqual(result["bounds"]["center"], [5.0, 6.0])
        self.assertEqual(result["bounds"]["size"], [6.0, 6.0])

    def test_individual_candidates_prioritize_semantic_building(self):
        scene_group = {
            "objects": [
                {
                    "name": "Mercado footprint",
                    "categories": ["buildings"],
                    "bounds": {"min": [0, 0, 0], "max": [10, 10, 5]},
                },
                {
                    "name": "terreno colisao",
                    "categories": ["terrain"],
                    "bounds": {"min": [-500, -500, 0], "max": [500, 500, 5]},
                },
            ],
            "bounds": {"min": [-500, -500], "max": [500, 500], "center": [0, 0], "size": [1000, 1000]},
            "categories": ["buildings", "terrain"],
        }
        ref_group = {
            "layers": ["buildings"],
            "bounds": {"min": [0, 0], "max": [10, 10], "center": [5, 5], "size": [10, 10]},
        }
        candidates = MODULE.compare_individual_objects(scene_group, ref_group, 1.0, 3.0, 0.25)
        self.assertEqual(candidates[0]["object_name"], "Mercado footprint")
        self.assertTrue(candidates[0]["semantic_match"])
        self.assertFalse(candidates[1]["semantic_match"])

    def test_binding_conflict_when_wrong_object_contaminates_aggregate(self):
        aggregate = {
            "center_offset_m": 250.0,
            "center_offset_blender_units": 250.0,
            "flags": ["center_offset_review"],
        }
        candidates = [
            {"object_name": "Mercado footprint", "semantic_match": True, "center_offset_m": 1.0, "center_offset_blender_units": 1.0},
            {"object_name": "terreno colisao", "semantic_match": False, "center_offset_m": 240.0, "center_offset_blender_units": 240.0},
        ]
        conflict, reasons = MODULE.binding_conflict(aggregate, candidates, 3.0)
        self.assertTrue(conflict)
        self.assertGreaterEqual(len(reasons), 2)


if __name__ == "__main__":
    unittest.main()
