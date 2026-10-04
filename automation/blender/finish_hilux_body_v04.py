"""Fecha junções, perfil frontal STD, pneus e fixações da revisão V04 ao vivo."""
import bpy,bmesh,math,json,hashlib,ast
from pathlib import Path
from mathutils import Vector,Matrix
repo=Path(__file__).resolve().parents[2];scene=bpy.context.scene
assert scene.name=='VIATURA | Rondesp Hilux marrom v04'
root=scene.objects['RDP01_ROOT | viatura']
scope={'bpy':bpy,'bmesh':bmesh,'math':math,'Vector':Vector,'Matrix':Matrix,'root':root,'collections':{k:bpy.data.collections['RDP01 | '+k] for k in ['CARROCERIA','PORTAS','CAPOTA','VIDROS','RODAS','CHASSIS','LUZES','ACABAMENTOS','INSCRICOES','APRESENTACAO']}}
for key,label in [('brown','Pintura marrom Rondesp'),('black','Polímero preto'),('steel','Aço preto rodas'),('silver','Metal acetinado'),('white','Inscrição branca'),('glass','Vidro fumê'),('clear','Lentes transparentes'),('red','Lentes vermelhas'),('rubber','Borracha pneus')]:scope[key]=bpy.data.materials['RDP01 | '+label]
tree=ast.parse((repo/'automation/blender/create_rondesp_pickup_v01.py').read_text(encoding='utf-8'))
for n in ['mesh','box','tube','cylinder','parent_keep']:
    fn=next(f for f in tree.body if isinstance(f,ast.FunctionDef) and f.name==n);exec(compile(ast.Module(body=[fn],type_ignores=[]),'<helper>','exec'),scope)
for n in ['curve','part','grid','rounded','ring','arch','sidewidth','nosepoint']:
    tree2=ast.parse((repo/'automation/blender/rebuild_hilux_body_v04.py').read_text(encoding='utf-8'))
    fn=next(f for f in tree2.body if isinstance(f,ast.FunctionDef) and f.name==n);exec(compile(ast.Module(body=[fn],type_ignores=[]),'<shape>','exec'),scope)
scope.update(axles=(-1.43,1.655),wz=.38815,front=-2.43,paint=bpy.data.materials['RDP01 | Camuflagem marrom candidata'])
mesh,box,tube,cylinder,parent_keep,grid,part,curve,rounded,nosepoint,sidewidth=[scope[n] for n in ['mesh','box','tube','cylinder','parent_keep','grid','part','curve','rounded','nosepoint','sidewidth']]
brown,black,steel,silver,white,glass,clear,red,rubber=[scope[n] for n in ['brown','black','steel','silver','white','glass','clear','red','rubber']]
paint=scope['paint'];front=-2.43

# A frente STD tem uma máscara preta que envolve as duas grelhas.
for ob in list(scene.objects):
    if any(x in ob.name for x in ['Moldura grade superior','Fundo grade superior','Aleta grade','Centro para-choque','Entrada inferior','Aleta inferior']):bpy.data.objects.remove(ob,do_unlink=True)
gp=rounded([(-.492,1.195),(.492,1.195),(.577,1.032),(.530,.699),(.43,.624),(-.43,.624),(-.530,.699),(-.577,1.032)],.10)
scope['ring']('Moldura envolvente STD',gp,lambda p:nosepoint(p.x,p.y,-.012),black,'ACABAMENTOS',inset=.89)
part('Fundo máscara STD',[nosepoint(p.x,p.y,.014) for p in gp],[tuple(range(len(gp)))],black,'ACABAMENTOS')
grid('Ponte central grade STD',lambda u,t:nosepoint(-.49+.98*u,.834+.064*t,-.022),24,4,steel,'ACABAMENTOS')
for j,z in enumerate([.959,1.031,1.099,1.157]):
    w=.444 if j==3 else .485
    tube('HILUX04 | Aleta superior STD '+str(j),[nosepoint(-w+2*w*k/36,z,-.031) for k in range(37)],.009,steel)
