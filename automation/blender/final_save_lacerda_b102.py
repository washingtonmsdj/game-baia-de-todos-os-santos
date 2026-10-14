"""Salva pose inicial após prova, sem criar cópia/revisão artificial."""
import bpy,json,runpy,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[2];out=root/'docs/reports/blender/lacerda-exterior-b102';file=Path(bpy.data.filepath)
assert file.name=='salvador_lacerda_r30b102_corpo_encosta_quatro_elevadores.blend'
proof=json.loads((out/'live-proof.json').read_text());assert proof['status']=='FOUR_LIFTS_LIVE_ROUND_TRIP_PASSED'
r=json.loads((out/'application.json').read_text());sig=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'))['signature']
for row in r['added']:assert sig(bpy.context.scene.objects[row['object']])==row['after']['signature'],row['object']
for n,s in r['preserved_signatures'].items():assert sig(bpy.context.scene.objects[n])==s,n
assert sig(bpy.context.scene.objects['MVP | terreno corrigido | colisão estática'])==r['terrain_after_signature']
bpy.ops.wm.save_mainfile()
with file.open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
r['sha256']=sha;r['live_proof']='docs/reports/blender/lacerda-exterior-b102/live-proof.json'
(out/'application.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
catpath=root/'world/areas/mvp-centro-lacerda/blender-revisions.json';cat=json.loads(catpath.read_text())
for v in cat['revisions']:
 if v['file']==r['file']:v['sha256']=sha
for key in ('authoring_source','validation_source'):cat[key]['sha256']=sha
catpath.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'file':r['file'],'sha256':sha,'dirty':bpy.data.is_dirty,'pose':'ALL_CLOSED_UPPER'}))
