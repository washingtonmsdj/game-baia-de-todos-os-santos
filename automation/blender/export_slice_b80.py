import runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
runpy.run_path(str(ROOT/'automation/blender/export_slice_collision_b79.py'),init_globals={
    'REVISION_NAME':'salvador_lacerda_r30b80_piso_e_embarque_superior.blend','OUTPUT_GEOMETRY_NAME':'geometry_b80.json',
    'QA_PATH':'docs/reports/blender/lacerda-controller-b80/walkability_candidate_b80.json'})
