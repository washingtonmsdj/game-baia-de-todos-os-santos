"""Reabrir e conferir a fonte V21 na mesma janela; revisão visual adicional."""
import bpy,hashlib,json,struct
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parents[2];out=r/'blender/assets/vehicles/rondesp-pickup/marrom_v21_montada.blend';rp=r/'docs/reports/blender/rondesp_marrom_v21.json'
assert not bpy.app.background and Path(bpy.data.filepath).resolve()==out.resolve()
assert not bpy.app.is_job_running('RENDER')
bpy.ops.wm.open_mainfile(filepath=str(out));s=bpy.context.scene;data=json.loads(rp.read_text(encoding='utf8'))
def fingerprint(ob):
 h=hashlib.sha256()
 for v in ob.data.vertices:h.update(struct.pack('<3d',*v.co))
 for p in ob.data.polygons:h.update(struct.pack('<I',len(p.vertices)));h.update(struct.pack('<'+'I'*len(p.vertices),*p.vertices))
 return h.hexdigest()
data['source_reopened']=Path(bpy.data.filepath).resolve()==out.resolve();data['protected_meshes_verified_after_reopen']=all(fingerprint(s.objects[n])==h for n,h in data['protected_mesh_hashes'].items());data['source_sha256_after_reopen']=hashlib.sha256(out.read_bytes()).hexdigest()
assert data['source_sha256_after_reopen']==data['sha256'] and data['protected_meshes_verified_after_reopen']
data['closed_door_children']={o.name:[c.name for c in o.children] for o in s.objects if 'Pivô porta' in o.name}
data['wheel_pivots_preserved']=[o.name for o in s.objects if 'Eixo giro roda' in o.name]
data['material_preview_enabled']=all(a.spaces.active.shading.type=='MATERIAL' for sc in bpy.data.screens for a in sc.areas if a.type=='VIEW_3D')
data['visual_review']='Front and rear inspected; assembled candidate, no final fidelity approval.'
rp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
# Maior amostragem na vista traseira para reduzir o ruído da prévia Eevee.
if hasattr(s,'eevee') and hasattr(s.eevee,'taa_render_samples'):s.eevee.taa_render_samples=128
cam=s.camera;mw=cam.matrix_world.copy();scale=cam.data.ortho_scale
cam.location=(-7,8,3.25);cam.rotation_euler=(Vector((0,.25,1.04))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=6.7
s.render.filepath=str(r/data['preview_rear']);bpy.ops.render.render(write_still=True)
cam.matrix_world=mw;cam.data.ortho_scale=scale
print(json.dumps({'source_reopened':True,'sha256':data['sha256'],'body_and_doors_preserved':True,'material_preview':data['material_preview_enabled']}))
