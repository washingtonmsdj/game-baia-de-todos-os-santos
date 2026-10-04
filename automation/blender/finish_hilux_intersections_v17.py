"""Acabamento V17: retopologia localizada e folga real entre tampa e caçamba."""
import ast, bpy, bmesh, collections, json, math, hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
out=r/'blender/assets/vehicles/rondesp-pickup/hilux_carroceria_v17.blend'
assert not bpy.app.background and Path(bpy.data.filepath).resolve()==out.resolve()
assert s.get('boas_v17_structure_applied') and not s.get('boas_v17_intersections_finished')
o=s.objects['HILUX | CARROCERIA PRINCIPAL'];labels=json.loads(o['boas_panel_id_map'])
checkpoint=r/'artifacts/vehicles/rondesp/pre-v17-intersections.blend'
if not checkpoint.exists():
    bpy.data.libraries.write(str(checkpoint),{s},path_remap='RELATIVE',compress=True)
else:
    expected=json.loads((r/'docs/reports/blender/hilux_carroceria_v17.json').read_text(encoding='utf-8'))['sha256']
    assert hashlib.sha256(out.read_bytes()).hexdigest()==expected and not bpy.data.is_dirty, 'Cena alterada após checkpoint'
bm=bmesh.new();bm.from_mesh(o.data);fl=bm.faces.layers.int.get('boas_panel_id')

def remesh(panel,axes,normal):
    old=[f for f in bm.faces if f[fl]==panel]
    vertices=list({v for f in old for v in f.verts});index={v:i for i,v in enumerate(vertices)}
    counts=collections.Counter(e for f in old for e in f.edges)
    edges=[e for e,n in counts.items() if n==1]
    points=[Vector((v.co[axes[0]],v.co[axes[1]])) for v in vertices]
    constraints=[tuple(index[v] for v in e.verts) for e in edges]
    def inside(p):
        yes=False
        for ia,ib in constraints:
            a,b=points[ia],points[ib]
            if (a.y>p[1])!=(b.y>p[1]) and p[0]<(b.x-a.x)*(p[1]-a.y)/(b.y-a.y)+a.x:yes=not yes
        return yes
    co,_,faces,originals,*_=delaunay_2d_cdt(points,constraints,[],1,1e-9)
    assert all(ids for ids in originals), 'Contorno projetado tem cruzamento: '+labels[str(panel)]
    mapped=[vertices[ids[0]] for ids in originals]
    triangles=[]
    for indices in faces:
        center=tuple(sum(float(co[i][axis]) for i in indices)/len(indices) for axis in range(2))
        area=abs(sum(float(co[a].x)*float(co[b].y)-float(co[b].x)*float(co[a].y)
            for a,b in zip(indices,indices[1:]+indices[:1])))/2
        if area>1e-10 and inside(center):triangles.append(indices)
    material=old[0].material_index
    bmesh.ops.delete(bm,geom=old,context='FACES_ONLY')
    for inds in triangles:
        f=bm.faces.new([mapped[i] for i in inds]);f[fl]=panel;f.material_index=material;f.smooth=True
        f.normal_update()
        if f.normal.dot(Vector(normal))<0:f.normal_flip()
    return {'old_faces':len(old),'new_faces':len(triangles),'preserved_control_vertices':len(vertices)}

# Reordenar a conectividade das duas chapas pelo seu plano de modelagem.
# Conserva pontos e contornos 3D; elimina quads que se dobravam sobre si mesmos.
remeshed={}
remeshed['fender']=remesh(70,(1,2),(1,0,0))
remeshed['front']=remesh(108,(0,2),(0,-1,0))

# O triângulo antigo do pé A atravessava a borda do cowl recém conectado.
# Sua diagonal é o limite correto para o cowl; retirar a lâmina redundante.
a=Vector((.8345,-.975,1.303));b=Vector((.803,-.970,1.326))
foot=[f for f in bm.faces if f[fl]==87 and len(f.verts)==3
    and any((v.co-a).length<1e-5 for v in f.verts) and any((v.co-b).length<1e-5 for v in f.verts)
    and min(v.co.y for v in f.verts)<-.97501]
