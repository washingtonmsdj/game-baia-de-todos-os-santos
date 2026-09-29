"""Modelagem autoral ao vivo; medidas aproximadas para gameplay, referências fornecidas pelo usuário."""
import bpy, math, json
from mathutils import Vector
from pathlib import Path
from math import sin, cos, pi
NAME = "ONIBUS02 | Integra 31065"
scene = bpy.data.scenes.get(NAME)
if scene and len(scene.objects)>1:
    raise RuntimeError('Cena já modelada; preservar.')
scene = scene or bpy.data.scenes.new(NAME)
bpy.context.window.scene = scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1
cols = {}
for n in ["EXTERIOR","RODAS","PORTAS","INTERIOR_ESBOCO","GAMEPLAY","APRESENTACAO"]:
    c=bpy.data.collections.get("BUS02 | "+n) or bpy.data.collections.new("BUS02 | "+n)
    if c.name not in scene.collection.children: scene.collection.children.link(c)
    cols[n]=c
root=bpy.data.objects.get("BUS02_ROOT") or bpy.data.objects.new("BUS02_ROOT",None)
if root.name not in cols["EXTERIOR"].objects: cols["EXTERIOR"].objects.link(root)
root["asset_id"]="onibus-integra-31065"
root["status"]="modeling"
root["dimensions_source"]="Aproximação artística: 12,0 x 2,5 x 3,2 m; não medido"
root["reference_source"]="3 imagens anexadas pelo usuário em 2026-09-29"
root["reference_usage"]="PENDENTE_VERIFICACAO"
root["front_axis"]="-Y"
root["gameplay"]="Portas independentes; quadro 1 fechado, 50 aberto. Plataforma elevatória central no quadro 75. Integração de engine pendente."
def mat(n,c,metal=0,rough=.35,trans=0,em=0):
    m=bpy.data.materials.new("BUS02 | "+n); m.diffuse_color=(*c,1); m.use_nodes=True
    p=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None) or m.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
    output=next((n for n in m.node_tree.nodes if n.type=='OUTPUT_MATERIAL'),None) or m.node_tree.nodes.new('ShaderNodeOutputMaterial')
    m.node_tree.links.new(p.outputs['BSDF'],output.inputs['Surface'])
    p.inputs['Base Color'].default_value=(*c,1)
    p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough
    p.inputs['Transmission Weight'].default_value=0 if n=="Vidro fumê" else trans
    if em: p.inputs['Emission Color'].default_value=(*c,1); p.inputs['Emission Strength'].default_value=em
    return m
yellow=mat("Amarelo carroceria",(1,.57,.005),.18,.27)
white=mat("Branco perolado",(.86,.88,.89),.16,.3)
black=mat("Borracha",(.012,.016,.019),0,.65)
dark=mat("Moldura preta",(.018,.023,.028),.25,.32)
glass=mat("Vidro fumê",(.075,.14,.18),.1,.16,.55)
silver=mat("Aluminio",(.48,.54,.58),.8,.24)
chrome=mat("Refletor",(.8,.85,.9),.9,.16)
red=mat("Lanterna vermelha",(.65,.012,.015),.2,.25,.05,.3)
amber=mat("Indicador âmbar",(1,.28,.004),.2,.24,0,.4)
lens=mat("Lente farol",(.8,.9,1),.25,.17,.18,.25)
blue=mat("Azul acessibilidade",(.005,.06,.62),.1,.35)
green=mat("Verde faixa",(.005,.43,.13),.1,.35)
seatmat=mat("Bancos esboço",(.025,.08,.19),0,.8)
floor=mat("Piso antiderrapante",(.09,.105,.12),0,.9)
led=mat("LED âmbar",(1,.48,.04),0,.35,0,2)
def link(o,n,ma,col):
    o.name="BUS02 | "+n
    for c in list(o.users_collection): c.objects.unlink(o)
    cols[col].objects.link(o)
    if ma: o.data.materials.append(ma)
    if col!="APRESENTACAO": o.parent=root
    return o
def bevel(o,w=.025,s=3):
    b=o.modifiers.new("Bordas de fabricação",'BEVEL'); b.width=w; b.segments=s
    b=o.modifiers.new("Normais",'WEIGHTED_NORMAL')
    return o
def box(n,p,d,ma,col="EXTERIOR",b=.02):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p); o=link(bpy.context.object,n,ma,col)
    o.dimensions=d; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if b: bevel(o,b)
    return o
