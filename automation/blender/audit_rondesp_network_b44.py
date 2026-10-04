"""Auditoria integral read-only da candidata R30B.44."""
import runpy
from pathlib import Path
source={
 "file":"blender/salvador_lacerda_r30b44_proxy_misericordia.blend",
 "revision":"R30B.44",
 "status":"validation_candidate",
 "parent_file":"blender/salvador_lacerda_r30b43_twist_misericordia.blend",
 "evidence":"docs/reports/blender/misericordia_proxy_r30b44.json",
 "sha256":"e07323b0306f30cc7946dcfb61d47e9a2c349c6fc43448f8fc98239481b81f32"
}
runpy.run_path(str(Path(__file__).with_name("audit_rondesp_network.py")),init_globals={
 "BOAS_SOURCE_OVERRIDE":source,
 "BOAS_REPORT_PATH":"artifacts/roads/rondesp/rondesp_network_b44_candidate.json"
})
