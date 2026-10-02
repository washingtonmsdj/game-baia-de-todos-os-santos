"""Acabamento da fachada superior conforme fotografia da praça fornecida."""
import bpy,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
assert bpy.data.filepath.endswith('salvador_lacerda_r30b22_exterior_vidros.blend')
def mat(name,color,rough):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
 p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough
 return m,p
beige,p=mat('LAC R30B23 | reboco bege fachada alta',(.57,.46,.34),.83)
nt=beige.node_tree;n=nt.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=38
b=nt.nodes.new('ShaderNodeBump');b.inputs['Strength'].default_value=.08;b.inputs['Distance'].default_value=.0006
nt.links.new(n.outputs['Fac'],b.inputs['Height']);nt.links.new(b.outputs['Normal'],p.inputs['Normal'])
trim,_=mat('LAC R30B23 | moldura mineral clara',(.78,.77,.69),.73)
stone,p=mat('LAC R30B23 | pedra castanha pilares altos',(.24,.20,.16),.63)
glass,p=mat('LAC R30B23 | vidro fachada da praca',(.19,.30,.35),.19)
p.inputs['Alpha'].default_value=.68;glass.surface_render_method='BLENDED';glass.diffuse_color=(.19,.30,.35,.68)
changed=[]
for o in bpy.data.objects:
 if o.type!='MESH':continue
 name=o.name;material=None
 if name.startswith(('FACHADA SUPERIOR | corpo elevado','FACHADA SUPERIOR | platibanda','SUPERIOR | lateral corpo elevado','FACHADA SUPERIOR | rebaixo quadrado','LAC R30B03 | Cidade Alta | degrau')):material=beige
 elif name.startswith(('FACHADA SUPERIOR | moldura','FACHADA SUPERIOR | relevo quadrado','FACHADA SUPERIOR | cornija','FACHADA SUPERIOR | faixa Lacerda')):material=trim
 elif name.startswith('FACHADA SUPERIOR | pilar térreo'):material=stone
 elif name.startswith(('FACHADA SUPERIOR | janela','EDIFICIO | janela lateral')):material=glass
 elif name.startswith('FACHADA SUPERIOR | folha aberta'):material=bpy.data.materials['LAC R30B21 | vidro bandeiras acesso']
 if material:
  o.data.materials.clear();o.data.materials.append(material)
  o['boas_location_id']='elevador-lacerda';o['reference_status']='partial';changed.append(name)
bpy.context.scene['lacerda_revision']='R30B.23 | fachada superior e contraste dos elementos'
dest=ROOT/'blender/salvador_lacerda_r30b23_fachada_praca.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
(ROOT/'artifacts/lacerda/r30b23_report.json').write_text(json.dumps({'revision':dest.name,'changed':changed,'reference':'foto da praca fornecida pelo usuario; tons interpretados sob iluminacao diurna','geography_changed':False,'status':'partial','runtime_promoted':False},ensure_ascii=False,indent=2),encoding='utf8')
