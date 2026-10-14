import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name('derive_lacerda_walkability_b77.py')),init_globals={'BOAS_ONLY_PORTAL_PROBE':True})
