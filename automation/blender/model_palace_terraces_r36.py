"""Terraços/colunata do Rio Branco: passe de conjunto a partir das fotos do usuário.

Planta/ruas herdadas preservadas. Implantação relativa e dimensões candidatas;
não é levantamento e não cria ligação pública fictícia à ladeira.
"""
import bpy,bmesh,json,math,hashlib,runpy
import numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
root=Path(__file__).resolve().parents[2];scene=bpy.context.scene
catalog=json.loads((root/'world/areas/mvp-centro-lacerda/blender-revisions.json').read_text(encoding='utf8'));parent=catalog['authoring_source']
assert parent['revision']=='R30B.35' and Path(bpy.data.filepath).resolve()==(root/parent['file']).resolve()
dest=root/'blender/salvador_lacerda_r30b36_terracos_palacio.blend';assert not dest.exists()
c=json.loads((root/'artifacts/palacio-rio-branco/terrace_controls.json').read_text(encoding='utf8'));previous=json.loads((root/'docs/reports/blender/torre_galerias_r30b35.json').read_text(encoding='utf8'))
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));sig,wm=h['signature'],h['world_matrix'];G=runpy.run_path(str(root/'automation/blender/architectural_mesh.py'))['Geometry']
palace=json.loads((root/'docs/reports/blender/palacio_rio_branco_r30b34.json').read_text(encoding='utf8'))
protected={n:sig(scene.objects[n]) for n in set(previous['protected_signatures'])|set(previous['created_objects'])|set(previous['tower_alignment']['objects'])|set(palace['created_objects'])}
assert all(protected[n]==s for n,s in previous['protected_signatures'].items())
P=Vector(c['origin_world']);P.z=0;U=Vector(c['along_world']);N=Vector(c['outward_world']);UP=Vector((0,0,1));L=c['length_m']
S=Matrix(((U.x,N.x,0,P.x),(U.y,N.y,0,P.y),(0,0,1,0),(0,0,0,1)));SI=S.inverted()
x0,x1=.10*L,.90*L;front=33.;back=27.;center=L*.5
road=[next(v for v in row['samples'] if v['material'] and 'asfalto' in v['material']) for row in c['samples']]
floor=sum(v['z'] for v in road)/len(road)+6.8;roof=floor+5.25;levels=[69.8,69.8-(69.8-roof)/3,69.8-2*(69.8-roof)/3,roof]
col=bpy.data.collections.new('HERO | Terraços Rio Branco | fotografia R36');scene.collection.children.link(col);col['boas_role']='visual_architecture'
collision=bpy.data.collections.new('COLLISION | Terraços Rio Branco R36');scene.collection.children.link(collision);collision.hide_render=True;collision['boas_role']='static_collider'
ivory=bpy.data.materials['RIO R34 | ornatos e cornijas marfim'];stone=bpy.data.materials['RIO R34 | embasamento de pedra'];pavement=bpy.data.materials['PRACA R35 | paralelepípedos métricos']
def mat(name,color):
    m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1);bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Base Color'].default_value=m.diffuse_color;bs.inputs['Roughness'].default_value=.88
    geo=m.node_tree.nodes.new('ShaderNodeNewGeometry');noise=m.node_tree.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=24;m.node_tree.links.new(geo.outputs['Position'],noise.inputs['Vector']);b=m.node_tree.nodes.new('ShaderNodeBump');b.inputs['Strength'].default_value=.15;b.inputs['Distance'].default_value=.008;m.node_tree.links.new(noise.outputs['Fac'],b.inputs['Height']);m.node_tree.links.new(b.outputs['Normal'],bs.inputs['Normal']);return m
