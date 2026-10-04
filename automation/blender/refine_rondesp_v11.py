"""Corrige os encontros das chapas V10 na única sessão visível; preserva V10."""
import ast, bpy, bmesh, math, json, hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

r = Path(__file__).resolve().parents[2]
s = bpy.context.scene
source = r / 'blender/assets/vehicles/rondesp-pickup/marrom_v10.blend'
out = r / 'blender/assets/vehicles/rondesp-pickup/marrom_v11.blend'
assert not bpy.app.background and Path(bpy.data.filepath).resolve() == source.resolve()
assert not out.exists() and not s.get('boas_v11_finish')
root = s.objects['RDP01_ROOT | viatura']
collections = {g: bpy.data.collections['RDP01 | '+g] for g in ['CARROCERIA','PORTAS','CAPOTA','VIDROS','RODAS','CHASSIS','LUZES','ACABAMENTOS','INSCRICOES','APRESENTACAO']}
brown = bpy.data.materials['RDP01 | Pintura marrom Rondesp']
paint = bpy.data.materials['RDP01 | Camuflagem marrom candidata']
black = bpy.data.materials['RDP01 | Polímero preto']
for filename, names in [('create_rondesp_pickup_v01.py',['mesh','tube','box']), ('rebuild_hilux_reference_v06.py',['interp','sidewidth'])]:
    for fn in ast.parse((r/'automation/blender'/filename).read_text(encoding='utf-8')).body:
        if isinstance(fn,ast.FunctionDef) and fn.name in names:
            exec(compile(ast.Module(body=[fn],type_ignores=[]),'<v11-helpers>','exec'),globals())
checkpoint = r/'artifacts/vehicles/rondesp/pre-v11-visible-session.blend'
assert not checkpoint.exists()
bpy.data.libraries.write(str(checkpoint),{s},path_remap='RELATIVE',compress=True)
pfx = 'RDP01 | HILUX06 | '
changed = []

def touch(o):
    if o.type == 'MESH':
        bm=bmesh.new();bm.from_mesh(o.data)
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
        if o.data.has_custom_normals:
            o.data.normals_split_custom_set([(0,0,0)]*len(o.data.loops))
        o.data.update()
    changed.append(o.name)

def grid(name,fn,nu,nv,mat,group):
    vs=[fn(i/nu,j/nv) for i in range(nu+1) for j in range(nv+1)]
    faces=[(i*(nv+1)+j,(i+1)*(nv+1)+j,(i+1)*(nv+1)+j+1,i*(nv+1)+j+1) for i in range(nu) for j in range(nv)]
    ob=mesh('HILUX11 | '+name,vs,faces,mat,group,smooth=True,thickness=.006)
    touch(ob);return ob

# O recuo artificial da coluna C criava uma quina e deixava a borracha solta.
for side in (-1,1):
    names=['Armação cabine com vãos '+str(side),'Vidro traseira '+str(side),
           'Vedação vidro traseira'+str(side),'Divisória vidro traseiro '+str(side)]
    for name in names:
        o=s.objects[pfx+name]; inv=o.matrix_world.inverted()
        points=o.data.vertices if o.type=='MESH' else [p for sp in o.data.splines for p in sp.points]
        for v in points:
            p=o.matrix_world@Vector(v.co[:3])
            fade=max(0,min(1,(p.y-.84)/.17))
            p.x+=side*.030*math.exp(-((p.y-1.105)/.13)**2)*fade
            v.co=inv@p if o.type=='MESH' else (*(inv@p),v.co.w)
        touch(o)

def boundary_edges(o):
    count={}
    for p in o.data.polygons:
        ids=list(p.vertices)
        for a,b in zip(ids,ids[1:]+ids[:1]):
            k=tuple(sorted((a,b)));count[k]=count.get(k,0)+1
    return [(o.matrix_world@o.data.vertices[a].co,o.matrix_world@o.data.vertices[b].co) for (a,b),n in count.items() if n==1]

