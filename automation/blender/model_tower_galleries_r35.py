"""Encaixe do apoio no saguão e galerias com abóbada/fundos reais."""
import bpy,json,math,hashlib,runpy
from pathlib import Path
from mathutils import Matrix,Vector

root=Path(__file__).resolve().parents[2];scene=bpy.context.scene
r34=json.loads((root/'docs/reports/blender/palacio_rio_branco_r30b34.json').read_text(encoding='utf8'))
assert Path(bpy.data.filepath).resolve()==(root/r34['source_after']['file']).resolve()
dest=root/'blender/salvador_lacerda_r30b35_torre_galerias.blend';assert not dest.exists()
G=runpy.run_path(str(root/'automation/blender/architectural_mesh.py'))['Geometry']
helper=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));sig=helper['signature'];wm=helper['world_matrix']
controls=json.loads((root/'artifacts/palacio-rio-branco/alignment_controls_r35.json').read_text(encoding='utf8'));R=Matrix(controls['rotation']);I=R.inverted();up=Vector((0,0,1))
def bounds(o):
    pts=[I@wm(o)@v.co for v in o.data.vertices]
    return [[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]
floor=next(o for o in scene.objects if o.name.startswith('SUPERIOR | piso sagu'))
back=scene.objects['EDIFICIO | parede posterior alta'];bb=bounds(back);fb=bounds(floor)
rear=bb[0][0];front=fb[0][1];cy=sum(fb[1])/2
names=['LAC R30B08 | apoio oposto | '+n for n in ('corpo estrutural afunilado','capitel sob passarela','ressalto transversal')]
gallery_names=[n for n in r34['galleries']['created_objects'] if any(k in n for k in ('alvenaria vazada','nichos internos','Laje de apoio'))]
slab_colliders=[s['collider'] for s in r34['galleries']['support_slabs']]
terrain_names=['MVP | terreno corrigido | colisão estática','R30A5 | COLLISION | terrain proxy']
editable=set(names+gallery_names+slab_colliders+terrain_names)
protected_names=set(r34['protected_signatures'])|set(r34['created_objects'])|set(r34['galleries']['created_objects'])
protected={n:sig(scene.objects[n]) for n in protected_names-editable}
before={n:sig(scene.objects[n]) for n in editable}
def replace(o,g):
    old=o.data;me=bpy.data.meshes.new(o.name+' | R35');me.from_pydata(g.v,[],g.f);me.update()
    for m in old.materials:me.materials.append(m)
    o.data=me;o['boas_revision']='R30B.35'
    if old.users==0:bpy.data.meshes.remove(old)

# A face marítima do apoio segue a parede posterior do edifício superior.
# O capitel sustenta a laje real do saguão, não um ponto escolhido no terreno.
body=scene.objects[names[0]];oldbb=bounds(body);oldwidth=oldbb[0][1]-oldbb[0][0]
g=G();rings=[]
for j in range(0,len(body.data.vertices),4):
    pts=[I@wm(body)@v.co for v in list(body.data.vertices)[j:j+4]]
    z=sum(p.z for p in pts)/4;width=max(p.x for p in pts)-min(p.x for p in pts)
    x0=rear;x1=rear+(front-rear)*width/oldwidth
    y0=cy-3.47;y1=cy+3.47
    if z>68:y0=cy-3.62;y1=cy+3.62
    rings.append([x0,x1,y0,y1,z])
    g.v.extend(tuple(R@Vector(p)) for p in ((x0,y0,z),(x1,y0,z),(x1,y1,z),(x0,y1,z)))
g.f=[(3,2,1,0)]
for j in range(len(rings)-1):
    a=j*4;b=a+4;g.f.extend((a+i,a+(i+1)%4,b+(i+1)%4,b+i) for i in range(4))
g.f.append(tuple(range((len(rings)-1)*4,len(rings)*4)));replace(body,g)
for name,z0,z1,dy in ((names[1],68.74,fb[2][0],7.45),(names[2],68.46,68.70,7.18)):
    g=G();g.box(R@Vector(((rear+front)/2,cy,(z0+z1)/2)),(front-rear,dy,z1-z0),(R@Vector((1,0,0)),R@Vector((0,1,0)),up));replace(scene.objects[name],g)
for name in names:
    o=scene.objects[name];o['r35_alignment_control']=back.name+' / '+floor.name
    o['r35_correction_reason']='Apoio anterior inteiramente fora do intervalo do saguão. Face alinhada à parede superior e capitel sob a laje; terreno será refeito ao redor.'
    o['classification']='ERROR';o['reference_status']='partial'

col=bpy.data.collections['ENVIRONMENT_FINAL | Galerias Cidade Alta R34'];collision=bpy.data.collections['COLLISION | Galerias Cidade Alta R34'];stone=bpy.data.materials['GAL R34 | alvenaria mista de pedra']
new=[];segments=[];depth=4.2
for s in r34['galleries']['segments']:
    p=Vector(s['origin_world']);u=Vector(s['along_world']);n=Vector(s['outward_world']);L=s['length_from_existing_controls_m'];h=s['height_candidate_m'];count=s['arch_count'];width=s['arch_width_candidate_m'];rad=width/2;spring=2.8 if s['name']=='Palácio' else 3.3;pitch=L/count
    wall=G();inside=G();vault=G()
    for j in range(count):
        x=(j+.5)*pitch;left=x-rad;right=x+rad
        wall.panel(p,u,n,j*pitch,left,0,h,depth);wall.panel(p,u,n,right,(j+1)*pitch,0,h,depth)
        wall.arch(p+u*x,u,n,width,spring,0,h,depth,32)
        inside.box(p+u*x-n*(depth-.08)+up*(spring+rad)/2,(width,.16,spring+rad),(u,n,up))
        inside.box(p+u*x-n*depth/2-up*.08,(width,depth,.16),(u,n,up))
        # Nervuras discretas de la abóbada, sem ramais internos inventados.
        for y in (.65,2.35,depth-.25):
            vault.arch_ring(p+u*x-n*y,u,n,rad-.04,spring,.055,.07,32)
    replace(scene.objects['GAL R34 | '+s['name']+' | alvenaria vazada'],wall)
    replace(scene.objects['GAL R34 | '+s['name']+' | nichos internos'],inside)
    props={'boas_revision':'R30B.35','boas_role':'visual_structure','boas_location_candidate':'praca-tome-de-sousa','reference_status':'partial','depth_candidate_m':depth,'depth_verified_m':None,'classification':'ADAPT_LOCAL'}
    o=vault.object('GAL R35 | '+s['name']+' | Nervuras internas',col,stone,props=props);new.append(o.name)
    slab=next(v for v in r34['galleries']['support_slabs'] if s['name'] in v['visual']);top=slab['top_from_previous_ground_m'];bottom=p.z+h
    g=G();g.box(p+u*L/2-n*depth/2+up*((bottom+top)/2-p.z),(L,depth,top-bottom),(u,n,up));replace(scene.objects[slab['visual']],g);replace(scene.objects[slab['collider']],g)
    # Proxies simples independentes da malha visual detalhada.
    g=G();g.box(p+u*L/2-n*depth/2-up*.08,(L,depth,.16),(u,n,up))
    o=g.object('COLLISION R35 | '+s['name']+' | Piso das galerias',collision,stone,props={'boas_role':'static_collider','boas_revision':'R30B.35','boas_location_candidate':'praca-tome-de-sousa'});o.hide_render=True;o.hide_set(True);new.append(o.name)
    segments.append({**s,'depth_candidate_m':depth,'depth_verified_m':None,'spring_candidate_m':spring,'floor_thickness_m':.16,'top_plaza_m':top})

# Os vãos envidraçados deixam ler o volume interno; não uma placa opaca.
glass=bpy.data.materials['GAL R34 | vidros em sombra'];bsdf=next(n for n in glass.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bsdf.inputs['Transmission Weight'].default_value=.88;bsdf.inputs['Roughness'].default_value=.13;bsdf.inputs['Alpha'].default_value=.40;glass.diffuse_color=(*glass.diffuse_color[:3],.40);glass.surface_render_method='DITHERED'
assert all(sig(scene.objects[n])==v for n,v in protected.items() if 'GAL R34 | Prefeitura | vidros'!=n),'Mudança fora do escopo'
scene['architecture_revision']='R30B.35 | Apoio alinhado e galerias em profundidade; terreno em correção'
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
with dest.open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
report={'schema':'boas/architectural-correction-v1','revision':'R30B.35','source_before':r34['source_after'],'source_after':{'file':dest.relative_to(root).as_posix(),'sha256':sha,'scene':scene.name,'revision':'R30B.35'},'reference_media_ids':r34['reference_media_ids'],'status':'modeling_candidate_terrain_pending','runtime_promoted':False,'protected_signatures':protected,'edited_before':before,'created_objects':new,'tower_alignment':{'objects':names,'rotation_world':[list(row) for row in R],'control_wall':back.name,'control_floor':floor.name,'sea_face_x_from_upper_wall_m':rear,'land_face_x_from_upper_floor_m':front,'center_y_from_upper_floor_m':cy,'cap_top_from_floor_bottom_m':fb[2][0],'old_body_bounds_local':oldbb,'rings_local':rings,'classification':'ERROR','real_dimensions_status':'Medidas do modelo existente, não levantamento da edificação real.'},'galleries':{'segments':segments,'changed_objects':gallery_names+slab_colliders,'depth_status':'Candidata: volume mínimo para leitura e continuidade espacial; profundidade real não levantada. Sem corredores/ramais extrapolados.'},'terrain_names':terrain_names,'terrain_stage':'pending','limitations':['Circulação/colliders novos ainda não aprovados para runtime.','Implantação fina das galerias e dimensões reais internas não levantadas.','Esculturas e outras estruturas pendentes de B34 continuam pendentes.']}
# Atualiza a evidência de transparência, que afeta somente o componente vidro.
if 'GAL R34 | Prefeitura | vidros' in report['protected_signatures']:report['protected_signatures']['GAL R34 | Prefeitura | vidros']=sig(scene.objects['GAL R34 | Prefeitura | vidros'])
out=root/'docs/reports/blender/torre_galerias_r30b35.json';out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'saved':report['source_after'],'tower_controls':(rear,front,fb[2][0]),'gallery_depth_candidate_m':depth},ensure_ascii=False))
