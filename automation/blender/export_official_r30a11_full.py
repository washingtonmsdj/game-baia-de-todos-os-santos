import bpy
import json
from pathlib import Path

scene = bpy.context.scene
excluded_prefixes = ('SOURCE_GEOREF |', 'LEGACY |', '32', '33', '34', '35', '37')
output = Path(r'C:/Users/TONECOS/Documents/github/game-baia-de-todos-os-santos/prototypes/threejs-water-lab/public/assets/city/salvador_lacerda_mvp_r30a11_full.glb')
output.parent.mkdir(parents=True, exist_ok=True)

bpy.ops.object.select_all(action='DESELECT')
selected = []
for obj in scene.objects:
    if obj.type not in {'MESH', 'CURVE', 'FONT'}:
        continue
    if obj.name.startswith(('BUS02 |', 'BUS03 |')):
        continue
    if not obj.visible_get():
        continue
    collection_names = [collection.name for collection in obj.users_collection]
    if any(name.startswith(excluded_prefixes) for name in collection_names):
        continue
    obj.select_set(True)
    selected.append(obj)

if not selected:
    raise RuntimeError('Nenhum objeto visual visível da cidade foi selecionado')
bpy.context.view_layer.objects.active = selected[0]
bpy.ops.export_scene.gltf(
    filepath=str(output),
    export_format='GLB',
    use_selection=True,
    export_apply=True,
    export_yup=True,
    export_materials='EXPORT',
    export_cameras=False,
    export_lights=False,
    export_animations=False,
)
summary = {'source_scene': scene.name, 'source_file': bpy.data.filepath, 'selected_objects': len(selected), 'output': str(output)}
Path(r'C:/Users/TONECOS/Documents/github/game-baia-de-todos-os-santos/artifacts/r30a11_full_export.json').write_text(json.dumps(summary, ensure_ascii=False), encoding='utf-8')
print(json.dumps(summary, ensure_ascii=False))
