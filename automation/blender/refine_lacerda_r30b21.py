"""Repara a face oposta e suaviza o acabamento mineral do acesso baixo."""
import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[2]
assert bpy.data.filepath.endswith('salvador_lacerda_r30b20_torre_duas_faces.blend')
R=Matrix.Rotation(bpy.data.objects['CASCA | parede lateral'].rotation_euler.z,4,'Z')

def normals(mesh):
 bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();mesh.update()

# R30B20 utilizou um cortador com faces orientadas para dentro. Restaura apenas
# a mesh anterior da parede, preservando objeto, transform e dependencias.
wall=bpy.data.objects['CASCA | fachada poço.002']
with bpy.data.libraries.load(str(ROOT/'blender/salvador_lacerda_r30b19_torre_venezianas.blend'),link=False) as (src,dst):
 dst.objects=['CASCA | fachada poço.002']
loaded=dst.objects[0]
wall.data=loaded.data.copy();bpy.data.objects.remove(loaded,do_unlink=True)
wall.data.materials.clear();wall.data.materials.append(bpy.data.materials['LAC R30B19 | reboco creme torre'])
normals(wall.data)
verts=[];faces=[]
for z,h in [(16.,2.8),(27.2,3.2),(39.,3.1),(51.,3.),(62.4,2.8)]:
 for yc in [2.2,6.2]:
  for j in [-1,0,1]:
   x=-66.9;y=yc+j*.49;n=len(verts)
   verts += [R@Vector((x+a*.4,y+b*.17,z+c*h/2)) for a,b,c in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]]
   faces += [tuple(n+i for i in f) for f in [(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]]
me=bpy.data.meshes.new('R30B21 cortador');me.from_pydata(verts,[],faces);normals(me)
ob=bpy.data.objects.new('R30B21 cortador',me);bpy.context.scene.collection.objects.link(ob)
mod=wall.modifiers.new('Venezianas opostas corrigidas','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=ob
bpy.context.view_layer.objects.active=wall;bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.data.objects.remove(ob,do_unlink=True);bpy.data.meshes.remove(me)
normals(wall.data)
for o in bpy.data.objects:
 if o.type=='MESH' and o.name.startswith('LAC R30B20 |'):normals(o.data)

def material(name,color,roughness):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1)
 nt=m.node_tree;nt.nodes.clear();p=nt.nodes.new('ShaderNodeBsdfPrincipled');out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(p.outputs['BSDF'],out.inputs['Surface'])
 p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=roughness
 return m,p

stone,p=material('LAC R30B21 | pedra clara acesso baixo',(.59,.57,.51),.68)
nt=stone.node_tree
noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=38
ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.47,.45,.40,1);ramp.color_ramp.elements[1].color=(.65,.63,.57,1)
nt.links.new(noise.outputs['Fac'],ramp.inputs[0]);nt.links.new(ramp.outputs[0],p.inputs['Base Color'])
glass,p=material('LAC R30B21 | vidro bandeiras acesso',(.22,.29,.27),.18)
p.inputs['Alpha'].default_value=.48;p.inputs['Transmission Weight'].default_value=.15
methods={item.identifier for item in glass.bl_rna.properties['surface_render_method'].enum_items}
glass.surface_render_method='BLENDED' if 'BLENDED' in methods else 'DITHERED'
glass.diffuse_color=(.22,.29,.27,.48)
changed=[]
for o in bpy.data.objects:
 if o.type!='MESH':continue
 if o.name.startswith(('LAC R30B03 | Cidade Baixa | retorno portal','LAC R30B03 | Cidade Baixa | verga portal')):
  o.data.materials.clear();o.data.materials.append(stone);changed.append(o.name)
 if o.name.startswith('FACHADA INFERIOR | bandeira'):
  o.data.materials.clear();o.data.materials.append(glass);changed.append(o.name)

target=R@Vector((-82.2,4.2,10.2));eye=R@Vector((-98.,4.2,10.9))
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   sp=area.spaces.active;r=sp.region_3d;r.view_perspective='PERSP';r.view_location=target;r.view_rotation=(target-eye).to_track_quat('-Z','Y');r.view_distance=(target-eye).length;sp.shading.type='MATERIAL'
bpy.context.scene['lacerda_revision']='R30B.21 | recortes e acabamento acesso baixo'
dest=ROOT/'blender/salvador_lacerda_r30b21_acesso_baixo.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
report={'revision':dest.name,'opposite_face_boolean_repaired':True,'modified_finishes':changed,'geography_changed':False,'runtime_promoted':False,'texture_status':'procedural; bake runtime pendente','status':'partial'}
(ROOT/'artifacts/lacerda/r30b21_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
