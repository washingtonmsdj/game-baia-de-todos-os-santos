"""Auditoria integral read-only da candidata R30B.43."""
import json,runpy
from pathlib import Path
root=Path(__file__).resolve().parents[2]
source={
 "file":"blender/salvador_lacerda_r30b43_twist_misericordia.blend",
 "revision":"R30B.43",
 "status":"validation_candidate",
 "parent_file":"blender/salvador_lacerda_r30b42_superficie_misericordia.blend",
 "evidence":"docs/reports/blender/misericordia_twist_r30b43.json",
 "sha256":"de19d1f8aa672b38d56aa39b88ee1a34c852024fcc47c2ed177b4e9c3f1c3339"
}
runpy.run_path(str(Path(__file__).with_name("audit_rondesp_network.py")),init_globals={
 "BOAS_SOURCE_OVERRIDE":source,
 "BOAS_REPORT_PATH":"artifacts/roads/rondesp/rondesp_network_b43_candidate.json"
})
