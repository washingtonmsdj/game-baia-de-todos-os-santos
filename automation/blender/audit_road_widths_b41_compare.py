"""Reaudita larguras de cena na B41 sem substituir o relatório histórico B39."""
import runpy
from pathlib import Path
runpy.run_path(
    str(Path(__file__).with_name("audit_road_widths.py")),
    init_globals={"BOAS_REPORT_PATH":"artifacts/roads/rondesp/road_width_scene_b41_compare.json"}
)
