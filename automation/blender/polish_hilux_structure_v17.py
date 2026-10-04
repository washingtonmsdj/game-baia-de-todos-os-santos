"""V17: conexões reais da chapa, sem fechar vãos funcionais ou a junta da caçamba.

Executar somente pela sessão MCP visível. Preserva V16 e componentes reservados.
As curvas e espessuras são interpretação candidata, não medição industrial.
"""
import ast, bpy, bmesh, collections, hashlib, json, math
from pathlib import Path
from mathutils import Vector
from mathutils.kdtree import KDTree

r = Path(__file__).resolve().parents[2]
s = bpy.context.scene
catalog = json.loads((r/'world/vehicles/catalog.json').read_text(encoding='utf-8'))
asset = next(v for v in catalog['vehicles'] if v['asset_id']=='vehicle-rondesp-pickup')
source = r/asset['authoring_base']['file']
out = r/'blender/assets/vehicles/rondesp-pickup/hilux_carroceria_v17.blend'
assert not bpy.app.background and source.name=='hilux_carroceria_v16.blend'
assert Path(bpy.data.filepath).resolve()==source.resolve() and not out.exists()
assert hashlib.sha256(source.read_bytes()).hexdigest()==asset['authoring_base']['sha256']
o = s.objects['HILUX | CARROCERIA PRINCIPAL']
checkpoint = r/'artifacts/vehicles/rondesp/pre-v17-visible-session.blend'
assert not checkpoint.exists()
bpy.data.libraries.write(str(checkpoint), {s}, path_remap='RELATIVE', compress=True)
labels = json.loads(o['boas_panel_id_map'])
bm = bmesh.new(); bm.from_mesh(o.data)
fl = bm.faces.layers.int.get('boas_panel_id')
deform = bm.verts.layers.deform.verify()
mat = list(o.data.materials).index(bpy.data.materials['RDP01 | Pintura marrom Rondesp'])
new = []

def boundary(panel):
    counts = collections.Counter(e for f in bm.faces if f[fl]==panel for e in f.edges)
    return [e for e,n in counts.items() if n==1]

def contour(panel, predicate, axis):
    return sorted({v for e in boundary(panel) for v in e.verts if predicate(v.co)}, key=lambda v:v.co[axis])

def coords(vs): return [v.co.copy() for v in vs]

def sample(points, t, axis):
    q = points[0][axis]+t*(points[-1][axis]-points[0][axis])
    if t<=0: return points[0].copy()
    if t>=1: return points[-1].copy()
    for a,b in zip(points,points[1:]):
        if a[axis]-1e-7<=q<=b[axis]+1e-7:
            return a.lerp(b, (q-a[axis])/max(b[axis]-a[axis],1e-10))
    raise RuntimeError('Contorno sem segmento para a amostra')

def strip(name, rows, normal):
    g = o.vertex_groups.new(name='HILUX17 | '+name)
    labels[str(g.index+1)] = g.name; new.append(g.name)
    vv = [[bm.verts.new(p) for p in row] for row in rows]
    for row in vv:
        for v in row: v[deform][g.index]=1.
    for a,b in zip(vv,vv[1:]):
        for j in range(len(a)-1):
            f=bm.faces.new([a[j],b[j],b[j+1],a[j+1]])
            f[fl]=g.index+1; f.material_index=mat; f.smooth=True
            f.normal_update()
            if f.normal.dot(Vector(normal))<0: f.normal_flip()
    return g.index+1

# Capturar bordas antes de retirar exclusivamente os painéis substituídos.
bed_fore = coords(contour(96,lambda p:abs(p.y-1.165)<1e-6,2))
head_top = coords(contour(103,lambda p:abs(p.y-1.153)<1e-6 and abs(p.z-1.306)<1e-6,0))
hood_aft = coords(contour(1,lambda p:abs(p.y+.975)<1e-6,0))
cab_bottom = coords(contour(87,lambda p:abs(p.z-.489)<1e-6 and p.y>=-.895-1e-6,1))
floor_back = coords(contour(49,lambda p:abs(p.y-1.135)<1e-6,0))
cab_back = coords(contour(92,lambda p:abs(p.z-.489)<1e-6,0))
assert len(bed_fore)==37 and len(head_top)>60 and len(hood_aft)>30
assert len(cab_bottom)>40 and len(floor_back)>10 and len(cab_back)>20

retire={19,75,76,15,104}
old=[f for f in bm.faces if f[fl] in retire]
removed=len(old); bmesh.ops.delete(bm,geom=old,context='FACES')

# A flange da grade antiga incluía parte da abertura do farol: retirar somente
# sua duplicação, mantendo a flange óptica e a chapa exterior.
duplicate_flange={f for e in bm.edges if len(e.link_faces)>2
    and {f[fl] for f in e.link_faces}=={77,78,108}
    for f in e.link_faces if f[fl]==78}
