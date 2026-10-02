"""Refino fotográfico do Rio Branco/praça na revisão aberta, sem mudar implantação.

Relevos legíveis nas fotos; esculturas figurativas e fundos não documentados
permanecem pendentes. Medidas de ornatos são proporcionais, não levantadas.
"""
import bpy,json,math,runpy,hashlib
from pathlib import Path
from mathutils import Matrix,Vector
root=Path(__file__).resolve().parents[2];scene=bpy.context.scene
rp=root/'docs/reports/blender/torre_galerias_r30b35.json';r=json.loads(rp.read_text(encoding='utf8'))
r34=json.loads((root/'docs/reports/blender/palacio_rio_branco_r30b34.json').read_text(encoding='utf8'))
assert Path(bpy.data.filepath).resolve()==(root/r['source_after']['file']).resolve()
assert 'palace_facade_refinement' not in r,'Passe já aplicado'
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));sig,wm=h['signature'],h['world_matrix']
assert all(sig(scene.objects[n])==s for n,s in r['protected_signatures'].items())
G=runpy.run_path(str(root/'automation/blender/architectural_mesh.py'))['Geometry'];T=Matrix(r34['palace']['frame_world']);UP=Vector((0,0,1))
local=[T.inverted()@Vector((*p,70)) for p in r34['palace']['footprint_before_world']];W=r34['palace']['front_width_from_existing_footprint_m']
ivory=bpy.data.materials['RIO R34 | ornatos e cornijas marfim'];cream=bpy.data.materials['RIO R34 | reboco bege claro'];metal=bpy.data.materials['RIO R34 | grades e esquadrias']
col=bpy.data.collections.new('HERO | Palácio Rio Branco | relevos R35');scene.collection.children.link(col);col['boas_role']='visual_architecture'
refs=json.loads((root/'artifacts/palacio-rio-branco/reference_pass.json').read_text(encoding='utf8'))['media_ids']
props={'boas_revision':'R30B.35','boas_location_candidate':'palacio-rio-branco','osm_way_id':'402383814','boas_role':'visual_architecture','classification':'ADAPT_LOCAL','reference_status':'partial','reference_media_ids':json.dumps(refs),'dimensions_status':'proporções candidatas das fotos; dimensões reais não levantadas'}
buffers={};mats={};changed={};new=[]
def buf(name,mat=ivory):
    if name not in buffers:buffers[name]=G();mats[name]=mat
    return buffers[name]
def line(name,p,q,radius=.035,mat=ivory):buf(name,mat).bar(p,q,radius,8)
def path(name,points,radius=.035,mat=ivory):
    for a,b in zip(points,points[1:]):line(name,a,b,radius,mat)
def ellipse(name,p,u,n,rx,rz,tube=.035):
    p,u,n=Vector(p),Vector(u),Vector(n)
    path(name,[p+u*(rx*math.cos(i*math.tau/48))+UP*(rz*math.sin(i*math.tau/48)) for i in range(49)],tube)
def rosette(name,p,u,n,radius):
    p,u,n=Vector(p),Vector(u),Vector(n)
    ellipse(name,p,u,n,radius*.26,radius*.26,.045)
    for j in range(8):
        angle=j*math.tau/8;points=[]
        for k in range(17):
            t=k*math.tau/16;rr=radius*(.57+.31*math.cos(t));aa=angle+.19*math.sin(t)
            points.append(p+u*(rr*math.cos(aa))+UP*(rr*math.sin(aa))+n*(.018*math.sin(t)))
        path(name,points,.027)
def relief_leaf(name,p,u,n,size,flip=1):
    p,u,n=Vector(p),Vector(u),Vector(n)
    for side in (-1,1):
        path(name,[p+u*(flip*size*(t/20))+UP*(side*size*.20*math.sin(math.pi*t/20))+n*(.025*math.sin(math.pi*t/20)) for t in range(21)],.025)
    line(name,p,p+u*(flip*size),.025)
