"""Carroceria Hilux: contornos de referência, chapas curvas e aberturas reais.

Executar via MCP na cena V05. As fotos controlam forma, não são texturas.
Dimensões nominais verificadas; seções e acessórios continuam interpretação.
"""
import bpy, bmesh, math, json, ast, hashlib
from pathlib import Path
from mathutils import Vector, Matrix
from mathutils.geometry import delaunay_2d_cdt

repo=Path(__file__).resolve().parents[2]
scene=bpy.context.scene
assert Path(bpy.data.filepath).name=='marrom_v05.blend'
out=repo/'blender/assets/vehicles/rondesp-pickup/marrom_v06.blend'
assert not out.exists(), 'Revisão anterior preservada; não sobrescrever.'
root=scene.objects['RDP01_ROOT | viatura']
groups=['CARROCERIA','PORTAS','CAPOTA','VIDROS','RODAS','CHASSIS','LUZES','ACABAMENTOS','INSCRICOES','APRESENTACAO']
collections={g:bpy.data.collections['RDP01 | '+g] for g in groups}
brown=bpy.data.materials['RDP01 | Pintura marrom Rondesp']
black=bpy.data.materials['RDP01 | Polímero preto']
silver=bpy.data.materials['RDP01 | Metal acetinado']
glass=bpy.data.materials['RDP01 | Vidro fumê']
clear=bpy.data.materials['RDP01 | Lentes transparentes']
paint=bpy.data.materials['RDP01 | Camuflagem marrom candidata']
red=bpy.data.materials['RDP01 | Lentes vermelhas']
scope=dict(bpy=bpy,bmesh=bmesh,math=math,Vector=Vector,Matrix=Matrix,root=root,collections=collections,black=black)
tree=ast.parse((repo/'automation/blender/create_rondesp_pickup_v01.py').read_text(encoding='utf-8'))
for name in ['mesh','box','tube','cylinder']:
    fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name)
    exec(compile(ast.Module(body=[fn],type_ignores=[]),'<hilux-data-api>','exec'),scope)
mesh,box,tube,cylinder=[scope[k] for k in ['mesh','box','tube','cylinder']]

# Substituição explícita do conjunto reprovado. Rodas, mecânica e equipamento
# policial independente permanecem; V05 inteira está preservada em outro arquivo.
for o in list(scene.objects):
    g=next((g for g in groups if collections[g] in o.users_collection),None)
    delete=(g in ['CARROCERIA','PORTAS','VIDROS'] and o.type!='EMPTY')
    delete|=('HILUX04' in o.name or 'HILUX05' in o.name) and g not in ['RODAS','CHASSIS']
    delete|=g=='CAPOTA' and any(s in o.name for s in ['Acesso lateral','Junta acesso','Capota','capota'])
    if delete:bpy.data.objects.remove(o,do_unlink=True)

def part(name,vs,fs,mat=brown,group='CARROCERIA',thick=.012,normal=None):
    ob=mesh('HILUX06 | '+name,vs,fs,mat,group,smooth=True,thickness=thick)
    if normal:
        bm=bmesh.new();bm.from_mesh(ob.data)
        for f in bm.faces:
            if f.normal.dot(Vector(normal))<0:f.normal_flip()
        bm.to_mesh(ob.data);bm.free()
    ob['boas_reference_ids']='hilux-2024-std-dealer-side;hilux-srx-user-front;hilux-srx-user-side;rondesp-31110-front;rondesp-31110-rear'
    ob['boas_shape_status']='candidate: contornos interpretados de fotos, sem fotogrametria'
    return ob

def grid(name,fn,nu=48,nv=20,mat=brown,group='CARROCERIA',normal=None,thick=.012):
    vs=[fn(i/nu,j/nv) for i in range(nu+1) for j in range(nv+1)]
    fs=[(i*(nv+1)+j,(i+1)*(nv+1)+j,(i+1)*(nv+1)+j+1,i*(nv+1)+j+1) for i in range(nu) for j in range(nv)]
    return part(name,vs,fs,mat,group,thick,normal)

