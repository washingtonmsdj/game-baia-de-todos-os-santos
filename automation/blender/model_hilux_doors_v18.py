"""Quatro folhas ajustadas à V17, com estrutura interna e dobradiças independentes.

Aplicar uma vez pelo MCP na única janela visível. A carroceria permanece intacta.
Medidas das folhas, estampagens, ferragens e folgas são parâmetros candidatos.
"""
import ast, bpy, bmesh, collections, hashlib, json, math, struct
from pathlib import Path
from mathutils import Vector, Matrix
from mathutils.geometry import delaunay_2d_cdt

r = Path(__file__).resolve().parents[2]
s = bpy.context.scene
catalog = json.loads((r / 'world/vehicles/catalog.json').read_text(encoding='utf8'))
vehicle = next(v for v in catalog['vehicles'] if v['asset_id'] == 'vehicle-rondesp-pickup')
source = r / vehicle['authoring_base']['file']
out = r / 'blender/assets/vehicles/rondesp-pickup/hilux_portas_v18.blend'
assert not bpy.app.background and Path(bpy.data.filepath).resolve() == source.resolve()
assert source.name == 'hilux_carroceria_v17.blend' and not out.exists()
assert hashlib.sha256(source.read_bytes()).hexdigest() == vehicle['authoring_base']['sha256']
assert not s.get('boas_v18_doors_applied')
before = json.loads((r / 'artifacts/vehicles/rondesp/v18-doors-before.json').read_text(encoding='utf8'))
body = s.objects['HILUX | CARROCERIA PRINCIPAL']
root = s.objects['RDP01_ROOT | viatura']

def fingerprint(ob):
    h = hashlib.sha256()
    for v in ob.data.vertices: h.update(struct.pack('<3d', *v.co))
    for p in ob.data.polygons:
        h.update(struct.pack('<I', len(p.vertices)))
        h.update(struct.pack('<' + 'I' * len(p.vertices), *p.vertices))
    return h.hexdigest()

assert fingerprint(body) == before['body_hash']
# Só funções geométricas; nunca executar novamente scripts antigos de mutação.
for file, names in [
    ('rebuild_hilux_reference_v06.py', {'interp', 'sidewidth'}),
    ('rebuild_hilux_cab_v15.py', {'smooth', 'roof_width', 'roof_edge_z', 'cab_side', 'radius', 'rear_y', 'cab_x', 'rounded'}),
    ('finish_hilux_cab_v15.py', {'regular_x'}),
]:
    for fn in ast.parse((r / 'automation/blender' / file).read_text(encoding='utf8')).body:
        if isinstance(fn, ast.FunctionDef) and fn.name in names:
            exec(compile(ast.Module(body=[fn], type_ignores=[]), file, 'exec'), globals())

def field(y, z):
    x = regular_x(y, z)
    if 1.331 < z < roof_edge_z(y) - .017 and y < -.16:
        fy = -.970 + .632 * (z - 1.326) / .442
        fx = .803 - .092 * (z - 1.326) / .442
        w = 1 - smooth((y - fy - .14) / .15)
        x = x * (1 - w) + fx * w
    return x

def area(loop):
    return sum(a.x * b.y - b.x * a.y for a, b in zip(loop, loop[1:] + loop[:1])) / 2

def inside(p, loop):
    yes = False
    for a, b in zip(loop, loop[1:] + loop[:1]):
        if (a.y > p.y) != (b.y > p.y) and p.x < (b.x - a.x) * (p.y - a.y) / (b.y - a.y) + a.x:
            yes = not yes
    return yes

def inset(loop, distance):
    result = []
    for i, p in enumerate(loop):
        a = (p - loop[i - 1]).normalized()
        b = (loop[(i + 1) % len(loop)] - p).normalized()
        n1, n2 = Vector((-a.y, a.x)), Vector((-b.y, b.x))
        bis = (n1 + n2).normalized()
        result.append(p + bis * distance / max(.35, bis.dot(n1)))
    return result

def dense(loop, spacing=.026):
    result = []
    for a, b in zip(loop, loop[1:] + loop[:1]):
        n = max(1, math.ceil((b - a).length / spacing))
        result.extend(a.lerp(b, i / n) for i in range(n))
    return result

