"""Enquadramento de planta, sem mudar cena ou geometria."""
import runpy
from pathlib import Path
root=Path(__file__).resolve().parents[2]
runpy.run_path(str(root/'automation/blender/present_lacerda_structure_b89.py'),init_globals={'BOAS_STRUCTURE_VIEW':'plan'})