def mesh(n,v,f,ma,col="EXTERIOR",solid=0,b=0):
    me=bpy.data.meshes.new(n); me.from_pydata(v,[],f); me.update()
    o=bpy.data.objects.new("BUS02 | "+n,me); cols[col].objects.link(o); o.parent=root
    if ma: me.materials.append(ma)
    if solid: m=o.modifiers.new("Espessura",'SOLIDIFY'); m.thickness=solid
    if b: bevel(o,b,2)
    return o
def rod(n,a,b,r,ma,col="EXTERIOR",vertices=12):
    delta=Vector(b)-Vector(a)
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=delta.length,location=(Vector(a)+Vector(b))/2)
    o=link(bpy.context.object,n,ma,col); o.rotation_euler=delta.to_track_quat('Z','Y').to_euler()
    for p in o.data.polygons: p.use_smooth=True
    return o
def line(n,pts,r,ma,col="EXTERIOR",cyclic=False):
    c=bpy.data.curves.new(n,'CURVE'); c.dimensions='3D'; c.resolution_u=1;c.bevel_depth=r;c.bevel_resolution=2
    sp=c.splines.new('POLY');sp.points.add(len(pts)-1)
    for p,co in zip(sp.points,pts): p.co=(*co,1)
    sp.use_cyclic_u=cyclic
    o=bpy.data.objects.new("BUS02 | "+n,c); cols[col].objects.link(o);o.parent=root;c.materials.append(ma)
    return o
def rr(w,h,r):
    pts=[]
    for cx,cy,a in [(w/2-r,h/2-r,0),(-w/2+r,h/2-r,90),(-w/2+r,-h/2+r,180),(w/2-r,-h/2+r,270)]:
        for i in range(6):
            t=math.radians(a+i*18);pts.append((cx+r*cos(t),cy+r*sin(t)))
    return pts
def sidewindow(n,x,y,z,w,h):
    pts=rr(w,h,.12); inside=rr(w-.085,h-.085,.08); k=len(pts)
    v=[(x,y+a,z+b) for a,b in pts]+[(x,y+a,z+b) for a,b in inside]
    mesh(n+" moldura",v,[(i,(i+1)%k,(i+1)%k+k,i+k) for i in range(k)],dark,solid=.045,b=.009)
    mesh(n+" vidro",[(x*.995,y+a,z+b) for a,b in inside],[tuple(range(k))],glass,solid=.012)
    box(n+" travessa",(x,y,z+.17),(.045,w-.1,.035),dark,b=.008)
    box(n+" montante",(x,y,z+.36),(.046,.025,.34),dark,b=.004)
def text(n,body,p,size,ma,rot=(pi/2,0,0),col="EXTERIOR"):
    c=bpy.data.curves.new(n,'FONT');c.body=body;c.size=size;c.align_x='CENTER';c.align_y='CENTER';c.extrude=.0008;c.resolution_u=4
    o=bpy.data.objects.new("BUS02 | "+n,c);cols[col].objects.link(o);o.parent=root;o.location=p;o.rotation_euler=rot;c.materials.append(ma)
    return o
# Carroceria oca: painéis seguem caixas de roda, com dois vãos reais à direita.
axles=[-3.65,2.65]
doors=[(-5.05,1.14),(.25,1.18),(4.50,1.14)]
def inside_door(y): return any(abs(y-c)<w/2+.035 for c,w in doors)
def bottom(y):
    z=.40
    for a in axles:
        if abs(y-a)<.69: z=max(z,.56+math.sqrt(max(0,.69**2-(y-a)**2)))
    return z
