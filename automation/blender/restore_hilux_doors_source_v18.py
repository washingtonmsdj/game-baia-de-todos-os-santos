"""Recupera exclusivamente a base salva V17 após execução parcial da etapa das portas."""
import bpy,json,hashlib
from pathlib import Path
r=Path(__file__).resolve().parents[2]
v=next(v for v in json.loads((r/'world/vehicles/catalog.json').read_text(encoding='utf8'))['vehicles'] if v['asset_id']=='vehicle-rondesp-pickup')
p=r/v['authoring_base']['file']
assert not bpy.app.background and p.name=='hilux_carroceria_v17.blend'
assert Path(bpy.data.filepath).resolve()==p.resolve()
assert not (r/'blender/assets/vehicles/rondesp-pickup/hilux_portas_v18.blend').exists()
assert hashlib.sha256(p.read_bytes()).hexdigest()==v['authoring_base']['sha256']
def restore():
 bpy.ops.wm.open_mainfile(filepath=str(p));return None
bpy.app.timers.register(restore,first_interval=.5)
