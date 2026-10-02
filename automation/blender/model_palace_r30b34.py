"""Palácio Rio Branco: arquitetura observável nas nove fotos do usuário.

Preserva a planta B33, piso 70 m e outros marcos/ruas; detalhes não visíveis
não são inventados. Arquiva apenas o esboço substituído, sem apagar objetos.
"""
import bpy,json,runpy,math,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.geometry import tessellate_polygon
root=Path(__file__).resolve().parents[2];scene=bpy.context.scene
catalog=json.loads((root/'world/areas/mvp-centro-lacerda/blender-revisions.json').read_text(encoding='utf8'));before=catalog['authoring_source']
assert before['revision']=='R30B.33' and Path(bpy.data.filepath).resolve()==(root/before['file']).resolve()
assert bpy.data.collections.get('HERO | Palácio Rio Branco | fotografia R34') is None,'Passe já aplicado; não repetir'
bpy.context.view_layer.update()
Geometry=runpy.run_path(str(root/'automation/blender/architectural_mesh.py'))['Geometry']
signature=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'))['signature']
base=json.loads((root/'docs/reports/blender/cidade_baixa_r30b33.json').read_text(encoding='utf8'))
protected_names=set(base['road_signatures'])|set(base['preserved_components']) if 'preserved_components' in base else set(base['road_signatures'])
recovered=json.loads((root/'docs/reports/blender/cidade_baixa_r30b32.json').read_text(encoding='utf8'))
protected_names.update(recovered['restored_bodies']+recovered['restored_existing_components'])
protected_names.update(base['created_objects']);protected_names.update(x['body'] for x in base['buildings'])
protected_names.update(o.name for o in scene.objects if o.get('boas_location_id')=='elevador-lacerda' and o.type in ('MESH','CURVE','FONT') and not o.constraints)
protected={n:signature(scene.objects[n]) for n in sorted(protected_names)}
col=bpy.data.collections.new('HERO | Palácio Rio Branco | fotografia R34');scene.collection.children.link(col)
col['boas_role']='visual_architecture';col['boas_location_candidate']='palacio-rio-branco'
old=scene.objects['RIO BRANCO | corpo footprint 402383814'];old_signature=signature(old)
pts=[old.matrix_world@v.co for v in old.data.vertices];zbase=min(p.z for p in pts)
plan=[p for p in pts if abs(p.z-zbase)<.001];a,b=plan[1],plan[2];center=(a+b)/2
U=(b-a).normalized();N=Vector((-U.y,U.x,0));UP=Vector((0,0,1));W=(b-a).length
T=Matrix(((U.x,N.x,0,center.x),(U.y,N.y,0,center.y),(0,0,1,zbase),(0,0,0,1)));inv=T.inverted()
local=[inv@p for p in plan];created=[];archived=[]
props={'boas_revision':'R30B.34','boas_location_candidate':'palacio-rio-branco','osm_way_id':'402383814','boas_role':'visual_architecture','reference_status':'partial','classification':'ADAPT_LOCAL','dimensions_status':'proporções fotográficas candidatas; sem levantamento','reference_media_ids':json.dumps(json.loads((root/'artifacts/palacio-rio-branco/reference_pass.json').read_text())['media_ids'])}

def material(name,color,rough=.65,metal=0,trans=0,noise_scale=None):
    m=bpy.data.materials.new('RIO R34 | '+name);m.use_nodes=True;m.diffuse_color=(*color,1)
    p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=m.diffuse_color;p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;p.inputs['Transmission Weight'].default_value=trans
    if noise_scale:
        nt=m.node_tree;n=nt.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=noise_scale
        b=nt.nodes.new('ShaderNodeBump');b.inputs['Strength'].default_value=.12;b.inputs['Distance'].default_value=.003
        nt.links.new(n.outputs['Fac'],b.inputs['Height']);nt.links.new(b.outputs['Normal'],p.inputs['Normal'])
    return m
