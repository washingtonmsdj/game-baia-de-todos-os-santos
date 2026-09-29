"""Refino externo Torino 31065 a partir das quatro vistas fornecidas pelo usuário.
Executar somente via MCP na janela Blender existente. Não altera a cidade.
As dimensões são proporções de modelagem, não medição certificada do veículo.
"""
import bpy, math, json
from pathlib import Path
from mathutils import Vector, Matrix
from math import sin, cos, pi, sqrt

BASE = Path(bpy.data.filepath).parent
OUT = BASE / 'onibus_torino_31065_v04.blend'
assert 'onibus_torino_31065_v03' in bpy.data.filepath, 'Carregar primeiro a fonte v03'
assert not OUT.exists(), 'Preservar revisão já existente'
old = bpy.data.scenes['ONIBUS | Torino 31065 v03']
s = bpy.data.scenes.new('ONIBUS | Torino 31065 v04')
bpy.context.window.scene = s
s.unit_settings.system = 'METRIC'
s.unit_settings.scale_length = 1
s.render.fps = 30
s.frame_end = 120
groups = {}
for name in ['CARROCERIA','VIDROS','PORTA_DIANTEIRA','PORTA_CENTRAL','PORTA_TRASEIRA','RODAS_DIANTEIRAS','RODAS_TRASEIRAS','PNEUS','AROS','FAROIS','LANTERNAS','RETROVISORES','PARACHOQUES','ACABAMENTOS','INTERIOR_ESBOCO','REFERENCIA','APRESENTACAO']:
    c=bpy.data.collections.new('TOR04 | '+name);s.collection.children.link(c);groups[name]=c
root=bpy.data.objects.new('TOR04_ROOT',None);groups['CARROCERIA'].objects.link(root)
root['asset_id']='onibus-torino-31065'
root['reference']='Concept 601998669_839548205639278_4023019591288351440_n.jpg fornecido pelo usuário; vistas frontal, traseira e duas laterais'
root['reference_credit']='Desenho GABBB; EPSBUS; conforme assinatura na imagem fornecida'
root['reference_usage']='Referência do usuário; origem/licença externa não verificada'
root['dimensions_status']='Proporções derivadas visualmente do desenho; não medidas de fábrica'
root['front_axis']='-Y';root['door_side']='-X'
root['door_mechanism']='Duas folhas pivotantes para dentro; mecanismo interno interpretado, não documentado pela imagem'
root['review_frames']='1 fechado; 35 meia abertura; 65 aberto; 95 meia abertura; 120 fechado'

def mat(name,rgb,metal=0,rough=.4):
    m=bpy.data.materials.new('TOR04 | '+name);m.diffuse_color=(*rgb,1);m.use_nodes=True
    p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=(*rgb,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
    return m
yellow=mat('Amarelo ouro',(.94,.55,.008),.22,.29)
white=mat('Branco pintura',(.81,.83,.84),.16,.32)
black=mat('Borracha EPDM',(.009,.012,.015),0,.6)
dark=mat('Perfis anodizados',(.027,.031,.035),.55,.3)
glass=mat('Vidro cinza fumê',(.074,.102,.114),.28,.17)
next(n for n in glass.node_tree.nodes if n.type=='BSDF_PRINCIPLED').inputs['Coat Weight'].default_value=.35
silver=mat('Aro aço pintado',(.49,.52,.54),.75,.28)
chrome=mat('Alumínio polido',(.69,.73,.76),.86,.2)
rubber=mat('Pneu borracha',(.024,.027,.031),0,.83)
tread=mat('Fundo dos sulcos',(.009,.011,.012),0,.9)
red=mat('Lente vermelha',(.56,.009,.013),.18,.23)
amber=mat('Lente âmbar',(.96,.22,.006),.12,.22)
lens=mat('Lente cristal',(.77,.82,.83),.18,.17)
blue=mat('Azul acessibilidade',(.008,.049,.42),.1,.34)
green=mat('Verde faixa',(.008,.35,.076),.1,.36)
paper=mat('Branco sinalização',(.96,.96,.93),0,.45)

def link(o,name,group,ma=None,parent=None):
    o.name='TOR04 | '+name;groups[group].objects.link(o);o.parent=parent or root
    if ma:o.data.materials.append(ma)
    o['component']=group
    return o
def mesh(name,vs,fs,ma,group='CARROCERIA',smooth=False,thick=0):
    me=bpy.data.meshes.new('TOR04 | '+name);me.from_pydata(vs,[],fs);me.update()
    o=link(bpy.data.objects.new(name,me),name,group,ma)
    for p in me.polygons:p.use_smooth=smooth
    if thick:
        mod=o.modifiers.new('Espessura da chapa','SOLIDIFY');mod.thickness=thick;mod.offset=-1
    return o
def bevel(o,w=.015,n=3):
    m=o.modifiers.new('Raios de fabricação','BEVEL');m.width=w;m.segments=n
    return o
def box(name,p,d,ma,group='ACABAMENTOS',radius=.012):
    x,y,z=(v*.5 for v in d)
    vs=[(-x,-y,-z),(-x,-y,z),(-x,y,-z),(-x,y,z),(x,-y,-z),(x,-y,z),(x,y,-z),(x,y,z)]
    fs=[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]
    o=mesh(name,vs,fs,ma,group);o.location=p
    if radius:bevel(o,radius)
    return o
def curve(name,pts,ma,r=.009,group='ACABAMENTOS',closed=False):
    cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=1;cu.bevel_depth=r;cu.bevel_resolution=2
    sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
    for p,v in zip(sp.points,pts):p.co=(*v,1)
    sp.use_cyclic_u=closed
    return link(bpy.data.objects.new(name,cu),name,group,ma)
def parent_keep(o,parent):
    bpy.context.view_layer.update();m=o.matrix_world.copy();o.parent=parent;o.matrix_world=m
def empty(name,p,group):
    o=link(bpy.data.objects.new(name,None),name,group);o.location=p;o.empty_display_type='PLAIN_AXES';o.empty_display_size=.12;return o
def cylinder(name,p,r,depth,ma,group,axis='X',n=48):
    vs=[]
    for a in [-depth/2,depth/2]:
        for i in range(n):
            t=2*pi*i/n;v=(a,r*cos(t),r*sin(t)) if axis=='X' else ((r*cos(t),a,r*sin(t)) if axis=='Y' else (r*cos(t),r*sin(t),a));vs.append(v)
    fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    o=mesh(name,vs,fs,ma,group,True);o.location=p;return o
def rr(cx,cz,w,h,r=.06,n=5):
    pts=[]
    for x,z,a in [(cx+w/2-r,cz+h/2-r,0),(cx-w/2+r,cz+h/2-r,90),(cx-w/2+r,cz-h/2+r,180),(cx+w/2-r,cz-h/2+r,270)]:
        for i in range(n+1):
            t=(a+i*90/n)*pi/180;pts.append((x+r*cos(t),z+r*sin(t)))
    return pts
def ring(name,outer,inner,mapper,ma,group='ACABAMENTOS',thick=.012):
    N=len(outer);assert N==len(inner)
    return mesh(name,[mapper(*p) for p in outer+inner],[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)],ma,group,True,thick)
