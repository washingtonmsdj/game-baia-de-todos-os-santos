import bpy,runpy
from pathlib import Path
scene=bpy.context.scene;frame=scene.frame_current;scene.frame_set(31978)
try:runpy.run_path(str(Path(__file__).with_name('derive_lacerda_walkability_b77.py')),init_globals={'BOAS_ONLY_LOWER_ROUTE':True})
finally:scene.frame_set(frame)