wallmat=mat('RIO R36 | cantaria dos terraços',(.32,.32,.27));soil=mat('RIO R36 | solo e vegetação baixa',(.17,.23,.09))
props={'boas_revision':'R30B.36','boas_location_candidate':'palacio-rio-branco','osm_way_id':'402383814','classification':'ADAPT_LOCAL','reference_status':'partial','dimensions_status':'candidate; proporções das fotos sem medição real','reference_media_ids':json.dumps(['palacio-rio-branco-oblique_right-47b57baa4f1a','palacio-rio-branco-right-5c2fa307341b']),'boas_role':'visual_architecture'}
buffers={};materials={};created=[]
def g(name,material=ivory):
    if name not in buffers:buffers[name]=G();materials[name]=material
    return buffers[name]
def railing(a,b,z,label='Balaustradas dos terraços'):
    a,b=Vector(a),Vector(b);d=(b-a).normalized();normal=Vector((-d.y,d.x,0));length=(b-a).length;geom=g(label)
    for zz,w,hh in ((z+.12,.24,.18),(z+1.04,.30,.15)):geom.box((a+b)/2+UP*zz,(length,w,hh),(d,normal,UP))
    count=max(2,round(length/.42))
    for j in range(count+1):
        v=a+(b-a)*j/count
        geom.lathe((v.x,v.y,z+.2),[(.07,0),(.07,.1),(.043,.2),(.078,.38),(.056,.54),(.045,.69),(.065,.77)],8)
    for v in (a,b):geom.box((v.x,v.y,z+.60),(.36,.36,1.20));geom.box((v.x,v.y,z+1.24),(.46,.46,.13))
def prism(geom,outline,bottom,top):
    geom.poly([(x,y,top) for x,y in outline]);geom.poly([(x,y,bottom) for x,y in reversed(outline)])
    for a,b in zip(outline,outline[1:]+outline[:1]):geom.poly([(*a,bottom),(*b,bottom),(*b,top),(*a,top)])
colliders=[]
def collider(name,geom):
    o=geom.object('COL R36 | '+name,collision,stone,S,props={'boas_revision':'R30B.36','boas_role':'static_collider','boas_location_candidate':'palacio-rio-branco','classification':'ADAPT_LOCAL'});o.display_type='WIRE';o.hide_render=True;o.hide_set(True);colliders.append(o.name)

# Colunata aberta, sete vãos e laje perfurada para a escada interna.
span=x1-x0;hole=(center-3.70,center+.85,back+.4,back+2.3)
for a,b in ((x0,hole[0]),(hole[1],x1)):
    g('Laje superior da colunata',pavement).box(((a+b)/2,(back+front)/2,roof-.20),(b-a,front-back,.40))
for a,b in ((back,hole[2]),(hole[3],front)):
    g('Laje superior da colunata',pavement).box(((hole[0]+hole[1])/2,(a+b)/2,roof-.20),(hole[1]-hole[0],b-a,.40))
g('Piso interior da colunata',pavement).box((center,(back+front)/2,floor-.13),(span,front-back,.26))
g('Parede posterior e retornos',wallmat).box((center,back-.18,(floor+roof)/2),(span,.36,roof-floor))
for x in (x0,x1):g('Parede posterior e retornos',wallmat).box((x,(back+front)/2,(floor+roof)/2),(.30,front-back,roof-floor))
for j in range(8):
    x=x0+j*span/7;geom=g('Pilares da colunata')
    geom.box((x,front-.20,(floor+roof-.40)/2),(.38,.44,roof-floor-.40))
    for z in (floor+.16,roof-.48):geom.box((x,front-.20,z),(.64,.64,.30))
for z,depth,hh in ((roof-.45,.70,.45),(roof-.10,.83,.16)):
    g('Entablamento da colunata').box((center,front-.18,z),(span+.55,depth,hh))
railing((x0,front,0),(x1,front,0),roof)
for x in (x0,x1):railing((x,back,0),(x,front,0),roof)
# Bordas do vão: abertura real na laje, guarda lateral.
for d in (hole[2],hole[3]):railing((hole[0],d,0),(hole[1],d,0),roof,'Guarda da escada interna')
railing((hole[0],hole[2],0),(hole[0],hole[3],0),roof,'Guarda da escada interna')

