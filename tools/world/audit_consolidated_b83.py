"""Auditoria da B83 em saída separada; não reclassifica gates históricos."""
from pathlib import Path
import audit_slice_volume_b79 as audit
ROOT=Path(__file__).resolve().parents[2]
audit.GEOMETRY=ROOT/'artifacts/lacerda-controller/geometry_b83.json'
audit.OUT=ROOT/'docs/reports/blender/lacerda-consolidation-b83'
audit.SUFFIX='b83'
data=audit.load()
audit.cabin_sweep(data)
audit.character_sweep(data,skin=.015)