def interp(points,x):
    if x<=points[0][0]:return points[0][1]
    if x>=points[-1][0]:return points[-1][1]
    for i,(a,b) in enumerate(zip(points,points[1:])):
        if a[0]<=x<=b[0]:
            t=(x-a[0])/(b[0]-a[0]);p=points[max(0,i-1)];q=points[min(len(points)-1,i+2)]
            m0=(b[1]-p[1])/(b[0]-p[0]);m1=(q[1]-a[1])/(q[0]-a[0])
            return (2*t**3-3*t*t+1)*a[1]+(t**3-2*t*t+t)*(b[0]-a[0])*m0+(-2*t**3+3*t*t)*b[1]+(t**3-t*t)*(b[0]-a[0])*m1

def bezier_loop(points,rounding=.20,n=8):
    pts=[]
    for i,p in enumerate(points):
        p=Vector(p);a=p+(Vector(points[i-1])-p)*rounding;b=p+(Vector(points[(i+1)%len(points)])-p)*rounding
        for j in range(n):
            t=j/n;pts.append((1-t)**2*a+2*(1-t)*t*p+t*t*b)
    return pts

def inside(p,poly):
    odd=False
    for a,b in zip(poly,poly[1:]+poly[:1]):
        if (a.y>p.y)!=(b.y>p.y) and p.x<(b.x-a.x)*(p.y-a.y)/(b.y-a.y)+a.x:odd=not odd
    return odd

def sheet(name,outline,holes,project,mat=brown,group='CARROCERIA',normal=None,spacing=.034):
    # CDT respeita aberturas; amostras interiores evitam n-gons não planos.
    pts=[];edges=[]
    for loop in [outline]+holes:
        base=len(pts);pts.extend(loop);edges.extend((base+i,base+(i+1)%len(loop)) for i in range(len(loop)))
    xmin,xmax=min(p.x for p in outline),max(p.x for p in outline)
    ymin,ymax=min(p.y for p in outline),max(p.y for p in outline)
    nx=max(2,math.ceil((xmax-xmin)/spacing));ny=max(2,math.ceil((ymax-ymin)/spacing))
    for i in range(1,nx):
        for j in range(1,ny):
            p=Vector((xmin+(xmax-xmin)*i/nx,ymin+(ymax-ymin)*j/ny))
            if inside(p,outline) and not any(inside(p,h) for h in holes):pts.append(p)
    coords,_,faces,*_=delaunay_2d_cdt(pts,edges,[],0,1e-7)
    faces=[f for f in faces if inside(sum((coords[k] for k in f),Vector((0,0)))/len(f),outline) and not any(inside(sum((coords[k] for k in f),Vector((0,0)))/len(f),h) for h in holes)]
    return part(name,[project(p) for p in coords],faces,mat,group,.009,normal)

def sidewidth(y,z):
    # Seção da porta: ombro superior, concavidade ampla, ressalto inferior e soleira.
    w=interp([(.45,.787),(.51,.836),(.60,.865),(.68,.883),(.77,.868),(.91,.863),(1.03,.880),(1.15,.895),(1.245,.872),(1.31,.828)],z)
    for ax in [-1.43,1.655]:
        d=abs(y-ax)
        w+=.047*math.exp(-(d/.61)**4)*math.exp(-((z-.86)/.31)**4)
    return min(.9275,w)

def arch(y,ax):
    d=abs(y-ax)/.523
    return .485 if d>=1 else max(.485,.38815+.516*(1-d**2.45)**.53)

def cabwidth(y,z):
    w=interp([(1.275,.842),(1.34,.837),(1.50,.800),(1.68,.751),(1.755,.718),(1.795,.689)],z)
    w-=.034*math.exp(-((y-1.105)/.13)**2)
    return w

def nose(x,z,offset=0):
    # Retorno para as laterais, com canto inferior recolhido: forma de fábrica.
    return -2.435+.49*(abs(x)/.9275)**3.5+.092*math.exp(-((z-.47)/.16)**2)+offset

def fronttop(x):return 1.137+.10*(abs(x)/.9275)**2.8

