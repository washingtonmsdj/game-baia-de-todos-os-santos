"""V15: armação contínua da cabine sem portas, via única sessão visível.

As bordas do teto, colunas e painel posterior compartilham vértices. Preserva
V14, identidade da carroceria, Mirror X e todos os conjuntos reservados.
"""
import ast,bpy,bmesh,math,json,hashlib,collections
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt

r=Path(__file__).resolve().parents[2];s=bpy.context.scene
catalog=json.loads((r/'world/vehicles/catalog.json').read_text(encoding='utf-8'))
vehicle=next(v for v in catalog['vehicles'] if v['asset_id']=='vehicle-rondesp-pickup')
source=r/vehicle['authoring_base']['file'];out=r/'blender/assets/vehicles/rondesp-pickup/hilux_carroceria_v15.blend'
assert not bpy.app.background and source.name=='hilux_carroceria_v14.blend'
assert Path(bpy.data.filepath).resolve()==source.resolve() and not out.exists()
assert hashlib.sha256(source.read_bytes()).hexdigest()==vehicle['authoring_base']['sha256']
o=s.objects['HILUX | CARROCERIA PRINCIPAL'];labels=json.loads(o['boas_panel_id_map'])
attr=o.data.attributes['boas_panel_id']
checkpoint=r/'artifacts/vehicles/rondesp/pre-v15-visible-session.blend'
assert not checkpoint.exists()
bpy.data.libraries.write(str(checkpoint),{s},path_remap='RELATIVE',compress=True)
for fn in ast.parse((r/'automation/blender/rebuild_hilux_reference_v06.py').read_text(encoding='utf-8')).body:
    if isinstance(fn,ast.FunctionDef) and fn.name in {'interp','sidewidth'}:
        exec(compile(ast.Module(body=[fn],type_ignores=[]),'secoes-v06','exec'),globals())
def pid(name):return next(int(k) for k,v in labels.items() if v==name)
def smooth(t):
    t=max(0,min(1,t));return t*t*(3-2*t)
def key(p):return tuple(round(float(c),6) for c in p)

# Manter a borda do para-lama já corrigida: o pé A continua ligado a ela.
fender=pid('HILUX14 | Para-lama continuo ate soleira');counts=collections.Counter();direct={}
for p in o.data.polygons:
    if attr.data[p.index].value!=fender:continue
    vv=list(p.vertices)
    for a,b in zip(vv,vv[1:]+vv[:1]):
        e=tuple(sorted((a,b)));counts[e]+=1;direct[e]=(a,b)
aft=[]
for e,n in counts.items():
    if n!=1:continue
    a,b=[o.data.vertices[i].co.copy() for i in direct[e]]
    if min(a.y,b.y)>-1.01 and abs(a.z-b.z)>.001:aft.extend([a,b])
aft=sorted({key(p):p for p in aft}.values(),key=lambda p:p.z)
# Separar a borda traseira do arco de roda adjacente, que também varia em Z.
def on_aft(p):
    t=(p.z-.485)/.818
    if t<=.66:return abs(p.y-(-.975+.080*(1-t)**4))<.00002
    return p.y>=-.976 and p.z<=1.304
aft=[p for p in aft if on_aft(p)]
assert len(aft)>=35

# Curvas comuns a todos os painéis novos. Parâmetros autorais candidatos.
def roof_width(y):return interp([(-.338,.711),(-.24,.708),(-.06,.700),(.50,.693),(.86,.694),(1.02,.706),(1.105,.708)],y)
def roof_edge_z(y):return interp([(-.338,1.768),(-.24,1.786),(-.06,1.795),(.50,1.793),(.86,1.782),(1.02,1.770),(1.105,1.761)],y)
def cab_side(z):return interp([(.489,.8274),(.60,.878),(.80,.911),(.99,.895),(1.15,.885),(1.291,.836),(1.5,.800),(1.68,.744),(1.761,.708)],z)
def radius(z):return .024*(1-smooth((z-1.68)/.081))
def wall_width(z):return cab_side(z)-radius(z)
def rear_y(z):
    h=(z-.489)/1.296
    return (1.145-.032*h)*(1-smooth((z-1.60)/.161))+1.105*smooth((z-1.60)/.161)
