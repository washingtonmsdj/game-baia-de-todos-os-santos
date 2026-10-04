"""Finaliza microjunções do arredondamento e salva a revisão visível."""
import bpy,bmesh,json
from pathlib import Path
r=Path(__file__).resolve().parents[2]
assert not bpy.app.background and Path(bpy.data.filepath).name=='hilux_superficies_v19.blend'
o=bpy.context.scene.objects['HILUX | CARROCERIA PRINCIPAL']
from mathutils.kdtree import KDTree
before=json.loads((r/'artifacts/vehicles/rondesp/v19-mesh-before.json').read_text(encoding='utf8'))['geometry']['vertices']
base=json.loads((r/'artifacts/vehicles/rondesp/v17-mesh-after.json').read_text(encoding='utf8'))['geometry']['vertices']
def smooth(t):
 t=max(0.,min(1.,t));return t*t*(3-2*t)
kd=KDTree(len(o.data.vertices))
for v in o.data.vertices:kd.insert(v.co,v.index)
kd.balance()
count=0
for a,b in zip(before,base):
 if a[2]>1.675 and abs(a[0]-b[0])>1e-7:
  expected=(a[0]+(b[0]-a[0])*smooth((a[2]-1.675)/.058),a[1],a[2])
  _,idx,d=kd.find(expected)
  assert d<.00001
  o.data.vertices[idx].co.x=a[0]+(b[0]-a[0])*smooth((a[2]-1.752)/.020)
  count+=1
bm=bmesh.new();bm.from_mesh(o.data)
bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00002)
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
bm.to_mesh(o.data);bm.free();o.data.update()
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
print('V19: microjunções consolidadas e arquivo salvo')