def border(label):
    data = before['borders']['HILUX15 | Batente ' + label + ' ligado ao contorno']
    adj = collections.defaultdict(list)
    for a, b in data['edges']: adj[a].append(b); adj[b].append(a)
    loops, seen = [], set()
    for start in adj:
        if start in seen: continue
        loop, previous, cur = [], None, start
        while True:
            loop.append(Vector(data['vertices'][str(cur)])); seen.add(cur)
            nxt = next(v for v in adj[cur] if v != previous)
            previous, cur = cur, nxt
            if cur == start: break
        loops.append(loop)
    outer = max(loops, key=lambda loop: sum(p.x for p in loop) / len(loop))
    loop = [Vector((p.y, p.z)) for p in outer]
    if area(loop) < 0: loop.reverse(); outer.reverse()
    return loop, outer

gray = (.53, .55, .58, 1)
paint = bpy.data.materials['RDP01 | Pintura marrom Rondesp']
black = bpy.data.materials['RDP01 | Polímero preto']
metal = bpy.data.materials['RDP01 | Metal acetinado']
edit = bpy.data.collections.new('HILUX | PORTAS EM EDICAO')
s.collection.children.link(edit)
changed, added, doors = [], [], []
meshes = {}

def move_to(ob, col):
    for old in list(ob.users_collection): old.objects.unlink(ob)
    col.objects.link(ob)
    ob.hide_viewport = False; ob.hide_render = False; ob.hide_set(False)

def mesh_object(name, vs, fs, col, parent, side=1, material=paint, color=gray, existing=None):
    data = bpy.data.meshes.new(name + ' | malha V18')
    origin = parent.location if parent != root else Vector((0, 0, 0))
    data.from_pydata([Vector((side * p[0], p[1], p[2])) - origin for p in vs], [],
                     [tuple(f) if side == 1 else tuple(reversed(f)) for f in fs])
    data.materials.append(material)
    ob = existing or bpy.data.objects.new(name, data)
    ob.data = data
    ob.modifiers.clear()
    ob.parent = parent; ob.matrix_parent_inverse = Matrix.Identity(4); ob.matrix_basis = Matrix.Identity(4)
    move_to(ob, col)
    ob.color = color
    ob['boas_asset_id'] = 'vehicle-rondesp-pickup'
    ob['boas_component'] = 'doors'
    ob['boas_shape_status'] = 'candidate; dimensoes de modelagem, sem levantamento industrial'
    ob['boas_reference_ids'] = 'hilux-2024-std-dealer-side;hilux-srx-user-side'
    bm = bmesh.new(); bm.from_mesh(data)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-7)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces)); bm.normal_update()
    # Suavizar as chapas; preservar as dobras mais fechadas.
    for f in bm.faces: f.smooth = True
    for e in bm.edges:
        if len(e.link_faces) == 2 and e.calc_face_angle() > math.radians(38): e.smooth = False
    bm.to_mesh(data); bm.free(); data.update()
    (changed if existing else added).append(ob.name)
    return ob

