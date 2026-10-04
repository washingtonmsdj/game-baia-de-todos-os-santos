import bpy,bmesh
from pathlib import Path
assert not bpy.app.background and Path(bpy.data.filepath).name=='hilux_superficies_v19.blend'
o=bpy.context.scene.objects['HILUX | CARROCERIA PRINCIPAL']
bm=bmesh.new();bm.from_mesh(o.data)
bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00002)
for e in bm.edges:
 if len(e.link_faces)==2 and any(all(abs(v.co.z-z)<.000002 for v in e.verts) for z in [1.750,1.752,1.754,1.756,1.758]):e.smooth=True
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
bm.to_mesh(o.data);bm.free();o.data.update()
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
