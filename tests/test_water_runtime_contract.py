import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / 'docs' / 'reports' / 'blender' / 'r30a8' / 'water_runtime_contract.json'
SCENE = ROOT / 'docs' / 'reports' / 'blender' / 'r30a8' / 'ocean_scene.json'


class WaterRuntimeContractTests(unittest.TestCase):
    def test_contract_keeps_visual_waves_separate_from_gameplay_collision(self):
        data = json.loads(CONTRACT.read_text(encoding='utf-8'))
        self.assertEqual(0.35, data['water_level_m'])
        self.assertTrue(data['gameplay']['swimmable'])
        self.assertTrue(data['gameplay']['diveable'])
        self.assertTrue(data['gameplay']['boats_supported'])
        self.assertTrue(data['gameplay']['runtime_surface_query_required'])
        self.assertTrue(data['gameplay']['visual_wave_displacement_must_not_be_used_as_collision_mesh'])
        self.assertEqual('engine_runtime', data['engine_contract']['wave_simulation'])
        self.assertEqual('engine_runtime', data['engine_contract']['buoyancy'])

    def test_ocean_scene_uses_water_mesh_boundary_for_shoreline(self):
        data = json.loads(SCENE.read_text(encoding='utf-8'))
        self.assertEqual('R30A.8', data['revision'])
        self.assertEqual('water_surface_boundary', data['shoreline_source'])
        self.assertEqual('water_runtime_contract.json', data['runtime_contract'])
        self.assertTrue(data['gameplay_surface_flat'])
        self.assertEqual(64, len(data['output_sha256']))


if __name__ == '__main__':
    unittest.main()
