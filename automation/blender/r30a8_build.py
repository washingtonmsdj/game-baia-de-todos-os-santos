import hashlib
import json
import runpy
from pathlib import Path
import bpy

ROOT = Path(__file__).resolve().parents[2]
STEPS = [
    ROOT / 'automation' / 'blender' / 'r30a8_ocean_system.py',
    ROOT / 'automation' / 'blender' / 'r30a8_shoreline_from_water.py',
    ROOT / 'automation' / 'blender' / 'r30a8_gameplay_water_metadata.py',
]

for step in STEPS:
    print('R30A8 STEP', step.name)
    runpy.run_path(str(step), run_name='__main__')

blend = Path(bpy.data.filepath)
digest = hashlib.sha256()
with blend.open('rb') as handle:
    for chunk in iter(lambda: handle.read(1024 * 1024), b''):
        digest.update(chunk)

report_path = ROOT / 'docs' / 'reports' / 'blender' / 'r30a8' / 'ocean_scene.json'
report = json.loads(report_path.read_text(encoding='utf-8'))
report['output_sha256'] = digest.hexdigest().upper()
report['shoreline_source'] = 'water_surface_boundary'
report['runtime_contract'] = 'water_runtime_contract.json'
report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')

print({'revision': 'R30A.8', 'blend': str(blend), 'sha256': report['output_sha256']})
