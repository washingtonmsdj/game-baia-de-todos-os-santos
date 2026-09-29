"""Entrada canônica de exportação; executar pelo MCP na única janela Blender."""
import bpy
import runpy
import sys
from pathlib import Path

root = next(p for p in Path(bpy.data.filepath).parents if (p / 'world/areas/mvp-centro-lacerda/production.json').exists())
sys.path.insert(0, str(root))
from tools.runtime.production import load_contract, require_source

contract = load_contract()
require_source(contract['world_source'], bpy.data.filepath)
if bpy.data.is_dirty:
    raise RuntimeError('Cena tem alterações não salvas. Salve/promova uma revisão antes de exportar.')
for script in ('export_official_r30a11_full.py','export_runtime_surfaces.py'):
    runpy.run_path(str(root / 'automation/blender' / script), run_name='__main__')
print('Exportações concluídas. Próxima etapa: python tools/runtime/package_world.py')
