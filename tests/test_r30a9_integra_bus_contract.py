import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "automation" / "blender" / "r30a9_integrate_integra_bus.py"
ASSET_REPORT = ROOT / "docs" / "reports" / "blender" / "r30a9" / "source_asset.json"

EXPECTED_SHA256 = "F3D5DEE69DCAB15379817A9AE13E562DF8023FD7AF38E8B6A0CDB4742AB650A2"


class R30A9IntegraBusContractTests(unittest.TestCase):
    def test_script_preserves_r30a8_and_writes_r30a9(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("r30a8_ocean.blend", source)
        self.assertIn("r30a9_integra_bus.blend", source)
        self.assertIn("bpy.data.is_dirty", source)
        self.assertIn("OUTPUT_BLEND.exists()", source)
        self.assertIn("bpy.ops.wm.save_as_mainfile", source)

    def test_script_pins_the_uploaded_asset(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertIn(EXPECTED_SHA256, source)
        self.assertIn("BOAS_INTEGRA_BUS_GLB", source)
        self.assertIn("artifacts", source)
        self.assertIn("incoming", source)

    def test_runtime_status_is_explicitly_not_final(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("candidate_only", source)
        self.assertIn("authoring_only_needs_lod_and_vehicle_rig", source)
        self.assertIn("road_graph_centerline_staging", source)

    def test_source_report_matches_contract(self) -> None:
        report = json.loads(ASSET_REPORT.read_text(encoding="utf-8"))
        self.assertEqual(report["source_sha256"], EXPECTED_SHA256)
        self.assertEqual(report["inspection"]["geometry_count"], 67)
        self.assertEqual(report["inspection"]["triangles"], 1_954_141)
        self.assertEqual(report["authoring_assessment"]["classification"], "authoring_source_not_runtime_ready")


if __name__ == "__main__":
    unittest.main()