def wall_y(x,z):
    h=max(0,min(1,(z-.489)/1.296));w=max(wall_width(z),.001)
    crown=.004*(1-(x/w)**2)*math.sin(math.pi*h)
    return rear_y(z)+crown*(1-smooth((z-1.70)/.061))
def roof_point(y,u):return Vector((roof_width(y)*u,y,roof_edge_z(y)+.024*(1-u**4)))
def cab_x(y,z):
    low=sidewidth(y,z)
    if z<.525:low=.830*(1-smooth((z-.489)/.036))+low*smooth((z-.489)/.036)
    high=interp([(1.30,.834),(1.50,.800),(1.68,.752),(1.80,.690)],z)
    x=low*(1-smooth((z-1.27)/.06))+high*smooth((z-1.27)/.06)
    blend=smooth((y-.82)/max(.02,rear_y(z)-radius(z)-.82))
    x=x*(1-blend)+cab_side(z)*blend
    if z>1.58:
        rz=roof_edge_z(y);mix=smooth((z-1.58)/max(.05,rz-1.58))
        x+=(roof_width(y)-interp([(1.30,.834),(1.50,.800),(1.68,.752),(1.80,.690)],rz))*mix*(1-blend)
    return x

ny,nx,nz=64,32,80
roof_ys=sorted(set([-.338+1.443*i/ny for i in range(ny+1)]+[.118,.232,.86,1.02]))
zs=[.489+(1.761-.489)*i/nz for i in range(nz+1)]
roof_side=[roof_point(y,1) for y in roof_ys]
side_back=[Vector((cab_side(z),rear_y(z)-radius(z),z)) for z in zs]
fore=aft+[Vector((.837,-.981,1.322)),Vector((.803,-.970,1.326))]
fore+=[Vector((.803*(1-t)+.711*t,-.970*(1-t)-.338*t,1.326*(1-t)+1.768*t)) for t in [i/32 for i in range(1,33)]]
outer3=fore+roof_side[1:]+list(reversed(side_back[:-1]))
outer3+=[Vector((.830,1.121-(1.121+.895)*i/48,.489)) for i in range(1,49)]
# Evitar um segundo ponto de fechamento quase coincidente.
if (outer3[-1]-outer3[0]).length<.005:outer3.pop()
outer=[Vector((p.y,p.z)) for p in outer3];bindings={key(p):v for p,v in zip(outer,outer3)}

def rounded(points,rad=.028,n=8):
    result=[]
    for i,point in enumerate(points):
        p=Vector(point);prev=Vector(points[i-1]);nxt=Vector(points[(i+1)%len(points)])
        a=p+(prev-p).normalized()*min(rad,(prev-p).length*.30)
        b=p+(nxt-p).normalized()*min(rad,(nxt-p).length*.30)
        for j in range(n):
            t=j/n;result.append((1-t)**2*a+2*(1-t)*t*p+t*t*b)
    return result
front_hole=rounded([(-.877,.516),(.100,.516),(.111,1.750),(-.258,1.746),(-.360,1.694),(-.910,1.320),(-.940,1.245),(-.908,.610)])
rear_hole=rounded([(.244,.516),(1.043,.516),(1.087,.625),(1.094,1.280),(1.061,1.510),(.977,1.681),(.891,1.750),(.240,1.750)])
holes=[front_hole,rear_hole]
def inside(p,poly):
    yes=False
    for a,b in zip(poly,poly[1:]+poly[:1]):
        if (a.y>p.y)!=(b.y>p.y) and p.x<(b.x-a.x)*(p.y-a.y)/(b.y-a.y)+a.x:yes=not yes
    return yes