for s in [-1,1]:
    cuts=set([-5.8,5.8])
    cuts.update(-5.8+i*11.6/180 for i in range(181))
    if s==1:
        for c,w in doors: cuts.update([c-w/2-.035,c+w/2+.035])
    ys=sorted(cuts)
    for lo,hi,ma in [(.4,1.4,white),(1.4,1.84,yellow)]:
        v=[];f=[]
        for a,b in zip(ys[:-1],ys[1:]):
            if s==1 and inside_door((a+b)/2): continue
            za=max(lo,bottom(a));zb=max(lo,bottom(b))
            if max(za,zb)>=hi: continue
            k=len(v);v.extend([(s*1.245,a,za),(s*1.245,b,zb),(s*1.245,b,hi),(s*1.245,a,hi)]);f.append(tuple(range(k,k+4)))
        mesh("Lateral %s faixa %.1f"%(s,lo),v,f,ma,solid=.05,b=.008)
    box("Longarina superior",(s*1.22,0,3.045),(.10,11.75,.20),yellow,b=.045)
    box("Friso sob janelas",(s*1.267,0,1.83),(.035,11.65,.045),black,b=.01)
    for a in axles:
        pts=[(s*1.27,a+.70*cos(t*pi/40),.56+.70*sin(t*pi/40)) for t in range(41)]
        line("Acabamento arco de roda",pts,.025,black)
    # Painéis de manutenção e refletores
    for y in [-5.7,-4.4,-2.75,-1.6,-.4,1.25,3.55,4.55,5.6]:
        if s==1 and inside_door(y): continue
        if bottom(y)>.6: continue
        line("Junta painel",[(s*1.275,y,.42),(s*1.275,y,1.1)],.0035,dark)
        box("Refletor vermelho",(s*1.28,y,1.02),(.016,.16,.035),red,b=.003)
        box("Refletor branco",(s*1.281,y+.12,1.02),(.017,.075,.035),white,b=.003)
    for y in [-4.35,-1.8,1.7,3.5,5.2]:
        if s==1 and inside_door(y): continue
        box("Pisca lateral",(s*1.28,y,.81),(.035,.11,.05),amber,b=.015)
    for yc in [4.95]:
        box("Grade motor fundo",(s*1.28,yc,1.13),(.035,.72,.86),dark,b=.045)
        for i in range(9):
            box("Aleta motor",(s*1.305,yc-.32+i*.08,1.13),(.035,.035,.78),white,b=.008)
# Janelas e pilares
for s,spans in [(-1,[(-5.45,-4.55),(-4.43,-2.55),(-2.43,-.83),(-.71,.89),(1.01,2.61),(2.73,4.20),(4.32,5.78)]),
                (1,[(-5.79,-5.68),(-4.40,-2.75),(-2.63,-1.75),(-1.63,-.42),(.92,1.62),(1.74,3.82),(5.18,5.78)])]:
    for i,(a,b) in enumerate(spans):
        if b-a<.3: continue
        sidewindow("Janela %s %02d"%(s,i),s*1.255,(a+b)/2,2.385,b-a,1.03)
    bounds=sorted(set([v for ab in spans for v in ab]))
    for y in bounds:
        if s==1 and inside_door(y): continue
        box("Pilar lateral",(s*1.218,y,2.39),(.075,.055,1.15),yellow,b=.014)
# teto fechado, bordas arredondadas; escotilhas e faixas Salvador
box("Teto",(0,0,3.125),(2.46,11.8,.18),yellow,b=.085)
for y in [-4,0,4]:
    box("Escotilha base",(0,y,3.235),(.87,.72,.08),dark,b=.06)
    box("Escotilha tampa",(0,y,3.275),(.80,.66,.06),silver,b=.045)
for s in [-1,1]:
    for y,ma in [(-3.7,white),(-2.8,blue),(-1.9,green)]:
        box("Faixa superior Salvador",(s*1.247,y,3.055),(.070,.90,.16),ma,b=.004)
# Frente curva por seções transversais, recuada nos cantos
def fy(x,z):
    return -6.04 + .24*(abs(x)/1.25)**4 + max(0,z-1.35)*.125 + max(0,.7-z)*.14
def frontpatch(n,x0,x1,z0,z1,ma,offset=0):
    nx=24;nz=8;v=[];f=[]
    for j in range(nz+1):
        z=z0+(z1-z0)*j/nz
        for i in range(nx+1):
            x=x0+(x1-x0)*i/nx
            if 'Para-brisa' in n:
                mid=(x0+x1)/2; x=mid+(x-mid)*(1-.085*abs(2*j/nz-1)**8)
            v.append((x,fy(x,z)+offset,z))
    for j in range(nz):
        for i in range(nx):
            k=j*(nx+1)+i;f.append((k,k+1,k+nx+2,k+nx+1))
    return mesh(n,v,f,ma,solid=.035,b=.008)
