"""Reamostra a máscara material depois do perfil local, sem mover vértices."""
import bpy,json,hashlib
import numpy as np
from pathlib import Path

root=Path(__file__).resolve().parents[2]
path=root/'docs/reports/blender/palacio_rio_branco_r30b34.json'
r=json.loads(path.read_text(encoding='utf8'))
assert not r.get('barranco_mask_resampled'),'Máscara já atualizada'
o=bpy.context.scene.objects['MVP | terreno corrigido | colisão estática'];me=o.data
points=np.empty(len(me.vertices)*3,dtype=np.float32);me.vertices.foreach_get('co',points)
matrix=np.array(o.matrix_world,dtype=np.float64)
world=points.reshape((-1,3))@matrix[:3,:3].T+matrix[:3,3]
weights=np.zeros(len(me.vertices),dtype=np.float32)
for s in r['galleries']['segments']:
    delta=world-np.array(s['origin_world']);x=delta@np.array(s['along_world']);y=delta@np.array(s['outward_world'])
    region=(x>-3)&(x<s['length_from_existing_controls_m']+3)&(y>.1)&(y<20)&(world[:,2]>22)&(world[:,2]<s['top_z_preserved_m']-.2)
    values=np.clip(1-np.maximum(0,y-7)/13,0,1)
    weights=np.maximum(weights,np.where(region,values,0).astype(np.float32))
me.attributes['boas_r34_barranco'].data.foreach_set('value',weights)
for name in r['galleries']['terrain']['material_graphs_copied']:
    nt=bpy.data.materials[name].node_tree
    attr=next(n for n in nt.nodes if n.type=='ATTRIBUTE' and n.attribute_name=='boas_r34_barranco')
    mult=attr.outputs['Fac'].links[0].to_node
    mix=mult.outputs[0].links[0].to_node
    nt.links.new(attr.outputs['Fac'],mix.inputs[0])
    # Solo nas áreas expostas sob a contenção; não apenas nas faces verticais.
    clay=mix.inputs[2].links[0].from_node
    ramp=clay.inputs['Base Color'].links[0].from_node
    ramp.color_ramp.elements[0].color=(.11,.09,.055,1)
    ramp.color_ramp.elements[1].color=(.22,.29,.075,1)
    position=nt.nodes.new('ShaderNodeNewGeometry').outputs['Position']
    grain=nt.nodes.new('ShaderNodeTexNoise');grain.inputs['Scale'].default_value=75;grain.inputs['Detail'].default_value=3
    nt.links.new(position,grain.inputs['Vector'])
    fine=nt.nodes.new('ShaderNodeBump');fine.inputs['Strength'].default_value=.28;fine.inputs['Distance'].default_value=.012
    nt.links.new(grain.outputs['Fac'],fine.inputs['Height'])
    if clay.inputs['Normal'].links:nt.links.new(clay.inputs['Normal'].links[0].from_socket,fine.inputs['Normal'])
    nt.links.new(fine.outputs['Normal'],clay.inputs['Normal'])

r['barranco_mask_resampled']={'masked_vertices':int(np.count_nonzero(weights)),'reason':'Máscara original antecedia a escavação; reamostrada no perfil final para texturizar o solo exposto.','geometry_changed':False,'scope':'Somente material de terreno nas duas bandas de galerias; materiais de circulação não alterados.','status':'candidate'}
r['visual_review']='pending_final_material_review'
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
with Path(bpy.data.filepath).open('rb') as f:r['source_after']['sha256']=hashlib.file_digest(f,'sha256').hexdigest()
path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'masked_vertices':r['barranco_mask_resampled']['masked_vertices'],'source_after':r['source_after']},ensure_ascii=False))
