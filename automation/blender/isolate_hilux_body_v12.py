"""Oficina da carroceria Hilux: sem portas, capota policial, rodas ou chassi.

Uma malha principal com Mirror X; conjuntos retirados são preservados e ocultos.
Executar na V11 aberta, somente pela sessão Blender visível.
"""
import bpy, bmesh, ast, math, json, hashlib
from pathlib import Path
from mathutils import Vector

r=Path(__file__).resolve().parents[2];s=bpy.context.scene
source=r/'blender/assets/vehicles/rondesp-pickup/marrom_v11.blend'
out=r/'blender/assets/vehicles/rondesp-pickup/hilux_carroceria_v12.blend'
assert not bpy.app.background and Path(bpy.data.filepath).resolve()==source.resolve()
assert not out.exists() and not s.get('boas_v11_rig')
root=s.objects['RDP01_ROOT | viatura'];pfx='RDP01 | HILUX06 | '
collections={g:bpy.data.collections['RDP01 | '+g] for g in ['CARROCERIA','PORTAS','CAPOTA','VIDROS','RODAS','CHASSIS','LUZES','ACABAMENTOS','INSCRICOES','APRESENTACAO']}
brown=bpy.data.materials['RDP01 | Pintura marrom Rondesp'];paint=bpy.data.materials['RDP01 | Camuflagem marrom candidata'];black=bpy.data.materials['RDP01 | Polímero preto']
for fn in ast.parse((r/'automation/blender/create_rondesp_pickup_v01.py').read_text(encoding='utf-8')).body:
    if isinstance(fn,ast.FunctionDef) and fn.name=='mesh':exec(compile(ast.Module(body=[fn],type_ignores=[]),'<body-v12>','exec'),globals())
bpy.context.view_layer.update()

def grid(name,fn,nu,nv,group='CARROCERIA'):
    return mesh('HILUX12 | '+name,[fn(i/nu,j/nv) for i in range(nu+1) for j in range(nv+1)],
                [(i*(nv+1)+j,(i+1)*(nv+1)+j,(i+1)*(nv+1)+j+1,i*(nv+1)+j+1) for i in range(nu) for j in range(nv)],brown,group,smooth=True)

def clip(poly,fn,positive):
    result=[]
    for a,b in zip(poly,poly[1:]+poly[:1]):
        da,db=fn(a),fn(b);ia=da>=-1e-8 if positive else da<=1e-8;ib=db>=-1e-8 if positive else db<=1e-8
        if ia:result.append(a)
        if ia!=ib:result.append(a.lerp(b,da/(da-db)))
    return result

def split(o,name,fn,positive,group):
    vs=[];faces=[]
    for p in o.data.polygons:
        poly=clip([o.matrix_world@o.data.vertices[i].co for i in p.vertices],fn,positive)
        if len(poly)<3:continue
        base=len(vs);vs.extend(poly);faces.append(tuple(range(base,len(vs))))
    ob=mesh('HILUX12 | '+name,vs,faces,o.data.materials[0],group,smooth=True)
    bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001);bm.to_mesh(ob.data);bm.free()
    return ob

def keep(o,parent):
    world=o.matrix_world.copy();o.parent=parent;o.matrix_parent_inverse=parent.matrix_world.inverted();o.matrix_world=world

# Os caixilhos externos pertencem às portas. Colunas e calha ficam na cabine.
for side in (-1,1):
    frame=s.objects[pfx+'Armação cabine com vãos '+str(side)]
    counts={}
    for p in frame.data.polygons:
        ids=list(p.vertices)
        for a,b in zip(ids,ids[1:]+ids[:1]):k=tuple(sorted((a,b)));counts[k]=counts.get(k,0)+1
    edges=[(frame.data.vertices[a].co.copy(),frame.data.vertices[b].co.copy()) for (a,b),n in counts.items() if n==1]
    def top(y):
        zs=[a.z+(b.z-a.z)*(y-a.y)/(b.y-a.y) for a,b in edges if abs(b.y-a.y)>1e-8 and min(a.y,b.y)-1e-7<=y<=max(a.y,b.y)+1e-7]
        return max(zs) if zs else 1.78
    roof_fn=lambda p:top(p.y)-.018-p.z
    split(frame,'Calha fixa '+str(side),roof_fn,False,'CARROCERIA')
    moving=split(frame,'Armação temporária '+str(side),roof_fn,True,'PORTAS')
    def c_line(z):
        nodes=[(1.28,1.118),(1.50,1.092),(1.68,1.035),(1.75,.955),(1.81,.85)]
        for a,b in zip(nodes,nodes[1:]):
            if a[0]<=z<=b[0]:return a[1]+(b[1]-a[1])*(z-a[0])/(b[0]-a[0])
        return nodes[0][1] if z<1.28 else nodes[-1][1]
    cfn=lambda p:p.y-c_line(p.z)
    split(moving,'Coluna C fixa '+str(side),cfn,True,'CARROCERIA')
    leaves=split(moving,'Folhas temporárias '+str(side),cfn,False,'PORTAS')
    for part,positive in [('dianteira',False),('traseira',True)]:
        ob=split(leaves,'Caixilho porta '+part+' '+str(side),lambda p:p.y-(.121+.070*(p.z-1.291)),positive,'PORTAS')
        keep(ob,s.objects[f'RDP01 | Pivô porta {part} {side:+}'])
    for ob in (leaves,moving,frame):bpy.data.objects.remove(ob,do_unlink=True)
    trim=s.objects[pfx+'Acabamento B '+str(side)]
    for col in list(trim.users_collection):col.objects.unlink(trim)
    collections['PORTAS'].objects.link(trim)
    # Coluna B estrutural em chapa, atrás das folhas; sem barra de chassis.
    grid('Coluna B '+str(side),lambda u,t:(side*(.805-.095*t**2),.090+.086*u+.070*t,.488+1.292*t),5,32)

