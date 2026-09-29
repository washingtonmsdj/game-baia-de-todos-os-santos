import bpy
from pathlib import Path

scene = bpy.context.scene
patterns = (
    # Geometria hero já construída no arquivo oficial. A seleção deliberada
    # evita exportar árvores e o conjunto decorativo da Praça Cairu.
    'MERCADO MODELO',
    'FACHADA SUPERIOR',
    'PALÁCIO DO RIO BRANCO',
    'PREFEITURA',
    'ACESSO LACERDA',
)
output = Path(r'C:/Users/TONECOS/Documents/github/game-baia-de-todos-os-santos/prototypes/threejs-water-lab/public/assets/city/mvp_official_heroes.glb')
output.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action='DESELECT')
selected = []
for obj in scene.objects:
    if obj.type not in {'MESH', 'CURVE', 'FONT'}:
        continue
    if obj.name.startswith(('BUS02 |', 'BUS03 |')):
        continue
    name = obj.name.upper()
    if any(name.startswith(pattern.upper()) for pattern in patterns):
        # Alguns heróis estão em coleções de revisão ocultas no arquivo oficial.
        # Torná-los visíveis apenas durante a exportação preserva a geometria
        # existente e garante que o Three.js receba a cidade construída.
        obj.hide_set(False)
        obj.hide_viewport = False
        obj.hide_render = False
        for collection in obj.users_collection:
            collection.hide_viewport = False
            collection.hide_render = False
        obj.select_set(True)
        selected.append(obj)
if len(selected) < 10:
    raise RuntimeError(f'Poucos herois oficiais selecionados: {len(selected)}')
bpy.context.view_layer.objects.active = selected[0]
bpy.ops.export_scene.gltf(
    filepath=str(output), export_format='GLB', use_selection=True,
    export_apply=True, export_yup=True, export_materials='EXPORT',
    export_cameras=False, export_lights=False, export_animations=False,
)
print(f'Exportados {len(selected)} objetos oficiais para {output}')
