"""Refino de forma, aros de aço, lentes e camuflagem após comparação das fotos."""
import bpy,bmesh,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
repo=Path(__file__).resolve().parents[2]
scene=bpy.context.scene
assert scene.name=='VIATURA | Rondesp picape marrom v02'
out=repo/'blender/assets/vehicles/rondesp-pickup/marrom_v03.blend'
assert not out.exists()
root=scene.objects['RDP01_ROOT | viatura']
coll=bpy.data.collections['RDP01 | RODAS']
black=bpy.data.materials['RDP01 | Polímero preto']
steel=bpy.data.materials['RDP01 | Aço preto rodas']
rubber=bpy.data.materials['RDP01 | Borracha pneus']
brown=bpy.data.materials['RDP01 | Pintura marrom Rondesp']

def part(name,vs,fs,mat,collection,parent=root):
    me=bpy.data.meshes.new('RDP03 | '+name);me.from_pydata(vs,[],fs);me.update()
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    ob=bpy.data.objects.new('RDP03 | '+name,me);collection.objects.link(ob);me.materials.append(mat);ob.parent=parent
    ob['boas_asset_id']='vehicle-rondesp-pickup'
    return ob

def remove(prefix):
    for o in list(scene.objects):
        if o.name.startswith(prefix): bpy.data.objects.remove(o,do_unlink=True)

# Elimina degrau indevido capô/para-lama; reconstrói perfil superior do painel.
controls=[(-2.70,1.11),(-2.50,1.21),(-2.35,1.275),(-1.43,1.325),(-1.02,1.355),(-.85,1.31)]
def lerp_profile(y):
    for (a,za),(b,zb) in zip(controls,controls[1:]):
        if a<=y<=b:return za+(zb-za)*(y-a)/(b-a)
    return controls[0][1] if y<controls[0][0] else controls[-1][1]
for side in (-1,1):
    fender=scene.objects[f'RDP01 | Para-lama dianteiro {side:+}']
    vs=fender.data.vertices
    for i in range(61):
        low=vs[i*5].co.z
        y=vs[i*5].co.y
        top=lerp_profile(y)
        for k,f in enumerate((0,.15,.62,.84,1)):
            vs[i*5+k].co.z=low+(top-low)*f
    fender.data.update()

# Superfície do capô com mais curvas transversais, sem degraus de seção.
remove('RDP01 | Capô conformado')
verts=[]
for j in range(29):
    y=-2.64+1.62*j/28
    z=lerp_profile(y)+.012
    w=.86+.025*math.sin(math.pi*j/28)
    for i in range(33):
        u=-1+2*i/32
        # Ombros de borda e dois vincos sutis, próprios do capô visto na foto.
        crown=.032*(1-u*u)+.009*math.exp(-((abs(u)-.56)/.10)**2)
        verts.append((w*u,y,z+crown))
hood=part('Capô abaulado',verts,[(j*33+i,j*33+i+1,(j+1)*33+i+1,(j+1)*33+i) for j in range(28) for i in range(32)],brown,bpy.data.collections['RDP01 | CARROCERIA'])
sol=hood.modifiers.new('Chapa capô','SOLIDIFY');sol.thickness=.022
for p in hood.data.polygons:p.use_smooth=True

# Aro estampado com doze perfurações reais; substitui braços que pareciam esportivos.
remove('RDP01 | Braço aço aro ')
for side in (-1,1):
    for ai,y in enumerate((-1.43,1.655)):
        pivot=scene.objects[f'RDP01 | Eixo giro roda {ai} {side:+}']
        verts=[];rings=[(.068,.145),(.109,.129),(.132,.123),(.170,.126),(.201,.145)];n=144
        for r,dx in rings:
            for i in range(n):
                a=2*math.pi*i/n
                # Coords do pivô: seu X é o eixo físico de rotação.
                verts.append((side*dx,math.sin(a)*r,math.cos(a)*r))
        fs=[]
        for j in range(4):
            for i in range(n):
                # Buracos arredondados por bevel nas paredes da chapa estampada.
                if j==2 and 3<=(i%12)<=7:continue
                fs.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
        ob=part(f'Aro aço estampado {ai} {side:+}',verts,fs,steel,coll,pivot)
        sol=ob.modifiers.new('Chapa aro','SOLIDIFY');sol.thickness=.006
        bevel=ob.modifiers.new('Borda perfurações','BEVEL');bevel.width=.004;bevel.segments=3
        for p in ob.data.polygons:p.use_smooth=True
        # Consolida somente blocos do mesmo pneu, preservando movimento independente.
        blocks=[o for o in scene.objects if o.name.startswith(f'RDP01 | Bloco banda pneu {ai} {side:+} ')]
        vv=[];ff=[]
        inv=pivot.matrix_world.inverted()
        for block in blocks:
            offset=len(vv);m=inv@block.matrix_world
            vv.extend(tuple(m@v.co) for v in block.data.vertices)
            ff.extend(tuple(offset+k for k in p.vertices) for p in block.data.polygons)
        tread=part(f'Banda pneu {ai} {side:+}',vv,ff,rubber,coll,pivot)
        bevel=tread.modifiers.new('Aresta blocos borracha','BEVEL');bevel.width=.003;bevel.segments=2
        for b in blocks:bpy.data.objects.remove(b,do_unlink=True)

