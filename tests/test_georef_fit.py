import importlib.util
import math
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "georef" / "solve_osm_blender_fit.py"
SPEC = importlib.util.spec_from_file_location("solve_osm_blender_fit", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class GeorefFitTests(unittest.TestCase):
    def make_anchors(self, scale=1.003, rotation_deg=7.25, tx=210.0, ty=-87.5):
        theta = math.radians(rotation_deg)
        ac = scale * math.cos(theta)
        bs = scale * math.sin(theta)
        source = [
            (-4271234.0, -1459000.0),
            (-4271100.0, -1458950.0),
            (-4271000.0, -1459100.0),
            (-4270900.0, -1458800.0),
            (-4270800.0, -1459050.0),
            (-4270700.0, -1458900.0),
            (-4270600.0, -1458750.0),
            (-4270500.0, -1459150.0),
        ]
        anchors = []
        for index, (x, y) in enumerate(source, start=1):
            bx = ac * x - bs * y + tx
            by = bs * x + ac * y + ty
            anchors.append({
                "osm_id": index,
                "epsg3857": [x, y],
                "blender_xy": [bx, by],
                "object_names": [f"anchor-{index}"],
            })
        return anchors

    def test_exact_similarity_fit(self):
        anchors = self.make_anchors()
        result = MODULE.fit_similarity(anchors)
        self.assertAlmostEqual(result["scale_blender_units_per_meter"], 1.003, places=10)
        self.assertAlmostEqual(result["rotation_epsg3857_to_blender_deg"], 7.25, places=9)
        self.assertAlmostEqual(result["translation_blender"][0], 210.0, places=5)
        self.assertAlmostEqual(result["translation_blender"][1], -87.5, places=5)
        self.assertLess(result["rms_residual_blender_units"], 1e-7)

    def test_robust_fit_removes_outlier(self):
        anchors = self.make_anchors()
        anchors.append({
            "osm_id": 999,
            "epsg3857": [-4270400.0, -1458600.0],
            "blender_xy": [999999.0, -999999.0],
            "object_names": ["bad-anchor"],
        })
        result = MODULE.robust_fit(anchors, min_anchors=4, max_residual=8.0)
        removed = {item["osm_id"] for item in result["removed_outliers"]}
        self.assertIn(999, removed)
        self.assertAlmostEqual(result["scale_blender_units_per_meter"], 1.003, places=8)
        self.assertAlmostEqual(result["rotation_epsg3857_to_blender_deg"], 7.25, places=7)
        self.assertLess(result["rms_residual_blender_units"], 1e-5)


if __name__ == "__main__":
    unittest.main()