def section(edges,value,axis,highest):
    hits=[]
    for a,b in edges:
        if abs(b[axis]-a[axis])>1e-8 and min(a[axis],b[axis])-1e-7<=value<=max(a[axis],b[axis])+1e-7:
            hits.append(a.lerp(b,(value-a[axis])/(b[axis]-a[axis])))
    return max(hits,key=lambda p:p[highest]) if hits else None

# Teto e armação usam agora exatamente a mesma borda, sem ressalto lateral.
roof=s.objects[pfx+'Teto curvatura dupla']
edges=boundary_edges(s.objects[pfx+'Armação cabine com vãos 1'])
for i in range(59):
    y=sum(roof.data.vertices[i*43+j].co.y for j in range(43))/43
    edge=section(edges,y,1,2)
    if edge is None:continue
    for j in range(43):
        f=2*j/42-1
        roof.data.vertices[i*43+j].co=(edge.x*f,y,edge.z+.024*(1-abs(f)**4))
touch(roof)

# Fechamento posterior segue a borda real da porta, com separação cabine/caçamba.
for side in (-1,1):
    old=s.objects[pfx+'Fechamento posterior cabine lateral '+str(side)]
    bpy.data.objects.remove(old,do_unlink=True)
    door=s.objects[pfx+'Porta traseira '+str(side)]
    row=[door.matrix_world@door.data.vertices[46*35+j].co for j in range(35)]
    def aft(u,t):
        j=min(33,int(t*34));a=row[j].lerp(row[j+1],t*34-j)
        a.y+=.005
        y=a.y+(1.140-a.y)*u
        endx=sidewidth(1.14,a.z)
        x=abs(a.x)*(1-u)+endx*u
        return side*x,y,a.z
    grid('Retour colonne C '+str(side),aft,14,34,paint,'CARROCERIA')
    # Une fente étroite, en retrait, distingue les deux ensembles mécaniques.
    grid('Joint cabine caçamba '+str(side),lambda u,t:(side*(sidewidth(1.15,.493+.798*t)-.008),1.140+.025*u,.493+.798*t),4,34,black,'ACABAMENTOS')

def bvh_for(o):
    ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
    tree=BVHTree.FromPolygons([ev.matrix_world@v.co for v in me.vertices],[tuple(p.vertices) for p in me.polygons])
    ev.to_mesh_clear();return tree

bpy.context.view_layer.update()
# Les accès latéraux sont conformés à la coque actuelle, pas au vieux profil.
cap=s.objects[pfx+'Capota policial ombros curvos'];cap_tree=bvh_for(cap)
for side in (-1,1):
    for key,offset in [('Acesso lateral capota ',.0018),('Junta acesso capota ',.003)]:
        o=s.objects[pfx+key+str(side)];inv=o.matrix_world.inverted()
        points=o.data.vertices if o.type=='MESH' else [p for sp in o.data.splines for p in sp.points]
        for v in points:
            p=o.matrix_world@Vector(v.co[:3]);hit,*_=cap_tree.ray_cast(Vector((side*2,p.y,p.z)),Vector((-side,0,0)),4)
            if hit is not None:
                q=inv@(hit+Vector((side*offset,0,0)))
                v.co=q if o.type=='MESH' else (*q,v.co.w)
        if o.type=='CURVE':o.data.bevel_depth=.0018
        touch(o)
    # Divisória termina na borda do vidro, sem ponta pendurada na chapa.
    div=s.objects[pfx+'Divisória vidro traseiro '+str(side)]
    pane=s.objects[pfx+'Vidro traseira '+str(side)]
    glass_edges=boundary_edges(pane)
    pts=div.data.splines[0].points
    for i,z in enumerate((1.339,1.666,1.721)):
        y=(.872,.932,.905)[i]
        p=section(glass_edges,y,1,2) if i==2 else None
        tree=bvh_for(pane);hit,*_=tree.ray_cast(Vector((side*2,y,z)),Vector((-side,0,0)),4)
        if hit is not None:pts[i].co=(*(div.matrix_world.inverted()@(hit+Vector((side*.003,0,0)))),1)
    div.data.bevel_depth=.005
    touch(div)

