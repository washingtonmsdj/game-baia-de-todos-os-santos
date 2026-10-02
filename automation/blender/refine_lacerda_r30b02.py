"""Refino de saguões, aberturas e acabamentos funcionais na única janela MCP."""
import bpy, math, json
from pathlib import Path
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[2]
assert bpy.data.filepath.endswith('salvador_lacerda_r30b01_refinamento.blend')
assert not bpy.data.collections.get('HERO | Lacerda | acabamentos R30B02')
col=bpy.data.collections.new('HERO | Lacerda | acabamentos R30B02');bpy.context.scene.collection.children.link(col)
R=Matrix.Rotation(bpy.data.objects['CASCA | parede lateral'].rotation_euler.z,4,'Z');I=R.inverted()
stone=bpy.data.materials['LAC R30B | marmore claro peitoris']
steel=bpy.data.materials['LAC R30B | inox escovado']
ivory=bpy.data.materials['LAC R30B | reboco marfim fino']
frame=bpy.data.materials['LAC R30B | esquadria clara acetinada']
glass=bpy.data.materials['LAC R30B | vidro incolor transparente']
floor=bpy.data.materials['LAC R30B | granito cinza piso']
dark=bpy.data.materials['LAC R30B | sombra veneziana']

def bounds(o):
    vv=[I@o.matrix_world@v.co for v in o.data.vertices]
    return [(min(v[k] for v in vv),max(v[k] for v in vv)) for k in range(3)]

def batch(name, boxes, mat, parent=None, bevel=.003):
    vv=[];ff=[]
    for center,size in boxes:
        x,y,z=[s/2 for s in size];p=Vector(center);base=len(vv)
        vv.extend(tuple(R@(p+Vector(v))) for v in [(-x,-y,-z),(-x,-y,z),(-x,y,-z),(-x,y,z),(x,-y,-z),(x,-y,z),(x,y,-z),(x,y,z)])
        ff.extend(tuple(base+i for i in f) for f in [(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)])
    me=bpy.data.meshes.new(name);me.from_pydata(vv,[],ff);me.update();me.materials.append(mat)
    o=bpy.data.objects.new('LAC R30B02 | '+name,me);col.objects.link(o)
    o['boas_location_id']='elevador-lacerda';o['boas_role']='visual_detail';o['reference_status']='partial'
    if parent:
        o.parent=parent;o.matrix_parent_inverse=parent.matrix_world.inverted()
        o['elevator_id']=parent.get('elevator_id',0);o['elevator_role']='visual_child'
    if bevel:
        m=o.modifiers.new('Bordas de acabamento','BEVEL');m.width=bevel;m.segments=2
    return o

changes=[]
# Erro de material: janelas não devem ter reboco, nem rebaixos parecer sólidos planos.
for o in bpy.data.objects:
    if o.type!='MESH':continue
    if o.name.startswith('FACHADA SUPERIOR | janela'):
        o.data.materials.clear();o.data.materials.append(glass);changes.append(o.name)
    if o.name.startswith('FACHADA SUPERIOR | montante janela'):
        o.data.materials.clear();o.data.materials.append(frame)

