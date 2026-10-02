"""Reabre a revisão atual na única instância visível do Blender."""
import bpy
from pathlib import Path
root=Path(__file__).resolve().parents[2]
path=root/'blender/salvador_lacerda_r30b13_encosta_ladeira_continua.blend'
assert path.exists()
bpy.ops.wm.open_mainfile(filepath=str(path))
