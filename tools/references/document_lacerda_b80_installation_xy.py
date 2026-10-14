"""Consolida pesquisa específica SEMOB/XY/genealogia sem alterar a cena."""
import hashlib
import json
from pathlib import Path

import pdfplumber

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/reports/research/lacerda-b80-installation-xy"


def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def save(name, data):
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    genealogy = read("docs/reports/research/lacerda-b80-installation-xy/genealogy_snapshots_readonly.json")
    latest = genealogy["sources"][-1]
    earliest = genealogy["sources"][0]
    names = {o["name"] for o in earliest["shared_exact_world_offset"]}
    groups = {prefix: sum(o["name"].startswith(prefix) for o in latest["shared_exact_world_offset"]) for prefix in ["FUNCIONAL | 3", "FUNCIONAL | 4", "FUNCIONAL | soleira", "B79 | COLLISION"]}
    summary = {"status": "STILL_UNRESOLVED", "origin_semantic_context_found": True, "creation_operation_found": False, "first_introducing_revision": None, "first_preserved_snapshot": earliest["file"], "earlier_report_scene": "R27; metadado lower_terminal_r21", "semantic_context": "Cota inferior 7.406 e terreno 7.256 são aproximações do MVP, não levantamento oficial. Não é prova de introdução na R21.", "shared_exact_world_offset_by_snapshot": [{"file": r["file"], "count": len(r["shared_exact_world_offset"])} for r in genealogy["sources"]], "B80_groups": groups, "new_shared_objects": [o["name"] for o in latest["shared_exact_world_offset"] if o["name"] not in names], "direct_dependencies": latest["direct_dependencies"], "not_exact_transform_but_lower_level_consumers": [o for o in latest["tracked_elements"] if o["name"] in ["ESTAÇÃO INFERIOR | plataforma", "ESTAÇÃO INFERIOR | cobertura", "INFERIOR | piso do saguão"]], "consumer_scripts": ["automation/blender/derive_lacerda_walkability_b77.py:15-16", "automation/blender/model_lacerda_corridor_b77.py", "automation/blender/export_slice_collision_b79.py", "automation/blender/correct_corridor_doors_b77.py", "automation/blender/refine_lacerda_r30b03_exterior.py:35"], "bridge_by_snapshot": [], "correction_authorized": False}
    for source in genealogy["sources"]:
        obj = next(o for o in source["tracked_elements"] if o["name"] == "CALIBRADO | passarela piso 28.71 x 6.00m")
        summary["bridge_by_snapshot"].append({"file": source["file"], "local_min_x": obj["bounds_local"]["min"][0], "local_max_x": obj["bounds_local"]["max"][0], "longitudinal_extent": obj["bounds_local"]["max"][0]-obj["bounds_local"]["min"][0], "scale": obj["scale"], "parent": obj["parent"]})
    save("genealogy_summary.json", summary)
    controls, triangles = [], []
    raw = ROOT / "world-reference/mvp-centro-lacerda/research-20261006-issue22"
    for number, curve_index, indices in [(17, 1682, [5, 6, 14]), (12, 437, [0, 1, 3]), (13, 343, [0, 16, 23])]:
        path = raw / f"sucop-architectural-{number:02d}.pdf"
        with pdfplumber.open(path) as pdf:
            curve = pdf.pages[0].curves[curve_index]
            points = [list(curve["pts"][i]) for i in indices]
        a, b, c = points
        area = abs((b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]))/2
        assert area > 0
        triangles.append({"drawing_id": f"sucop-2023-{number:02d}", "non_collinear_document_points": True, "area_pdf_points_squared": area, "accepted_scene_correspondences": 0})
        for index, point in zip(indices, points):
            controls.append({"drawing_id": f"sucop-2023-{number:02d}", "control_id": f"XY-{number}-vector-{index}", "drawing_point": point, "drawing_frame": "PDF vector points; upper-left origin, not metric SSOT", "drawing_curve": curve_index, "drawing_vertex": index, "drawing_feature": "Quina do contorno estrutural documentado da região da torre; fase e face equivalente na cena pendentes", "scene_object": None, "scene_point": None, "source": f"source:lacerda-issue22-sucop-{number:02d}", "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "confidence": "DOCUMENT_POINT_IDENTIFIED_SCENE_MATCH_UNRESOLVED", "residual": None, "reason": "Os encontros documentais não têm correspondência física inequívoca com a malha dos obstáculos. Plataforma/cobertura retangulares não identificam por si só quinas de paredes/torre desenhadas. Não associar vértices de caixa aos encontros apenas por posição, nome ou número de pontos.", "accepted_for_registration": False})
    save("xy_controls_round2.json", {"controls": controls, "non_collinearity": triangles, "source_selection": "Pranchas 17/12/13 inspecionadas visualmente; 23 serve de controle vertical do baseline", "parent_ssot": "world/geographic-reference.json", "transform": None, "status": "STILL_UNRESOLVED", "metric_scale_from_pixels": False, "metric_scale_from_titleblock": False, "note": "Nove pontos no desenho não são nove correspondências. Nenhum fit foi calculado com pontos de cena inventados."})
    records = []
    for filename in ["semob_locators.json", "semob_navigation.json", "semob_search.json", "semob_annex_locators.json"]:
        records.extend(read(f"docs/reports/research/lacerda-b80-installation-xy/{filename}")["records"])
    save("source_summary.json", {"provider": "Prefeitura de Salvador / SEMOB e portais municipais", "process_target": "151228/2023", "contract_target": "008/2023", "inexigibility_target": "013/2023", "capture_date": "2026-10-06", "records": records, "release_status": "DEV_REFERENCE_ONLY", "installation_dimensions_found": False, "note": "Landing pages, respostas de busca, código público da aplicação e erros não são projeto básico/proposta/desenho executado. Não usar configuração de frontend para autenticação ou acesso reservado."})
    registry = read("world/data-provenance.json")
    resources = [{"resource_id": "source:lacerda-semob-locators-20261006", "provider": "Prefeitura de Salvador / SEMOB e portais municipais", "dataset": "Investigação pública de processo 151228/2023, contrato 008/2023 e inexigibilidade 013/2023", "capture_date": "2026-10-06", "bounds": None, "coordinates": None, "process": "151228/2023", "contract": "SEMOB 008/2023", "raw_files": [{"path": r["raw_file"], "sha256": r["sha256"], "url": r["requested_url"], "final_url": r.get("final_url"), "status_code": r.get("status_code")} for r in records if "raw_file" in r], "derived_objects": [], "purpose": "Localizar anexos da instalação atual; nenhum documento dimensional recuperado", "release_status": "DEV_REFERENCE_ONLY", "usage_class": "REFERENCIA_INTERNA", "dependencies": [], "kind": "document_reference", "evidence": "docs/reports/research/lacerda-b80-installation-xy/source_summary.json"}, {"resource_id": "derived:lacerda-b80-installation-xy-20261006", "provider": "Bay of All Saints / diagnóstico read-only", "dataset": "Genealogia de snapshots e controles documentais sem registro aprovado", "capture_date": "2026-10-06", "bounds": None, "raw_files": [], "inputs": [{"file": r["file"], "sha256": r["sha256"]} for r in genealogy["sources"]], "derived_objects": [], "purpose": "Rastrear transform inferior e passarela; comparar controles 12/13/17/23 sem alterar SSOT/cena", "release_status": "DEV_REFERENCE_ONLY", "usage_class": "REFERENCIA_INTERNA", "dependencies": ["source:lacerda-semob-locators-20261006"] + [f"source:lacerda-issue22-sucop-{n:02d}" for n in [12, 13, 17, 23]], "kind": "document_reference", "evidence": "docs/research/LACERDA_B80_INSTALLATION_XY_GENEALOGY_2026-10-06.md"}]
    ids = {r["resource_id"] for r in resources}
    registry["resources"] = [r for r in registry["resources"] if r["resource_id"] not in ids] + resources
    (ROOT / "world/data-provenance.json").write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    result = {"decision": "NO_SCENE_CHANGE", "ORIGIN_OF_3_709_FOUND": False, "SEMOB_INSTALLATION_DATA_FOUND": False, "XY_REGISTRATION_ACCEPTED": False, "status": "STILL_UNRESOLVED", "origin_context_partial": True, "B81_created": False, "CCD_repeated": False, "production_exported": False, "witnesses": {"UNRESOLVED": 27}, "note": "Origem semântica parcial, sem operação/revisão introdutora comprovada; nenhum dado de instalação dimensional nem correspondência XY aceita"}
    save("result.json", result)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
