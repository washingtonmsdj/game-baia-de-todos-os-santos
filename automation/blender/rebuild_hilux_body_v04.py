"""Reconstrução métrica da carroceria Hilux, ao vivo na única janela MCP.

Chapas curvas por seções, aberturas coincidentes das lentes e painéis independentes.
Medidas nominais Toyota em hilux-dimensions.json; acessórios policiais candidatos.
"""
import bpy, bmesh, math, json, hashlib, ast
from pathlib import Path
from mathutils import Vector, Matrix

repo=Path(__file__).resolve().parents[2]
scene=bpy.context.scene
assert scene.name=='VIATURA | Rondesp picape marrom v03'
out=repo/'blender/assets/vehicles/rondesp-pickup/marrom_v04.blend'
assert not out.exists(), 'Preservar revisão existente.'
root=scene.objects['RDP01_ROOT | viatura']
groups=['CARROCERIA','PORTAS','CAPOTA','VIDROS','RODAS','CHASSIS','LUZES','ACABAMENTOS','INSCRICOES','APRESENTACAO']
collections={k:bpy.data.collections['RDP01 | '+k] for k in groups}
scope=dict(bpy=bpy,bmesh=bmesh,math=math,Vector=Vector,Matrix=Matrix,root=root,collections=collections)
for key,label in [('brown','Pintura marrom Rondesp'),('black','Polímero preto'),('steel','Aço preto rodas'),('silver','Metal acetinado'),('white','Inscrição branca'),('glass','Vidro fumê'),('clear','Lentes transparentes'),('red','Lentes vermelhas')]:
    scope[key]=bpy.data.materials['RDP01 | '+label]
tree=ast.parse((repo/'automation/blender/create_rondesp_pickup_v01.py').read_text(encoding='utf-8'))
for name in ['mesh','box','tube','cylinder','parent_keep']:
    fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name)
    exec(compile(ast.Module(body=[fn],type_ignores=[]),'<hilux-helpers>','exec'),scope)
mesh,box,tube,cylinder,parent_keep=[scope[k] for k in ['mesh','box','tube','cylinder','parent_keep']]
brown,black,steel,silver,white,glass,clear,red=[scope[k] for k in ['brown','black','steel','silver','white','glass','clear','red']]
paint=bpy.data.materials['RDP01 | Camuflagem marrom candidata']
dims=json.loads((repo/'world/vehicles/hilux-dimensions.json').read_text(encoding='utf-8'))
axles=(-1.43,1.655); wz=dims['tires']['nominal_unloaded_radius_m']
front=-2.43; rear=front+dims['dimensions_m']['length']

# Elimina chapas substituídas explicitamente; preserva mecânica, equipamentos e inscrições.
remove_prefixes=['Coluna ','Borracha para-brisa','Limpador para-brisa','Palheta para-brisa','Haste espelho','Retrovisor carcaça','Espelho retrovisor','Maçaneta ','Borda caixa roda','Junta capô','Farol ','Farol 2024','Refletor farol','DRL farol','Grade Hilux','Barra grade','Rebaixo canto','Auxiliar canto','Placa suporte dianteiro']
for ob in list(scene.objects):
    group=next((g for g in groups if collections[g] in ob.users_collection),None)
    delete=(group=='CARROCERIA' and ob!=root) or (group=='PORTAS' and ob.type!='EMPTY')
    delete |= group=='VIDROS' and 'capota' not in ob.name.lower()
    delete |= any(ob.name.startswith('RDP01 | '+p) for p in remove_prefixes)
    delete |= ob.name.startswith('RDP03 | ') and group in ['CARROCERIA','PORTAS','VIDROS']
    if delete:bpy.data.objects.remove(ob,do_unlink=True)

def curve(values,t):
    if t<=values[0][0]:return values[0][1]
    if t>=values[-1][0]:return values[-1][1]
    for i in range(len(values)-1):
        x,a=values[i]; y,b=values[i+1]
        if x<=t<=y:
            k=(t-x)/(y-x)
            m0=(b-values[max(0,i-1)][1])/(y-values[max(0,i-1)][0])
            m1=(values[min(len(values)-1,i+2)][1]-a)/(values[min(len(values)-1,i+2)][0]-x)
            return (2*k**3-3*k*k+1)*a+(k**3-2*k*k+k)*(y-x)*m0+(-2*k**3+3*k*k)*b+(k**3-k*k)*(y-x)*m1

