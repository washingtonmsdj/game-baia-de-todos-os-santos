"""Continuidade da cabine e caçamba da Hilux isolada, via Blender visível.

V12 preservada. Contornos são interpretação das referências catalogadas,
sem alegar medidas de fábrica. Mantém malha única, Mirror X e peças reservadas.
"""
import bpy,bmesh,math,json,hashlib,bisect,collections
from pathlib import Path
from mathutils import Vector

r=Path(__file__).resolve().parents[2];s=bpy.context.scene
catalog=json.loads((r/'world/vehicles/catalog.json').read_text(encoding='utf-8'))
vehicle=next(v for v in catalog['vehicles'] if v['asset_id']=='vehicle-rondesp-pickup')
source=r/vehicle['authoring_base']['file'];out=r/'blender/assets/vehicles/rondesp-pickup/hilux_carroceria_v13.blend'
assert not bpy.app.background and source.name=='hilux_carroceria_v12.blend'
assert Path(bpy.data.filepath).resolve()==source.resolve() and not out.exists()
assert hashlib.sha256(source.read_bytes()).hexdigest()==vehicle['authoring_base']['sha256']
o=s.objects['HILUX | CARROCERIA PRINCIPAL']
recovery=r/'artifacts/vehicles/rondesp/pre-v13-visible-session.blend'
assert not recovery.exists()
bpy.data.libraries.write(str(recovery),{s},path_remap='RELATIVE',compress=True)
membership=collections.defaultdict(set)
for v in o.data.vertices:
    for g in v.groups:membership[g.group].add(v.index)
names={g.name:g.index for g in o.vertex_groups}

def ids(fragment):
    return set().union(*(membership[i] for name,i in names.items() if fragment in name))

def boundary(fragment):
    members=ids(fragment);count=collections.Counter()
    for p in o.data.polygons:
        if all(i in members for i in p.vertices):
            vs=list(p.vertices)
            for a,b in zip(vs,vs[1:]+vs[:1]):count[tuple(sorted((a,b)))]+=1
    return [(o.data.vertices[a].co.copy(),o.data.vertices[b].co.copy()) for (a,b),n in count.items() if n==1]

def section(edges,z):
    hits=[]
    for a,b in edges:
        if abs(b.z-a.z)>1e-8 and min(a.z,b.z)-1e-7<=z<=max(a.z,b.z)+1e-7:
            hits.append(a.lerp(b,(z-a.z)/(b.z-a.z)))
    return max(hits,key=lambda p:p.x) if hits else max((p for e in edges for p in e),key=lambda p:p.z)

def linear(nodes,x):
    if x<=nodes[0][0]:return nodes[0][1]
    if x>=nodes[-1][0]:return nodes[-1][1]
    for a,b in zip(nodes,nodes[1:]):
        if a[0]<=x<=b[0]:return a[1]+(b[1]-a[1])*(x-a[0])/(b[0]-a[0])

def smooth(t):return max(0,min(1,t))**2*(3-2*max(0,min(1,t)))

# Bordas existentes controlam os retornos: não tapar por cima com outra placa.
fender_ids=ids('Para-lama dianteiro 1')
lead=sorted((o.data.vertices[i].co.copy() for i in fender_ids if abs(o.data.vertices[i].co.y+1.945)<.002),key=lambda p:p.z)
fascia_edges=boundary('Para-choque e testa esculpidos')
bed_edge_points={}
for a,b in boundary('Lateral caçamba 1'):
    for p in (a,b):
        if p.z>1.28:
            key=round(p.y,5)
            if key not in bed_edge_points or p.z>bed_edge_points[key].z:bed_edge_points[key]=p
bed_edge=sorted(bed_edge_points.values(),key=lambda p:p.y)
def bed_top(y):
    ys=[p.y for p in bed_edge];i=max(0,min(len(ys)-2,bisect.bisect_right(ys,y)-1))
    a,b=bed_edge[i:i+2];return a.lerp(b,max(0,min(1,(y-a.y)/(b.y-a.y))))

