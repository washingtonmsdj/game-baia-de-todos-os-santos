"""Liga a borda superior frontal ao contorno existente do capô, via sessão visível."""
import bpy,bmesh,json,math,collections
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
assert not bpy.app.background and Path(bpy.data.filepath).name=='hilux_carroceria_v16.blend'
assert s.get('boas_v16_bed_applied') and not s.get('boas_v16_front_aligned')
o=s.objects['HILUX | CARROCERIA PRINCIPAL'];labels=json.loads(o['boas_panel_id_map'])
checkpoint=r/'artifacts/vehicles/rondesp/pre-v16-front-finish.blend'
assert not checkpoint.exists()
bpy.data.libraries.write(str(checkpoint),{s},path_remap='RELATIVE',compress=True)
bm=bmesh.new();bm.from_mesh(o.data);fl=bm.faces.layers.int.get('boas_panel_id');deform=bm.verts.layers.deform.verify()
def pid(name):return next(int(k) for k,v in labels.items() if v==name)
hood=pid('HILUX06 | Capô e ombros estampados');front=pid('HILUX06 | Para-choque e testa esculpidos')
def boundary(panel):
    counts=collections.Counter(e for f in bm.faces if f[fl]==panel for e in f.edges)
    return [e for e,n in counts.items() if n==1]
def front_y(x):return -2.435+.49*(abs(x)/.9275)**3.5
def front_z(x):return 1.137+.10*(abs(x)/.9275)**2.8
he=[e for e in boundary(hood) if all(abs(v.co.y-front_y(v.co.x))<.00002 for v in e.verts)]
fe=[e for e in boundary(front) if all(v.co.z>front_z(v.co.x)-.012 for v in e.verts)
    and abs(e.verts[0].co.x-e.verts[1].co.x)>.00001]
assert len(he)==36 and len(fe)>20
reference=sorted({tuple(v.co):v.co.copy() for e in he for v in e.verts}.values(),key=lambda p:p.x)
assert reference[0].x<.00001 and reference[-1].x>.9274
def point_at(x):
    for a,b in zip(reference,reference[1:]):
        if a.x-.00001<=x<=b.x+.00001:
            return a.lerp(b,max(0,min(1,(x-a.x)/(b.x-a.x))))
    return reference[0].copy() if x<0 else reference[-1].copy()
stations=sorted(set(round(v.co.x,7) for e in he+fe for v in e.verts))
def split_edges(edges):
    result=[]
    for original in edges:
        a,b=sorted(original.verts,key=lambda v:v.co.x)
        interior=[x for x in stations if a.co.x+.000001<x<b.co.x-.000001]
        active=original;start=a;end=b
        for x in interior:
            ratio=(x-start.co.x)/(end.co.x-start.co.x)
            _,v=bmesh.utils.edge_split(active,start,ratio)
            result.append(v);start=v
            active=next(e for e in v.link_edges if end in e.verts)
        result.extend([a,b])
    return set(result)
hv=split_edges(he);fv=split_edges(fe)
for v in fv:v.co=point_at(v.co.x)
g=o.vertex_groups.new(name='HILUX16 | Chapa frontal alinhada ao capo')
labels[str(g.index+1)]=g.name
front_faces=[f for f in bm.faces if f[fl]==front]
for f in front_faces:
    f[fl]=g.index+1
    for v in f.verts:v[deform][g.index]=1.
# Faces com novos pontos de borda são trianguladas, sem ngons torcidos.
subdivided=[f for f in bm.faces if len(f.verts)>4 and any(v in hv|fv for v in f.verts)]
if subdivided:bmesh.ops.triangulate(bm,faces=subdivided,quad_method='BEAUTY',ngon_method='BEAUTY')
bmesh.ops.remove_doubles(bm,verts=list(hv|fv),dist=.000004)
bm.normal_update()
joint=[e for e in bm.edges if len(e.link_faces)==2 and {f[fl] for f in e.link_faces}=={hood,g.index+1}]
for e in joint:e.smooth=False
bm.to_mesh(o.data);bm.free();o.data.update()
o['boas_panel_id_map']=json.dumps(labels,ensure_ascii=False);s['boas_v16_front_aligned']=True
rp=r/'docs/reports/blender/hilux_carroceria_v16.json';report=json.loads(rp.read_text(encoding='utf-8'))
report['front_finish']={'hood_stations_before':len(reference),'shared_upper_front_edges':len(joint),
    'scope':'Borda superior da chapa frontal acompanha o contorno existente do capô, com divisões comuns e normal de dobra.'}
report['new_components'].append(g.name)
report['notes'].append('Contorno superior da frente ligado à borda real do capô; faróis e grade continuam reservados.')
report['base_vertices']=len(o.data.vertices);report['base_faces']=len(o.data.polygons)
rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
bpy.context.view_layer.update()
