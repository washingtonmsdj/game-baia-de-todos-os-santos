"""Vistas da B96 e apresentação final do mapa na mesma janela."""
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name('capture_lacerda_enclosure_b95.py')),init_globals={'BOAS_CAPTURE_REVISION':96})
