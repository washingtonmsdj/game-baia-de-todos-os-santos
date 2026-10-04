"""Encaixe das chapas V06, máscara Hilux e reposição do conjunto Rondesp."""
import bpy,bmesh,math,ast,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.geometry import delaunay_2d_cdt
from mathutils.bvhtree import BVHTree
repo=Path(__file__).resolve().parents[2];scene=bpy.context.scene
assert Path(bpy.data.filepath).name=='marrom_v06.blend'
root=scene.objects['RDP01_ROOT | viatura']
groups=['CARROCERIA','PORTAS','CAPOTA','VIDROS','RODAS','CHASSIS','LUZES','ACABAMENTOS','INSCRICOES','APRESENTACAO']
collections={g:bpy.data.collections['RDP01 | '+g] for g in groups}
brown=bpy.data.materials['RDP01 | Pintura marrom Rondesp'];black=bpy.data.materials['RDP01 | Polímero preto']
silver=bpy.data.materials['RDP01 | Metal acetinado'];glass=bpy.data.materials['RDP01 | Vidro fumê'];paint=bpy.data.materials['RDP01 | Camuflagem marrom candidata'];red=bpy.data.materials['RDP01 | Lentes vermelhas']
for file,names in [('create_rondesp_pickup_v01.py',['mesh','box','tube','cylinder']),('rebuild_hilux_reference_v06.py',['part','grid','interp','bezier_loop','inside','sheet','rim','sidewidth','arch','cabwidth','fronttop','cap','cap_x'])]:
    tree=ast.parse((repo/'automation/blender'/file).read_text(encoding='utf-8'))
    for fn in tree.body:
        if isinstance(fn,ast.FunctionDef) and fn.name in names:exec(compile(ast.Module(body=[fn],type_ignores=[]),'<hilux-shape>','exec'),globals())

def nose(x,z,offset=0):
    y=-2.435+.49*(abs(x)/.9275)**3.5+.16*math.exp(-((z-.45)/.12)**2)
    y-=.033*math.exp(-((z-.595)/.058)**2)*math.exp(-(x/.65)**8)
    y+=.029*math.exp(-((z-.77)/.16)**2)*math.exp(-((abs(x)-.69)/.14)**2)
    return y+offset

def upper(u,v):
    frac=-1+2*v;w=.9275-.093*u**3;x=w*frac
    yf=-2.435+.49*abs(frac)**3.5;y=yf+(-.975-yf)*u
    z=fronttop(.9275*frac)*(1-u)+1.303*u+.025*math.sin(math.pi*u)
    z+=.020*(1-frac*frac)*u+.013*math.exp(-((abs(frac)-.63)/.09)**2)*math.sin(math.pi*u)
    z-=.038*abs(frac)**10*math.sin(math.pi*u)
    return x,y,z

def replace_grid(ob,fn,nu,nv):
    for i in range(nu+1):
        for j in range(nv+1):ob.data.vertices[i*(nv+1)+j].co=fn(i/nu,j/nv)
    ob.data.update()
replace_grid(scene.objects['RDP01 | HILUX06 | Capô e ombros estampados'],upper,66,72)
for side in [-1,1]:
    def fender(u,t):
        y=-1.945+(.970)*u;low=arch(y,-1.43);top=upper(u,0)[2];z=low+(top-low)*t
        x=sidewidth(y,z)*(1-t**4)+(.9275-.093*u**3)*t**4
        return side*x,y,z
    replace_grid(scene.objects['RDP01 | HILUX06 | Para-lama dianteiro '+str(side)],fender,72,30)
    seam=scene.objects['RDP01 | HILUX06 | Junta capô '+str(side)]
    for j,p in enumerate(seam.data.splines[0].points):p.co=(*upper(j/60,(side*.84+1)/2),1)
    # Bordo de A e teto passam a compartilhar o limite do para-brisa.
    ob=scene.objects['RDP01 | HILUX06 | Montante A curvo '+str(side)]
    for v in ob.data.vertices:
        if v.co.z>1.72:v.co.z+=.012*(v.co.z-1.72)/.05
    # Suavização dos retrovisores arredondados, preservando faces da lente.
    ob=scene.objects['RDP01 | HILUX06 | Espelho '+str(side)]
    for m in ob.modifiers:
        if m.type=='BEVEL':m.segments=6
    for p in ob.data.polygons:p.use_smooth=True
    ob.modifiers.new('Normais carcaça','WEIGHTED_NORMAL')

remove=['Para-choque e testa','Moldura máscara','Fundo grade','Travessa central máscara']
for o in list(scene.objects):
    if 'HILUX06' in o.name and (any(s in o.name for s in remove) or any(s in o.name for s in ['Grelha horizontal','Montante grade','Toyota '])):bpy.data.objects.remove(o,do_unlink=True)
