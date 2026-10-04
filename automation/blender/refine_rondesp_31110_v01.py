"""Refina a cena própria com as duas fotos 2024/2025 fornecidas na sessão."""
import bpy
import json
import math
import hashlib
from pathlib import Path
from mathutils import Vector, Matrix

repo=Path(__file__).resolve().parents[2]
scene=bpy.context.scene
assert scene.name=='VIATURA | Rondesp picape marrom v01'
# Reusa os helpers do gerador sem executar o gerador outra vez.
scope={'__name__':'rondesp_helpers','__file__':str(repo/'automation/blender/create_rondesp_pickup_v01.py')}
source=(repo/'automation/blender/create_rondesp_pickup_v01.py').read_text(encoding='utf-8')
scope.update({'bpy':bpy,'bmesh':__import__('bmesh'),'math':math,'Vector':Vector,'Matrix':Matrix})
scope['root']=scene.objects['RDP01_ROOT | viatura']
scope['collections']={k:bpy.data.collections['RDP01 | '+k] for k in ['CARROCERIA','PORTAS','CAPOTA','VIDROS','RODAS','CHASSIS','LUZES','ACABAMENTOS','INSCRICOES','APRESENTACAO']}
for k,name in [('brown','Pintura marrom Rondesp'),('black','Polímero preto'),('steel','Aço preto rodas'),('silver','Metal acetinado'),('white','Inscrição branca'),('glass','Vidro fumê'),('clear','Lentes transparentes'),('red','Lentes vermelhas')]:
    scope[k]=bpy.data.materials['RDP01 | '+name]
for symbol in ['linear','material','attach','mesh','box','tube','cylinder','loft','parent_keep','side_text']:
    import ast
    tree=ast.parse(source)
    fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==symbol)
    exec(compile(ast.Module(body=[fn],type_ignores=[]),'<helpers>','exec'),scope)
scope['root']=scene.objects['RDP01_ROOT | viatura']
scope['collections']={k:bpy.data.collections['RDP01 | '+k] for k in ['CARROCERIA','PORTAS','CAPOTA','VIDROS','RODAS','CHASSIS','LUZES','ACABAMENTOS','INSCRICOES','APRESENTACAO']}
for k,name in [('brown','Pintura marrom Rondesp'),('black','Polímero preto'),('steel','Aço preto rodas'),('silver','Metal acetinado'),('white','Inscrição branca'),('glass','Vidro fumê'),('clear','Lentes transparentes'),('red','Lentes vermelhas')]:
    scope[k]=bpy.data.materials['RDP01 | '+name]
scope['ROOT']=repo
mesh=scope['mesh']; box=scope['box']; tube=scope['tube']; cylinder=scope['cylinder']
brown=scope['brown']; black=scope['black']; steel=scope['steel']; silver=scope['silver']; white=scope['white']; glass=scope['glass']; clear=scope['clear']; red=scope['red']

def remove_prefix(prefixes):
    for o in list(scene.objects):
        if any(o.name.startswith('RDP01 | '+p) for p in prefixes):
            bpy.data.objects.remove(o,do_unlink=True)

# Inscrições na orientação correta em ambas as faces.
for side in (-1,1):
    for title in ('POLÍCIA MILITAR ','Telefone 190 '):
        ob=scene.objects['RDP01 | '+title+str(side)]
        p=ob.location.copy()
        right=Vector((0,side,0)); up=Vector((0,0,1)); n=right.cross(up)
        ob.matrix_world=Matrix(((right.x,up.x,n.x,p.x),(right.y,up.y,n.y,p.y),(right.z,up.z,n.z,p.z),(0,0,0,1)))

def text(label,body,side,y,z,size):
    ob=scope['side_text'](label,body,side,y,z,size)
    p=ob.location.copy(); right=Vector((0,side,0)); up=Vector((0,0,1)); n=right.cross(up)
    ob.matrix_world=Matrix(((right.x,up.x,n.x,p.x),(right.y,up.y,n.y,p.y),(right.z,up.z,n.z,p.z),(0,0,0,1)))
    return ob

# Frente da Hilux recente: faróis maiores e máscara preta alta no centro.
remove_prefix(['Farol carcaça','Farol lente angular','Projetor farol','Filete farol','Farol neblina','Grade superior','Friso grade','Entrada ar inferior','Lâmina entrada ar'])
mesh('Grade Hilux 2024 preta',[(-.60,-2.729,.69),(-.65,-2.724,1.095),(-.54,-2.721,1.18),(.54,-2.721,1.18),(.65,-2.724,1.095),(.60,-2.729,.69)],[(0,1,2,3,4,5)],black,'ACABAMENTOS',thickness=.022)
for z,w in [(1.14,.55),(1.075,.61),(1.015,.61),(.955,.61),(.895,.60),(.81,.58),(.75,.56)]:
    tube('Barra grade 2024 '+str(z),[(-w,-2.752,z),(0,-2.768,z-.006),(w,-2.752,z)],.013,steel)