def part(name,vs,fs,mat=brown,group='CARROCERIA',parent=None,thickness=.016):
    ob=mesh('HILUX04 | '+name,vs,fs,mat,group,smooth=True,thickness=thickness)
    if parent:parent_keep(ob,parent)
    ob['boas_geometry_basis']='Toyota Hilux 2024 STD; seções interpretadas das referências laterais e fotos 3.1110'
    ob['boas_dimensions_source']='world/vehicles/hilux-dimensions.json'
    return ob

def grid(name,fn,nu,nv,mat=brown,group='CARROCERIA',parent=None):
    vs=[fn(i/nu,j/nv) for i in range(nu+1) for j in range(nv+1)]
    fs=[(i*(nv+1)+j,(i+1)*(nv+1)+j,(i+1)*(nv+1)+j+1,i*(nv+1)+j+1) for i in range(nu) for j in range(nv)]
    return part(name,vs,fs,mat,group,parent)

def rounded(poly,ratio=.10,steps=7):
    pts=[]
    for i,p in enumerate(poly):
        cur=Vector(p);a=cur+(Vector(poly[i-1])-cur)*ratio;b=cur+(Vector(poly[(i+1)%len(poly)])-cur)*ratio
        for k in range(steps):
            t=k/(steps-1);pts.append((1-t)**2*a+2*t*(1-t)*cur+t*t*b)
    return pts

def ring(name,poly,point,mat=brown,group='CARROCERIA',parent=None,inset=.92):
    center=sum(poly,Vector((0,0)))/len(poly)
    inn=[center+(p-center)*inset for p in poly];n=len(poly)
    frame=part(name,[point(p) for p in poly+inn],[(i,(i+1)%n,n+(i+1)%n,n+i) for i in range(n)],mat,group,parent)
    return inn

def arch(y,axle):
    r=.475;d=abs(y-axle)
    if d>=r:return .53
    # Arco ligeiramente achatado no topo; lábios integram-se ao painel, sem tubo sobreposto.
    return max(.53,wz+.49*math.sqrt(max(0,1-(d/r)**2)))

def sidewidth(y,z):
    # Ombro, concavidade inferior e vinco contínuo de portas na lateral real.
    w=curve([(.50,.835),(.58,.853),(.68,.867),(.79,.878),(.96,.900),(1.06,.908),(1.16,.902),(1.28,.862),(1.35,.846)],z)
    bulge=max(math.exp(-((y-axles[0])/.57)**4),math.exp(-((y-axles[1])/.56)**4))
    w+=bulge*.019*math.exp(-((z-.91)/.28)**2)
    return min(.9275,w)

def hoodtop(y):return curve([(-2.43,1.15),(-2.18,1.20),(-1.70,1.25),(-1.15,1.29),(-.96,1.29)],y)

# Para-lamas e caçamba com arqueamento transversal e bordas reais dos poços.
for side in (-1,1):
    for start,end,label,axle in [(-2.115,-.975,'Para-lama dianteiro',axles[0]),(1.17,rear-.045,'Lateral caçamba',axles[1])]:
        def fn(u,t,start=start,end=end,axle=axle):
            y=start+(end-start)*u; low=arch(y,axle)
            top=hoodtop(y)+.012 if axle==axles[0] else 1.285-.018*math.exp(-((y-rear)/.10)**2)
            z=low+(top-low)*t
            x=sidewidth(y,z)
            if axle==axles[0] and y<-1.97:x-=.018*((-1.97-y)/.145)**2
            if axle==axles[1] and y>rear-.19:x-=.032*((y-rear+.19)/.19)**2
            return (side*x,y,z)
        grid(f'{label} {side:+}',fn,100,18,paint)
        # Retorno da chapa na caixa de roda; espessura e profundidade, não preenchimento.
        pts=[];vs=[]
        for i in range(81):
            y=axle-.475+.95*i/80; z=arch(y,axle)
            x=sidewidth(y,z)
            vs.extend([(side*x,y,z),(side*(x-.05),y,z-.014)])
            pts.append((side*(x+.001),y,z))
        part(f'Retorno arco {axle} {side}',vs,[(2*i,2*i+1,2*i+3,2*i+2) for i in range(80)],paint,thickness=.008)
        tube(f'HILUX04 | Vinco arco {axle} {side}',pts,.004,paint)