# Escada da colunata: voo longitudinal cabe sob o terraço, com topo na abertura.
count=30;run=(roof-floor)/.175*.26;startx=center-run;endx=center;stairwidth=1.25;stairy=back+1.30
for j in range(count):
    z=floor+(j+1)*(roof-floor)/count;x=startx+(j+.5)*(endx-startx)/count
    g('Escada interna da colunata',stone).box((x,stairy,z-.09),((endx-startx)/count,stairwidth,.18))
g('Patamar da escada interna',stone).box((endx+.60,stairy,roof-.13),(1.2,stairwidth,.26))
internal=G();internal.poly([(startx,stairy-stairwidth/2,floor),(endx,stairy-stairwidth/2,roof),(endx,stairy+stairwidth/2,roof),(startx,stairy+stairwidth/2,floor)]);internal.box((endx+.6,stairy,roof-.1),(1.2,stairwidth,.2));collider('Rampa interna e patamar',internal)
for d in (stairy-stairwidth/2,stairy+stairwidth/2):
    g('Laje inclinada da escada interna',stone).poly([(startx,d,floor-.20),(endx,d,roof-.20),(endx,d,roof-.40),(startx,d,floor-.40)])

# Terraço curvo sob a sacada do palácio, com cantaria aparente.
outline=[(center-5.8,3.8),(center+5.8,3.8)]+[(center+5.8*math.cos(j*math.pi/40),3.8+6.3*math.sin(j*math.pi/40)) for j in range(41)]
prism(g('Bastião curvo sob o pórtico',wallmat),outline,levels[1]-.5,69.67)
prism(g('Passeio superior curvo',pavement),outline,69.67,69.83)
for z in [levels[1]+k*.72 for k in range(9) if levels[1]+k*.72<69.5]:
    for a,b in zip(outline[2:],outline[3:]):g('Juntas horizontais da cantaria',stone).bar((*a,z),(*b,z),.025,6)
for a,b in zip(outline[2:],outline[3:]):
    # Corrimão contínuo, sem um pilar a cada segmento da curva.
    g('Guarda do terraço curvo').bar((*a,70.84),(*b,70.84),.07,8)
for j in range(31):
    t=j*math.pi/30;x=center+5.8*math.cos(t);y=3.8+6.3*math.sin(t)
    g('Guarda do terraço curvo').lathe((x,y,69.85),[(.06,0),(.06,.12),(.08,.42),(.04,.69),(.06,.92)],8)

# Patamares de jardim e escada lateral visíveis na encosta das fotografias.
stairx=x1-1.05;sw=1.70;flights=[]
for j in range(3):
    d0=5+j*9.2;d1=d0+8.2;za,zb=levels[j],levels[j+1];steps=math.ceil((za-zb)/.18);geom=g('Escadas laterais do jardim',stone)
    for k in range(steps):
        d=d0+(k+.5)*(d1-d0)/steps;z=za-k*(za-zb)/steps
        geom.box((stairx,d,z-.12),(sw,(d1-d0)/steps,.24))
    # Laje inclinada sob degraus, em vez de peças flutuantes.
    for x in (stairx-sw/2,stairx+sw/2):geom.poly([(x,d0,za-.2),(x,d1,zb-.2),(x,d1,zb-.45),(x,d0,za-.45)])
    geom.poly([(stairx-sw/2,d0,za-.45),(stairx+sw/2,d0,za-.45),(stairx+sw/2,d1,zb-.45),(stairx-sw/2,d1,zb-.45)])
    geom.box((stairx,d1+.5,zb-.13),(sw,1.,.26))
    ramp=G();ramp.poly([(stairx-sw/2,d0,za),(stairx+sw/2,d0,za),(stairx+sw/2,d1,zb),(stairx-sw/2,d1,zb)]);ramp.box((stairx,d1+.5,zb-.08),(sw,1.,.16));collider('Rampa jardim '+str(j+1),ramp)
    for x in (stairx-sw/2,stairx+sw/2):
        rail=g('Guardas das escadas');rail.bar((x,d0,za+1.0),(x,d1,zb+1.0),.055,8)
        for k in range(11):
            d=d0+(d1-d0)*k/10;z=za+(zb-za)*k/10;rail.bar((x,d,z),(x,d,z+1.),.035,8)
    flights.append({'from_z':za,'to_z':zb,'start_d':d0,'end_d':d1,'steps':steps,'rise_m':(za-zb)/steps})
