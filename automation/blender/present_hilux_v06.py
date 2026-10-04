"""Batentes construídos, ópticas com lente e identificação da viatura V06."""
import bpy,bmesh,math,ast,json,hashlib,os
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.geometry import delaunay_2d_cdt
from mathutils.bvhtree import BVHTree
repo=Path(__file__).resolve().parents[2];scene=bpy.context.scene
assert Path(bpy.data.filepath).name=='marrom_v06.blend'
root=scene.objects['RDP01_ROOT | viatura']
groups=['CARROCERIA','PORTAS','CAPOTA','VIDROS','RODAS','CHASSIS','LUZES','ACABAMENTOS','INSCRICOES','APRESENTACAO']
collections={g:bpy.data.collections['RDP01 | '+g] for g in groups}
brown=bpy.data.materials['RDP01 | Pintura marrom Rondesp'];black=bpy.data.materials['RDP01 | Polímero preto'];silver=bpy.data.materials['RDP01 | Metal acetinado'];glass=bpy.data.materials['RDP01 | Vidro fumê'];paint=bpy.data.materials['RDP01 | Camuflagem marrom candidata'];red=bpy.data.materials['RDP01 | Lentes vermelhas'];white=bpy.data.materials['RDP01 | Inscrição branca'];clear=bpy.data.materials['RDP01 | Lentes transparentes']
for file,names in [('create_rondesp_pickup_v01.py',['mesh','box','tube','cylinder']),('rebuild_hilux_reference_v06.py',['part','grid','interp','bezier_loop','inside','sheet','sidewidth','cabwidth']),('finish_hilux_reference_v06.py',['nose'])]:
    tree=ast.parse((repo/'automation/blender'/file).read_text(encoding='utf-8'))
    for fn in tree.body:
        if isinstance(fn,ast.FunctionDef) and fn.name in names:exec(compile(ast.Module(body=[fn],type_ignores=[]),'<hilux-final>','exec'),globals())

for side in [-1,1]:
    holes=[]
    for label,a,b in [('dianteira',-.968,.093),('traseira',.101,1.12)]:
        def edge(u,t):
            z=.493+.798*t;left=a+.080*(1-t)**9;right=b-.060*(1-t)**8+.028*t**5
            if label=='traseira':right-=.034*t**4
            return Vector((left+(right-left)*u,z))
        loop=[edge(i/40,0) for i in range(41)]+[edge(1,j/30) for j in range(1,31)]+[edge(1-i/40,1) for i in range(1,41)]+[edge(0,1-j/30) for j in range(1,31)]
        center=sum(loop,Vector((0,0)))/len(loop)
        holes.append([center+(p-center)*1.005 for p in loop])
    outline=[Vector(p) for p in [(-.980,.463),(1.145,.463),(1.145,1.302),(-.980,1.302)]]
    sheet('Batentes externos e soleira '+str(side),outline,holes,lambda p:(side*sidewidth(p.x,p.y),p.x,p.y),paint,normal=(side,0,0),spacing=.022)
    # O interior de cada caixa de roda é uma superfície própria, não carroceria tampando roda.
    for axle in [-1.43,1.655]:
        grid('Caixa interna roda '+str((side,axle)),lambda u,t:(side*(.56+.30*t),axle+.515*math.cos(math.pi*u),.38815+.515*math.sin(math.pi*u)),64,12,black,normal=(0,0,-1),thick=.008)

# Refletores retangulares curvos e lente transparente sobre o conjunto.
for o in list(scene.objects):
    if 'HILUX06 | Refletor parabólico' in o.name or 'HILUX06 | Lâmpada' in o.name:bpy.data.objects.remove(o,do_unlink=True)
