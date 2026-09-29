"""Correções locais de encaixe, acessos e materiais na sessão Blender visível."""
import bpy, math, bmesh, json
from pathlib import Path
from mathutils import Vector
s=bpy.context.scene
assert s.name=='ONIBUS | Torino 31065 v04'
root=bpy.data.objects['TOR04_ROOT']; base=Path(bpy.data.filepath).parent
target=base/'onibus_torino_31065_v05_encaixes.blend'
assert not target.exists(), 'Preservar revisão existente'
def mat(name,color,metal=0,rough=.4):
    m=bpy.data.materials.new('TOR05 | '+name);m.diffuse_color=(*color,1);m.use_nodes=True
    p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
    return m
white=mat('Revestimento interno branco',(.72,.75,.76),.18)
metal=mat('Espelhos degraus aluminio',(.5,.55,.59),.7,.3)
rubber=mat('Piso antiderrapante',(.065,.075,.083),0,.86)
yellow=bpy.data.materials['TOR04 | Amarelo ouro']
def mesh(name,vs,fs,material,collection='INTERIOR_ESBOCO'):
    me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.materials.append(material);me.update()
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    o=bpy.data.objects.new('TOR05 | '+name,me);bpy.data.collections['TOR04 | '+collection].objects.link(o);o.parent=root
    return o
def box(name,lo,hi,material,collection='INTERIOR_ESBOCO'):
    x,y,z=lo;X,Y,Z=hi
    return mesh(name,[(x,y,z),(X,y,z),(X,Y,z),(x,Y,z),(x,y,Z),(X,y,Z),(X,Y,Z),(x,Y,Z)],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],material,collection)
inter=bpy.data.collections['TOR04 | INTERIOR_ESBOCO'];inter.hide_render=False
for o in inter.objects:o.hide_render=False
# Remove somente peças provisórias que serão substituídas por acessos e recortes.
for o in list(inter.objects):
    if any(k in o.name for k in ('Piso corredor','Piso lado motorista','Piso lateral direito','Degrau entrada','Borda degrau','Caixa roda interna')):bpy.data.objects.remove(o,do_unlink=True)
Y=lambda u:6-(u-26)*12/1084
doors=[('Dianteira',Y(1077),Y(984)),('Central',Y(624),Y(519)),('Traseira',Y(270),Y(181))]
axles=[-3.70,2.14]
# Piso contínuo, com poços das escadas e recortes reais para as rodas.
xs=[-1.22,-.62,-.27,.62,1.22]
ys=sorted(set([-5.78,5.78]+[q for _,a,b in doors for q in (a,b)]+[q for c in axles for q in (c-.72,c+.72)]))
vs=[];fs=[]
for x,X in zip(xs,xs[1:]):
    for y,v in zip(ys,ys[1:]):
        cx=(x+X)/2;cy=(y+v)/2
        if cx<-.27 and any(a<cy<b for _,a,b in doors):continue
        if abs(cx)>.62 and any(abs(cy-c)<.72 for c in axles):continue
        n=len(vs);vs.extend([(x,y,.81),(X,y,.81),(X,v,.81),(x,v,.81)]);fs.append((n,n+1,n+2,n+3))
floor=mesh('Piso recortado para escadas e rodas',vs,fs,rubber)
bm=bmesh.new();bm.from_mesh(floor.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);bm.to_mesh(floor.data);bm.free()
sol=floor.modifiers.new('Espessura piso','SOLIDIFY');sol.thickness=.055;sol.offset=-1
for name,a,b in doors:
    # Primeiro patamar cobre o envelope das folhas; elevação só após o alcance dos pivôs.
    for i,(x,X,z) in enumerate([(-1.25,-.59,.4212),(-.59,-.27,.6156)]):
        box(name+' patamar '+str(i+1),(x,a+.025,z-.04),(X,b-.025,z),rubber)
        box(name+' espelho '+str(i+1),(X-.018,a+.025,z),(X,b-.025,z+.1944),metal)
        box(name+' borda amarela '+str(i+1),(x,a+.025,z+.001),(x+.027,b-.025,z+.008),yellow)
    for side in (a+.01,b-.027):
        box(name+' fechamento lateral escada',( -1.23,side,.38),(-.27,side+.016,.81),white)
# As rodas permanecem dentro dos arcos, com face externa praticamente alinhada à carroceria.
for o in s.objects:
    if o.type=='EMPTY' and ('Dianteira roda ' in o.name or 'Traseira roda ' in o.name):
        o.location.x+=math.copysign(.065,o.location.x)
        o['folga_radial_nominal_m']=.105