def disk(name,pts,mapper,ma,group='VIDROS',thick=.007):
    # Concentric quad bands follow the curved mapping, avoiding a flat n-gon.
    cx=sum(p[0] for p in pts)/len(pts);cz=sum(p[1] for p in pts)/len(pts);N=len(pts);vs=[mapper(cx,cz)];fs=[]
    for k in range(1,9):
        for x,z in pts:vs.append(mapper(cx+(x-cx)*k/8,cz+(z-cz)*k/8))
    fs.extend((0,i+1,(i+1)%N+1) for i in range(N))
    for k in range(7):
        a=1+k*N;b=a+N;fs.extend((a+i,b+i,b+(i+1)%N,a+(i+1)%N) for i in range(N))
    return mesh(name,vs,fs,ma,group,True,thick)
def scalepts(pts,sx,sz=None):
    sz=sz if sz is not None else sx;cx=sum(x for x,z in pts)/len(pts);cz=sum(z for x,z in pts)/len(pts)
    return [(cx+(x-cx)*sx,cz+(z-cz)*sz) for x,z in pts]
def spline(pts,n=4):
    out=[]
    for i,p in enumerate(pts):
        p0=Vector(pts[i-1]);p1=Vector(p);p2=Vector(pts[(i+1)%len(pts)]);p3=Vector(pts[(i+2)%len(pts)])
        for j in range(n):
            t=j/n;out.append(tuple(.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t)))
    return out

font_path=Path('C:/Windows/Fonts/arialbd.ttf')
font=bpy.data.fonts.load(str(font_path)) if font_path.exists() else None
def text(name,body,p,size,ma,orientation,group='ACABAMENTOS'):
    cu=bpy.data.curves.new(name,'FONT');cu.body=body;cu.size=size;cu.align_x='CENTER';cu.align_y='CENTER';cu.extrude=.0002;cu.resolution_u=8
    if font:cu.font=font
    o=link(bpy.data.objects.new(name,cu),name,group,ma);o.location=p
    # local x text-right, local y text-up; normal points outward.
    right={'R':(0,-1,0),'L':(0,1,0),'F':(1,0,0),'B':(-1,0,0)}[orientation];up=(0,0,1)
    a=Vector(right);b=Vector(up);c=a.cross(b);o.rotation_euler=Matrix((a,b,c)).transposed().to_euler();return o

def Y(u):return 6-(u-26)*12/1084
def Z(v):return (286-v)*.0117
def side_x(sign,z):return sign*(1.25-.045*max(0,z-2.6)**2)
def smap(sign,offset=0):return lambda y,z:(side_x(sign,z)+sign*offset,y,z)
DOORS=[('DIANTEIRA',Y(1077),Y(984)),('CENTRAL',Y(624),Y(519)),('TRASEIRA',Y(270),Y(181))]
axles=[-3.70,2.14];wz=.558;wr=.555
def bottom(y):
    z=.397+.04*(abs(y)/6)**5
    for a in axles:
        if abs(y-a)<.646:z=max(z,wz+sqrt(max(0,.646**2-(y-a)**2)))
    return z
def cut(y):return any(a-.018<y<b+.018 for _,a,b in DOORS)
def paint(sign,y,z):
    white_band=(-2.95<y<1.86) if sign<0 else (-3.13<y<1.8)
    return white if white_band or z<Z(164) else yellow