duplicate_flange_count=len(duplicate_flange)
bmesh.ops.delete(bm,geom=list(duplicate_flange),context='FACES')

# Frente externa da cabeceira, ligada pelo retorno superior à face interna.
# O fecho anterior terminava na parede interna e gerava uma junção tripla.
fractions=[p.x/head_top[-1].x for p in head_top]
head_rows=[]
for p in bed_fore:
    head_rows.append([Vector((p.x*u,1.153,p.z)) for u in fractions])
head_rows[-1]=head_top
strip('Cabeceira externa com retorno superior ligado',head_rows,(0,-1,0))
strip('Retorno lateral cabeceira sem juncao tripla',
    [[p.lerp(Vector((p.x,1.153,p.z)),j/8) for j in range(9)] for p in bed_fore],(1,0,0))

# Seção de soleira em um percurso contínuo: cabine -> dobra inferior -> piso.
# A seção anterior fazia uma segunda lâmina passar por baixo da armação.
floor_ys=[v.co.y for e in boundary(49) for v in e.verts if abs(v.co.x-.793)<1e-6]
ys=sorted(set([p.y for p in cab_bottom]+[y for y in floor_ys if cab_bottom[0].y<=y<=cab_bottom[-1].y]))
profile=[(.830,.489),(.831,.480),(.824,.466),(.810,.465),(.801,.470),(.793,.485)]
rows=[]
for y in ys:
    t=(y-cab_bottom[0].y)/(cab_bottom[-1].y-cab_bottom[0].y)
    edge=sample(cab_bottom,t,1); dx=edge.x-.830
    rows.append([Vector((x+dx*(x-.793)/(.830-.793),y,z)) for x,z in profile])
strip('Soleira continua da cabine ao piso',rows,(1,0,0))

# A pequena transição do assoalho ao painel posterior segue as duas bordas.
us=sorted(set([p.x/floor_back[-1].x for p in floor_back]+[p.x/cab_back[-1].x for p in cab_back]))
strip('Encontro assoalho painel posterior',
    [[sample(floor_back,u,0).lerp(sample(cab_back,u,0),j/4) for j in range(5)] for u in us],(0,0,1))

# Cowl ligado ao capô e ao pé do para-brisa, sem a chapa preta solta anterior.
strip('Cowl continuo na base do parabrisa',
    [[p.lerp(Vector((.803*p.x/hood_aft[-1].x,-.970,1.326)),j/4) for j in range(5)] for p in hood_aft],(0,0,1))

# A tampa externa usa as mesmas estações das dobras já existentes; a malha
# antiga tinha 28 linhas em Z e as dobras tinham 40, deixando todos os nós soltos.
for fn in ast.parse((r/'automation/blender/rebuild_hilux_reference_v06.py').read_text(encoding='utf-8')).body:
    if isinstance(fn,ast.FunctionDef) and fn.name=='interp':
        exec(compile(ast.Module(body=[fn],type_ignores=[]),'secoes-v06','exec'),globals())
def gate_width(z):
    return interp([(.535,.800),(.62,.825),(.69,.831),(.80,.820),(.90,.817),
        (1.03,.839),(1.16,.849),(1.24,.828),(1.285,.799)],z)-.004
strip('Tampa externa ligada a todas as dobras',
    [[Vector((gate_width(z)*j/40,2.789-.045*(j/40)**4,z)) for j in range(41)]
        for z in [.535+.75*i/40 for i in range(41)]],(0,1,0))

# Compatibilizar amostras nas bordas: dividir no ponto existente e soldar
# somente pontos coincidentes a 20 micrômetros. Não aproxima juntas físicas.
bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000004)
splits=[]
for iteration in range(5):
    bm.verts.ensure_lookup_table(); bm.verts.index_update(); bm.edges.ensure_lookup_table()
    kd=KDTree(len(bm.verts))
    for v in bm.verts: kd.insert(v.co,v.index)
    kd.balance(); jobs=[]
    for e in bm.edges:
        if len(e.link_faces)!=1: continue
        a,b=e.verts; d=b.co-a.co; length=d.length
        if length<1e-7: continue
        hits=[]
        for co,i,_ in kd.find_range((a.co+b.co)/2,length/2+.00002):
            v=bm.verts[i]
            if v in e.verts or not v.link_faces: continue
            t=(co-a.co).dot(d)/(length*length)
            if .00001<t<.99999 and (co-a.co-d*t).length<.00002:
                hits.append((t,v.co.copy()))
        if hits: jobs.append((e,a,sorted(hits,key=lambda p:p[0])))
    if not jobs: break
    count=0
    for e,a,hits in jobs:
        end=e.other_vert(a)
        last=0.
        for t,co in hits:
            if t-last<1e-6: continue
            _,nv=bmesh.utils.edge_split(e,a,(t-last)/(1-last))
            nv.co=co; e=next(edge for edge in nv.link_edges if end in edge.verts)
            a=nv; last=t; count+=1
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000021)
    splits.append(count)

