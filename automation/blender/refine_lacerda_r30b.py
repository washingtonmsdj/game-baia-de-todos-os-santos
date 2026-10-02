"""Refinamento local, executado na janela Blender via MCP. Preserva a base R30A.11."""
import bpy, math, json
from pathlib import Path
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'artifacts/lacerda'
OUT.mkdir(parents=True, exist_ok=True)
assert 'r30a11_pedestrian_nav' in bpy.data.filepath, 'Abrir a fonte oficial antes de executar.'
assert not bpy.data.collections.get('HERO | Lacerda | detalhes R30B'), 'Revisão já aplicada.'
col = bpy.data.collections.new('HERO | Lacerda | detalhes R30B')
bpy.context.scene.collection.children.link(col)
theta = bpy.data.objects['CASCA | parede lateral'].rotation_euler.z
R = Matrix.Rotation(theta, 4, 'Z')
I = R.inverted()
targets = set()
for c in bpy.data.collections:
    if c.name.startswith(('11 ELEVADOR', '12 LACERDA', '30 LACERDA', '31 LACERDA')):
        targets.update(c.all_objects)

def material(name, color, rough=.5, metal=0):
    m = bpy.data.materials.new('LAC R30B | '+name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Roughness'].default_value = rough
    p.inputs['Metallic'].default_value = metal
    return m, p

ivory, p = material('reboco marfim fino', (.79,.77,.69), .73)
n=ivory.node_tree.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value=150
b=ivory.node_tree.nodes.new('ShaderNodeBump'); b.inputs['Strength'].default_value=.13; b.inputs['Distance'].default_value=.0015
ivory.node_tree.links.new(n.outputs['Fac'],b.inputs['Height']); ivory.node_tree.links.new(b.outputs['Normal'],p.inputs['Normal'])
frame,_ = material('esquadria clara acetinada',(.72,.74,.72),.3,.45)
dark,_ = material('sombra veneziana',(.095,.105,.10),.8)
steel,p = material('inox escovado',(.48,.50,.52),.32,.85)
for socket in p.inputs:
    if socket.name in ('Anisotropic','Anisotropic IOR Level'):
        socket.default_value=.45
glass,p = material('vidro incolor transparente',(.83,.9,.92),.08)
p.inputs['Transmission Weight'].default_value=1
p.inputs['IOR'].default_value=1.45
glass.diffuse_color=(.65,.78,.8,.2)
glass.surface_render_method='DITHERED'
stone,p=material('marmore claro peitoris',(.7,.72,.71),.28)
nt=stone.node_tree
n=nt.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value=5; n.inputs['Detail'].default_value=4; n.inputs['Roughness'].default_value=.75
r=nt.nodes.new('ShaderNodeValToRGB'); r.color_ramp.elements[0].position=.36;r.color_ramp.elements[0].color=(.24,.27,.29,1);r.color_ramp.elements[1].position=.55;r.color_ramp.elements[1].color=(.78,.79,.75,1)
nt.links.new(n.outputs['Fac'],r.inputs[0]);nt.links.new(r.outputs[0],p.inputs['Base Color'])
floor,p=material('granito cinza piso',(.3,.31,.3),.4)
nt=floor.node_tree;n=nt.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=220
r=nt.nodes.new('ShaderNodeValToRGB');r.color_ramp.elements[0].color=(.09,.10,.09,1);r.color_ramp.elements[1].color=(.42,.44,.42,1)
nt.links.new(n.outputs['Fac'],r.inputs[0]);nt.links.new(r.outputs[0],p.inputs['Base Color'])

def bounds(o):
    vs=[I@o.matrix_world@v.co for v in o.data.vertices]
    return [(min(v[i] for v in vs),max(v[i] for v in vs)) for i in range(3)]

def box(name, pos, size, mat, bevel=.006):
    x,y,z=[v/2 for v in size]
    vs=[(-x,-y,-z),(-x,-y,z),(-x,y,-z),(-x,y,z),(x,-y,-z),(x,-y,z),(x,y,-z),(x,y,z)]
    me=bpy.data.meshes.new(name);me.from_pydata(vs,[],[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]);me.update()
    o=bpy.data.objects.new('LAC R30B | '+name,me);col.objects.link(o)
    o.location=R@Vector(pos);o.rotation_euler.z=theta;o.data.materials.append(mat)
    o['boas_location_id']='elevador-lacerda';o['boas_role']='visual_detail';o['reference_status']='partial'
    if bevel:
        m=o.modifiers.new('Arestas de acabamento','BEVEL');m.width=bevel;m.segments=2
    return o

changes=[]
for o in targets:
    if o.type!='MESH':continue
    name=o.name.lower()
    if not o.data.materials:continue
    # Materiais novos só nos objetos deste marco; não alterar materiais compartilhados da cidade.
    for i,m in enumerate(o.data.materials):
        if not m:continue
        old=m.name.lower();new=None
        if 'vidro' in old or 'janela fum' in name:new=glass
        elif 'peitoril interno' in name:new=stone
        elif any(t in old for t in ['reboco','marfim']):new=ivory
        elif 'caixilho' in old or ('passarela' in name and 'esquadria' in old):new=frame
        elif 'inox' in old:new=steel
        if name.startswith('funcional') and any(t in name for t in ['lateral inferior','lateral superior','porta cabine','botoeira']):new=steel
        if name.startswith('funcional') and name.endswith(' piso'):new=floor
        if 'peitoril interno' in name:new=stone
        if new:o.data.materials[i]=new;changes.append(o.name)
    if any(t in name for t in ['cornija','consolo','peitoril','batente','moldura','pilastra']) and not any(m.type=='BEVEL' for m in o.modifiers):
        m=o.modifiers.new('R30B | acabamento arestas','BEVEL');m.width=.018;m.segments=3

# Venezianas nas aberturas existentes: ritmo e posição herdados, sem deslocar a torre.
for o in sorted(targets,key=lambda o:o.name):
    if o.type!='MESH' or not o.name.startswith(('TORRE | janela técnica','TORRE | fresta tecnica superior')):continue
    bb=bounds(o); dx,dy,dz=[b-a for a,b in bb]
    if min(dx,dy)>.3:continue
    o.data.materials.clear();o.data.materials.append(dark)
    thin=0 if dx<dy else 1
    center=[(a+b)/2 for a,b in bb]
    center[thin]+=(-1 if center[thin]<(-68.698 if thin==0 else 4.245) else 1)*.052
    count=max(3,round(dz/.14))
    for j in range(count):
        pos=center.copy();pos[2]=bb[2][0]+(j+.5)*dz/count
        size=[dx*.93,dy*.93,.045];size[thin]=.062
        box(o.name+' | lamela %02d'%j,pos,size,frame,.004)

# Friso em losangos observado sob as janelas da galeria de 2025.
for o in sorted(targets,key=lambda o:o.name):
    if o.type!='MESH' or not o.name.startswith(('GALERIA | vidro frontal','GALERIA | vidro lateral')):continue
    bb=bounds(o);thin=0 if bb[0][1]-bb[0][0]<bb[1][1]-bb[1][0] else 1;long=1-thin
    center=[sum(b)/2 for b in bb];a,b=bb[long];z=70.48
    # Preservar janela e elevar apenas sua borda inferior para dar lugar ao friso opaco.
    for v in o.data.vertices:
        w=o.matrix_world@v.co
        if w.z<70.7:w.z=70.72;v.co=o.matrix_world.inverted()@w
    center[2]=z;size=[.12,.12,.43];size[long]=b-a
    box('Galeria | fundo friso '+o.name,center,size,dark)
    count=max(1,round((b-a)/.6));step=(b-a)/count
    for j in range(count):
        for sign in [-1,1]:
            p=center.copy();p[long]=a+(j+.5)*step;p[thin]+=-.085 if center[thin]<(-68.698 if thin==0 else 4.245) else .085
            size=[.065,.065,.055];size[long]=math.hypot(step,.37)
            bar=box('Galeria | cruzeta %s %02d %s'%(o.name,j,sign),p,size,ivory,.004)
            local=Matrix.Rotation(sign*math.atan2(.37,step),4,'Y' if long==0 else 'X')
            bar.rotation_euler=(R@local).to_euler()

bpy.context.scene['lacerda_revision']='R30B.01 | refinamento visual parcial'
bpy.context.scene['lacerda_reference_status']='partial; fotos Commons 2025 catalogadas; sem levantamento metrologico'
dest=ROOT/'blender/salvador_lacerda_r30b01_refinamento.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(dest))
report={'source':'blender/salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a11_pedestrian_nav.blend','revision':str(dest.relative_to(ROOT)).replace('\\','/'),'materials_updated_objects':len(set(changes)),'added_visual_objects':len(col.objects),'geography_changed':False,'existing_animation_changed':False,'status':'partial','references':['elevador-lacerda-detail-ded7c75d401c','elevador-lacerda-oblique_left-ca2c56d9b78b']}
(OUT/'refinement_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(report,ensure_ascii=False))
