"""Registro derivado da pesquisa #22: compara controles, nunca modifica a cena.

Transformação Z de diagnóstico não é registro XY aprovado. Controles sem
correspondência inequívoca continuam nulos/rejeitados; não há nearest-neighbour.
"""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/reports/research/lacerda-registration-b80"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    baseline = load(ROOT / "docs/reports/research/lacerda-issue22/reconciliation.json")
    snapshot = load(OUT / "scene_controls_readonly.json")
    scene = {row["name"]: row for row in snapshot["objects"]}
    source_hash = baseline["protected_revisions"][-1]["actual_sha256"]
    assert snapshot["source"]["sha256"] == source_hash and snapshot["saved"] is False
    ssot_path = ROOT / "world/geographic-reference.json"
    assert hashlib.sha256(ssot_path.read_bytes()).hexdigest() == baseline["ssot_sha256"]
    raw = ROOT / "world-reference/mvp-centro-lacerda/research-20261006-issue22"
    purpose = {
        17: ("primary_xy_upper", "Acesso superior, limites da passarela e contorno esquemático da torre"),
        12: ("primary_xy_lower", "Desembarque inferior, saguão, túnel e torre"),
        13: ("primary_xy_lower_roof", "Cobertura inferior e relação com torre; duas aberturas de iluminação"),
        23: ("primary_z", "Cortes AA/BB e cotas dos acessos, cobertura inferior e passarela"),
        21: ("primary_z_crosscheck", "Cortes construtivos AA/BB; existente/proposto"),
        24: ("secondary_z", "CC/DD, estrutura do acesso superior; escala de carimbo conflitante"),
        3: ("context_only", "Construção/demolição inferior; não duplicar controles da 12"),
        4: ("context_only", "Construção/demolição da cobertura; não duplicar controles da 13"),
        8: ("context_only", "Construção/demolição superior; não duplicar controles da 17"),
        22: ("context_only", "CC/DD construtivos; escala conflitante; não valida perfil longitudinal sozinho"),
        31: ("services_only", "Instalações/teto inferior não equivalem à laje do poço"),
        34: ("services_only", "Grelhas/teto superior não equivalem à cabine ou à laje estrutural"),
    }
    selections = [{"drawing_id": f"sucop-2023-{n:02d}", "resource_id": f"source:lacerda-issue22-sucop-{n:02d}", "role": role, "reason": reason, "registration_approved": False} for n, (role, reason) in purpose.items()]
    # Pontos são níveis documentais impressos; XY do ponto na prancha desconhecido.
    levels = [
        ("upper-platform", 0.0, "ESTAÇÃO SUPERIOR | plataforma"),
        ("bridge-roof", 4.0, "CALIBRADO | passarela cobertura 28.71 x 6.00m"),
        ("lower-roof", -53.17, "ESTAÇÃO INFERIOR | cobertura"),
        ("lower-platform", -58.93, "ESTAÇÃO INFERIOR | plataforma"),
    ]
    upper = scene[levels[0][2]]["bounds"]["max"][2]
    controls = []
    for drawing in [21, 23]:
        for feature, documented_z, name in levels:
            obj = scene[name]
            top = obj["bounds"]["max"][2]
            vertices = [v for v in obj["vertices_world"] if abs(v[2] - top) < 1e-5]
            point = [sum(v[i] for v in vertices) / len(vertices) for i in range(3)]
            controls.append({"control_id": f"C{drawing}-{feature}", "drawing_id": f"sucop-2023-{drawing:02d}", "drawing_point": [None, None, documented_z], "drawing_point_frame": "datum local do projeto, metros; XY não estabelecido", "scene_object": name, "scene_point": point, "scene_point_frame": "world/geographic-reference.json; unidade nominal 1m não levantada", "source": f"source:lacerda-issue22-sucop-{drawing:02d}", "confidence": "candidate_correspondence", "residual": {"z_anchored_upper": top - (upper + documented_z), "xy": None}, "reason": "Plano superior da mesh medido diretamente; nível impresso no corte. Associação física ainda candidata: nenhuma porta/cabine usada como controle. Falta identificar no desenho o mesmo plano estrutural e estado executado.", "accepted_for_registration": False, "independent_feature": feature, "roof_plane_ambiguity": "Cota do desenho e topo/impermeabilização versus centro da mesh precisam de confirmação" if "roof" in feature else None})
    offsets = [scene[name]["bounds"]["max"][2] - z for _, z, name in levels]
    offset_fit = sum(offsets) / len(offsets)
    residuals = [v - offset_fit for v in offsets]
    save("vertical_registration.json", {"schema": "boas/drawing-registration-v1", "parent_ssot": "world/geographic-reference.json", "ssot_sha256": baseline["ssot_sha256"], "scene_source": snapshot["source"], "decision": "NO_SCENE_CHANGE", "status": "PARTIAL_DIAGNOSTIC_NOT_REGISTERED", "selected_sheets": selections, "controls": controls, "candidate_Z_only": {"scale_fixed": 1.0, "upper_anchor_offset": upper, "least_squares_offset_diagnostic_only": offset_fit, "rms_candidate_residual": math.sqrt(sum(r*r for r in residuals)/len(residuals)), "residuals": residuals, "unique_physical_level_features": 4, "independent_documents": "21 e 23 pertencem ao mesmo projeto; repetição não acrescenta quatro controles independentes", "accepted_controls": 0, "XY_transform": None, "full_transform": None, "applied": False}, "registration_gate": "blocked: faltam >=3 controles físicos não colineares XY com associação inequívoca e calibração por cotas; comparação Z isolada não basta"})

    # Extração de coordenadas vetoriais, não medidas físicas por pixels ou carimbo.
    import pdfplumber
    vector_controls = []
    for n, curve_index, indices in [(12, 437, [0, 1, 3]), (17, 1682, [5, 6, 14])]:
        with pdfplumber.open(raw / f"sucop-architectural-{n:02d}.pdf") as pdf:
            curve = pdf.pages[0].curves[curve_index]
            assert curve["stroke"] and not curve["fill"]
            for number, index in enumerate(indices, 1):
                xy = list(curve["pts"][index])
                vector_controls.append({"control_id": f"XY-{n}-{number}", "drawing_id": f"sucop-2023-{n:02d}", "drawing_point": xy, "drawing_point_frame": "PDF points, origem superior esquerda; não é coordenada métrica", "vector_curve_index": curve_index, "vector_vertex_index": index, "scene_object": None, "scene_point": None, "source": f"source:lacerda-issue22-sucop-{n:02d}", "confidence": "unmatched", "residual": None, "reason": "Quina do contorno vetorial da região da torre: a B80 contém plataformas retangulares e elementos de fases diferentes, sem vínculo físico suficiente com esta quina. Não escolher vértice por proximidade ou pelo nome.", "accepted_for_registration": False})
    # A cobertura inferior não ganha um registro próprio apenas por alinhamento visual.
    for feature in ["encontro cobertura/torre", "quina estrutural da cobertura", "limite permanente do saguão"]:
        vector_controls.append({"control_id": "XY-13-" + str(len(vector_controls)-5), "drawing_id": "sucop-2023-13", "drawing_point": None, "scene_object": None, "scene_point": None, "source": "source:lacerda-issue22-sucop-13", "confidence": "unmatched", "residual": None, "reason": feature + ": candidato buscado, sem identificação inequívoca dos mesmos pontos na cena; nenhum registro independente foi ajustado para encaixar a cobertura.", "accepted_for_registration": False})
    save("xy_control_attempts.json", {"schema": "boas/drawing-control-attempts-v1", "controls": vector_controls, "transform_to_ssot": None, "physical_dimensions_from_pixels": False, "scale_from_titleblock": False, "status": "UNRESOLVED", "note": "Pontos vetoriais extraídos são candidatos documentais, não controles físicos já aceitos. Não bastam três pontos na mesma curva para provar a associação com a B80."})

    low = scene["FUNCIONAL | 3 soleira inferior"]
    high = scene["FUNCIONAL | 3 soleira superior"]
    local_low = low["local_bounds"]["min"][2]
    world_low = low["bounds"]["min"][2]
    world_high = high["bounds"]["min"][2]
    motion = load(ROOT / "docs/reports/blender/lacerda-controller-b80/cabin_sweep_b80.json")["motion"]["translation"][2]
    roof_top = scene["ESTAÇÃO INFERIOR | cobertura"]["bounds"]["max"][2]
    floor_top = scene["ESTAÇÃO INFERIOR | plataforma"]["bounds"]["max"][2]
    bridge = scene["CALIBRADO | passarela piso 28.71 x 6.00m"]
    lengths = [bridge["local_bounds"]["max"][i] - bridge["local_bounds"]["min"][i] for i in range(3)]
    save("vertical_decomposition.json", {"schema": "boas/architectural-diagnostic-v1", "unit_status": snapshot["units"], "physical_scale_survey_verified": False, "travel_CCD": abs(motion), "historical_travel": 59.0, "project_access_difference": 58.93, "difference_CCD_project": abs(motion)-58.93, "lower_sill": {"object": low["name"], "local_bottom": local_low, "world_bottom": world_low, "matrix_world": low["matrix_world"], "parent_chain": low["parent_chain"], "translation_z": low["matrix_world"][2][3]}, "upper_sill": {"world_bottom": world_high, "matrix_world": high["matrix_world"], "parent_chain": high["parent_chain"]}, "decomposition": {"upper_minus_untranslated_lower_mesh": world_high-local_low, "lower_transform_contribution": -low["matrix_world"][2][3], "historical_minus_2023": 59.0-58.93, "nominal_sum": -low["matrix_world"][2][3]+59.0-58.93, "float_geometry_roundoff": world_high-world_low-abs(motion)}, "architecture_platform_difference": upper-floor_top, "lower_floor_roof_distance_top_to_top": roof_top-floor_top, "documented_lower_floor_roof_distance": 5.76, "roof_minus_floor_distance_residual_candidate": roof_top-floor_top-5.76, "origin_vs_transform": "Offset Z uniforme de datum cancela na diferença entre acessos. A contribuição -3,709 é local à soleira inferior, sem parent, e já aparece no inventário anterior B77. Não é escala Z global nem evidência de que deve ser desfeita.", "historical_trace": "docs/reports/blender/lacerda-corridor/inventory_before_b77.json", "first_introducing_revision": None, "original_transform_intent": None, "bridge_geometry": {"object": bridge["name"], "actual_local_extents": lengths, "object_scale": bridge["scale"], "parent_chain": bridge["parent_chain"], "matrix_world": bridge["matrix_world"], "warning": "Nome mantém 28.71 mas extensão real no eixo longitudinal é ~55.54; não usar nome ou dimensão publicada como controle aceito. Não autoriza encurtar passarela sem registro."}, "correction_authorized": False})
    witnesses = load(ROOT / "docs/reports/research/lacerda-issue22/witness_triage.json")["witnesses"]
    updated = []
    for w in witnesses:
        updated.append({**w, "registration_classification": "UNRESOLVED", "registration_evidence": ["vertical_registration.json", "xy_control_attempts.json", "vertical_decomposition.json"], "registered_physical_correspondence": False, "reason_after_registration_attempt": "Os controles Z permitem diagnóstico de deslocamento, mas XY e perfil estrutural não foram registrados com três correspondências físicas verificadas; arquitetura e cabine continuam hipóteses sem atribuição exclusiva.", "authorized_correction": None})
    save("witness_reclassification.json", {"schema": "boas/registered-witness-triage-v1", "allowed_classes": ["ARCHITECTURE_CONFIRMED_WRONG", "CABIN_CANDIDATE_WRONG", "BOTH_POSSIBLE", "CONTACT_ONLY", "UNRESOLVED"], "witnesses": updated, "counts": {"UNRESOLVED": 27}, "contact_only_solid_witnesses": 0, "movement_enabled": False, "decision": "NO_SCENE_CHANGE", "note": "UNRESOLVED não apaga o ERROR geométrico original; CONTACT_ONLY não foi usado para penetrações sólidas. Os outros 27 pares superficiais continuam no baseline para triagem, sem promoção automática."})
    registry_path = ROOT / "world/data-provenance.json"
    registry = load(registry_path)
    resource = {"resource_id": "derived:lacerda-registration-b80-20261006", "provider": "Bay of All Saints / diagnóstico read-only B80 + SUCOP 2023", "dataset": "Registro arquitetônico parcial; transformação não aprovada", "capture_date": "2026-10-06", "bounds": None, "coordinates": None, "raw_files": [], "derived_objects": [], "dependencies": [f"source:lacerda-issue22-sucop-{n:02d}" for n in [12, 13, 17, 21, 23, 24]], "inputs": [snapshot["source"], {"file": "world/geographic-reference.json", "sha256": baseline["ssot_sha256"]}], "purpose": "Investigar níveis e correspondências das 27 testemunhas, sem produzir geometria ou promover fonte temporária", "release_status": "DEV_REFERENCE_ONLY", "usage_class": "REFERENCIA_INTERNA", "kind": "document_reference", "evidence": "docs/research/LACERDA_B80_CONTROLLED_REGISTRATION_2026-10-06.md", "derived_reports": [f"docs/reports/research/lacerda-registration-b80/{name}" for name in ["scene_controls_readonly.json", "vertical_registration.json", "xy_control_attempts.json", "vertical_decomposition.json", "witness_reclassification.json"]]}
    registry["resources"] = [r for r in registry["resources"] if r["resource_id"] != resource["resource_id"]] + [resource]
    registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"decision": "NO_SCENE_CHANGE", "vertical_comparison_controls": len(controls), "xy_controls_attempted": len(vector_controls), "accepted_full_registration_controls": 0, "lower_offset": low["matrix_world"][2][3], "witnesses": len(updated)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
