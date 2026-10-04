"""Substitui a dianteira em painéis fragmentados por casca curva contínua Hilux."""
import bpy,bmesh,math,ast,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.geometry import delaunay_2d_cdt
repo=Path(__file__).resolve().parents[2];scene=bpy.context.scene
assert scene.name=='VIATURA | Rondesp Hilux marrom v04'
out=repo/'blender/assets/vehicles/rondesp-pickup/marrom_v05.blend';assert not out.exists()
root=scene.objects['RDP01_ROOT | viatura']
brown=bpy.data.materials['RDP01 | Pintura marrom Rondesp'];black=bpy.data.materials['RDP01 | Polímero preto'];paint=bpy.data.materials['RDP01 | Camuflagem marrom candidata']
scope=dict(bpy=bpy,bmesh=bmesh,math=math,Vector=Vector,Matrix=Matrix,root=root,brown=brown,black=black,collections={k:bpy.data.collections['RDP01 | '+k] for k in ['CARROCERIA','PORTAS','CAPOTA','VIDROS','RODAS','CHASSIS','LUZES','ACABAMENTOS','INSCRICOES','APRESENTACAO']})
tree=ast.parse((repo/'automation/blender/create_rondesp_pickup_v01.py').read_text(encoding='utf-8'))
for name in ['mesh','tube']:
    fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name);exec(compile(ast.Module(body=[fn],type_ignores=[]),'<helper>','exec'),scope)
mesh,tube=scope['mesh'],scope['tube']
for o in list(scene.objects):
    if o.type!='MESH' or scope['collections']['CARROCERIA'] not in o.users_collection:continue
    if any(s in o.name for s in ['Para-lama dianteiro','Retorno arco -1.43','Capô Hilux','Para-choque curvo','Pálpebra farol','Retorno lateral para-choque','Ombro capô','Junção curva nariz','Base arredondada para-choque']):bpy.data.objects.remove(o,do_unlink=True)
for o in list(scene.objects):
    if o.type=='CURVE' and ('Junta capô' in o.name or 'Vinco arco -1.43' in o.name):bpy.data.objects.remove(o,do_unlink=True)

def cinterp(vals,t):
    t=max(0,min(len(vals)-1.000001,t));i=int(t);f=t-i
    a,b,c,d=[Vector(vals[min(len(vals)-1,max(0,j))]) for j in [i-1,i,i+1,i+2]]
    return .5*((2*b)+(-a+c)*f+(2*a-5*b+4*c-d)*f*f+(-a+3*b-3*c+d)*f*f*f)

def nose(x,z):
    # Seção frontal envolve os cantos e arredonda o lábio inferior em perfil.
    return -2.435+.323*(abs(x)/.9275)**3.8+.092*math.exp(-((z-.51)/.16)**2)

def section(u,s):
    y0=-2.435+.323*abs(math.cos(math.pi*s))**3.8
    y=y0+(-.973-y0)*u
    low=.54
    d=abs(y+1.43)
    if d<.486:low=max(.54,.38815+.489*math.sqrt(1-(d/.486)**2))
    top=1.218+.089*math.sin(u*math.pi/2)
    bulge=math.exp(-((y+1.43)/.58)**4)
    # Controles de seção: concavidade inferior, ombro de para-lama e centro do capô.
    w=.897+.0305*bulge
    pts=[(-.827,low),(-.861,low+.038),(-w,max(low+.09,1.056)),(-w+.004,1.16),(-.894,top-.016),(-.831,top+.008),(-.628,top+.026),(0,top+.045),(.628,top+.026),(.831,top+.008),(.894,top-.016),(w-.004,1.16),(w,max(low+.09,1.056)),(.861,low+.038),(.827,low)]
    p=cinterp(pts,s*(len(pts)-1));x=max(-.9275,min(.9275,p.x));z=p.y
    # O nariz é arredondado em planta e perfil; as seções se conectam sem emenda vertical.
    if u<.23:
        fronty=nose(x,z);y=fronty+(-.973-fronty)*u
    return (x,y,z)

nu=112;ns=112
vs=[section(i/nu,j/ns) for i in range(nu+1) for j in range(ns+1)]
fs=[]
for i in range(nu):
    for j in range(ns):
        ids=(i*(ns+1)+j,(i+1)*(ns+1)+j,(i+1)*(ns+1)+j+1,i*(ns+1)+j+1)
        c=sum((Vector(vs[k]) for k in ids),Vector())/4
        # Abertura lateral dos faróis, não lente sobre chapa maciça.
        if abs(c.x)>.865 and c.y<-2.005 and 1.058<c.z<1.223:continue
        fs.append(ids)
body=mesh('HILUX05 | Casca orgânica frente',vs,fs,paint,smooth=True,thickness=.014)
bm=bmesh.new();bm.from_mesh(body.data)
for f in bm.faces:
    c=f.calc_center_median();direction=Vector((c.x,0,max(0,c.z-1.16)))
    if f.normal.dot(direction)<0:f.normal_flip()
bm.to_mesh(body.data);bm.free()
body['boas_modeling_method']='Seções transversais cúbicas contínuas, volumes de para-lama e capô compartilhados; sem blocos primitivos para a carroceria'
body['boas_reference_ids']='hilux-srx-user-front; hilux-srx-user-side; hilux-2024-std-dealer-side; rondesp-31110-front'

# Fecha a testa com malha triangulada restrita; recortes seguem os contornos das lentes.
outer=[Vector((p[0],p[2])) for p in vs[:ns+1]]
holes=[]
for side in (-1,1):
    lens=next(o for o in scene.objects if 'HILUX04 | Farol lente '+str(side) in o.name)
    holes.append([Vector((v.co.x,v.co.z)) for v in lens.data.vertices])