cream=material('reboco bege claro',(.73,.66,.53),noise_scale=80);ivory=material('ornatos e cornijas marfim',(.84,.83,.75),noise_scale=110)
stone=material('embasamento de pedra',(.48,.48,.44),noise_scale=32);dark=material('portas de madeira escura',(.075,.063,.048),.66)
glass=material('vidro transparente da fachada',(.40,.52,.55),.19,.08,.72);metal=material('grades e esquadrias',(.21,.24,.22),.38,.55)
roof=material('telha cerâmica envelhecida',(.34,.17,.095),noise_scale=70);dome=material('cobertura clara da cúpula',(.67,.69,.67),.48,.24,noise_scale=90)
buffers={};mats={}
def buf(name,mat):
    if name not in buffers:buffers[name]=Geometry();mats[name]=mat
    return buffers[name]
def box(name,c,s,mat=ivory):buf(name,mat).box(c,s)
def line(name,p,q,r,mat=ivory,n=8):buf(name,mat).bar(p,q,r,n)
def column(c,r,h,name='Colunas',mat=ivory):
    x,y,z=c;g=buf(name,mat);g.lathe((x,y,z),[(r*1.36,0),(r*1.36,.14),(r*1.16,.20),(r,.38),(r*.89,h-.45),(r*1.2,h-.28),(r*1.46,h-.19),(r*1.46,h)],20)
def facade_window(p,u,n,x,w,z,h,pediment=True):
    p=Vector(p);u,n=Vector(u),Vector(n)
    def pos(a,b,c):return p+u*a+n*b+UP*c
    # Vidro e caixilho ficam dentro do vão, não na frente de uma parede sólida.
    g=buf('Vidros das alas',glass);g.box(pos(x,-.22,z+h/2),(w,.026,h),(u,n,UP))
    f=buf('Caixilhos das alas',ivory)
    for xx in (x-w/2+.04,x,x+w/2-.04):f.box(pos(xx,-.16,z+h/2),(.055,.10,h),(u,n,UP))
    for zz in (z+.04,z+h*.30,z+h*.76,z+h-.04):f.box(pos(x,-.16,zz),(w,.10,.065),(u,n,UP))
    f=buf('Molduras e peitoris',ivory)
    for xx in (x-w/2-.12,x+w/2+.12):f.box(pos(xx,.045,z+h/2),(.18,.22,h+.32),(u,n,UP))
    for zz in (z-.15,z+h+.12):f.box(pos(x,.08,zz),(w+.52,.32,.22),(u,n,UP))
    if pediment:
        f.arch_ring(pos(x,.13,0),u,n,w*.58,z+h+.32,.14,.11,20)
        f.box(pos(x,.20,z+h+.34),(w*1.44,.32,.13),(u,n,UP))
    else:
        f.box(pos(x,.11,z+h+.40),(w+.62,.36,.13),(u,n,UP))

# Carroceria arquitetônica: perímetro OSM herdado, paredes vazadas e piso/cobertura.
body=Geometry();cornice=buf('Cornijas contínuas e frisos',ivory);basegeom=buf('Embasamento e juntas horizontais',stone)
front_windows=[];side_windows=[];height=14.3
for i,p in enumerate(local):
    q=local[(i+1)%len(local)];u=(q-p).normalized();n=Vector((-u.y,u.x,0));L=(q-p).length
    # Plan clockwise: normal à esquerda aponta para fora.
    holes=[];is_front=i==1;is_seaside=i==0;is_far_side=i==2
    if is_front:
        positions=[W/2+s*(5.7+(k+.5)*(W/2-5.7)/4) for s in (-1,1) for k in range(4)]
        holes=[(x-.77,x+.77,z,z+h) for x in positions for z,h in ((1.25,4.05),(8.0,4.1))]
        # Pavilhão central elevado tem sua própria parede; abertura real no corpo.
        holes.append((W/2-5.6,W/2+5.6,0,height))
    elif is_seaside or is_far_side:
        count=11 if is_seaside else 14;positions=[(k+.5)*L/count for k in range(count)]
        holes=[(x-.70,x+.70,z,z+h) for x in positions for z,h in ((1.25,4.05),(8.0,4.1))]
    else:positions=[]
    body.panel(p,u,n,0,L,0,height,.46,holes)
    for z,sx,sz in ((.20,.65,.40),(6.1,.58,.22),(6.4,.56,.22),(13.20,.70,.25),(13.65,.82,.34),(14.13,.96,.32),(14.45,.70,.34)):
        cornice.box(p+u*L/2+n*.12+UP*z,(L,sx,sz),(u,n,UP))
    for z in (1.,2.2,3.4,4.6,5.8,7.2,8.4,9.6,10.8,12.):
        buf('Juntas do reboco',ivory).box(p+u*L/2+n*.015+UP*z,(L,.024,.026),(u,n,UP))
    for x in positions:
        for z,h in ((1.25,4.05),(8.,4.1)):facade_window(p,u,n,x,1.54 if is_front else 1.4,z,h,z>7)
        f=buf('Pilastras das alas',ivory);pitch=L/(4 if is_front else len(positions))
        f.box(p+u*(x+.99)+n*.065+UP*7.0,(.18,.20,13.1),(u,n,UP))
        for z in (6.0,12.9):f.box(p+u*(x+.99)+n*.12+UP*z,(.40,.30,.22),(u,n,UP))
