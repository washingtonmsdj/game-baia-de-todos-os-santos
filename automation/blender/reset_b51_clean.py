import bpy
from pathlib import Path
root=Path(__file__).resolve().parents[2]
target=root/"blender/salvador_lacerda_r30b51_gameplay_costeiro.blend"
assert target.exists()
bpy.ops.wm.open_mainfile(filepath=str(target))
print({"opened":str(target),"dirty":bpy.data.is_dirty})
