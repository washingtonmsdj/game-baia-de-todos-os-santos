"""Abre a última revisão útil sem o corte inferior experimental."""
import bpy
from pathlib import Path
path=Path(__file__).resolve().parents[2]/'blender/salvador_lacerda_r30b16_apoio_encosta_suavizada.blend'
assert path.exists()
bpy.ops.wm.open_mainfile(filepath=str(path))
