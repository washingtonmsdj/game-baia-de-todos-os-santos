"""Apoio oposto da passarela e intradorso, editados na janela visível."""
import bpy, bmesh, json
from pathlib import Path
from mathutils import Matrix, Vector

root = Path(__file__).resolve().parents[2]
assert bpy.data.filepath.endswith('salvador_lacerda_r30b07_torre_entrada.blend')
assert 'HERO | Lacerda | apoio oposto R30B08' not in bpy.data.collections
rotation = Matrix.Rotation(bpy.data.objects['CASCA | parede lateral'].rotation_euler.z, 4, 'Z')
collection = bpy.data.collections.new('HERO | Lacerda | apoio oposto R30B08')
bpy.context.scene.collection.children.link(collection)
cream = bpy.data.materials['LAC R30B | reboco marfim fino']

shade = bpy.data.materials.get('LAC R30B08 | intradorso marfim sombreado')
if shade is None:
    shade = bpy.data.materials.new('LAC R30B08 | intradorso marfim sombreado')
    shade.diffuse_color = (.53, .49, .38, 1)
    shade.use_nodes = True
    bsdf = next(n for n in shade.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs['Base Color'].default_value = (.53, .49, .38, 1)
    bsdf.inputs['Roughness'].default_value = .82

def mesh(name, vertices, faces, material, role='visual_architecture'):
    data = bpy.data.meshes.new(name)
    data.from_pydata([tuple(rotation @ Vector(p)) for p in vertices], [], faces)
    data.update()
    bm = bmesh.new()
    bm.from_mesh(data)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(data)
    bm.free()
    data.materials.append(material)
    obj = bpy.data.objects.new('LAC R30B08 | ' + name, data)
    collection.objects.link(obj)
    obj['boas_location_id'] = 'elevador-lacerda'
    obj['boas_role'] = role
    obj['classification'] = 'ADAPT_LOCAL'
    obj['reference_status'] = 'partial'
    obj['reference_note'] = 'Fotografia fornecida pelo usuario: apoio largo oposto a torre; dimensoes ajustadas ao terreno existente.'
    return obj

def box(name, center, size, material):
    x, y, z = [value / 2 for value in size]
    points = [(-x,-y,-z), (-x,-y,z), (-x,y,-z), (-x,y,z),
              (x,-y,-z), (x,-y,z), (x,y,-z), (x,y,z)]
    vertices = [tuple(Vector(center) + Vector(p)) for p in points]
    faces = [(0,4,6,2), (1,3,7,5), (0,1,5,4), (2,6,7,3),
             (0,2,3,1), (4,5,7,6)]
    return mesh(name, vertices, faces, material)

# O apoio fica na extremidade Cidade Alta, sob a galeria, e penetra na encosta
# já existente. A base foi confrontada com amostras do terreno desta revisão.
# Contornos em X,Y,Z: base estreita, corpo vertical e consolo que se alarga
# até a face inferior da passarela. Não cria um segundo poço de elevador.
rings = [
    (-26.10, -18.20, .78, 7.72, 21.00),
    (-25.30, -17.30, .78, 7.72, 39.00),
    (-24.55, -16.65, .78, 7.72, 58.00),
    (-24.25, -16.25, .78, 7.72, 65.40),
    (-26.60, -11.85, .63, 7.87, 68.85),
]
verts = []
for x0, x1, y0, y1, z in rings:
    verts.extend([(x0,y0,z), (x1,y0,z), (x1,y1,z), (x0,y1,z)])
faces = [(3,2,1,0)]
for k in range(len(rings)-1):
    a = 4*k
    b = a+4
    faces.extend([(a+i, a+(i+1)%4, b+(i+1)%4, b+i) for i in range(4)])
faces.append(tuple(range(4*(len(rings)-1), 4*len(rings))))
support = mesh('apoio oposto | corpo estrutural afunilado', verts, faces, cream)
support['ground_sample_min_z'] = 21.0
support['ground_sample_max_z'] = 68.85
support['design_note'] = 'Base enterrada na encosta; não desloca malha de terreno nem superfície da ladeira.'
bevel = support.modifiers.new('Arestas suaves de concreto', 'BEVEL')
bevel.width = .09
bevel.segments = 2
bevel.affect = 'EDGES'
support.modifiers.new('Normais ponderadas', 'WEIGHTED_NORMAL')

# Cabeça da fundação e encontro com a viga sob o piso da galeria.
box('apoio oposto | capitel sob passarela', (-19.225, 4.25, 68.96), (15.0, 7.45, .44), cream)
box('passarela | intradorso continuo', (-39.1545, 4.245, 68.98), (55.539, 5.73, .30), cream)
box('passarela | sombra central do intradorso', (-39.1545, 4.245, 68.80), (54.90, 4.90, .025), shade)
for y in (1.26, 7.23):
    box('passarela | viga longitudinal inferior %.2f' % y,
        (-39.1545, y, 68.75), (55.539, .30, .60), cream)

# Faixa de encontro discreta mantém leitura de peça independente e evita
# uma emenda aberta entre a galeria e o apoio visto da Cidade Baixa.
box('apoio oposto | ressalto transversal', (-19.225, 4.25, 68.58), (14.50, 7.18, .24), cream)

for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D' and area.spaces.active.local_view:
        for obj in collection.objects:
            obj.local_view_set(area.spaces.active, True)
bpy.context.scene['lacerda_revision'] = 'R30B.08 | apoio oposto e intradorso da passarela'
dest = root / 'blender/salvador_lacerda_r30b08_apoio_passarela.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(dest))
report = {
    'revision': dest.name,
    'location_id': 'elevador-lacerda',
    'new_objects': [o.name for o in collection.objects],
    'reference': 'fotografia fornecida pelo usuario e R30B10_ALEPH_STRUCTURAL_RESEARCH',
    'classification': 'ADAPT_LOCAL',
    'terrain_changed': False,
    'road_changed': False,
    'runtime_promoted': False,
    'status': 'partial',
}
(root / 'artifacts/lacerda/r30b08_support_report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf8')
print(json.dumps({'saved': dest.name, 'objects': len(collection.objects)}, ensure_ascii=False))