frontpatch("Mascara frontal amarela",-1.24,1.24,.80,1.52,yellow)
frontpatch("Parachoque frontal branco",-1.23,1.23,.39,.79,white)
frontpatch("Testeira amarela",-1.23,1.23,2.77,3.13,yellow)
frontpatch("Para-brisa borracha",-1.20,1.20,1.47,2.81,dark,-.012)
for a,b in [(-1.145,-.022),(.022,1.145)]:
    frontpatch("Para-brisa bipartido",a,b,1.525,2.755,glass,-.063)
for s in [-1,1]:
    frontpatch("Coluna frontal",s*1.14,s*1.25,1.45,2.82,yellow,-.002)
frontpatch("Letreiro alojamento",-1.08,1.08,2.86,3.08,dark,-.035)
text("Destino","100  CENTRO",(0,-5.892,2.965),.14,led)
text("Frota frente","31065",(-.61,-6.021,1.25),.14,white)
text("Integra frente","integra",(.49,-6.02,1.25),.21,white)
text("Salvador frente","Salvador",(.46,-6.026,1.115),.07,white)
# Faróis angulares e refletores separados
for s in [-1,1]:
    shape=[(s*.72,.83),(s*1.17,.98),(s*1.17,1.24),(s*.92,1.09)]
    mesh("Mascara farol",[(x,fy(x,z)-.036,z) for x,z in shape],[(0,1,2,3)],dark,solid=.04,b=.018)
    for x,z,r,ma in [(s*1.055,1.087,.074,lens),(s*.91,1.005,.054,lens),(s*.84,.928,.036,amber)]:
        y=fy(x,z)-.067
        rod("Aro farol",(x,y+.024,z),(x,y-.012,z),r+ .009,chrome,vertices=24)
        rod("Lente farol",(x,y-.013,z),(x,y-.02,z),r,ma,vertices=24)
    box("Rebaixo neblina",(s*.94,-5.982,.58),(.29,.06,.17),dark,b=.04)
    rod("Farol neblina",(s*.94,-6.03,.58),(s*.94,-6.05,.58),.054,lens,vertices=20)
    # limpadores
    line("Braco limpador",[(s*.72,-6.046,1.50),(s*.11,-5.983,2.09)],.015,dark)
    line("Palheta",[(s*.12,-5.99,1.82),(s*.12,-5.945,2.41)],.017,black)
    line("Suporte retrovisor",[(s*1.16,-5.70,2.74),(s*1.47,-5.87,2.82),(s*1.62,-5.97,2.65),(s*1.62,-5.97,2.35)],.023,dark)
    box("Retrovisor carenagem",(s*1.62,-5.97,2.34),(.18,.22,.42),dark,b=.072)
    box("Retrovisor espelho",(s*1.62,-5.852,2.34),(.135,.015,.34),chrome,b=.04)
for z,w in [(1.0,.74),(.865,1.38)]:
    box("Entrada ar frontal",(0,-6.023,z),(w,.025,.044),dark,b=.02)
box("Placa moldura",(0,-6.03,.565),(.53,.035,.17),dark,b=.016)
box("Placa",(0,-6.054,.565),(.48,.016,.135),white,b=.009)
text("Placa texto","BAO 1001",(0,-6.065,.564),.063,dark)
# Emblema geométrico central
pts=[(.075*cos(i*2*pi/32),-6.045,1.11+.075*sin(i*2*pi/32)) for i in range(32)]
line("Aro emblema",pts,.008,chrome,cyclic=True)
for t in [pi/2,pi/2+2*pi/3,pi/2+4*pi/3]:
    rod("Raio emblema",(0,-6.055,1.11),(.071*cos(t),-6.055,1.11+.071*sin(t)),.006,chrome)
# Traseira: interpretação simplificada, não há fotografia traseira
box("Traseira inferior",(0,5.91,1.08),(2.48,.17,1.34),white,b=.10)
box("Traseira superior",(0,5.91,2.42),(2.48,.16,1.30),yellow,b=.10)
box("Vidro traseiro moldura",(0,6.005,2.42),(2.18,.05,.86),dark,b=.12)
box("Vidro traseiro",(0,6.034,2.42),(2.06,.018,.74),glass,b=.095)
for s in [-1,1]:
    box("Lanterna traseira base",(s*1.10,6.012,1.4),(.17,.06,.69),dark,b=.055)
    for z,ma in [(1.64,red),(1.43,amber),(1.22,red)]:
        box("Lente traseira",(s*1.10,6.05,z),(.12,.025,.16),ma,b=.03)
