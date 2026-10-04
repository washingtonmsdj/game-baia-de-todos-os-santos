"""Executa auditoria integral da B42 sem promovê-la no registro."""
import runpy,json,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[2]
blend=root/"blender/salvador_lacerda_r30b42_superficie_misericordia.blend"
source={"file":blend.relative_to(root).as_posix(),"revision":"R30B.42","status":"validation_candidate","sha256":hashlib.sha256(blend.read_bytes()).hexdigest()}
runpy.run_path(str(root/"automation/blender/audit_rondesp_network.py"),init_globals={
 "BOAS_SOURCE_OVERRIDE":source,
 "BOAS_REPORT_PATH":"artifacts/roads/rondesp/rondesp_network_b42_candidate.json",
})
