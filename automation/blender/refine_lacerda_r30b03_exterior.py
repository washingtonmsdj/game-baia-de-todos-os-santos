"""Volumes de fachada e portais, sem alterar implantação ou sistemas internos."""
import bpy,json
from pathlib import Path
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[2]
assert bpy.data.filepath.endswith('salvador_lacerda_r30b02_saguoes.blend')
col=bpy.data.collections.new('HERO | Lacerda | fachadas e acessos R30B03');bpy.context.scene.collection.children.link(col)
R=Matrix.Rotation(bpy.data.objects['CASCA | parede lateral'].rotation_euler.z,4,'Z');I=R.inverted()
ivory=bpy.data.materials['LAC R30B | reboco marfim fino'];stone=bpy.data.materials['LAC R30B | marmore claro peitoris'];frame=bpy.data.materials['LAC R30B | esquadria clara acetinada']

def bb(o):
    vv=[I@o.matrix_world@v.co for v in o.data.vertices]
    return [(min(v[i] for v in vv),max(v[i] for v in vv)) for i in range(3)]

def box(name,pos,size,mat=ivory):
    x,y,z=[s/2 for s in size];v=[(-x,-y,-z),(-x,-y,z),(-x,y,-z),(-x,y,z),(x,-y,-z),(x,-y,z),(x,y,-z),(x,y,z)]
    me=bpy.data.meshes.new(name);me.from_pydata([tuple(R@(Vector(p)+Vector(pos))) for p in v],[],[tuple(reversed(f)) for f in [(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]]);me.update();me.materials.append(mat)
    o=bpy.data.objects.new('LAC R30B03 | '+name,me);col.objects.link(o);o['boas_location_id']='elevador-lacerda';o['boas_role']='visual_architecture';o['reference_status']='partial';return o

def cut(wall,pos,size):
    o=box('recorte temporario',pos,size);m=wall.modifiers.new('Abertura real','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=o;bpy.context.view_layer.objects.active=wall;bpy.ops.object.modifier_apply(modifier=m.name)
    mesh=o.data;bpy.data.objects.remove(o,do_unlink=True);bpy.data.meshes.remove(mesh)

# Pano acima da marquise baixa era um bloco de dois metros sem correspondência na foto.
o=bpy.data.objects['FACHADA INFERIOR | platibanda'];bounds=bb(o);old=bounds[2]
for v in o.data.vertices:
    p=o.matrix_world@v.co;p.z=12.30+(p.z-old[0])/(old[1]-old[0])*.24;v.co=o.matrix_world.inverted()@p
o['revision_note']='R30B03: coroamento baixo reduzido conforme foto 2025; torre e acesso preservados.'

# Perfis da marquise e profundidade dos portais da Cidade Baixa.
o=bpy.data.objects['FACHADA INFERIOR | marquise'];b=bb(o);x0,x1=b[0];y0,y1=b[1];z=b[2][0]
box('Cidade Baixa | testeira da marquise',(x0+.06,(y0+y1)/2,z+.10),(.12,y1-y0,.20))
box('Cidade Baixa | faixa inferior da marquise',(x0+.10,(y0+y1)/2,z-.065),(.20,y1-y0-.16,.13))
for door in [o for o in bpy.data.objects if o.name.startswith('FACHADA INFERIOR | porta') and o.type=='MESH']:
    b=bb(door);y0,y1=b[1];bottom=7.406;top=b[2][1]
    # A folha antiga já estava oculta. Não reativar ou preencher a passagem.
    for y in [y0-.055,y1+.055]:box('Cidade Baixa | retorno portal '+door.name+str(y),(-82.10,y,(bottom+top)/2),(.28,.11,top-bottom),stone)
    box('Cidade Baixa | verga portal '+door.name,(-82.10,(y0+y1)/2,top+.07),(.28,y1-y0+.22,.14),stone)

# Coroamento escalonado da fachada da praça: extensão do volume existente.
box('Cidade Alta | degrau central do coroamento',(-.55,4.245,87.31),(.60,5.5,.42))
box('Cidade Alta | degrau intermediario esquerdo',(-.55,.72,87.21),(.60,1.55,.22))
box('Cidade Alta | degrau intermediario direito',(-.55,7.77,87.21),(.60,1.55,.22))

# Janelas laterais existentes: abrir a parede atrás dos caixilhos, mantendo ritmo e footprint.
walls=[o for o in bpy.data.objects if o.name.startswith('SUPERIOR | lateral corpo elevado') and o.type=='MESH']
windows=[o for o in bpy.data.objects if o.name.startswith('EDIFICIO | janela lateral') and o.type=='MESH']
openings=0
for wall in walls:
    wb=bb(wall);wy=sum(wb[1])/2
    for win in windows:
        b=bb(win);y=sum(b[1])/2
        if abs(y-wy)>.7:continue
        x0,x1=b[0];z0,z1=b[2];cut(wall,((x0+x1)/2,wy,(z0+z1)/2),(x1-x0,1,z1-z0));openings+=1

# Laterais do acesso superior: pórticos abertos acima do peitoril, coerentes com varandas.
# Mantêm pilares, viga, piso e proteção inferior. Dimensões são adaptação à malha existente.
for wall in [o for o in bpy.data.objects if o.name.startswith('SUPERIOR | parede lateral saguão') and o.type=='MESH']:
    b=bb(wall);x0,x1=b[0];y=sum(b[1])/2;span=(x1-x0-.9)/3
    for j in range(3):
        a=x0+.45+j*span+.14;end=x0+.45+(j+1)*span-.14
        cut(wall,((a+end)/2,y,72.65),(end-a,.8,2.70))
        box('Cidade Alta | peitoril lateral '+str(j)+' '+wall.name,((a+end)/2,y,71.31),(end-a+.06,.36,.10),stone)
    wall['classification']='ADAPT_LOCAL';wall['revision_note']='Aberturas de varanda; dimensões adaptadas à implantação existente, sem levantamento cadastral.'

for a in bpy.context.screen.areas:
    if a.type=='VIEW_3D' and a.spaces.active.local_view:
        for o in col.objects:o.local_view_set(a.spaces.active,True)
bpy.context.scene['lacerda_revision']='R30B.03 | fachadas e acessos'
path=ROOT/'blender/salvador_lacerda_r30b03_exterior_acessos.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path))
report={'revision':path.name,'side_window_openings':openings,'lateral_access_openings':6,'new_architecture_objects':len(col.objects),'geography_changed':False,'runtime_promoted':False,'classification':'ADAPT_LOCAL; fidelity partial','legacy_lower_landing':'Coleção 13 já oculta; não alterada.'}
(ROOT/'artifacts/lacerda/r30b03_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(report,ensure_ascii=False))
