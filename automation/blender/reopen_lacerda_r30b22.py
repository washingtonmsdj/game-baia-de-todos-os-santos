"""Confere reabertura da candidata na unica janela visivel."""
import bpy
from pathlib import Path
path=Path(__file__).resolve().parents[2]/'blender/salvador_lacerda_r30b22_exterior_vidros.blend'
assert path.is_file()
def reopen():
 bpy.ops.wm.open_mainfile(filepath=str(path))
 return None
bpy.app.timers.register(reopen,first_interval=2.0)