# Capô e ombros: superfícies compartilhando limites, com volume de estampagem.
def upper(u,v):
    x=.9275*(-1+2*v);yf=nose(x,fronttop(x));y=yf+(-.975-yf)*u
    z=fronttop(x)*(1-u)+1.302*u+.028*math.sin(math.pi*u)
    z+=.018*(1-(abs(x)/.9275)**2)*u
    z+=.012*math.exp(-((abs(x)-.57)/.09)**2)*math.sin(math.pi*u)
    return x,y,z
grid('Capô e ombros estampados',upper,66,72,paint,normal=(0,0,1))
for side in [-1,1]:
    def fender(u,t):
        fronty=nose(side*.9275,1.237);y=fronty+(-.975-fronty)*u
        low=arch(y,-1.43);top=upper(u,0)[2];z=low+(top-low)*t
        x=sidewidth(y,z)*(1-t**5)+.9275*t**5
        return(side*x,y,z)
    grid('Para-lama dianteiro '+str(side),fender,72,30,paint,normal=(side,0,0))
    # Abertura circular achatada e retorno da chapa para o interior da caixa.
    for ax in [-1.43,1.655]:
        def lip(u,t):
            y=ax-.523+1.046*u;z=arch(y,ax);x=sidewidth(y,z)
            return(side*(x-.048*t),y,z-.018*t)
        grid('Retorno caixa roda '+str((ax,side)),lip,80,4,paint,normal=(side,0,0),thick=.007)
    seam=[upper(j/60,(side*.79/.9275+1)/2) for j in range(61)]
    tube('HILUX06 | Junta capô '+str(side),seam,.0015,black)

    # Duas portas com bordas em curva, e vincos herdados da mesma seção lateral.
    for label,a,b in [('dianteira',-.968,.093),('traseira',.101,1.12)]:
        def door(u,t):
            z=.493+.798*t
            left=a+.080*(1-t)**9
            right=b-.060*(1-t)**8+.028*t**5
            if label=='traseira':right-=.034*t**4
            y=left+(right-left)*u
            return(side*sidewidth(y,z),y,z)
        ob=grid('Porta '+label+' '+str(side),door,46,34,paint,'PORTAS',(side,0,0))
        edge=[door(i/40,0) for i in range(41)]+[door(1,j/30) for j in range(1,31)]+[door(1-i/40,1) for i in range(1,41)]+[door(0,1-j/30) for j in range(1,31)]
        tube('HILUX06 | Junta porta '+label+' '+str(side),edge,.0015,black,'PORTAS',True)
        # Pivô preservado, transformação local explícita.
        pivot=scene.objects[f'RDP01 | Pivô porta {label} {side:+}']
        ob.parent=pivot;ob.matrix_parent_inverse=pivot.matrix_basis.inverted();ob.matrix_basis=Matrix.Identity(4)
        y=b-.17;z=1.145;x=sidewidth(y,z)
        pocket=box('HILUX06 | Bolso maçaneta '+label+str(side),(side*(x+.001),y,z),(.018,.247,.066),brown,'PORTAS',.032)
        handle=box('HILUX06 | Maçaneta '+label+str(side),(side*(x+.020),y-.01,z+.004),(.030,.180,.031),black,'PORTAS',.014)
    grid('Soleira '+str(side),lambda u,t:(side*(.787+.043*math.sin(math.pi*t/2)),-.88+1.96*u,.465+.029*t),48,6,paint,normal=(side,0,0))

    # Silhueta completa da cabine e recortes seguindo a referência de fábrica.
    outline=bezier_loop([(-.98,1.283),(-.91,1.401),(-.56,1.66),(-.32,1.768),(-.06,1.794),(.86,1.791),(1.065,1.76),(1.123,1.656),(1.14,1.292)],.24,10)
    fw=bezier_loop([(-.873,1.316),(-.742,1.463),(-.449,1.675),(-.268,1.723),(.093,1.744),(.038,1.313)],.18,10)
    rw=bezier_loop([(.181,1.319),(.233,1.744),(.87,1.738),(1.009,1.708),(1.034,1.604),(.88,1.333)],.36,12)
    project=lambda p:(side*cabwidth(p.x,p.y),p.x,p.y)
    sheet('Armação cabine com vãos '+str(side),outline,[fw,rw],project,brown,normal=(side,0,0))
    for label,loop in [('dianteira',fw),('traseira',rw)]:
        sheet('Vidro '+label+' '+str(side),loop,[],lambda p:(side*(cabwidth(p.x,p.y)-.012),p.x,p.y),glass,'VIDROS',(side,0,0),.040)
        tube('HILUX06 | Vedação vidro '+label+str(side),[project(p) for p in loop],.005,black,'VIDROS',True)
    # Divisória do vidro fixo traseiro fina, presente na vista lateral.
    tube('HILUX06 | Divisória vidro traseiro '+str(side),[(side*(cabwidth(y,z)-.007),y,z) for y,z in [(.849,1.334),(.934,1.665),(.903,1.727)]],.009,black,'VIDROS')
    # Coluna B estreita e inclinada; não barra solta sobre a porta.
    grid('Acabamento B '+str(side),lambda u,t:(side*(cabwidth(.06+.13*u+.05*t,1.305+.447*t)+.001),.06+.13*u+.05*t,1.305+.447*t),4,22,black,normal=(side,0,0),thick=.002)
    # Espelho de corpo arredondado com suporte triangular integrado.
    mirror=bezier_loop([(-.917,1.310),(-.744,1.463),(-.701,1.312)],.2)
    sheet('Base espelho '+str(side),mirror,[],lambda p:(side*.843,p.x,p.y),black,'ACABAMENTOS',(side,0,0))
    box('HILUX06 | Espelho '+str(side),(side*1.008,-.786,1.428),(.22,.257,.138),black,bevel=.059)
    box('HILUX06 | Vidro espelho '+str(side),(side*1.008,-.659,1.430),(.168,.005,.094),silver,bevel=.029)

    # Caçamba: arco do para-lama e ombro esculpido, sem parede vertical plana.
    def bed(u,t):
        y=1.165+1.61*u;low=arch(y,1.655);top=1.306-.019*u**10;z=low+(top-low)*t
        x=sidewidth(y,z)-.046*u**12
        return(side*x,y,z)
    grid('Lateral caçamba '+str(side),bed,100,36,paint,normal=(side,0,0))
    tube('HILUX06 | Borda caçamba '+str(side),[bed(i/60,1) for i in range(61)],.007,black)
    if side==-1:
        flap=bezier_loop([(1.38,1.03),(1.69,1.03),(1.69,1.20),(1.38,1.20)],.45,12)
        tube('HILUX06 | Junta abastecimento',[(side*(sidewidth(p.x,p.y)+.001),p.x,p.y) for p in flap],.0016,black)