# Sem a capota, a caçamba precisa mostrar sua própria chapa interna e piso.
def arch(y):
    d=(y-1.655)/.525
    return max(.576,.38815+.518*math.sqrt(max(0,1-d*d)))

# Piso com os recortes funcionais das duas caixas de roda.
xs=sorted(set([-.807,-.585]+[-.585+1.17*i/20 for i in range(21)]+[.585,.807]))
ys=sorted(set([1.175,1.180,2.180,2.738]+[1.180+1.0*i/28 for i in range(29)]+[2.180+.558*i/12 for i in range(13)]))
vs=[(x,y,.576+.003*math.sin(2*math.pi*x/.135)**8) for x in xs for y in ys];fs=[]
for i in range(len(xs)-1):
    for j in range(len(ys)-1):
        cx=(xs[i]+xs[i+1])/2;cy=(ys[j]+ys[j+1])/2
        if abs(cx)>.585 and cy<2.180:continue
        fs.append((i*len(ys)+j,(i+1)*len(ys)+j,(i+1)*len(ys)+j+1,i*len(ys)+j+1))
mesh('HILUX12 | Piso caçamba aberto',vs,fs,brown,'CARROCERIA',smooth=True)
for side in (-1,1):
    grid('Parede interna caçamba '+str(side),lambda u,t:(side*(.807+.020*t),1.175+1.563*u,.576+.715*t),56,22)
    grid('Caixa roda caçamba '+str(side),lambda u,t:(side*(.585+.222*u),1.175+1.005*t,arch(1.175+1.005*t)),8,44)
    grid('Face interna caixa '+str(side),lambda u,t:(side*.585,1.175+1.005*u,.576+(arch(1.175+1.005*u)-.576)*t),44,12)
    # Flange superior enrolada entre a chapa exterior e a parede da caçamba.
    bed=s.objects[pfx+'Lateral caçamba '+str(side)]
    row=[bed.matrix_world@bed.data.vertices[i*37+36].co for i in range(101)]
    def lip(u,t):
        k=min(99,int(u*100));a=row[k].lerp(row[k+1],u*100-k)
        return a.lerp(Vector((side*.827,a.y,1.291)),t)
    grid('Borda superior caçamba '+str(side),lip,100,4)
grid('Parede frontal caçamba',lambda u,t:(-.807+1.614*u,1.175,.576+.715*t),40,22)
grid('Revestimento tampa caçamba',lambda u,t:(-.807+1.614*u,2.738,.576+.715*t),40,22)
grid('Piso estrutural cabine',lambda u,t:(-.793+1.586*u,-.949+2.084*t,.485),40,42)

# Reunir superfícies base, mantendo os quadros e os materiais originais.
# Materiais temporários do depsgraph nunca entram na base persistente.
parts=[o for o in collections['CARROCERIA'].objects if o.type=='MESH']
vs=[];faces=[];mats=[];mis=[];smooth=[];ranges=[]
for ob in parts:
    base=len(vs);transform=root.matrix_world.inverted()@ob.matrix_world
    vs.extend(transform@v.co for v in ob.data.vertices)
    mapping=[]
    for mat in ob.data.materials:
        if mat not in mats:mats.append(mat)
        mapping.append(mats.index(mat))
    for p in ob.data.polygons:
        faces.append(tuple(base+i for i in p.vertices));mis.append(mapping[p.material_index]);smooth.append(p.use_smooth)
    ranges.append((ob.name,base,len(vs)))
