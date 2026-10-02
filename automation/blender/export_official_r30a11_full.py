"""Exporta a arte visível da R30A.11 sem alterar ou salvar a cena-fonte."""
import bpy
import json
import hashlib
import sys
from pathlib import Path

source = Path(bpy.data.filepath)
root = source.parent.parent
sys.path.insert(0, str(root))
from tools.runtime.production import load_contract, require_source, resolve
contract = load_contract()
require_source(contract['world_source'], source)
scene = bpy.context.scene
if scene.name != contract['world_source']['scene']:
    raise RuntimeError('Cena ativa diferente da registrada')
output = resolve(contract['staging']['city'])
old_selection = list(bpy.context.selected_objects)
old_active = bpy.context.view_layer.objects.active
selected = []
# Coleções de arte da cena. Objetos compartilhados com GAMEPLAY continuam arte.
# Referências, nav hints e colisores dedicados não são geometria visual.
def artistic(collection):
    prefix = collection.name.split(' ', 1)[0]
    return prefix in contract['export']['visual_collection_ids']
try:
    bpy.ops.object.select_all(action='DESELECT')
    for obj in scene.objects:
        # Assets novos usam bibliotecas/instâncias, sem realizar cópias na cena.
        # Somente instâncias identificadas e nas coleções artísticas do contrato.
        asset_instance = (obj.type == 'EMPTY' and obj.instance_type == 'COLLECTION'
                          and obj.instance_collection is not None and obj.get('boas_asset_id'))
        if obj.type not in {'MESH', 'CURVE', 'FONT'} and not asset_instance:
            continue
        if not obj.visible_get() or obj.hide_render:
            continue
        if not any(artistic(c) and not c.hide_render and not c.hide_viewport for c in obj.users_collection):
            continue
        obj.select_set(True)
        selected.append(obj)
    if not selected:
        raise RuntimeError('Nenhuma geometria oficial selecionada')
    previous_manifest = output.with_suffix('.json')
    if previous_manifest.exists():
        previous = json.loads(previous_manifest.read_text(encoding='utf-8'))
        if previous.get('source_sha256') == contract['world_source']['sha256']:
            expected = set(previous['objects'])
            actual = {obj.name for obj in selected}
            if actual != expected:
                raise RuntimeError('Inventário visual mudou sem nova fonte: conferir visibilidade/view layer antes de exportar')
    bpy.context.view_layer.objects.active = selected[0]
    bpy.ops.export_scene.gltf(filepath=str(output), export_format='GLB', use_selection=True,
        export_apply=True, export_yup=True, export_materials='EXPORT',
        export_cameras=False, export_lights=False, export_animations=False, export_extras=True)
    manifest = {'source_file': 'blender/' + source.name,
        'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'source_scene': scene.name, 'objects': [o.name for o in selected],
        'export_sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
        'export_bytes': output.stat().st_size,
        'selection': 'Arte visível e renderizável das coleções declaradas no contrato, incluindo instâncias de assets; sem proxies de runtime'}
    output.with_suffix('.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k:v for k,v in manifest.items() if k != 'objects'}, ensure_ascii=False))
finally:
    bpy.ops.object.select_all(action='DESELECT')
    for obj in old_selection:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = old_active