for sign in [-1,1]:
    # Lower shell consists of quads, with true door and wheel openings.
    ys=[-5.73+i*11.48/250 for i in range(251)]
    for a in axles:ys.extend(a+.646*cos(pi*i/40) for i in range(41))
    for _,a,b in DOORS:ys.extend([a-.018,a,b,b+.018])
    ys.extend([-2.95,1.86,-3.13,1.8]);ys=sorted(set(y for y in ys if -5.73<=y<=5.75))
    for band,(za,zb) in enumerate([(.397,Z(205)),(Z(205),Z(164)),(Z(164),Z(133))]):
        vs=[];fs=[];mats=[]
        for a,b in zip(ys,ys[1:]):
            if sign<0 and cut((a+b)/2):continue
            lo1=max(za,bottom(a));lo2=max(za,bottom(b))
            if min(lo1,lo2)>=zb:continue
            lo1=min(lo1,zb);lo2=min(lo2,zb);j=len(vs)
            vs.extend([smap(sign)(a,lo1),smap(sign)(b,lo2),smap(sign)(b,zb),smap(sign)(a,zb)])
            fs.append((j,j+1,j+2,j+3) if sign<0 else (j+3,j+2,j+1,j));mats.append(paint(sign,(a+b)/2,(za+zb)/2)==white)
        o=mesh('Painel lateral %s faixa %s'%(sign,band),vs,fs,yellow,'CARROCERIA',True,.026);o.data.materials.append(white)
        for p,m in zip(o.data.polygons,mats):p.material_index=int(m)
    # Window openings follow measured 2D concept positions.
    intervals=([(49,167),(282,311),(315,446),(451,505),(637,700),(705,842),(846,969)] if sign<0 else [(176,286),(290,421),(427,557),(564,690),(695,826),(831,962),(969,1079)])
    windows=[]
    for index,(u0,u1) in enumerate(intervals):
        a,b=sorted((Y(u0),Y(u1))) if sign<0 else (-Y(u0),-Y(u1));cy=(a+b)/2;w=b-a;zc=(Z(48)+Z(134))/2;h=Z(48)-Z(134)
        windows.append((a,b))
        outer=rr(cy,zc,w,h,.135,6);inner=rr(cy,zc,w-.085,h-.085,.102,6)
        ring('Janela %s %02d moldura'%(sign,index),outer,inner,smap(sign,.022),black,'VIDROS',.023)
        ring('Janela %s %02d filete'%(sign,index),rr(cy,zc,w-.026,h-.026,.124,6),rr(cy,zc,w-.04,h-.04,.117,6),smap(sign,.035),dark,'VIDROS',.008)
        disk('Janela %s %02d vidro'%(sign,index),inner,smap(sign,.027),glass)
        # Surround connects rounded window corners to a rectangular structural bay.
        ring('Chapa ao redor janela %s %02d'%(sign,index),rr(cy,zc,w+.02,h+.022,.006,6),outer,smap(sign),paint(sign,cy,zc),'CARROCERIA',.024)
        if w>.43:
            zh=Z(92);curve('Travessa janela',[(side_x(sign,zh)+sign*.049,a+.048,zh),(side_x(sign,zh)+sign*.049,b-.048,zh)],dark,.014,'VIDROS')
            curve('Divisoria janela',[(side_x(sign,zc)+sign*.048,cy,Z(133)+.047),(side_x(sign,zc)+sign*.048,cy,Z(49)-.045)],dark,.010,'VIDROS')
            for edge in [a+.07,b-.07]:box('Fecho janela',(sign*1.30,edge,Z(99)),(.012,.048,.027),black,'VIDROS',.004)
    occupied=windows+([(a,b) for _,a,b in DOORS] if sign<0 else [])
    # Driver glass uses its own slanted silhouette.
    if sign>0:
        p=[(-5.72,Z(82)),(-5.60,Z(62)),(-4.66,Z(62)),(-4.57,Z(141)),(-5.71,Z(151))];p=spline(p,5)
        ring('Motorista moldura',p,scalepts(p,.94,.94),smap(sign,.018),black,'VIDROS',.02)
        disk('Motorista vidro',scalepts(p,.94,.94),smap(sign,.025),glass)
        curve('Motorista folha corrediça',[(1.289,-5.14,Z(63)),(1.289,-5.14,Z(145))],dark,.013,'VIDROS')
        occupied.append((-5.73,-4.57))
    occupied=sorted(occupied)
    cursor=-5.73
    for a,b in occupied+[(5.75,5.75)]:
        if a>cursor+.003:
            cy=(cursor+a)/2;box('Montante estrutural %s'%sign,(sign*1.235,cy,(Z(134)+Z(48))/2),(.032,a-cursor,Z(48)-Z(134)),paint(sign,cy,Z(90)),'CARROCERIA',.004)
        cursor=max(cursor,b)
    # Continuous upper waist / roof rail, split at color boundaries.
    for a,b in zip([-5.73,-3.13,-2.95,1.8,1.86,5.75],[-3.13,-2.95,1.8,1.86,5.75,5.75]):
        if b>a:box('Cinta superior %s'%sign,(sign*1.224,(a+b)/2,2.94),(.043,b-a,.285),paint(sign,(a+b)/2,2.94),'CARROCERIA',.026)
    # Longitudinal service-panel seams interrupted at doors and wheel openings.
    for y in [-5.58,-4.45,-2.88,-1.15,1.06,3.17,5.37]:
        if sign<0 and cut(y):continue
        za=bottom(y)+.018
        if za<Z(204):
            curve('Junta tampa lateral',[(sign*1.268,y,za),(sign*1.268,y,Z(204))],black,.0035)
            box('Fecho tampa',(sign*1.277,y+.08,Z(218)),(.012,.058,.075),silver,radius=.006)
    for a,b in zip(ys,ys[1:]):
        if sign<0 and cut((a+b)/2):continue
        if bottom(a)<Z(204) and bottom(b)<Z(204):curve('Junta horizontal saia',[(sign*1.266,a,Z(204)),(sign*1.266,b,Z(204))],dark,.0025)
    for y in [-5.57,-4.52,-2.73,-1.3,1.0,3.05,5.38]:
        if sign<0 and cut(y):continue
        box('Refletivo vermelho',(sign*1.278,y,Z(208)),(.012,.14,.038),red,radius=.003)
        box('Refletivo branco',(sign*1.279,y+.13,Z(208)),(.012,.12,.038),paper,radius=.003)
    for y in [-5.5,-2.85,.6,3.05,5.3]:
        if sign<0 and cut(y):continue
        box('Luz demarcadora base',(sign*1.282,y,.76),(.023,.095,.043),black,radius=.009)
        box('Luz demarcadora lente',(sign*1.297,y,.763),(.018,.075,.032),amber,radius=.008)
    for a in axles:
        pts=[(sign*1.272,a+.651*cos(t*pi/64),wz+.651*sin(t*pi/64)) for t in range(65)]
        curve('Guarnicao arco roda',pts,black,.018)
        pts2=[(sign*1.275,a+.685*cos(t*pi/64),wz+.685*sin(t*pi/64)) for t in range(65)]
        curve('Vinco chapa arco roda',pts2,white,.008)
        # Real wheel well inner liner follows the arch across wheel width.
        vs=[(xx,a+.627*cos(t*pi/48),wz+.627*sin(t*pi/48)) for xx in [sign*.84,sign*1.25] for t in range(49)]
        mesh('Caixa de roda interna',vs,[(i,i+1,50+i,49+i) for i in range(48)],black,'CARROCERIA',True,.012)
        box('Para-barro roda',(sign*1.05,a+.58,.32),(.36,.025,.37),rubber,radius=.008)

