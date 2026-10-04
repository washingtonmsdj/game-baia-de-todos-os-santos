"""Traseira e identificação V10; executar somente na janela visível sobre V09."""
import bpy,bmesh,math,ast,json,hashlib,os
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
repo=Path(__file__).resolve().parents[2]; scene=bpy.context.scene
assert not bpy.app.background and Path(bpy.data.filepath).name=='marrom_v09.blend'
out=repo/'blender/assets/vehicles/rondesp-pickup/marrom_v10.blend'; assert not out.exists()
root=scene.objects['RDP01_ROOT | viatura']
collections={g:bpy.data.collections['RDP01 | '+g] for g in ['CARROCERIA','PORTAS','CAPOTA','VIDROS','RODAS','CHASSIS','LUZES','ACABAMENTOS','INSCRICOES','APRESENTACAO']}
for key,label in [('brown','Pintura marrom Rondesp'),('black','Polímero preto'),('silver','Metal acetinado'),('white','Inscrição branca'),('red','Lentes vermelhas'),('clear','Lentes transparentes')]:globals()[key]=bpy.data.materials['RDP01 | '+label]
for fn in ast.parse((repo/'automation/blender/create_rondesp_pickup_v01.py').read_text(encoding='utf-8')).body:
    if isinstance(fn,ast.FunctionDef) and fn.name in ['mesh','box','tube']:exec(compile(ast.Module(body=[fn],type_ignores=[]),'<helpers>','exec'),globals())
bpy.data.libraries.write(str(repo/'artifacts/vehicles/rondesp/pre-v10.blend'),{scene},path_remap='RELATIVE',compress=True)

# Transformação comum das chapas e ferragens: capota estreita em cima,
# painel traseiro inclinado, sem separar vidro, vedações e corpo.
def shape(p):
    x,y,z=p
    if y>1.16 and z>1.285:
        h=max(0,min(1,(z-1.285)/.575))
        x*=1-.105*h*h
        rear=max(0,min(1,(y-2.30)/.44)); rear=rear*rear*(3-2*rear)
        y-=.145*h*rear
        z-=.022*rear*h
    if y>2.48 and .5<z<1.29:
        t=max(0,min(1,(y-2.48)/.32))
        y-=.065*t*t*(abs(x)/.93)**5
    return Vector((x,y,z))
changed=[]
for o in list(scene.objects):
    if o.type not in ['MESH','CURVE'] or collections['APRESENTACAO'] in o.users_collection:continue
    if collections['INSCRICOES'] in o.users_collection:continue
    mat=root.matrix_world.inverted()@o.matrix_world;inv=mat.inverted();dirty=False
    points=o.data.vertices if o.type=='MESH' else [p for sp in o.data.splines for p in sp.points]
    for v in points:
        p=mat@Vector(v.co[:3]);q=shape(p)
        if (q-p).length>1e-7:
            v.co=inv@q if o.type=='MESH' else (*(inv@q),v.co.w);dirty=True
    if dirty:
        changed.append(o.name)
        if o.type=='MESH':o.data.update()

# Para-choque em duas asas arredondadas com rebaixo central para placa.
removed=[]
for o in list(scene.objects):
    if any(t in o.name for t in ['Para-choque traseiro','Apoio passo para-choque traseiro']):
        removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
for side in [-1,1]:
    ob=box('HILUX10 | Asa para-choque '+str(side),(side*.61,2.805,.535),(.63,.27,.20),black,'ACABAMENTOS',.075)
    for m in ob.modifiers:
        if m.type=='BEVEL':m.segments=8
    for p in ob.data.polygons:p.use_smooth=True
    ob.modifiers.new('Normais de fabricação','WEIGHTED_NORMAL')
    box('HILUX10 | Piso antiderrapante '+str(side),(side*.61,2.80,.638),(.48,.21,.018),black,'ACABAMENTOS',.025)
box('HILUX10 | Rebaixo placa traseira',(0,2.793,.50),(.52,.105,.19),black,'ACABAMENTOS',.035)
box('HILUX10 | Placa sem número confirmado',(0,2.852,.514),(.39,.008,.112),white,'ACABAMENTOS',.012)

# Tipografia com altura controlada separadamente da largura, mais pesada e
# levemente inclinada como nas fotos; não reutiliza o letreiro fino anterior.
for o in list(collections['INSCRICOES'].objects):
    if o.get('boas_inscription_text') or o.type=='FONT' or 'Contorno brasão' in o.name:
        removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();vs=[];fs=[]
