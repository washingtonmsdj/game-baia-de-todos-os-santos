"""Entorno imediato ancorado na geometria/IDs existentes; executar via MCP."""
import bpy,math,json
from pathlib import Path
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[2]
assert bpy.data.filepath.endswith('salvador_lacerda_r30b03_exterior_acessos.blend')
R=Matrix.Rotation(bpy.data.objects['CASCA | parede lateral'].rotation_euler.z,4,'Z');I=R.inverted()
col=bpy.data.collections.new('ENVIRONMENT_FINAL | entorno Lacerda R30B04');bpy.context.scene.collection.children.link(col)
ivory=bpy.data.materials['LAC R30B | reboco marfim fino'];dark=bpy.data.materials['LAC R30B | sombra veneziana'];frame=bpy.data.materials['LAC R30B | esquadria clara acetinada']

def mat(name,color):
    m=bpy.data.materials.new('ENTORNO LAC | '+name);m.diffuse_color=(*color,1);m.use_nodes=True
    p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=.72;return m,p

sett,p=mat('pedra irregular da praca',(.27,.30,.29));nt=sett.node_tree;g=nt.nodes.new('ShaderNodeNewGeometry');mapping=nt.nodes.new('ShaderNodeVectorMath');mapping.operation='SCALE';mapping.inputs[3].default_value=1
nt.links.new(g.outputs['Position'],mapping.inputs[0]);brick=nt.nodes.new('ShaderNodeTexBrick');brick.inputs['Scale'].default_value=1;brick.inputs['Brick Width'].default_value=.26;brick.inputs['Row Height'].default_value=.16;brick.inputs['Mortar Size'].default_value=.009
brick.inputs['Color1'].default_value=(.18,.21,.21,1);brick.inputs['Color2'].default_value=(.37,.40,.38,1);brick.inputs['Mortar'].default_value=(.065,.07,.065,1)
nt.links.new(mapping.outputs['Vector'],brick.inputs['Vector']);nt.links.new(brick.outputs['Color'],p.inputs['Base Color']);b=nt.nodes.new('ShaderNodeBump');b.inputs['Strength'].default_value=.38;b.inputs['Distance'].default_value=.012;nt.links.new(brick.outputs['Fac'],b.inputs['Height']);nt.links.new(b.outputs[0],p.inputs['Normal'])
mosaic,p=mat('pedra portuguesa calcada',(.62,.60,.53));nt=mosaic.node_tree;g=nt.nodes.new('ShaderNodeNewGeometry');v=nt.nodes.new('ShaderNodeTexVoronoi');v.feature='DISTANCE_TO_EDGE';v.inputs['Scale'].default_value=17;nt.links.new(g.outputs['Position'],v.inputs['Vector']);r=nt.nodes.new('ShaderNodeValToRGB');r.color_ramp.elements[0].position=.012;r.color_ramp.elements[0].color=(.12,.13,.12,1);r.color_ramp.elements[1].position=.06;r.color_ramp.elements[1].color=(.72,.71,.64,1);nt.links.new(v.outputs['Distance'],r.inputs[0]);nt.links.new(r.outputs[0],p.inputs['Base Color'])
yellow,_=mat('toldo amarelo Vissor',(.95,.55,.025));green,_=mat('reboco verde claro Vissor',(.64,.68,.49))

def boxes(name,items,material,location=None,osm=None):
    vv=[];ff=[]
    for center,size in items:
        x,y,z=[s/2 for s in size];k=len(vv);vv.extend(tuple(R@(Vector(center)+Vector(p))) for p in [(-x,-y,-z),(-x,-y,z),(-x,y,-z),(-x,y,z),(x,-y,-z),(x,-y,z),(x,y,-z),(x,y,z)])
        ff.extend(tuple(k+i for i in reversed(f)) for f in [(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)])
    me=bpy.data.meshes.new(name);me.from_pydata(vv,[],ff);me.update();me.materials.append(material);o=bpy.data.objects.new('ENTORNO LAC | '+name,me);col.objects.link(o);o['boas_role']='visual_environment';o['classification']='ADAPT_LOCAL';o['reference_status']='partial'
    if location:o['boas_location_id']=location
    if osm:o['osm_way_id']=osm
    return o

# Guarda-corpo na borda do polígono existente; intervalo da entrada explicitamente livre.
rail=[];posts=[]
for ya,yb,xa,xb in [(-22,-6,.55,.15),(15,41,-1.536,-3.31)]:
    length=yb-ya;n=math.ceil(length/2.8)
    for j in range(n+1):
        t=j/n;y=ya+length*t;x=xa+(xb-xa)*t+.18
        posts.extend([((x,y,70.57),(.36,.36,1.14)),((x,y,71.15),(.44,.44,.12))])
    for j in range(n):
        t=(j+.5)/n;y=ya+length*t;x=xa+(xb-xa)*t+.18
        rail.extend([((x,y,70.13),(.24,length/n-.25,.20)),((x,y,71.03),(.28,length/n-.25,.14))])
    count=math.floor(length/.28)
    for j in range(count):
        t=(j+.5)/count;y=ya+length*t;x=xa+(xb-xa)*t+.18
        # Perfil de balaústre esquemático, sem decorar o interior do elevador.
        for z,h,w in [(70.29,.16,.13),(70.45,.16,.075),(70.64,.22,.115),(70.84,.18,.065)]:rail.append(((x,y,z),(.14,w,h)))
