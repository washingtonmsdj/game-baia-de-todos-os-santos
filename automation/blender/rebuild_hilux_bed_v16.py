"""V16: caçamba com superfícies e dobras conectadas, na sessão visível.

Preserva a V15, a cabine, a tampa e todos os componentes reservados. Forma
autoral candidata interpretada das referências catalogadas, sem medidas fabris.
"""
import ast,bpy,bmesh,math,json,hashlib
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
cat=json.loads((r/'world/vehicles/catalog.json').read_text(encoding='utf-8'))
vehicle=next(v for v in cat['vehicles'] if v['asset_id']=='vehicle-rondesp-pickup')
source=r/vehicle['authoring_base']['file'];out=r/'blender/assets/vehicles/rondesp-pickup/hilux_carroceria_v16.blend'
assert not bpy.app.background and source.name=='hilux_carroceria_v15.blend'
assert Path(bpy.data.filepath).resolve()==source.resolve() and not out.exists()
assert hashlib.sha256(source.read_bytes()).hexdigest()==vehicle['authoring_base']['sha256']
o=s.objects['HILUX | CARROCERIA PRINCIPAL'];labels=json.loads(o['boas_panel_id_map'])
checkpoint=r/'artifacts/vehicles/rondesp/pre-v16-visible-session.blend'
assert not checkpoint.exists()
bpy.data.libraries.write(str(checkpoint),{s},path_remap='RELATIVE',compress=True)
for fn in ast.parse((r/'automation/blender/rebuild_hilux_reference_v06.py').read_text(encoding='utf-8')).body:
    if isinstance(fn,ast.FunctionDef) and fn.name in {'interp','arch'}:
        exec(compile(ast.Module(body=[fn],type_ignores=[]),'secoes-v06','exec'),globals())
def smooth(t):
    t=max(0,min(1,t));return t*t*(3-2*t)
def pid(name):return next(int(k) for k,v in labels.items() if v==name)
retire=['HILUX06 | Lateral caçamba 1','HILUX13 | Parede interna caçamba',
    'HILUX13 | Piso caçamba e estampagem longitudinal','HILUX13 | Borda enrolada caçamba',
    'HILUX13 | Caixa roda interna integrada','HILUX13 | Face interna caixa roda',
    'HILUX13 | Cabeceira caçamba estampada','HILUX13 | Retorno superior cabeceira',
    'HILUX13 | Retorno recorte Lateral caçamba 1','HILUX14 | Dobra inferior cantos cacamba']
retired={pid(n) for n in retire}
bm=bmesh.new();bm.from_mesh(o.data);fl=bm.faces.layers.int.get('boas_panel_id');deform=bm.verts.layers.deform.verify()
old=[f for f in bm.faces if f[fl] in retired];removed=len(old)
bmesh.ops.delete(bm,geom=old,context='FACES')
mat=list(o.data.materials).index(bpy.data.materials['RDP01 | Pintura marrom Rondesp']);new=[]
def patch(name,vs,fs,normal=None):
    g=o.vertex_groups.new(name='HILUX16 | '+name);new.append(g.name);labels[str(g.index+1)]=g.name
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

# Estações únicas para lateral, borda enrolada, interior e caixas de roda.
fore,aft=1.165,2.749;axle=1.655;floor=.575
ys=sorted(set([fore+(aft-fore)*i/96 for i in range(97)]+[axle,2.178,2.180,2.190,2.550]))
nt=36
def top_z(y):
    u=(y-fore)/(aft-fore);return 1.306-.019*u**10
def bottom_z(y):return arch(y,axle)+.050*smooth((y-2.18)/.56)
def tail_width(z):
    return interp([(.535,.800),(.62,.825),(.69,.831),(.80,.820),(.90,.817),
        (1.03,.839),(1.16,.849),(1.24,.828),(1.285,.799)],z)
