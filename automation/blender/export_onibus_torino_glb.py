import bpy
import sys
from pathlib import Path

root = next(p for p in Path(bpy.data.filepath).parents if (p / 'world/areas/mvp-centro-lacerda/production.json').exists())
sys.path.insert(0, str(root))
from tools.runtime.production import load_contract, require_source, resolve
contract = load_contract()
require_source(contract['vehicle']['source'], bpy.data.filepath)
scene = bpy.context.scene
assert scene.name == contract['vehicle']['source']['scene'], scene.name
output = resolve(contract['staging']['vehicle'])
output.parent.mkdir(parents=True, exist_ok=True)

bpy.ops.object.select_all(action='DESELECT')
selected = []
for obj in scene.objects:
    if any('APRESENTACAO' in c.name for c in obj.users_collection):
        continue
    if 'estudio' in obj.name.lower() or 'estúdio' in obj.name.lower():
        continue
    if obj.name.startswith('BUS02 | ') or obj.name.startswith('BUS03 | '):
        if obj.type in {'MESH', 'CURVE', 'FONT', 'EMPTY'}:
            obj.select_set(True)
            selected.append(obj)
if not selected:
    raise RuntimeError('Nenhum objeto do ônibus para exportar')
bpy.context.view_layer.objects.active = selected[0]
bpy.ops.export_scene.gltf(
    filepath=str(output),
    export_format='GLB',
    use_selection=True,
    export_apply=True,
    export_yup=True,
    export_materials='EXPORT',
    export_animations=True,
)
print(f'Exportado {output} com {len(selected)} objetos')
