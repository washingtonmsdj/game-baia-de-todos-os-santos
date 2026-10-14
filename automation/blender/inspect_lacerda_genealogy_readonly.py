"""Leitura de snapshots históricos; não cria objetos, não salva nem anima."""
import bpy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/reports/research/lacerda-b80-installation-xy"
OUT.mkdir(parents=True, exist_ok=True)
sources = [ROOT / "blender/salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a_structure_ref.blend", ROOT / "blender/salvador_lacerda_r30b01_refinamento.blend", ROOT / "blender/salvador_lacerda_r30b80_piso_e_embarque_superior.blend"]
targets = {"FUNCIONAL | 3 soleira inferior", "FUNCIONAL | soleira inferior", "ESTAÇÃO INFERIOR | plataforma", "ESTAÇÃO INFERIOR | cobertura", "CALIBRADO | passarela piso 28.71 x 6.00m", "CALIBRADO | passarela cobertura 28.71 x 6.00m", "INFERIOR | piso do saguão"}
reports = []
for source in sources:
    before = hashlib.sha256(source.read_bytes()).hexdigest()
    if Path(bpy.data.filepath).resolve() != source.resolve():
        bpy.ops.wm.open_mainfile(filepath=str(source))
    selected, sharing = [], []
    for obj in bpy.context.scene.objects:
        if obj.type != "MESH":
            continue
        offset = abs(obj.matrix_world.translation.z + 3.70900011062622) < 1e-6
        if obj.name not in targets and not offset:
            continue
        local = [list(v.co) for v in obj.data.vertices]
        world = [list(obj.matrix_world @ v.co) for v in obj.data.vertices]
        if not local:
            continue
        row = {"name": obj.name, "location": list(obj.location), "matrix_world": [list(r) for r in obj.matrix_world], "parent": obj.parent.name if obj.parent else None, "scale": list(obj.scale), "bounds_local": {"min": [min(v[i] for v in local) for i in range(3)], "max": [max(v[i] for v in local) for i in range(3)]}, "bounds_world": {"min": [min(v[i] for v in world) for i in range(3)], "max": [max(v[i] for v in world) for i in range(3)]}, "properties": {k: obj[k] for k in obj.keys() if isinstance(obj[k], (str, int, float, bool))}, "collections": [c.name for c in obj.users_collection], "hidden_object": obj.hide_get(), "hidden_render": obj.hide_render, "vertices": len(local)}
        if obj.name in targets:
            selected.append(row)
        if offset:
            sharing.append(row)
    shared_names = {o["name"] for o in sharing}
    dependencies = [{"name": o.name, "parent": o.parent.name if o.parent else None, "constraints": [{"name": c.name, "type": c.type, "target": getattr(c, "target", None).name if getattr(c, "target", None) else None} for c in o.constraints]} for o in bpy.context.scene.objects if (o.parent and o.parent.name in shared_names) or any(getattr(c, "target", None) and c.target.name in shared_names for c in o.constraints)]
    props = {k: bpy.context.scene[k] for k in bpy.context.scene.keys() if k in ["lower_terminal_r21", "mvp_terrain_method", "mvp_terrain_source"]}
    assert hashlib.sha256(source.read_bytes()).hexdigest() == before
    reports.append({"file": source.relative_to(ROOT).as_posix(), "sha256": before, "objects_total": len(bpy.context.scene.objects), "scene_properties": props, "tracked_elements": selected, "shared_exact_world_offset": sharing, "direct_dependencies": dependencies})
result = {"read_only": True, "saved": False, "sources": reports, "first_introducing_revision": None, "note": "A sessão background só lê snapshots preservados. Coincidência numérica não comprova intenção compartilhada; ausência de parent/constraint não exclui consumidores externos de cotas."}
(OUT / "genealogy_snapshots_readonly.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"read_only": True, "saved": False, "snapshots": [{"file": r["file"], "shared_offset": len(r["shared_exact_world_offset"]), "dependencies": len(r["direct_dependencies"])} for r in reports]}))