# Roof shell: transverse curvature and end roll, not a rectangular block.
vs=[];fs=[];nx=48;ny=70
for j in range(ny+1):
    y=-5.77+j*11.53/ny
    for i in range(nx+1):
        t=-pi/2+i*pi/nx;x=1.247*sin(t);z=2.85+.22*cos(t)-.022*(abs(y)/5.77)**10;vs.append((x,y,z))
for j in range(ny):
    for i in range(nx):
        a=j*(nx+1)+i;fs.append((a,a+1,a+nx+2,a+nx+1))
mesh('Teto transversal abaulado',vs,fs,yellow,'CARROCERIA',True,.026)
for y in [-4.1,-.5,3.5]:
    box('Escotilha borracha',(0,y,3.073),(.87,.64,.033),black,'CARROCERIA',.07)
    box('Escotilha capa',(0,y,3.101),(.82,.59,.06),white,'CARROCERIA',.07)
for sign in [-1,1]:
    curve('Calha superior continua',[(sign*1.248,-5.6,2.894),(sign*1.248,5.58,2.894)],dark,.008)
    for cy,ma in [(-3.23,green),(-3.78,yellow),(-4.28,blue),(-4.78,yellow)]:
        box('Faixa teto lateral',(sign*1.256,cy,2.975),(.009,.5,.17),ma,'ACABAMENTOS',.003)

# End surfaces and glazing are physically open rings, not glass pasted on opaque panels.
def depth(x,z,end,off=0):
    return (-6.045+.205*(abs(x)/1.25)**4+.145*max(0,z-1.12)+.08*max(0,.67-z)-off) if end<0 else (6.025-.19*(abs(x)/1.25)**4-.075*max(0,z-1.8)+off)
def fmap(end,off=0):return lambda x,z:(x,depth(x,z,end,off),z)
front=spline([(-1.08,2.59),(-1.035,2.65),(1.035,2.65),(1.08,2.59),(1.085,1.66),(.93,1.4),(.62,1.255),(-.62,1.255),(-.93,1.4),(-1.085,1.66)],5)
rear=spline([(-1.065,2.82),(1.065,2.82),(1.1,2.69),(1.105,2.07),(.88,2.10),(0,2.135),(-.88,2.10),(-1.105,2.07),(-1.1,2.69)],5)
for end,wind,label in [(-1,front,'Dianteira'),(1,rear,'Traseira')]:
    # Radial annulus maps the window perimeter onto the rounded overall end silhouette.
    N=len(wind);zc=1.73 if end<0 else 1.73
    outer=[]
    for x,z in wind:
        dx=x;dz=z-zc;sc=min(1.247/max(abs(dx),1e-8),(3.046-zc)/max(dz,1e-8) if dz>0 else (zc-.407)/max(-dz,1e-8))
        xx=dx*sc;zz=zc+dz*sc
        if zz>2.85:xx*=1-.08*((zz-2.85)/.2)
        outer.append((xx,zz))
    vs=[];fs=[]
    for j in range(13):
        t=j/12
        for p,q in zip(wind,outer):vs.append(fmap(end)(p[0]*(1-t)+q[0]*t,p[1]*(1-t)+q[1]*t))
    for j in range(12):
        for i in range(N):
            a=j*N+i;b=j*N+(i+1)%N;fs.append((a,b,b+N,a+N))
    mesh(label+' chapa envolvente',vs,fs,yellow,'CARROCERIA',True,.028)
    for sign in [-1,1]:
        zs=[.42,.48,.7,1.1,1.5,1.9,2.3,2.65,2.8,2.91,3.01,3.05]
        vs=[]
        for z in zs:
            w=1.247*(1-.08*max(0,z-2.85)/.2);vs.extend([(sign*w,depth(sign*w,z,end),z),(side_x(sign,z),end*5.745,z)])
        mesh(label+' retorno de canto',vs,[(2*i,2*i+1,2*i+3,2*i+2) for i in range(len(zs)-1)],yellow,'CARROCERIA',True,.026)
    ring(label+' vedacao vidro',wind,scalepts(wind,.964,.964),fmap(end,.024),black,'VIDROS',.016)
    ring(label+' filete vidro',scalepts(wind,.985,.985),scalepts(wind,.977,.977),fmap(end,.029),dark,'VIDROS',.004)
    disk(label+' vidro curvo',scalepts(wind,.964,.964),fmap(end,.025),glass)
    if end<0:
        curve('Para-brisa montante central',[fmap(-1,.047)(0,z) for z in [1.25,1.4,1.9,2.3,2.65]],black,.009,'VIDROS')
        for sign in [-1,1]:
            # Short upper mounting arms and blades follow curved windshield.
            curve('Limpador haste superior',[fmap(-1,.07)(sign*.65,2.64),fmap(-1,.083)(sign*.23,2.02)],black,.012)
            curve('Limpador palheta',[fmap(-1,.097)(sign*.11,1.98),fmap(-1,.092)(sign*.40,2.59)],dark,.015)
            cylinder('Eixo limpador',fmap(-1,.08)(sign*.65,2.64),.026,.025,black,'ACABAMENTOS','Y',24)
    else:
        curve('Borracha inferior vidro traseiro',[fmap(1,.04)(x,2.09+.045*(1-(x/1.08)**2)) for x in [-1.05+i*2.10/36 for i in range(37)]],black,.013,'VIDROS')