for side in (-1,1):
    outline=[(side*.578,-2.754,1.10),(side*.66,-2.72,1.206),(side*.88,-2.69,1.235),(side*.923,-2.41,1.234),(side*.924,-2.28,1.21),(side*.895,-2.41,1.08),(side*.665,-2.72,1.01)]
    mesh('Farol 2024 carcaça '+str(side),outline,[tuple(range(7))],black,'LUZES',thickness=.033)
    cx=sum(v[0] for v in outline)/7; cz=sum(v[2] for v in outline)/7
    inset=[(cx+(x-cx)*.91,y-.009,cz+(z-cz)*.82) for x,y,z in outline]
    mesh('Farol 2024 lente '+str(side),inset,[tuple(range(7))],clear,'LUZES',thickness=.007)
    for x,z,r in [(.735,1.14,.045),(.843,1.15,.034)]:
        cylinder('Refletor farol '+str(side)+str(x),(side*x,-2.752,z),r,.009,silver,'LUZES','Y')
    tube('DRL farol '+str(side),[(side*.66,-2.75,1.188),(side*.84,-2.71,1.211),(side*.917,-2.42,1.207)],.008,white,'LUZES')
    # Rebaixo preto vertical de canto: suporte do farol auxiliar da referência.
    pts=[(side*.747,-2.731,.97),(side*.82,-2.72,.94),(side*.83,-2.72,.71),(side*.76,-2.737,.68),(side*.69,-2.745,.72),(side*.71,-2.74,.79),(side*.74,-2.735,.79)]
    mesh('Rebaixo canto para-choque '+str(side),pts,[tuple(range(7))],black,'ACABAMENTOS',thickness=.008)
    box('Auxiliar canto lente '+str(side),(side*.767,-2.752,.77),(.065,.01,.035),clear,'LUZES',.01)

# Capota com bordas arredondadas, acesso lateral, tampas inclinadas e fechos.
remove_prefix(['Nervura capota','Reforço diagonal capota'])
cap=scene.objects['RDP01 | Capota fechada reforçada']
bevel=cap.modifiers.new('Curvatura fabricação capota','BEVEL'); bevel.width=.07; bevel.segments=5
bevel.limit_method='ANGLE'

def hatch(side):
    # Plano inclinado da lateral superior; canto arredondado em cada vértice.
    poly=[(1.10,1.365),(1.56,1.365),(1.62,1.72),(1.51,1.91),(1.19,1.93),(1.10,1.70)]
    pts=[]
    for i,(y,z) in enumerate(poly):
        prev=Vector(poly[i-1]); cur=Vector((y,z)); nxt=Vector(poly[(i+1)%len(poly)])
        a=cur+(prev-cur)*.11; b=cur+(nxt-cur)*.11
        for k in range(7):
            t=k/6; p=(1-t)**2*a+2*t*(1-t)*cur+t*t*b
            yy,zz=p
            x=.91 if zz<1.64 else .895-(zz-1.64)*.50
            pts.append((side*(x+.007),yy,zz))
    plate=mesh('Acesso lateral capota '+str(side),pts,[tuple(range(len(pts)))],brown,'CAPOTA',thickness=.012)
    tube('Junta acesso capota '+str(side),pts,.007,black,'CAPOTA',True)
    box('Fecho acesso capota '+str(side),(side*.909,1.24,1.41),(.028,.055,.018),black,'CAPOTA',.007)
    for k,y in enumerate((1.74,2.0,2.26)):
        # Tampas de ventilação/proteção vistas de lado, discretamente afastadas.
        z=1.77
        verts=[]
        for yy,zz in [(y-.092,z-.065),(y+.092,z-.065),(y+.092,z+.065),(y-.092,z+.065)]:
            x=.895-(zz-1.64)*.50+.035
            verts.append((side*x,yy,zz))
        mesh('Tampa inclinada capota '+str(side)+' '+str(k),verts,[(0,1,2,3)],brown,'CAPOTA',thickness=.025,bevel=.008)
        for yy in (y-.073,y+.073):
            for zz in (z-.044,z+.044):
                cylinder('Rebite tampa '+str(side)+str(k)+str(yy)+str(zz),(side*(.895-(zz-1.64)*.50+.051),yy,zz),.004,.006,silver,'CAPOTA',vertices=12)
    text('Prefixo lateral '+str(side),'3.1110',side,2.13,1.201,.115)
    text('RONDESP lateral '+str(side),'RONDESP',side,2.13,1.103,.067)
    # Bandeira baiana estilizada em faixas cromáticas vistas, sem emblema inventado.
    flag_red=scope['material']('Bandeira vermelho '+str(side),(.8,.02,.035))
    flag_blue=scope['material']('Bandeira azul '+str(side),(.16,.30,.57))
    for j,mat in enumerate((flag_red,white,flag_red)):
        box('Bandeira faixa '+str(side)+str(j),(side*.942,-1.01,1.226-j*.025),(.004,.092,.022),mat,'INSCRICOES',.001)
    box('Bandeira campo '+str(side),(side*.945,-1.034,1.225),(.004,.043,.027),flag_blue,'INSCRICOES',.001)