data=bpy.data.meshes.new('HILUX12 | Chaparia fixa editável');data.from_pydata(vs,[],faces)
for mat in mats:data.materials.append(mat)
for p,mi,sm in zip(data.polygons,mis,smooth):p.material_index=mi;p.use_smooth=sm
body=bpy.data.objects.new('HILUX | CARROCERIA PRINCIPAL',data);collections['CARROCERIA'].objects.link(body);body.parent=root
for label,start,end in ranges:
    group=body.vertex_groups.new(name=label.replace('RDP01 | ','')[:63]);group.add(list(range(start,end)),1,'REPLACE')
bm=bmesh.new();bm.from_mesh(data)
bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.000001,plane_co=Vector((0,0,0)),plane_no=Vector((1,0,0)),clear_inner=True,clear_outer=False)
for v in bm.verts:
    if abs(v.co.x)<.00001:v.co.x=0
bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001)
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free();data.update()
for ob in parts:bpy.data.objects.remove(ob,do_unlink=True)
mirror=body.modifiers.new('ESPELHO X • editar metade +X','MIRROR');mirror.use_clip=True;mirror.use_mirror_merge=True;mirror.merge_threshold=.00001;mirror.show_on_cage=True
thickness=body.modifiers.new('Espessura da chapa • 8 mm candidata','SOLIDIFY');thickness.thickness=.008;thickness.offset=-1
body.color=(.53,.55,.58,1)
body['boas_asset_id']='vehicle-rondesp-pickup';body['boas_role']='fixed_body_shell'
body['boas_editing']='Uma malha, simetria X. Editar +X. Portas, rodas, chassi e capota estão reservados e ocultos.'
body['boas_components']=json.dumps([label for label,_,_ in ranges],ensure_ascii=False)
body['boas_status']='candidate; chapa visual, não collider; forma e interior da caçamba para ajuste fino'

# A oficina mostra apenas a carroceria. Tudo retirado continua na mesma fonte.
stash=bpy.data.collections.new('RDP01 | PECAS RESERVADAS');s.collection.children.link(stash)
for g,col in collections.items():
    if g=='CARROCERIA':continue
    if col in list(s.collection.children):s.collection.children.unlink(col)
    stash.children.link(col);col.hide_viewport=True;col.hide_render=True
stash.hide_viewport=True;stash.hide_render=True
for ob in s.objects:
    ob.select_set(False)
    if ob not in (body,root):ob.hide_set(True)
body.hide_set(False);root.hide_set(True);body.select_set(True);bpy.context.view_layer.objects.active=body
s.frame_set(1);s.name='HILUX | carroceria isolada v12'
s['boas_authoring_mode']='body_only; factory pickup shell; parts retained hidden'
s['boas_revision_parent']=source.relative_to(r).as_posix();s['boas_edit_symmetry']='X; half +X'
s['boas_next_scope']='Ajustar carroceria isolada. Reintroduzir portas, rodas, chassi e equipamento somente depois.'
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            space=area.spaces.active;space.shading.type='SOLID';space.shading.color_type='OBJECT';space.shading.light='STUDIO';space.shading.studio_light='paint.sl';space.shading.show_cavity=False
            space.shading.background_type='VIEWPORT';space.shading.background_color=(.055,.055,.065)
            space.overlay.show_overlays=False
            space.region_3d.view_rotation=(Vector((0,.15,1.02))-Vector((-7,-8,3.3))).to_track_quat('-Z','Y')
            space.region_3d.view_location=(0,.15,1.02);space.region_3d.view_distance=5.4;space.region_3d.view_perspective='ORTHO'
bpy.context.view_layer.update()
bpy.data.libraries.write(str(out),{s},path_remap='RELATIVE',fake_user=True,compress=True)
rp=r/'docs/reports/blender/hilux_carroceria_v12.json'
report={'asset_id':'vehicle-rondesp-pickup','file':out.relative_to(r).as_posix(),'scene':s.name,'parent':source.relative_to(r).as_posix(),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'status':'candidate','authoring_mode':'body_only','body_mesh':body.name,'symmetry':'Mirror X; source half +X','body_components':[label for label,_,_ in ranges],'visible_meshes':[o.name for o in s.objects if o.type=='MESH' and o.visible_get()],'reserved_collection':stash.name,'objects':len(s.objects),'source_reopened':False,'visual_review':'pending','rig_applied':False,'runtime_exported':False,'notes':['Carroceria visual em malha única; juntas de chapas mantidas, não union boolean nem collider.','Portas/caixilhos, chassi, rodas, capota policial, vidros, interiores e equipamentos preservados ocultos.','Caçamba aberta com piso, paredes internas e caixas de roda candidatas, dimensões autorais.','Tentativa de rig V11 descartada após falha do Blender e mudança de escopo do usuário.']}
rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def reopen():
    bpy.ops.wm.open_mainfile(filepath=str(out));report=json.loads(rp.read_text(encoding='utf-8'));report['source_reopened']=True
    rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');return None
bpy.app.timers.register(reopen,first_interval=.5)