# Teto: centro alto e bordas enroladas, encaixado na abertura da cabine.
def roof(u,v):
    y=-.325+1.438*u;x=(-1+2*v)*interp([(-.325,.711),(-.05,.714),(.87,.709),(1.113,.667)],y)
    z=interp([(-.325,1.770),(-.07,1.807),(.50,1.811),(.90,1.797),(1.113,1.718)],y)
    return(x,y,z-.032*(abs(2*v-1)**4))
grid('Teto curvatura dupla',roof,58,42,normal=(0,0,1))

def windshield(u,v):
    x=(-1+2*u)*(.803*(1-v)+.705*v)
    y=-.970*(1-v)-.338*v-.038*(1-(2*u-1)**2)*math.sin(math.pi*v)
    z=1.326*(1-v)+1.767*v+.010*(1-(2*u-1)**2)
    return x,y,z
grid('Para-brisa envolvente',windshield,48,30,glass,'VIDROS',(0,-1,.5),.005)
edge=[windshield(i/48,0) for i in range(49)]+[windshield(1,j/30) for j in range(1,31)]+[windshield(1-i/48,1) for i in range(1,49)]+[windshield(0,1-j/30) for j in range(1,31)]
tube('HILUX06 | Borracha para-brisa',edge,.009,black,'VIDROS',True)
for side in [-1,1]:
    def pillar(u,t):
        a=Vector(windshield((side+1)/2,t));y=-.981*(1-t)-.321*t;z=1.322*(1-t)+1.770*t
        b=Vector((side*cabwidth(y,z),y,z));return a.lerp(b,u)
    grid('Montante A curvo '+str(side),pillar,6,36,normal=(side,-.5,.2))