for x in [-.42,-.28,-.14,.14,.28,.42]:tube('HILUX04 | Grade vertical '+str(x),[nosepoint(x,.911,-.026),nosepoint(x,1.175,-.026)],.008,steel)
for j in range(4):tube('HILUX04 | Grade inferior STD '+str(j),[nosepoint(-.433+.866*k/36,.688+j*.042,-.029) for k in range(37)],.006,steel)
for x in [-.36,-.24,-.12,0,.12,.24,.36]:tube('HILUX04 | Grade inferior nervura '+str(x),[nosepoint(x,.673,-.025),nosepoint(x,.823,-.025)],.004,steel)
grid('Base arredondada para-choque',lambda u,t:nosepoint(-.51+1.02*u,.495+.155*t),32,12,paint)
box('HILUX04 | Reforço placa STD',(0,-2.452,.855),(.43,.03,.126),black,bevel=.018)

# Fecha a junção frontal/lateral por chapa curva, com retorno real do farol.
for side in (-1,1):
    def bridge(u,t):
        z=.53+.486*t;a=Vector(nosepoint(side*.909,z));b=Vector((side*sidewidth(-2.112,z),-2.112,z))
        return tuple(a.lerp(b,u))
    grid(f'Junção curva nariz para-lama {side}',bridge,8,32,paint)
    f=scene.objects[f'RDP01 | HILUX04 | Para-lama dianteiro {side:+}']
    bm=bmesh.new();bm.from_mesh(f.data)
    cut=[p for p in bm.faces if p.calc_center_median().y<-2.01 and p.calc_center_median().z>1.083]
    bmesh.ops.delete(bm,geom=cut,context='FACES');bm.to_mesh(f.data);bm.free()
    poly=rounded([(-2.148,1.205),(-2.008,1.230),(-2.024,1.167),(-2.110,1.091)],.10)
    part(f'Retorno farol lateral {side}',[(side*.900,p.x,p.y) for p in poly],[tuple(range(len(poly)))],clear,'LUZES',thickness=.004)
    tube(f'HILUX04 | Vedação retorno farol {side}',[(side*.905,p.x,p.y) for p in poly],.006,black,'LUZES',True)
    # Transição capô/fender arredondada; remove o vão lateral entre chapas.
    grid(f'Ombro capô para-lama {side}',lambda u,t:(side*(.864+.031*t),-2.103+1.13*u,curve([(-2.103,1.218),(-1.70,1.262),(-.973,1.295)],-2.103+1.13*u)-.008*t),40,6,paint)

# Fixações do quebra-mato estavam ainda nas coordenadas do nariz anterior.
for o in scene.objects:
    if o.name.startswith('RDP01 | Base quebra-mato'):o.location.y+=.29
    if 'POLÍCIA MILITAR traseira' in o.name:o.location.x=0
    if o.type=='FONT' and ('Prefixo vidro' in o.name):o.location.z-=.11
    if o.name.startswith('RDP01 | Para-choque traseiro') or o.name.startswith('RDP01 | Apoio passo'):o.location.y-=.11

# A medida total stock inclui os para-choques, não a caçamba isoladamente.
for o in scene.objects:
    if o.name.startswith('RDP01 | HILUX04 | Lateral caçamba'):
        for v in o.data.vertices:v.co.y=1.17+(v.co.y-1.17)*1.58/(2.85-1.17)
    if o.name.startswith('RDP01 | HILUX04 | Tampa caçamba'):o.location.y-=.074
    if 'capota' in o.name.lower() and o.type=='MESH':
        if o.location.length<.01:
            for v in o.data.vertices:v.co.y=1.17+(v.co.y-1.17)*1.58/(2.845-1.17)
        else:o.location.y-=.07
    elif 'capota' in o.name.lower() and o.type=='CURVE':
        for sp in o.data.splines:
            for p in sp.points:p.co.y=1.17+(p.co.y-1.17)*1.58/(2.845-1.17)
    if o.type=='FONT' and o.location.y>2.7:o.location.y-=.125