def solid_box(name, center, dims, col, parent, side, material=metal, bevel=.003, color=(.23, .24, .25, 1), existing=None):
    cx, cy, cz = center; dx, dy, dz = [v / 2 for v in dims]
    vs = [(cx + a * dx, cy + b * dy, cz + c * dz) for a, b, c in
          [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
    fs = [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    ob = mesh_object(name, vs, fs, col, parent, side, material, color, existing)
    mod = ob.modifiers.new('Raios de acabamento', 'BEVEL'); mod.width = bevel; mod.segments = 5
    mod = ob.modifiers.new('Normais da ferragem', 'WEIGHTED_NORMAL'); mod.keep_sharp = True
    return ob

def tube(name, points, radius, col, parent, side, closed=False, material=black, color=(.055,.059,.064,1)):
    origin = parent.location if parent != root else Vector((0,0,0))
    data = bpy.data.curves.new(name, 'CURVE'); data.dimensions = '3D'; data.resolution_u = 1
    data.bevel_depth = radius; data.bevel_resolution = 3
    spl = data.splines.new('POLY'); spl.points.add(len(points) - 1)
    for point, p in zip(spl.points, points): point.co = (*(Vector((side*p[0],p[1],p[2])) - origin), 1)
    spl.use_cyclic_u = closed
    ob = bpy.data.objects.new(name, data); col.objects.link(ob)
    ob.parent = parent; ob.matrix_parent_inverse = Matrix.Identity(4); ob.color = color; data.materials.append(material)
    ob['boas_component'] = 'door_seal'; added.append(ob.name)
    return ob

def skin(vs, fs, outline, holes, project, reverse=False, step=.024):
    pts, edges = [], []
    for loop in [outline] + holes:
        base = len(pts); pts.extend(loop)
        edges.extend((base+i,base+(i+1)%len(loop)) for i in range(len(loop)))
    lo = Vector((min(p.x for p in outline),min(p.y for p in outline)))
    hi = Vector((max(p.x for p in outline),max(p.y for p in outline)))
    ny, nz = math.ceil((hi.x-lo.x)/step), math.ceil((hi.y-lo.y)/step)
    for i in range(1,ny):
        for j in range(1,nz):
            p = Vector((lo.x+(hi.x-lo.x)*i/ny,lo.y+(hi.y-lo.y)*j/nz))
            if inside(p,outline) and not any(inside(p,h) for h in holes): pts.append(p)
    coords, _, faces, *_ = delaunay_2d_cdt(pts,edges,[],1,1e-8)
    base = len(vs); vs.extend(project(p) for p in coords)
    for f in faces:
        center = sum((coords[i] for i in f),Vector((0,0)))/len(f)
        if not inside(center,outline) or any(inside(center,h) for h in holes): continue
        if len(f)==3 and abs((coords[f[1]]-coords[f[0]]).cross(coords[f[2]]-coords[f[0]]))<2e-10: continue
        fs.append(tuple(base+i for i in (reversed(f) if reverse else f)))

def strip(vs, fs, rows):
    n = len(rows[0]); base = len(vs); vs.extend(p for row in rows for p in row)
    for i in range(len(rows)-1):
        for j in range(n-1): fs.append((base+i*n+j,base+(i+1)*n+j,base+(i+1)*n+j+1,base+i*n+j+1))

def door_shape(label):
    aperture, original = border('dianteiro' if label=='dianteira' else 'traseiro')
    outline = dense(inset(aperture,.0035))
    win_points = ([(-.869,1.324),(-.741,1.451),(-.386,1.694),(-.237,1.713),(.071,1.714),(.069,1.324)]
        if label=='dianteira' else [(.281,1.324),(.286,1.715),(.866,1.713),(.941,1.655),(.997,1.538),(1.025,1.324)])
    window = rounded(win_points,rad=.014,n=8)
    if area(window)<0: window.reverse()
    window = dense(window)
    # O bordo segue a chapa fixa; coroa suave apenas longe das juntas.
    def distance(p):
        return min((p-(a+(b-a)*max(0,min(1,(p-a).dot(b-a)/(b-a).length_squared)))).length
                   for a,b in zip(aperture,aperture[1:]+aperture[:1]))
    hy = -.065 if label=='dianteira' else .866
    def outside(p):
        y,z=p
        crown=.006*smooth(distance(p)/.10)*(1-smooth((z-1.22)/.13))
        handle_recess=.009*math.exp(-((y-hy)/.123)**6-((z-1.155)/.037)**4)
        return Vector((field(y,z)+.0004+crown-handle_recess,y,z))
    def depth(z): return .057*(1-smooth((z-1.24)/.10))+.019*smooth((z-1.24)/.10)
    def inner(p):
        q=outside(p);q.x-=depth(p.y)
        q.x+=.006*math.exp(-((p.y-.97)/.080)**4)*smooth(distance(p)/.08)
        q.x-=.004*math.exp(-((p.y-.62)/.042)**4)*smooth(distance(p)/.08)
        return q
    # Service holes are in the inner stamping; no trim panel masks the structure.
    a,b=(-.77,-.16) if label=='dianteira' else (.36,.94)
    service=rounded([(a,.710),(b,.710),(b,.993),(a,.993)],rad=.030,n=8)
    if area(service)<0:service.reverse()
    service=dense(service)
    vs,fs=[],[]
    skin(vs,fs,outline,[window],outside)
    skin(vs,fs,outline,[window,service],inner,True)
    # Hemmed perimeter and narrow window return form a real volume.
    for loop in [outline,window]:
        strip(vs,fs,[[outside(p).lerp(inner(p),j/4) for j in range(5)] for p in loop+[loop[0]]])
    # Rolled return on the internal service opening, clear of the outer skin.
    strip(vs,fs,[[inner(p),inner(p)+Vector((.005,0,0))] for p in service+[service[0]]])
    return vs,fs,outline,window,outside,inner,hy

fixed = bpy.data.collections.new('HILUX | FERRAGENS FIXAS DAS PORTAS'); edit.children.link(fixed)
for label in ['dianteira','traseira']:
    vs,fs,outline,window,outside,inner,hy=door_shape(label)
    meshes[label]=(vs,fs)
    for side in [-1,1]:
        handed = 'esquerda' if side==-1 else 'direita'
        col = bpy.data.collections.new('HILUX | Porta '+label+' '+handed); edit.children.link(col)
        pivot = s.objects[f'RDP01 | Pivô porta {label} {side:+}']
        # Eixo candidato situado à frente do bordo para permitir abertura externa.
        pivot.animation_data_clear(); pivot.parent=root; pivot.matrix_parent_inverse=Matrix.Identity(4)
        pivot.location=(side*(.907 if label=='dianteira' else .912),-.962 if label=='dianteira' else .208,.985)
        pivot.rotation_euler=(0,0,0);pivot.scale=(1,1,1);pivot.empty_display_type='PLAIN_AXES';pivot.empty_display_size=.07
        move_to(pivot,col)
        # Caixilho antigo permanece reservado; migração explícita para folha única.
        for child in list(pivot.children):
            if 'Caixilho' in child.name:
                child.parent=root;child.matrix_parent_inverse=Matrix.Identity(4);child.matrix_basis=Matrix.Identity(4)
                child['boas_v18_role']='legacy_reserved_frame; replaced by integrated door shell'
        ob = s.objects[f'RDP01 | HILUX06 | Porta {label} {side}']
        ob.animation_data_clear()
        mesh_object(ob.name,vs,fs,col,pivot,side,existing=ob)
        ob['boas_role']='moving_door_shell'
        ob['boas_door_name']='Porta '+label+' '+handed
        ob['boas_v18_gap_candidate_m']=.0035
        ob['boas_v18_thickness_candidate_m']=.057
        pivot['abertura_graus']=0.0
        pivot.id_properties_ui('abertura_graus').update(min=0,max=70,soft_min=0,soft_max=70,
            description='Abertura independente da porta: 0 fechada, 70 aberta (graus).')
        pivot['boas_hinge_axis']='local Z; opposite rotation signs at mirrored sides'
        pivot['boas_opening_status']='candidate; movement review pending'
        pivot['boas_door_shell']=ob.name
        driver=pivot.driver_add('rotation_euler',2).driver
        driver.type='SCRIPTED';var=driver.variables.new();var.name='graus';var.type='SINGLE_PROP'
        var.targets[0].id=pivot;var.targets[0].data_path='["abertura_graus"]'
        driver.expression=f'{-side}*min(70,max(0,graus))*0.017453292519943295'
        pivot.lock_location=(True,True,True);pivot.lock_rotation=(True,True,True);pivot.lock_scale=(True,True,True)
        ob.lock_location=(True,True,True);ob.lock_rotation=(True,True,True);ob.lock_scale=(True,True,True)
        # Vedação e canal da janela acompanham a folha, sem restaurar o vidro antigo.
        tube(f'HILUX18 | Canal vidro {label} {handed}',[outside(p)+Vector((-.006,0,0)) for p in window],.003,col,pivot,side,True)
        tube(f'HILUX18 | Vedacao interna {label} {handed}',[inner(p)+Vector((-.0015,0,0)) for p in outline],.003,col,pivot,side,True)
        if label=='traseira':
            points=[Vector((field(.878+.024*t,1.330+.364*t)-.006,.878+.024*t,1.330+.364*t)) for t in [i/16 for i in range(17)]]
            tube(f'HILUX18 | Divisoria janela {handed}',points,.0075,col,pivot,side)
        handle=s.objects[f'RDP01 | HILUX06 | Maçaneta {label}{side}']
        pocket=s.objects[f'RDP01 | HILUX06 | Bolso maçaneta {label}{side}']
        x=outside(Vector((hy,1.155))).x
        solid_box(pocket.name,(x+.001,hy,1.155),(.012,.205,.047),col,pivot,side,black,.017,(.070,.073,.077,1),pocket)
        solid_box(handle.name,(x+.022,hy-.003,1.157),(.031,.165,.024),col,pivot,side,black,.010,(.043,.046,.049,1),handle)
        # Duas dobradiças: folhas fixas e móveis separadas, eixo do pino comum.
        hx=abs(pivot.location.x);hinge_y=pivot.location.y
        for number,z in enumerate([.695,1.135],1):
            solid_box(f'HILUX18 | Dobradica fixa {label} {handed} {number}',(hx-.012,hinge_y-.018,z),(.007,.047,.048),fixed,root,side,metal,.002)
            solid_box(f'HILUX18 | Dobradica movel {label} {handed} {number}',(hx-.012,hinge_y+.021,z),(.007,.054,.048),col,pivot,side,metal,.002)
            tube(f'HILUX18 | Pino dobradica {label} {handed} {number}',[(hx,hinge_y,z-.026),(hx,hinge_y,z+.026)],.006,fixed,root,side,False,metal,(.19,.20,.21,1))
        doors.append({'shell':ob.name,'pivot':pivot.name,'door':ob['boas_door_name'],'side':side,
            'opening_control':'abertura_graus','range_degrees':[0,70],'hinge_position_candidate_m':list(pivot.location),
            'children':[o.name for o in col.objects if o!=pivot]})

assert fingerprint(body)==before['body_hash']
s.name='HILUX | carroceria e portas v18'
s['boas_v18_doors_applied']=True
s['boas_authoring_mode']='body_and_doors; independent moving assemblies'
s['boas_revision_parent']=source.relative_to(r).as_posix()
s['boas_next_scope']='Refinar encaixes das portas; rodas, chassi, vidros e equipamento continuam reservados.'
for ob in s.objects:ob.select_set(False)
front=s.objects['RDP01 | HILUX06 | Porta dianteira 1'];front.select_set(True)
bpy.context.view_layer.objects.active=front
for screen in bpy.data.screens:
    for a in screen.areas:
        if a.type=='VIEW_3D':
            sp=a.spaces.active;sp.shading.color_type='OBJECT';sp.shading.show_cavity=False;sp.shading.show_shadows=False
            sp.region_3d.view_rotation=(Vector((0,.15,1.05))-Vector((7,-8,3.8))).to_track_quat('-Z','Y')
            sp.region_3d.view_location=(0,.15,1.05);sp.region_3d.view_distance=5.5
bpy.context.view_layer.update()
report={'asset_id':'vehicle-rondesp-pickup','file':out.relative_to(r).as_posix(),'scene':s.name,
    'parent':source.relative_to(r).as_posix(),'parent_sha256':vehicle['authoring_base']['sha256'],
    'status':'candidate','authoring_mode':'body_and_doors','body_hash_before':before['body_hash'],
    'body_hash_after':fingerprint(body),'body_unchanged':True,'door_assemblies':doors,
    'migrated_objects':changed,'added_objects':added,'source_reopened':False,'visual_review':'pending',
    'runtime_exported':False,'wheel_rig_applied':False,'door_rig_applied':True,
    'reference_ids':['hilux-2024-std-dealer-side','hilux-srx-user-side'],
    'notes':['Contornos derivados dos vãos efetivos da V17, com folga candidata de 3,5 mm.',
        'Uma folha integrada por porta: chapa externa, caixilho, dobra periférica e estampagem interna com abertura de serviço.',
        'Geometria simétrica, sem escala negativa nos objetos; ferragens e maçanetas acompanham o conjunto correspondente.',
        'Carroceria fixa preservada; caixilhos antigos continuam reservados e documentados como legados.',
        'Vidros, rodas, chassi, capota, inscrições e demais peças continuam ocultos.',
        'Parâmetros autorais candidatos; não representam medidas de fábrica.',
        'Sem npm, testes, build, exportação runtime ou commit.']}
rp=r/'docs/reports/blender/hilux_portas_v18.json'
rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
bpy.data.libraries.write(str(out),{s},path_remap='RELATIVE',fake_user=True,compress=True)
report['sha256']=hashlib.sha256(out.read_bytes()).hexdigest()
rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def reopen():
    bpy.ops.wm.open_mainfile(filepath=str(out));data=json.loads(rp.read_text(encoding='utf8'))
    data['source_reopened']=Path(bpy.data.filepath).resolve()==out.resolve()
    rp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');return None
bpy.app.timers.register(reopen,first_interval=.5)
print(json.dumps({'file':str(out.relative_to(r)),'doors':len(doors),'body_unchanged':True}))
