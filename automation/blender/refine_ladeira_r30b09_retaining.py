"""Material da contenção da Ladeira da Montanha na geometria existente."""
import bpy, json
from pathlib import Path
from mathutils import Matrix, Vector

root = Path(__file__).resolve().parents[2]
assert bpy.data.filepath.endswith('salvador_lacerda_r30b08_apoio_passarela.blend')
terrain = bpy.data.objects['MVP | terreno corrigido | colisão estática']
rotation = Matrix.Rotation(bpy.data.objects['CASCA | parede lateral'].rotation_euler.z, 4, 'Z')
inverse = rotation.inverted()
stone = bpy.data.materials.get('LAC R30B09 | pedra irregular da contenção')
if stone is None:
    stone = bpy.data.materials.new('LAC R30B09 | pedra irregular da contenção')
    stone.diffuse_color = (.32, .31, .27, 1)
    stone.use_nodes = True
    nt = stone.node_tree
    bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs['Roughness'].default_value = .92
    tex = nt.nodes.new('ShaderNodeTexVoronoi')
    tex.feature = 'DISTANCE_TO_EDGE'
    tex.inputs['Scale'].default_value = 1.35
    geo = nt.nodes.new('ShaderNodeNewGeometry')
    nt.links.new(geo.outputs['Position'], tex.inputs['Vector'])
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = .018
    ramp.color_ramp.elements[0].color = (.075,.074,.066,1)
    ramp.color_ramp.elements[1].position = .11
    ramp.color_ramp.elements[1].color = (.36,.35,.30,1)
    nt.links.new(tex.outputs['Distance'], ramp.inputs[0])
    nt.links.new(ramp.outputs[0], bsdf.inputs['Base Color'])
    bump = nt.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = .33
    bump.inputs['Distance'].default_value = .055
    nt.links.new(tex.outputs['Distance'], bump.inputs['Height'])
    nt.links.new(bump.outputs[0], bsdf.inputs['Normal'])

old = {i for i,m in enumerate(terrain.data.materials) if m and m.name == 'MVP | terreno contínuo'}
assert old
terrain.data.materials.append(stone)
new_index = len(terrain.data.materials)-1
changed = 0
for poly in terrain.data.polygons:
    if poly.material_index not in old:
        continue
    p = inverse @ terrain.matrix_world @ poly.center
    if not (-38.0 <= p.x <= -18.0 and -40.0 <= p.y <= 46.0 and 21.0 <= p.z <= 69.0):
        continue
    normal = (terrain.matrix_world.to_3x3() @ poly.normal).normalized()
    if abs(normal.z) > .72:
        continue
    poly.material_index = new_index
    changed += 1
assert changed > 0, 'Nenhuma face do talude foi encontrada para a contenção'
terrain['r30b09_retaining_faces'] = changed
terrain['r30b09_note'] = 'Apenas material visual nas faces íngremes junto à Ladeira; topologia, pista e colisão preservadas.'
bpy.context.scene['lacerda_revision'] = 'R30B.09 | contenção visual Ladeira da Montanha'
dest = root / 'blender/salvador_lacerda_r30b09_contecao_ladeira.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(dest))
report = {
    'revision':dest.name,
    'location_id':'corredor-cidade-baixa',
    'related_location_id':'elevador-lacerda',
    'terrain_material_faces':changed,
    'terrain_vertices_changed':0,
    'road_material_faces_changed':0,
    'reference':'elevador-lacerda-oblique_right-4ba71f16af8d',
    'classification':'ADAPT_LOCAL',
    'status':'partial; muro acompanha geometria atual, cota e contorno seguem revisão estrutural',
    'runtime_promoted':False,
}
(root / 'artifacts/lacerda/r30b09_retaining_report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf8')
print(json.dumps({'saved':dest.name,'faces':changed},ensure_ascii=False))
