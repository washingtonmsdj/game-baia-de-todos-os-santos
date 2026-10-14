"""Registrar a revisão já salva; não altera geometria ou fonte de produção."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = "docs/reports/blender/centro-expansion/"


def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf8"))


def write(path, value):
    dest = ROOT / path
    temporary = dest.with_suffix(dest.suffix + ".writing")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
    temporary.replace(dest)


def main():
    validation = read(REPORT + "validation_b74.json")
    source = validation["source"]
    with (ROOT / source["file"]).open("rb") as stream:
        assert hashlib.file_digest(stream, "sha256").hexdigest() == source["sha256"]
    assert validation["source_reopened"] and not validation["protected_changes"]
    catalogue_path = "world/areas/mvp-centro-lacerda/blender-revisions.json"
    catalogue = read(catalogue_path)
    assert catalogue["validation_source"]["file"] == source["file"]
    for entry in [catalogue["validation_source"], *catalogue["revisions"]]:
        if entry.get("file") == source["file"]:
            entry.update(source_reopened=True, local_geometry_checks_passed=True,
                         validation_evidence=REPORT + "validation_b74.json")
    write(catalogue_path, catalogue)
    scene = read(REPORT + "scene_b74.json")
    scene.update(source_reopened=True, validation_evidence=REPORT + "validation_b74.json",
                 visual_review_status="partial_two_driver_renders_checked_remaining_pending")
    write(REPORT + "scene_b74.json", scene)
    derivation = read(REPORT + "candidate_derivation.json")
    derivation["rejected_preapplication_domain"] = {
        "classification": "ERROR", "applied": False,
        "reason": "Recorte inicial abrangia ausência costeira; descartado antes da mutação. Recorte aplicado limitado à expansão terrestre sul/leste.",
        "source_dem_changed": False}
    write(REPORT + "candidate_derivation.json", derivation)
    preparation_path = "docs/reports/world/centro-lapa-tororo-fontenova/preparation.json"
    preparation = read(preparation_path)
    preparation.update(candidate_source=source, candidate_scene_applied=True,
                       candidate_application_evidence=REPORT + "scene_b74.json",
                       source_reopened=True, scene_merged=False,
                       scene_merged_meaning="Ambiente final não integrado; somente terreno e referências candidatos.",
                       car_traversal_done=True, car_traversal_method="replay_cinematico_e_sondagem_dos_quatro_apoios",
                       physical_vehicle_tested=False, final_roads_built=False,
                       vehicle_evidence=REPORT + "rondesp_ground_probe_b74.json")
    write(preparation_path, preparation)
    probe = read(REPORT + "rondesp_ground_probe_b74.json")
    ledger_path = "world/areas/centro-lapa-tororo-fontenova/road-corrections.json"
    issues = [{"issue_id": f"B74-grade-{i:03d}", "status": "pending", **entry}
              for i, entry in enumerate(probe["issues"], 1)]
    ledger = {"schema": "boas/road-corrections-v1", "area_id": "centro-lapa-tororo-fontenova",
              "cycle": "2026-10-05-B74", "source": source, "issues": issues,
              "threshold": {"grade": .30, "status": "candidate_review_criterion_not_legal_or_vehicle_limit"},
              "evidence": REPORT + "rondesp_ground_probe_b74.json", "production_ready": False,
              "pending": validation["pending"], "dynamic_physics_tested": False,
              "widths_verified": False, "pavement_built": False}
    write(ledger_path, ledger)
    core_path = "world/areas/mvp-centro-lacerda/road-corrections.json"
    core = read(core_path)
    assert len(core["issues"]) == 716
    if not any(c.get("cycle") == "2026-10-05-B74" for c in core["applied_corrections"]):
        core["applied_corrections"].append({
            "cycle": "2026-10-05-B74", "classification": "ADAPT_LOCAL",
            "scope": "Terreno e referências candidatos sul/leste; núcleo/costa/píeres preservados",
            "source_after": source, "source_reopened": True,
            "evidence": [REPORT + "scene_b74.json", REPORT + "validation_b74.json", ledger_path],
            "source_dem_changed": False, "global_z_scale_or_offset_applied": False,
            "road_width_changed": False, "geographic_fit_verified": False,
            "runtime_exported": False, "gameplay_approved": False})
    write(core_path, core)
    note = """## 05/10/2026 — B74: expansão candidata e revisão dos apoios da RONDESP

