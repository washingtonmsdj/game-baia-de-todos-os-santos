"""Checkpoint final de apresentação: preservar a plataforma legada substituída."""
import bpy,json,hashlib,runpy
from pathlib import Path
root=Path(__file__).resolve().parents[2];out=root/'docs/reports/blender/lacerda-bridge-b92';path=out/'application.json';r=json.loads(path.read_text())
file=Path(bpy.data.filepath);assert file.name==Path(r['file']).name
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));sig=h['signature']
old=bpy.context.scene.objects['CALIBRADO | piso superior torre'];source=json.loads((root/'docs/reports/blender/lacerda-mesh-b91/remaining-legacy.json').read_text());expected=next(row for row in source if row['object']==old.name)
assert sig(old)==expected['signature']
window=next(w for w in bpy.context.window_manager.windows if w.screen);area=next(a for a in window.screen.areas if a.type=='VIEW_3D')
assert not area.spaces.active.local_view and bpy.context.scene.objects['MVP | terreno corrigido | colisão estática'].visible_get()
before={'signature':sig(old),'visible':old.visible_get()}
old.hide_set(True);old.hide_render=True;old['boas_active_authoring']=False;old['boas_role']='SUPERSEDED_REFERENCE';old['boas_superseded_by']='TORRE | cornija galeria';old['boas_superseded_reason']='Plataforma da implantação antiga, preservada; galeria atual deriva do contorno SUCOP17';old['boas_provenance_ids']=json.dumps(['derived:lacerda-bridge-b92'])
assert sig(old)==before['signature']
r['changes'].append({'object':old.name,'before':before,'after':{'signature':sig(old),'visible':old.visible_get()},'operation':'PRESERVE_AS_REFERENCE'})
r['presentation_checkpoint_before_sha256']=r['sha256'];r['presentation_checkpoint_backup']=r['file']+'1';r['reopened']=False
# Mesma geometria B92, alteração somente de apresentação/classificação da
# referência. O backup nativo preserva o checkpoint anterior desta candidata.
bpy.ops.wm.save_as_mainfile(filepath=str(file),compress=True)
backup=Path(str(file)+'1')
assert backup.exists(),'Checkpoint anterior deve ser preservado'
with backup.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==r['presentation_checkpoint_before_sha256']
with file.open('rb') as f:r['sha256']=hashlib.file_digest(f,'sha256').hexdigest()
path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
catpath=root/'world/areas/mvp-centro-lacerda/blender-revisions.json';cat=json.loads(catpath.read_text())
for entry in cat['revisions']:
 if entry['file']==r['file']:entry['sha256']=r['sha256'];entry['presentation_checkpoint_before_sha256']=r['presentation_checkpoint_before_sha256']
for key in ('authoring_source','validation_source'):cat[key]['sha256']=r['sha256']
catpath.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'revision':'B92','sha256':r['sha256'],'legacy_platform_preserved':old.name,'prior_checkpoint_preserved':True}))
