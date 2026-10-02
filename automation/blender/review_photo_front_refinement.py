"""Rever somente as fachadas que receberam correções desde a vista anterior."""
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name('review_photo_city_baixa.py')),init_globals={'BOAS_REVIEW_VIEWS':['fachadas']})