# Fundo/piso e laje superior seguem a mesma planta côncava.
for tri in tessellate_polygon([local]):
    tri=[local[v] if isinstance(v,int) else v for v in tri]
    body.poly([Vector((v.x,v.y,.05)) for v in reversed(tri)])
    body.poly([Vector((v.x,v.y,14.30)) for v in tri])
# Mantém nome/objeto da planta para dependências; mesh antiga preservada no datablock.
temp=body.object('RIO R34 | paredes do footprint',col,cream,T)
old.data=temp.data;old.data.transform(old.matrix_world.inverted()@T);bpy.data.objects.remove(temp,do_unlink=True)
for k,v in props.items():old[k]=v
old['source_footprint_object']='RIO BRANCO | corpo footprint 402383814';old['footprint_xy_preserved']=True
created.append(old.name)

# Pavilhão frontal: três portas, três vãos de sacada e grande janela semicircular.
front=buf('Pavilhão central vazado',cream);front.panel((0,.18,0),(1,0,0),(0,1,0),-5.6,5.6,0,13.3,.62,[(-4.1,-2.2,.82,5.95),(-.97,.97,.82,5.95),(2.2,4.1,.82,5.95),(-4.1,-2.2,7.3,12.9),(-.97,.97,7.3,12.9),(2.2,4.1,7.3,12.9)])
front.panel((0,.18,0),(1,0,0),(0,1,0),-5.6,-4.3,13.3,20.05,.62)
front.panel((0,.18,0),(1,0,0),(0,1,0),4.3,5.6,13.3,20.05,.62)
front.arch((0,.18,0),(1,0,0),(0,1,0),8.6,14.35,13.3,20.05,.62,40)
for x in (-5.6,5.6):front.box((x,-4.0,10.025),(.5,8.35,20.05))
front.box((0,-8.15,10.025),(11.2,.5,20.05))
front.box((0,-4.0,20.0),(11.2,8.8,.22))
for x in (-3.15,0,3.15):
    # Portas reais de madeira, sem inventar interior atrás delas.
    box('Portas principais',(x,-.05,3.38),(1.85,.14,5.10),dark)
    for sx in (-.56,.56):
        for z in (2.,4.5):box('Entalhes das portas',(x+sx,.035,z),(.59,.09,1.65),dark)
    for z in (.9,5.45):box('Bandeiras e soleiras',(x,.06,z),(1.98,.2,.20),ivory)
    facade_window((0,.18,0),(1,0,0),(0,1,0),x,1.90,7.3,5.60,False)
    box('Sacada principal laje',(x,1.15,7.18),(2.65,2.0,.30),ivory)
for x in (-4.95,4.95):column((x,.55,.82),.34,12.30,'Colunas monumentais')
for x in (-1.55,1.55):
    box('Pilastras centrais caneladas',(x,.40,10.2),(.27,.36,5.8),ivory)
    for k in range(3):box('Caneluras pilastras',(x-.08+k*.08,.60,10.0),(.023,.024,5.2),cream)