# O teto estava descendo 11 cm na última estação, deixando a chapa posterior solta.
roof_ids=ids('Teto curvatura dupla')
roof_before={i:o.data.vertices[i].co.copy() for i in roof_ids}
for i in roof_ids:
    v=o.data.vertices[i];x,y,z=v.co
    if y<=.86:continue
    t=(y-.86)/.253;blend=smooth(t)
    row=[p for p in roof_before.values() if abs(p.y-y)<.00001]
    width=max(p.x for p in row);f=x/width
    target_width=.708
    v.co.x=x*(1-blend)+target_width*f*blend
    v.co.y=y-.008*blend
    v.co.z=z*(1-blend)+(1.785-.024*f**4)*blend

remove_fragments=['Parede posterior cabine','Retour colonne C','Coluna C fixa',
                  'Parede frontal caçamba','Piso caçamba aberto','Parede interna caçamba',
                  'Caixa roda caçamba','Face interna caixa','Borda superior caçamba',
                  'Revestimento tampa caçamba','Caixa interna roda (1, 1.655)',
                  'Retorno para-choque 1','Retorno farol 1']
remove_sets=[ids(name) for name in remove_fragments]
bm=bmesh.new();bm.from_mesh(o.data);bm.verts.ensure_lookup_table()
faces=[f for f in bm.faces if any(all(v.index in members for v in f.verts) for members in remove_sets if members)]
removed_faces=len(faces);bmesh.ops.delete(bm,geom=faces,context='FACES')
loose=[v for v in bm.verts if not v.link_faces]
if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
deform=bm.verts.layers.deform.verify()
brown=bpy.data.materials['RDP01 | Pintura marrom Rondesp']
mat=list(o.data.materials).index(brown)
new_components=[]

def patch(name,vs,fs,normal,smooth_faces=True):
    group=o.vertex_groups.new(name='HILUX13 | '+name);new_components.append(group.name)
    verts=[bm.verts.new(Vector(p)) for p in vs]
    for v in verts:v[deform][group.index]=1.
    for indices in fs:
        try:f=bm.faces.new([verts[k] for k in indices])
        except ValueError:continue
        f.normal_update()
        if f.normal.dot(Vector(normal))<0:f.normal_flip()
        f.material_index=mat;f.smooth=smooth_faces
    return verts

def grid(name,fn,nu,nv,normal):
    return patch(name,[fn(i/nu,j/nv) for i in range(nu+1) for j in range(nv+1)],
                 [(i*(nv+1)+j,(i+1)*(nv+1)+j,(i+1)*(nv+1)+j+1,i*(nv+1)+j+1) for i in range(nu) for j in range(nv)],normal)

# A chapa posterior tem contorno, janela e retorno arredondado na coluna C.
def cab_side(z):
    return linear([(.489,.8274),(.60,.878),(.80,.911),(.99,.895),(1.15,.885),(1.291,.836),(1.5,.800),(1.68,.744),(1.76,.708)],z)
def radius(z):return .024*(1-smooth((z-1.68)/.08))
def wall_width(z):return cab_side(z)-radius(z)
def rear_y(x,z):
    h=(z-.489)/1.296;w=wall_width(z)
    return 1.145-.032*h+.005*(1-(x/w)**2)*math.sin(math.pi*h)
def roof_back(x):return 1.785-.024*(x/.708)**4
def door_back(z):
    return linear([(.489,1.06),(.62,1.109),(.95,1.119),(1.291,1.115),(1.5,1.092),(1.68,1.035),(1.76,.965)],z)

grid('Coluna C e canto posterior',lambda u,t:(
    cab_side(.489+1.272*t) if u<=.70 else wall_width(.489+1.272*t)+radius(.489+1.272*t)*math.cos((u-.70)/.30*math.pi/2),
    door_back(.489+1.272*t)+(rear_y(wall_width(.489+1.272*t),.489+1.272*t)-radius(.489+1.272*t)-door_back(.489+1.272*t))*u/.70 if u<=.70 else rear_y(wall_width(.489+1.272*t),.489+1.272*t)-radius(.489+1.272*t)+radius(.489+1.272*t)*math.sin((u-.70)/.30*math.pi/2),
    .489+1.272*t),24,64,(1,0,0))

