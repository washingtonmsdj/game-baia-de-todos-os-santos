import runpy
from pathlib import Path
p=Path(__file__).parent
runpy.run_path(str(p/'inspect_context_r35.py'))
runpy.run_path(str(p/'review_city_context_r35.py'))