archglass=buf('Vidro grande arco central',glass)
outline=[(-4.3,.01,13.3),(4.3,.01,13.3)]+[(4.3*math.cos(j*math.pi/40),.01,14.35+4.3*math.sin(j*math.pi/40)) for j in range(41)]
archglass.poly(outline)
for x in (-3,-1.5,0,1.5,3):
    top=14.35+math.sqrt(4.3**2-x*x);line('Caixilho grande arco',(x,.075,13.3),(x,.075,top),.038,metal)
for z in (13.65,14.45,15.7,17.1):
    w=4.3 if z<14.35 else math.sqrt(4.3**2-(z-14.35)**2);line('Caixilho grande arco',(-w,.075,z),(w,.075,z),.039,metal)
for r,t,d in ((4.33,.15,.13),(4.60,.19,.15),(4.94,.14,.16)):buf('Arquivoltas do pavilhão',ivory).arch_ring((0,.22,0),(1,0,0),(0,1,0),r,14.35,t,d,48)
for z,w,depth,h in ((6.35,11.8,.80,.30),(6.70,12.0,.9,.25),(13.18,11.5,.70,.22),(19.7,12.1,.85,.25),(20.15,12.8,1.0,.36),(20.58,13.3,1.15,.34)):
    box('Entablamento central',(0,.27,z),(w,depth,h),ivory)
for i in range(19):box('Dentículos centrais',(-5.8+i*.645,.76,20.36),(.30,.36,.25),ivory)

def balustrade(p,q,z,label='Balaustradas do palácio'):
    p,q=Vector(p),Vector(q);u=(q-p).normalized();L=(q-p).length;n=Vector((-u.y,u.x,0))
    g=buf(label,ivory)
    for zz,h,w in ((z,.14,.22),(z+.95,.14,.30)):g.box((p+q)/2+UP*zz,(L,w,h),(u,n,UP))
    for i in range(max(2,round(L/.36))+1):
        c=p+(q-p)*i/max(2,round(L/.36));g.lathe((c.x,c.y,z+.06),[(.065,0),(.065,.10),(.045,.15),(.075,.3),(.087,.43),(.044,.56),(.052,.77),(.065,.82)],10)
balustrade((-4.35,2.08,0),(4.35,2.08,0),7.38)
for x in (-4.35,4.35):balustrade((x,.45,0),(x,2.08,0),7.38)
# Escadaria frontal com elevação coerente, do piso legado à soleira.
for i in range(6):box('Escadaria principal',(0,1.4+(5-i)*.30,.07*(i+1)),(8.8,2.65-i*.30,.14*(i+1)),stone)

# Cobertura das alas e pavilhão: telhado baixo visível nas oblíquas.
# Faixa seaward longitudinal dentro do footprint; demais coberturas sem fundo inventado.
for p,q in ((local[0],local[1]),(local[2],local[3])):
    u=(q-p).normalized();n=Vector((-u.y,u.x,0));L=(q-p).length
    g=buf('Telhados baixos das alas',roof)
    g.poly([p+UP*14.4,q+UP*14.4,q-n*4.5+UP*15.65,p-n*4.5+UP*15.65])
    g.poly([p-n*4.5+UP*15.65,q-n*4.5+UP*15.65,q-n*9+UP*14.4,p-n*9+UP*14.4])
    for k in range(round(L/.30)):
        x=(k+.5)*.30;line('Ritmo de telhas',p+u*x+UP*14.42,p+u*x-n*4.5+UP*15.67,.025,roof,6)
        line('Ritmo de telhas',p+u*x-n*4.5+UP*15.67,p+u*x-n*9+UP*14.42,.025,roof,6)
    line('Cumeeiras',p-n*4.5+UP*15.65,q-n*4.5+UP*15.65,.10,roof,12)