grid('Cowl',lambda u,t:(-.81+1.62*u,-1.015+.045*t,1.314+.009*t),36,4,black)
for a,b in [(-.57,-.03),(.07,.57)]:
    tube('HILUX06 | Limpador',[(a,-.985,1.34),((a+b)/2,-.935,1.365),(b,-.932,1.365)],.007,black)
grid('Parede posterior cabine',lambda u,t:(-.81+1.62*u,1.139-.037*t,.49+1.206*t),40,32,normal=(0,1,0))

# Frente: os recortes pertencem à chapa. Grade e faróis têm fundo/relevo próprios.
outer=bezier_loop([(-.9275,.55),(-.9275,1.237),(-.73,1.185),(-.50,1.155),(0,1.137),(.50,1.155),(.73,1.185),(.9275,1.237),(.9275,.55),(.80,.46),(.47,.455),(0,.51),(-.47,.455),(-.80,.46)],.10,8)
mask=bezier_loop([(-.48,1.126),(.48,1.126),(.555,.964),(.505,.691),(.41,.61),(-.41,.61),(-.505,.691),(-.555,.964)],.15,10)
light=bezier_loop([(.510,1.140),(.715,1.164),(.922,1.216),(.907,1.096),(.805,.986),(.594,.998),(.536,1.025)],.15,10)
lights=[[Vector((s*p.x,p.y)) for p in light] for s in [-1,1]]
sheet('Para-choque e testa com aberturas',outer,[mask]+lights,lambda p:(p.x,nose(p.x,p.y),p.y),paint,normal=(0,-1,0),spacing=.022)
def rim(name,loop,project,mat,width=.03,group='ACABAMENTOS'):
    c=sum(loop,Vector((0,0)))/len(loop);inner=[c+(p-c)*(1-width) for p in loop];n=len(loop)
    part(name,[project(p) for p in loop+inner],[(i,(i+1)%n,n+(i+1)%n,n+i) for i in range(n)],mat,group,.012,(0,-1,0))
    return inner
inn=rim('Moldura máscara STD',mask,lambda p:(p.x,nose(p.x,p.y,-.008),p.y),black,.10)
sheet('Fundo grade',inn,[],lambda p:(p.x,nose(p.x,p.y,.045),p.y),black,'ACABAMENTOS',(0,-1,0))
for z,w in [(1.087,.448),(1.025,.476),(.963,.48),(.735,.43),(.680,.39)]:
    tube('HILUX06 | Grelha horizontal',[(x,nose(x,z,.007),z) for x in [-w+2*w*i/36 for i in range(37)]],.009,black)
grid('Travessa central máscara',lambda u,t:(-.46+.92*u,nose(-.46+.92*u,.824+.08*t,-.006),.824+.08*t),40,6,black,normal=(0,-1,0))
for x in [-.37,-.25,-.13,0,.13,.25,.37]:
    tube('HILUX06 | Montante grade',[(x,nose(x,z,.015),z) for z in [.66,.75,.84,.95,1.09]],.005,black)
