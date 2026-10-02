"""Reabre o hash autoral registrado, na mesma janela e preservando sessão suja."""
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name('open_registered_source.py')),init_globals={'BOAS_FORCE_REOPEN':True,'BOAS_SOURCE_MODE':'authoring'})
