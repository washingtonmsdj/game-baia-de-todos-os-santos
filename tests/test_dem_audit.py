from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("audit_dem", ROOT / "tools/terrain/audit_dem.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class DEMAuditTests(unittest.TestCase):
    def test_parse_gdalinfo_json(self):
        payload = {
            "driverShortName": "GTiff",
            "size": [1024, 512],
            "geoTransform": [100.0, 2.0, 0.0, 200.0, 0.0, -2.0],
            "cornerCoordinates": {
                "lowerLeft": [100.0, -824.0],
                "upperRight": [2148.0, 200.0],
            },
            "coordinateSystem": {"wkt": "PROJCRS[\"WGS 84 / Pseudo-Mercator\",ID[\"EPSG\",3857]]"},
            "bands": [{"type": "Float32", "noDataValue": -9999.0}],
        }
        result = MODULE.parse_gdalinfo_json(payload)
        self.assertEqual(result["driver"], "GTiff")
        self.assertEqual(result["width"], 1024)
        self.assertEqual(result["height"], 512)
        self.assertEqual(result["pixel_size"], {"x": 2.0, "y": 2.0})
        self.assertEqual(result["nodata"], [-9999.0])
        self.assertIn("3857", result["crs"])


if __name__ == "__main__":
    unittest.main()
