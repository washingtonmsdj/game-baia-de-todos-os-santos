"""Diagnóstico read-only da B80: controles estáticos, matrizes e níveis.

Permitido em background somente para leitura; não salva, cria ou altera objetos.
"""
import bpy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/reports/research/lacerda-registration-b80"
OUT.mkdir(parents=True, exist_ok=True)
source = ROOT / "blender/salvador_lacerda_r30b80_piso_e_embarque_superior.blend"
assert Path(bpy.data.filepath).resolve() == source.resolve()
assert hashlib.sha256(source.read_bytes()).hexdigest() == "2dc973c3efc4710cf268b348d4892fc17df0c2ac2ecef0e2e45d0493c249e4c4"
names = []
rows = []
for ob in bpy.context.scene.objects:
    if not any(ob.name.startswith(p) for p in ["ESTAÇÃO ", "CALIBRADO |", "SUPERIOR |", "INFERIOR |", "TORRE |", "PASSARELA |", "LAC R30B | Passarela", "FUNCIONAL | 3 piso", "FUNCIONAL | 3 soleira", "FUNCIONAL | soleira"]):
        continue
    if ob.type != "MESH":
        continue
    points = [list(ob.matrix_world @ v.co) for v in ob.data.vertices]
    parents = []
    ancestor = ob.parent
    while ancestor:
        parents.append({"name": ancestor.name, "matrix_world": [list(r) for r in ancestor.matrix_world], "scale": list(ancestor.scale)})
        ancestor = ancestor.parent
    rows.append({"name": ob.name, "matrix_world": [list(r) for r in ob.matrix_world], "matrix_basis": [list(r) for r in ob.matrix_basis], "scale": list(ob.scale), "location": list(ob.location), "rotation_euler": list(ob.rotation_euler), "parent_chain": parents, "vertices_world": points if len(points) <= 5000 else None, "vertices": len(points), "bounds": {"min": [min(p[i] for p in points) for i in range(3)], "max": [max(p[i] for p in points) for i in range(3)]}, "local_bounds": {"min": [min(v.co[i] for v in ob.data.vertices) for i in range(3)], "max": [max(v.co[i] for v in ob.data.vertices) for i in range(3)]}, "modifiers": [{"name": m.name, "type": m.type} for m in ob.modifiers], "properties": {k: ob[k] for k in ob.keys() if isinstance(ob[k], (str, int, float, bool))}, "collections": [c.name for c in ob.users_collection]})
report = {"source": {"file": source.relative_to(ROOT).as_posix(), "sha256": "2dc973c3efc4710cf268b348d4892fc17df0c2ac2ecef0e2e45d0493c249e4c4"}, "read_only": True, "saved": False, "frame": bpy.context.scene.frame_current, "objects_total": len(bpy.context.scene.objects), "units": {"system": bpy.context.scene.unit_settings.system, "scale_length": bpy.context.scene.unit_settings.scale_length}, "objects": rows, "note": "Base meshes/world transforms da fonte salva; bounds não identificam automaticamente controles arquitetônicos."}
(OUT / "scene_controls_readonly.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"read_only": True, "saved": False, "objects": len(rows)}))
