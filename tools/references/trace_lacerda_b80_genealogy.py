"""Histórico read-only de offset e passarela; não executa scripts de cena."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/reports/research/lacerda-b80-installation-xy"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    paths = ["docs/reports/blender/r30a/georef_hints.json", "docs/reports/blender/r30a/structural_scene_audit_before.json", "docs/reports/blender/r30a1/structural_scene_audit_before.json"]
    target = {"FUNCIONAL | 3 soleira inferior", "FUNCIONAL | soleira inferior", "ESTAÇÃO INFERIOR | plataforma", "ESTAÇÃO INFERIOR | cobertura", "CALIBRADO | passarela piso 28.71 x 6.00m", "CALIBRADO | passarela cobertura 28.71 x 6.00m", "INFERIOR | piso do saguão"}
    reports = []
    for path in paths:
        raw = (ROOT / path).read_bytes()
        data = json.loads(raw)
        rows = []
        for row in data.get("objects", []):
            if row.get("name") in target:
                rows.append(row)
        props = data.get("scene_properties", {})
        selected_props = {k: v for k, v in props.items() if k in ["mvp_terrain_method", "lower_terminal_r21", "mvp_terrain_source", "terrain_surface_revision"]}
        reports.append({"path": path, "sha256": hashlib.sha256(raw).hexdigest(), "blend_file": data.get("blend_file"), "generated_at": data.get("generated_at"), "properties": selected_props, "objects": rows})
    commits = {}
    for token in ["3.709", "28.71", "lower_terminal_r21", "55.539"]:
        commits[token] = subprocess.check_output(["git", "log", "--all", "--format=%H %ad %s", "--date=iso", "--name-only", "-S", token, "--", "automation", "docs", "tools"], cwd=ROOT, text=True, encoding="utf-8")
    evidence = {"status": "STILL_UNRESOLVED", "decision": "NO_SCENE_CHANGE", "reports": reports, "git_pickaxe": commits, "first_introducing_revision": None, "semantic_hint": "lower_terminal_r21 registra cota aproximada do MVP 7.406, não levantamento oficial; isso não prova que R21 introduziu o transform", "note": "Primeira ocorrência em relatório/commit não equivale à operação que criou o offset ou deformou a passarela. Não executar scripts históricos."}
    (OUT / "genealogy_history.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"reports": [{"path": r["path"], "blend_file": r["blend_file"], "objects": [{"name": o["name"], "location_world": o.get("location_world"), "bounds_world": o.get("bounds_world"), "properties": o.get("properties")} for o in r["objects"]], "scene_properties": r["properties"]} for r in reports]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