inner=[];outer=[];N=64
for i in range(N+1):
    a=-math.pi/2+math.pi*i/N
    x=.660*max(0,math.cos(a))**(1/3);z=1.528+.190*math.copysign(abs(math.sin(a))**(1/3),math.sin(a))
    if i in (0,N):x=0
    inner.append(Vector((x,rear_y(x,z),z)))
    dx,dz=x,z-1.528
    low,hi=1.,10.
    for _ in range(36):
        k=(low+hi)/2;px=dx*k;pz=1.528+dz*k
        valid=pz>=.489 and px<=wall_width(pz) and pz<=roof_back(px)
        if valid:low=k
        else:hi=k
    px,pz=dx*low,1.528+dz*low
    outer.append(Vector((px,rear_y(px,pz),pz)))
vs=[]
for i in range(N+1):
    for j in range(13):
        t=j/12;p=inner[i].lerp(outer[i],t)
        p.y=rear_y(p.x,p.z)
        # Nervuras rasas na chapa inferior, sem alterar as bordas de encontro.
        p.y-=.005*math.exp(-((p.z-.98)/.21)**4)*(math.exp(-((p.x-.24)/.045)**4)+math.exp(-((p.x-.51)/.045)**4))*math.sin(math.pi*t)**2
        vs.append(p)
patch('Painel posterior com vão do vidro',vs,[(i*13+j,(i+1)*13+j,(i+1)*13+j+1,i*13+j+1) for i in range(N) for j in range(12)],(0,1,0))
vs=[p+Vector((0,-.010*t,0)) for p in inner for t in (0,1)]
patch('Flange do vidro posterior',vs,[(i*2,(i+1)*2,(i+1)*2+1,i*2+1) for i in range(N)],(0,1,0))

# Bordas da caçamba compartilham as mesmas estações. Retorno com raio em vez de quina.
fore=1.175;aft=2.738
def bed_w(y):return .807-.030*max(0,min(1,(y-fore)/(aft-fore)))**12
def floor_z(x):return .575+.005*(.5+.5*math.cos(math.tau*x/.12))**8
def wall_x(y,z):
    edge=bed_top(y);t=max(0,min(1,(z-floor_z(bed_w(y)))/(edge.z-.014-floor_z(bed_w(y)))))
    return bed_w(y)*(1-t)+(edge.x-.032)*t
ys=sorted(set([fore,aft,2.180]+[fore+(2.180-fore)*i/40 for i in range(41)]+[2.180+(aft-2.180)*i/18 for i in range(19)]))
xs=sorted(set([0,.585,.807]+[.807*i/64 for i in range(65)]))
vs=[(x*bed_w(y)/.807,y,floor_z(x*bed_w(y)/.807)) for x in xs for y in ys];fs=[]
for i in range(len(xs)-1):
    for j in range(len(ys)-1):
        if (xs[i]+xs[i+1])/2>.585 and (ys[j]+ys[j+1])/2<2.180:continue
        fs.append((i*len(ys)+j,(i+1)*len(ys)+j,(i+1)*len(ys)+j+1,i*len(ys)+j+1))
patch('Piso caçamba e estampagem longitudinal',vs,fs,(0,0,1))
def innerwall(u,t):
    y=fore+(aft-fore)*u;e=bed_top(y);z=floor_z(bed_w(y))+(e.z-.014-floor_z(bed_w(y)))*t
    return bed_w(y)*(1-t)+(e.x-.032)*t,y,z
grid('Parede interna caçamba',innerwall,80,28,(-1,0,0))
grid('Borda enrolada caçamba',lambda u,t:(bed_top(fore+(aft-fore)*u).x-.032*math.sin(math.pi*t/2),fore+(aft-fore)*u,bed_top(fore+(aft-fore)*u).z-.014*(1-math.cos(math.pi*t/2))),80,12,(0,0,1))

def hump(y):
    t=max(0,min(1,(y-fore)/(2.180-fore)))
    return floor_z(.585)+.319*math.sin(math.pi*t)**.70
grid('Caixa roda interna integrada',lambda u,t:(.585+(wall_x(fore+(2.180-fore)*t,hump(fore+(2.180-fore)*t))-.585)*u,fore+(2.180-fore)*t,hump(fore+(2.180-fore)*t)),16,40,(0,0,1))
grid('Face interna caixa roda',lambda u,t:(.585,fore+(2.180-fore)*u,floor_z(.585)+(hump(fore+(2.180-fore)*u)-floor_z(.585))*t),40,20,(-1,0,0))

