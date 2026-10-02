import runpy
from pathlib import Path
folder=Path(__file__).parent
runpy.run_path(str(folder/'inspect_gallery_proxy_r35.py'))
import json
audit=json.loads((folder.parents[1]/'artifacts/palacio-rio-branco/gallery_proxy_occupation_r35.json').read_text(encoding='utf8'))
assert all(not row['occupied'] for row in audit),'Solo/proxy ainda ocupa galerias'
runpy.run_path(str(folder/'present_tower_galleries_r35.py'))
runpy.run_path(str(folder/'review_support_only_r35.py'))