def replace(name,g):
    o=scene.objects[name];changed[name]={'before':sig(o),'reason':'Refino de ornatos visíveis nas fotos frontais/oblíquas; planta preservada.'}
    temp=g.object('TEMP | ornato',col,o.data.materials[0],T)
    old=o.data;o.data=temp.data;o.data.transform(wm(o).inverted()@T);bpy.data.objects.remove(temp,do_unlink=True)
    o['boas_revision']='R30B.35';o['reference_status']='partial'
    changed[name]['after']=sig(o)

# Molduras: alternância de frontões curvos e triangulares observável nas fotos.
# Refaz somente o componente de cantaria, mantendo vidro e abertura existentes.
trim=G()
for i in (0,1,2):
    p,q=local[i],local[(i+1)%len(local)];u=(q-p).normalized();n=Vector((-u.y,u.x,0));L=(q-p).length
    positions=sorted([W/2+s*(5.7+(k+.5)*(W/2-5.7)/4) for s in (-1,1) for k in range(4)]) if i==1 else [(k+.5)*L/(11 if i==0 else 14) for k in range(11 if i==0 else 14)]
    w=1.54 if i==1 else 1.4
    for j,x in enumerate(positions):
        def P(xx,yy,zz):return p+u*xx+n*yy+UP*zz
        for z,height in ((1.25,4.05),(8.,4.1)):
            for xx in (x-w/2-.12,x+w/2+.12):trim.box(P(xx,.045,z+height/2),(.18,.22,height+.32),(u,n,UP))
            for zz in (z-.15,z+height+.12):trim.box(P(x,.08,zz),(w+.52,.32,.22),(u,n,UP))
            trim.box(P(x,.11,z+height+.40),(w+.62,.36,.13),(u,n,UP))
            if z>7:
                if j%3==1:
                    path('Frontões triangulares',[P(x-w*.73,.24,12.52),P(x,.24,13.02),P(x+w*.73,.24,12.52)],.075)
                    buf('Tímpanos triangulares',cream).poly([P(x-w*.62,.10,12.55),P(x+w*.62,.10,12.55),P(x,.10,12.92)])
                    rosette('Rosetas dos tímpanos',P(x,.25,12.70),u,n,.17)
                else:
                    trim.arch_ring(P(x,.13,0),u,n,w*.58,12.42,.14,.11,24)
            if (i==1 and j in (1,2,5,6)) or (i==0 and j in (1,5,9)):
                if z<7:
                    for t in range(22):
                        a=math.pi*t/22;b=math.pi*(t+1)/22
                        line('Guirlandas sobre vãos',P(x+math.cos(a)*.78,.20,5.90+math.sin(a)*.36),P(x+math.cos(b)*.78,.20,5.90+math.sin(b)*.36),.055)
                    rosette('Fechos florais das janelas',P(x,.26,6.03),u,n,.18)
        # Pequenos consoles e dentículos, em ritmo vinculado aos vãos.
        for dx in (-w*.60,w*.60):
            b=buf('Consoles e dentículos das alas')
            b.box(P(x+dx,.16,13.20),(.17,.34,.36),(u,n,UP))
            b.box(P(x+dx,.23,13.34),(.23,.46,.12),(u,n,UP))
    for k in range(round(L/.46)):
        buf('Consoles e dentículos das alas').box(p+u*((k+.5)*L/round(L/.46))+n*.47+UP*13.93,(.18,.22,.18),(u,n,UP))
# Reincorpora molduras dos três vãos centrais na mesma peça.
for x in (-3.15,0,3.15):
    for xx in (x-1.07,x+1.07):trim.box((xx,.225,10.1),(.18,.22,5.92))
    for zz in (7.15,13.02):trim.box((x,.26,zz),(2.42,.32,.22))
    trim.box((x,.29,13.30),(2.52,.36,.13))
replace('RIO R34 | Molduras e peitoris',trim)