pts=list(outer);edges=[]
for loop in [outer]+holes:
    base=0 if loop is outer else len(pts)
    if loop is not outer:pts.extend(loop)
    edges.extend((base+i,base+(i+1)%len(loop)) for i in range(len(loop)))
# É parte do contorno frontal o retorno inferior entre os dois lados.
for x in [-.6,-.3,0,.3,.6]:pts.append(Vector((x,.51)))
for i in range(55):
    for j in range(24):pts.append(Vector((-.90+1.80*i/54,.52+.71*j/23)))
coords,ed,faces,*_=delaunay_2d_cdt(pts,edges,[],0,1e-6)
def inside(p,poly):
    odd=False
    for a,b in zip(poly,poly[1:]+poly[:1]):
        if (a.y>p.y)!=(b.y>p.y) and p.x<(b.x-a.x)*(p.y-a.y)/(b.y-a.y)+a.x:odd=not odd
    return odd
faces=[f for f in faces if inside(sum((coords[k] for k in f),Vector((0,0)))/len(f),outer) and not any(inside(sum((coords[k] for k in f),Vector((0,0)))/len(f),h) for h in holes)]
noseob=mesh('HILUX05 | Nariz esculpido com aberturas',[(p.x,nose(p.x,p.y),p.y) for p in coords],faces,paint,smooth=True,thickness=.014)
bm=bmesh.new();bm.from_mesh(noseob.data)
for f in bm.faces:
    if f.normal.y>0:f.normal_flip()
bm.to_mesh(noseob.data);bm.free()

# Os encaixes de faróis e a máscara seguem a nova curvatura da casca.
def oldnose(x,z):return -2.43+.30*(abs(x)/.9275)**3+.040*math.exp(-((z-.60)/.15)**2)
for o in scene.objects:
    if o.type=='MESH' and any(t in o.name for t in ['Farol encaixe','Farol fundo','Farol lente','Refletor integrado','Moldura envolvente','Fundo máscara','Ponte central grade','Rebaixo vertical']):
        for v in o.data.vertices:v.co.y+=nose(v.co.x,v.co.z)-oldnose(v.co.x,v.co.z)
        o.data.update()
    elif o.type=='CURVE' and any(t in o.name for t in ['Aleta superior STD','Grade vertical','Grade inferior','Toyota ','Linha superior farol','Nervura refletor']):
        for sp in o.data.splines:
            for p in sp.points:p.co.y+=nose(p.co.x,p.co.z)-oldnose(p.co.x,p.co.z)
    if o.type=='MESH' and 'Retorno farol lateral' in o.name:
        for v in o.data.vertices:v.co.y+=.025

# Linha de corte do capô acompanha a casca; sem chapa sobreposta ou tampa quadrada.
for side in (-1,1):
    j=.34 if side<0 else .66
    tube('HILUX05 | Junta real capô '+str(side),[section(i/nu,j) for i in range(nu+1)],.0017,black)
    # Lábio interno do poço faz a transição da casca externa para o revestimento.
    vv=[]
    for i in range(101):
        y=-1.43-.486+.972*i/100;d=abs(y+1.43);z=max(.54,.38815+.489*math.sqrt(max(0,1-(d/.486)**2)))
        x=.827
        vv.extend([(side*x,y,z),(side*(x-.11),y,z-.012)])
    mesh('HILUX05 | Retorno poço '+str(side),vv,[(2*i,2*i+1,2*i+3,2*i+2) for i in range(100)],black,thickness=.009,smooth=True)

# Reforça o abaulamento das chapas laterais, preservando os limites métricos.
for o in scene.objects:
    if o.type!='MESH' or not any(t in o.name for t in ['Porta estampada','Lateral caçamba']):continue
    for v in o.data.vertices:
        side=1 if v.co.x>0 else -1;y,z=v.co.y,v.co.z
        bulge=.014*math.exp(-((z-1.08)/.12)**2)-.006*math.exp(-((z-.69)/.08)**2)
        v.co.x=side*min(.9275,abs(v.co.x)+bulge)
    o.data.update()

scene.name='VIATURA | Rondesp Hilux marrom v05'
scene['boas_body_revision']='V05: casca dianteira contínua esculpida, substitui dianteira quadrada V04'
bpy.context.view_layer.update()
scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=1200;scene.render.resolution_y=750
scene.camera.location=(-7,-7,2.75);scene.camera.rotation_euler=(Vector((0,.10,1.01))-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.camera.data.ortho_scale=6.6
scene.render.filepath=str(repo/'artifacts/vehicles/rondesp/v05-frente-geometria.png');bpy.ops.render.render(write_still=True)
for screen in bpy.data.screens:
    for a in screen.areas:
        if a.type=='VIEW_3D':
            s=a.spaces.active;s.shading.type='SOLID';s.shading.color_type='MATERIAL';s.region_3d.view_rotation=scene.camera.rotation_euler.to_quaternion()
bpy.data.libraries.write(str(out),{scene},path_remap='RELATIVE',fake_user=True,compress=True)
r=json.loads((repo/'docs/reports/blender/rondesp_marrom_v04.json').read_text(encoding='utf-8'))
r.update(file=out.relative_to(repo).as_posix(),scene=scene.name,sha256=hashlib.sha256(out.read_bytes()).hexdigest(),objects=len(scene.objects),previous_revision='marrom_v04.blend',visual_review='Recomparar casca contínua V05 com vistas do usuário',body_revision=scene['boas_body_revision'])
r.pop('actual_mesh_measurements',None);r.pop('material_render',None);r.pop('material_preview_note',None)
(repo/'docs/reports/blender/rondesp_marrom_v05.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def reopen():bpy.ops.wm.open_mainfile(filepath=str(out));return None
bpy.app.timers.register(reopen,first_interval=.5)