display=rr(0,2.844,2.29,.275,.075,8)
disk('Letreiro eletronico alojamento',display,fmap(-1,.028),black,'ACABAMENTOS')
ring('Letreiro aro',display,scalepts(display,.977,.82),fmap(-1,.04),dark,'ACABAMENTOS')
for sign in [-1,1]:
    disk('Luz de posicao frontal',rr(sign*.995,2.93,.072,.035,.012,4),fmap(-1,.053),lens,'FAROIS')
    disk('Luz superior traseira',rr(sign*1.035,2.975,.13,.031,.012,4),fmap(1,.027),red,'LANTERNAS')

# Recessed swept headlights, segmented reflectors and clear cover.
lamp_base=[(.75,.82),(1.17,1.17),(1.18,1.03),(1.105,.885),(.84,.795)]
for sign in [-1,1]:
    pts=spline([(sign*x,z) for x,z in lamp_base],5)
    disk('Farol alojamento curvo',scalepts(pts,1.07),fmap(-1,.038),dark,'FAROIS')
    ring('Farol aro cromado',pts,scalepts(pts,.91),fmap(-1,.05),chrome,'FAROIS',.008)
    disk('Farol refletor',scalepts(pts,.9),fmap(-1,.055),silver,'FAROIS')
    for x,z,r in [(1.095,1.021,.051),(.995,.924,.045),(.883,.856,.031)]:
        q=rr(sign*x,z,r*1.9,r*1.55,r*.65,6)
        disk('Farol lente optica',q,fmap(-1,.079),lens if x>.90 else amber,'FAROIS')
        curve('Farol contorno refletor',[fmap(-1,.073)(*p) for p in q],chrome,.004,'FAROIS',True)
    for j in range(9):
        x=.9+j*.025;z=.855+(x-.9)*.72
        curve('Estria lente farol',[fmap(-1,.081)(sign*x,z-.018),fmap(-1,.081)(sign*x,z+.02)],lens,.0015,'FAROIS')
    curve('Vinco lateral para-choque',[fmap(-1,.016)(sign*x,z) for x,z in [(1.17,.73),(.94,.68),(.86,.58),(1.15,.58)]],yellow,.008,'PARACHOQUES')
grille=spline([(-.7,.68),(.7,.68),(.61,.48),(.34,.437),(-.34,.437),(-.61,.48)],7)
disk('Grade frontal rebaixo',grille,fmap(-1,.035),black,'PARACHOQUES')
for z,w in [(.495,.54),(.545,.61),(.598,.66),(.651,.69)]:curve('Grade frontal aleta',[fmap(-1,.052)(-w,z),fmap(-1,.052)(0,z-.009),fmap(-1,.052)(w,z)],dark,.008,'PARACHOQUES')
for end in [-1,1]:
    curve('Junta para-choque',[fmap(end,.022)(-1.16,.735),fmap(end,.024)(0,.727),fmap(end,.022)(1.16,.735)],yellow,.009,'PARACHOQUES')
    disk('Placa suporte',rr(0,.448,.48,.108,.01,4),fmap(end,.069),black,'PARACHOQUES')
    disk('Placa branca',rr(0,.453,.43,.084,.006,4),fmap(end,.075),paper,'PARACHOQUES')
    text('Placa caracteres','PJR7D37',fmap(end,.082)(0,.448),.054,dark,'F' if end<0 else 'B')
    for x in [-.18,.18]:cylinder('Placa fixacao',fmap(end,.082)(x,.476),.004,.004,chrome,'PARACHOQUES','Y',8)

# Rear vertical swept taillights match the red outer housings of the drawing.
for sign in [-1,1]:
    pts=spline([(sign*1.17,1.52),(sign*1.08,1.40),(sign*1.015,.88),(sign*1.17,.81),(sign*1.205,1.15)],5)
    disk('Lanterna traseira suporte',scalepts(pts,1.05),fmap(1,.025),black,'LANTERNAS')
    disk('Lanterna traseira lente integral',pts,fmap(1,.041),red,'LANTERNAS')
    for j,z in enumerate([.93,1.075,1.22,1.355]):
        x=sign*(1.15-.06*(z-.9)/.46)
        q=rr(x,z,.065,.102,.027,5)
        disk('Lanterna compartimento',q,fmap(1,.06),lens if j==0 else red,'LANTERNAS')
        curve('Lanterna optica nervura',[fmap(1,.064)(x-.022,z),fmap(1,.064)(x+.022,z)],chrome,.002,'LANTERNAS')
    curve('Vinco tampa traseira',[fmap(1,.016)(sign*x,z) for x,z in [(1.035,1.90),(.85,1.82),(.3,1.79)]],yellow,.008)