# Portas abauladas, recorte inferior arredondado e vinco seguindo a carroceria.
for side in (-1,1):
    for label,start,end in [('dianteira',-.965,.105),('traseira',.114,1.16)]:
        pivot=scene.objects[f'RDP01 | Pivô porta {label} {side:+}']
        def door(u,t):
            z=.545+.739*t
            corner=.10*(1-t)**10
            y=start+corner+(end-start-2*corner)*u
            return (side*sidewidth(y,z),y,z)
        grid(f'Porta estampada {label} {side}',door,36,24,paint,'PORTAS',pivot)
        edge=[door(i/30,0) for i in range(31)]+[door(1,j/20) for j in range(1,21)]+[door(1-i/30,1) for i in range(1,31)]+[door(0,1-j/20) for j in range(1,21)]
        seam=tube(f'HILUX04 | Junta porta {label} {side}',edge,.0022,black,'PORTAS',True);parent_keep(seam,pivot)
        # Contorno exterior da janela é o aro metálico da porta, não uma janela quadrada.
        poly=rounded(([(-.955,1.287),(-.43,1.714),(-.24,1.757),(.084,1.759),(.088,1.286)] if label=='dianteira' else [(.13,1.286),(.13,1.759),(.89,1.751),(1.063,1.69),(1.123,1.51),(1.02,1.286)]),.12)
        def pnt(p,offset=0):
            y,z=p
            x=curve([(1.28,.862),(1.45,.826),(1.63,.787),(1.76,.758)],z)
            return (side*(x+offset),y,z)
        inn=ring(f'Aro porta {label} {side}',poly,pnt,brown,'PORTAS',pivot,.915)
        pane=part(f'Vidro porta {label} {side}',[pnt(p,-.008) for p in inn],[tuple(range(len(inn)))],glass,'VIDROS',pivot,.004)
        seal=tube(f'HILUX04 | Vedação {label} {side}',[pnt(p,.001) for p in inn],.009,black,'VIDROS',True);parent_keep(seal,pivot)
        # Maçaneta alongada, junto à linha do ombro; bolso abaulado próprio.
        y=end-.16
        pocket=box(f'HILUX04 | Rebaixo maçaneta {label} {side}',(side*.910,y,1.135),(.020,.20,.062),brown,'PORTAS',.025);parent_keep(pocket,pivot)
        handle=box(f'HILUX04 | Maçaneta {label} {side}',(side*.928,y,1.145),(.032,.155,.036),black,'PORTAS',.014);parent_keep(handle,pivot)
    # Soleira e colunas modeladas por superfícies; montantes se unem ao teto.
    grid(f'Soleira curva {side}',lambda u,t:(side*(.84+.015*math.sin(t*math.pi)),-.90+2.03*u,.51+.035*t),40,4,paint)
    tube(f'HILUX04 | Coluna A {side}',[(side*.863,-.97,1.29),(side*.807,-.71,1.51),(side*.762,-.40,1.73)],.027,brown)
    grid(f'Coluna B {side}',lambda u,t:(side*(.862-.104*t),.086+.045*u,1.284+.475*t),3,16,black)
    # Painel C largo e arqueado na traseira da cabine, seguindo o perfil de fábrica.
    grid(f'Coluna C {side}',lambda u,t:(side*(.857-.099*t),curve([(0,1.17),(.5,1.16),(1,.987)],t)-(.065+.04*math.sin(t*math.pi))*u,1.28+.485*t),5,24,brown)

