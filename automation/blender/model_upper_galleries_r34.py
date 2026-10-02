"""Galerias sob capeamentos existentes e leitura material localizada da encosta.

Não prolonga limites, vias ou escarpa por uma largura inventada. Extensão das
galerias ainda parcial; três arcos ao lado do palácio e trecho oposto legível.
"""
import bpy,json,runpy,math,hashlib
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2];scene=bpy.context.scene
report_path=root/'docs/reports/blender/palacio_rio_branco_r30b34.json';r=json.loads(report_path.read_text(encoding='utf8'))
assert 'galleries' not in r,'Galerias já aplicadas; não repetir'
assert bpy.data.collections.get('ENVIRONMENT_FINAL | Galerias Cidade Alta R34') is None
G=runpy.run_path(str(root/'automation/blender/architectural_mesh.py'))['Geometry'];signature=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'))['signature']
col=bpy.data.collections.new('ENVIRONMENT_FINAL | Galerias Cidade Alta R34');scene.collection.children.link(col)
col['boas_role']='visual_architecture';col['boas_location_candidate']='praca-tome-de-sousa'
created=[];caps=[];rows=[];up=Vector((0,0,1));buffers={};mats={}
def mat(name,color,rough=.8,noise=None):
    m=bpy.data.materials.new('GAL R34 | '+name);m.diffuse_color=(*color,1);m.use_nodes=True
    nt=m.node_tree;p=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=m.diffuse_color;p.inputs['Roughness'].default_value=rough
    if noise:
        n=nt.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=noise;n.inputs['Detail'].default_value=4
        colorramp=nt.nodes.new('ShaderNodeValToRGB');colorramp.color_ramp.elements[0].color=(*(v*.45 for v in color),1);colorramp.color_ramp.elements[1].color=(*(min(.95,v*1.4) for v in color),1)
        nt.links.new(n.outputs['Fac'],colorramp.inputs[0]);nt.links.new(colorramp.outputs[0],p.inputs['Base Color'])
        b=nt.nodes.new('ShaderNodeBump');b.inputs['Strength'].default_value=.33;b.inputs['Distance'].default_value=.07;nt.links.new(n.outputs['Fac'],b.inputs['Height']);nt.links.new(b.outputs['Normal'],p.inputs['Normal'])
    return m
stone=mat('alvenaria mista de pedra',(.29,.25,.19),noise=3.2);brick=mat('tijolo exposto dos arcos',(.44,.23,.15),noise=22);white=mat('argamassa e guarda-corpo claro',(.79,.79,.70),noise=85)
iron=mat('grade de ferro escuro',(.06,.072,.061),.44);shadow=mat('interior dos vãos',(.08,.075,.06));frame=mat('esquadrias claras das galerias',(.65,.68,.63),.57);glass=mat('vidros em sombra',(.12,.18,.18),.35)
def buf(name,material):
    if name not in buffers:buffers[name]=G();mats[name]=material
    return buffers[name]
