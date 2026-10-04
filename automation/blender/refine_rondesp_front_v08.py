"""Frente Rondesp V08: protetor tubular, ópticas e sinalizador sem peças duplicadas."""
import bpy,bmesh,math,ast,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
repo=Path(__file__).resolve().parents[2];scene=bpy.context.scene
assert Path(bpy.data.filepath).name=='marrom_v07.blend' and not bpy.data.is_dirty
out=repo/'blender/assets/vehicles/rondesp-pickup/marrom_v08.blend';assert not out.exists()
root=scene.objects['RDP01_ROOT | viatura']
collections={k:bpy.data.collections['RDP01 | '+k] for k in ['CARROCERIA','PORTAS','CAPOTA','VIDROS','RODAS','CHASSIS','LUZES','ACABAMENTOS','INSCRICOES','APRESENTACAO']}
black=bpy.data.materials['RDP01 | Polímero preto'];silver=bpy.data.materials['RDP01 | Metal acetinado'];red=bpy.data.materials['RDP01 | Lentes vermelhas'];clear=bpy.data.materials['RDP01 | Lentes transparentes'];brown=bpy.data.materials['RDP01 | Pintura marrom Rondesp']
for file,names in [('create_rondesp_pickup_v01.py',['mesh','box','tube','cylinder']),('rebuild_hilux_reference_v06.py',['bezier_loop']),('finish_hilux_reference_v06.py',['nose'])]:
    for fn in ast.parse((repo/'automation/blender'/file).read_text(encoding='utf-8')).body:
        if isinstance(fn,ast.FunctionDef) and fn.name in names:exec(compile(ast.Module(body=[fn],type_ignores=[]),'<front-helpers>','exec'),globals())
removed=[]
for o in list(scene.objects):
    n=o.name.lower()
    if 'quebra-mato' in n or any(t in n for t in ['base barra sinalizadora','barra vermelha','led vermelho barra']):
        removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)

def bent(name,points,radius=.024):
    # Arcos quadráticos tangentes nos cantos, em vez de cotovelos de polilinha.
    pts=[Vector(points[0])]
    for i in range(1,len(points)-1):
        p=Vector(points[i]);a=p+(Vector(points[i-1])-p)*.20;b=p+(Vector(points[i+1])-p)*.20
        pts.append(a)
        for j in range(1,13):
            t=j/12;pts.append((1-t)**2*a+2*(1-t)*t*p+t*t*b)
    pts.append(Vector(points[-1]))
    o=tube('HILUX08 | '+name,[tuple(p) for p in pts],radius,black)
    o['boas_reference_ids']='rondesp-31110-front';o['boas_dimensions_status']='candidate: acessórios interpretados da fotografia, não medidos'
    return o

# Arco principal à frente da máscara e asas com retorno para as laterais.
bent('Arco principal protetor',[(-.545,-2.61,.48),(-.545,-2.64,1.105),(-.475,-2.655,1.185),(.475,-2.655,1.185),(.545,-2.64,1.105),(.545,-2.61,.48)],.025)
bent('Travessa inferior protetor',[(-.97,-2.35,.65),(-.86,-2.52,.65),(-.54,-2.625,.65),(.54,-2.625,.65),(.86,-2.52,.65),(.97,-2.35,.65)],.023)
for side in [-1,1]:
    bent('Asa frontal '+str(side),[(side*.545,-2.64,1.07),(side*.83,-2.50,1.07),(side*.979,-2.32,1.025),(side*.979,-2.32,.803),(side*.86,-2.49,.763),(side*.545,-2.64,.763)],.019)
    # Suporte de aço em chapa, com retorno até a longarina do veículo.
    poly=[(-2.19,.34),(-2.57,.32),(-2.638,.39),(-2.645,1.086),(-2.602,1.13),(-2.563,1.09),(-2.567,.46),(-2.19,.43)]
    vs=[(side*(.43+dx),y,z) for dx in [-.009,.009] for y,z in poly];n=len(poly)
    fs=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    ob=mesh('HILUX08 | Suporte estrutural '+str(side),vs,fs,black,'CHASSIS',bevel=.008)
    for z in [.405,.49,.92]:
        cylinder('HILUX08 | Parafuso suporte',(side*.448,-2.594,z),.009,.005,silver,'ACABAMENTOS','X',6)
    # Junção de chapa atrás do farol; espessura milimétrica, não vinco tubular largo.
    bent('Junta para-choque '+str(side),[(side*.915,-1.960,1.08),(side*.914,-1.92,.984),(side*.921,-1.84,.919)],.0012)

# Remover módulos antigos repetidos e sinalizador alto, preservando rack e antena.
# Corpo novo baixo com extremidades arredondadas e módulos internos independentes.
bar=box('HILUX08 | Base sinalizador',(0,.035,1.918),(1.13,.247,.025),black,'LUZES',.012)
housing=box('HILUX08 | Cúpula sinalizador',(0,.035,1.948),(1.11,.228,.050),clear,'LUZES',.024)
for ob in [bar,housing]:
    for m in ob.modifiers:
        if m.type=='BEVEL':m.segments=8
    for p in ob.data.polygons:p.use_smooth=True
    ob.modifiers.new('Normais da peça','WEIGHTED_NORMAL')