# Teto com raio longitudinal contínuo e arqueamento transversal; altura stock 1.815 m.
def roof(u,t):
    y=-.42+1.52*u; z=curve([(-.42,1.733),(-.25,1.791),(.20,1.801),(.70,1.798),(.95,1.777),(1.10,1.69)],y)
    w=curve([(-.42,.754),(-.25,.769),(.65,.775),(1.10,.762)],y)
    v=-1+2*t;return (w*v,y,z+.014*(1-v*v)-.024*abs(v)**8)
grid('Teto cabine curvatura dupla',roof,44,32)
# Para-brisa curvo, borda coincidente com o teto e base do capô.
def windshield(u,t):
    v=-1+2*u; w=.829*(1-t)+.749*t
    y=-.995*(1-t)-.431*t-.035*(1-v*v)*math.sin(math.pi*t)
    z=1.306*(1-t)+1.738*t+.010*(1-v*v)
    return (w*v,y,z)
grid('Para-brisa curvado Hilux',windshield,32,22,glass,'VIDROS')
border=[windshield(i/32,0) for i in range(33)]+[windshield(1,j/22) for j in range(1,23)]+[windshield(1-i/32,1) for i in range(1,33)]+[windshield(0,1-j/22) for j in range(1,23)]
tube('HILUX04 | Vedação para-brisa',border,.015,black,'VIDROS',True)
grid('Painel cowl',lambda u,t:((-.85+1.70*u),-1.06+.07*t,1.292+.014*t),32,3,black)
for x in (-.58,.20):
    tube('HILUX04 | Limpador '+str(x),[(x,-1.004,1.316),(x+.18,-.95,1.365),(x+.43,-.93,1.39)],.009,black)
    tube('HILUX04 | Palheta '+str(x),[(x+.1,-.951,1.367),(x+.47,-.921,1.403)],.011,black)
grid('Parede traseira cabine',lambda u,t:(-.845+1.69*u,1.157-.048*t,.57+1.10*t),32,24)

# Capô: frente envolvente em U, duas linhas de estampagem e bordas conectadas aos para-lamas.
def hood(u,t):
    v=-1+2*u; xf=.867*v
    yf=front+.027+.297*abs(v)**3
    y=yf+(-1.059-yf)*t
    z=hoodtop(y)+.027*(1-v*v)+.006*math.exp(-((abs(v)-.57)/.095)**2)
    return (xf,y,z)
grid('Capô Hilux contínuo',hood,48,44,paint)
for side in (-1,1):
    tube('HILUX04 | Junta capô '+str(side),[hood((side+1)/2,j/44) for j in range(45)],.0028,black)

# Frente: superfícies envelopantes; bordas dos recortes e dos faróis compartilham as coordenadas.
def nosepoint(x,z,offset=0):
    y=front+.30*(abs(x)/.9275)**3+.040*math.exp(-((z-.60)/.15)**2)+offset
    return (x,y,z)
