"""Reabrir revisão de modelagem salva na única janela MCP."""
import bpy
from pathlib import Path
root=Path(__file__).resolve().parents[2]
bpy.ops.wm.open_mainfile(filepath=str(root/'blender/salvador_lacerda_r30b31_cidade_baixa_fachadas_cravo.blend'))