for side,loop in zip([-1,1],lights):
    inn=rim('Encaixe farol '+str(side),loop,lambda p:(p.x,nose(p.x,p.y,-.005),p.y),black,.065,'LUZES')
    sheet('Fundo óptico '+str(side),inn,[],lambda p:(p.x,nose(p.x,p.y,.016),p.y),black,'LUZES',(0,-1,0),.025)
    # Refletores côncavos de duas câmaras; superfície frontal deixa leitura do volume.
    for j,(x,z,rx,rz) in enumerate([(.636,1.074,.083,.052),(.793,1.101,.075,.047)]):
        def dish(u,v):
            ang=u*math.tau;r=.20+.80*v;px=side*(x+rx*r*math.cos(ang));pz=z+rz*r*math.sin(ang)
            return px,nose(px,pz,-.004)+.030*(1-r*r),pz
        grid('Refletor parabólico '+str((side,j)),dish,48,12,silver,'LUZES',(0,-1,0),.003)
        px=side*x
        cylinder('HILUX06 | Lâmpada '+str((side,j)),(px,nose(px,z,-.006),z),.018,.011,silver,'LUZES','Y',32)
    tube('HILUX06 | Guia óptica '+str(side),[(side*x,nose(side*x,z,-.011),z) for x,z in [(.559,1.017),(.65,1.018),(.79,1.006),(.885,1.102)]],.008,silver,'LUZES')
    # Rebaixo vertical com bordo reentrante.
    p=bezier_loop([(side*.742,.94),(side*.792,.94),(side*.802,.685),(side*.757,.594),(side*.687,.634),(side*.692,.689),(side*.735,.721)],.28)
    sheet('Rebaixo auxiliar '+str(side),p,[],lambda p:(p.x,nose(p.x,p.y,-.009),p.y),black,'ACABAMENTOS',(0,-1,0))
    # Retorno baixo entre nariz e começo do arco, acompanha a largura do para-lama.
    def lowerreturn(u,t):
        z=.52+.36*t;xa=.9275;ya=nose(xa,z);yb=-1.948;y=ya+(yb-ya)*u
        return side*(xa*(1-u)+sidewidth(y,z)*u),y,z
    grid('Retorno para-choque '+str(side),lowerreturn,18,18,paint,normal=(side,0,0))
for name,rx,rz in [('oval',.055,.036),('vertical',.021,.034),('horizontal',.050,.015)]:
    tube('HILUX06 | Toyota '+name,[(rx*math.cos(a),nose(rx*math.cos(a),1.01+rz*math.sin(a),-.021),1.01+rz*math.sin(a)) for a in [i*math.tau/64 for i in range(64)]],.0035,silver,closed=True)

# Capota policial com ombros e cantos arredondados; tampa lateral sem n-gon.
def cap_x(z):
    return interp([(1.29,.866),(1.52,.858),(1.68,.823),(1.79,.749),(1.848,.624),(1.86,0)],z)
def cap(u,v):
    a=math.pi*v;x=.865*math.cos(a);z=1.294+.566*(max(0,1-(abs(x)/.865)**6)**.43)
    y=1.179+1.562*u
    # Raios longitudinais nos dois topos, não seção extrudida rígida.
    z-=.035*(abs(2*u-1)**12);x*=1-.023*(abs(2*u-1)**12)
    return x,y,z
grid('Capota policial ombros curvos',cap,54,80,brown,'CAPOTA',normal=(0,0,1))
# Face traseira com vidro efetivamente recortado.
co=bezier_loop([(-.846,1.29),(.846,1.29),(.84,1.58),(.77,1.77),(.62,1.827),(-.62,1.827),(-.77,1.77),(-.84,1.58)],.25)
ci=bezier_loop([(-.674,1.375),(.674,1.375),(.699,1.48),(.655,1.704),(.53,1.762),(-.53,1.762),(-.655,1.704),(-.699,1.48)],.22)
sheet('Tampa traseira capota',co,[ci],lambda p:(p.x,2.746,p.y),brown,'CAPOTA',(0,1,0))
sheet('Vidro capota traseira',ci,[],lambda p:(p.x,2.741,p.y),glass,'VIDROS',(0,1,0))
tube('HILUX06 | Vedação traseira capota',[(p.x,2.749,p.y) for p in ci],.006,black,'CAPOTA',True)
for side in [-1,1]:
    loop=bezier_loop([(1.235,1.34),(1.72,1.34),(1.77,1.61),(1.64,1.775),(1.29,1.78),(1.205,1.59)],.3,12)
    sheet('Acesso lateral capota '+str(side),loop,[],lambda p:(side*(cap_x(p.y)+.004),p.x,p.y),brown,'CAPOTA',(side,0,0),.022)
    tube('HILUX06 | Junta acesso capota '+str(side),[(side*(cap_x(p.y)+.009),p.x,p.y) for p in loop],.003,black,'CAPOTA',True)
