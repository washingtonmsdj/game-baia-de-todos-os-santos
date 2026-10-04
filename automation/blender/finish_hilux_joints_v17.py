"""V17: mitra do para-brisa e retorno frontal ligado às bordas reais da chapa."""
import bpy,bmesh,collections,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.kdtree import KDTree
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
out=r/'blender/assets/vehicles/rondesp-pickup/hilux_carroceria_v17.blend'
assert not bpy.app.background and Path(bpy.data.filepath).resolve()==out.resolve()
assert s.get('boas_v17_intersections_finished') and not s.get('boas_v17_joints_finished')
o=s.objects['HILUX | CARROCERIA PRINCIPAL'];labels=json.loads(o['boas_panel_id_map'])
checkpoint=r/'artifacts/vehicles/rondesp/pre-v17-joints.blend'
if not checkpoint.exists():bpy.data.libraries.write(str(checkpoint),{s},path_remap='RELATIVE',compress=True)
else:assert not bpy.data.is_dirty,'Cena modificada após checkpoint'
bm=bmesh.new();bm.from_mesh(o.data);fl=bm.faces.layers.int.get('boas_panel_id')
# A mitra liga também os pontos internos dos dois retornos, evitando que
# duas abas independentes passem uma através da outra no canto do vidro.
header=[v for v in bm.verts if (v.co-Vector((.711,-.329,1.754))).length<1e-5]
side=[v for v in bm.verts if (v.co-Vector((.699,-.332,1.766))).length<1e-5]
assert len(header)==len(side)==1,'Pontos da mitra não encontrados'
bmesh.ops.pointmerge(bm,verts=header+side,merge_co=side[0].co.copy())
fore_edges=[e for e in bm.edges if len(e.link_faces)==2 and {f[fl] for f in e.link_faces}=={70,72}]
fore=sorted({v for e in fore_edges for v in e.verts},key=lambda v:v.co.z)
border=[]
for e in bm.edges:
    ids=[f[fl] for f in e.link_faces]
    if ids.count(108)!=1 or not set(ids).issubset({108,72}):continue
    if all(v.co.x>.80 and v.co.z>=fore[0].co.z-1e-6 for v in e.verts):border.extend(e.verts)
front=sorted(set(border),key=lambda v:v.co.z)
assert len(fore)>=40 and len(front)>35,'Contornos frontais incompletos'
fc=[v.co.copy() for v in fore];bc=[v.co.copy() for v in front]
assert bc[-1].z<fc[-1].z and (fc[-1]-Vector((.9275,-1.945,1.237))).length<1e-5
bc.append(fc[-1].copy())
old=[f for f in bm.faces if f[fl]==72]
bmesh.ops.delete(bm,geom=old,context='FACES_ONLY')
g=o.vertex_groups.new(name='HILUX17 | Retorno frontal com bordas comuns');labels[str(g.index+1)]=g.name
deform=bm.verts.layers.deform.verify();mat=list(o.data.materials).index(bpy.data.materials['RDP01 | Pintura marrom Rondesp'])
def at(points,z):
    if z<=points[0].z:return points[0].copy()
    if z>=points[-1].z:return points[-1].copy()
    for a,b in zip(points,points[1:]):
        if a.z<=z<=b.z:return a.lerp(b,(z-a.z)/max(b.z-a.z,1e-10))
    raise RuntimeError('Estação frontal sem segmento')
stations=sorted(set([p.z for p in fc+bc]));rows=[]
for z in stations:
    a,b=at(bc,z),at(fc,z)
    row=[bm.verts.new(a.lerp(b,j/8)) for j in range(9)]
    for v in row:v[deform][g.index]=1.
    rows.append(row)
added=0
for a,b in zip(rows,rows[1:]):
    for j in range(8):
        f=bm.faces.new([a[j],b[j],b[j+1],a[j+1]]);f[fl]=g.index+1
        f.material_index=mat;f.smooth=True;added+=1
bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000004)
bm.verts.ensure_lookup_table();bm.verts.index_update();kd=KDTree(len(bm.verts))
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
multi=[e for e in bm.edges if len(e.link_faces)>2]
assert not multi,'Junções triplas no retorno: '+str(len(multi))
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.normal_update()
# A referência do capô mantém o conjunto frontal/cabine apontando para fora.
pending=set(bm.faces)
while pending:
    f=next(iter(pending));pending.remove(f);stack=[f];island=[]
    while stack:
        f=stack.pop();island.append(f)
        for e in f.edges:
            for n in e.link_faces:
                if n in pending:pending.remove(n);stack.append(n)
    for panel,n in {1:Vector((0,0,1)),96:Vector((1,0,0)),114:Vector((0,1,0)),21:Vector((0,-1,0))}.items():
        chosen=[f for f in island if f[fl]==panel]
        if chosen:
            if sum(f.normal.dot(n)*f.calc_area() for f in chosen)<0:
                for f in island:f.normal_flip()
            break
bm.normal_update()
for e in bm.edges:
    if len(e.link_faces)==2 and e.calc_face_angle(0)>math.radians(55):e.smooth=False
bm.to_mesh(o.data);bm.free();o.data.update();o['boas_panel_id_map']=json.dumps(labels,ensure_ascii=False)
s['boas_v17_joints_finished']=True;bpy.context.view_layer.update()
for script in ['inspect_hilux_mesh_v17.py','inspect_hilux_intersections_v17.py']:
    path=r/'automation/blender'/script
    exec(compile(path.read_text(encoding='utf-8'),str(path),'exec'),{'__file__':str(path)})
rp=r/'docs/reports/blender/hilux_carroceria_v17.json';report=json.loads(rp.read_text(encoding='utf-8'))
report['joint_finish']={'windshield_return_miter':True,'front_return_stations':len(stations),
    'front_return_faces':added-len(bad),'front_return_component':g.name}
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
