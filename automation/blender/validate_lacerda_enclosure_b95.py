"""Reutiliza QA dos encontros B94 com controles e assinaturas atuais B95."""
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name('validate_lacerda_corridors_b94.py')),init_globals={'BOAS_ENCLOSURE_REVISION':95})
