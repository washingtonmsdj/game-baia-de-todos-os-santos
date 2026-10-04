"""Arredondamento final do nariz, lanternas volumétricas e inspeção de materiais."""
import bpy,bmesh,math,json,hashlib,ast
from pathlib import Path
from mathutils import Vector,Matrix
repo=Path(__file__).resolve().parents[2];scene=bpy.context.scene;assert scene.name=='VIATURA | Rondesp Hilux marrom v04'
root=scene.objects['RDP01_ROOT | viatura']
groups=['CARROCERIA','PORTAS','CAPOTA','VIDROS','RODAS','CHASSIS','LUZES','ACABAMENTOS','INSCRICOES','APRESENTACAO']
scope=dict(bpy=bpy,bmesh=bmesh,math=math,Vector=Vector,Matrix=Matrix,root=root,collections={k:bpy.data.collections['RDP01 | '+k] for k in groups})
for key,label in [('brown','Pintura marrom Rondesp'),('black','Polímero preto'),('steel','Aço preto rodas'),('silver','Metal acetinado'),('white','Inscrição branca'),('glass','Vidro fumê'),('clear','Lentes transparentes'),('red','Lentes vermelhas')]:scope[key]=bpy.data.materials['RDP01 | '+label]
for file,names in [('create_rondesp_pickup_v01.py',['mesh','box','tube','parent_keep']),('rebuild_hilux_body_v04.py',['curve','part','grid','rounded','ring'])]:
    tree=ast.parse((repo/'automation/blender'/file).read_text(encoding='utf-8'))
    for name in names:
        fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name);exec(compile(ast.Module(body=[fn],type_ignores=[]),'<helpers>','exec'),scope)
part,grid,rounded,ring,tube,curve=[scope[n] for n in ['part','grid','rounded','ring','tube','curve']]
brown,black,silver,red,clear=[scope[k] for k in ['brown','black','silver','red','clear']]

# O para-choque afunila abaixo dos cantos e recua progressivamente na base.
for o in scene.objects:
    if o.type!='MESH' or 'HILUX04' not in o.name or not any(c==scope['collections']['CARROCERIA'] for c in o.users_collection):continue
    for v in o.data.vertices:
        x,y,z=v.co
        if y<-1.985 and z<1.03:
            w=curve([(.49,.825),(.57,.88),(.72,.9275),(.88,.925),(1.03,.911)],z)
            scale=w/.911
            if abs(x)>.60:v.co.x*=scale
            # Arredondamento de perfil; não reescala do veículo.
            v.co.y+=.063*math.exp(-((z-.49)/.13)**2)
    o.data.update()

# Lanternas assentadas no canto da caçamba; elimina as placas vermelhas afastadas.
for o in list(scene.objects):
    if any(s in o.name for s in ['Lanterna traseira angular','Lente vermelha traseira','Filete lanterna','Ré traseira']):bpy.data.objects.remove(o,do_unlink=True)
for side in (-1,1):
    poly=rounded([(.912,1.235),(.805,1.209),(.766,1.116),(.731,.978),(.738,.785),(.895,.770)],.13,8)
    def lp(p,off=0):
        x,z=p;y=2.793-.04*((x-.75)/.17)**2
        return(side*x,y+off,z)
    inn=ring(f'Carcaça lanterna Hilux {side}',poly,lp,black,'LUZES',inset=.91)
    part(f'Lente lanterna Hilux {side}',[lp(p,.005) for p in inn],[tuple(range(len(inn)))],red,'LUZES',thickness=.012)
    # Retorno lateral triangular da lente, alinhado ao perfil inclinado da foto.
    sp=rounded([(2.750,1.231),(2.535,1.114),(2.560,.927),(2.745,.780)],.10)
    part(f'Retorno lateral lanterna {side}',[(side*.899,p.x,p.y) for p in sp],[tuple(range(len(sp)))],red,'LUZES',thickness=.009)
    reverse=rounded([(.825,.792),(.884,.792),(.884,.887),(.804,.889)],.19)
    part(f'Reverso lanterna {side}',[lp(p,.019) for p in reverse],[tuple(range(len(reverse)))],clear,'LUZES',thickness=.003)
    for i,z in enumerate([.956,1.055,1.158]):
        q=rounded([(.790,z-.024),(.878,z-.024),(.887,z+.025),(.802,z+.032)],.25)
        tube(f'HILUX04 | Canal lanterna {side} {i}',[lp(p,.025) for p in q],.005,black,'LUZES',True)

# Prefixos corrigidos após encurtar o painel da caçamba; devem estar no painel, sob a junta.
for o in scene.objects:
    if o.type=='MESH' and ('Prefixo lateral' in o.name or 'RONDESP lateral' in o.name):
        for v in o.data.vertices:
            v.co.z-=.047
            # Perfil local da chapa: x cresce no ombro e recua na linha superior.
            x=curve([(.9,.900),(1.06,.908),(1.16,.902),(1.28,.862)],v.co.z)
            v.co.x=math.copysign(x+.003,v.co.x)
        o.data.update()
# Evita o brilho branco que escondia o desenho dos faróis no preview.
clear.diffuse_color=(.30,.36,.38,1)
red.diffuse_color=(.40,.008,.012,1)
scene.world.color=(.15,.15,.15)
scene.camera.location=(-7,-7,3.0);scene.camera.rotation_euler=(Vector((0,.10,1.02))-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.camera.data.ortho_scale=6.65
scene.render.filepath=str(repo/'artifacts/vehicles/rondesp/v04-frente-geometria.png');bpy.ops.render.render(write_still=True)

# Apenas uma inspeção da geometria com materiais, sem build/runtime.
scene.render.engine='CYCLES';scene.cycles.samples=4;scene.cycles.use_denoising=True
scene.render.threads_mode='FIXED';scene.render.threads=4
scene.render.resolution_x=900;scene.render.resolution_y=600
scene.view_settings.view_transform='AgX';scene.view_settings.exposure=.6
scene.render.filepath=str(repo/'artifacts/vehicles/rondesp/v04-frente-materiais.png')
# Salva a fonte antes da inspeção renderizada para preservar a edição mesmo em interrupção.
out=repo/'blender/assets/vehicles/rondesp-pickup/marrom_v04.blend'
for screen in bpy.data.screens:
    for a in screen.areas:
        if a.type=='VIEW_3D':
            s=a.spaces.active;s.shading.type='SOLID';s.shading.color_type='MATERIAL';s.region_3d.view_rotation=scene.camera.rotation_euler.to_quaternion();s.region_3d.view_location=(0,.10,1);s.region_3d.view_distance=7
bpy.context.view_layer.update();bpy.data.libraries.write(str(out),{scene},path_remap='RELATIVE',fake_user=True,compress=True)
path=repo/'docs/reports/blender/rondesp_marrom_v04.json';r=json.loads(path.read_text(encoding='utf-8'))
r.update(sha256=hashlib.sha256(out.read_bytes()).hexdigest(),objects=len(scene.objects),material_render='artifacts/vehicles/rondesp/v04-frente-materiais.png',body_polish=['afunilamento e curvatura base para-choque','lanternas volumétricas com retorno lateral','prefixos assentados abaixo da junta'])
path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
bpy.ops.render.render(write_still=True)
def reopen():bpy.ops.wm.open_mainfile(filepath=str(out));return None
bpy.app.timers.register(reopen,first_interval=.5)
