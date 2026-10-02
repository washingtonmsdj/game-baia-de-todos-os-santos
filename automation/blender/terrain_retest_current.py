"""Auditoria e replay da revisão atual, sequenciais na mesma janela MCP."""
import runpy
from pathlib import Path
root=Path(__file__).resolve().parents[2]
runpy.run_path(str(root/'automation/blender/terrain_vehicle_audit_r30b23.py'),run_name='__main__')
runpy.run_path(str(root/'automation/blender/terrain_vehicle_replay.py'),run_name='__main__')