text('Frota frontal','31065',fmap(-1,.07)(-.7,.805),.12,black,'F')
text('Marca frontal','Marcopolo',fmap(-1,.066)(0,1.18),.055,paper,'F')
text('Frota traseira','31065',fmap(1,.054)(-.83,.92),.137,black,'B')
text('Marca traseira','Marcopolo',fmap(1,.05)(0,1.93),.067,chrome,'B')
# VW rondel, replacing the unrelated Mercedes emblem from the original blockout.
curve('VW aro',[fmap(-1,.06)(.058*cos(t*2*pi/48),.797+.058*sin(t*2*pi/48)) for t in range(48)],chrome,.0045,closed=True)
curve('VW V',[fmap(-1,.07)(x,z) for x,z in [(-.028,.824),(0,.79),(.028,.824)]],chrome,.004)
curve('VW W',[fmap(-1,.07)(x,z) for x,z in [(-.04,.802),(-.023,.773),(0,.796),(.023,.773),(.04,.802)]],chrome,.004)

# Three separate door assemblies, two independent leaves and their parent hinges.
for name,a,b in DOORS:
    group='PORTA_'+name;cy=(a+b)/2;width=b-a;z0=Z(250);z1=Z(70);h=z1-z0
    box(name+' travessa superior',(-1.247,cy,z1+.03),(.085,width+.07,.069),black,group,.008)
    box(name+' calha',(-1.296,cy,z1+.065),(.11,width+.14,.024),dark,group,.008)
    for y in [a-.018,b+.018]:box(name+' batente',(-1.24,y,(z0+z1)/2),(.07,.037,h+.08),black,group,.007)
    box(name+' soleira',(-1.18,cy,z0-.015),(.20,width+.07,.04),silver,group,.005)
    box(name+' borda amarela soleira',(-1.292,cy,z0+.009),(.025,width+.03,.018),yellow,group,.004)
    assembly=empty(name+' controle',(0,0,0),group);assembly['tipo']='porta_duas_folhas_internas';assembly['frames']='1/120 fechada; 65 aberta'
    for leaf,sgn in [('A',1),('B',-1)]:
        hinge_y=a+.027 if sgn>0 else b-.027;leafw=width/2-.037;center=hinge_y+sgn*leafw/2
        hinge=empty(name+' pivo '+leaf,(-1.195,hinge_y,z0),group);parent_keep(hinge,assembly)
        parts=[]
        outer=rr(center,(z0+z1)/2,leafw,h-.025,.035,6);inner=rr(center,(z0+z1)/2,leafw-.068,h-.095,.024,6)
        parts.append(ring(name+' folha '+leaf+' estrutura',outer,inner,lambda y,z:(-1.262,y,z),silver,group,.031))
        parts.append(ring(name+' folha '+leaf+' vedacao',inner,scalepts(inner,.965,.985),lambda y,z:(-1.274,y,z),black,group,.012))
        split=Z(161)
        for idx,(low,high) in enumerate([(z0+.055,split-.04),(split+.022,z1-.051)]):
            pts=rr(center,(low+high)/2,leafw-.088,high-low,.062,6)
            parts.append(disk(name+' folha '+leaf+' vidro '+str(idx),pts,lambda y,z:(-1.277,y,z),glass,group,.01))
            parts.append(curve(name+' folha borracha vidro', [(-1.283,y,z) for y,z in pts],black,.012,group,True))
        parts.append(box(name+' folha travessa',(-1.272,center,split),(.038,leafw-.012,.05),silver,group,.006))
        # Yellow internal grab rails visible through the door, as in concept.
        rail=[(-1.291,center-sgn*.12,z1-.11),(-1.291,center-sgn*.12,split+.26),(-1.291,center+sgn*.11,split+.07)]
        parts.append(curve(name+' corrimao superior',rail,yellow,.012,group))
        parts.append(curve(name+' corrimao inferior',[(-1.291,center+sgn*.11,split-.12),(-1.291,center-sgn*.12,z0+.17)],yellow,.012,group))
        for z in [z0+.25,z1-.18]:parts.append(cylinder(name+' manga dobradica',(-1.2,hinge_y,z),.023,.10,dark,group,'Z',20))
        for o in parts:parent_keep(o,hinge)
        hinge.rotation_mode='XYZ'
        # For -X door side, A rotates -Z, B +Z: both sweep inboard into the doorway.
        for frame,t in [(1,0),(35,.5),(65,1),(95,.5),(120,0)]:
            hinge.rotation_euler.z=-sgn*t*math.radians(92);hinge.keyframe_insert(data_path='rotation_euler',index=2,frame=frame)
        hinge['abertura_graus']=92;hinge['mecanismo_status']='interpretação funcional da referência externa'
    if name=='CENTRAL':
        box('Plataforma acesso recolhida',(-1.07,cy,z0-.066),(.37,width-.09,.047),dark,group,.007)
    for y in [a+.17,b-.17]:box(name+' adesivo refletivo',(-1.287,y,z0+.073),(.008,.19,.034),red,group,.002)
    text(name+' identificação',{'DIANTEIRA':'Entrada','CENTRAL':'Uso nos Terminais','TRASEIRA':'Saída'}[name],(-1.285,cy,z1+.17),.11 if name!='CENTRAL' else .085,black,'R',group)

# Detailed wheels: lathed sidewall/tread, rim barrel, recessed steel disc, ten vents/bolts.
def lathe(name,profile,center,ma,group,n=80):
    vs=[];fs=[]
    for a,r in profile:
        for i in range(n):
            t=i*2*pi/n;vs.append((center[0]+a,center[1]+r*cos(t),center[2]+r*sin(t)))
    for j in range(len(profile)-1):
        for i in range(n):a=j*n+i;b=j*n+(i+1)%n;fs.append((a,b,b+n,a+n))
    return mesh(name,vs,fs,ma,group,True)
