from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "analyze_vertical_domains",
    ROOT / "tools/terrain/analyze_vertical_domains.py",
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class VerticalDomainsTests(unittest.TestCase):
    def test_split_domains_keeps_bathymetry_separate(self):
        records = [
            {"dem_z_m": -877.0},
            {"dem_z_m": -0.1},
            {"dem_z_m": 0.0},
            {"dem_z_m": 12.0},
        ]
        below, land = MODULE.split_domains(records, 0.0)
        self.assertEqual([row["dem_z_m"] for row in below], [-877.0, -0.1])
        self.assertEqual([row["dem_z_m"] for row in land], [0.0, 12.0])

    def test_spatial_grid_flags_only_cells_above_review_threshold(self):
        fit = {
            "scale_z_blender_units_per_dem_meter": 1.0,
            "z_offset_blender_units": 0.0,
        }
        records = [
            {"epsg3857_xy": [10.0, 10.0], "dem_z_m": 10.0, "blender_z": 10.5},
            {"epsg3857_xy": [20.0, 20.0], "dem_z_m": 11.0, "blender_z": 11.2},
            {"epsg3857_xy": [110.0, 10.0], "dem_z_m": 10.0, "blender_z": 20.0},
            {"epsg3857_xy": [120.0, 20.0], "dem_z_m": 11.0, "blender_z": 21.0},
        ]
        cells, review = MODULE.spatial_grid(
            records,
            fit,
            grid_size_m=100.0,
            review_median_abs_residual=5.0,
            min_cell_samples=2,
        )
        self.assertEqual(len(cells), 2)
        self.assertEqual(len(review), 1)
        self.assertEqual(review[0]["grid_index"], [1, 0])
        self.assertGreaterEqual(review[0]["residual_median_abs"], 5.0)

    def test_fit_records_recovers_simple_land_fit(self):
        records = []
        for index in range(60):
            dem = float(index)
            records.append({"dem_z_m": dem, "blender_z": dem + 2.0})
        result = MODULE.fit_records(
            records,
            horizontal_scale=1.0,
            min_points=50,
            residual_floor=0.75,
            mad_multiplier=4.0,
        )
        self.assertIn(result["quality"], {"candidate", "strong_candidate"})
        self.assertAlmostEqual(result["fit"]["scale_z_blender_units_per_dem_meter"], 1.0, places=6)
        self.assertAlmostEqual(result["fit"]["z_offset_blender_units"], 2.0, places=6)


if __name__ == "__main__":
    unittest.main()