# Frontões de platibanda: corpos fechados, círculos concêntricos e volutas.
crest=G()
for x in (-16.0,-7.45,7.45,16.0):
    z=15.30
    crest.box((x,.12,14.86),(2.90,.52,.64))
    outline=[Vector((x-1.08,.22,14.6)),Vector((x+1.08,.22,14.6))]+[Vector((x+1.08*math.cos(j*math.pi/32),.22,z+1.08*math.sin(j*math.pi/32))) for j in range(33)]
    crest.poly(outline);crest.poly([p-Vector((0,.38,0)) for p in reversed(outline)])
    for a,b in zip(outline,outline[1:]+outline[:1]):crest.poly([a,b,b-Vector((0,.38,0)),a-Vector((0,.38,0))])
    # Base do medalhão opaca, diferente de um arco vazio sobre o telhado.
    crest.poly([(x+.88*math.cos(t*math.tau/48),.32,z+.88*math.sin(t*math.tau/48)) for t in range(48)])
    for radius in (.42,.69,.98):ellipse('Molduras dos medalhões',(x,.43,z),(1,0,0),(0,1,0),radius,radius,.065)
    for side in (-1,1):
        points=[]
        for k in range(49):
            a=k*math.tau*1.10/48;rr=.43*(1-k/60)
            points.append((x+side*(1.10+rr*math.cos(a)),.39,14.92+rr*math.sin(a)))
        path('Volutas dos frontões',points,.065)
    for k in range(9):
        a=math.pi*(k+.5)/9
        relief_leaf('Folhas dos frontões',(x+math.cos(a)*1.02,.43,z+math.sin(a)*1.02),(math.cos(a),0,math.sin(a)),(0,1,0),.26)
replace('RIO R34 | Frontões e medalhões circulares',crest)

# Relevos arquitetônicos do arco e pedestais, sem simular estátuas ilegíveis.
for j in range(21):
    a=(j+.5)*math.pi/21;p=Vector((4.77*math.cos(a),.47,14.35+4.77*math.sin(a)))
    rosette('Rosetas da arquivolta',p,(1,0,0),(0,1,0),.18)
for x in (-4.8,4.8):
    rosette('Rosetas dos cantos do pavilhão',(x,.40,19.13),(1,0,0),(0,1,0),.36)
    for z in (18.05,18.42):relief_leaf('Ramos dos cantos',(x,.40,z),(1,0,0),(0,1,0),.42,-1 if x>0 else 1)
    # Painel ornamental no embasamento lateral da entrada.
    b=buf('Painéis em relevo do portal')
    b.box((x,.43,3.24),(.86,.22,3.58))
    for xx in (x-.40,x+.40):b.box((xx,.57,3.24),(.07,.08,3.60))
    for z in (1.48,5.00):b.box((x,.57,z),(.86,.08,.10))
    ellipse('Cartelas dos pedestais',(x,.62,3.7),(1,0,0),(0,1,0),.29,.49,.042)
    rosette('Rosetas dos pedestais',(x,.65,4.62),(1,0,0),(0,1,0),.25)
for x in (-1.55,1.55):
    rosette('Capitéis das pilastras centrais',(x,.68,12.85),(1,0,0),(0,1,0),.22)
    for side in (-1,1):ellipse('Volutas dos capitéis',(x+side*.20,.67,12.78),(1,0,0),(0,1,0),.10,.10,.034)
for x in (-4.95,4.95):
    for k in range(9):
        a=math.pi*(k+.5)/9
        line('Caneluras das colunas superiores',(x+.315*math.cos(a),.55+.315*math.sin(a),7.45),(x+.284*math.cos(a),.55+.284*math.sin(a),12.38),.012,cream)
    for side in (-1,1):ellipse('Volutas dos capitéis',(x+side*.30,.82,12.75),(1,0,0),(0,1,0),.16,.13,.045)
# Ferros delgados e ferragens das três folhas de entrada, claramente separados.
for x in (-3.15,0,3.15):
    for dx in (-.20,.20):line('Puxadores do portal',(x+dx,.15,2.50),(x+dx,.15,2.96),.025,metal)

