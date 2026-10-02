import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name('review_tower_galleries_r35.py')),init_globals={'SUPPORT_ONLY':True})