# Faces abertas tinham Solidify para o lado errado e escondiam as lentes.
for ob in scene.objects:
    if ob.name.startswith('RDP01 | Lanterna traseira angular '):
        for mod in ob.modifiers:
            if mod.type=='SOLIDIFY':mod.offset=0;mod.thickness=.01
    if ob.name.startswith('RDP01 | Lente vermelha traseira '):
        for v in ob.data.vertices:v.co.y+=.031
    if ob.name.startswith('RDP01 | Farol 2024 carcaça '):
        for mod in ob.modifiers:
            if mod.type=='SOLIDIFY':mod.offset=0;mod.thickness=.01
    if ob.name.startswith('RDP01 | Farol 2024 lente '):
        for v in ob.data.vertices:v.co.y-=.021
    if ob.type=='FONT':
        ob.data.offset=.0014
        if 'Prefixo lateral' in ob.name:ob.data.size=.122

# Cores em faces: camuflagem legível também em preview sólido, sem ruído de shader.
# Padrão inspirado nas bandas largas da referência, marcado como candidato.
colors=[(.46,.335,.285),(.42,.315,.285),(.52,.385,.29),(.465,.35,.30)]
palette=[]
for i,c in enumerate(colors):
    m=brown.copy();m.name='RDP03 | Camuflagem tom '+str(i)
    rgba=tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in c)+(1,)
    m.diffuse_color=rgba;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=rgba
    palette.append(m)
for ob in scene.objects:
    if ob.type!='MESH' or not any(ob.name.startswith(p) for p in ('RDP01 | Porta dianteira','RDP01 | Porta traseira','RDP01 | Para-lama dianteiro','RDP01 | Caçamba','RDP03 | Capô abaulado','RDP01 | Tampa traseira caçamba')):continue
    ob.data.materials.clear()
    for m in palette:ob.data.materials.append(m)
    for p in ob.data.polygons:
        c=sum((ob.data.vertices[i].co for i in p.vertices),Vector())/len(p.vertices)
        band=(c.y+.70*c.z+.05*math.sin(c.y*3.1))/.59
        p.material_index=int(math.floor(band))%len(palette)
    ob['boas_paint_status']='candidate; bandas largas observadas, desenho exato pendente'

# Remove peças invisíveis/soltas de suporte junto às rodas que ficaram verticais:
# os eixos de CHASSIS foram cilindros orientados X; cilindros corretos permanecem.
for o in list(scene.objects):
    if o.name.startswith('RDP01 | Eixo ') and not o.name.startswith('RDP01 | Eixo giro'):
        # O construtor anterior usou Y no contexto? Torna explícita a orientação física.
        o.rotation_euler=(0,math.pi/2,0)

scene.name='VIATURA | Rondesp picape marrom v03'
scene['boas_revision']='v03'
scene['boas_revision_parent']='blender/assets/vehicles/rondesp-pickup/marrom_v02.blend'
scene['boas_pending_details']=json.dumps(['brasão PMBA detalhado','confirmação de dimensões','mapa exato camuflagem','animação e inscrição dividida por folhas'],ensure_ascii=False)
bpy.context.view_layer.update()
scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.studio_light='paint.sl';scene.display.shading.color_type='MATERIAL'
scene.display.shading.light='STUDIO';scene.display.shading.show_cavity=True
scene.display.shading.cavity_type='BOTH';scene.display.shading.show_shadows=True
scene.render.resolution_x=1100;scene.render.resolution_y=730
scene.camera.location=(-8,-5.6,3.15)
scene.camera.rotation_euler=(Vector((0,0,1.02))-scene.camera.location).to_track_quat('-Z','Y').to_euler()
bpy.data.libraries.write(str(out),{scene},path_remap='RELATIVE',fake_user=True,compress=True)
report=json.loads((repo/'docs/reports/blender/rondesp_marrom_v02.json').read_text(encoding='utf-8'))
report.update({'file':out.relative_to(repo).as_posix(),'scene':scene.name,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'revision_parent':'blender/assets/vehicles/rondesp-pickup/marrom_v02.blend','vehicle_objects':len(scene.objects)-5,'pending':json.loads(scene['boas_pending_details']),'visual_review':'pending','reopened':'pending','corrections_v03':['perfil capô/para-lamas contínuo','aros aço com doze aberturas','lentes expostas','camuflagem bandas largas','quatro bandas de pneu agrupadas por roda']})
(repo/'docs/reports/blender/rondesp_marrom_v03.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
folder=repo/'artifacts/vehicles/rondesp'
scene.render.filepath=str(folder/'v03-frente-geometria.png');bpy.ops.render.render(write_still=True)
scene.camera.location=(-7,6,3.15)
scene.camera.rotation_euler=(Vector((0,0,1.02))-scene.camera.location).to_track_quat('-Z','Y').to_euler()
scene.render.filepath=str(folder/'v03-traseira-geometria.png');bpy.ops.render.render(write_still=True)
