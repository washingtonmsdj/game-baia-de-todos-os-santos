"""Confere a variante reaberta e enquadra frente/lateral."""
import bpy, hashlib, json
from pathlib import Path
from mathutils import Vector
repo = Path(__file__).resolve().parents[2]
path = repo / ('docs/reports/blender/torino_'+color+'_v01.json')
report = json.loads(path.read_text(encoding='utf-8'))
scene = bpy.context.scene
assert scene.name == report['output']['scene']
assert Path(bpy.data.filepath).resolve() == (repo / report['output']['file']).resolve()
assert len(scene.objects) == report['objects'] and len(bpy.data.scenes) == 1
assert hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest() == report['output']['sha256']
for name in report['preserved_yellow_objects']:
    assert any(s.material and 'Amarelo' in s.material.name for s in scene.objects[name].material_slots), name
for name in report['changed_material_objects']:
    expected = 'TOR04 | Branco sinalização' if scene.objects[name].type == 'FONT' else 'TORINO '+color.upper()+' | Pintura externa'
    assert any(s.material and s.material.name == expected for s in scene.objects[name].material_slots), name
ad = scene.objects['TOR06 | Anuncio cobrindo vidro traseiro']
images = [n.image for m in ad.data.materials for n in m.node_tree.nodes if n.type == 'TEX_IMAGE']
assert images and all(i.packed_file for i in images)
assert all(bpy.data.collections['TOR04 | PORTA_'+n].all_objects for n in ('DIANTEIRA','CENTRAL','TRASEIRA'))
report['readback'] = {'ok': True, 'scenes': 1, 'objects': len(scene.objects),
    'paint_materials_verified': True, 'safety_yellow_preserved': True,
    'rear_ad_packed': True, 'three_door_collections_present': True,
    'animated_objects': sum(bool(o.animation_data) for o in scene.objects)}
path.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
focus = Vector((0,0,1.5)); camera = Vector((-12,-16,8))
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            space = area.spaces.active
            space.shading.type = 'MATERIAL'
            space.region_3d.view_rotation = (focus-camera).to_track_quat('-Z','Y')
            space.region_3d.view_location = focus
            space.region_3d.view_distance = 10
            space.region_3d.view_perspective = 'ORTHO'
print('Variante reaberta; pintura, anúncio e componentes preservados.')