retire_names=['HILUX06 | Teto curvatura dupla','HILUX13 | Retorno continuo da borda do teto','HILUX13 | Encontro teto painel posterior',
    'HILUX13 | Coluna B com cantos arredondados','HILUX13 | Retorno batente B -1','HILUX13 | Retorno batente B 1',
    'HILUX13 | Coluna C e canto posterior','HILUX14 | Batente C com retorno interno',
    'HILUX13 | Painel posterior com vão do vidro','HILUX13 | Flange do vidro posterior',
    'HILUX14 | Montante A com largura de chapa','HILUX14 | Retorno interno montante A','HILUX14 | Pe montante A junto ao cowl',
    'HILUX14 | Batente A integrado ao para-lama']
retired={pid(n) for n in retire_names}
bm=bmesh.new();bm.from_mesh(o.data);fl=bm.faces.layers.int.get('boas_panel_id');deform=bm.verts.layers.deform.verify()
remove=[f for f in bm.faces if f[fl] in retired];removed=len(remove);bmesh.ops.delete(bm,geom=remove,context='FACES')
mat=list(o.data.materials).index(bpy.data.materials['RDP01 | Pintura marrom Rondesp']);new=[]
def patch(name,vs,fs,normal=None):
    g=o.vertex_groups.new(name='HILUX15 | '+name);new.append(g.name);labels[str(g.index+1)]=g.name
    vv=[bm.verts.new(Vector(p)) for p in vs]
    for v in vv:v[deform][g.index]=1.
    for inds in fs:
        try:f=bm.faces.new([vv[i] for i in inds])
        except ValueError:continue
        f.normal_update()
        if normal is not None and f.normal.dot(Vector(normal))<0:f.normal_flip()
        f[fl]=g.index+1;f.material_index=mat;f.smooth=True
    return vv
def strip(name,rows,normal=None):
    n=len(rows[0]);return patch(name,[p for row in rows for p in row],
        [(i*n+j,(i+1)*n+j,(i+1)*n+j+1,i*n+j+1) for i in range(len(rows)-1) for j in range(n-1)],normal)

# CDT conserva os vãos inteiros das portas, sem remendar colunas por cima.
pts=[];constraints=[]
for loop in [outer]+holes:
    base=len(pts);pts.extend(loop);constraints.extend((base+i,base+(i+1)%len(loop)) for i in range(len(loop)))
for i in range(1,85):
    for j in range(1,52):
        p=Vector((-.981+2.126*i/85,.489+1.33*j/52))
        if inside(p,outer) and not any(inside(p,h) for h in holes):pts.append(p)
coords,_,faces,*_=delaunay_2d_cdt(pts,constraints,[],0,1e-7)
faces=[f for f in faces if inside(sum((coords[k] for k in f),Vector((0,0)))/len(f),outer) and not any(inside(sum((coords[k] for k in f),Vector((0,0)))/len(f),h) for h in holes)]
vs=[bindings.get(key(p),Vector((cab_x(p.x,p.y),p.x,p.y))) for p in coords]
patch('Armacão lateral continua A B C',vs,faces,(1,0,0))
strip('Teto continuo ate as colunas',[[roof_point(y,i/nx) for i in range(nx+1)] for y in roof_ys],(0,0,1))

# Retornos dos batentes nas próprias bordas dos vãos: ambos ficam ligados ao cage.
for name,loop in zip(['dianteiro','traseiro'],holes):
    rows=[]
    for i,p in enumerate(loop+[loop[0]]):
        j=i%len(loop);tangent=(loop[(j+1)%len(loop)]-loop[(j-1)%len(loop)]).normalized()
        normal=Vector((-tangent.y,tangent.x));base=Vector((cab_x(p.x,p.y),p.x,p.y))
        rows.append([base+Vector((-.025*k/6,.002*math.sin(math.pi*k/6)*normal.x,.002*math.sin(math.pi*k/6)*normal.y)) for k in range(7)])
    strip('Batente '+name+' ligado ao contorno',rows)