Fonte de validação: `blender/salvador_lacerda_r30b74_expansao_lapa_tororo_fonte_nova.blend`, SHA-256 `1b4c16b9831a38bff93e3fb9c03c87bdfaf3e48f5a00cf03e0945b7f6d9b220a`. Salva e reaberta na única janela MCP 9876; B73 preservada, autoria B41 e produção B30 mantidas. Controle em seis anchors explícitos; coincidência relativa conferida, georreferenciamento e altimetria absolutos continuam candidatos.

Terreno: 92.609 vértices/181.899 triângulos, recorte terrestre sul/leste sem preencher ausências costeiras; sem degenerados, vértices duplicados, triângulos invertidos ou arestas com mais de duas faces na nova malha. Bordas abertas correspondem ao domínio esperado. Fonte DEM preservada, interpolação bilinear e transição local de 120 unidades de projeto (não largura levantada), delta Z máximo 15,6795 unidades. Núcleo, HQ, costa, cais e píeres anteriores preservados. A projeção XY preexistente contém uma auto-interseção; o reparo foi restrito à máscara derivada, sem mudar a malha original.

7.952 traçados OSM são referência, não pavimento. Center Lapa (way 257113955), Arena Fonte Nova (relation 3346613, com anel interno) e Dique (relation 15601931) têm IDs e bindings; continuam proxies. A água do Dique tem cota candidata, sem medição absoluta. Não foram criados edifícios fictícios nem larguras ausentes. Terreno, referências, água e QA permanecem separados.

RONDESP V25 compartilhada por instância, câmera do motorista e três replays por grafo OSM. 10.173 posições/40.692 sondagens, sem apoio ausente das rodas. Restam 106 alertas em oito OSM ways, classificados NEEDS_REVIEW por inclinação acima do critério candidato de 30%; máximo 41,61%. Isto não é aprovação física, teste de obstáculos, prova de largura ou de acesso ao destino. Duas imagens do motorista conferidas mostram terreno/contornos sem ruas finais; screenshots 1×1 foram rejeitados. A captura restante falhou com disco cheio e deve ser refeita.

Evidências: `docs/reports/blender/centro-expansion/{scene_b74,validation_b74,candidate_derivation,rondesp_ground_probe_b74}.json`; ledger da nova área em `world/areas/centro-lapa-tororo-fontenova/road-corrections.json`. As 716 detecções antigas do MVP foram preservadas. Sem npm/build/suíte de testes, exportação ou promoção ao runtime. Próximo: revisão visual restante, perfis viários e fonte confiável para limites/larguras das vias; não alisar ladeiras reais só para reduzir alertas.

"""
    for name in ["docs/PROJECT_STATUS.md", "docs/CODEX_HANDOFF.md"]:
        path = ROOT / name
        text = path.read_text(encoding="utf8")
        if "## 05/10/2026 — B74: expansão candidata" not in text:
            first, rest = text.split("\n", 1)
            temp = path.with_suffix(".md.writing")
            temp.write_text(first + "\n\n" + note + rest.lstrip("\n"), encoding="utf8")
            temp.replace(path)
    print(json.dumps({"source_registered": True, "reopened": True,
                      "grade_issues_registered": len(issues), "old_issues_preserved": len(core["issues"]),
                      "production_ready": False}, ensure_ascii=False))


if __name__ == "__main__":
    main()
