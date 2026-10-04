"""Substitui tiras de batente antigas que atravessavam os vãos sem portas."""
import bpy,bmesh,json,hashlib,math
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
out=r/'blender/assets/vehicles/rondesp-pickup/hilux_carroceria_v12.blend'
assert not bpy.app.background and Path(bpy.data.filepath).resolve()==out.resolve()
assert not s.get('boas_v12_jambs_cleaned')
o=s.objects['HILUX | CARROCERIA PRINCIPAL']
targets={g.index for g in o.vertex_groups if 'Batentes externos e soleira' in g.name}
indices={v.index for v in o.data.vertices if any(g.group in targets for g in v.groups)}
bm=bmesh.new();bm.from_mesh(o.data);bm.verts.ensure_lookup_table()
faces=[f for f in bm.faces if all(v.index in indices for v in f.verts)]
count=len(faces);bmesh.ops.delete(bm,geom=faces,context='FACES')
loose=[v for v in bm.verts if not v.link_faces]
if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
# Batente A inferior encostado na chapa do para-lama; não cruza o vão da porta.
rows=[]
for i in range(35):
    t=i/34;z=.489+.829*t;y=-.978+.084*(1-t)**9
    x=.816+.076*math.sin(math.pi*t)**1.5
    row=[]
    for j in range(5):
        u=j/4;row.append(bm.verts.new((x-.037*u,y-.006-.019*u,z)))
    rows.append(row)
for a,b in zip(rows,rows[1:]):
    for j in range(4):
        f=bm.faces.new((a[j],b[j],b[j+1],a[j+1]));f.smooth=True
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
s['boas_v12_jambs_cleaned']=True
bpy.context.view_layer.update()
bpy.data.libraries.write(str(out),{s},path_remap='RELATIVE',fake_user=True,compress=True)
rp=r/'docs/reports/blender/hilux_carroceria_v12.json';data=json.loads(rp.read_text(encoding='utf-8'))
data.update(sha256=hashlib.sha256(out.read_bytes()).hexdigest(),old_jamb_faces_replaced=count,source_reopened=False)
data['notes'].append('Batentes triangulados antigos substituídos: tiras não atravessam mais o vão das portas.')
rp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def reopen():
    bpy.ops.wm.open_mainfile(filepath=str(out));data=json.loads(rp.read_text(encoding='utf-8'));data['source_reopened']=True
    rp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');return None
bpy.app.timers.register(reopen,first_interval=.5)