box("Parachoque traseiro",(0,6,.46),(2.40,.19,.20),white,b=.07)
for i in range(9):
    box("Veneziana traseira",(0,6.013,.83+i*.047),(1.53,.018,.021),dark,b=.006)
text("Frota traseira","31065",(0,6.018,1.78),.20,yellow,(pi/2,0,pi))
# Rodagem em meshes independentes com eixo local X
for yi,y in enumerate(axles):
    for s in [-1,1]:
        hub=bpy.data.objects.new("BUS02 | Eixo roda %s %s"%(yi,s),None);cols["RODAS"].objects.link(hub);hub.parent=root;hub.location=(s*1.09,y,.56)
        parts=[]
        for x in ([s*1.085] if yi==0 else [s*.91,s*1.16]):
            bpy.ops.mesh.primitive_torus_add(major_segments=40,minor_segments=12,location=(x,y,.56),rotation=(0,pi/2,0),major_radius=.423,minor_radius=.132)
            o=link(bpy.context.object,"Pneu",black,"RODAS");parts.append(o)
            for p in o.data.polygons:p.use_smooth=True
        x=s*1.30
        parts.append(rod("Aro roda",(x-s*.12,y,.56),(x,y,.56),.335,silver,"RODAS",40))
        parts.append(rod("Rebaixo aro",(x+s*.003,y,.56),(x+s*.012,y,.56),.267,dark,"RODAS",32))
        parts.append(rod("Disco roda",(x+s*.016,y,.56),(x+s*.035,y,.56),.235,silver,"RODAS",32))
        parts.append(rod("Cubo",(x,y,.56),(x+s*.10,y,.56),.10,silver,"RODAS",24))
        for i in range(10):
            t=i*2*pi/10
            parts.append(rod("Parafuso roda",(x+s*.034,y+.153*cos(t),.56+.153*sin(t)),(x+s*.060,y+.153*cos(t),.56+.153*sin(t)),.017,chrome,"RODAS",6))
            parts.append(rod("Ventilacao aro",(x+s*.016,y+.276*cos(t),.56+.276*sin(t)),(x+s*.024,y+.276*cos(t),.56+.276*sin(t)),.031,black,"RODAS",12))
        for o in parts:
            mw=o.matrix_world.copy();o.parent=hub;o.matrix_world=mw
# Portas bipartidas com pivôs e animação de apresentação
for di,(cy,w) in enumerate(doors):
    for j in [-1,1]:
        pivot=bpy.data.objects.new("BUS02 | Porta %d pivo %d"%(di,j),None);cols["PORTAS"].objects.link(pivot);pivot.parent=root
        pivot.location=(1.26,cy+j*w/2,.40)
        members=[]
        yp=cy+j*w/4
        members.append(box("Porta folha",(1.27,yp,1.60),(.052,w/2-.018,2.40),dark,"PORTAS",.02))
        members.append(box("Porta vidro",(1.304,yp,1.66),(.018,w/2-.105,2.14),glass,"PORTAS",.018))
        for zz in [.46,1.10,2.72]:
            members.append(box("Porta travessa",(1.322,yp,zz),(.022,w/2-.075,.034),silver,"PORTAS",.006))
        members.append(rod("Porta puxador",(1.337,yp-j*.13,1.13),(1.337,yp-j*.13,1.76),.013,yellow,"PORTAS"))
        for o in members:
            mw=o.matrix_world.copy();o.parent=pivot;o.matrix_world=mw
        for frame,angle in [(1,0),(30,0),(50,j*pi/2),(85,j*pi/2),(110,0)]:
            pivot.rotation_euler.z=angle;pivot.keyframe_insert(data_path='rotation_euler',frame=frame)
    box("Porta calha",(1.29,cy,2.84),(.14,w+.16,.07),dark,b=.016)
# Esboço interno oco e acessos. Piso em faixas evita tampar os vãos.
box("Piso corredor",(0,0,.765),(1.18,11.56,.09),floor,"INTERIOR_ESBOCO")
box("Piso lado motorista",(-.87,0,.765),(.56,11.56,.09),floor,"INTERIOR_ESBOCO")
intervals=[(-5.78,-5.65),(-4.44,-.38),(.89,3.89),(5.11,5.78)]
for a,b in intervals:box("Piso lateral direito",(.88,(a+b)/2,.765),(.58,b-a,.09),floor,"INTERIOR_ESBOCO")
for xx,zz in [(1.08,.40),(.81,.59)]:
    box("Degrau entrada",(xx,-5.05,zz),(.29,1.10,.09),floor,"INTERIOR_ESBOCO")
    box("Borda degrau",(xx+.13,-5.05,zz+.05),(.025,1.1,.015),yellow,"INTERIOR_ESBOCO",.003)
