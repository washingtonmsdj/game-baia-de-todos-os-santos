"""Picape Rondesp candidata: cena própria, edição na única janela Blender via MCP.

Referência principal: fotografia enviada pelo usuário (baixa resolução).
Dimensões são parâmetros de modelagem candidatos, não levantamento da viatura.
Não altera ônibus, cidade, produção ou arquivos anteriores.
"""
import bpy
import bmesh
import math
import json
import hashlib
from pathlib import Path
from mathutils import Vector, Matrix

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'blender/assets/vehicles/rondesp-pickup/marrom_v01.blend'
REPORT = ROOT / 'docs/reports/blender/rondesp_marrom_v01.json'
if OUT.exists():
    raise RuntimeError('Revisão existente: preservar e usar um passe de refinamento.')

scene = bpy.data.scenes.new('VIATURA | Rondesp picape marrom v01')
bpy.context.window.scene = scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1
scene['boas_asset_id'] = 'vehicle-rondesp-pickup'
scene['boas_status'] = 'candidate'
scene['boas_front_axis'] = '-Y'
scene['boas_reference'] = 'rondesp-pickup-user-front-left'
scene['boas_dimension_status'] = 'candidate; proporções fotográficas, sem medida da viatura'
collections = {}
for name in ['CARROCERIA', 'PORTAS', 'CAPOTA', 'VIDROS', 'RODAS', 'CHASSIS', 'LUZES', 'ACABAMENTOS', 'INSCRICOES', 'APRESENTACAO']:
    c = bpy.data.collections.new('RDP01 | ' + name)
    scene.collection.children.link(c)
    collections[name] = c
collections['APRESENTACAO']['boas_export_role'] = 'presentation_only'
root = bpy.data.objects.new('RDP01_ROOT | viatura', None)
collections['CARROCERIA'].objects.link(root)
root['boas_asset_id'] = 'vehicle-rondesp-pickup'
root['boas_reference_status'] = 'partial'

def linear(v):
    return v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4

def material(name, rgb, metal=0, rough=.4, transmission=0, emission=0):
    m = bpy.data.materials.new('RDP01 | ' + name)
    m.use_nodes = True
    rgba = tuple(linear(v) for v in rgb) + (1,)
    m.diffuse_color = rgba
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = rgba
    p.inputs['Metallic'].default_value = metal
    p.inputs['Roughness'].default_value = rough
    p.inputs['Transmission Weight'].default_value = transmission
    p.inputs['IOR'].default_value = 1.45
    if name.startswith('Pintura'):
        p.inputs['Coat Weight'].default_value = .32
        p.inputs['Coat Roughness'].default_value = .24
    if emission:
        p.inputs['Emission Color'].default_value = rgba
        p.inputs['Emission Strength'].default_value = emission
    return m

brown = material('Pintura marrom Rondesp', (.47, .33, .27), .05, .48)
black = material('Polímero preto', (.045, .048, .05), .03, .35)
rubber = material('Borracha pneus', (.026, .028, .029), 0, .63)
steel = material('Aço preto rodas', (.12, .125, .13), .75, .3)
silver = material('Metal acetinado', (.53, .56, .58), .8, .28)
white = material('Inscrição branca', (.91, .92, .88), 0, .55)
glass = material('Vidro fumê', (.13, .20, .23), 0, .15, .83)
clear = material('Lentes transparentes', (.78, .84, .86), .05, .12, .68)
red = material('Lentes vermelhas', (.7, .015, .025), .08, .18, .24)
amber = material('Setas âmbar', (.96, .36, .045), .05, .22, .15)
interior = material('Interior carvão', (.10, .10, .11), 0, .7)

def attach(o, group, mat=None, parent=root):
    for c in list(o.users_collection):
        c.objects.unlink(o)
    collections[group].objects.link(o)
    if mat:
        o.data.materials.append(mat)
    if parent:
        # Neste gerador, objetos novos são locais à origem do veículo. Usar
        # basis evita perder rotações/posições ainda não avaliadas pelo depsgraph.
        basis = o.matrix_basis.copy()
        o.parent = parent
        o.matrix_parent_inverse = parent.matrix_basis.inverted()
        o.matrix_basis = basis
    o['boas_asset_id'] = 'vehicle-rondesp-pickup'
    o['boas_component'] = group.lower()
    return o