def lightbottom(x):return curve([(.50,1.056),(.55,1.044),(.69,1.030),(.81,1.036),(.91,1.13)],x)
def lighttop(x):return curve([(.50,1.179),(.69,1.201),(.83,1.211),(.91,1.22)],x)
for side in (-1,1):
    grid(f'Para-choque curvo canto {side}',lambda u,t:nosepoint(side*(.48+.43*u),.515+(lightbottom(.48+.43*u)-.515)*t),32,24,paint)
    grid(f'Pálpebra farol {side}',lambda u,t:nosepoint(side*(.50+.41*u),lighttop(.50+.41*u)+.034*t),32,3,paint)
    lp=rounded([(.505,1.174),(.67,1.201),(.832,1.211),(.910,1.219),(.892,1.111),(.805,1.036),(.68,1.028),(.544,1.041)],.055,5)
    point=lambda p,off=0:nosepoint(side*p.x,p.y,off)
    inn=ring(f'Farol encaixe {side}',lp,point,black,'LUZES',inset=.935)
    # Carcaça e refletores acompanham o plano envolvente; eliminam peças brancas flutuantes.
    part(f'Farol fundo {side}',[point(p,.020) for p in inn],[tuple(range(len(inn)))],black,'LUZES',thickness=.007)
    lens=part(f'Farol lente {side}',[point(p,-.006) for p in inn],[tuple(range(len(inn)))],clear,'LUZES',thickness=.004)
    for x,z,w,h in [(.607,1.10,.113,.078),(.754,1.13,.124,.08),(.847,1.15,.064,.05)]:
        reflector=rounded([(x-w/2,z-h/2),(x+w/2,z-h/2),(x+w/2,z+h/2),(x-w/2,z+h/2)],.23)
        part(f'Refletor integrado {side} {x}',[nosepoint(side*p.x,p.y,.010) for p in reflector],[tuple(range(len(reflector)))],silver,'LUZES',thickness=.003)
        tube(f'HILUX04 | Nervura refletor {side} {x}',[nosepoint(side*(x-w*.32),z,.004),nosepoint(side*x,z+.022,.004),nosepoint(side*(x+w*.32),z,.004)],.004,white,'LUZES')
    tube(f'HILUX04 | Linha superior farol {side}',[nosepoint(side*x,lighttop(x)-.026,-.009) for x in [.55,.60,.66,.72,.78,.83,.87]],.006,white,'LUZES')
    # Rebaixo vertical característico STD; canto inferior arredondado.
    poly=rounded([(.732,.972),(.783,.970),(.802,.665),(.76,.617),(.683,.651),(.69,.707),(.728,.711)],.16)
    part(f'Rebaixo vertical para-choque {side}',[nosepoint(side*p.x,p.y,-.008) for p in poly],[tuple(range(len(poly)))],black,'ACABAMENTOS',thickness=.008)
    grid(f'Retorno lateral para-choque {side}',lambda u,t:(side*(.88+.02*math.sin(u*math.pi)),-2.10+.24*u,.525+(.06+.36*t)*(1-.14*u)),18,14,paint)
    # Retrovisor em volumes arredondados, base triangular no canto da porta.
    poly=rounded([(-.957,1.298),(-.739,1.483),(-.728,1.298)],.08)
    part(f'Base retrovisor {side}',[(side*.866,p.x,p.y) for p in poly],[tuple(range(len(poly)))],black,'ACABAMENTOS')
    tube('HILUX04 | Haste retrovisor '+str(side),[(side*.867,-.78,1.346),(side*1.015,-.77,1.379)],.026,black)
    box('HILUX04 | Carcaça retrovisor '+str(side),(side*1.025,-.76,1.413),(.19,.255,.14),black,bevel=.052)
    box('HILUX04 | Lente retrovisor '+str(side),(side*1.027,-.637,1.417),(.153,.007,.091),silver,bevel=.025)

# Grade superior separada da entrada inferior, moldura preta fiel à versão STD.
gp=rounded([(-.505,1.181),(.505,1.181),(.56,1.01),(.485,.845),(-.485,.845),(-.56,1.01)],.05)
inn=ring('Moldura grade superior',gp,lambda p:nosepoint(p.x,p.y,-.010),black,'ACABAMENTOS',inset=.89)
part('Fundo grade superior',[nosepoint(p.x,p.y,.012) for p in inn],[tuple(range(len(inn)))],black,'ACABAMENTOS')
for j in range(7):
    z=.895+.036*j;w=.448+.04*math.sin(j/6*math.pi)
    tube('HILUX04 | Aleta grade '+str(j),[nosepoint(-w+2*w*k/24,z,-.012) for k in range(25)],.010,steel)
