"""Auditoria atual preservando o relatório histórico B38."""
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name('audit_rondesp_network.py')),init_globals={'BOAS_REPORT_PATH':'docs/reports/blender/rondesp_network_current.json'})