# O canto C e a parede traseira usam exatamente as mesmas estações de altura.
strip('Canto posterior cabine arredondado',[[Vector((wall_width(z)+radius(z)*math.cos(math.pi*j/24),rear_y(z)-radius(z)+radius(z)*math.sin(math.pi*j/24),z)) for j in range(13)] for z in zs],(1,1,0))
outer_back=[Vector((wall_width(.489)*i/nx,wall_y(wall_width(.489)*i/nx,.489),.489)) for i in range(nx+1)]
outer_back+=[Vector((wall_width(z),wall_y(wall_width(z),z),z)) for z in zs[1:]]
outer_back+=[roof_point(1.105,i/nx) for i in reversed(range(nx))]
inner=[]
for p in outer_back:
    dx,dz=p.x,p.z-1.528
    k=((dx/.660)**6+(dz/.190)**6)**(-1/6)
    x,z=dx*k,1.528+dz*k
    inner.append(Vector((x,wall_y(x,z),z)))
rows=[]
for a,b in zip(inner,outer_back):
    row=[]
    for i in range(13):
        t=i/12;p=a.lerp(b,t);p.y=wall_y(p.x,p.z)
        p.y-=.003*math.exp(-((p.z-.98)/.21)**4)*(math.exp(-((p.x-.24)/.045)**4)+math.exp(-((p.x-.51)/.045)**4))*math.sin(math.pi*t)**2
        row.append(p)
    rows.append(row)
strip('Painel posterior unido ao teto e cantos',rows,(0,1,0))
strip('Retorno vao vidro traseiro',[[p,p+Vector((0,-.010,0))] for p in inner])

# O cabeçalho do para-brisa acompanha a borda frontal do teto inteiro.
strip('Retorno cabeçalho parabrisa',[[roof_point(-.338,i/nx),roof_point(-.338,i/nx)+Vector((0,.009,-.014))] for i in range(nx+1)],(0,-1,0))
bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00006)
bad=[f for f in bm.faces if f.calc_area()<1e-10]
if bad:bmesh.ops.delete(bm,geom=bad,context='FACES')
loose=[v for v in bm.verts if not v.link_faces]
if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
bm.normal_update();bm.to_mesh(o.data);bm.free();o.data.update()
o['boas_panel_id_map']=json.dumps(labels,ensure_ascii=False)
o['boas_v15_changes']='Armação A/B/C, teto, cantos e painel posterior com contornos compartilhados; vãos abertos e batentes ligados.'
s.name='HILUX | carroceria isolada v15';s['boas_revision_parent']=source.relative_to(r).as_posix();s['boas_v15_applied']=True
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            sp=area.spaces.active;sp.shading.color_type='OBJECT';sp.shading.show_cavity=False;sp.shading.show_shadows=False
            sp.region_3d.view_rotation=(Vector((0,.12,1.13))-Vector((7,-8,4.1))).to_track_quat('-Z','Y')
            sp.region_3d.view_location=(0,.12,1.13);sp.region_3d.view_distance=5.3
bpy.context.view_layer.update()
bpy.data.libraries.write(str(out),{s},path_remap='RELATIVE',fake_user=True,compress=True)
report={'asset_id':'vehicle-rondesp-pickup','file':out.relative_to(r).as_posix(),'scene':s.name,'parent':source.relative_to(r).as_posix(),
    'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'status':'candidate','authoring_mode':'body_only','body_mesh':o.name,
    'removed_components':retire_names,'removed_faces':removed,'new_components':new,
    'base_vertices':len(o.data.vertices),'base_faces':len(o.data.polygons),'visible_meshes':[ob.name for ob in s.objects if ob.type=='MESH' and ob.visible_get()],
    'source_reopened':False,'visual_review':'pending','runtime_exported':False,'rig_applied':False,
    'reference_ids':['hilux-2024-std-dealer-side','hilux-srx-user-rear'],
    'notes':['Contornos autorais candidatos, não medidas de fábrica.','Armação sem portas, rodas, chassi, vidros ou cobertura policial; conjuntos reservados preservados.','Sem npm, testes, build, exportação runtime ou commit.','Contornos da cabine construídos com estações comuns antes da solda.']}
rp=r/'docs/reports/blender/hilux_carroceria_v15.json';rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def reopen():
    bpy.ops.wm.open_mainfile(filepath=str(out));data=json.loads(rp.read_text(encoding='utf-8'));data['source_reopened']=True
    rp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');return None
bpy.app.timers.register(reopen,first_interval=.5)