grid('Centro para-choque',lambda u,t:nosepoint(-.49+.98*u,.50+.345*t),36,18,paint)
lower=rounded([(-.40,.573),(.40,.573),(.51,.742),(.49,.793),(-.49,.793),(-.51,.742)],.09)
part('Entrada inferior',[nosepoint(p.x,p.y,-.009) for p in lower],[tuple(range(len(lower)))],black,'ACABAMENTOS')
for j in range(3):tube('HILUX04 | Aleta inferior '+str(j),[nosepoint(-.41+.82*k/24,.616+j*.057,-.018) for k in range(25)],.006,steel)
box('HILUX04 | Porta placa',(0,front-.036,.800),(.40,.022,.115),black,bevel=.012)
# Emblema Toyota em três elipses, geométrico e discreto.
for name,rx,rz in [('externo',.054,.037),('vertical',.022,.036),('horizontal',.052,.018)]:
    tube('HILUX04 | Toyota '+name,[nosepoint(rx*math.cos(i*2*math.pi/64),1.027+rz*math.sin(i*2*math.pi/64),-.033) for i in range(64)],.004,silver,'ACABAMENTOS',True)

# Ajusta a caçamba, capota e equipamentos à distância e altura stock, sem escala global.
bed_delta=rear-2.65
for ob in list(scene.objects):
    group=next((g for g in groups if collections[g] in ob.users_collection),None)
    if group=='CAPOTA' or ('capota' in ob.name.lower() and group=='VIDROS'):
        if ob.type=='MESH':
            for v in ob.data.vertices:
                # Dados de chapa são em espaço do veículo; primitivas ficam locais ao centro.
                if ob.location.length<.01:
                    v.co.y=1.16+(v.co.y-1.075)*(rear-.045-1.16)/(2.61-1.075);v.co.z-=.11
            if ob.location.length>=.01:ob.location.y+=bed_delta;ob.location.z-=.11
        elif ob.type=='CURVE':
            for sp in ob.data.splines:
                for p in sp.points:
                    p.co.y=1.16+(p.co.y-1.075)*(rear-.045-1.16)/(2.61-1.075);p.co.z-=.11
    elif group in ['LUZES','INSCRICOES','ACABAMENTOS','CHASSIS'] and ob.type!='EMPTY':
        if ob.location.y>2.4:ob.location.y+=bed_delta
        elif ob.type=='MESH' and ob.location.length<.01:
            for v in ob.data.vertices:
                if v.co.y>2.4:v.co.y+=bed_delta
                elif v.co.y<-2.55:v.co.y+=.29
        elif ob.type=='CURVE':
            for sp in ob.data.splines:
                for p in sp.points:
                    if p.co.y>2.4:p.co.y+=bed_delta
                    elif p.co.y<-2.55:p.co.y+=.29
    # Roof-mounted equipment follows the new stock roof, retaining its own estimated dimensions.
    if any(s in ob.name for s in ['Barra vermelha','Base sinalizador','LED vermelho barra','suporte teto','Antena rádio']):
        if ob.type=='MESH':ob.location.z-=.11
        elif ob.type=='CURVE':
            for sp in ob.data.splines:
                for p in sp.points:p.co.z-=.11
    if ob.name.startswith('RDP01 | Estribo lateral'):
        ob.data.materials.clear();ob.data.materials.append(silver)
    if ob.name.startswith('RDP01 | POLÍCIA MILITAR ') or ob.name.startswith('RDP01 | Telefone 190 '):ob.location.x=math.copysign(.913,ob.location.x)

# Capota policial continua candidata, agora com superfícies realmente curvas nos ombros.
cap=scene.objects.get('RDP01 | Capota fechada reforçada')
if cap:bpy.data.objects.remove(cap,do_unlink=True)
def canopy(u,t):
    y=1.17+(rear-.050-1.17)*u
    angle=math.pi*t
    x=.889*math.cos(angle)
    z=1.195+.68*math.sin(angle)**.48
    # Ombro arredondado, topo suavemente plano; não seção octogonal.
    z=min(z,1.864)+.006*math.sin(math.pi*u)
    return (x,y,z)
grid('Capota arredondada',canopy,36,64,brown,'CAPOTA')
for y in (1.17,rear-.05):
    outline=[canopy(0 if y==1.17 else 1,j/64) for j in range(65)]
    part('Fechamento capota '+str(y),outline,[tuple(range(len(outline)))],brown,'CAPOTA')
grid('Tampa caçamba curvada',lambda u,t:((-.87+1.74*u),rear-.053+.007*math.cos((u-.5)*math.pi),.565+.67*t),32,22,paint)
grid('Borda caixa caçamba',lambda u,t:((-.862+1.724*u),1.18+.025*t,1.285),28,3,paint)