def outer_x(y,z):
    base=interp([(.485,.813),(.58,.848),(.73,.883),(.88,.891),(1.00,.895),
        (1.12,.899),(1.20,.880),(1.306,.831)],z)
    flare=.030*math.exp(-((y-axle)/.58)**4)*math.exp(-((z-.94)/.33)**4)
    lip=.009*math.exp(-((z-bottom_z(y))/.070)**2)*(1-smooth((abs(y-axle)-.42)/.14))
    weight=smooth((y-2.50)/(aft-2.50))
    return (base+flare+lip)*(1-weight)+tail_width(z)*weight
def inner_y(y):return y-.011*smooth((y-2.55)/(aft-2.55))
def inner_x(y,z):
    low=.807-.030*smooth((y-2.55)/(aft-2.55))
    t=max(0,min(1,(z-floor)/(top_z(y)-.014-floor)))
    return low*(1-t)+(outer_x(y,top_z(y))-.032)*t
def well_z(y):
    if y>=2.19:return floor
    t=max(0,min(1,(y-fore)/(2.19-fore)))
    return floor+.420*math.sin(math.pi*t)**1.45
def floor_z(x):
    rib=.004*(.5+.5*math.cos(math.tau*x/.12))**8
    return floor+rib*(1-smooth((x-.510)/.055))
outer_rows=[];rim_rows=[];wall_rows=[];core_rows=[];well_face_rows=[];well_roof_rows=[]
for y in ys:
    lo,hi=bottom_z(y),top_z(y);xo=outer_x(y,hi);zi=hi-.014
    outer_rows.append([(outer_x(y,lo+(hi-lo)*j/nt),y,lo+(hi-lo)*j/nt) for j in range(nt+1)])
    rim_rows.append([(xo-.032*math.sin(math.pi*j/16),y+(inner_y(y)-y)*math.sin(math.pi*j/16),
        hi-.014*(1-math.cos(math.pi*j/16))) for j in range(9)])
    h=well_z(y);height=h-floor
    wall_rows.append([(inner_x(y,h+(zi-h)*j/nt),inner_y(y),h+(zi-h)*j/nt) for j in range(nt+1)])
    core_rows.append([(.565*j/48,inner_y(y),floor_z(.565*j/48)) for j in range(49)])
    well_face_rows.append([(.565+.028*(1-math.cos(math.pi*j/12)),inner_y(y),floor+height*math.sin(math.pi*j/12)) for j in range(7)])
    well_roof_rows.append([(.593+(inner_x(y,h)-.593)*j/16,inner_y(y),h+.008*math.sin(math.pi*j/16)*height/.420) for j in range(17)])
strip('Lateral cacamba estampagem suave',outer_rows,(1,0,0))
strip('Borda enrolada ligada aos dois lados',rim_rows,(0,0,1))
strip('Parede interna ligada a caixa roda',wall_rows,(-1,0,0))
strip('Piso longitudinal continuo',core_rows,(0,0,1))
strip('Face caixa roda com transicao no piso',well_face_rows,(-1,0,0))
strip('Teto caixa roda ligado a parede',well_roof_rows,(0,0,1))

# Cabeceira segue a largura da própria parede, com pé ligado ao piso.
front_floor=core_rows[0]+well_face_rows[0][1:]+well_roof_rows[0][1:]
fractions=[p[0]/inner_x(fore,floor) for p in front_floor]
head_rows=[]
for j in range(nt+1):
    t=j/nt;z=floor+(top_z(fore)-.014-floor)*t;w=inner_x(fore,z)
    head_rows.append([(w*u,fore,z+(front_floor[i][2]-floor)*(1-t)) for i,u in enumerate(fractions)])
strip('Cabeceira alinhada ao piso e laterais',head_rows,(0,1,0))
head_roll=[]
for j in range(9):
    a=math.pi*j/16;w=inner_x(fore,top_z(fore)-.014)+.032*(1-math.cos(a))
    head_roll.append([(w*u,fore-.012*math.sin(a),top_z(fore)-.014+.014*(1-math.cos(a))) for u in fractions])
