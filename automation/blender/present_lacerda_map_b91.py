import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name('present_lacerda_structure_b91.py')),init_globals={'BOAS_STRUCTURE_VIEW':'map'})
