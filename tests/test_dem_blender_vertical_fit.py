from __future__ import annotations

import importlib.util
import math
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "fit_dem_blender_vertical",
    ROOT / "tools/terrain/fit_dem_blender_vertical.py",
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class DEMBlenderVerticalFitTests(unittest.TestCase):
    def test_inverse_xy_recovers_epsg_point(self):
        scale = 1.25
        theta = math.radians(30.0)
        tx, ty = 400.0, -200.0
        px, py = 1000.0, 2000.0
        c, s = math.cos(theta), math.sin(theta)
        bx = scale * (c * px - s * py) + tx
        by = scale * (s * px + c * py) + ty
        fit = {
            "scale_blender_units_per_meter": scale,
            "rotation_epsg3857_to_blender_deg": 30.0,
            "translation_blender": [tx, ty],
        }
        recovered = MODULE.inverse_xy((bx, by), fit)
        self.assertAlmostEqual(recovered[0], px, places=6)
        self.assertAlmostEqual(recovered[1], py, places=6)

    def test_fit_line_recovers_scale_and_offset(self):
        pairs = [(z, 1.5 * z + 7.0) for z in range(0, 100, 5)]
        result = MODULE.fit_line(pairs)
        self.assertAlmostEqual(result["scale_z_blender_units_per_dem_meter"], 1.5, places=9)
        self.assertAlmostEqual(result["z_offset_blender_units"], 7.0, places=9)
        self.assertAlmostEqual(result["rms_residual_blender_units"], 0.0, places=9)

    def test_robust_fit_removes_large_outlier(self):
        records = [
            {"dem_z_m": float(z), "blender_z": 1.0 * z + 10.0, "object_name": "terrain"}
            for z in range(60)
        ]
        records.append({"dem_z_m": 30.0, "blender_z": 1000.0, "object_name": "bad"})
        fit, kept, removed = MODULE.robust_vertical_fit(records, min_points=30, residual_floor=0.5, mad_multiplier=4.0)
        self.assertAlmostEqual(fit["scale_z_blender_units_per_dem_meter"], 1.0, places=6)
        self.assertAlmostEqual(fit["z_offset_blender_units"], 10.0, places=6)
        self.assertGreaterEqual(len(removed), 1)
        self.assertEqual(len(kept), 60)

    def test_quality_checks_vertical_horizontal_scale_consistency(self):
        fit = {"scale_z_blender_units_per_dem_meter": 1.0, "rms_residual_blender_units": 0.2}
        self.assertEqual(MODULE.quality(fit, 300, 1.0), "strong_candidate")
        self.assertEqual(MODULE.quality(fit, 300, 3.0), "insufficient")


if __name__ == "__main__":
    unittest.main()