# Junta do capô assentada na superfície nova; retornos dianteiros sem sobreposição.
hood_tree=bvh_for(s.objects[pfx+'Capô e ombros estampados'])
for side in (-1,1):
    o=s.objects[pfx+'Junta capô '+str(side)]
    for p in o.data.splines[0].points:
        q=o.matrix_world@Vector(p.co[:3]);hit,*_=hood_tree.ray_cast(Vector((q.x,q.y,2)),Vector((0,0,-1)),2)
        if hit is not None:p.co=(*(o.matrix_world.inverted()@(hit+Vector((0,0,.001)))),1)
    o.data.bevel_depth=.001;touch(o)
    # Elimina junta antiga na frente que cruzava o farol e saía da carroceria.
    old=s.objects.get('RDP01 | HILUX08 | Junta para-choque '+str(side))
    if old:bpy.data.objects.remove(old,do_unlink=True)
    o=s.objects['RDP01 | HILUX09 | Retorno farol '+str(side)]
    for v in o.data.vertices:
        if abs(v.co.x)>.9275:v.co.x=side*.9275
    touch(o)

# Suportes antigos ultrapassavam a base do giroflex. Peças novas apoiadas no teto.
for o in list(s.objects):
    if any(k in o.name for k in ['Longarina suporte teto','Travessa suporte teto','Suporte giroflex']):
        bpy.data.objects.remove(o,do_unlink=True)
roof_tree=bvh_for(roof)
for side in (-1,1):
    for y in (-.10,.49):
        hit,*_=roof_tree.ray_cast(Vector((side*.56,y,3)),Vector((0,0,-1)),2)
        assert hit is not None
        top=1.862
        box('HILUX11 | Sapata teto '+str((side,y)),(side*.56,y,hit.z+.010),(.11,.10,.024),black,'ACABAMENTOS',.009)
        box('HILUX11 | Pé rack '+str((side,y)),(side*.56,y,(hit.z+.020+top)/2),(.043,.060,top-hit.z-.020),black,'ACABAMENTOS',.008)
    tube('HILUX11 | Longarina rack '+str(side),[(side*.56,y,1.875) for y in (-.20,.035,.59)],.014,black)
for y in (-.10,.49):
    tube('HILUX11 | Travessa rack '+str(y),[(-.56,y,1.875),(.56,y,1.875)],.012,black)
for side in (-1,1):
    box('HILUX11 | Apoio barra '+str(side),(side*.44,.035,1.891),(.065,.10,.030),black,'LUZES',.006)

s['boas_v11_finish']=True
s.name='VIATURA | Rondesp Hilux marrom v11'
s['boas_revision_parent']=source.relative_to(r).as_posix()
s['boas_review_status']='candidate; encaixes corrigidos; rig em preparação'
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            space=area.spaces.active
            space.shading.type='SOLID';space.shading.color_type='MATERIAL';space.shading.show_cavity=False
            space.overlay.show_overlays=False
            space.region_3d.view_rotation=(Vector((0,.2,1.1))-Vector((-7,7,3.1))).to_track_quat('-Z','Y')
            space.region_3d.view_location=(0,.2,1.1);space.region_3d.view_distance=5.8
bpy.context.view_layer.update()
bpy.data.libraries.write(str(out),{s},path_remap='RELATIVE',fake_user=True,compress=True)
rp=r/'docs/reports/blender/rondesp_marrom_v11.json'
rp.write_text(json.dumps({'file':out.relative_to(r).as_posix(),'scene':s.name,'asset_id':'vehicle-rondesp-pickup','parent':source.relative_to(r).as_posix(),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'status':'candidate','finish_changed':changed,'source_reopened':False,'visual_review':'pending','rig':'pending','runtime_exported':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def reopen():
    bpy.ops.wm.open_mainfile(filepath=str(out))
    data=json.loads(rp.read_text(encoding='utf-8'));data['source_reopened']=True
    rp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return None
bpy.app.timers.register(reopen,first_interval=.5)