assert len(foot)==1, 'Faces no pé A: '+str(len(foot))
bmesh.ops.delete(bm,geom=foot,context='FACES_ONLY')

# Terminação do raio do teto: o bevel anterior criou um leque microscópico
# torcido entre os dois retornos. Reconstruir o vértice comum do canto.
corner=Vector((.711,-.338,1.768))
fan=[v for v in bm.verts if (v.co-corner).length<.0018]
assert len(fan)>=7, 'Vértices no canto do teto: '+str(len(fan))
bmesh.ops.pointmerge(bm,verts=fan,merge_co=corner)

# Rearranjar a junta traseira da caçamba. A tampa interna ocupa Y=2.738;
# o batente terminava atravessando a tampa. As estações interna/externa
# convergem agora a Y=2.732: folga de 6 mm entre superfícies de autoria.
# É parâmetro candidato de montagem, registrado, não medição de fábrica.
for fn in ast.parse((r/'automation/blender/rebuild_hilux_bed_v16.py').read_text(encoding='utf-8')).body:
    if isinstance(fn,ast.FunctionDef) and fn.name in {'smooth','top_z','tail_width','outer_x','inner_y'}:
        exec(compile(ast.Module(body=[fn],type_ignores=[]),'secoes-cacamba-v16','exec'),globals())
for fn in ast.parse((r/'automation/blender/rebuild_hilux_reference_v06.py').read_text(encoding='utf-8')).body:
    if isinstance(fn,ast.FunctionDef) and fn.name in {'interp','arch'}:
        exec(compile(ast.Module(body=[fn],type_ignores=[]),'secoes-v06','exec'),globals())
fore,aft,axle=1.165,2.749,1.655
def bottom_z(y): return arch(y,axle)+.050*smooth((y-2.18)/.56)
bed_ids={96,97,98,99,100,101,102,103,105,106,107,109,110}
changed=0
for v in bm.verts:
    ids={f[fl] for f in v.link_faces}
    if not ids.intersection(bed_ids) or v.co.y<=2.55:continue
    old_y=v.co.y
    if 105 in ids:
        nominal=aft;fraction=max(0,min(1,(aft-old_y)/.011))
    elif ids.intersection({96,107}):
        nominal=old_y;fraction=0.
    elif ids.intersection({98,99,100,101}):
        lo,hi=old_y,min(aft,old_y+.0111)
        for _ in range(32):
            mid=(lo+hi)/2
            if inner_y(mid)<old_y:lo=mid
            else:hi=mid
        nominal=(lo+hi)/2;fraction=1.
    elif 97 in ids:
        lo,hi=old_y,min(aft,old_y+.0111)
        for _ in range(32):
            mid=(lo+hi)/2;q=max(0,min(1,(outer_x(mid,top_z(mid))-v.co.x)/.032))
            y=mid-.011*smooth((mid-2.55)/(aft-2.55))*q
            if y<old_y:lo=mid
            else:hi=mid
        nominal=(lo+hi)/2;fraction=max(0,min(1,(outer_x(nominal,top_z(nominal))-v.co.x)/.032))
    else:raise RuntimeError('Painel traseiro sem estação identificada')
    v.co.y=old_y-(.017-.011*fraction)*smooth((nominal-2.55)/(aft-2.55));changed+=1