for side in (-1,1): hatch(side)

# Camuflagem de baixa frequência, orientada pelas faixas diagonais da foto.
# Autoral/candidata, não extração ou republicação da fotografia.
paint=scope['material']('Camuflagem marrom candidata',(.47,.33,.27),.05,.5)
nodes=paint.node_tree.nodes; links=paint.node_tree.links
tex=nodes.new('ShaderNodeTexCoord')
mapping=nodes.new('ShaderNodeMapping'); mapping.inputs['Rotation'].default_value=(0,.25,.62)
links.new(tex.outputs['Object'],mapping.inputs['Vector'])
wave=nodes.new('ShaderNodeTexWave'); wave.wave_type='BANDS'; wave.bands_direction='Y'; wave.wave_profile='SAW'
wave.inputs['Scale'].default_value=1.7; wave.inputs['Distortion'].default_value=1.1; wave.inputs['Detail Scale'].default_value=1
links.new(mapping.outputs['Vector'],wave.inputs['Vector'])
ramp=nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.interpolation='CONSTANT'
palette=[(0,(.45,.325,.27)),(.32,(.49,.36,.29)),(.52,(.39,.29,.26)),(.72,(.46,.33,.29)),(.84,(.54,.40,.30))]
for e in list(ramp.color_ramp.elements)[1:]: ramp.color_ramp.elements.remove(e)
for i,(p,c) in enumerate(palette):
    e=ramp.color_ramp.elements[0] if i==0 else ramp.color_ramp.elements.new(p)
    e.position=p; e.color=tuple(scope['linear'](v) for v in c)+(1,)
links.new(wave.outputs['Color'],ramp.inputs['Fac']); links.new(ramp.outputs['Color'],nodes.get('Principled BSDF').inputs['Base Color'])
for o in scene.objects:
    if o.type=='MESH' and any(o.name.startswith('RDP01 | '+x) for x in ('Porta dianteira','Porta traseira','Para-lama dianteiro','Caçamba','Capô','Tampa traseira caçamba')):
        o.data.materials[0]=paint
        o['boas_paint_status']='candidate; faixas inspiradas nas fotos, mapa exato não medido'

# Tampa traseira da capota: janela escura real, junta, dobradiças e prefixo.
rear_poly=[(-.68,1.45),(.68,1.45),(.72,1.60),(.67,1.84),(.55,1.89),(-.55,1.89),(-.67,1.84),(-.72,1.60)]
pts=[(x,2.619,z) for x,z in rear_poly]
mesh('Vidro tampa capota traseira',pts,[tuple(range(8))],glass,'VIDROS',thickness=.008)
tube('Vedação vidro traseiro capota',pts,.022,black,'CAPOTA',True)
for x in (-.48,.48):
    box('Dobradiça capota traseira '+str(x),(x,2.65,1.93),(.04,.035,.09),black,'CAPOTA',.009)
