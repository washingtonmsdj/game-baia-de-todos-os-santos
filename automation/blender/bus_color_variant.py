"""Motor de variantes de pintura; executado somente pelos wrappers via MCP."""
import bpy, hashlib, json
from pathlib import Path

repo = Path(__file__).resolve().parents[2]
catalog_path = repo / 'world/vehicles/catalog.json'
catalog = json.loads(catalog_path.read_text(encoding='utf-8'))
vehicle = catalog['vehicles'][0]
base = vehicle['authoring_base']
variant = next(v for v in vehicle['variants'] if v['color'] == color)
source = repo / base['file']
target = repo / variant['file']
if Path(bpy.data.filepath).resolve() != source.resolve():
    assert not bpy.data.is_dirty, 'Preservar alterações abertas antes de mudar de fonte.'
    bpy.ops.wm.open_mainfile(filepath=str(source))
assert Path(bpy.data.filepath).resolve() == source.resolve()
assert hashlib.sha256(source.read_bytes()).hexdigest() == base['sha256']
assert bpy.context.scene.name == base['scene']
assert not target.exists(), 'Não sobrescrever variante existente.'
scene = bpy.context.scene
root = bpy.data.objects['TOR04_ROOT']

def fingerprint():
    h = hashlib.sha256()
    for o in sorted(scene.objects, key=lambda o: o.name):
        h.update(str((o.name, o.type, o.parent.name if o.parent else None,
                      tuple(o.location), tuple(o.rotation_euler), tuple(o.scale))).encode())
        if o.type == 'MESH':
            h.update(str([tuple(v.co) for v in o.data.vertices]).encode())
            h.update(str([(tuple(p.vertices), p.material_index) for p in o.data.polygons]).encode())
        if o.type == 'FONT':
            h.update(o.data.body.encode())
        if o.animation_data:
            h.update(str(o.animation_data.action).encode())
    return h.hexdigest()

before = fingerprint()
yellow = bpy.data.materials['TOR04 | Amarelo ouro']
green = yellow.copy()
green.name = 'TORINO '+color.upper()+' | Pintura externa'
paint_hex = {'verde': '#12941A', 'azul': '#16568F'}[color]
srgb = tuple(int(paint_hex[i:i+2],16)/255 for i in (1,3,5))
linear = tuple(c/12.92 if c <= .04045 else ((c+.055)/1.055)**2.4 for c in srgb)
green.diffuse_color = (*linear, 1)
for n in green.node_tree.nodes:
    if n.type == 'BSDF_PRINCIPLED':
        n.inputs['Base Color'].default_value = (*linear, 1)
green['boas_variant_id'] = variant['variant_id']
green['color_status'] = 'Aproximação visual sRGB '+paint_hex+', não cor medida de fábrica.'
white = bpy.data.materials['TOR04 | Branco sinalização']
changed = []
preserved_yellow = []
external = {'TOR04 | CARROCERIA', 'TOR04 | PARACHOQUES', 'TOR04 | ACABAMENTOS'}
for o in scene.objects:
    if not hasattr(o.data, 'materials'):
        continue
    eligible = bool(external.intersection(c.name for c in o.users_collection))
    # As bandas da faixa verde/amarela/azul continuam sendo as mesmas três cores.
    eligible = eligible and not o.name.startswith('TOR04 | Faixa pintura curva')
    for slot in o.material_slots:
        if slot.material == yellow:
            if eligible:
                slot.link = 'OBJECT'
                slot.material = green
                changed.append(o.name)
            else:
                preserved_yellow.append(o.name)
        elif eligible and o.type == 'FONT' and o.name.startswith(
                ('TOR04 | Frota ', 'TOR04 | URL lateral', 'TOR04 | Motor Euro')):
            slot.link = 'OBJECT'
            slot.material = white
            changed.append(o.name)
assert fingerprint() == before, 'A variante não pode modificar geometria, textos ou pivôs.'
root['boas_asset_id'] = vehicle['asset_id']
root['boas_variant_id'] = variant['variant_id']
root['boas_variant_parent'] = base['file']
root['boas_variant_scope'] = variant['scope']
scene.name = variant['scene']
scene['boas_variant_id'] = variant['variant_id']
scene.frame_set(1)

target.parent.mkdir(parents=True, exist_ok=True)
# Escreve apenas a cena ativa e suas dependências: uma unidade por arquivo,
# sem copiar as cenas históricas amarela/v03 que o arquivo legado contém.
bpy.data.libraries.write(str(target), {scene}, path_remap='RELATIVE', fake_user=True, compress=True)
variant['sha256'] = hashlib.sha256(target.read_bytes()).hexdigest()
catalog_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
report = {
    'asset_id': vehicle['asset_id'], 'variant_id': variant['variant_id'],
    'base': base, 'output': variant, 'objects': len(scene.objects),
    'paint_srgb': paint_hex, 'paint_status': 'approximation_not_factory_measurement',
    'changed_material_objects': sorted(set(changed)),
    'preserved_yellow_objects': sorted(set(preserved_yellow)),
    'geometry_text_transform_fingerprint_unchanged': True,
    'source_hash_unchanged': hashlib.sha256(source.read_bytes()).hexdigest() == base['sha256'],
    'notes': ['Mantidos anúncio, vidros, três portas, animações e todas as dimensões.',
              'Variante de pintura; carroceria, números de frota e textos existentes mantidos.',
              'Runtime não integrado nesta etapa.']
}
out = repo / ('docs/reports/blender/torino_'+color+'_v01.json')
out.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'file': variant['file'], 'changed': len(set(changed))}))
# Reabertura na mesma janela para conferir a fonte entregue.
def reopen():
    bpy.ops.wm.open_mainfile(filepath=str(target))
    return None
bpy.app.timers.register(reopen, first_interval=1)