bad=[f for f in bm.faces if f.calc_area()<1e-10]
if bad: bmesh.ops.delete(bm,geom=bad,context='FACES')
loose=[v for v in bm.verts if not v.link_faces]
if loose: bmesh.ops.delete(bm,geom=loose,context='VERTS')
bm.normal_update()
multi=[e for e in bm.edges if len(e.link_faces)>2]
if multi:
    diagnostics=[{'panels':[labels[str(f[fl])] for f in e.link_faces],
        'points':[list(v.co) for v in e.verts]} for e in multi]
    (r/'artifacts/vehicles/rondesp/v17-join-diagnostics.json').write_text(
        json.dumps(diagnostics,ensure_ascii=False,indent=2),encoding='utf-8')
assert not multi, 'Junções triplas remanescentes: '+str(len(multi))
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))

# Orientar cada ilha a partir de uma chapa externa identificada.
positive={1:Vector((0,0,1)),96:Vector((1,0,0)),49:Vector((0,0,1)),21:Vector((0,-1,0))}
positive.update({int(k):Vector((0,1,0)) for k,v in labels.items() if v=='HILUX17 | Tampa externa ligada a todas as dobras'})
pending=set(bm.faces)
while pending:
    seed=next(iter(pending)); stack=[seed]; pending.remove(seed); island=[]
    while stack:
        f=stack.pop(); island.append(f)
        for e in f.edges:
            for other in e.link_faces:
                if other in pending: pending.remove(other); stack.append(other)
    for panel,normal in positive.items():
        selected=[f for f in island if f[fl]==panel]
        if selected:
            if sum(f.normal.dot(normal)*f.calc_area() for f in selected)<0:
                for f in island: f.normal_flip()
            break
bm.normal_update()
assert not any(len(e.link_faces)==2 and not e.is_contiguous for e in bm.edges)
for e in bm.edges:
    if len(e.link_faces)==2:
        # Conserva dobras anteriores; a face exterior não herda uma quina de
        # uma orientação invertida que existia antes desta revisão.
        if e.calc_face_angle(0)>math.radians(55): e.smooth=False
        if any(f[fl] in {77,78} for f in e.link_faces) and len({f[fl] for f in e.link_faces})>1: e.smooth=False
bm.to_mesh(o.data); bm.free(); o.data.update()
o['boas_panel_id_map']=json.dumps(labels,ensure_ascii=False)
o['boas_v17_changes']='Cabeceira externa, soleiras, assoalho posterior, cowl, tampa e flanges corrigidos; bordas compatibilizadas e orientação coerente.'
s.name='HILUX | carroceria isolada v17'
s['boas_revision_parent']=source.relative_to(r).as_posix(); s['boas_v17_structure_applied']=True
bpy.context.view_layer.update()
bpy.data.libraries.write(str(out),{s},path_remap='RELATIVE',fake_user=True,compress=True)
rp=r/'docs/reports/blender/hilux_carroceria_v17.json'
report={'asset_id':'vehicle-rondesp-pickup','file':out.relative_to(r).as_posix(),'parent':source.relative_to(r).as_posix(),
    'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'scene':s.name,'status':'candidate','authoring_mode':'body_only',
    'body_mesh':o.name,'new_components':new,'removed_faces':removed,'duplicate_flange_faces_removed':duplicate_flange_count,
    'boundary_splits_per_pass':splits,'base_vertices':len(o.data.vertices),'base_faces':len(o.data.polygons),
    'visible_meshes':[ob.name for ob in s.objects if ob.type=='MESH' and ob.visible_get()],
    'source_reopened':False,'visual_review':'pending','runtime_exported':False,'rig_applied':False,
    'reference_ids':['hilux-2024-std-dealer-side','hilux-srx-user-rear','hilux-std-stock-front'],
    'notes':['Uma malha com Mirror X; junta cabine/caçamba e aberturas funcionais preservadas.',
        'Geometria candidata interpretada das referências; parâmetros não representam medidas de fábrica.',
        'Portas, rodas, chassi, vidros e equipamento continuam reservados.',
        'Sem npm, testes, build, exportação runtime ou commit.']}
rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def reopen():
    bpy.ops.wm.open_mainfile(filepath=str(out))
    data=json.loads(rp.read_text(encoding='utf-8')); data['source_reopened']=True
    rp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return None
bpy.app.timers.register(reopen,first_interval=.5)