box('Fecho capota traseira',(0,2.653,1.39),(.12,.02,.03),black,'CAPOTA',.009)
box('Puxador tampa caçamba',(0,2.666,1.145),(.25,.027,.07),black,'ACABAMENTOS',.025)
box('Terceira luz freio',(0,2.656,1.30),(.30,.012,.028),red,'LUZES',.007)
remove_prefix(['Lanterna traseira','Lanterna ré'])
for side in (-1,1):
    outline=[(side*.903,2.654,1.21),(side*.784,2.661,1.18),(side*.725,2.665,1.04),(side*.659,2.668,.849),(side*.737,2.671,.751),(side*.904,2.655,.762)]
    mesh('Lanterna traseira angular '+str(side),outline,[tuple(range(6))],black,'LUZES',thickness=.024)
    c=Vector((side*.80,2.68,.98))
    inset=[]
    for p in outline:
        q=c+(Vector(p)-c)*.91; q.y+=.005; inset.append(q)
    mesh('Lente vermelha traseira '+str(side),inset,[tuple(range(6))],red,'LUZES',thickness=.006)
    for z in (.84,.91,1.02,1.125):
        tube('Filete lanterna '+str(side)+str(z),[(side*.77,2.688,z),(side*.89,2.671,z+.01)],.009,black,'LUZES')
    box('Ré traseira '+str(side),(side*.86,2.684,.81),(.063,.008,.064),clear,'LUZES',.008)

def rear_text(label,body,x,z,size):
    cu=bpy.data.curves.new('RDP01 | '+label,'FONT'); cu.body=body; cu.size=size; cu.align_x='CENTER'; cu.align_y='CENTER'; cu.extrude=.0003
    ob=bpy.data.objects.new(cu.name,cu); scope['collections']['INSCRICOES'].objects.link(ob)
    ob.location=(x,2.664,z); ob.rotation_euler=(math.pi/2,0,math.pi)
    cu.materials.append(white); ob.parent=scope['root']
rear_text('Prefixo vidro traseiro','3.1110',0,1.674,.205)
rear_text('POLÍCIA MILITAR traseira','POLÍCIA MILITAR',0,.89,.12)
for x in (-.54,.54):
    box('Apoio passo para-choque traseiro '+str(x),(x,2.75,.58),(.57,.22,.07),black,bevel=.022)
box('Engate reboque',(0,2.81,.375),(.075,.19,.055),steel,'CHASSIS')
bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,radius=.025,location=(0,2.894,.415))
scope['attach'](bpy.context.object,'CHASSIS',silver)
bpy.context.object.name='RDP01 | Esfera engate'

# Suporte e barra clara como nas novas fotos; módulos vermelhos ficam sob a lente.
bar=scene.objects['RDP01 | Barra vermelha']; bar.data.materials[0]=clear
for side in (-1,1):
    tube('Longarina suporte teto '+str(side),[(side*.64,-.25,1.96),(side*.64,.62,1.99),(side*.57,.83,1.94)],.018,black,'LUZES')
for y in (-.10,.49):
    tube('Travessa suporte teto '+str(y),[(-.64,y,1.982),(.64,y,1.982)],.013,black,'LUZES')
    for x in (-.53,-.37,-.2,.2,.37,.53):
        box('LED vermelho barra '+str(y)+str(x),(x,.044,2.052),(.057,.142,.033),red,'LUZES',.005)
tube('Antena rádio',[(.43,.71,1.94),(.43,.73,2.77)],.003,black,'LUZES')

scene['boas_vehicle_model_reference']='Toyota Hilux CD 2.8 2024/2025; legenda da foto enviada, não verificação VIN'
scene['boas_unit_prefix']='3.1110'
scene['boas_reference']='rondesp-pickup-user-front-left; rondesp-31110-front; rondesp-31110-rear'
scene['boas_pending_details']=json.dumps(['brasão PMBA detalhado','confirmação de dimensões','mapa exato da camuflagem','mecanismos portas ainda sem teste'],ensure_ascii=False)
scene.camera.location=(-8,-5.6,3.15)
scene.camera.rotation_euler=(Vector((0,0,1.02))-scene.camera.location).to_track_quat('-Z','Y').to_euler()
scene.camera.data.ortho_scale=6.65
scene.cycles.samples=20
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            s=area.spaces.active
            s.region_3d.view_rotation=scene.camera.rotation_euler.to_quaternion()
            s.region_3d.view_location=(0,0,1)
            s.region_3d.view_distance=7
            s.region_3d.view_perspective='ORTHO'
bpy.context.view_layer.update()
out=repo/'blender/assets/vehicles/rondesp-pickup/marrom_v01.blend'
bpy.data.libraries.write(str(out),{scene},path_remap='RELATIVE',fake_user=True,compress=True)
path=repo/'docs/reports/blender/rondesp_marrom_v01.json'
report=json.loads(path.read_text(encoding='utf-8'))
report.update({'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'prefix':'3.1110','model_reference':scene['boas_vehicle_model_reference'],'pending':json.loads(scene['boas_pending_details']),'references':scene['boas_reference'],'vehicle_objects':sum(1 for o in scene.objects if not any(c==scope['collections']['APRESENTACAO'] for c in o.users_collection))})
path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