outer=bezier_loop([(-.9275,.55),(-.9275,1.237),(-.73,1.185),(-.50,1.155),(0,1.137),(.50,1.155),(.73,1.185),(.9275,1.237),(.9275,.55),(.80,.46),(.50,.455),(.35,.508),(-.35,.508),(-.50,.455),(-.80,.46)],.14,8)
mask=bezier_loop([(-.476,1.126),(.476,1.126),(.552,.959),(.505,.778),(.425,.722),(-.425,.722),(-.505,.778),(-.552,.959)],.18,10)
light=bezier_loop([(.510,1.140),(.715,1.164),(.922,1.216),(.907,1.096),(.805,.986),(.594,.998),(.536,1.025)],.15,10)
lights=[[Vector((s*p.x,p.y)) for p in light] for s in [-1,1]]
slot=bezier_loop([(-.444,.588),(.444,.588),(.407,.650),(-.407,.650)],.23,12)
sheet('Para-choque e testa esculpidos',outer,[mask,slot]+lights,lambda p:(p.x,nose(p.x,p.y),p.y),paint,normal=(0,-1,0),spacing=.019)
inn=rim('Moldura máscara Hilux STD',mask,lambda p:(p.x,nose(p.x,p.y,-.007),p.y),black,.13)
sheet('Fundo máscara Hilux STD',inn,[],lambda p:(p.x,nose(p.x,p.y,.045),p.y),black,'ACABAMENTOS',(0,-1,0))
sheet('Fundo entrada baixa',slot,[],lambda p:(p.x,nose(p.x,p.y,.02),p.y),black,'ACABAMENTOS',(0,-1,0))
grid('Travessa máscara Hilux STD',lambda u,t:(-.492+.984*u,nose(-.492+.984*u,.905+.052*t,-.008),.905+.052*t),48,6,black,normal=(0,-1,0))
for z,w in [(1.077,.44),(1.023,.46),(.865,.463),(.82,.44),(.776,.404)]:
    tube('HILUX06 | Aleta grelha',[(x,nose(x,z,.006),z) for x in [-w+2*w*i/40 for i in range(41)]],.007,black)
for x in [-.38,-.25,-.12,.12,.25,.38]:
    tube('HILUX06 | Nervura grelha',[(x,nose(x,z,.012),z) for z in [.785,.90,.99,1.095]],.005,black)
for name,rx,rz in [('oval',.056,.037),('vertical',.021,.034),('horizontal',.051,.015)]:
    tube('HILUX06 | Toyota '+name,[(rx*math.cos(a),nose(rx*math.cos(a),1.027+rz*math.sin(a),-.027),1.027+rz*math.sin(a)) for a in [i*math.tau/64 for i in range(64)]],.0035,silver,closed=True)
box('HILUX06 | Suporte placa',(0,-2.445,.692),(.39,.018,.125),black,bevel=.015)

# Câmaras frontais visíveis; materiais neutros usados apenas na revisão de forma.
# Restabelece equipamentos preservados, nunca a chapa antiga substituída.
for name in json.loads(scene.get('boas_v06_equipment_hidden_for_review','[]')):
    o=scene.objects.get(name)
    if o:o.hide_render=False;o.hide_set(False)
del scene['boas_v06_equipment_hidden_for_review']

# Lista os equipamentos existentes para conferir fixação e evitar sobreposições.
inventory=[]
for o in scene.objects:
    if o.type!='EMPTY' and any(collections[g] in o.users_collection for g in ['CAPOTA','ACABAMENTOS','LUZES','INSCRICOES']):
        inventory.append({'name':o.name,'type':o.type,'loc':list(o.location),'text':o.get('boas_inscription_text')})
