"""Descarta apenas as mutações incompletas deste script e retoma da revisão salva."""
import bpy,runpy,json
from pathlib import Path
root=Path(__file__).resolve().parents[2];c=json.loads((root/'world/areas/mvp-centro-lacerda/production.json').read_text())
if c['world_source']['revision']!='R30C.3':raise RuntimeError('Retomada exclusiva da R30C.3')
bpy.ops.wm.open_mainfile(filepath=str(root/c['world_source']['file']))
runpy.run_path(str(root/'automation/blender/urban_terrain_finish.py'),run_name='__main__')
