"""Acabamento externo: vidro legivel, reboco e letreiro do acesso inferior."""
import bpy,json
from pathlib import Path
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[2]
assert bpy.data.filepath.endswith('salvador_lacerda_r30b21_acesso_baixo.blend')
R=Matrix.Rotation(bpy.data.objects['CASCA | parede lateral'].rotation_euler.z,4,'Z');I=R.inverted()
glass=bpy.data.materials['LAC R30B | vidro incolor transparente']
p=next(n for n in glass.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
p.inputs['Base Color'].default_value=(.22,.31,.33,1)
p.inputs['Transmission Weight'].default_value=0
p.inputs['Alpha'].default_value=.32
p.inputs['Roughness'].default_value=.16
glass.diffuse_color=(.22,.31,.33,.32)
glass.surface_render_method='BLENDED'
glass['finish_note']='Vidro fino com alpha; evita ruido de transmissao no viewport. Rever refração por engine na exportação.'

cream=bpy.data.materials['LAC R30B19 | reboco creme torre']
nt=cream.node_tree;p=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED')
coord=nt.nodes.new('ShaderNodeTexCoord');noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=28;noise.inputs['Detail'].default_value=2
bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.10;bump.inputs['Distance'].default_value=.0006
nt.links.new(coord.outputs['Object'],noise.inputs['Vector']);nt.links.new(noise.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],p.inputs['Normal'])

# O letreiro cruza os pilares: ajustar a largura para caber no pano central.
o=bpy.data.objects['FACHADA INFERIOR R22 | identificação']
points=[I@o.matrix_world@v.co for v in o.data.vertices]
y0=min(p.y for p in points);y1=max(p.y for p in points);mid=(y0+y1)/2
inv=o.matrix_world.inverted()
for v in o.data.vertices:
 p=I@o.matrix_world@v.co;p.y=4.245+(p.y-mid)*(2.50/(y1-y0));v.co=inv@R@p
o['revision_note']='R30B22: texto contido entre pilares do portal central; sem mover fachada.'

bpy.context.scene['lacerda_revision']='R30B.22 | vidros, reboco e identificacao'
dest=ROOT/'blender/salvador_lacerda_r30b22_exterior_vidros.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
(ROOT/'artifacts/lacerda/r30b22_report.json').write_text(json.dumps({'revision':dest.name,'glass':'alpha blended, transmissao 0 para vidro fino','plaster':'microrelevo procedural em coordenadas de objeto','sign_width_m':2.5,'geography_changed':False,'status':'partial','runtime_promoted':False},ensure_ascii=False,indent=2),encoding='utf8')