light=bezier_loop([(.510,1.140),(.715,1.164),(.922,1.216),(.907,1.096),(.805,.986),(.594,.998),(.536,1.025)],.15,10)
clear.diffuse_color=(.42,.48,.50,1)
p=clear.node_tree.nodes.get('Principled BSDF');p.inputs['Transmission Weight'].default_value=1;p.inputs['Roughness'].default_value=.065;p.inputs['Metallic'].default_value=0;p.inputs['IOR'].default_value=1.46
for side in [-1,1]:
    for j,(x,z,rx,rz) in enumerate([(.636,1.071,.088,.054),(.798,1.107,.078,.061)]):
        def optical(u,v):
            a=u*math.tau;r=.20+.80*v
            xx=math.copysign(abs(math.cos(a))**.50,math.cos(a));zz=math.copysign(abs(math.sin(a))**.50,math.sin(a))
            px=side*(x+rx*r*xx);pz=z+rz*r*zz
            return px,nose(px,pz,.009)+.020*(1-r*r),pz
        grid('Câmara refletora '+str((side,j)),optical,64,12,silver,'LUZES',(0,-1,0),.002)
        cylinder('HILUX06 | Núcleo óptico '+str((side,j)),(side*x,nose(side*x,z,.009),z),.012,.008,silver,'LUZES','Y',24)
    loop=[Vector((side*p.x,p.y)) for p in light];c=sum(loop,Vector((0,0)))/len(loop);loop=[c+(p-c)*.942 for p in loop]
    lens=sheet('Lente óptica transparente '+str(side),loop,[],lambda p:(p.x,nose(p.x,p.y,-.012),p.y),clear,'LUZES',(0,-1,0),spacing=.020)

# Inscrições reconstruídas em fonte consistente, conformadas à chapa atual.
for o in list(scene.objects):
    if collections['INSCRICOES'] not in o.users_collection:continue
    text=o.data.body if o.type=='FONT' else o.get('boas_inscription_text','')
    if any(s in text.upper() for s in ['POLÍCIA','POLICIA','RONDESP','3.1110']):bpy.data.objects.remove(o,do_unlink=True)
fontpath=Path(os.environ.get('WINDIR','C:/Windows'))/'Fonts/arialbd.ttf'
font=bpy.data.fonts.load(str(fontpath)) if fontpath.exists() else bpy.data.fonts[0]
try:font.pack()
except Exception:pass
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();verts=[];faces=[]
for o in scene.objects:
    if o.type!='MESH' or not any(collections[g] in o.users_collection for g in ['CARROCERIA','PORTAS']):continue
    ev=o.evaluated_get(dg);m=ev.to_mesh();base=len(verts);verts.extend(ev.matrix_world@v.co for v in m.vertices);faces.extend(tuple(base+i for i in p.vertices) for p in m.polygons);ev.to_mesh_clear()
bvh=BVHTree.FromPolygons(verts,faces)
def lettering(label,text,loc,width,side=None):
    cu=bpy.data.curves.new('HILUX06 '+label,'FONT');cu.body=text;cu.font=font;cu.align_x='CENTER';cu.size=.15;cu.resolution_u=10
    o=bpy.data.objects.new('RDP01 | HILUX06 | '+label,cu);collections['INSCRICOES'].objects.link(o);o.data.materials.append(white);o.parent=root;o.location=loc
    rot=Matrix(((0,0,side),(side,0,0),(0,1,0))) if side else Matrix(((-1,0,0),(0,0,1),(0,1,0)))
    o.rotation_euler=rot.to_euler();bpy.context.view_layer.update()
    factor=width/max(o.dimensions.length,1e-6)
    # Fonte local: largura própria independente da orientação mundial.
    ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=bpy.data.meshes.new_from_object(ev)
    actual=max(v.co.x for v in m.vertices)-min(v.co.x for v in m.vertices);factor=width/actual
    for v in m.vertices:v.co*=factor
    if side:
        bm=bmesh.new();bm.from_mesh(m);bmesh.ops.triangulate(bm,faces=list(bm.faces))
        long=[e for e in bm.edges if e.calc_length()>.018]
        if long:bmesh.ops.subdivide_edges(bm,edges=long,cuts=4,use_grid_fill=True)
        bm.to_mesh(m);bm.free()
    mat=o.matrix_world.copy()
    for v in m.vertices:
        p=mat@v.co
        if side:
            hit,normal,index,d=bvh.ray_cast(Vector((side*2,p.y,p.z)),Vector((-side,0,0)),2)
            if hit is not None:p=hit+Vector((side*.0025,0,0))
        v.co=p
    new=bpy.data.objects.new(o.name,m);collections['INSCRICOES'].objects.link(new);new.parent=root;new['boas_inscription_text']=text
    bpy.data.objects.remove(o,do_unlink=True)