for o in scene.objects:
    if o.type!='MESH' or not any(collections[g] in o.users_collection for g in ['CARROCERIA','PORTAS','CAPOTA','VIDROS']):continue
    ev=o.evaluated_get(dg);me=ev.to_mesh();b=len(vs);vs.extend(ev.matrix_world@v.co for v in me.vertices);fs.extend(tuple(b+i for i in p.vertices) for p in me.polygons);ev.to_mesh_clear()
bvh=BVHTree.FromPolygons(vs,fs)
font=bpy.data.fonts.load(str(Path(os.environ.get('WINDIR','C:/Windows'))/'Fonts/ariblk.ttf'))
try:font.pack()
except Exception:pass
def project(p,face,offset=.003):
    if face in [-1,1]:origin=Vector((face*2,p.y,p.z));direction=Vector((-face,0,0));normal=Vector((face,0,0))
    elif face=='rear':origin=Vector((p.x,3.5,p.z));direction=Vector((0,-1,0));normal=Vector((0,1,0))
    else:origin=Vector((p.x,p.y,3));direction=Vector((0,0,-1));normal=Vector((0,0,1))
    hit,_,_,_=bvh.ray_cast(origin,direction,5)
    assert hit is not None,('Inscrição sem apoio',tuple(p),face)
    return hit+normal*offset
def label(name,text,center,width,height,face,italic=.13):
    cu=bpy.data.curves.new(name,'FONT');cu.body=text;cu.font=font;cu.size=1;cu.resolution_u=8
    ob=bpy.data.objects.new(name,cu);collections['INSCRICOES'].objects.link(ob)
    bpy.context.view_layer.update();me=bpy.data.meshes.new_from_object(ob.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    xmin=min(v.co.x for v in me.vertices);xmax=max(v.co.x for v in me.vertices);zmin=min(v.co.y for v in me.vertices);zmax=max(v.co.y for v in me.vertices)
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.subdivide_edges(bm,edges=list(bm.edges),cuts=2,use_grid_fill=True);bm.to_mesh(me);bm.free()
    for v in me.vertices:
        a=(v.co.x-(xmin+xmax)/2)/(xmax-xmin)*width;b=(v.co.y-(zmin+zmax)/2)/(zmax-zmin)*height;a+=italic*b
        if face in [-1,1]:p=Vector((center[0],center[1]+face*a,center[2]+b))
        elif face=='rear':p=Vector((center[0]-a,center[1],center[2]+b))
        else:p=Vector((center[0]+a,center[1]+b,center[2]))
        v.co=project(p,face)
    bpy.data.objects.remove(ob,do_unlink=True)
    o=bpy.data.objects.new('RDP01 | HILUX10 | '+name,me);collections['INSCRICOES'].objects.link(o);o.parent=root;me.materials.append(white);o['boas_inscription_text']=text
    return o
def phone(center,face,size=.052):
    pts=[]
    for i in range(25):
        a=math.radians(125+110*i/24);u=math.cos(a)*size*.46;v=math.sin(a)*size*.46
        p=Vector((center[0],center[1]+face*u,center[2]+v)) if face in [-1,1] else Vector((center[0]-u,center[1],center[2]+v))
        pts.append(project(p,face,.004))
    tube('HILUX10 | Telefone '+str(center),pts,.007,white,'INSCRICOES')
for side in [-1,1]:
    label('POLÍCIA MILITAR '+str(side),'POLÍCIA MILITAR',(side*.90,.10,.674),1.66,.103,side)
    label('Prefixo '+str(side),'3.1110',(side*.90,2.26,1.176),.40,.107,side)
    label('RONDESP '+str(side),'RONDESP',(side*.90,2.26,1.079),.37,.051,side)
    label('Unidade '+str(side),'LESTE',(side*.90,2.26,1.014),.24,.046,side)
    label('Emergência '+str(side),'190',(side*.91,-1.42,1.188),.125,.058,side)
    phone((side*.91,-1.42-side*.102,1.188),side)
label('Prefixo vidro','3.1110',(0,2.75,1.568),.98,.203,'rear',0)
label('POLÍCIA MILITAR traseira','POLÍCIA MILITAR',(0,2.8,.78),1.23,.112,'rear')
label('Emergência traseira','190',(.52,2.8,1.153),.17,.067,'rear')
phone((.66,2.8,1.153),'rear',.061)
label('POLÍCIA capô','POLÍCIA',(0,-2.13,1.3),.61,.105,'hood')

# Emblema vetorial candidato: campo vermelho, bordadura branca e armas
# cruzadas. Detalhes heráldicos ilegíveis não são apresentados como réplica.
def badge(center,face,radius):
    def xy(a,b,off=.004):
        if face in [-1,1]:p=Vector((center[0],center[1]+face*a,center[2]+b))
        elif face=='rear':p=Vector((center[0]-a,center[1],center[2]+b))
        else:p=Vector((center[0]+a,center[1]+b,center[2]))
        return project(p,face,off)
    n=80
    disk=[xy(0,0)]+[xy(radius*.76*math.cos(i*math.tau/n),radius*.90*math.sin(i*math.tau/n)) for i in range(n)]
    ob=mesh('HILUX10 | Campo brasão '+str(center),disk,[(0,i+1,(i+1)%n+1) for i in range(n)],red,'INSCRICOES')
    ob['boas_emblem_status']='candidate; simplificação vetorial, microdetalhes heráldicos pendentes'
    for scale,thick in [(1,.004),(.83,.0025)]:
        tube('HILUX10 | Bordadura brasão '+str((center,scale)),[xy(radius*.84*scale*math.cos(i*math.tau/n),radius*scale*math.sin(i*math.tau/n),.005) for i in range(n)],thick,white,'INSCRICOES',True)
    for sign in [-1,1]:
        tube('HILUX10 | Armas cruzadas '+str((center,sign)),[xy(sign*radius*t*.47,radius*t*.58,.006) for t in [-1,-.6,0,.6,1]],radius*.055,white,'INSCRICOES')
    tube('HILUX10 | Espada '+str(center),[xy(0,radius*t,.007) for t in [-.65,.65]],radius*.045,white,'INSCRICOES')
    for i in range(26):
        a=i*math.tau/26
        tube('HILUX10 | Marca bordadura '+str((center,i)),[xy(radius*.91*math.cos(a)*.84,radius*.91*math.sin(a),.006),xy(radius*.97*math.cos(a)*.84,radius*.97*math.sin(a),.006)],radius*.015,white,'INSCRICOES')
for side in [-1,1]:badge((side*.90,-.39,.997),side,.134)
badge((-.55,2.8,1.104),'rear',.098)
badge((0,-1.65,1.3),'hood',.185)

# Giroflex: cúpula transparente baixa, módulos vermelhos nas extremidades,
# perfil luminoso visível também em inspeção sólida. Material próprio.
led=red.copy();led.name='RDP01 | HILUX10 LED vermelho';led.diffuse_color=(.8,.006,.012,1)
bs=led.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.65,.002,.004,1);bs.inputs['Emission Color'].default_value=(1,.004,.006,1);bs.inputs['Emission Strength'].default_value=4
for o in scene.objects:
    if 'Módulo sinalizador' in o.name:
        o.data.materials[0]=led
        o.scale.z=1.35
    if 'Cúpula sinalizador' in o.name:
        o.hide_set(True);o.hide_render=False
        o['boas_viewport_note']='Cúpula transparente oculta somente em modo sólido para revelar módulos internos; render preservado.'