def segment(prefix,control_names,count,height,width_ratio,spring):
    controls=[scene.objects[n] for n in control_names];caps.extend(control_names)
    # Extrai a aresta marítima das peças do capeamento B23, não desloca geografia.
    pts=[]
    for o in controls:pts.extend(o.matrix_world@v.co for v in o.data.vertices)
    ctrs=[sum((o.matrix_world@v.co for v in o.data.vertices),Vector())/len(o.data.vertices) for o in controls]
    u=(ctrs[-1]-ctrs[0]);u.z=0;u.normalize();n=Vector((-u.y,u.x,0))
    s0=min(p.dot(u) for p in pts);s1=max(p.dot(u) for p in pts);face=max(p.dot(n) for p in pts);top=min(p.z for p in pts)
    p=u*s0+n*face+up*(top-height);L=s1-s0;pitch=L/count;ww=pitch*width_ratio;rad=ww/2
    wall=buf(prefix+' | alvenaria vazada',stone);head=buf(prefix+' | intradorsos e aduelas',brick)
    rail=buf(prefix+' | balaustrada da praça',white);interior=buf(prefix+' | nichos internos',stone);grille=buf(prefix+' | grades',iron);casement=buf(prefix+' | caixilhos',frame);glazing=buf(prefix+' | vidros',glass)
    for j in range(count):
        x=(j+.5)*pitch;left=x-ww/2;right=x+ww/2
        wall.panel(p,u,n,j*pitch,left,0,height,1.3)
        wall.panel(p,u,n,right,(j+1)*pitch,0,height,1.3)
        wall.arch(p+u*x,u,n,ww,spring,0,height,1.3,32)
        head.arch_ring(p+u*x,u,n,rad,spring,.20,.07,32)
        # Adaelas segmentadas: juntas discretas sobre o arco, forma observada.
        for k in range(18):
            t=k*math.pi/17;a=p+u*(x-rad*math.cos(t))+up*(spring+rad*math.sin(t))+n*.082;b=p+u*(x-(rad+.2)*math.cos(t))+up*(spring+(rad+.2)*math.sin(t))+n*.082
            buf(prefix+' | juntas das aduelas',shadow).bar(a,b,.014,6)
        # Cavidades finitas, laterais e teto de intradorso: não manchas no muro.
        back=p+u*x-n*1.27
        interior.box(back+up*(spring*.48),(ww, .10,spring*.96),(u,n,up))
        interior.box(p+u*x-n*.65-up*.08,(ww,1.30,.16),(u,n,up))
        if prefix=='Palácio':
            for k in range(max(3,round(ww/.17))+1):
                xx=left+.09+k*(ww-.18)/max(3,round(ww/.17));ztop=spring+math.sqrt(max(0,rad*rad-(xx-x)**2))
                grille.bar(p+u*xx-n*.15+up*.13,p+u*xx-n*.15+up*(ztop-.08),.018,6)
            for z in (.7,1.5,2.3):grille.bar(p+u*(left+.06)-n*.15+up*z,p+u*(right-.06)-n*.15+up*z,.025,8)
        else:
            # Alternância visível de portas/vidros; sem letreiros/uso comercial inventados.
            leaf_width=ww*.80;leaf_height=spring+.12
            for side in (-1,1):
                pp=p+u*(x+side*leaf_width/4)-n*.22+up*leaf_height/2
                glazing.box(pp,(leaf_width/2-.09,.03,leaf_height-.18),(u,n,up))
            for xx in (x-leaf_width/2,x,x+leaf_width/2):casement.box(p+u*xx-n*.17+up*leaf_height/2,(.08,.10,leaf_height),(u,n,up))
            for zz in (.12,leaf_height*.82,leaf_height):casement.box(p+u*x-n*.17+up*zz,(leaf_width,.11,.08),(u,n,up))
            if j in (count-1,count-2):
                # Últimos vãos têm fechamento parcial claro documentado na foto 9.
                for k in range(5):casement.box(p+u*(x-leaf_width/2+(k+.5)*leaf_width/5)-n*.06+up*.75,(leaf_width/5-.025,.10,1.4),(u,n,up))
    # Guarda-corpo sobre a própria parede, ligada ao capeamento no mesmo nível.
    for z,sz in ((height+.13,.24),(height+1.08,.18)):
        rail.box(p+u*L/2+up*z,(L,.38,sz),(u,n,up))
    for j in range(count*4+1):
        x=j*L/(count*4);q=p+u*x+up*(height+.25)
        rail.bar(q,q+up*.70,.068,10)
        # Moldura oval simplificada observável, não relevo figurativo inventado.
        if j<count*4:
            c=p+u*((j+.5)*L/(count*4))+up*(height+.58)
            for k in range(18):
                a=k*math.pi/9;b=(k+1)*math.pi/9
                rail.bar(c+u*(.22*math.cos(a))+up*(.30*math.sin(a)),c+u*(.22*math.cos(b))+up*(.30*math.sin(b)),.034,6)
    rows.append({'name':prefix,'control_objects':control_names,'origin_world':list(p),'along_world':list(u),'outward_world':list(n),'length_from_existing_controls_m':L,'top_z_preserved_m':top,'arch_count':count,'height_candidate_m':height,'arch_width_candidate_m':ww,'recess_candidate_m':1.3,'classification':'ADAPT_LOCAL','placement_status':'candidate_existing_plaza_controls','reference_measurements':None})
    return p,u,n,L,height
name='PRA\\u00c7A | capeamento conten\\u00e7\\u00e3o'
# Nomes históricos contém escape literal; resolve somente a sequência existente.
capnames=sorted([o.name for o in scene.objects if o.name.startswith('PRA') and 'capeamento' in o.name.lower()])
assert len(capnames)==16,'Revisar capeamentos antes de modelar; sem correspondência por nome similar'
left=segment('Palácio',capnames[:6],3,6.75,.73,2.8)
right=segment('Prefeitura',capnames[6:],10,7.0,.72,3.3)
props={'boas_revision':'R30B.34','boas_location_candidate':'praca-tome-de-sousa','boas_role':'visual_architecture','reference_status':'partial','classification':'ADAPT_LOCAL','dimensions_status':'arquitetura proporcional às fotos sobre controle existente; dimensões não medidas','reference_media_ids':json.dumps(r['reference_media_ids'])}
for name,g in buffers.items():
    if not g.v:continue
    o=g.object('GAL R34 | '+name,col,mats[name],props=props);created.append(o.name)
