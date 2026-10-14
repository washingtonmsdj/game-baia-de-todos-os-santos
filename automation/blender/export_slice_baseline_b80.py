import runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
runpy.run_path(str(ROOT/'automation/blender/export_slice_collision_b79.py'),init_globals={
    'REVISION_NAME':'salvador_lacerda_r30b79_contrato_colisao_slice.blend','OUTPUT_GEOMETRY_NAME':'geometry_b79.json'})