def mesh(name, verts, faces, mat, group='CARROCERIA', bevel=0, smooth=False, thickness=0):
    me = bpy.data.meshes.new('RDP01 | ' + name)
    me.from_pydata(verts, [], faces)
    me.update()
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new('RDP01 | ' + name, me)
    collections[group].objects.link(o)
    o.parent = root
    o.data.materials.append(mat)
    if thickness:
        mod = o.modifiers.new('Espessura real', 'SOLIDIFY')
        mod.thickness = thickness
    if bevel:
        mod = o.modifiers.new('Arestas de fabricação', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    o['boas_asset_id'] = 'vehicle-rondesp-pickup'
    o['boas_component'] = group.lower()
    return o

def box(name, loc, size, mat, group='ACABAMENTOS', bevel=.015):
    # API de dados: evita reavaliar toda a cena em cada bloco de pneu/parafuso.
    x,y,z=(v/2 for v in size)
    verts=[(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)]
    faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    me=bpy.data.meshes.new('RDP01 | '+name)
    me.from_pydata(verts,[],faces)
    o=bpy.data.objects.new('RDP01 | '+name,me)
    collections[group].objects.link(o)
    o.location=loc
    o.parent=root
    me.materials.append(mat)
    o['boas_asset_id']='vehicle-rondesp-pickup'
    o['boas_component']=group.lower()
    if bevel:
        m = o.modifiers.new('Bordas arredondadas', 'BEVEL')
        m.width = bevel
        m.segments = 3
    return o

def tube(name, pts, radius, mat=black, group='ACABAMENTOS', closed=False):
    cu = bpy.data.curves.new('RDP01 | ' + name, 'CURVE')
    cu.dimensions = '3D'
    cu.resolution_u = 12
    cu.bevel_depth = radius
    cu.bevel_resolution = 3
    s = cu.splines.new('POLY')
    s.points.add(len(pts)-1)
    for p, co in zip(s.points, pts):
        p.co = (*co, 1)
    s.use_cyclic_u = closed
    o = bpy.data.objects.new('RDP01 | ' + name, cu)
    collections[group].objects.link(o)
    cu.materials.append(mat)
    o.parent = root
    return o

def cylinder(name, loc, radius, depth, mat, group='RODAS', axis='X', vertices=48):
    verts=[]
    for z in (-depth/2,depth/2):
        for i in range(vertices):
            a=2*math.pi*i/vertices
            verts.append((radius*math.cos(a),radius*math.sin(a),z))
    faces=[tuple(range(vertices-1,-1,-1)),tuple(range(vertices,2*vertices))]
    faces += [(i,(i+1)%vertices,(i+1)%vertices+vertices,i+vertices) for i in range(vertices)]
    me=bpy.data.meshes.new('RDP01 | '+name); me.from_pydata(verts,[],faces)
    o=bpy.data.objects.new('RDP01 | '+name,me)
    collections[group].objects.link(o); o.location=loc; o.parent=root; me.materials.append(mat)
    if axis == 'X':
        o.rotation_euler[1] = math.pi/2
    elif axis == 'Y':
        o.rotation_euler[0] = math.pi/2
    m = o.modifiers.new('Usinagem', 'BEVEL')
    m.width = .003
    m.segments = 2
    for p in o.data.polygons:
        p.use_smooth = len(p.vertices) == 4
    return o

def loft(name, rings, mat, group='CARROCERIA', cap=True, smooth=True):
    n = len(rings[0]); verts = [v for ring in rings for v in ring]
    faces = []
    for j in range(len(rings)-1):
        for k in range(n):
            faces.append((j*n+k, j*n+(k+1)%n, (j+1)*n+(k+1)%n, (j+1)*n+k))
    if cap:
        faces += [tuple(range(n-1, -1, -1)), tuple((len(rings)-1)*n+k for k in range(n))]
    return mesh(name, verts, faces, mat, group, smooth=smooth)

# Modelo métrico candidato. Frente -Y; chão Z=0. Sem transform global de escala.
AXLES = (-1.43, 1.655)
WHEEL_Z = .415
ARCH_R = .48
door_roots = {}
for side in (-1, 1):
    for part, y in [('dianteira', -.83), ('traseira', .08)]:
        e = bpy.data.objects.new(f'RDP01 | Pivô porta {part} {side:+}', None)
        collections['PORTAS'].objects.link(e)
        e.location = (side*.92, y, 1)
        e.parent = root
        e['boas_hinge_axis'] = 'Z'
        e['boas_opening_status'] = 'prepared_not_tested'
        door_roots[(side, part)] = e

def parent_keep(o, e):
    basis = o.matrix_basis.copy()
    o.parent = e
    o.matrix_parent_inverse = e.matrix_basis.inverted()
    o.matrix_basis = basis

def arch_bottom(y):
    for axle in AXLES:
        d = y - axle
        if abs(d) < ARCH_R:
            return max(.57, WHEEL_Z + math.sqrt(ARCH_R**2-d*d))
    return .57

def width(y):
    if y < -2.35:
        return .89 + .037*(y+2.7)/.35
    if y > 2.35:
        return .927-.022*(y-2.35)/.29
    return .927

def shoulder(y):
    return 1.22 if y < -2.2 else (1.29 if y < -.95 else 1.31)

# Painéis inferiores delimitados por portas, com recorte real dos quatro arcos.
spans = [(-2.70,-.85,'Para-lama dianteiro'),(-.85,.07,'Porta dianteira'),(.07,1.04,'Porta traseira'),(1.04,2.63,'Caçamba')]
for side in (-1,1):
    for start, end, label in spans:
        ys = [start+.003 + (end-start-.006)*i/60 for i in range(61)]
        verts = []
        for y in ys:
            low = arch_bottom(y)
            top = shoulder(y)
            for f, dx in [(0,-.035),(.15,-.008),(.62,0),(.84,.003),(1,-.01)]:
                verts.append((side*(width(y)+dx), y, low+(top-low)*f))
        faces=[(i*5+k,i*5+k+1,(i+1)*5+k+1,(i+1)*5+k) for i in range(60) for k in range(4)]
        group='PORTAS' if label.startswith('Porta') else 'CARROCERIA'
        o=mesh(f'{label} {side:+}',verts,faces,brown,group,smooth=True,thickness=.026)
        if group=='PORTAS':
            part='dianteira' if 'dianteira' in label else 'traseira'
            parent_keep(o,door_roots[(side,part)])
    for ai, y in enumerate(AXLES):
        pts=[]
        for i in range(61):
            t=math.pi*i/60
            yy=y-ARCH_R*math.cos(t)
            zz=WHEEL_Z+ARCH_R*math.sin(t)
            if zz>=.57:
                pts.append((side*.954,yy,zz))
        tube(f'Borda caixa roda {ai} {side:+}',pts,.031,brown,'CARROCERIA')
        # Forro interno segue o arco, não fecha o espaço ocupado pelo pneu.
        verts=[]
        for i in range(49):
            t=math.pi*i/48
            for x in (.66,.937):
                verts.append((side*x,y-.485*math.cos(t),WHEEL_Z+.485*math.sin(t)))
        mesh(f'Forro arqueado roda {ai} {side:+}',verts,[(2*i,2*i+1,2*i+3,2*i+2) for i in range(48)],black,'CHASSIS',thickness=.006)
    box(f'Estribo lateral {side:+}',(side*.94,.11,.49),(.18,1.94,.075),black,bevel=.025)
    for y in (-.65,.76):
        box(f'Suporte estribo {side:+} {y}',(side*.76,y,.47),(.29,.07,.07),steel,'CHASSIS')
    for y in AXLES:
        box(f'Para-barro {side:+} {y}',(side*.88,y+.43,.39),(.26,.035,.38),rubber,'CHASSIS',.006)

# Capô esculpido: centro abaulado, ombros e vincos longitudinais.
hood=[]
for y,z,w in [(-2.64,1.09,.80),(-2.43,1.22,.90),(-1.45,1.33,.91),(-1.02,1.36,.88)]:
    hood.append([(-w,y,z-.025),(-w*.77,y,z+.01),(-w*.45,y,z+.035),(0,y,z+.045),(w*.45,y,z+.035),(w*.77,y,z+.01),(w,y,z-.025)])
mesh('Capô conformado', [v for r in hood for v in r], [(i*7+k,i*7+k+1,(i+1)*7+k+1,(i+1)*7+k) for i in range(3) for k in range(6)], brown,thickness=.024,smooth=True)
for side in (-1,1):
    tube(f'Junta capô {side:+}',[(side*.81,-2.52,1.13),(side*.87,-2.35,1.245),(side*.86,-1.05,1.345)],.003,black)

# Cabine com aberturas: só montantes, teto e vidros; não uma caixa tampando janelas.
roof=[]
for y,w,z in [(-.44,.75,1.83),(-.26,.77,1.88),(.62,.78,1.90),(.94,.76,1.86),(1.04,.75,1.78)]:
    roof.append([(-w,y,z-.045),(-w*.7,y,z+.006),(0,y,z+.03),(w*.7,y,z+.006),(w,y,z-.045)])
mesh('Teto cabine dupla',[v for r in roof for v in r],[(i*5+k,i*5+k+1,(i+1)*5+k+1,(i+1)*5+k) for i in range(4) for k in range(4)],brown,thickness=.026,smooth=True)

def side_x(side,z,offset=0):
    return side*(.923 - max(0,z-1.31)*.267 + offset)

def side_glass(side, label, poly, parent=None):
    # Faixa exterior da porta e vedação; vidro recuado em relação ao caixilho.
    cy=sum(y for y,z in poly)/len(poly); cz=sum(z for y,z in poly)/len(poly)
    inner=[(cy+(y-cy)*.90,cz+(z-cz)*.83) for y,z in poly]
    verts=[(side_x(side,z),y,z) for y,z in poly+inner]
    n=len(poly)
    frame=mesh(f'Caixilho {label} {side:+}',verts,[(i,(i+1)%n,n+(i+1)%n,n+i) for i in range(n)],brown,'PORTAS',thickness=.021)
    pts=[(side_x(side,z,.002),y,z) for y,z in inner]
    seal=tube(f'Vedação {label} {side:+}',pts,.012,black,'VIDROS',True)
    pane=mesh(f'Vidro {label} {side:+}',[(side_x(side,z,-.007),y,z) for y,z in inner],[tuple(range(n))],glass,'VIDROS',thickness=.005)
    pane['boas_glass'] = 'tinted_transmission'
    if parent:
        for ob in [frame,seal,pane]: parent_keep(ob,parent)

front_poly=[(-.865,1.31),(-.37,1.845),(.065,1.86),(.065,1.31)]
back_poly=[(.083,1.31),(.083,1.86),(.93,1.81),(1.035,1.31)]
for side in (-1,1):
    side_glass(side,'porta dianteira',front_poly,door_roots[(side,'dianteira')])
    side_glass(side,'porta traseira',back_poly,door_roots[(side,'traseira')])
    tube(f'Coluna A {side:+}',[(side*.91,-.99,1.34),(side*.76,-.39,1.85)],.042,brown,'CARROCERIA')
    box(f'Coluna B {side:+}',(side*.833,.074,1.587),(.05,.045,.54),black)
    tube(f'Coluna C {side:+}',[(side*.915,1.04,1.31),(side*.76,.94,1.81)],.04,brown,'CARROCERIA')
    for part,y in [('dianteira',-.07),('traseira',.76)]:
        h=box(f'Maçaneta {part} {side:+}',(side*.938,y,1.225),(.024,.15,.033),black,bevel=.011)
        parent_keep(h,door_roots[(side,part)])
    stalk=tube(f'Haste espelho {side:+}',[(side*.90,-.68,1.37),(side*1.04,-.70,1.40)],.03)
    mirror=box(f'Retrovisor carcaça {side:+}',(side*1.04,-.68,1.46),(.19,.26,.15),black,bevel=.048)
    box(f'Espelho retrovisor {side:+}',(side*1.045,-.544,1.46),(.155,.007,.10),silver,bevel=.025)

# Para-brisa com abaulamento nos dois sentidos e acabamento independente.
verts=[]
for j in range(13):
    t=j/12
    w=.85*(1-t)+.738*t
    for i in range(25):
        u=-1+2*i/24
        y=-1.00*(1-t)-.416*t - .040*(1-u*u)*math.sin(math.pi*t)
        z=1.372*(1-t)+1.829*t + .016*(1-u*u)
        verts.append((w*u,y,z))
mesh('Para-brisa curvo',verts,[(j*25+i,j*25+i+1,(j+1)*25+i+1,(j+1)*25+i) for j in range(12) for i in range(24)],glass,'VIDROS',thickness=.005,smooth=True)
border=verts[:25]+[verts[j*25+24] for j in range(1,13)]+list(reversed(verts[12*25:12*25+24]))+[verts[j*25] for j in range(11,0,-1)]
tube('Borracha para-brisa',border,.018,black,'VIDROS',True)
box('Corta fogo',(0,-.78,1.06),(1.70,.07,.40),interior,'CHASSIS')
box('Painel interno',(0,-.70,1.29),(1.56,.30,.12),interior,'CHASSIS',.04)
for x in (-.58,.27):
    tube('Limpador para-brisa '+str(x),[(x,-1.008,1.384),(x+.19,-.94,1.43),(x+.47,-.91,1.454)],.008,black)
    tube('Palheta para-brisa '+str(x),[(x+.15,-.928,1.44),(x+.49,-.901,1.464)],.012,black)
box('Piso cabine',(0,.1,.68),(1.71,1.89,.055),interior,'CHASSIS')
for x in (-.43,.43):
    box('Assento dianteiro '+str(x),(x,-.09,.91),(.48,.46,.14),interior,'CHASSIS',.07)
    back=box('Encosto dianteiro '+str(x),(x,.13,1.21),(.48,.13,.59),interior,'CHASSIS',.065)
    back.rotation_euler[0]=-.13
    box('Apoio cabeça '+str(x),(x,.16,1.55),(.25,.13,.17),interior,'CHASSIS',.04)
box('Banco traseiro',(0,.70,.91),(1.30,.38,.14),interior,'CHASSIS',.06)
box('Encosto traseiro',(0,.94,1.19),(1.3,.11,.47),interior,'CHASSIS',.05)
box('Parede traseira cabine',(0,1.018,1.22),(1.69,.055,1.03),brown,'CARROCERIA')

# Capota fechada alta: ombros chanfrados, laterais maciças e nervuras vistas na foto.
canopy=[]
for y in (1.075,1.16,2.46,2.61):
    canopy.append([(-.91,y,1.285),(-.895,y,1.64),(-.75,y,1.94),(-.66,y,1.98),(.66,y,1.98),(.75,y,1.94),(.895,y,1.64),(.91,y,1.285)])
loft('Capota fechada reforçada',canopy,brown,'CAPOTA',smooth=False)
for side in (-1,1):
    tube(f'Junta capota base {side:+}',[(side*.916,1.07,1.30),(side*.916,2.61,1.30)],.006,black,'CAPOTA')
    for y in (1.19,1.88,2.48):
        tube(f'Nervura capota {side:+} {y}',[(side*.902,y,1.31),(side*.900,y+.05,1.65),(side*.751,y+.05,1.946)],.020,brown,'CAPOTA')
    tube(f'Reforço diagonal capota {side:+}',[(side*.904,1.22,1.35),(side*.895,1.66,1.62),(side*.78,1.88,1.88)],.018,brown,'CAPOTA')
box('Tampa traseira caçamba',(0,2.626,.94),(1.79,.045,.69),brown,'CARROCERIA',.035)
box('Para-choque traseiro',(0,2.68,.52),(1.85,.15,.16),black,bevel=.035)

# Frente contornada, grade, para-choque e faróis angulares separados.
rings=[]
for y,w in [(-2.69,.84),(-2.61,.915),(-2.50,.927)]:
    rings.append([(-w,y,.59),(-w,y,1.10),(-w*.75,y,1.16),(w*.75,y,1.16),(w,y,1.10),(w,y,.59)])
loft('Máscara dianteira',rings,brown,cap=True,smooth=False)
mesh('Grade superior trapezoidal',[(-.59,-2.705,.90),(-.67,-2.70,1.095),(.67,-2.70,1.095),(.59,-2.705,.90)],[(0,1,2,3)],black,'ACABAMENTOS',thickness=.012)
for z,w in [(1.085,.65),(1.027,.64),(.97,.60)]:
    tube('Friso grade '+str(z),[(-w,-2.721,z),(0,-2.735,z-.007),(w,-2.721,z)],.009,silver)
mesh('Entrada ar inferior',[(-.58,-2.709,.65),(-.62,-2.709,.79),(.62,-2.709,.79),(.58,-2.709,.65)],[(0,1,2,3)],black,'ACABAMENTOS',thickness=.018)
for i in range(12):
    x=-.54+i*.098
    box('Lâmina entrada ar '+str(i),(x,-2.731,.719),(.01,.018,.13),steel,bevel=.002)
for side in (-1,1):
    # Lentes prolongam-se sobre os para-lamas, como no perfil fornecido.
    outline=[(side*.605,-2.722,1.082),(side*.862,-2.705,1.119),(side*.920,-2.49,1.176),(side*.926,-2.34,1.175),(side*.902,-2.40,1.082),(side*.68,-2.686,1.010)]
    mesh(f'Farol carcaça {side:+}',outline,[tuple(range(6))],black,'LUZES',thickness=.035)
    cx=sum(p[0] for p in outline)/6; cy=sum(p[1] for p in outline)/6; cz=sum(p[2] for p in outline)/6
    inset=[(cx+(x-cx)*.89,y-.004,cz+(z-cz)*.76) for x,y,z in outline]
    mesh(f'Farol lente angular {side:+}',inset,[tuple(range(6))],clear,'LUZES',thickness=.006)
    cylinder(f'Projetor farol {side:+}',(side*.766,-2.724,1.068),.035,.012,silver,'LUZES','Y')
    tube(f'Filete farol {side:+}',[(side*.68,-2.731,1.081),(side*.861,-2.711,1.115),(side*.912,-2.49,1.153)],.009,white,'LUZES')
    box(f'Farol neblina moldura {side:+}',(side*.753,-2.676,.726),(.14,.035,.16),black,'LUZES',.045)
    cylinder(f'Farol neblina lente {side:+}',(side*.753,-2.702,.726),.043,.012,clear,'LUZES','Y')
    box(f'Lanterna traseira {side:+}',(side*.84,2.655,1.01),(.115,.035,.39),red,'LUZES',.025)
    box(f'Lanterna ré {side:+}',(side*.84,2.676,1.024),(.095,.008,.065),clear,'LUZES',.008)
box('Placa suporte dianteiro',(0,-2.772,.596),(.40,.022,.11),black,bevel=.009)

# Quebra-mato preto, com tubos e suportes reais, sem cobrir os faróis.
for x in (-.54,.54):
    tube('Montante quebra-mato '+str(x),[(x,-2.57,.46),(x,-2.88,.58),(x,-2.88,1.035),(x,-2.85,1.085)],.029)
    box('Base quebra-mato '+str(x),(x,-2.73,.49),(.065,.29,.045),steel,'CHASSIS')
tube('Arco central quebra-mato',[(-.54,-2.85,1.085),(-.49,-2.87,1.13),(.49,-2.87,1.13),(.54,-2.85,1.085)],.029)
tube('Travessa quebra-mato',[(-.82,-2.85,.69),(-.54,-2.88,.68),(.54,-2.88,.68),(.82,-2.85,.69)],.025)
for side in (-1,1):
    tube(f'Proteção externa quebra-mato {side:+}',[(side*.54,-2.87,.77),(side*.88,-2.79,.79),(side*.93,-2.74,.93),(side*.86,-2.72,1.005),(side*.58,-2.85,1.005)],.021)

# Sinalizador vermelho no teto, suportes, módulos e vidro próprios.
for x in (-.47,.47):
    box('Suporte giroflex '+str(x),(x,.04,1.977),(.08,.15,.055),black,'LUZES')
box('Base barra sinalizadora',(0,.04,2.01),(1.09,.24,.043),black,'LUZES',.028)
box('Barra vermelha',(0,.04,2.058),(1.06,.22,.064),red,'LUZES',.026)
for x in (-.45,-.30,-.15,.15,.30,.45):
    box('Módulo refletor '+str(x),(x,-.07,2.054),(.09,.018,.035),silver,'LUZES',.003)

# Chassis e rodas com origens no eixo, pneu de perfil, aro vazado e porcas.
for x in (-.51,.51):
    box('Longarina '+str(x),(x,.05,.455),(.10,4.25,.135),steel,'CHASSIS')
for y in AXLES:
    cylinder('Eixo '+str(y),(0,y,WHEEL_Z),.062,1.56,steel,'CHASSIS')
    box('Diferencial '+str(y),(0,y,WHEEL_Z),(.25,.20,.21),steel,'CHASSIS',.07)

def revolved(name, side, y, profile, mat, parent=None):
    verts=[]; n=80
    for dx,r in profile:
        for i in range(n):
            a=2*math.pi*i/n
            verts.append((side*(.825+dx),y+math.sin(a)*r,WHEEL_Z+math.cos(a)*r))
    faces=[(j*n+i,j*n+(i+1)%n,((j+1)%len(profile))*n+(i+1)%n,((j+1)%len(profile))*n+i) for j in range(len(profile)) for i in range(n)]
    o=mesh(name,verts,faces,mat,'RODAS',smooth=True)
    if parent: parent_keep(o,parent)
    return o

for side in (-1,1):
    for ai,y in enumerate(AXLES):
        pivot=bpy.data.objects.new(f'RDP01 | Eixo giro roda {ai} {side:+}',None)
        collections['RODAS'].objects.link(pivot)
        pivot.location=(side*.825,y,WHEEL_Z)
        pivot.parent=root
        pivot['boas_rotation_axis']='X'
        profile=[(-.133,.218),(-.150,.29),(-.131,.365),(-.104,.395),(-.072,.405),(.072,.405),(.104,.395),(.131,.365),(.15,.29),(.133,.218)]
        revolved(f'Pneu {ai} {side:+}',side,y,profile,rubber,pivot)
        revolved(f'Aro borda {ai} {side:+}',side,y,[(.115,.20),(.146,.20),(.151,.21),(.139,.222),(.110,.222),(.103,.213)],steel,pivot)
        for radius in (.285,.32,.355):
            prof=[(.142,radius-.002),(.144,radius),(.142,radius+.002),(.140,radius)]
            revolved(f'Relevo lateral pneu {ai} {side:+} {radius}',side,y,prof,rubber,pivot)
        # Aro de aço com dez aberturas reais entre os braços.
        for k in range(10):
            a=2*math.pi*k/10
            verts=[]
            for r,half,dx in [(.072,.20,.129),(.16,.13,.112),(.201,.10,.143)]:
                for aa in (a-half,a+half):
                    verts.append((side*(.825+dx),y+math.sin(aa)*r,WHEEL_Z+math.cos(aa)*r))
            o=mesh(f'Braço aço aro {ai} {side:+} {k}',verts,[(0,1,3,2),(2,3,5,4)],steel,'RODAS',thickness=.012)
            parent_keep(o,pivot)
        hub=cylinder(f'Cubo roda {ai} {side:+}',(side*.979,y,WHEEL_Z),.070,.065,steel)
        parent_keep(hub,pivot)
        disc=cylinder(f'Disco freio {ai} {side:+}',(side*.916,y,WHEEL_Z),.173,.018,silver)
        parent_keep(disc,pivot)
        for k in range(6):
            a=2*math.pi*k/6
            nut=cylinder(f'Porca roda {ai} {side:+} {k}',(side*.968,y+math.sin(a)*.097,WHEEL_Z+math.cos(a)*.097),.011,.022,silver,vertices=6)
            parent_keep(nut,pivot)
        for k in range(56):
            a=2*math.pi*k/56
            for row,dx in enumerate((-.076,0,.076)):
                ob=box(f'Bloco banda pneu {ai} {side:+} {k} {row}',(side*(.825+dx),y+math.sin(a)*.403,WHEEL_Z+math.cos(a)*.403),(.063,.031,.012),rubber,'RODAS',.003)
                ob.rotation_euler[0]=-a
                parent_keep(ob,pivot)

# Letras legíveis da fotografia. Brasão detalhado e prefixo não inventados.
def side_text(label, text, side, y, z, size, mat=white):
    cu=bpy.data.curves.new('RDP01 | '+label,'FONT')
    cu.body=text; cu.align_x='CENTER'; cu.align_y='CENTER'
    cu.size=size; cu.extrude=.0003
    ob=bpy.data.objects.new('RDP01 | '+label,cu)
    collections['INSCRICOES'].objects.link(ob)
    # Texto cresce do fundo para a frente no lado esquerdo; normal aponta para fora.
    right=Vector((0,side,0)); up=Vector((0,0,1)); normal=right.cross(up)
    ob.matrix_world=Matrix(((right.x,up.x,normal.x,side*.941),(right.y,up.y,normal.y,y),(right.z,up.z,normal.z,z),(0,0,0,1)))
    cu.materials.append(mat); ob.parent=root
    return ob

for side in (-1,1):
    side_text('POLÍCIA MILITAR '+str(side),'POLÍCIA MILITAR',side,.16,.807,.139)
    side_text('Telefone 190 '+str(side),'190',side,-1.20,1.21,.080)
    # Só a borda circular confirmada pela imagem: interior do brasão é pendente.
    pts=[(side*.944,-.13+math.sin(a)*.083,1.064+math.cos(a)*.083) for a in [2*math.pi*k/64 for k in range(64)]]
    badge=tube('Contorno brasão pendente '+str(side),pts,.006,white,'INSCRICOES',True)
    badge['boas_detail_status']='pending; brasão não legível na referência fornecida'

scene['boas_pending_details']=json.dumps(['brasão PMBA legível','prefixo exato','vista traseira correspondente','confirmação de dimensões e ano'],ensure_ascii=False)

# Apresentação removível e câmera de comparação com a foto.
floor_mat=material('Piso estúdio',(.23,.25,.27),0,.85)
floor=box('Piso apresentação',(0,0,-.055),(200,200,.10),floor_mat,'APRESENTACAO',0)
floor.parent=None
world=bpy.data.worlds.new('RDP01 | Estúdio')
world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(.35,.42,.50,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.55
scene.world=world
for name,loc,power,size in [('Principal',(-4,-5,7),1800,6),('Preenchimento',(5,-1,5),1400,5),('Recorte',(0,5,6),1900,5)]:
    data=bpy.data.lights.new('RDP01 | '+name,'AREA'); data.energy=power; data.shape='DISK'; data.size=size
    ob=bpy.data.objects.new(data.name,data); collections['APRESENTACAO'].objects.link(ob); ob.location=loc
    ob.rotation_euler=(Vector((0,0,1))-ob.location).to_track_quat('-Z','Y').to_euler()
cam_data=bpy.data.cameras.new('RDP01 | Camera referência')
cam=bpy.data.objects.new(cam_data.name,cam_data)
collections['APRESENTACAO'].objects.link(cam)
cam.location=(-7.5,-7.8,3.65)
cam.rotation_euler=(Vector((0,0,1))-cam.location).to_track_quat('-Z','Y').to_euler()
cam_data.type='ORTHO'; cam_data.ortho_scale=6.65
scene.camera=cam
scene.render.engine='CYCLES'
scene.cycles.samples=24
scene.cycles.use_denoising=True
scene.render.resolution_x=1200; scene.render.resolution_y=800; scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX'
scene.render.image_settings.file_format='PNG'
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            space=area.spaces.active
            space.region_3d.view_rotation=(cam.rotation_euler.to_quaternion())
            space.region_3d.view_location=(0,0,1)
            space.region_3d.view_distance=7.5
            space.region_3d.view_perspective='PERSP'
            space.shading.type='MATERIAL'
            space.shading.studiolight_rotate_z=.6
            space.overlay.show_overlays=False

text=bpy.data.texts.new('RDP01 | Fonte e limites')
text.write('Bay of All Saints — viatura Rondesp candidata. Fonte: fotografia enviada pelo usuário.\nCabine dupla, capota fechada, pintura marrom, estribos, rodas pretas e quebra-mato.\nEixos, folhas de porta, lentes e componentes separados. Dimensões candidatas.\nBrasão detalhado, prefixo e traseira permanecem pendentes; não há aprovação final.\nFrente -Y, metros, origem no centro longitudinal/chão. APRESENTACAO não exportável.\n')
scene['boas_authoring_notes']=text.as_string()
bpy.context.view_layer.update()
OUT.parent.mkdir(parents=True,exist_ok=True)
bpy.data.libraries.write(str(OUT),{scene},path_remap='RELATIVE',fake_user=True,compress=True)
report={
    'asset_id':'vehicle-rondesp-pickup','status':'candidate','file':OUT.relative_to(ROOT).as_posix(),
    'scene':scene.name,'sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),
    'reference_id':'rondesp-pickup-user-front-left','dimensions_status':'candidate_not_measured',
    'parameters_m':{'body_length':5.335,'body_width':1.854,'wheelbase':3.085,'tire_radius':.405},
    'vehicle_objects':sum(len(c.objects) for n,c in collections.items() if n!='APRESENTACAO'),
    'collections':list(collections),'door_pivots':4,'wheel_pivots':4,
    'window_apertures':'cabine sem sólido obstruindo os vidros','glass':'Principled transmission 0.83',
    'pending':json.loads(scene['boas_pending_details']),
    'preserved':'ônibus azul aberto anteriormente; fontes existentes não sobrescritas',
    'runtime_integration':False,'visual_review':'pending','reopened':'pending'
}
REPORT.parent.mkdir(parents=True,exist_ok=True)
REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
