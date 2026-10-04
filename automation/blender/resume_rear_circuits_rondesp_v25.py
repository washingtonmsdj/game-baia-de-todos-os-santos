"""Descarta apenas o passe V25 incompleto e reaplica sobre a V24 salva."""
import bpy,hashlib,runpy
from pathlib import Path
r=Path(__file__).resolve().parents[2]
source=r/'blender/assets/vehicles/rondesp-pickup/marrom_v24_farois.blend'
assert not bpy.app.background and Path(bpy.data.filepath).resolve()==source.resolve()
assert not (r/'blender/assets/vehicles/rondesp-pickup/marrom_v25_lanternas_re.blend').exists()
assert hashlib.sha256(source.read_bytes()).hexdigest()=='362783bb439f3f26d337c477bccdc955790b448fc5e25cb72f2db6be043945db'
bpy.ops.wm.open_mainfile(filepath=str(source))
runpy.run_path(str(r/'automation/blender/rear_circuits_rondesp_v25.py'),run_name='__main__')
