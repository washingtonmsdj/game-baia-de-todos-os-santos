"""Auditoria integral read-only da candidata R30B.45."""
import runpy
from pathlib import Path
source={
 "file":"blender/salvador_lacerda_r30b45_proxy_misericordia_final.blend",
 "revision":"R30B.45",
 "status":"validation_candidate",
 "parent_file":"blender/salvador_lacerda_r30b44_proxy_misericordia.blend",
 "evidence":"docs/reports/blender/misericordia_proxy_r30b45.json",
 "sha256":"3911fd4402591a0484da3adee15b64ba6af01b50133f49215fd67ff17f58ab0e"
}
runpy.run_path(str(Path(__file__).with_name("audit_rondesp_network.py")),init_globals={
 "BOAS_SOURCE_OVERRIDE":source,
 "BOAS_REPORT_PATH":"artifacts/roads/rondesp/rondesp_network_b45_candidate.json"
})