# Compatibilizar o novo limite A/cowl dividindo somente arestas com pontos
# colineares existentes. Inclui arestas internas, pois a lâmina foi retirada.
from mathutils.kdtree import KDTree
bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000004)
bm.verts.ensure_lookup_table();bm.verts.index_update()
kd=KDTree(len(bm.verts))
for v in bm.verts:kd.insert(v.co,v.index)
kd.balance();jobs=[]
for e in bm.edges:
    if len(e.link_faces)!=1:continue
    a,b=e.verts;d=b.co-a.co;l=d.length
    if l<1e-7:continue
    hits=[]
    for co,i,_ in kd.find_range((a.co+b.co)/2,l/2+.00002):
        if bm.verts[i] in e.verts or not bm.verts[i].link_faces:continue
        t=(co-a.co).dot(d)/(l*l)
        if 1e-5<t<1-1e-5 and (co-a.co-d*t).length<.00002:hits.append((t,co.copy()))
    if hits:jobs.append((e,a,sorted(hits,key=lambda p:p[0])))
for e,a,hits in jobs:
    end=e.other_vert(a);last=0.
    for t,co in hits:
        if t-last<1e-6:continue
        _,v=bmesh.utils.edge_split(e,a,(t-last)/(1-last));v.co=co
        e=next(edge for edge in v.link_edges if end in edge.verts);a=v;last=t
bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000021)
bad=[f for f in bm.faces if f.calc_area()<1e-10]
if bad:bmesh.ops.delete(bm,geom=bad,context='FACES_ONLY')
wire=[e for e in bm.edges if not e.link_faces]
if wire:bmesh.ops.delete(bm,geom=wire,context='EDGES')
loose=[v for v in bm.verts if not v.link_faces]
if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.normal_update()
multi=[e for e in bm.edges if len(e.link_faces)>2]
if multi:
    (r/'artifacts/vehicles/rondesp/v17-retopology-diagnostics.json').write_text(json.dumps([
        {'panels':[f[fl] for f in e.link_faces],'points':[list(v.co) for v in e.verts]} for e in multi],indent=2),encoding='utf-8')
assert not multi, 'Arestas triplas após retopologia: '+str(len(multi))
pending=set(bm.faces)
reference={1:Vector((0,0,1)),96:Vector((1,0,0)),114:Vector((0,1,0)),21:Vector((0,-1,0))}
while pending:
    f=next(iter(pending));pending.remove(f);stack=[f];island=[]
    while stack:
        f=stack.pop();island.append(f)
        for e in f.edges:
            for other in e.link_faces:
                if other in pending:pending.remove(other);stack.append(other)
    for panel,n in reference.items():
        selected=[f for f in island if f[fl]==panel]
        if selected:
            if sum(f.normal.dot(n)*f.calc_area() for f in selected)<0:
                for f in island:f.normal_flip()
            break
bm.normal_update()
for e in bm.edges:
    if len(e.link_faces)==2 and e.calc_face_angle(0)>math.radians(55):e.smooth=False
bm.to_mesh(o.data);bm.free();o.data.update()
s['boas_v17_intersections_finished']=True
o['boas_v17_tailgate_clearance_candidate_m']=.006
bpy.context.view_layer.update()
for script in ['inspect_hilux_mesh_v17.py','inspect_hilux_intersections_v17.py']:
    path=r/'automation/blender'/script
    exec(compile(path.read_text(encoding='utf-8'),str(path),'exec'),{'__file__':str(path)})
rp=r/'docs/reports/blender/hilux_carroceria_v17.json';report=json.loads(rp.read_text(encoding='utf-8'))
report['intersection_finish']={'remeshed':remeshed,'redundant_A_foot_faces_removed':len(foot),
    'roof_corner_vertices_rebuilt':len(fan),'bed_rear_vertices_adjusted':changed,'tailgate_base_clearance_candidate_m':.006}
report['base_vertices']=len(o.data.vertices);report['base_faces']=len(o.data.polygons)
report['visual_review']='pending';report['source_reopened']=False
bpy.data.libraries.write(str(out),{s},path_remap='RELATIVE',fake_user=True,compress=True)
report['sha256']=hashlib.sha256(out.read_bytes()).hexdigest()
rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def reopen():
    bpy.ops.wm.open_mainfile(filepath=str(out));data=json.loads(rp.read_text(encoding='utf-8'))
    data['source_reopened']=True;rp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return None
bpy.app.timers.register(reopen,first_interval=.5)
