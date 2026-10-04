"""Descarta execução parcial, reabrindo o checkpoint V18 na mesma janela MCP."""
import bpy
from pathlib import Path
r=Path(__file__).resolve().parents[2];p=r/'blender/assets/vehicles/rondesp-pickup/hilux_portas_v18.blend'
assert not bpy.app.background and Path(bpy.data.filepath).resolve()==p.resolve()
assert not bpy.context.scene.get('boas_v18_center_seam')
def restore():
 bpy.ops.wm.open_mainfile(filepath=str(p));return None
bpy.app.timers.register(restore,first_interval=.5)