for d,z in ((13.7,levels[1]),(22.9,levels[2])):
    g('Passeios dos patamares',pavement).box(((x0+stairx)/2,d,z-.13),(stairx-x0,1.05,.26))
    g('Contenções dos patamares',wallmat).box(((x0+stairx)/2,d+.7,z-1.2),(stairx-x0,.42,2.4))
    railing((x0,d+.75,0),(stairx-.9,d+.75,0),z)
# Embasamento da colunata acompanha cotas herdadas da ladeira, sem mover a pista.
base=G()
for j in range(7):
    a=x0+j*span/7;b=x0+(j+1)*span/7;z0=road[0]['z']+(road[-1]['z']-road[0]['z'])*(a/L);z1=road[0]['z']+(road[-1]['z']-road[0]['z'])*(b/L)
    base.poly([(a,front+.05,z0),(b,front+.05,z1),(b,front+.05,floor),(a,front+.05,floor)])
o=base.object('RIO R36 | Contenção sob a colunata',col,wallmat,S,props=props);created.append(o.name)
for name,geom in buffers.items():
    o=geom.object('RIO R36 | '+name,col,materials[name],S,props=props);created.append(o.name)
    if name in ('Laje superior da colunata','Piso interior da colunata','Passeios dos patamares','Passeio superior curvo','Parede posterior e retornos','Pilares da colunata'):collider(name,geom)

# Escavação/reperfilamento local: terreno cede lugar à estrutura; vias travadas.
source=scene.objects[previous['terrain_names'][0]];allowed={i for i,m in enumerate(source.data.materials) if any(s in m.name.lower() for s in ('terreno','encosta','conten')) and not any(s in m.name.lower() for s in ('asfalto','passeio','pedonal','chile'))}
def road_positions():return {tuple(round(v,5) for v in source.data.vertices[i].co) for p in source.data.polygons if p.material_index not in allowed for i in p.vertices}
roads=road_positions();terrain=[]
def ease(t):t=max(0,min(1,t));return t*t*(3-2*t)
def target(x,d,z):
    if x0-.01<=x<=x1+.01 and back-.02<=d<=front+.15:return floor-.22
    if abs(x-center)<5.8 and 3.8<=d<=3.8+6.3*math.sqrt(max(0,1-((x-center)/5.8)**2)):return min(z,69.50)
    if d<10.3:desired=levels[1]-.2
    elif d<14.1:desired=levels[1]-.2
    elif d<23.2:desired=levels[2]-.2
    else:desired=roof-.2
    if abs(x-stairx)<sw/2+.16:
        for f in flights:
            if f['start_d']<=d<=f['end_d']+1:desired=min(desired,f['from_z']+(f['to_z']-f['from_z'])*min(1,(d-f['start_d'])/(f['end_d']-f['start_d']))-.48)
    weight=ease((x-(x0-1.8))/1.8)*ease(((x1+1.8)-x)/1.8)*ease((d-3.8)/1.5)*ease((35-d)/1.7)
    return z+(min(z,desired)-z)*weight
