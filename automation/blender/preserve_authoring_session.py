"""Cópia de recuperação da sessão; não altera a fonte nem cria revisão numerada."""
import bpy,json,os,hashlib
from datetime import datetime,timezone
from pathlib import Path
root=Path(__file__).resolve().parents[2];folder=root/'artifacts/blender-sessions';folder.mkdir(parents=True,exist_ok=True)
original=bpy.data.filepath;dirty=bpy.data.is_dirty;scene=bpy.context.scene.name
if not original:raise RuntimeError('Sessão sem fonte identificada')
tag=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ');copy=folder/(Path(original).stem+'_sessao_'+tag+'.blend')
bpy.ops.wm.save_as_mainfile(filepath=str(copy),copy=True)
assert bpy.data.filepath==original
report={'schema':'boas/blender-session-recovery-v1','source_file':Path(original).relative_to(root).as_posix(),'source_sha256':hashlib.file_digest(Path(original).open('rb'),'sha256').hexdigest(),'scene':scene,'unsaved_changes_before_copy':dirty,'recovery_file':copy.relative_to(root).as_posix(),'recovery_sha256':hashlib.file_digest(copy.open('rb'),'sha256').hexdigest(),'pid':os.getpid(),'mcp_port':9876,'active_file_changed':False,'recovery_is_production_revision':False}
report['recovered_source_file']=report.pop('source_file');report['recovered_source_sha256']=report.pop('source_sha256');report['observed_file']=report['recovered_source_file']
report['mcp_port']=globals().get('BOAS_MCP_PORT',9876)
(folder/'current-session.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(report,ensure_ascii=False))
