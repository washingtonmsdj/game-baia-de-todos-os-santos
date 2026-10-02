"""Acabamento procedural em escala métrica; sem usar fotos como textura."""
import bpy,json,hashlib
from pathlib import Path

root=Path(__file__).resolve().parents[2]
path=root/'docs/reports/blender/palacio_rio_branco_r30b34.json'
r=json.loads(path.read_text(encoding='utf8'))
assert not r.get('gallery_material_refinement'),'Material já refinado'

def noise(nt,position,scale,detail=3):
    node=nt.nodes.new('ShaderNodeTexNoise')
    node.inputs['Scale'].default_value=scale
    node.inputs['Detail'].default_value=detail
    nt.links.new(position,node.inputs['Vector'])
    return node

stone=bpy.data.materials['GAL R34 | alvenaria mista de pedra']
nt=stone.node_tree;nt.nodes.clear()
output=nt.nodes.new('ShaderNodeOutputMaterial')
bsdf=nt.nodes.new('ShaderNodeBsdfPrincipled');bsdf.inputs['Roughness'].default_value=.91
nt.links.new(bsdf.outputs['BSDF'],output.inputs['Surface'])
position=nt.nodes.new('ShaderNodeNewGeometry').outputs['Position']
# Perturbação curta do desenho das pedras, em metros do mundo.
warp=noise(nt,position,2.7)
center=nt.nodes.new('ShaderNodeVectorMath');center.operation='SUBTRACT';center.inputs[1].default_value=(.5,.5,.5)
nt.links.new(warp.outputs['Color'],center.inputs[0])
amp=nt.nodes.new('ShaderNodeVectorMath');amp.operation='SCALE';amp.inputs['Scale'].default_value=.18
nt.links.new(center.outputs[0],amp.inputs[0])
coords=nt.nodes.new('ShaderNodeVectorMath');coords.operation='ADD'
nt.links.new(position,coords.inputs[0]);nt.links.new(amp.outputs[0],coords.inputs[1])
cells=nt.nodes.new('ShaderNodeTexVoronoi');cells.feature='DISTANCE_TO_EDGE';cells.inputs['Scale'].default_value=3.1
nt.links.new(coords.outputs[0],cells.inputs['Vector'])
edges=nt.nodes.new('ShaderNodeValToRGB')
edges.color_ramp.elements[0].position=.012;edges.color_ramp.elements[0].color=(0,0,0,1)
edges.color_ramp.elements[1].position=.052;edges.color_ramp.elements[1].color=(1,1,1,1)
nt.links.new(cells.outputs['Distance'],edges.inputs[0])
variation=noise(nt,position,4.2,5)
color=nt.nodes.new('ShaderNodeValToRGB')
color.color_ramp.elements[0].position=.25;color.color_ramp.elements[0].color=(.08,.068,.045,1)
color.color_ramp.elements[1].position=.76;color.color_ramp.elements[1].color=(.38,.33,.25,1)
color.color_ramp.elements.new(.49).color=(.19,.19,.145,1)
nt.links.new(variation.outputs['Fac'],color.inputs[0])
mix=nt.nodes.new('ShaderNodeMixRGB');mix.blend_type='MIX';mix.inputs[1].default_value=(.095,.083,.068,1)
nt.links.new(edges.outputs[0],mix.inputs[0]);nt.links.new(color.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],bsdf.inputs['Base Color'])
fine=noise(nt,position,95,2)
bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.34;bump.inputs['Distance'].default_value=.014
nt.links.new(fine.outputs['Fac'],bump.inputs['Height'])
joint=nt.nodes.new('ShaderNodeBump');joint.inputs['Strength'].default_value=.38;joint.inputs['Distance'].default_value=.026
nt.links.new(edges.outputs[0],joint.inputs['Height']);nt.links.new(bump.outputs[0],joint.inputs['Normal']);nt.links.new(joint.outputs[0],bsdf.inputs['Normal'])

changed=[stone.name]
for name in ('GAL R34 | tijolo exposto dos arcos','GAL R34 | argamassa e guarda-corpo claro'):
    m=bpy.data.materials[name];nodes=m.node_tree.nodes;links=m.node_tree.links
    position=nodes.new('ShaderNodeNewGeometry').outputs['Position']
    for node in list(nodes):
        if node.type=='TEX_NOISE':
            node.inputs['Scale'].default_value=18 if 'tijolo' in name else 70
            links.new(position,node.inputs['Vector'])
        if node.type=='BUMP':
            node.inputs['Distance'].default_value=.007 if 'tijolo' in name else .002
            node.inputs['Strength'].default_value=.25 if 'tijolo' in name else .12
    changed.append(name)

# Apenas o ramo novo da máscara do barranco: cores em escala de metros.
for name in r['galleries']['terrain']['material_graphs_copied']:
    m=bpy.data.materials[name];nt=m.node_tree
    position=nt.nodes.new('ShaderNodeNewGeometry').outputs['Position']
    for node in list(nt.nodes):
        if node.type=='TEX_NOISE' and abs(node.inputs['Scale'].default_value-1.6)<.001:
            nt.links.new(position,node.inputs['Vector'])
    changed.append(name)

r['gallery_material_refinement']={'materials':changed,'texture_source':'procedural_only','coordinates':'Geometry.Position em metros; sem capturas fotográficas embutidas','status':'candidate','geometry_changed':False,'reason':'Pedras e argamassa visíveis nas fotos; remove aparência de parede lisa causada por coordenadas Generated normalizadas.'}
r['galleries']['terrain']['scope']='Etapa inicial somente de máscara/material; alterações posteriores de geometria/proxy estão em retaining_profile_refinement.'
r['galleries']['terrain']['vertices_moved_in_material_stage']=r['galleries']['terrain'].pop('vertices_moved')
r['galleries']['terrain']['collider_changed_in_material_stage']=r['galleries']['terrain'].pop('collider_changed')
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
with Path(bpy.data.filepath).open('rb') as f:r['source_after']['sha256']=hashlib.file_digest(f,'sha256').hexdigest()
path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'materials':changed,'source_after':r['source_after']},ensure_ascii=False))