for side in [-1,1]:
    box('HILUX10 | LED lateral '+str(side),(side*.531,.035,1.952),(.031,.15,.041),led,'LUZES',.012)
scene.name='VIATURA | Rondesp Hilux marrom v10'
scene['boas_v10_status']='candidate; brasão detalhado e desenho exato da camuflagem pendentes'
bpy.context.view_layer.update();bpy.data.libraries.write(str(out),{scene},path_remap='RELATIVE',fake_user=True,compress=True)
rp=repo/'docs/reports/blender/rondesp_marrom_v10.json'
r={'file':out.relative_to(repo).as_posix(),'scene':scene.name,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'parent':'blender/assets/vehicles/rondesp-pickup/marrom_v09.blend','status':'candidate','changed':changed,'removed':removed,'changes':['capota afunilada e painel traseiro inclinado','cantos traseiros curvos','para-choque com asas e rebaixo','tipografia pesada inclinada e prefixo traseiro maior','190 com símbolo de telefone, unidade LESTE e POLÍCIA no capô','giroflex com módulos vermelhos emissivos'],'source_reopened':False,'runtime_exported':False,'pending':['brasão PMBA detalhado','fidelidade final','camuflagem exata'],'reference_ids':['rondesp-user-rear-21212-v10','rondesp-user-front-21103-v10','rondesp-user-lightbar-v10'],'checks':'Somente revisão de modelagem; sem npm, testes ou build conforme solicitação.'}
rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def reopen():
    bpy.ops.wm.open_mainfile(filepath=str(out));r=json.loads(rp.read_text(encoding='utf-8'));r['source_reopened']=Path(bpy.data.filepath)==out;rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return None
bpy.app.timers.register(reopen,first_interval=.5)
