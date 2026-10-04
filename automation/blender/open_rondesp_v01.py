"""Abre a fonte própria na mesma janela, depois de devolver o resultado MCP."""
import bpy
from pathlib import Path
path=Path(__file__).resolve().parents[2]/'blender/assets/vehicles/rondesp-pickup/marrom_v01.blend'
assert path.exists()
def reopen():
    bpy.ops.wm.open_mainfile(filepath=str(path))
    return None
bpy.app.timers.register(reopen,first_interval=.5)
