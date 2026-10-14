"""Atualiza apenas o snapshot informativo do contrato antes da conferência final."""
import bpy,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/reports/blender/lacerda-controller'
r=json.loads((OUT/'scene_b79.json').read_text(encoding='utf8'))
assert Path(bpy.data.filepath).resolve()==(ROOT/r['source_after']['file']).resolve()
text=bpy.data.texts['BOAS | contrato slice B79'];text.clear()
text.write('Snapshot informativo. Fonte canônica: world/areas/mvp-centro-lacerda/corridor-slice.json\n')
text.write((ROOT/'world/areas/mvp-centro-lacerda/corridor-slice.json').read_text(encoding='utf8'))
bpy.context.scene.frame_set(65024);bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
with Path(bpy.data.filepath).open('rb') as stream:sha=hashlib.file_digest(stream,'sha256').hexdigest()
r['source_after']['sha256']=sha
(OUT/'scene_b79.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'sha256':sha,'geometry_changed':False,'contract_snapshot_updated':True}))
