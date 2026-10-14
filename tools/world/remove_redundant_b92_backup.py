"""Libera somente o backup automático B92 previamente comparado na sessão."""
import json,hashlib,shutil
from pathlib import Path
root=Path(__file__).resolve().parents[2];out=root/'docs/reports/blender/lacerda-body-b96';p=json.loads((out/'backup-comparison.json').read_text())
assert p['official_source_validated'] and p['objects_compared']==542 and not p['geometry_differences']
source=(root/p['source']).resolve();backup=(root/p['backup']).resolve()
assert source.parent==backup.parent==(root/'blender').resolve() and backup.name=='salvador_lacerda_r30b92_ponte_estrutural_consolidada.blend1'
catpath=root/'world/areas/mvp-centro-lacerda/blender-revisions.json';cat=json.loads(catpath.read_text());entry=next(v for v in cat['revisions'] if v.get('file')==p['source'])
with source.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==entry['sha256']
with backup.open('rb') as f:oldhash=hashlib.file_digest(f,'sha256').hexdigest()
assert oldhash=='bad73e6c5e114862c4da284f943b91bf7339fb29aca82100f520e9d0db342112'
session=json.loads((root/'artifacts/blender-sessions/current-session.json').read_text());assert (root/session['recovery_file']).exists() and session['unsaved_changes_before_copy']
size=backup.stat().st_size;record={**p,'backup_sha256':oldhash,'source_sha256':entry['sha256'],'bytes_removed':size,'operation':'REMOVE_ONLY_REDUNDANT_AUTOMATIC_BACKUP','reason':'Checkpoint automático anterior ao B92 final validado. Geometria/transform/material dos 542 componentes idênticos; não é alegação de identidade binária ou comparação de todos os metadados. Revisões oficiais e recuperação B95 preservadas.'}
(out/'space-recovery.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
backup.unlink()
cat.setdefault('automatic_backup_cleanup',[]).append({'file':p['backup'],'sha256':oldhash,'state':'removed_redundant_automatic_checkpoint','evidence':'docs/reports/blender/lacerda-body-b96/space-recovery.json'})
catpath.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'bytes_removed':size,'official_b92_preserved':source.exists(),'free_bytes':shutil.disk_usage(root).free}))
