"""Retira arestas sem faces da união e conserva a oficina isolada."""
import bpy,bmesh,json,hashlib
from pathlib import Path
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
out=r/'blender/assets/vehicles/rondesp-pickup/hilux_carroceria_v12.blend'
assert not bpy.app.background and Path(bpy.data.filepath).resolve()==out.resolve()
assert not s.get('boas_v12_finished')
body=s.objects['HILUX | CARROCERIA PRINCIPAL']
bm=bmesh.new();bm.from_mesh(body.data)
wires=[e for e in bm.edges if not e.link_faces];count=len(wires)
if wires:bmesh.ops.delete(bm,geom=wires,context='EDGES')
loose=[v for v in bm.verts if not v.link_faces];loose_count=len(loose)
if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
bm.to_mesh(body.data);bm.free();body.data.update()
s['boas_v12_finished']=True
bpy.context.view_layer.update()
bpy.data.libraries.write(str(out),{s},path_remap='RELATIVE',fake_user=True,compress=True)
rp=r/'docs/reports/blender/hilux_carroceria_v12.json';data=json.loads(rp.read_text(encoding='utf-8'))
data.update(sha256=hashlib.sha256(out.read_bytes()).hexdigest(),wire_edges_removed=count,loose_vertices_removed=loose_count,source_reopened=False)
rp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def reopen():
    bpy.ops.wm.open_mainfile(filepath=str(out));data=json.loads(rp.read_text(encoding='utf-8'));data['source_reopened']=True
    rp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');return None
bpy.app.timers.register(reopen,first_interval=.5)
