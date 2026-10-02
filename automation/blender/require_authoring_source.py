"""Preflight do editor: janela adotada e fonte explícita, antes de mutações."""
import bpy,json,os,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[2]
session=root/'artifacts/blender-sessions/current-session.json'
if not session.exists():raise RuntimeError('Adote/preserve primeiro a sessão MCP indicada pelo usuário.')
registered=json.loads(session.read_text(encoding='utf8'))
if registered['mcp_port']!=BOAS_MCP_PORT or registered['pid']!=os.getpid():raise RuntimeError('Janela/porta diferente da sessão adotada; não editar outra instância.')
if not BOAS_SOURCE_OPERATION:
    if BOAS_SOURCE_MODE=='authoring':entry=json.loads((root/'world/areas/mvp-centro-lacerda/blender-revisions.json').read_text(encoding='utf8'))['authoring_source']
    else:entry=json.loads((root/'world/areas/mvp-centro-lacerda/production.json').read_text(encoding='utf8'))['world_source']
    expected=(root/entry['file']).resolve()
    if Path(bpy.data.filepath).resolve()!=expected:raise RuntimeError('Fonte incorreta na janela. Fonte '+BOAS_SOURCE_MODE+': '+entry['file']+'. Nenhuma modelagem executada.')
    with expected.open('rb') as f:actual=hashlib.file_digest(f,'sha256').hexdigest()
    if actual!=entry['sha256']:raise RuntimeError('Hash da fonte mudou: registrar/revisar a nova alteração antes de prosseguir.')