strip('Dobra superior cabeceira arredondada',head_roll,(0,0,1))
# Fechos finos da borda lateral na frente e na traseira usam os mesmos nós.
for name,index,normal in [('Fecho dianteiro lateral',0,(0,-1,0)),('Batente posterior lateral',-1,(0,1,0))]:
    strip(name,[[Vector(outer_rows[index][j]).lerp(Vector(wall_rows[index][j]),k/8) for k in range(9)] for j in range(nt+1)],normal)
strip('Canto cabeceira borda lateral',[[Vector(head_roll[j][-1]).lerp(Vector(rim_rows[0][8-j]),k/6) for k in range(7)] for j in range(9)],(0,-1,1))
# A dobra do recorte acompanha o arco, sem uma lâmina independente pendurada.
strip('Dobra continua arco e borda inferior',[[Vector(row[0])+Vector((-.025*j/8,0,-.002*math.sin(math.pi*j/8))) for j in range(9)] for row in outer_rows],(0,0,-1))

bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00006)
bad=[f for f in bm.faces if f.calc_area()<1e-10]
if bad:bmesh.ops.delete(bm,geom=bad,context='FACES')
loose=[v for v in bm.verts if not v.link_faces]
if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
newids={int(k) for k,v in labels.items() if v.startswith('HILUX16 |')}
nf=[f for f in bm.faces if f[fl] in newids]
bmesh.ops.recalc_face_normals(bm,faces=nf);bm.normal_update()
outfaces=[f for f in nf if labels[str(f[fl])]=='HILUX16 | Lateral cacamba estampagem suave']
if sum(f.normal.x*f.calc_area() for f in outfaces)<0:
    for f in nf:f.normal_flip()
foldids={int(k) for k,v in labels.items() if v.startswith('HILUX16 |') and
    any(n in v for n in ['Fecho','Batente','Dobra continua'])}
for e in bm.edges:
    if len(e.link_faces)!=2:continue
    ids={f[fl] for f in e.link_faces}
    if ids.intersection(newids) and (e.calc_face_angle(0)>math.radians(55) or (len(ids)>1 and ids.intersection(foldids))):e.smooth=False
bm.to_mesh(o.data);bm.free();o.data.update()
o['boas_panel_id_map']=json.dumps(labels,ensure_ascii=False)
o['boas_v16_changes']='Caçamba com piso, caixa de roda, paredes, cabeceira e bordas em contornos comuns; chapa lateral regularizada.'
s.name='HILUX | carroceria isolada v16';s['boas_revision_parent']=source.relative_to(r).as_posix();s['boas_v16_bed_applied']=True
bpy.context.view_layer.update()
bpy.data.libraries.write(str(out),{s},path_remap='RELATIVE',fake_user=True,compress=True)
report={'asset_id':'vehicle-rondesp-pickup','file':out.relative_to(r).as_posix(),'scene':s.name,'parent':source.relative_to(r).as_posix(),
    'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'status':'candidate','authoring_mode':'body_only','body_mesh':o.name,
    'removed_components':retire,'removed_faces':removed,'new_components':new,
    'base_vertices':len(o.data.vertices),'base_faces':len(o.data.polygons),
    'visible_meshes':[ob.name for ob in s.objects if ob.type=='MESH' and ob.visible_get()],
    'source_reopened':False,'visual_review':'pending','runtime_exported':False,'rig_applied':False,
    'reference_ids':['hilux-2024-std-dealer-side','hilux-srx-user-rear'],
    'notes':['Forma, raios e espessura são parâmetros autorais candidatos, não medidas de fábrica.',
        'Uma malha visível com Mirror X; junta física cabine/caçamba preservada.',
        'Cabine e tampa preservadas; portas, rodas, chassi e equipamentos separados e ocultos.',
        'Sem npm, testes, build, exportação runtime ou commit.']}
rp=r/'docs/reports/blender/hilux_carroceria_v16.json';rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def reopen():
    bpy.ops.wm.open_mainfile(filepath=str(out));data=json.loads(rp.read_text(encoding='utf-8'));data['source_reopened']=True
    rp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');return None
bpy.app.timers.register(reopen,first_interval=.5)