for name,g in buffers.items():
    if not g.v:continue
    o=g.object('RIO R35 | '+name,col,mats[name],T,props=props);new.append(o.name)

# Piso da praça: material em coordenadas métricas, sem deformação da malha.
plaza=scene.objects['PRAÇA | OSM 1263035782'];plaza_before=sig(plaza);old_mats=[m.name for m in plaza.data.materials]
if plaza.data.users>1:plaza.data=plaza.data.copy()
mat=bpy.data.materials.new('PRACA R35 | paralelepípedos métricos');mat.use_nodes=True;mat.diffuse_color=(.32,.34,.33,1)
nt=mat.node_tree;bs=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Base Color'].default_value=mat.diffuse_color;bs.inputs['Roughness'].default_value=.86
geo=nt.nodes.new('ShaderNodeNewGeometry');combine=nt.nodes.new('ShaderNodeCombineXYZ')
for socket,axis in [('X',T.col[0].xyz),('Y',T.col[1].xyz)]:
    dot=nt.nodes.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT';dot.inputs[1].default_value=axis;nt.links.new(geo.outputs['Position'],dot.inputs[0]);nt.links.new(dot.outputs['Value'],combine.inputs[socket])
brick=nt.nodes.new('ShaderNodeTexBrick');brick.offset=.5;brick.offset_frequency=2;brick.inputs['Scale'].default_value=1;brick.inputs['Brick Width'].default_value=.22;brick.inputs['Row Height'].default_value=.13
brick.inputs['Mortar Size'].default_value=.007;brick.inputs['Mortar Smooth'].default_value=.008
brick.inputs['Color1'].default_value=(.25,.28,.27,1);brick.inputs['Color2'].default_value=(.42,.43,.40,1);brick.inputs['Mortar'].default_value=(.075,.080,.075,1)
nt.links.new(combine.outputs[0],brick.inputs['Vector']);nt.links.new(brick.outputs['Color'],bs.inputs['Base Color'])
bump=nt.nodes.new('ShaderNodeBump');bump.invert=True;bump.inputs['Distance'].default_value=.008;bump.inputs['Strength'].default_value=.48;nt.links.new(brick.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
plaza.data.materials.clear();plaza.data.materials.append(mat);plaza['r35_pavement_status']='Padrão métrico candidato pela fotografia; não é medição do assentamento real';plaza['r35_pavement_geometry_unchanged']=True
assert sig(plaza)['geometry_sha256']==plaza_before['geometry_sha256'] and sig(plaza)['transform']==plaza_before['transform']

# Explicita a ampliação autorizada de escopo, conservando a prova anterior.
for name,item in changed.items():
    assert item['before']==r['protected_signatures'][name]
    del r['protected_signatures'][name]
assert all(sig(scene.objects[n])==s for n,s in r['protected_signatures'].items())
r['created_objects'].extend(new)
r['palace_facade_refinement']={'classification':'ADAPT_LOCAL','reference_media_ids':refs,'created_objects':new,'updated_existing_objects':changed,'footprint_and_base_preserved':sig(scene.objects[r34['palace']['object']])==r['protected_signatures'][r34['palace']['object']],'plaza':{'object':plaza.name,'before':plaza_before,'after':sig(plaza),'materials_before':old_mats,'brick_size_candidate_m':[.22,.13],'measured_real_size_m':None,'displacement':False},'limitations':['Esculturas figurativas e águias não reproduzidas sem referência legível suficiente.','Fachadas posteriores/interiores não documentados: preservados, fidelidade não atestada.','Relevos e proporções candidatas, não levantamento arquitetônico.'],'visual_review':'pending'}
r.pop('localized_scene_review',None)
scene['architecture_revision']='R30B.35 | apoio escalonado, galerias e fachadas | candidato'
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
with Path(bpy.data.filepath).open('rb') as f:r['source_after']['sha256']=hashlib.file_digest(f,'sha256').hexdigest()
rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'created':len(new),'updated':list(changed),'saved':r['source_after']},ensure_ascii=False))