# Cúpula apoiada no pavilhão: octógono/tambor, perfil curvo, nervuras e lanternim.
dc=(0,-4.65,0);g=buf('Tambor octogonal',ivory)
g.lathe(dc,[(4.85,20.05),(5.12,20.65),(5.12,20.90),(4.62,21.08),(4.62,22.03),(4.96,22.23),(4.96,22.43)],8)
g=buf('Cúpula curvada',dome)
profile=[(4.90,22.42),(4.85,22.70),(4.69,23.12),(4.44,23.58),(4.04,24.15),(3.55,24.75),(2.98,25.31),(2.30,25.84),(1.76,26.25),(1.25,26.61)]
g.lathe(dc,profile,64)
for j in range(12):
    t=j*2*math.pi/12
    for (r,z),(r2,z2) in zip(profile,profile[1:]):line('Nervuras da cúpula',(r*math.cos(t),dc[1]+r*math.sin(t),z),(r2*math.cos(t),dc[1]+r2*math.sin(t),z2),.045,ivory)
    # Lucarnas: moldura curva, vidro e separações; forma candidata, não escultura copiada.
    u=Vector((-math.sin(t),math.cos(t),0));n=Vector((math.cos(t),math.sin(t),0));p=Vector((n.x*4.84,dc[1]+n.y*4.84,22.7))
    buf('Lucarnas e óculos',ivory).arch_ring(p,u,n,.54,0,.14,.11,24)
    v=buf('Vidros lucarnas',glass);v.poly([p-u*.54-UP*.40,p+u*.54-UP*.40]+[p+u*(.54*math.cos(k*math.pi/24))+UP*(.54*math.sin(k*math.pi/24)) for k in range(25)])
    line('Caixilhos lucarnas',p-UP*.36,p+UP*.51,.025,metal)
    for s in (-1,1):line('Lucarnas e óculos',p+u*(s*.63)-UP*.40,p+u*(s*.63)+UP*.03,.065,ivory)
g=buf('Lanternim e remate',ivory);g.lathe(dc,[(1.22,26.55),(1.30,26.78),(1.12,26.93),(1.00,27.0),(1.00,27.60),(1.21,27.73),(1.21,27.88),(.89,28.0),(.71,28.3),(.12,28.7)],24)
for j in range(8):
    t=j*math.pi/4;line('Guarda do lanternim',(1.27*math.cos(t),dc[1]+1.27*math.sin(t),27.9),(1.27*math.cos(t),dc[1]+1.27*math.sin(t),28.55),.024,metal)
g=buf('Aros do lanternim',metal);g.lathe(dc,[(1.29,28.49),(1.29,28.54)],48)
line('Haste superior',(0,dc[1],28.65),(0,dc[1],30.2),.028,metal)

# Portico lateral voltado para o barranco: sacada curva e pilares sob a laje.
# Localização proporcional na parede marítima existente, sem transladar o edifício.
p,q=local[0],local[1];su=(q-p).normalized();sn=Vector((-su.y,su.x,0));sc=p+(q-p)*.50
terrace=buf('Pórtico lateral e sacada curva',ivory)
outline=[sc-su*6.2,sc+su*6.2]+[sc+su*(6.2*math.cos(t))+sn*(3.6*math.sin(t)) for t in [i*math.pi/32 for i in range(33)]]
for z in (0.7,6.3):
    terrace.poly([v+UP*z for v in outline]);terrace.poly([v+UP*(z-.3) for v in reversed(outline)])
    for a,b in zip(outline,outline[1:]+outline[:1]):terrace.poly([a+UP*(z-.3),b+UP*(z-.3),b+UP*z,a+UP*z])
for x in (-5.,-1.8,1.8,5.):
    pos=sc+su*x+sn*2.7;column((pos.x,pos.y,.7),.23,5.3,'Colunas pórtico lateral')
for a,b in zip(outline[2:],outline[3:]):balustrade(a,b,6.55,'Balaustrada sacada lateral')

