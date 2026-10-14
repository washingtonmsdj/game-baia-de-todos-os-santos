"""Deixa o conjunto dentro do mapa atual, sem isolamento local."""
import runpy
from pathlib import Path
root=Path(__file__).resolve().parents[2]
runpy.run_path(str(root/'automation/blender/present_lacerda_structure_b89.py'),init_globals={'BOAS_STRUCTURE_VIEW':'map'})