boxes('Praca | pilaretes',posts,ivory,'praca-tome-de-sousa');boxes('Praca | balustrada modular',rail,ivory,'praca-tome-de-sousa')
plaza=bpy.data.objects['PRAÇA | OSM 1263035782'];plaza.data.materials.clear();plaza.data.materials.append(sett)
for o in bpy.data.objects:
    if o.name.startswith('MVP | saída baixa | caminho OSM 312006925'):o.data.materials.clear();o.data.materials.append(mosaic)

# Somente faces de passeio já classificadas, no entorno baixo; não pintar pista como calçada.
terrain=next(o for o in bpy.data.objects if o.name=='MVP | terreno corrigido | colisão estática')
ids={i for i,m in enumerate(terrain.data.materials) if m and any(t in m.name.lower() for t in ['passeio','percurso pedonal','pedra portuguesa'])}
terrain.data.materials.append(mosaic);newidx=len(terrain.data.materials)-1;count=0
for p in terrain.data.polygons:
    c=I@terrain.matrix_world@p.center
    if p.material_index in ids and -100<c.x<-76 and -6<c.y<52 and c.z<12:p.material_index=newidx;count+=1

# Vissor confirmado por OSM 1220650857 e letreiro da foto; não atribuir nome aos outros blocos.
building=next(o for o in bpy.data.objects if str(o.get('osm_way_id',''))=='1220650857')
building.data.materials.clear();building.data.materials.append(green)
a=Vector((-73.391,40.609,0));b=Vector((-72.395,47.712,0));t=(b-a).normalized();normal=Vector((-t.y,t.x,0));length=(b-a).length
def facadebox(name,s,z,width,height,depth,offset,material):
    # Construir no eixo da fachada real, sem usar o AABB rotacionado como footprint.
    o=boxes(name,[((0,0,0),(depth,width,height))],material,osm='1220650857')
    center=a+t*s+normal*offset;center.z=z
    for v in o.data.vertices:
        local=I@v.co;v.co=R@(center+normal*local.x+t*local.y+Vector((0,0,local.z)))
    return o
for row,z in enumerate([11.6,14.9]):
    for j in range(3):
        s=(j+.5)*length/3
        facadebox('Vissor | vao %d %d'%(row,j),s,z,1.35,1.9,.05,.04,dark)
        for edge in [-1,1]:facadebox('Vissor | moldura %d %d %d'%(row,j,edge),s+edge*.72,z,.10,2.1,.11,.09,ivory)
        facadebox('Vissor | peitoril %d %d'%(row,j),s,z-1.02,1.55,.14,.18,.14,ivory)
for j in range(2):facadebox('Vissor | abertura comercial '+str(j),(j+.5)*length/2,8.65,length/2-.35,2.6,.06,.04,dark)
awning=facadebox('Vissor | toldo amarelo',length/2,10.17,length+.2,.16,1.35,.72,yellow)
facadebox('Vissor | faixa do letreiro',length/2,10.55,length,.58,.09,.11,yellow)
data=bpy.data.curves.new('Deposito Vissor','FONT');data.body='DEPÓSITO VISSOR';data.align_x='CENTER';data.size=.36;data.extrude=.001
text=bpy.data.objects.new('ENTORNO LAC | Vissor | letreiro',data);col.objects.link(text);data.materials.append(dark)
text.location=R@(a+t*(length/2)+normal*.17+Vector((0,0,10.43)))
rot=Matrix(((t.x,0,normal.x),(t.y,0,normal.y),(0,1,0)));text.rotation_euler=(R.to_3x3()@rot).to_euler();text['osm_way_id']='1220650857';text['classification']='ADAPT_LOCAL'

for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D' and area.spaces.active.local_view:
        region=next(r for r in area.regions if r.type=='WINDOW')
        with bpy.context.temp_override(area=area,region=region):bpy.ops.view3d.localview(frame_selected=False)
dest=ROOT/'blender/salvador_lacerda_r30b04_entorno.blend';bpy.context.scene['lacerda_revision']='R30B.04 | entorno imediato';bpy.ops.wm.save_as_mainfile(filepath=str(dest))
report={'file':dest.name,'sidewalk_faces_material_refined':count,'new_objects':len(col.objects),'osm_building':'1220650857','geography_changed':False,'references_reused':['elevador-lacerda-front-2d9b4031ff6a','elevador-lacerda-front-97e36e6f289f'],'status':'partial; outros estabelecimentos sem identificacao confirmada'}
(ROOT/'artifacts/lacerda/r30b04_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(report,ensure_ascii=False))