for axle_idx,y in enumerate(axles):
    group='RODAS_DIANTEIRAS' if axle_idx==0 else 'RODAS_TRASEIRAS'
    axle=empty('Eixo '+('dianteiro' if axle_idx==0 else 'traseiro'),(0,y,wz),group)
    for sign in [-1,1]:
        carrier=empty(('Dianteira' if axle_idx==0 else 'Traseira')+' roda '+str(sign),(sign*1.043,y,wz),group);parent_keep(carrier,axle)
        centers=[sign*1.042] if axle_idx==0 else [sign*1.055,sign*.771]
        for k,cx in enumerate(centers):
            profile=[(-.145,.315),(-.147,.405),(-.14,.475),(-.116,.527),(-.091,.55),(-.065,.555),(.065,.555),(.091,.55),(.116,.527),(.14,.475),(.147,.405),(.145,.315)]
            tire=lathe('Pneu %s %s %s'%(axle_idx,sign,k),profile,(cx,y,wz),rubber,'PNEUS');parent_keep(tire,carrier)
            # Four continuous recessed grooves and staggered transverse shoulder sipes.
            for dx in [-.071,-.024,.024,.071]:
                groove=lathe('Sulco longitudinal',[(dx-.004,.5552),(dx+.004,.5552)],(cx,y,wz),tread,'PNEUS');parent_keep(groove,carrier)
            vs=[];fs=[]
            for i in range(64):
                t=i*2*pi/64
                for side in [-1,1]:
                    a=side*.079;b=side*.119;ta=t+side*.01;tb=t+side*.048;j=len(vs)
                    for xx,tt,r in [(a,ta,.555),(b,tb,.527),(b,tb+.008,.527),(a,ta+.008,.555)]:vs.append((cx+xx,y+r*cos(tt),wz+r*sin(tt)))
                    fs.append((j,j+1,j+2,j+3))
            o=mesh('Lamelas ombro pneu',vs,fs,tread,'PNEUS');parent_keep(o,carrier)
        outer=sign*(1.19 if axle_idx==0 else 1.201)
        for radius in [.35,.447,.493]:
            o=lathe('Nervura lateral pneu',[(outer-.001*sign,radius-.002),(outer+.001*sign,radius+.002)],(0,y,wz),tread,'PNEUS');parent_keep(o,carrier)
        barrel=[(sign*.89,.312),(sign*1.15,.312),(sign*1.189,.327),(sign*1.208,.327),(sign*1.215,.31),(sign*1.202,.298),(sign*1.17,.289)]
        o=lathe('Aro borda e canal',barrel,(0,y,wz),silver,'AROS');parent_keep(o,carrier)
        discx=sign*(1.19 if axle_idx==0 else 1.075)
        # Ten real vent cutouts are part of the disc topology, not black decals.
        nv=120;vs=[];fs=[]
        for r in [.115,.174,.20,.26,.289]:
            x=discx-sign*(.018 if r>.2 else 0)
            for i in range(nv):t=i*2*pi/nv;vs.append((x,y+r*cos(t),wz+r*sin(t)))
        for j in range(4):
            for i in range(nv):
                if j==2 and 3<=i%12<=8:continue
                a=j*nv+i;b=j*nv+(i+1)%nv;fs.append((a,b,b+nv,a+nv))
        o=mesh('Disco roda dez janelas',vs,fs,silver,'AROS',True,.011);parent_keep(o,carrier);bevel(o,.004,2)
        for r,dep in [(.122,.068),(.086,.08)]:
            o=cylinder('Cubo roda',(discx+sign*dep/2,y,wz),r,dep,silver,group);parent_keep(o,carrier);bevel(o,.006,3)
        for i in range(10):
            t=2*pi*i/10;yy=y+.156*cos(t);zz=wz+.156*sin(t)
            for radius,dep,ma in [(.024,.01,dark),(.017,.031,chrome)]:
                o=cylinder('Porca roda dez fixacoes',(discx+sign*.018,yy,zz),radius,dep,ma,group,n=6 if ma==chrome else 24);parent_keep(o,carrier)
        for i in range(6):
            t=2*pi*i/6;o=cylinder('Parafuso tampa cubo',(discx+sign*.083,y+.062*cos(t),wz+.062*sin(t)),.007,.006,chrome,group,n=6);parent_keep(o,carrier)
        o=cylinder('Valvula pneu',(sign*1.213,y+.27,wz+.04),.009,.036,black,group,n=12);parent_keep(o,carrier)

# Exterior mirrors: swept support tubes, separately replaceable shell and mirror.
for sign in [-1,1]:
    box('Base retrovisor',(sign*1.25,-5.57,2.55),(.072,.12,.16),black,'RETROVISORES',.025)
    curve('Braco retrovisor',[(sign*1.27,-5.59,2.61),(sign*1.61,-5.70,2.62),(sign*1.69,-5.86,2.47),(sign*1.69,-5.90,2.20)],dark,.024,'RETROVISORES')
    box('Carcaca retrovisor',(sign*1.69,-5.91,2.06),(.17,.115,.49),black,'RETROVISORES',.075)
    box('Espelho retrovisor',(sign*1.69,-5.838,2.06),(.126,.012,.419),chrome,'RETROVISORES',.047)
    curve('Junta retrovisor',[(sign*1.69-.06,-5.83,2.03),(sign*1.69+.06,-5.83,2.03)],dark,.003,'RETROVISORES')

