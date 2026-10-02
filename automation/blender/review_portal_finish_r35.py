import runpy
from pathlib import Path
root=Path(__file__).resolve().parents[2]
runpy.run_path(str(root/'automation/blender/review_facade_context_r35.py'),init_globals={'BOAS_REVIEW_NAMES':['frente']})
runpy.run_path(str(root/'automation/blender/inspect_gallery_proxy_r35.py'))
