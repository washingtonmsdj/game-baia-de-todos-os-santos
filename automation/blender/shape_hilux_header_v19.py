import bpy,bmesh,json
from pathlib import Path
from mathutils.kdtree import KDTree
r=Path(__file__).resolve().parents[2]
assert not bpy.app.background and Path(bpy.data.filepath).name=='hilux_superficies_v19.blend'
o=bpy.context.scene.objects['HILUX | CARROCERIA PRINCIPAL']
def smooth(t):
 t=max(0.,min(1.,t));return t*t*(3-2*t)
a=json.loads((r/'artifacts/vehicles/rondesp/v19-mesh-before.json').read_text(encoding='utf8'))['geometry']['vertices']
b=json.loads((r/'artifacts/vehicles/rondesp/v17-mesh-after.json').read_text(encoding='utf8'))['geometry']['vertices']
kd=KDTree(len(o.data.vertices))
for v in o.data.vertices:kd.insert(v.co,v.index)
kd.balance()
for p,q in zip(a,b):
 if p[2]>1.675 and abs(p[0]-q[0])>1e-7:
  expected=(p[0]+(q[0]-p[0])*smooth((p[2]-1.752)/.020),p[1],p[2])
  _,idx,d=kd.find(expected);assert d<.00001
  o.data.vertices[idx].co.x=q[0]
bm=bmesh.new();bm.from_mesh(o.data)
for z in [1.750,1.752,1.754,1.756,1.758]:
 bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-7,plane_co=(0,0,z),plane_no=(0,0,1),clear_inner=False,clear_outer=False)
for v in bm.verts:
 x,y,z=v.co
 if z>1.675 and x>.64:
  wy=smooth((y-.075)/.030)*(1-smooth((y-.254)/.032))
  v.co.x-=.042*wy*(1-smooth((z-1.750)/.008))
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
bm.to_mesh(o.data);bm.free();o.data.update()
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
