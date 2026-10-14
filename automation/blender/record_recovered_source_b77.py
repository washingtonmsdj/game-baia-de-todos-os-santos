"""Prova de leitura na instância visível recuperada, sem salvar/mudar geometria."""
import bpy,json,os,hashlib
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[2]
entry=json.loads((ROOT/'world/areas/mvp-centro-lacerda/blender-revisions.json').read_text(encoding='utf8'))['validation_source']
assert entry['revision']=='R30B.77' and os.getpid()!=9084
assert Path(bpy.data.filepath).resolve()==(ROOT/entry['file']).resolve()
with (ROOT/entry['file']).open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
assert sha==entry['sha256']
proof={'file':entry['file'],'sha256':sha,'source_mode':'validation','scene':bpy.context.scene.name,'load_post_completed':True,'timestamp_utc':datetime.now(timezone.utc).isoformat(),'pid':os.getpid(),'method':'nova instância única abriu B77 via CLI; inspeção MCP após carga','previous_process':9084,'previous_open_operation':'timeout; não usada como prova'}
(ROOT/'artifacts/blender-sessions/last-open.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(proof,ensure_ascii=False))
