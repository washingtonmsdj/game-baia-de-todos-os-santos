import bpy
import json
from pathlib import Path

REVISION = 'R30A.8'
SURFACE_NAME = 'BAÍA DE TODOS-OS-SANTOS | superfície e recorte costeiro'
VOLUME_NAME = 'BAÍA | volume de água no limite do recorte'
FOAM_SOURCE = 'REF_WATERFRONT'
VISUAL_COLLECTION = '36 VISUAL | OCEANO R30A8'


def ensure_collection(name):
    coll = bpy.data.collections.get(name)
    if coll is None:
        coll = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(coll)
    return coll


def clear_material(mat):
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    return nodes, mat.node_tree.links


def input_set(node, name, value):
    sock = node.inputs.get(name)
    if sock is not None:
        sock.default_value = value

def make_water_material():
    mat = bpy.data.materials.get('R30A8 | Água oceânica') or bpy.data.materials.new('R30A8 | Água oceânica')
    nodes, links = clear_material(mat)
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    tex = nodes.new('ShaderNodeTexCoord')
    mapping = nodes.new('ShaderNodeMapping')
    noise_big = nodes.new('ShaderNodeTexNoise')
    noise_small = nodes.new('ShaderNodeTexNoise')
    bump_big = nodes.new('ShaderNodeBump')
    bump_small = nodes.new('ShaderNodeBump')
    layer = nodes.new('ShaderNodeLayerWeight')
    mix = nodes.new('ShaderNodeMixRGB')
    mix.blend_type = 'MIX'
    mix.inputs[1].default_value = (0.006, 0.055, 0.072, 1.0)
    mix.inputs[2].default_value = (0.018, 0.19, 0.22, 1.0)
    input_set(bsdf, 'Roughness', 0.16)
    input_set(bsdf, 'IOR', 1.333)
    input_set(bsdf, 'Metallic', 0.0)
    input_set(bsdf, 'Transmission Weight', 0.18)
    input_set(bsdf, 'Coat Weight', 0.22)
    input_set(bsdf, 'Coat Roughness', 0.08)
    input_set(noise_big, 'Scale', 0.055)
    input_set(noise_big, 'Detail', 5.0)
    input_set(noise_big, 'Roughness', 0.65)
    input_set(noise_big, 'Distortion', 0.18)
    input_set(noise_small, 'Scale', 0.22)
    input_set(noise_small, 'Detail', 3.0)
    input_set(noise_small, 'Roughness', 0.72)
    input_set(noise_small, 'Distortion', 0.08)
    input_set(bump_big, 'Strength', 0.23)
    input_set(bump_big, 'Distance', 0.35)
    input_set(bump_small, 'Strength', 0.12)
    input_set(bump_small, 'Distance', 0.12)
    mapping.vector_type = 'POINT'
    links.new(tex.outputs['Object'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], noise_big.inputs['Vector'])
    links.new(mapping.outputs['Vector'], noise_small.inputs['Vector'])
    links.new(noise_big.outputs['Fac'], bump_big.inputs['Height'])
    links.new(noise_small.outputs['Fac'], bump_small.inputs['Height'])
    links.new(bump_big.outputs['Normal'], bump_small.inputs['Normal'])
    links.new(bump_small.outputs['Normal'], bsdf.inputs['Normal'])
    links.new(layer.outputs['Facing'], mix.inputs[0])
    links.new(mix.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mat.diffuse_color = (0.01, 0.11, 0.15, 1.0)
    mat['boas_revision'] = REVISION
    mat['boas_water_role'] = 'visual_surface'
    return mat


def make_volume_material():
    mat = bpy.data.materials.get('R30A8 | Volume oceânico') or bpy.data.materials.new('R30A8 | Volume oceânico')
    nodes, links = clear_material(mat)
    out = nodes.new('ShaderNodeOutputMaterial')
    volume = nodes.new('ShaderNodeVolumePrincipled')
    input_set(volume, 'Color', (0.004, 0.035, 0.05, 1.0))
    input_set(volume, 'Density', 0.035)
    input_set(volume, 'Anisotropy', 0.25)
    links.new(volume.outputs['Volume'], out.inputs['Volume'])
    mat.diffuse_color = (0.004, 0.035, 0.05, 1.0)
    mat['boas_revision'] = REVISION
    mat['boas_water_role'] = 'visual_volume'
    return mat


def make_foam_material(name, alpha, emission_strength):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    nodes, links = clear_material(mat)
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    input_set(bsdf, 'Base Color', (0.82, 0.92, 0.94, 1.0))
    input_set(bsdf, 'Roughness', 0.48)
    input_set(bsdf, 'Emission Color', (0.18, 0.23, 0.24, 1.0))
    input_set(bsdf, 'Emission Strength', emission_strength)
    input_set(bsdf, 'Alpha', alpha)
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mat.diffuse_color = (0.82, 0.92, 0.94, alpha)
    try:
        mat.surface_render_method = 'DITHERED'
    except Exception:
        pass
    mat['boas_revision'] = REVISION
    return mat


def assign_material(obj, mat):
    if obj.data and hasattr(obj.data, 'materials'):
        obj.data.materials.clear()
        obj.data.materials.append(mat)

def animate_water_material(mat):
    noises = [n for n in mat.node_tree.nodes if n.bl_idname == 'ShaderNodeTexNoise']
    for index, node in enumerate(noises):
        try:
            node.noise_dimensions = '4D'
            socket = node.inputs.get('W')
            if socket is not None:
                socket.default_value = index * 11.3
                driver = socket.driver_add('default_value').driver
                driver.expression = f'{index * 11.3} + frame * {0.006 + index * 0.004}'
        except Exception:
            pass


def rebuild_foam(source, collection, material, name, bevel, z_offset):
    old = bpy.data.objects.get(name)
    if old is not None:
        bpy.data.objects.remove(old, do_unlink=True)
    obj = source.copy()
    obj.data = source.data.copy()
    obj.name = name
    collection.objects.link(obj)
    obj.location.z += z_offset
    if obj.type == 'CURVE':
        obj.data.bevel_depth = bevel
        obj.data.bevel_resolution = 3
        obj.data.resolution_u = max(6, obj.data.resolution_u)
        obj.data.materials.clear()
        obj.data.materials.append(material)
    obj['boas_revision'] = REVISION
    obj['boas_visual_only'] = True
    obj.hide_render = False
    return obj

def main():
    surface = bpy.data.objects.get(SURFACE_NAME)
    volume_obj = bpy.data.objects.get(VOLUME_NAME)
    source = bpy.data.objects.get(FOAM_SOURCE)
    assert surface is not None, SURFACE_NAME
    assert volume_obj is not None, VOLUME_NAME
    assert source is not None, FOAM_SOURCE

    visual = ensure_collection(VISUAL_COLLECTION)
    water_mat = make_water_material()
    animate_water_material(water_mat)
    volume_mat = make_volume_material()
    foam_near = make_foam_material('R30A8 | Espuma costeira', 0.70, 0.10)
    foam_soft = make_foam_material('R30A8 | Espuma costeira suave', 0.28, 0.03)
    assign_material(surface, water_mat)
    assign_material(volume_obj, volume_mat)
    foam_a = rebuild_foam(source, visual, foam_near, 'R30A8 | FOAM | linha costeira', 0.28, 0.43)
    foam_b = rebuild_foam(source, visual, foam_soft, 'R30A8 | FOAM | halo costeiro', 0.72, 0.405)

    for obj in (surface, volume_obj, foam_a, foam_b):
        obj['boas_water_system'] = 'r30a8_ocean'
    surface['boas_gameplay_surface_flat'] = True
    volume_obj['boas_runtime_volume'] = True
    scene = bpy.context.scene
    scene['boas_revision'] = REVISION
    scene['boas_ocean_status'] = 'visual_candidate'
    scene['boas_ocean_surface_z_m'] = 0.35
    scene['boas_ocean_animation'] = 'shader_4d_noise_driven_by_frame'
    # O volume existe para semântica/runtime, mas não deve pesar no render visual.
    volume_obj.hide_render = True
    volume_obj.hide_viewport = True
    surface.hide_render = False
    surface.hide_viewport = False
    foam_a.hide_viewport = False
    foam_b.hide_viewport = False

    # Mantém a água física plana; a sensação de ondas nasce só no shader.
    for area in bpy.context.screen.areas if bpy.context.screen else []:
        if area.type == 'VIEW_3D':
            try:
                area.spaces.active.shading.type = 'MATERIAL'
            except Exception:
                pass

    output = Path(bpy.path.abspath('//salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a8_ocean.blend'))
    bpy.ops.wm.save_as_mainfile(filepath=str(output))

    report_dir = Path(bpy.path.abspath('//../docs/reports/blender/r30a8'))
    report_dir.mkdir(parents=True, exist_ok=True)
    report = {
        'schema': 'bay-of-all-saints/r30a8-ocean-scene-v1',
        'revision': REVISION,
        'status': 'visual_candidate',
        'surface_z_m': 0.35,
        'surface': surface.name,
        'volume': volume_obj.name,
        'foam': [foam_a.name, foam_b.name],
        'water_material': water_mat.name,
        'volume_material': volume_mat.name,
        'gameplay_surface_flat': True,
        'animation': '4D shader noise driven by frame',
        'output_blend': str(output),
    }
    import hashlib
    digest = hashlib.sha256()
    with output.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    report['output_sha256'] = digest.hexdigest().upper()
    (report_dir / 'ocean_scene.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8'
    )
    print(report)


if __name__ == '__main__':
    main()