for name in previous['terrain_names']:
    o=scene.objects[name];before=sig(o);me=o.data;M=wm(o);I=M.inverted()
    vertices=np.empty(len(me.vertices)*3,dtype=np.float32);me.vertices.foreach_get('co',vertices);A=np.array(SI@M);local=vertices.reshape((-1,3))@A[:3,:3].T+A[:3,3]
    indices=np.empty(len(me.loops),dtype=np.int32);me.loops.foreach_get('vertex_index',indices);starts=np.empty(len(me.polygons),dtype=np.int32);me.polygons.foreach_get('loop_start',starts)
    mask=np.ones(len(me.polygons),dtype=bool)
    for axis,low,high in ((0,x0-1.8,x1+1.8),(1,3.8,35),(2,-100,69.85)):
        vals=local[:,axis][indices];mask&=(np.maximum.reduceat(vals,starts)>low)&(np.minimum.reduceat(vals,starts)<high)
    if o==source:
        materials_idx=np.empty(len(me.polygons),dtype=np.int32);me.polygons.foreach_get('material_index',materials_idx);mask&=np.isin(materials_idx,list(allowed))
    bm=bmesh.new();bm.from_mesh(me);bm.faces.ensure_lookup_table();region={bm.faces[int(i)] for i in np.flatnonzero(mask)}
    for axis,val in ((U,x0-1.8),(U,x0),(U,x1),(U,x1+1.8),(N,3.8),(N,10.3),(N,14.1),(N,23.2),(N,back-.02),(N,front+.15),(N,35)):
        faces=[f for f in region if f.is_valid and (o!=source or f.material_index in allowed)];geom=set(faces)
        for f in faces:geom.update(f.edges);geom.update(f.verts)
        result=bmesh.ops.bisect_plane(bm,geom=list(geom),dist=.00001,plane_co=I@(P+axis*val),plane_no=M.to_3x3().transposed()@axis,clear_inner=False,clear_outer=False)
        for element in result['geom_cut']:
            if hasattr(element,'link_faces'):region.update(element.link_faces)
    moved=0;maxdelta=0
    for v in {v for f in region if f.is_valid for v in f.verts}:
        if o==source and any(f.material_index not in allowed for f in v.link_faces):continue
        p=SI@M@v.co
        if not (x0-1.801<=p.x<=x1+1.801 and 3.799<=p.y<=35.001 and p.z<69.85):continue
        newz=target(p.x,p.y,p.z)
        if abs(newz-p.z)<.00001:continue
        w=M@v.co;maxdelta=max(maxdelta,abs(newz-w.z));w.z=newz;v.co=I@w;moved+=1
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()
    terrain.append({'object':name,'before':before,'after':sig(o),'moved_vertices':moved,'maximum_z_delta_candidate_m':maxdelta})
assert not roads-road_positions(),'Uma posição existente de via mudou'
assert all(sig(scene.objects[n])==s for n,s in protected.items()),'Componente fora do escopo mudou'
report={'schema':'boas/architectural-pass-v1','revision':'R30B.36','source_before':parent,'source_after':None,'scene':scene.name,'status':'modeling_candidate','runtime_promoted':False,'created_objects':created,'colliders':colliders,'protected_signatures':protected,'terrain':terrain,'reference_media_ids':['palacio-rio-branco-oblique_right-47b57baa4f1a','palacio-rio-branco-right-5c2fa307341b'],'layout':{'frame_world':[list(row) for row in S],'palace_edge_length_m':L,'colonnade_extent_candidate':[x0,x1,back,front],'colonnade_floor_candidate_m':floor,'colonnade_roof_candidate_m':roof,'garden_levels_candidate_m':levels,'flights':flights,'verified_real_dimensions':None,'classification':'ADAPT_LOCAL','road_positions_preserved':len(roads)},'limitations':['Implantação relativa/cotas são candidatas pelos controles herdados e proporções das fotos; não medidas reais.','Fachada posterior voltada à rua não documentada suficientemente: preservada.','Escada interna da colunata e acesso superior exigem conferência visual antes de considerar circulação concluída.','Sem acesso público inventado da ladeira ao jardim; sem navmesh de produção.'],'visual_review':'pending'}
scene['architecture_revision']='R30B.36 | terraços e colunata do palácio | candidato'
bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
with dest.open('rb') as f:report['source_after']={'file':dest.relative_to(root).as_posix(),'sha256':hashlib.file_digest(f,'sha256').hexdigest(),'revision':'R30B.36','scene':scene.name}
(root/'docs/reports/blender/terracos_palacio_r30b36.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
