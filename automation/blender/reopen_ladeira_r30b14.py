"""Reabre a revisão R30B.14 na única instância visível do Blender."""
import bpy
from pathlib import Path
path=Path(__file__).resolve().parents[2]/'blender/salvador_lacerda_r30b14_apoio_encosta_ladeira.blend'
assert path.exists()
bpy.ops.wm.open_mainfile(filepath=str(path))