platform=box("Plataforma elevatoria",(.90,.25,.765),(.72,1.12,.09),floor,"GAMEPLAY",.014)
platform["status"]="geometria e animacao de conceito; mecanica runtime pendente"
for frame,loc in [(1,(.90,.25,.765)),(50,(.90,.25,.765)),(62,(1.65,.25,.765)),(75,(1.65,.25,.20)),(85,(1.65,.25,.765)),(100,(.90,.25,.765))]:
    platform.location=loc;platform.keyframe_insert(data_path="location",frame=frame)
for s in [-1,1]:
    for a in axles:
        box("Caixa roda interna",(s*.91,a,.98),(.57,1.40,.42),floor,"INTERIOR_ESBOCO",.13)
for y in [-3.35,-2.5,-1.65,1.45,3.50,5.3]:
    for s in [-1,1]:
        if s==1 and y in [1.45]:continue
        box("Banco assento",(s*.86,y,1.19),(.53,.49,.12),seatmat,"INTERIOR_ESBOCO",.045)
        box("Banco encosto",(s*.86,y+.23,1.49),(.53,.10,.61),seatmat,"INTERIOR_ESBOCO",.055)
        rod("Banco apoio",(s*.86,y,.82),(s*.86,y,1.13),.025,silver,"INTERIOR_ESBOCO")
box("Painel motorista",(-.61,-5.56,1.32),(1.0,.43,.32),dark,"INTERIOR_ESBOCO",.1)
box("Banco motorista",(-.65,-4.88,1.22),(.50,.48,.15),seatmat,"INTERIOR_ESBOCO",.05)
box("Encosto motorista",(-.65,-4.65,1.52),(.50,.10,.58),seatmat,"INTERIOR_ESBOCO",.05)
rod("Coluna volante",(-.65,-5.20,1.05),(-.65,-5.4,1.55),.035,dark,"INTERIOR_ESBOCO")
bpy.ops.mesh.primitive_torus_add(major_segments=24,minor_segments=8,major_radius=.19,minor_radius=.017,location=(-.65,-5.4,1.56),rotation=(.45,0,0))
link(bpy.context.object,"Volante esboco",dark,"INTERIOR_ESBOCO")
for s in [-1,1]:
    for y in [-4.4,-1.1,1.1,4.0]:
        rod("Balaustre",(s*.60,y,.82),(s*.60,y,2.8),.017,yellow,"INTERIOR_ESBOCO")
    rod("Corrimao superior",(s*.60,-4.4,2.78),(s*.60,5.35,2.78),.018,yellow,"INTERIOR_ESBOCO")
# Identidade visual geométrica, sem rasterizar as imagens fornecidas
for s in [-1,1]:
    rot=(pi/2,0,pi/2 if s==1 else -pi/2)
    text("Marca lateral","integra",(s*1.282,1.48,1.57),.34,yellow,rot)
    text("Cidade lateral","Salvador",(s*1.284,1.45,1.30),.115,dark,rot)
    text("Numero lateral","31065",(s*1.284,-2.9,1.62),.24,dark,rot)
    # Símbolo de acesso desenhado com geometria
    x=s*1.286;y=-4.22;z=1.20
    box("Sinal acessibilidade",(x,y,z),(.018,.28,.29),blue,b=.015)
    xp=s*1.30
    pts=[(xp,y+.073*cos(t),z-.037+.073*sin(t)) for t in [i*2*pi/30 for i in range(31)]]
    line("Cadeira roda",pts,.008,white)
    line("Cadeira estrutura",[(xp,y-.04,z+.075),(xp,y-.028,z-.018),(xp,y+.062,z-.018),(xp,y+.096,z-.075)],.009,white)
    rod("Cadeira cabeca",(xp,y-.045,z+.100),(xp+s*.006,y-.045,z+.100),.022,white,vertices=16)
