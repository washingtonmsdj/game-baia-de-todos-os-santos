"""Correção local V07: raios da chapa, continuidade das normais e pintura fosca.
MCP visível, sem render offline. Preserva V06; não altera medidas dos eixos.
"""
import bpy,bmesh,math,ast,json,hashlib
from pathlib import Path
from mathutils import Vector
repo=Path(__file__).resolve().parents[2];scene=bpy.context.scene
assert Path(bpy.data.filepath).name=='marrom_v06.blend' and not bpy.data.is_dirty
out=repo/'blender/assets/vehicles/rondesp-pickup/marrom_v07.blend'
assert not out.exists()
root=scene.objects['RDP01_ROOT | viatura']
for fn in ast.parse((repo/'automation/blender/rebuild_hilux_reference_v06.py').read_text(encoding='utf-8')).body:
    if isinstance(fn,ast.FunctionDef) and fn.name in ['interp','sidewidth','arch','fronttop']:
        exec(compile(ast.Module(body=[fn],type_ignores=[]),'<profile>','exec'),globals())

def width(u):return .9275-.093*u**3-.032*math.sin(math.pi*u)
def upper(u,v):
    f=2*v-1;x=width(u)*f
    yf=-2.435+.49*abs(f)**3.5;y=yf+(-.975-yf)*u
    z=fronttop(.9275*f)*(1-u)+1.303*u+.025*math.sin(math.pi*u)
    z+=.024*(1-f*f)*u+.008*math.exp(-((abs(f)-.63)/.12)**2)*math.sin(math.pi*u)
    z-=.025*abs(f)**8*math.sin(math.pi*u)
    return x,y,z
hood=scene.objects['RDP01 | HILUX06 | Capô e ombros estampados']
for i in range(67):
    for j in range(73):hood.data.vertices[i*73+j].co=upper(i/66,j/72)
hood.data.update()
for side in [-1,1]:
    ob=scene.objects['RDP01 | HILUX06 | Para-lama dianteiro '+str(side)]
    for i in range(73):
        u=i/72;y=-1.945+.970*u;lo=arch(y,-1.43);hi=upper(u,0)[2]
        for j in range(31):
            t=j/30
            # Seção curvilínea: ombro arredonda até tangenciar o capô.
            z=lo+(hi-lo)*math.sin(t*math.pi/2)
            r=max(0,(t-.65)/.35)
            x=sidewidth(y,z)*(1-r)+width(u)*r
            ob.data.vertices[i*31+j].co=(side*x,y,z)
    ob.data.update()
    seam=scene.objects['RDP01 | HILUX06 | Junta capô '+str(side)]
    for j,p in enumerate(seam.data.splines[0].points):p.co=(*upper(j/60,(side*.84+1)/2),1)

# Normais comuns na borda dos dois painéis, mantendo objetos e espessuras próprios.
# Não há deslocamento para esconder uma fenda: o limite geométrico é compartilhado.
hood_normals=[v.normal.copy() for v in hood.data.vertices]
for side,column in [(-1,0),(1,72)]:
    ob=scene.objects['RDP01 | HILUX06 | Para-lama dianteiro '+str(side)]
    ns=[v.normal.copy() for v in ob.data.vertices]
    for i in range(73):
        u=i/72;hi=round(u*66)*73+column;fi=i*31+30
        n=(hood_normals[hi]+ns[fi]).normalized()
        if n.z<0:n=-n
        ns[fi]=n
    ob.data.normals_split_custom_set_from_vertices(ns)
    ob['boas_v07_change']='Seção com raio no ombro, limite coincidente com capô; não escala global'

# Suavização do teto em Y e fechamento do encaixe superior do para-brisa.
roof=scene.objects['RDP01 | HILUX06 | Teto curvatura dupla']
for v in roof.data.vertices:
    if v.co.y<-.26:
        t=max(0,min(1,(-.26-v.co.y)/.065))
        # Limite dianteiro liga-se à vedação superior em Z=1.767.
        target=1.767+.010*(1-(abs(v.co.x)/.711)**2)
        v.co.z=v.co.z*(1-t)+target*t
roof.data.update()

# Raios maiores e normais de acabamento das peças moldadas.
for ob in scene.objects:
    if ob.type!='MESH':continue
    if any(s in ob.name for s in ['Espelho ','Maçaneta','Bolso maçaneta','Portinhola capota']):
        for mod in ob.modifiers:
            if mod.type=='BEVEL':mod.segments=6
        for p in ob.data.polygons:p.use_smooth=True
        if not any(m.type=='WEIGHTED_NORMAL' for m in ob.modifiers):ob.modifiers.new('Normais de acabamento','WEIGHTED_NORMAL')

# A referência da viatura tem acabamento marrom fosco e faixas de baixo contraste.
palette=[(.108,.063,.045,1),(.174,.102,.073,1),(.218,.141,.105,1)]
for label in ['Pintura marrom Rondesp','Camuflagem marrom candidata']:
    mat=bpy.data.materials['RDP01 | '+label];mat.diffuse_color=palette[1]
    bs=mat.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Roughness'].default_value=.55;bs.inputs['Metallic'].default_value=0
    bs.inputs['Coat Weight'].default_value=.10;bs.inputs['Coat Roughness'].default_value=.4
    if not bs.inputs['Base Color'].is_linked:bs.inputs['Base Color'].default_value=palette[1]
    for n in mat.node_tree.nodes:
        if n.type=='VALTORGB':
            count=len(n.color_ramp.elements)
            for i,e in enumerate(n.color_ramp.elements):e.color=palette[round(2*i/max(1,count-1))]
    mat['boas_finish_status']='Cores interpretadas das fotos 3.1110; desenho exato da camuflagem continua pendente'
poly=bpy.data.materials['RDP01 | Polímero preto'];bs=poly.node_tree.nodes.get('Principled BSDF')
bs.inputs['Roughness'].default_value=.53;bs.inputs['Metallic'].default_value=0

scene.name='VIATURA | Rondesp Hilux marrom v07'
scene['boas_review_status']='candidate: V07, correção local de raios e acabamento; não aprovado como réplica'
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            s=area.spaces.active;s.shading.type='SOLID';s.shading.color_type='MATERIAL';s.shading.light='STUDIO';s.shading.studio_light='paint.sl';s.shading.show_cavity=False;s.overlay.show_overlays=False
            s.region_3d.view_rotation=(Vector((0,.12,1))-Vector((-7,-8,3.2))).to_track_quat('-Z','Y');s.region_3d.view_location=(0,.12,1);s.region_3d.view_distance=7
bpy.context.view_layer.update()
bpy.data.libraries.write(str(out),{scene},path_remap='RELATIVE',fake_user=True,compress=True)
report={'asset_id':'vehicle-rondesp-pickup','file':out.relative_to(repo).as_posix(),'scene':scene.name,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'parent':'blender/assets/vehicles/rondesp-pickup/marrom_v06.blend','status':'candidate','changes':['ombros dos para-lamas arredondados e contínuos com capô','encaixe teto/para-brisa','acabamento das peças moldadas','pintura menos brilhante e camuflagem de menor contraste'],'wheelbase_m':3.085,'dimensions_source':'world/vehicles/hilux-dimensions.json','runtime_exported':False,'pending':['fidelidade final de carroceria','brasão PMBA','camuflagem exata','animação e runtime']}
(repo/'docs/reports/blender/rondesp_marrom_v07.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def reopen():bpy.ops.wm.open_mainfile(filepath=str(out));return None
bpy.app.timers.register(reopen,first_interval=.5)
print(json.dumps({'saved':report['file'],'status':'candidate'}))
