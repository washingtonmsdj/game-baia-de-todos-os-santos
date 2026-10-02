"""Corrige a leitura externa da torre conforme a referencia fotografica."""
import bpy, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
assert bpy.data.filepath.endswith('salvador_lacerda_r30b16_apoio_encosta_suavizada.blend')

def material(name,color,roughness):
    mat=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color=(*color,1)
    mat.use_nodes=True
    nodes=mat.node_tree.nodes
    nodes.clear()
    node=nodes.new('ShaderNodeBsdfPrincipled')
    output=nodes.new('ShaderNodeOutputMaterial')
    mat.node_tree.links.new(node.outputs['BSDF'],output.inputs['Surface'])
    node.inputs['Base Color'].default_value=(*color,1)
    node.inputs['Roughness'].default_value=roughness
    return mat

cream=material('LAC R30B19 | reboco creme torre',(0.72,0.705,0.635),0.88)
slat=material('LAC R30B19 | veneziana metal grafite',(0.16,0.165,0.155),0.68)
shadow=material('LAC R30B19 | fundo escuro veneziana',(0.055,0.059,0.056),0.9)

targets={
    'CASCA | fachada poço':cream,
    'CASCA | fachada poço.002':cream,
    'CALIBRADO | torre 3.55 x 7.48 x 73.50m':cream,
    'LAC R30B07 | torre | fundos recuados':shadow,
    'LAC R30B07 | torre | laminas venezianas':slat,
    'LAC R30B07 | corpo tecnico | fundos venezianas':shadow,
    'LAC R30B07 | corpo tecnico | laminas':slat,
}
updated=[]
for name,mat in targets.items():
    obj=bpy.data.objects.get(name)
    if not obj or obj.type!='MESH':continue
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    obj['boas_location_id']='elevador-lacerda'
    obj['reference_status']='partial'
    updated.append(name)

bpy.context.scene['lacerda_revision']='R30B.19 | torre venezianas e reboco'
dest=ROOT/'blender/salvador_lacerda_r30b19_torre_venezianas.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(dest))
report={'revision':dest.name,'source':'salvador_lacerda_r30b16_apoio_encosta_suavizada.blend','updated':updated,'terrain_changed':False,'support_moved':False,'status':'partial'}
(ROOT/'artifacts/lacerda/r30b19_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(report,ensure_ascii=False))
