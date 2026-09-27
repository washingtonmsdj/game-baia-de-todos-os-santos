from __future__ import annotations

import importlib.util
import math
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "build_blender_structure_reference",
    ROOT / "tools/world/build_blender_structure_reference.py",
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class BlenderStructureReferenceTests(unittest.TestCase):
    def test_transform_matches_similarity_model(self):
        fit = {
            "scale_blender_units_per_meter": 2.0,
            "rotation_epsg3857_to_blender_deg": 90.0,
            "translation_blender": [10.0, -5.0],
        }
        result = MODULE.transform_point([3.0, 4.0], fit)
        self.assertAlmostEqual(result[0], 2.0, places=6)
        self.assertAlmostEqual(result[1], 1.0, places=6)

    def test_zero_rotation(self):
        fit = {
            "scale_blender_units_per_meter": 1.0,
            "rotation_epsg3857_to_blender_deg": 0.0,
            "translation_blender": [100.0, 200.0],
        }
        result = MODULE.transform_point([5.0, 7.0], fit)
        self.assertEqual(result, [105.0, 207.0])


if __name__ == "__main__":
    unittest.main()