for side in [-1,1]:
    lettering('POLÍCIA MILITAR '+str(side),'POLÍCIA MILITAR',(side*.90,.10,.666),1.61,side)
    lettering('Prefixo lateral '+str(side),'3.1110',(side*.91,2.11,1.11),.48,side)
    lettering('RONDESP '+str(side),'RONDESP',(side*.91,2.11,1.015),.44,side)
lettering('POLÍCIA MILITAR traseira','POLÍCIA MILITAR',(0,2.797,.69),1.30)
lettering('Prefixo vidro traseiro','3.1110',(0,2.755,1.475),.66)

# Apresentação PBR simples: permite julgar as chapas sob reflexos amplos.
for o in list(scene.objects):
    if o.type=='LIGHT':bpy.data.objects.remove(o,do_unlink=True)
def area(name,pos,power,size,target=(0,0,1)):
    d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size
    o=bpy.data.objects.new(name,d);collections['APRESENTACAO'].objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
area('HILUX06 | Luz principal',(-4,-5,6),1500,5)
area('HILUX06 | Luz lateral',(4,-1,4),1150,4)
area('HILUX06 | Luz contorno',(0,5,5),1700,4)
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.38,.42,.46,1);scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.45
for m in [brown,paint]:
    n=m.node_tree.nodes.get('Principled BSDF');n.inputs['Roughness'].default_value=.34;n.inputs['Coat Weight'].default_value=.28;n.inputs['Coat Roughness'].default_value=.24
scene.render.engine='CYCLES';scene.cycles.samples=12;scene.cycles.use_denoising=True;scene.cycles.device='CPU';scene.render.threads_mode='FIXED';scene.render.threads=8
scene.render.resolution_x=1050;scene.render.resolution_y=680;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX';scene.view_settings.exposure=0
scene.camera.location=(-7,-8,3.4);scene.camera.rotation_euler=(Vector((0,.16,1.03))-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.camera.data.ortho_scale=6.65
for screen in bpy.data.screens:
    for a in screen.areas:
        if a.type=='VIEW_3D':
            s=a.spaces.active;s.shading.type='SOLID';s.shading.color_type='MATERIAL';s.shading.light='STUDIO';s.shading.studio_light='paint.sl';s.shading.show_cavity=False
            s.region_3d.view_rotation=scene.camera.rotation_euler.to_quaternion();s.region_3d.view_location=(0,.16,1.0);s.region_3d.view_distance=7

# Salvar fonte antes da imagem. Esta imagem serve à revisão, não aprova o asset.
out=repo/'blender/assets/vehicles/rondesp-pickup/marrom_v06.blend'
bpy.context.view_layer.update();bpy.data.libraries.write(str(out),{scene},path_remap='RELATIVE',fake_user=True,compress=True)
path=repo/'docs/reports/blender/rondesp_marrom_v06.json';r=json.loads(path.read_text(encoding='utf-8'))
r.update(sha256=hashlib.sha256(out.read_bytes()).hexdigest(),source_saved=True,objects=len(scene.objects),wheelbase_measured_m=abs(scene.objects['RDP01 | Eixo giro roda 1 -1'].location.y-scene.objects['RDP01 | Eixo giro roda 0 -1'].location.y),pending=['aprovação visual de fidelidade','brasão PMBA detalhado','mapeamento exato de camuflagem','animação e integração runtime'])
path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
scene.render.filepath=str(repo/'artifacts/vehicles/rondesp/v06-materiais.png');bpy.ops.render.render(write_still=True)
def reopen():bpy.ops.wm.open_mainfile(filepath=str(out));return None
bpy.app.timers.register(reopen,first_interval=.5)
