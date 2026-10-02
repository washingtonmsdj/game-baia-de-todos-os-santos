"""Fecha empenas e estrutura da praça sobre os arcos; acabamento visível."""
import bpy,json,math,runpy,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
root=Path(__file__).resolve().parents[2];scene=bpy.context.scene;p=root/'docs/reports/blender/palacio_rio_branco_r30b34.json';r=json.loads(p.read_text(encoding='utf8'))
assert not r.get('finish_components'),'Acabamento já aplicado'
G=runpy.run_path(str(root/'automation/blender/architectural_mesh.py'))['Geometry'];signature=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'))['signature'];T=Matrix(r['palace']['frame_world']);I=T.inverted();up=Vector((0,0,1))
col=bpy.data.collections['HERO | Palácio Rio Branco | fotografia R34'];cream=bpy.data.materials['RIO R34 | reboco bege claro'];ivory=bpy.data.materials['RIO R34 | ornatos e cornijas marfim']
props={'boas_revision':'R30B.34','boas_location_candidate':'palacio-rio-branco','boas_role':'visual_architecture','reference_status':'partial','classification':'ADAPT_LOCAL','dimensions_status':'acabamento proporcional à fotografia; detalhes esculpidos menores pendentes'}
created=[];g=G();plan=[I@Vector((x,y,r['palace']['base_z_preserved_m'])) for x,y in r['palace']['footprint_before_world']]
for a,b in ((plan[0],plan[1]),(plan[2],plan[3])):
    u=(b-a).normalized();n=Vector((-u.y,u.x,0))
    for v in (a,b):g.poly([v+up*14.35,v-n*9+up*14.35,v-n*4.5+up*15.65])
o=g.object('RIO R34 | Empenas fechadas das alas',col,cream,T,props=props);created.append(o.name)
g=G()
# Relevos geométricos visíveis: cantos, flores de moldura e volutas; sem figuras.
for corner in (plan[1],plan[2]):
    x,y=corner.x,corner.y
    for j in range(12):
        z=.7+j*1.05;g.box((x,y+.045,z),(.65,.24,.10))
        g.box((x,y-.29,z),(.20,.78,.10))
for side in (-1,1):
    for x,z,scale in ((4.65,14.12,.58),(4.63,18.62,.42),(5.05,19.52,.24)):
        cx=side*x
        for j in range(48):
            t=j*math.pi/24;t2=(j+1)*math.pi/24;rr=scale*(1-j/58);rr2=scale*(1-(j+1)/58)
            g.bar((cx+side*rr*math.cos(t),.43,z+rr*math.sin(t)),(cx+side*rr2*math.cos(t2),.43,z+rr2*math.sin(t2)),.042,8)
    for z in (1.3,6.5,13.55):
        cx=side*4.95
        for k in range(8):
            t=k*math.pi/4;g.bar((cx,.76,z),(cx+.18*math.cos(t),.75,z+.18*math.sin(t)),.045,8)
    g.box((side*1.55,.59,12.9),(.49,.28,.32))
# Chave do arco / óvalos geométricos conforme leitura das vistas próximas.
g.box((0,.57,18.8),(.38,.42,.78));g.box((0,.65,19.22),(.56,.38,.18))
for k in range(12):
    t=k*math.pi/6;g.bar((.30*math.cos(t),.73,19.25+.17*math.sin(t)),(.30*math.cos(t+.12),.73,19.25+.17*math.sin(t+.12)),.032,8)
o=g.object('RIO R34 | Cantaria volutas e chaves',col,ivory,T,props=props);created.append(o.name)

# A praça permanece na cota prévia sobre uma laje, mesmo com nichos abaixo.
gallery_col=bpy.data.collections['ENVIRONMENT_FINAL | Galerias Cidade Alta R34'];cname='COLLISION | Galerias Cidade Alta R34'
assert not bpy.data.collections.get(cname)
collision=bpy.data.collections.new(cname);scene.collection.children.link(collision);collision['boas_role']='collision';collision.hide_render=True;collision.hide_viewport=True
sections=json.loads((root/'artifacts/palacio-rio-branco/gallery_ground.json').read_text(encoding='utf8'))['ground'];slabs=[]
for s,ground in zip(r['galleries']['segments'],sections):
    p0=Vector(s['origin_world']);u=Vector(s['along_world']);n=Vector(s['outward_world']);L=s['length_from_existing_controls_m'];bottom=p0.z+s['height_candidate_m']
    samples=[sec['samples'][0][1][2] for sec in ground['sections']];top=sum(samples)/len(samples)
    assert bottom<top<bottom+.3,'Cota superior deve vir das amostras anteriores, não de offset arbitrário'
    g=G();g.box(p0+u*L/2-n*.65+up*((bottom+top)/2-p0.z),(L,1.3,top-bottom),(u,n,up))
    pr={'boas_revision':'R30B.34','boas_location_candidate':'praca-tome-de-sousa','boas_role':'visual_structure','classification':'ADAPT_LOCAL','reference_status':'partial','top_z_from_previous_ground_m':top,'base_z_from_existing_caps_m':bottom,'depth_candidate_m':1.3,'reason':'Laje da praça sobre galerias, necessária para separar piso superior e nichos; apoiada na alvenaria e mesma cota da superfície anterior.'}
    o=g.object('GAL R34 | '+s['name']+' | Laje de apoio da praça',gallery_col,bpy.data.materials['GAL R34 | argamassa e guarda-corpo claro'],props=pr);r['galleries']['created_objects'].append(o.name)
    co=bpy.data.objects.new('COLLISION R34 | '+s['name']+' | Laje superior',o.data.copy());collision.objects.link(co);co['boas_role']='static_collider';co['source_visual_object']=o.name;co['boas_revision']='R30B.34';co.hide_render=True;co.hide_set(True);created.append(co.name)
    slabs.append({'visual':o.name,'collider':co.name,'top_from_previous_ground_m':top,'thickness_derived_m':top-bottom,'depth_candidate_m':1.3})
r['finish_components']=created;r['created_objects'].extend(n for n in created if not n.startswith('COLLISION'))
r['galleries']['support_slabs']=slabs;r['retaining_profile_refinement']['top_plaza_changed']=False
r['retaining_profile_refinement']['top_plaza_support']='Galerias têm laje e proxy próprios, mesma cota superior amostrada antes da escavação. A altura do chão da praça foi decomposta entre estrutura e barranco, sem reescala global.'
r['changes'].append('Empenas fechadas, cantaria/volutas e lajes reais sob a borda da praça, com proxies simples separados.')
bpy.context.view_layer.update()
assert all(signature(scene.objects[n])==sig for n,sig in r['protected_signatures'].items() if n not in [x['object'] for x in r['retaining_profile_refinement']['geometry']]),'Alteração fora do escopo'
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True);r['source_after']['sha256']=hashlib.file_digest(Path(bpy.data.filepath).open('rb'),'sha256').hexdigest()
(root/'docs/reports/blender/palacio_rio_branco_r30b34.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'finish_components':len(created),'support_slabs':slabs,'source_after':r['source_after']},ensure_ascii=False))