(repo/'artifacts/vehicles/rondesp/v06-components.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2),encoding='utf-8')

# Lanternas com retorno lateral, volume de lente e elementos internos.
for side in [-1,1]:
    loop=bezier_loop([(2.743,1.255),(2.781,1.199),(2.788,.675),(2.665,.651),(2.485,.79),(2.585,.973)],.15,10)
    def tail(p,offset=0):
        y,z=p;x=sidewidth(y,z)-.02+.014*(y-2.49)/.30
        return(side*(x+offset),y,z)
    sheet('Base lanterna traseira '+str(side),loop,[],lambda p:tail(p,.005),black,'LUZES',(side,0,0),.024)
    c=sum(loop,Vector((0,0)))/len(loop);inner=[c+(p-c)*.94 for p in loop]
    sheet('Lente vermelha traseira '+str(side),inner,[],lambda p:tail(p,.014),red,'LUZES',(side,0,0),.023)
    for z,a,b in [(1.095,2.62,2.775),(.943,2.552,2.777),(.767,2.558,2.780)]:
        poly=bezier_loop([(a,z-.039),(b,z-.039),(b,z+.039),(a+.05,z+.039)],.20)
        sheet('Segmento lanterna '+str((side,z)),poly,[],lambda p:tail(p,.018),silver if z==.943 else red,'LUZES',(side,0,0))
    # Retorno posterior das lanternas, orientado para a traseira.
    loop2=bezier_loop([(side*.725,.67),(side*.864,.67),(side*.864,1.25),(side*.752,1.25)],.20)
    sheet('Retorno lanterna '+str(side),loop2,[],lambda p:(p.x,2.784,p.y),red,'LUZES',(0,1,0))
    # Recria saídas da capota em escala compatível; painéis inclinados da referência.
    for j,y in enumerate([1.91,2.16,2.41]):
        flap=box('HILUX06 | Portinhola capota '+str((side,j)),(side*.848,y,1.63),(.027,.167,.110),brown,'CAPOTA',.009)
        flap.rotation_euler[1]=side*.18
        for dy in [-.070,.070]:
            cylinder('HILUX06 | Fixação portinhola',(side*.865,y+dy,1.655),.006,.004,silver,'CAPOTA',vertices=12)

# Vedações e fechamentos estruturais, não planos escondendo aberturas indevidas.
frontcap=[cap(0,j/80) for j in range(81)]
part('Parede frontal capota',frontcap,[tuple(range(81))],brown,'CAPOTA',.015,(0,-1,0))
for side in [-1,1]:
    # Acabamento de borda das chapas internas e estribos preservados.
    grid('Fechamento posterior cabine lateral '+str(side),lambda u,t:(side*(.795+.036*u),1.130+.025*u,.492+.798*t),5,32,paint,normal=(side,0,0))

# Reprojeta os decals somente na chapa atual, seguindo a curvatura e a espessura.
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();vs=[];fs=[]
for o in scene.objects:
    if o.type!='MESH' or not any(collections[g] in o.users_collection for g in ['CARROCERIA','PORTAS']):continue
    ev=o.evaluated_get(dg);m=ev.to_mesh();base=len(vs);vs.extend(ev.matrix_world@v.co for v in m.vertices);fs.extend(tuple(base+i for i in p.vertices) for p in m.polygons);ev.to_mesh_clear()
bvh=BVHTree.FromPolygons(vs,fs)
for o in scene.objects:
    if o.type!='MESH' or not o.get('boas_inscription_text'):continue
    for v in o.data.vertices:
        p=o.matrix_world@v.co;side=1 if p.x>0 else -1
        if p.y>2.7 or p.z>1.30:continue
        hit,normal,index,d=bvh.ray_cast(Vector((side*2,p.y,p.z)),Vector((-side,0,0)),2)
        if hit is not None:v.co=o.matrix_world.inverted()@(hit+Vector((side*.003,0,0)))
    o.data.update()

scene.display.shading.color_type='MATERIAL';scene.display.shading.studio_light='paint.sl';scene.display.shading.show_cavity=False
scene.display.shading.studiolight_rotate_z=.65
bpy.context.view_layer.update()
for name,pos,scale in [('frente',(-7,-8,3.1),6.5),('lateral',(-10,.16,1.1),6.5),('traseira',(-7,8,3.1),6.5)]:
    scene.camera.location=pos;scene.camera.rotation_euler=(Vector((0,.16,1.03))-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.camera.data.ortho_scale=scale
    scene.render.filepath=str(repo/f'artifacts/vehicles/rondesp/v06-{name}.png');bpy.ops.render.render(write_still=True)
scene.camera.location=(-7,-8,3.1);scene.camera.rotation_euler=(Vector((0,.16,1.03))-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.camera.data.ortho_scale=6.5
out=repo/'blender/assets/vehicles/rondesp-pickup/marrom_v06.blend'
bpy.data.libraries.write(str(out),{scene},path_remap='RELATIVE',fake_user=True,compress=True)
p=repo/'docs/reports/blender/rondesp_marrom_v06.json';r=json.loads(p.read_text(encoding='utf-8'))
r.update(sha256=hashlib.sha256(out.read_bytes()).hexdigest(),objects=len(scene.objects),pending=['aprovação visual','brasão PMBA','camuflagem exata'],equipment_restored=True)
p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def reopen():bpy.ops.wm.open_mainfile(filepath=str(out));return None
bpy.app.timers.register(reopen,first_interval=.5)