# Recortes verdadeiros no pano superior; os caixilhos existentes permanecem no lugar.
wall=bpy.data.objects['FACHADA SUPERIOR | corpo elevado']
cut=0
for win in [o for o in bpy.data.objects if o.name.startswith('FACHADA SUPERIOR | janela') and o.type=='MESH']:
    bb=bounds(win);y0,y1=bb[1];z0,z1=bb[2]
    cutter=batch('temporario recorte', [((-.6,(y0+y1)/2,(z0+z1)/2),(2,y1-y0,z1-z0))],dark,bevel=0)
    mod=wall.modifiers.new('Vão real '+win.name,'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
    bpy.context.view_layer.objects.active=wall
    bpy.ops.object.modifier_apply(modifier=mod.name)
    mesh=cutter.data;bpy.data.objects.remove(cutter,do_unlink=True);bpy.data.meshes.remove(mesh);cut+=1

# Lambris com juntas, sem ocupar portas ou alterar as superfícies de colisão.
for o in list(bpy.data.objects):
    if o.type!='MESH' or not o.name.startswith(('INFERIOR | parede lateral','SUPERIOR | posterior lateral')):continue
    bb=bounds(o);lengths=[b-a for a,b in bb];thin=0 if lengths[0]<lengths[1] else 1;long=1-thin
    center=[sum(b)/2 for b in bb]
    toward=(4.245-center[1]) if thin==1 else (-5-center[0])
    sign=1 if toward>0 else -1
    plane=bb[thin][1 if sign>0 else 0]+sign*.018
    base=bb[2][0]+.01;top=min(base+1.65,bb[2][1]);n=math.ceil(lengths[long]/.6);rows=4;boxes=[]
    for i in range(n):
        for j in range(rows):
            p=center.copy();p[thin]=plane;p[long]=bb[long][0]+(i+.5)*lengths[long]/n;p[2]=base+.17+(j+.5)*(top-base-.17)/rows
            size=[.025,.025,(top-base-.17)/rows-.003];size[long]=lengths[long]/n-.003
            boxes.append((p,size))
    batch('Lambril marmore | '+o.name,boxes,stone)
    p=center.copy();p[thin]=plane;p[2]=base+.085;s=[.035,.035,.17];s[long]=lengths[long]
    batch('Rodape escuro | '+o.name,[(p,s)],dark)

# Folhas de cabine conservam nomes, metadata e independência para o mecanismo existente.
for o in list(bpy.data.objects):
    if o.type!='MESH' or not o.name.startswith('FUNCIONAL |'):continue
    role=o.get('elevator_role');bb=bounds(o)
    if role in ('cabin_door','landing_door'):
        o.data.materials.clear();o.data.materials.append(steel)
        if not any(m.type=='BEVEL' for m in o.modifiers):
            m=o.modifiers.new('Borda inox','BEVEL');m.width=.003;m.segments=2
        cx=sum(bb[0])/2;cy=sum(bb[1])/2;z0,z1=bb[2];side=o.get('door_side',1)
        # Junta de borracha e nervura de acabamento solidárias à própria folha.
        edge=bb[1][1 if o.get('door_leaf',1)<0 else 0]
        batch('Vedacao | '+o.name,[((cx+side*.041,edge,(z0+z1)/2),(.012,.009,z1-z0-.008))],dark,parent=o,bevel=.001)
    if 'corrimão' in o.name and not any(m.type=='BEVEL' for m in o.modifiers):
        o.data.materials.clear();o.data.materials.append(steel)
        m=o.modifiers.new('Perfil arredondado','BEVEL');m.width=.024;m.segments=5
    if o.name.endswith(' teto') and role=='cabin':
        o.data.materials.clear();o.data.materials.append(steel)
    if 'soleira' in o.name:
        # Soleiras de 1,12 m estavam menores que os vãos de 1,82 m.
        if bb[1][1]-bb[1][0]<1.2:
            mid=sum(bb[1])/2;factor=1.88/(bb[1][1]-bb[1][0])
            for v in o.data.vertices:
                p=I@o.matrix_world@v.co;p.y=mid+(p.y-mid)*factor;v.co=o.matrix_world.inverted()@R@p
            changes.append(o.name)
        o.data.materials.clear();o.data.materials.append(steel)

# Friso cruzetado da passarela: observado na foto exterior 20250721125003.
# Uma malha por lateral; não centenas de objetos.
for source in [o for o in bpy.data.objects if o.name.startswith('PASSARELA EXTERNA | vidro') and o.type=='MESH']:
    bb=bounds(source);x0,x1=bb[0];y=sum(bb[1])/2;sign=1 if y>4.245 else -1;y+=sign*.09;z=70.83
    vv=[];ff=[];step=.68;n=round((x1-x0)/step);step=(x1-x0)/n
    for j in range(n):
        for sgn in [-1,1]:
            a=Vector((x0+j*step,y,z-sgn*.22));b=Vector((x0+(j+1)*step,y,z+sgn*.22));axis=(b-a).normalized();up=Vector((-axis.z,0,axis.x))*.045;depth=Vector((0,.04,0));k=len(vv)
            vv.extend(tuple(R@p) for p in [a-up-depth,a-up+depth,a+up-depth,a+up+depth,b-up-depth,b-up+depth,b+up-depth,b+up+depth])
            ff.extend(tuple(k+i for i in f) for f in [(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)])
    me=bpy.data.meshes.new('Friso passarela');me.from_pydata(vv,[],ff);me.materials.append(ivory)
    o=bpy.data.objects.new('LAC R30B02 | Friso losangos | '+source.name,me);col.objects.link(o);o['boas_location_id']='elevador-lacerda';o['boas_role']='visual_detail'

bpy.context.scene['lacerda_revision']='R30B.02 | saguoes e acabamentos'
dest=ROOT/'blender/salvador_lacerda_r30b02_saguoes.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(dest))
report={'revision':dest.name,'true_window_openings':cut,'corrected_objects':changes,'new_objects':len(col.objects),'preserved':'Implantação, cabines, metadata e fonte runtime; nenhuma animação de gameplay substituída.','status':'partial'}
(ROOT/'artifacts/lacerda/r30b02_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(report,ensure_ascii=False))