# Frontões circulares observados nas alas; esculturas ilegíveis ficam pendentes.
for x in (-13.3,-7.4,7.4,13.3):
    g=buf('Frontões e medalhões circulares',ivory)
    g.arch_ring((x,.1,0),(1,0,0),(0,1,0),.70,14.65,.15,.19,28)
    box('Frontões e medalhões circulares',(x,.13,14.68),(1.95,.55,.26),ivory)
    # Medalhão frontal em rotação vertical.
    for j in range(40):
        t=j*math.pi/20;t2=(j+1)*math.pi/20;line('Frontões e medalhões circulares',(x+.41*math.cos(t),.40,14.9+.41*math.sin(t)),(x+.41*math.cos(t2),.40,14.9+.41*math.sin(t2)),.07,ivory)

for name,g in buffers.items():
    o=g.object('RIO R34 | '+name,col,mats[name],T,bevel=.006 if name in ('Cornijas contínuas e frisos','Embasamento e juntas horizontais') else 0,props=props);created.append(o.name)
archive=bpy.data.collections.new('REFERENCE | Palácio esboço anterior R34');scene.collection.children.link(archive);archive.hide_render=True;archive.hide_viewport=True;archive['boas_role']='reference_only'
for o in list(scene.objects):
    if o.name.startswith('RIO BRANCO |') and o!=old:
        # Não altera praça, poste ou Câmara; histórico mantido e reversível.
        archive.objects.link(o)
        for c in list(o.users_collection):
            if c!=archive:c.objects.unlink(o)
        o.hide_set(True);o.hide_render=True;o['boas_archive_reason']='Esboço do palácio substituído por arquitetura fotográfica R34; preservado sem apagar.';archived.append(o.name)
bpy.context.view_layer.update()
assert all(signature(scene.objects[n])==sig for n,sig in protected.items()),'Fora do escopo mudou'
report={'schema':'boas/architectural-pass-v1','revision':'R30B.34','source_before':before,'source_after':None,'scene':scene.name,'status':'modeling_candidate','runtime_promoted':False,'reference_media_ids':json.loads((root/'artifacts/palacio-rio-branco/reference_pass.json').read_text())['media_ids'],'created_objects':created,'archived_objects':archived,'protected_signatures':protected,'palace':{'object':old.name,'osm_way_id':'402383814','binding_status':'candidate','footprint_before_world':[[p.x,p.y] for p in plan],'base_z_preserved_m':zbase,'frame_world':[list(r) for r in T],'front_width_from_existing_footprint_m':W,'front_edge_indices':[1,2],'facade_height_candidate_m':height,'height_verified_m':None,'dome_center_change_reason':'Cúpula antiga deslocada do pavilhão; fotos frontais/oblíquas mostram apoio no pavilhão central. Ajuste arquitetônico local dentro da planta, sem mudança XY da implantação.','body_before':old_signature},'changes':['Paredes vazadas nas alas e pavilhão, caixilhos/vidros, três portas, escadaria frontal, pilastras, cornijas, arquivoltas, sacadas e pórtico lateral.','Cúpula curva apoiada, nervuras, lucarnas, tambor octogonal e lanternim. Materiais autorais procedurais; nenhuma foto usada como textura.'],'limitations':['Esculturas figurativas, esculturas de águias e relevos finos sem leitura suficiente: pendentes.','Fundos e interiores não documentados: não reproduzidos.','Profundidade das sacadas, altura e perfil da cúpula são proporcionais às fotos, não medidos.','Galerias e barranco entram no refinamento seguinte da mesma revisão.'],'visual_review':'pending'}
out=root/'docs/reports/blender/palacio_rio_branco_r30b34.json';out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
dest=root/'blender/salvador_lacerda_r30b34_palacio_galerias.blend';assert not dest.exists(),'Revisão existente; não sobrescrever outra cena'
scene['architecture_revision']='R30B.34 | Palácio Rio Branco e galerias | modelagem candidata'
bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
report['source_after']={'file':dest.relative_to(root).as_posix(),'sha256':hashlib.file_digest(dest.open('rb'),'sha256').hexdigest(),'revision':'R30B.34','scene':scene.name}
out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'saved':report['source_after'],'components':len(created),'preserved_components':len(protected),'archived':len(archived),'review':'pending'},ensure_ascii=False))
