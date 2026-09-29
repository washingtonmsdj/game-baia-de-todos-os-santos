"""Aplica o anúncio fornecido no vidro traseiro do Torino 31065."""
import bpy, json
from pathlib import Path

s = bpy.context.scene
assert s.name == 'ONIBUS | Torino 31065 v05'
root = bpy.data.objects['TOR04_ROOT']
base = Path(bpy.data.filepath).parent
image_path = Path(r'C:/Users/TONECOS/Downloads/1410158f-a935-4d7d-863a-6491bdb5ee04.png')
assert image_path.exists(), image_path
target = base / 'onibus_torino_31065_v06_anuncio_traseiro.blend'
assert not target.exists(), 'Preservar revisões anteriores'

coll = bpy.data.collections.get('TOR04 | ACABAMENTOS') or bpy.data.collections.new('TOR04 | ACABAMENTOS')
if coll.name not in s.collection.children:
    try: s.collection.children.link(coll)
    except RuntimeError: pass

img = bpy.data.images.load(str(image_path), check_existing=True)
img.name = 'TOR06 | Anuncio Bay of All Saints'
img.pack()

mat = bpy.data.materials.get('TOR06 | Anuncio no vidro traseiro') or bpy.data.materials.new('TOR06 | Anuncio no vidro traseiro')
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links
nodes.clear()
out = nodes.new('ShaderNodeOutputMaterial')
tex = nodes.new('ShaderNodeTexImage')
tex.image = img
tex.interpolation = 'Linear'
tex.extension = 'CLIP'
emission = nodes.new('ShaderNodeEmission')
emission.inputs['Strength'].default_value = .85
links.new(tex.outputs['Color'], emission.inputs['Color'])
links.new(emission.outputs['Emission'], out.inputs['Surface'])
if hasattr(mat, 'surface_render_method'):
    mat.surface_render_method = 'DITHERED'
mat.diffuse_color = (.08, .18, .28, 1.0)

frame_mat = bpy.data.materials.get('TOR04 | Borracha EPDM')
assert frame_mat is not None

def box_mesh(name, lo, hi, material):
    x,y,z = lo; X,Y,Z = hi
    vs = [(x,y,z),(X,y,z),(X,Y,z),(x,Y,z),(x,y,Z),(X,y,Z),(X,Y,Z),(x,Y,Z)]
    fs = [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    me = bpy.data.meshes.new(name+' mesh'); me.from_pydata(vs, [], fs); me.materials.append(material); me.update()
    ob = bpy.data.objects.new(name, me); coll.objects.link(ob); ob.parent = root
    bevel = ob.modifiers.new('Arredondamento da moldura', 'BEVEL'); bevel.width = .008; bevel.segments = 2
    return ob

# Duplica a superfície curva real para que o anúncio cubra 100% do vidro,
# sem deixar bordas vazias e sem criar uma placa plana atravessando a janela.
glass = bpy.data.objects['TOR04 | Traseira vidro curvo']
ad = bpy.data.objects.new('TOR06 | Anuncio cobrindo vidro traseiro', glass.data.copy())
coll.objects.link(ad); ad.parent = root; ad.data.materials.clear(); ad.data.materials.append(mat)
for vertex in ad.data.vertices: vertex.co.y += .022
uv = ad.data.uv_layers.new(name='UV anuncio tela inteira')
xs = [vertex.co.x for vertex in ad.data.vertices]; zs = [vertex.co.z for vertex in ad.data.vertices]
x0,x1,z0,z1 = min(xs),max(xs),min(zs),max(zs)
for poly in ad.data.polygons:
    for loop_index in poly.loop_indices:
        vertex = ad.data.vertices[ad.data.loops[loop_index].vertex_index].co
        loop_uv = uv.data[loop_index]
        loop_uv.uv = (1-(vertex.x-x0)/(x1-x0),(vertex.z-z0)/(z1-z0))
ad.data.update()
ad['asset_role'] = 'advertisement_full_rear_glass'
ad['coverage'] = '100% da superficie do vidro traseiro'
ad['source_image'] = str(image_path)
ad['reference_note'] = 'Imagem fornecida pelo usuario; textura embutida no arquivo blend.'

root['v06_anuncio_traseiro'] = 'Imagem fornecida cobrindo integralmente o vidro traseiro.'
s.name = 'ONIBUS | Torino 31065 v06'
s.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(target), compress=True)
print(json.dumps({'arquivo': str(target), 'imagem': str(image_path), 'cobertura': '100% do vidro traseiro'}))
