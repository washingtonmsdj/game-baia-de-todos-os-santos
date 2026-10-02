"""Remove dentículos que pertenciam à cornija contínua diante do grande arco."""
import bpy,bmesh,json,runpy,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[2];rp=root/'docs/reports/blender/torre_galerias_r30b35.json';r=json.loads(rp.read_text(encoding='utf8'))
assert not r.get('facade_final_correction')
sig=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'))['signature']
o=bpy.context.scene.objects['RIO R35 | Consoles e dentículos das alas'];before=sig(o)
bm=bmesh.new();bm.from_mesh(o.data)
verts=[v for v in bm.verts if abs(v.co.x)<5.62 and .3<v.co.y<.7 and 13.80<v.co.z<14.06]
assert verts,'Dentículos centrais não encontrados; revisar antes de repetir'
bmesh.ops.delete(bm,geom=verts,context='VERTS');bm.to_mesh(o.data);bm.free();o.data.update()
r['facade_final_correction']={'object':o.name,'before':before,'after':sig(o),'reason':'Dentículos das alas limitados às cornijas laterais; removidas peças suspensas diante do vidro central.'}
assert all(sig(bpy.context.scene.objects[n])==s for n,s in r['protected_signatures'].items())
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
with Path(bpy.data.filepath).open('rb') as f:r['source_after']['sha256']=hashlib.file_digest(f,'sha256').hexdigest()
rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
runpy.run_path(str(root/'automation/blender/review_facade_context_r35.py'),init_globals={'BOAS_REVIEW_NAMES':['frente']})