# Livery and identifiers positioned from the drawing, not the previous bus reference.
for sign,label in [(-1,'R'),(1,'L')]:
    yfleet=Y(880) if sign<0 else -Y(235)
    text('Frota lateral','31065',(sign*1.285,yfleet,1.53),.225,black,label)
    ylogo=Y(730) if sign<0 else -Y(476)
    text('Integra lateral','integra',(sign*1.288,ylogo,1.37),.45,yellow,label)
    text('Operadora lateral','Plataforma',(sign*1.289,ylogo,1.105),.086,black,label)
    text('URL lateral','integrasalvador.com.br',(sign*1.285,Y(357) if sign<0 else -Y(790),1.585),.071,black,label)
    text('Motor Euro 5','Motor Euro 5 - Ar mais puro',(sign*1.286,Y(223) if sign<0 else -Y(956),2.965),.080,black,label)
    # Driver side narrow grille directly ahead of front axle, as shown.
    if sign>0:
        for i in range(13):box('Entrada ar lateral dianteira',(1.283,-5.14+i*.031,1.025),(.011,.012,.2),dark,radius=.002)
        text('Torino identificação','TORINO',(1.285,-5.1,2.78),.085,paper,'L')

def access(name,mapper,cx,cz,size,group='ACABAMENTOS'):
    disk(name+' fundo',rr(cx,cz,size,size,.009,4),mapper,blue,group,.002)
    # Geometric ISA: head, seat and incomplete wheel, coherent at close range.
    pp=lambda u,v:mapper(cx+u*size,cz+v*size)
    curve(name+' roda',[pp(-.06+.245*cos(t),-.13+.245*sin(t)) for t in [(.18+i*1.58/26)*pi for i in range(27)]],paper,size*.035,group)
    curve(name+' figura',[pp(-.04,.23),pp(-.04,-.035),pp(.2,-.035),pp(.29,-.27),pp(.39,-.23)],paper,size*.036,group)
    curve(name+' apoio',[pp(-.04,.105),pp(.19,.105)],paper,size*.033,group)
    disk(name+' cabeça',rr(cx-.04*size,cz+.31*size,size*.12,size*.12,size*.06,6),mapper,paper,group,.003)
access('Acessibilidade frente',fmap(-1,.054),.12,1.38,.235)
access('Acessibilidade traseira',fmap(1,.054),.94,.91,.21)
access('Acessibilidade lado portas',smap(-1,.04),Y(500),1.49,.25)
access('Acessibilidade lado motorista',smap(1,.04),-Y(715),1.51,.25)

# Preserve only the existing interior blockout, unchanged, in the new asset scene.
mapping={}
for o in bpy.data.collections['BUS02 | INTERIOR_ESBOCO'].objects:
    cp=o.copy();groups['INTERIOR_ESBOCO'].objects.link(cp);mapping[o]=cp
for o,cp in mapping.items():
    cp.parent=mapping.get(o.parent,root);cp.matrix_world=o.matrix_world.copy()
groups['INTERIOR_ESBOCO']['status']='Esboço anterior preservado; não refinado nesta etapa'

# Modeling review cameras and studio lights (never part of the vehicle geometry).
camd=bpy.data.cameras.new('TOR04 camera');cam=link(bpy.data.objects.new('TOR04 camera',camd),'Camera revisão','APRESENTACAO');cam.parent=None;s.camera=cam
camd.type='ORTHO';camd.ortho_scale=14.9
cam.location=(-15,-18,10);cam.rotation_euler=(Vector((0,0,1.5))-cam.location).to_track_quat('-Z','Y').to_euler()
world=bpy.data.worlds.new('TOR04 studio');world.use_nodes=True;bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs[0].default_value=(.16,.19,.24,1);bg.inputs[1].default_value=.6;s.world=world
for name,p,energy,size in [('Principal',(-5,-7,10),1900,8),('Preenchimento',(5,-1,7),1600,7),('Recorte',(-2,8,7),1800,6)]:
    ld=bpy.data.lights.new('TOR04 '+name,'AREA');ld.energy=energy;ld.shape='DISK';ld.size=size;lo=link(bpy.data.objects.new(name,ld),name,'APRESENTACAO');lo.parent=None;lo.location=p;lo.rotation_euler=(Vector((0,0,1.4))-lo.location).to_track_quat('-Z','Y').to_euler()
s.render.engine='BLENDER_WORKBENCH';s.render.resolution_x=1700;s.render.resolution_y=950;s.render.resolution_percentage=100
s.display.shading.light='STUDIO';s.display.shading.studio_light='paint.sl';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.display.shading.curvature_ridge_factor=1.15;s.display.shading.curvature_valley_factor=1.0
s.display.shading.background_type='WORLD';s.world.color=(.16,.17,.19)
s.view_settings.view_transform='Standard'
s.frame_set(1)
for frame,name in [(1,'FECHADO'),(35,'MEIA ABERTURA'),(65,'ABERTO'),(95,'FECHANDO'),(120,'FECHADO')]:s.timeline_markers.new(name,frame=frame)
notes=bpy.data.texts.new('TOR04 | NOTAS DE MODELAGEM')
notes.write('Exterior reconstruído pela referência do Torino 31065 fornecida nesta sessão. Três portas laterais -X; frente -Y; rodas/eixos independentes. Quatro vistas para comparação. Dimensões de modelagem proporcionais ao desenho, não medidas de fábrica. Mecanismo interno das portas interpretado. Interior anterior em esboço preservado. Revisão v03 preservada no arquivo anterior. Nenhuma alteração na cidade ou no Three.js.\n')
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        area.spaces.active.region_3d.view_perspective='CAMERA'
        area.spaces.active.shading.type='SOLID'
        area.spaces.active.shading.color_type='MATERIAL'
        area.spaces.active.overlay.show_overlays=False
bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
print(json.dumps({'saved':str(OUT),'scene':s.name,'objects':len(s.objects),'doors':3,'frames':[1,35,65,120]}))