# Estúdio e enquadramento
scene.world=bpy.data.worlds.new("BUS02 | Estudio");scene.world.use_nodes=True
bg=next((n for n in scene.world.node_tree.nodes if n.type=='BACKGROUND'),None) or scene.world.node_tree.nodes.new('ShaderNodeBackground')
wo=next((n for n in scene.world.node_tree.nodes if n.type=='OUTPUT_WORLD'),None) or scene.world.node_tree.nodes.new('ShaderNodeOutputWorld')
scene.world.node_tree.links.new(bg.outputs[0],wo.inputs['Surface'])
bg.inputs[0].default_value=(.16,.19,.23,1)
bg.inputs[1].default_value=.5
ground=box("Chao estudio",(0,0,-.055),(200,200,.08),mat("Estudio",(.19,.22,.26),0,.8),"APRESENTACAO",0)
for n,p,energy,size in [("Key",(5,-7,10),2300,8),("Fill",(-6,-1,6),1800,7),("Rim",(3,6,8),2500,6)]:
    d=bpy.data.lights.new(n,'AREA');d.energy=energy;d.shape='DISK';d.size=size
    o=bpy.data.objects.new(n,d);cols["APRESENTACAO"].objects.link(o);o.location=p;o.rotation_euler=(Vector((0,0,1.4))-o.location).to_track_quat('-Z','Y').to_euler()
camd=bpy.data.cameras.new("BUS Camera");cam=bpy.data.objects.new("BUS Camera",camd);cols["APRESENTACAO"].objects.link(cam)
cam.location=(15,-18,8);cam.rotation_euler=(Vector((0,0,1.4))-cam.location).to_track_quat('-Z','Y').to_euler();camd.type='ORTHO';camd.ortho_scale=15
scene.camera=cam;scene.render.engine='CYCLES';scene.cycles.samples=24
scene.render.resolution_x=1600;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.frame_start=1;scene.frame_end=110;scene.frame_set(1)
for fr,n in [(1,"FECHADO"),(50,"PORTAS ABERTAS"),(75,"ELEVADOR BAIXO"),(110,"FECHADO")]:scene.timeline_markers.new(n,frame=fr)
scene.view_settings.view_transform='AgX'
bpy.context.view_layer.update()
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        sp=area.spaces.active;sp.region_3d.view_perspective='CAMERA';sp.overlay.show_overlays=False
        sp.shading.type='MATERIAL'

# Passe de carroceria Torino: costuras limpas e seção arredondada do teto.
import bmesh
from mathutils import Matrix
for o in list(scene.objects):
    if o.type=='MESH' and o.name.startswith("BUS02 | Lateral"):
        bm=bmesh.new();bm.from_mesh(o.data)
        bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001)
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
        if "1.4" in o.name:
            o.data.materials.append(white)
            for p in o.data.polygons:
                cy=sum(o.data.vertices[i].co.y for i in p.vertices)/len(p.vertices)
                if -2.85<cy<4.30:p.material_index=1
# Novo teto curvo contínuo, com bordas caídas e cabeceiras arredondadas.
old=bpy.data.objects.get("BUS02 | Teto")
if old:bpy.data.objects.remove(old,do_unlink=True)
v=[];f=[]
xs=[-1.25,-1.24,-1.20,-1.12,-.96,-.72,0,.72,.96,1.12,1.20,1.24,1.25]
zs=[2.995,3.07,3.15,3.20,3.225,3.24,3.25,3.24,3.225,3.20,3.15,3.07,2.995]
for yy in [-5.94,-5.88,-5.72,5.72,5.88,5.94]:
    shrink=.97 if abs(yy)>5.9 else 1
    drop=.09 if abs(yy)>5.9 else (.025 if abs(yy)>5.8 else 0)
    for x,z in zip(xs,zs):v.append((x*shrink,yy,z-drop))
k=len(xs)
for j in range(5):
    for i in range(k-1):
        a=j*k+i;f.append((a,a+1,a+k+1,a+k))
roof=mesh("Teto abaulado",v,f,yellow,solid=.035)
for p in roof.data.polygons:p.use_smooth=True
# Acabamento superior arredondado ao redor do para-brisa.
for s in [-1,1]:
    line("Canto frontal curvo",[(s*1.17,fy(s*1.17,1.48)-.035,1.48),(s*1.22,fy(s*1.22,1.65)-.035,1.65),(s*1.22,fy(s*1.22,2.55)-.035,2.55),(s*1.18,fy(s*1.18,2.78)-.035,2.78),(s*1.07,fy(s*1.07,2.88)-.035,2.88)],.048,yellow)