# Capota com topo largo e ombros de grande raio, como na viatura; sem perfil em barril.
cap=scene.objects.get('RDP01 | HILUX04 | Capota arredondada')
if cap:bpy.data.objects.remove(cap,do_unlink=True)
def capshape(u,t):
    angle=math.pi*t;x=.889*math.cos(angle);z=1.195+.685*math.sqrt(max(0,1-(abs(x)/.889)**8))
    return (x,1.17+1.58*u,z+.004*math.sin(math.pi*u))
grid('Capota topo largo Hilux',capshape,42,80,brown,'CAPOTA')
# Remove o fechamento traseiro sólido: o vidro ocupa uma abertura de verdade.
for o in list(scene.objects):
    if o.name.startswith('RDP01 | HILUX04 | Fechamento capota'):bpy.data.objects.remove(o,do_unlink=True)
part('Parede frontal capota',[capshape(0,j/80) for j in range(81)],[tuple(range(81))],brown,'CAPOTA')
outer=rounded([(-.88,1.20),(.88,1.20),(.88,1.60),(.79,1.78),(.67,1.875),(-.67,1.875),(-.79,1.78),(-.88,1.60)],.12)
inner=rounded([(-.68,1.34),(.68,1.34),(.72,1.49),(.67,1.73),(.55,1.78),(-.55,1.78),(-.67,1.73),(-.72,1.49)],.12)
n=len(outer);part('Aro tampa capota traseira',[(p.x,2.752,p.y) for p in outer+inner],[(i,(i+1)%n,n+(i+1)%n,n+i) for i in range(n)],brown,'CAPOTA')