# Capeamentos antigos mantidos ocultos: substituídos pelo guarda-corpo, mesmo traçado.
archive=bpy.data.collections.new('REFERENCE | Capeamentos substituídos R34');scene.collection.children.link(archive);archive.hide_render=True;archive.hide_viewport=True
for name in caps:
    o=scene.objects[name];archive.objects.link(o)
    for c in list(o.users_collection):
        if c!=archive:c.objects.unlink(o)
    o.hide_set(True);o.hide_render=True;o['boas_archive_reason']='Capeamento e guarda-corpo ligados à galeria; mesmo alinhamento e cota preservados.'

# Encosta: somente material sobre faces íngremes do terreno visual existentes.
# Atributo de máscara deixa pistas, superfícies superiores e colisor intocados.
terrain=scene.objects['MVP | terreno corrigido | colisão estática'];terrain.data=terrain.data.copy();me=terrain.data
mask=me.attributes.new('boas_r34_barranco','FLOAT','POINT');weights=[]
for v in me.vertices:
    w=terrain.matrix_world@v.co;val=0.0
    for p,u,n,L,h in (left,right):
        d=w-p;x=d.dot(u);y=d.dot(n)
        if -3<x<L+3 and .1<y<20 and 22<w.z<69:
            val=max(val,max(0,1-max(0,y-7)/13))
    weights.append(val)
mask.data.foreach_set('value',weights)
updated=[]
for i,m in enumerate(list(me.materials)):
    if not m or not any(t in m.name.lower() for t in ('grama','veget','encosta','terreno')) or any(t in m.name.lower() for t in ('asfalto','pista','rua','ladeira','calç','praca','praça')):continue
    new=m.copy();new.name='GAL R34 | encosta localizada | '+m.name;new.use_nodes=True;nt=new.node_tree
    output=next(n for n in nt.nodes if n.type=='OUTPUT_MATERIAL');links=list(output.inputs['Surface'].links)
    if not links:continue
    old_shader=links[0].from_socket;nt.links.remove(links[0])
    clay=nt.nodes.new('ShaderNodeBsdfPrincipled');clay.inputs['Base Color'].default_value=(.25,.22,.14,1);clay.inputs['Roughness'].default_value=.98
    noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=1.6;noise.inputs['Detail'].default_value=5
    ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.15,.12,.085,1);ramp.color_ramp.elements[1].color=(.30,.35,.14,1)
    nt.links.new(noise.outputs['Fac'],ramp.inputs[0]);nt.links.new(ramp.outputs[0],clay.inputs['Base Color'])
    bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.22;bump.inputs['Distance'].default_value=.09;nt.links.new(noise.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],clay.inputs['Normal'])
    attr=nt.nodes.new('ShaderNodeAttribute');attr.attribute_name=mask.name
    geom=nt.nodes.new('ShaderNodeNewGeometry');sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(geom.outputs['Normal'],sep.inputs[0])
    steep=nt.nodes.new('ShaderNodeMath');steep.operation='LESS_THAN';steep.inputs[1].default_value=.72;nt.links.new(sep.outputs['Z'],steep.inputs[0])
    mult=nt.nodes.new('ShaderNodeMath');mult.operation='MULTIPLY';nt.links.new(attr.outputs['Fac'],mult.inputs[0]);nt.links.new(steep.outputs[0],mult.inputs[1])
    mix=nt.nodes.new('ShaderNodeMixShader');nt.links.new(mult.outputs[0],mix.inputs[0]);nt.links.new(old_shader,mix.inputs[1]);nt.links.new(clay.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],output.inputs['Surface'])
    me.materials[i]=new;updated.append(new.name)
terrain['r34_material_mask']='boas_r34_barranco: material em banda íngreme sob galerias; sem deslocar vértices, estrada ou colisor.'
assert all(signature(scene.objects[n])==sig for n,sig in r['protected_signatures'].items()),'Geometria, transforms ou materiais-base fora do escopo mudaram'
r['galleries']={'created_objects':created,'segments':rows,'archived_caps':caps,'extent_status':'partial_existing_controls','limits':'Não estender por adivinhação a fachada além dos controles. Perfil/depth dos nichos não levantado; associação de cada fechamento às fotos candidata.','terrain':{'vertices_moved':0,'collider_changed':False,'mask_vertices':sum(v>0 for v in weights),'material_graphs_copied':updated,'visual_only':True}}
r['limitations']=[x for x in r['limitations'] if 'refinamento seguinte' not in x]+['Galerias parciais, alinhadas aos capeamentos herdados; posição fina, largura e profundidade reais ainda não levantadas.','Galeria branca com colunas e escadaria da encosta: implantação específica ainda precisa de controle; não instanciada por aproximação.']
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
r['source_after']['sha256']=hashlib.file_digest(Path(bpy.data.filepath).open('rb'),'sha256').hexdigest()
report_path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'gallery_components':len(created),'arches':13,'terrain_vertices_moved':0,'masked_materials':len(updated),'source_after':r['source_after']},ensure_ascii=False))
