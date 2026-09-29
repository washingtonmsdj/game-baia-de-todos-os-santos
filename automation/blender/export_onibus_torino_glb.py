import bpy
from pathlib import Path

scene = bpy.context.scene
assert scene.name == 'ONIBUS | Torino 31065 v03', scene.name
output = Path(r'C:/Users/TONECOS/Documents/github/game-baia-de-todos-os-santos/prototypes/threejs-water-lab/public/assets/vehicles/torino-31065/onibus_torino_31065_v03.glb')
output.parent.mkdir(parents=True, exist_ok=True)

bpy.ops.object.select_all(action='DESELECT')
selected = []
for obj in scene.objects:
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