# Para-choque amarelo e traseira do novo concept.
for o in scene.objects:
    if any(o.name.startswith("BUS02 | "+n) for n in ["Parachoque frontal branco","Traseira inferior","Parachoque traseiro"]):
        o.data.materials.clear();o.data.materials.append(yellow)
    if o.name.startswith("BUS02 | Traseira inferior") or o.name.startswith("BUS02 | Traseira superior"):
        for m in o.modifiers:
            if m.type=='BEVEL':m.width=.16;m.segments=6
for y in [-5.05,4.50]:
    text("Identificacao porta","Entrada" if y<0 else "Saida",(1.29,y,2.945),.10,dark,(pi/2,0,pi/2))
text("Terminal","Uso nos Terminais",(1.29,.25,2.945),.085,dark,(pi/2,0,pi/2))
text("Torino frontal","TORINO",(0,fy(0,1.52)-.09,1.48),.075,silver)
# Degraus também no vão traseiro.
for xx,zz in [(1.08,.40),(.81,.59)]:
    box("Degrau saida",(xx,4.50,zz),(.29,1.10,.09),floor,"INTERIOR_ESBOCO")
    box("Borda degrau saida",(xx+.13,4.50,zz+.05),(.025,1.1,.015),yellow,"INTERIOR_ESBOCO",.003)
# Transferir lateral, interior e pivôs juntos; malhas com escala positiva e normais corretas.
# Conjugação de coordenadas evita escala negativa no asset; textos continuam legíveis.
S=Matrix.Diagonal((-1,1,1,1))
asset_objects=[o for o in scene.objects if o!=root and o.name.startswith("BUS02 |") and o.name!="BUS02 | Chao estudio"]
for o in asset_objects:
    o.matrix_basis=S@o.matrix_basis@S
    o.matrix_parent_inverse=S@o.matrix_parent_inverse@S
    if o.type=='MESH':
        o.data.transform(S)
        bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
    elif o.type=='CURVE':
        for sp in o.data.splines:
            for p in sp.points:p.co.x=-p.co.x
            for p in sp.bezier_points:
                p.co.x=-p.co.x;p.handle_left.x=-p.handle_left.x;p.handle_right.x=-p.handle_right.x
    if o.animation_data and o.animation_data.action:
        action=o.animation_data.action
        curves=[]
        if hasattr(action,'fcurves'):curves.extend(action.fcurves)
        for layer in action.layers:
            for strip in layer.strips:
                if hasattr(strip,'channelbags'):
                    for bag in strip.channelbags:curves.extend(bag.fcurves)
        for fc in curves:
            if (fc.data_path=='location' and fc.array_index==0) or (fc.data_path=='rotation_euler' and fc.array_index in [1,2]):
                for kp in fc.keyframe_points:
                    kp.co.y=-kp.co.y;kp.handle_left.y=-kp.handle_left.y;kp.handle_right.y=-kp.handle_right.y
root["door_side"]="-X; transferida conforme pedido do usuário"
root["reference_source"]="Concept Torino 2014 31065 fornecido pelo usuário; anterior preservado."
root["revision"]="v02: três portas na lateral oposta, teto curvo, vidro sem ruído, pintura revista"
cam.location=(-15,-19,6.8);cam.rotation_euler=(Vector((0,0,1.4))-cam.location).to_track_quat('-Z','Y').to_euler();camd.ortho_scale=14.8
scene.frame_set(1)
bpy.context.view_layer.update()

# Salva somente o asset, sem regravar a cidade carregada.
out=Path(bpy.data.filepath).parent/"assets"/"onibus_torino_31065_v02.blend"
out.parent.mkdir(parents=True,exist_ok=True)
if out.exists(): raise RuntimeError("Arquivo de asset já existe; não sobrescrever.")
note=bpy.data.texts.new("ONIBUS02 | Notas de modelagem")
note.write("Exterior detalhado baseado nas três imagens do usuário. Interior em esboço. Traseira aproximada, sem vista de referência. Dimensões artísticas, não medidas. Acesso frontal por degraus e central por plataforma. Quadro 50 abre portas; quadro 75 baixa elevador. Sem validação em engine. Referências com proveniência pendente. Cidade preservada.")
scene["asset_notes"]=note.as_string()
bpy.data.libraries.write(str(out),{scene},fake_user=True,compress=True)
print(json.dumps({"asset":str(out),"scene":scene.name,"objects":len(scene.objects),"saved":True},ensure_ascii=False))
