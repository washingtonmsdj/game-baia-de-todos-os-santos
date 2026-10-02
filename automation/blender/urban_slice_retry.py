"""Reaplica a transação de modelagem ainda não salva após falha de material."""
import bpy,json,runpy
from pathlib import Path
root=Path(__file__).resolve().parents[2]
contract=json.loads((root/'world/areas/mvp-centro-lacerda/production.json').read_text())
assert contract['world_source']['revision']=='R30A.11', 'Não descartar revisão promovida'
bpy.ops.wm.open_mainfile(filepath=str(root/contract['world_source']['file']))
runpy.run_path(str(root/'automation/blender/urban_slice_apply.py'),run_name='__main__')