# Caixas internas arqueadas independentes dos pneus e com tampas inboard.
for c in axles:
    for sign in (-1,1):
        rr=.675;z0=.558;angles=[math.pi*i/48 for i in range(49)]
        vs=[(sign*x,c+rr*math.cos(t),z0+rr*math.sin(t)) for x in (.615,1.29) for t in angles]
        fs=[(i,i+1,50+i,49+i) for i in range(48)]
        o=mesh('Caixa roda arco '+str((c,sign)),vs,fs,white)
        sol=o.modifiers.new('Chapa caixa roda','SOLIDIFY');sol.thickness=.018
        vs=[(sign*.615,c,z0)]+[(sign*.615,c+rr*math.cos(t),z0+rr*math.sin(t)) for t in angles]
        mesh('Caixa roda fechamento interno '+str((c,sign)),vs,[(0,i+1,i+2) for i in range(48)],white)
# Reposiciona somente o banco provisório que bloqueava a porta traseira.
for o in inter.objects:
    if '.019' in o.name and any(k in o.name for k in ('Banco','Apoio')):o.location.y+=1.15
    if 'Balaustre' in o.name and o.location.x<0 and abs(o.location.y-4)<.03:o.location.y=4.42
# Revestimento próprio nas faces internas geradas pela espessura das chapas.
for o in s.objects:
    if o.type!='MESH' or not o.name.startswith('TOR04'):continue
    if not any(k in o.name for k in ('Painel lateral','Chapa ao redor','chapa envolvente','retorno de canto','Teto transversal')):continue
    solids=[m for m in o.modifiers if m.type=='SOLIDIFY']
    if not solids:continue
    if o.data.users>1:o.data=o.data.copy()
    n=len(o.data.materials)
    for _ in range(n):o.data.materials.append(white)
    for m in solids:m.material_offset=n;m.material_offset_rim=n
# Cintas se encontram com o topo das janelas e a borda real do teto.
for o in s.objects:
    if 'Cinta superior' in o.name:
        o.dimensions.z=.26;o.location.z=2.895
        o.dimensions.x=.057
    if 'Faixa pintura curva' in o.name:
        # A faixa termina na face vertical: nenhum polígono acompanha o topo do teto.
        if o.data.users>1:o.data=o.data.copy()
        zs=[v.co.z for v in o.data.vertices];low=min(zs);high=max(zs)
        for v in o.data.vertices:
            v.co.x=math.copysign(1.256,v.co.x)
            v.co.z=2.86+(v.co.z-low)/(high-low)*.137
        o.data.update()
# Vidro fino com passagem de luz e reflexão Fresnel, visível também em Eevee.
g=next(m for m in bpy.data.materials if m.name.startswith('TOR04 | Vidro cinza'))
g.use_nodes=True;nodes=g.node_tree.nodes;nodes.clear();links=g.node_tree.links
out=nodes.new('ShaderNodeOutputMaterial');trans=nodes.new('ShaderNodeBsdfTransparent');trans.inputs[0].default_value=(.82,.9,.92,1)
p=nodes.new('ShaderNodeBsdfPrincipled');p.inputs['Base Color'].default_value=(.82,.9,.92,1);p.inputs['Metallic'].default_value=0;p.inputs['Roughness'].default_value=.085
f=nodes.new('ShaderNodeFresnel');f.inputs['IOR'].default_value=1.46
mix=nodes.new('ShaderNodeMixShader');links.new(f.outputs[0],mix.inputs[0]);links.new(trans.outputs[0],mix.inputs[1]);links.new(p.outputs[0],mix.inputs[2]);links.new(mix.outputs[0],out.inputs[0])
g.diffuse_color=(.3,.43,.46,.23)
if hasattr(g,'surface_render_method'):g.surface_render_method='DITHERED'
s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True
s.frame_set(65)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.shading.type='MATERIAL'
            area.spaces.active.region_3d.view_location=(0,0,1.5)
            area.spaces.active.region_3d.view_distance=15
root['revisao_encaixes']='v05: piso recortado, caixas de roda independentes, 3 escadas, revestimento interno, cinta contínua, faixas somente laterais e vidro transparente.'
s.name='ONIBUS | Torino 31065 v05'
bpy.ops.wm.save_as_mainfile(filepath=str(target),compress=True)
print(json.dumps({'arquivo':str(target),'portas_abertas_frame':65,'correcoes':'piso/rodas/escadas/revestimento/cinta/vidros/faixas'}))