# Rodas métricas: pneu nominal 265/65R17, eixo mantido com 3.085 m entre centros.
for side in (-1,1):
    for ai,y in enumerate(axles):
        pivot=scene.objects[f'RDP01 | Eixo giro roda {ai} {side:+}']
        pivot.location=(side*.795,y,wz)
        for ob in pivot.children:
            # Os filhos estão em coordenadas locais à roda desde a revisão V02.
            ob.scale.y*=wz/.405;ob.scale.z*=wz/.405
        pivot['boas_tire_nominal']='265/65 R17';pivot['boas_wheelbase_m']=3.085

scene.name='VIATURA | Rondesp Hilux marrom v04'
scene['boas_dimension_status']='Nominais Toyota confirmadas; seções de carroceria e acessórios interpretados das fotos'
scene['boas_pending_details']=json.dumps(['brasão PMBA detalhado','dimensões dos acessórios policiais','mapa exato camuflagem','animação das portas'],ensure_ascii=False)
scene['boas_reference']='rondesp-31110-front; rondesp-31110-rear; hilux-gx-factory-side; hilux-2024-std-dealer-side'
bpy.context.view_layer.update()
scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.light='STUDIO';scene.display.shading.studiolight_rotate_z=.3
scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True
scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.display.shading.show_specular_highlight=True
scene.display.shading.background_type='WORLD';scene.world.color=(.20,.20,.20)
scene.view_settings.view_transform='Standard';scene.view_settings.exposure=0
scene.render.resolution_x=1200;scene.render.resolution_y=750;scene.render.resolution_percentage=100
imgdir=repo/'artifacts/vehicles/rondesp';imgdir.mkdir(parents=True,exist_ok=True)
views=[('frente',(-7,-7,3.5)),('lateral',(-9,0,1.15)),('frontal',(0,-10,1.35)),('traseira',(-7,7,3.1))]
for name,pos in views:
    scene.camera.location=pos;scene.camera.rotation_euler=(Vector((0,.18,1.02))-scene.camera.location).to_track_quat('-Z','Y').to_euler()
    scene.camera.data.type='ORTHO';scene.camera.data.ortho_scale=6.7
    scene.render.filepath=str(imgdir/f'v04-{name}-geometria.png');bpy.ops.render.render(write_still=True)
scene.camera.location=views[0][1];scene.camera.rotation_euler=(Vector((0,.18,1.02))-scene.camera.location).to_track_quat('-Z','Y').to_euler()
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            s=area.spaces.active;s.shading.type='SOLID';s.shading.color_type='MATERIAL';s.overlay.show_overlays=False
            s.region_3d.view_rotation=scene.camera.rotation_euler.to_quaternion();s.region_3d.view_location=(0,.18,1);s.region_3d.view_distance=7
bpy.data.libraries.write(str(out),{scene},path_remap='RELATIVE',fake_user=True,compress=True)
report={'file':out.relative_to(repo).as_posix(),'scene':scene.name,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'asset_id':'vehicle-rondesp-pickup','status':'candidate','dimensions_nominal':dims['dimensions_m'],'tires_nominal':dims['tires'],'body_reference':'Toyota Hilux 2024 STD Power Pack; seções interpretadas, não escaneamento','accessories_status':'candidate; sem levantamento das dimensões policiais','body_endpoints_y_m':[front,rear],'wheelbase_measured_m':axles[1]-axles[0],'objects':len(scene.objects),'corrections':['carroceria reconstruída por superfícies curvas','frente com encaixes de faróis coincidentes','grade STD e para-choque separados','teto e janelas corrigidos pela vista lateral de fábrica','caçamba e capota arredondadas','rodas nas medidas nominais'],'pending':json.loads(scene['boas_pending_details'])}
(repo/'docs/reports/blender/rondesp_marrom_v04.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def reopen():
    bpy.ops.wm.open_mainfile(filepath=str(out));return None
bpy.app.timers.register(reopen,first_interval=.5)
