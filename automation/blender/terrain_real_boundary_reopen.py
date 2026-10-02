"""Reabre somente a revisão candidata, em chamada separada da verificação."""
import bpy,json
from pathlib import Path
root=Path(__file__).resolve().parents[2]
r=json.loads((root/'docs/reports/blender/terrain_real_boundary_extension.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(root/r['candidate_file']))