for side in [-1,1]:
    for x in [-.43,-.29,-.15,.15,.29,.43]:
        box('HILUX08 | Módulo sinalizador '+str((side,x)),(x,.035+side*.092,1.946),(.109,.026,.026),red,'LUZES',.009)

# Filetes internos do refletor e acabamento do perímetro da lente.
for side in [-1,1]:
    for x in [.588,.613,.638,.663,.688,.765,.79,.815,.840]:
        z=1.065 if x<.72 else 1.105
        pts=[]
        for j in range(9):
            zz=z-.031+.062*j/8;xx=side*x;pts.append((xx,nose(xx,zz,.013)+.010*math.sin(j*math.pi/8),zz))
        tube('HILUX08 | Estria refletor '+str((side,x)),pts,.0012,silver,'LUZES')
    # A lente permanece transparente no render; a cor de exibição não simula vidro branco.
    lens=scene.objects.get('RDP01 | HILUX06 | Lente óptica transparente '+str(side))
    if lens:
        lens['boas_display_note']='Vidro transparente no material PBR; modo sólido é apenas inspeção geométrica'
clear.diffuse_color=(.105,.145,.16,1)

scene.name='VIATURA | Rondesp Hilux marrom v08'
scene['boas_review_status']='candidate; frente e equipamentos refinados pelas fotos 3.1110'
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            s=area.spaces.active;s.shading.type='SOLID';s.shading.color_type='MATERIAL';s.shading.light='STUDIO';s.shading.studio_light='paint.sl';s.shading.show_cavity=False;s.overlay.show_overlays=False
            s.region_3d.view_rotation=(Vector((0,0,1))-Vector((-7,-9,3.2))).to_track_quat('-Z','Y');s.region_3d.view_location=(0,0,1);s.region_3d.view_distance=5.1
bpy.context.view_layer.update();bpy.data.libraries.write(str(out),{scene},path_remap='RELATIVE',fake_user=True,compress=True)
report={'asset_id':'vehicle-rondesp-pickup','file':out.relative_to(repo).as_posix(),'scene':scene.name,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'parent':'blender/assets/vehicles/rondesp-pickup/marrom_v07.blend','status':'candidate','removed_components':removed,'changes':['protetor frontal com tubos curvos, retornos e suportes de chapa','sinalizador baixo e remoção de módulos antigos duplicados','acabamento interno dos refletores e junção do para-choque'],'dimensions_accessories':'candidate, interpretadas das fotos','runtime_exported':False,'pending':['fidelidade final da carroceria','brasão PMBA detalhado','camuflagem exata','animação e runtime']}
rp=repo/'docs/reports/blender/rondesp_marrom_v08.json'
rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def reopen():
    bpy.ops.wm.open_mainfile(filepath=str(out))
    r=json.loads(rp.read_text(encoding='utf-8'));r['source_reopened']=Path(bpy.data.filepath)==out;r['is_dirty_after_reopen']=bpy.data.is_dirty
    rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    cp=repo/'world/vehicles/catalog.json';d=json.loads(cp.read_text(encoding='utf-8'));v=next(v for v in d['vehicles'] if v['asset_id']=='vehicle-rondesp-pickup');base={k:r[k] for k in ['file','scene','sha256']}
    v['authoring_base']=base;v['variants'][0].update(base,status='candidate',scope='V08: protetor frontal tubular, sinalizador e acabamento óptico; fidelidade ainda em revisão, sem runtime.')
    v['revision_policy']='V08 é a fonte explícita. V01–V07 preservadas; não selecionar por sufixo ou mtime.'
    cp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    note='## 03/10/2026 — Rondesp: fonte candidata V08\n\nFonte `blender/assets/vehicles/rondesp-pickup/marrom_v08.blend`, V07 preservada. Protetor frontal reconstruído com tubos curvos e suportes, sinalizador baixo sem módulos repetidos e acabamento dos refletores. Acessórios interpretados das fotos, dimensões não verificadas. Relatório/hash: `docs/reports/blender/rondesp_marrom_v08.json`. Script `automation/blender/refine_rondesp_front_v08.py`, aplicado via MCP na única janela, fonte reaberta. Sem render offline/npm/build/testes gerais; sem exportação runtime. Fidelidade final da carroceria, brasão e camuflagem exata continuam pendentes.\n\n'
    for rel in ['docs/PROJECT_STATUS.md','docs/CODEX_HANDOFF.md']:
        p=repo/rel;t=p.read_text(encoding='utf-8');i=t.index('\n')+1;p.write_text(t[:i]+'\n'+note+t[i:],encoding='utf-8')
    return None
bpy.app.timers.register(reopen,first_interval=.5)
