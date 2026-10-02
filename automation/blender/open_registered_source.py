"""Abrir ponteiro declarado, preservando uma sessão suja; mesma janela MCP."""
import bpy,json,hashlib,runpy
from pathlib import Path
from datetime import datetime,timezone
from bpy.app.handlers import persistent
root=Path(__file__).resolve().parents[2]
mode=globals().get('BOAS_SOURCE_MODE','authoring')
if mode=='authoring':entry=json.loads((root/'world/areas/mvp-centro-lacerda/blender-revisions.json').read_text(encoding='utf8'))['authoring_source']
else:entry=json.loads((root/'world/areas/mvp-centro-lacerda/production.json').read_text(encoding='utf8'))['world_source']
file=(root/entry['file']).resolve()
with file.open('rb') as stream:actual=hashlib.file_digest(stream,'sha256').hexdigest()
if actual!=entry['sha256']:raise RuntimeError('Fonte mudou sem registrar revisão')
if Path(bpy.data.filepath).resolve()==file and not globals().get('BOAS_FORCE_REOPEN',False):print('Fonte registrada já está aberta; não recarregar nem descartar alterações.')
else:
    if bpy.data.is_dirty:runpy.run_path(str(root/'automation/blender/preserve_authoring_session.py'),run_name='__main__',init_globals={'BOAS_MCP_PORT':globals().get('BOAS_MCP_PORT',9876)})
    @persistent
    def _boas_registered_source_loaded(_unused):
        if Path(bpy.data.filepath).resolve()==file:
            proof={'file':entry['file'],'sha256':actual,'source_mode':mode,'scene':bpy.context.scene.name,'load_post_completed':True,'timestamp_utc':datetime.now(timezone.utc).isoformat()}
            folder=root/'artifacts/blender-sessions';folder.mkdir(parents=True,exist_ok=True);(folder/'last-open.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf8')
        bpy.app.handlers.load_post.remove(_boas_registered_source_loaded)
    bpy.app.handlers.load_post.append(_boas_registered_source_loaded)
    bpy.ops.wm.open_mainfile(filepath=str(file))
