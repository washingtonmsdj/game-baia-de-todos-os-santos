"""Conferência somente dos dois enquadramentos afetados pelo encontro do solo."""
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name('review_terraces_r36.py')),init_globals={'review_view_names':['terracos','encontro']})
