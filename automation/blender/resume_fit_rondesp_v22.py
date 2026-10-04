"""Retoma a aplicação V22 após guard de contato, restaurando somente a V21 conhecida."""
import bpy,hashlib,runpy
from pathlib import Path
r=Path(__file__).resolve().parents[2];source=r/'blender/assets/vehicles/rondesp-pickup/marrom_v21_montada.blend'
assert not bpy.app.background and Path(bpy.data.filepath).resolve()==source.resolve()
assert hashlib.sha256(source.read_bytes()).hexdigest()=='41c5833edb6350c83d1e23900d1d2347b628909f86804829bca7b1271d2cc581'
assert not bpy.context.scene.get('boas_v22_lights_applied') and not bpy.app.is_job_running('RENDER')
bpy.ops.wm.open_mainfile(filepath=str(source))
runpy.run_path(str(r/'automation/blender/fit_and_light_rondesp_v22.py'),run_name='__main__')
