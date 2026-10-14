"""Remove somente a cópia de diagnóstico B40 comprovadamente idêntica à revisão preservada."""
from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parents[2]
probe=(root/'artifacts/blender-sessions/b40_saved_probe_copy.blend').resolve()
source=(root/'blender/salvador_lacerda_r30b40_fluxos_e_colisao.blend').resolve()
assert probe.is_relative_to((root/'artifacts/blender-sessions').resolve())
removed=0
if probe.is_file() and source.is_file():
    with probe.open('rb') as f:a=hashlib.file_digest(f,'sha256').hexdigest()
    with source.open('rb') as f:b=hashlib.file_digest(f,'sha256').hexdigest()
    assert a==b,'Cópia diferente: preservar'
    removed=probe.stat().st_size;probe.unlink()
print(json.dumps({'verified_duplicate_removed_bytes':removed,'source_preserved':source.is_file(),'scene_unchanged':True}))