grid('Tampa caçamba',lambda u,t:(-.839+1.678*u,2.779+.011*math.sin(math.pi*u),.535+.75*t),48,28,paint,normal=(0,1,0))

# Visão de estudo da carroceria. O equipamento é preservado e volta após conferência.
hidden=[]
for o in scene.objects:
    if o.type=='EMPTY':continue
    if 'HILUX06' not in o.name and any(collections[g] in o.users_collection for g in ['INSCRICOES','CAPOTA','ACABAMENTOS','LUZES']):
        o.hide_render=True;o.hide_set(True);hidden.append(o.name)
scene['boas_v06_equipment_hidden_for_review']=json.dumps(hidden)
scene.name='VIATURA | Rondesp Hilux marrom v06'
scene['boas_review_status']='candidate; carroceria em revisão visual, não aprovada'
scene['boas_reference_method']='Dimensões nominais + silhueta lateral Toyota STD + frente/lateral SRX somente para forma compartilhada; acessórios Rondesp por fotos 3.1110'
scene.render.engine='BLENDER_WORKBENCH'
sh=scene.display.shading;sh.light='STUDIO';sh.studio_light='paint.sl';sh.color_type='SINGLE';sh.single_color=(.48,.48,.48)
sh.show_cavity=True;sh.cavity_type='WORLD';sh.curvature_ridge_factor=1;sh.curvature_valley_factor=1
sh.show_shadows=True;sh.show_specular_highlight=True;sh.studiolight_rotate_z=.6
scene.view_settings.view_transform='Standard';scene.view_settings.exposure=0
scene.render.resolution_x=1200;scene.render.resolution_y=750;scene.render.resolution_percentage=100
imgdir=repo/'artifacts/vehicles/rondesp'
bpy.context.view_layer.update()
for name,pos,scale in [('base-lateral',(-10,.16,1.1),6.5),('base-frente',(-7,-8,3.0),6.5),('base-frontal',(0,-10,1.2),3.6)]:
    scene.camera.location=pos;scene.camera.rotation_euler=(Vector((0,.16,1.03))-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.camera.data.type='ORTHO';scene.camera.data.ortho_scale=scale
    scene.render.filepath=str(imgdir/f'v06-{name}.png');bpy.ops.render.render(write_still=True)
scene.camera.location=(-7,-8,3);scene.camera.rotation_euler=(Vector((0,.16,1.03))-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.camera.data.ortho_scale=6.5
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            s=area.spaces.active;s.shading.type='SOLID';s.shading.color_type='MATERIAL';s.overlay.show_overlays=False
            s.region_3d.view_rotation=scene.camera.rotation_euler.to_quaternion();s.region_3d.view_location=(0,.16,1);s.region_3d.view_distance=7
bpy.data.libraries.write(str(out),{scene},path_remap='RELATIVE',fake_user=True,compress=True)
report={'file':out.relative_to(repo).as_posix(),'scene':scene.name,'asset_id':'vehicle-rondesp-pickup','status':'candidate','sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'parent':'blender/assets/vehicles/rondesp-pickup/marrom_v05.blend','changes':['capô mais baixo e inclinado','para-lamas com ombros e caixas abertas','cabine estreita no teto e curva dos vidros','chapas de porta com seção estampada','faróis com câmaras côncavas','capota com raios e tampas tesselladas'],'dimensions_source':'world/vehicles/hilux-dimensions.json','pending':['conferência e restauração de equipamento','aprovação visual','brasão PMBA','camuflagem exata'],'runtime_exported':False}
(repo/'docs/reports/blender/rondesp_marrom_v06.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def reopen():bpy.ops.wm.open_mainfile(filepath=str(out));return None
bpy.app.timers.register(reopen,first_interval=.5)
print(json.dumps({'saved':str(out.relative_to(repo)),'objects':len(scene.objects),'status':'candidate'}))
