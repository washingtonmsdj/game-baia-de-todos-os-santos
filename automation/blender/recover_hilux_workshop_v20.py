"""Preserva cena padrão e carrega fonte explícita da Hilux na janela existente."""
import bpy,os,json,hashlib
from pathlib import Path
r=Path(__file__).resolve().parents[2]
assert not bpy.app.background and os.getpid()==19576
assert not bpy.data.filepath and set(bpy.context.scene.objects.keys())=={'Cube','Camera','Light'}
cat=json.loads((r/'world/vehicles/catalog.json').read_text(encoding='utf8'))
a=next(v for v in cat['vehicles'] if v['asset_id']=='vehicle-rondesp-pickup')['authoring_base']
p=r/a['file'];assert p.name=='hilux_superficies_v19.blend'
assert hashlib.sha256(p.read_bytes()).hexdigest()==a['sha256']
checkpoint=r/'artifacts/vehicles/rondesp/v20-recovered-default-scene.blend'
assert not checkpoint.exists()
bpy.data.libraries.write(str(checkpoint),set(bpy.data.scenes),path_remap='RELATIVE',compress=True)
bpy.ops.wm.open_mainfile(filepath=str(p))
assert bpy.context.scene.name==a['scene']
print(json.dumps({'file':bpy.data.filepath,'pid':os.getpid(),'preserved':checkpoint.relative_to(r).as_posix()}))