# Rodas em coordenadas locais controladas. Reconstrói banda para eliminar blocos desalinhados.
for side in (-1,1):
    for ai,y in enumerate((-1.43,1.655)):
        pivot=scene.objects[f'RDP01 | Eixo giro roda {ai} {side:+}']
        for o in list(pivot.children):bpy.data.objects.remove(o,do_unlink=True)
        def wheelpart(name,vs,fs,mat):
            ob=part(f'{name} {ai} {side}',vs,fs,mat,'RODAS',thickness=0)
            ob.parent=pivot;ob.matrix_parent_inverse=Matrix.Identity(4);ob.matrix_basis=Matrix.Identity(4)
            return ob
        n=128;profile=[(-.105,.216),(-.131,.245),(-.1325,.295),(-.12,.356),(-.10,.382),(-.075,.386),(.075,.386),(.10,.382),(.12,.356),(.1325,.295),(.131,.245),(.105,.216)]
        vs=[(x,r*math.sin(i*math.tau/n),r*math.cos(i*math.tau/n)) for x,r in profile for i in range(n)]
        fs=[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(len(profile)-1) for i in range(n)]
        wheelpart('Pneu 265 65 R17',vs,fs,rubber)
        # Blocos orientados radialmente; volume máximo do pneu é o nominal .38815.
        vv=[];ff=[]
        for i in range(84):
            for row in range(3):
                a=(i+(row%2)*.36)*math.tau/84; center=Vector((-.07+.07*row,.3865*math.sin(a),.3865*math.cos(a)))
                radial=Vector((0,math.sin(a),math.cos(a)));tangent=Vector((0,math.cos(a),-math.sin(a)))
                base=len(vv)
                for dx,dy,dz in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]:
                    vv.append(tuple(center+Vector((dx*.03,0,0))+tangent*(dy*.010)+radial*(dz*.00165)))
                ff.extend(tuple(base+k for k in f) for f in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
        ob=wheelpart('Banda de rodagem',vv,ff,rubber)
        for p in ob.data.polygons:p.use_smooth=False
        # Aro estampado de 17", com perfurações reais e borda de montagem.
        n=256;rs=[(.062,.130),(.099,.115),(.135,.100),(.164,.098),(.184,.109),(.206,.132),(.2159,.127)]
        vs=[(side*x,r*math.sin(i*math.tau/n),r*math.cos(i*math.tau/n)) for r,x in rs for i in range(n)]
        fs=[]
        for j in range(len(rs)-1):
            for i in range(n):
                if j in [2,3] and 4<=(i%16)<=11:continue
                fs.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
        rim=wheelpart('Aro aço 17 perfurado',vs,fs,steel);sol=rim.modifiers.new('Chapa aro','SOLIDIFY');sol.thickness=.004
        bevel=rim.modifiers.new('Borda estampada','BEVEL');bevel.width=.002;bevel.segments=3
        for a,r in [(0,.058)]+[(i*math.tau/6,.009) for i in range(6)]:
            rr=0 if r>.05 else .072
            ob=cylinder('HILUX04 | Cubo porca', (side*.144,rr*math.sin(a),rr*math.cos(a)),r,.018,steel,vertices=32 if r>.05 else 6)
            ob.parent=pivot;ob.matrix_parent_inverse=Matrix.Identity(4)

# Inscrições acompanham as chapas abauladas, eliminando letras flutuantes.
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
for o in list(scene.objects):
    if o.type!='FONT' or abs(o.location.x)<.5 or o.location.y>2.7:continue
    ev=o.evaluated_get(dg);me=bpy.data.meshes.new_from_object(ev)
    body=o.data.body;side=1 if o.location.x>0 else -1
    for v in me.vertices:
        p=o.matrix_world@v.co;p.x=side*(sidewidth(p.y,p.z)+.0025);v.co=p
    ob=bpy.data.objects.new(o.name,me);scope['collections']['INSCRICOES'].objects.link(ob);ob.parent=root;ob['boas_inscription_text']=body
    bpy.data.objects.remove(o,do_unlink=True)

# Painéis nunca usam um vinco artificial muito grosso para parecerem acabados.
for o in scene.objects:
    if o.type=='CURVE' and any(x in o.name for x in ['Junta porta','Junta capô']):o.data.bevel_depth=.0016
glass.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.24
clear.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.18
bpy.context.view_layer.update()
imgdir=repo/'artifacts/vehicles/rondesp'
for name,pos,scale in [('frente',(-7,-7,3.0),6.65),('lateral',(-9,0,1.18),6.65),('frontal',(0,-9,1.35),4.7),('traseira',(-7,7,3.0),6.65)]:
    scene.camera.location=pos;scene.camera.rotation_euler=(Vector((0,.10,1.03))-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.camera.data.ortho_scale=scale
    scene.render.filepath=str(imgdir/f'v04-{name}-geometria.png');bpy.ops.render.render(write_still=True)
scene.camera.location=(-7,-7,3.0);scene.camera.rotation_euler=(Vector((0,.10,1.03))-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.camera.data.ortho_scale=6.65
out=repo/'blender/assets/vehicles/rondesp-pickup/marrom_v04.blend'
bpy.data.libraries.write(str(out),{scene},path_remap='RELATIVE',fake_user=True,compress=True)
path=repo/'docs/reports/blender/rondesp_marrom_v04.json';r=json.loads(path.read_text(encoding='utf-8'))
r.update(sha256=hashlib.sha256(out.read_bytes()).hexdigest(),objects=len(scene.objects),visual_review='Quatro vistas Workbench comparadas; aprovação final não concedida',geometry_finish=['junções frontais','máscara STD e grelhas','perfil topo capota','abertura vidro traseiro','rodas métricas reconstruídas','inscrições conformadas às chapas'])
path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def reopen():bpy.ops.wm.open_mainfile(filepath=str(out));return None
bpy.app.timers.register(reopen,first_interval=.5)