# Cabeceira própria da caçamba, sem prolongar a parede da cabine como uma tampa.
grid('Cabeceira caçamba estampada',lambda u,t:(.815*u,fore+.005*math.sin(math.pi*t)*math.sin(math.pi*u)**2,floor_z(.815*u)+(1.293-floor_z(.815*u))*t),64,32,(0,1,0))
grid('Retorno superior cabeceira',lambda u,t:(.815*u,fore-.014*math.sin(math.pi*t/2),1.293+.014*(1-math.cos(math.pi*t/2))),64,12,(0,0,1))
grid('Face interna tampa caçamba',lambda u,t:(bed_w(aft)*u,aft,floor_z(bed_w(aft)*u)+(1.282-floor_z(bed_w(aft)*u))*t),60,28,(0,-1,0))
grid('Retorno superior tampa caçamba',lambda u,t:(bed_w(aft)*u,aft+.041*math.sin(math.pi*t/2),1.282+.005*(1-math.cos(math.pi*t/2))),60,12,(0,0,1))

# Um único retorno dianteiro, entre as bordas reais do para-lama e da testa.
if len(lead)>=12:
    vs=[]
    for b in lead:
        a=section(fascia_edges,b.z)
        for i in range(9):vs.append(a.lerp(b,i/8))
    patch('Retorno dianteiro sem chapas duplicadas',vs,[(j*9+k,(j+1)*9+k,(j+1)*9+k+1,j*9+k+1) for j in range(len(lead)-1) for k in range(8)],(1,0,0))

# Remover superfícies degeneradas, unir apenas bordas já coincidentes e manter aberturas.
bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00008)
bm.normal_update()
bad=[f for f in bm.faces if f.calc_area()<1e-9]
if bad:bmesh.ops.delete(bm,geom=bad,context='FACES')
wire=[e for e in bm.edges if not e.link_faces]
if wire:bmesh.ops.delete(bm,geom=wire,context='EDGES')
loose=[v for v in bm.verts if not v.link_faces]
if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
bm.to_mesh(o.data);bm.free();o.data.update()
thick=next(m for m in o.modifiers if m.type=='SOLIDIFY')
thick.name='Espessura visual da chapa • candidata';thick.thickness=.0025;thick.use_even_offset=True;thick.use_quality_normals=True;thick.thickness_clamp=1.
o['boas_v13_changes']='Painel posterior com janela; canto C arredondado; cabeceira e bordas da caçamba; eliminação de retornos duplicados.'
s.name='HILUX | carroceria isolada v13';s['boas_revision_parent']=source.relative_to(r).as_posix();s['boas_v13_applied']=True
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            sp=area.spaces.active;sp.shading.color_type='OBJECT';sp.shading.show_cavity=False;sp.overlay.show_overlays=False
            sp.region_3d.view_rotation=(Vector((0,.40,1.1))-Vector((7,8,4.1))).to_track_quat('-Z','Y')
            sp.region_3d.view_location=(0,.40,1.1);sp.region_3d.view_distance=5.5
bpy.context.view_layer.update()
bpy.data.libraries.write(str(out),{s},path_remap='RELATIVE',fake_user=True,compress=True)
report={'asset_id':'vehicle-rondesp-pickup','file':out.relative_to(r).as_posix(),'scene':s.name,'parent':source.relative_to(r).as_posix(),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'status':'candidate','authoring_mode':'body_only','body_mesh':o.name,'replaced_components':remove_fragments,'new_components':new_components,'removed_faces':removed_faces,'base_vertices':len(o.data.vertices),'base_faces':len(o.data.polygons),'visible_meshes':[ob.name for ob in s.objects if ob.type=='MESH' and ob.visible_get()],'source_reopened':False,'visual_review':'pending','runtime_exported':False,'rig_applied':False,'reference_ids':['hilux-srx-user-rear','hilux-2024-std-dealer-side'],'notes':['Contornos, raios e espessura são parâmetros autorais candidatos, não medidas confirmadas de fábrica.','Cabine e caçamba mantêm a separação física, dentro da mesma malha de autoria.','Peças reservadas continuam ocultas; nenhuma exportação, npm, testes ou build.']}
rp=r/'docs/reports/blender/hilux_carroceria_v13.json';rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def reopen():
    bpy.ops.wm.open_mainfile(filepath=str(out));data=json.loads(rp.read_text(encoding='utf-8'));data['source_reopened']=True
    rp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');return None
bpy.app.timers.register(reopen,first_interval=.5)
