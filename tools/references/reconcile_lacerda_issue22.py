"""Reconcilia evidência documental com auditorias B80, sem executar Blender.

As observações são um registro humano independente; este script organiza e
verifica rastreabilidade, não determina uma correção arquitetônica automática.
"""
from __future__ import annotations

import collections
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/reports/research/lacerda-issue22"
B80 = ROOT / "docs/reports/blender/lacerda-controller-b80"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def dictionaries(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from dictionaries(child)
    elif isinstance(value, list):
        for child in value:
            yield from dictionaries(child)


def main():
    validation = read(B80 / "validation_b80.json")
    sweep = read(B80 / "cabin_sweep_b80.json")
    triage = read(B80 / "triage_b80.json")
    geometry = read(ROOT / "artifacts/lacerda-controller/geometry_b80.json")
    observations = read(ROOT / "docs/research/LACERDA_DRAWING_OBSERVATIONS_2026-10-06.json")
    revisions = read(ROOT / "world/areas/mvp-centro-lacerda/blender-revisions.json")
    source = validation["source"]
    assert sweep["source"]["sha256"] == geometry["source"]["sha256"] == source["sha256"]

    protected = validation["protected_sources"] + [source]
    preservation = []
    for expected in protected:
        record = next(r for r in dictionaries(revisions) if r.get("revision") == expected["revision"] and r.get("file"))
        actual = digest(ROOT / record["file"])
        assert actual == expected["sha256"], (record["file"], "Hash divergiu; interromper reconciliação")
        preservation.append({"file": record["file"], "revision": expected["revision"], "expected_sha256": expected["sha256"], "actual_sha256": actual, "preserved": True})
    ssot = ROOT / "world/geographic-reference.json"
    assert digest(ssot) == "1d9da0962d456cb38ed3df0da797208e499a8465f82e9836c14bb337df2385e7"
    canonical = [{"file": p.relative_to(ROOT).as_posix(), "sha256": digest(p)} for p in sorted(B80.glob("*.json"))]
    canonical.append({"file": "docs/LACERDA_CORRIDOR_B80.md", "sha256": digest(ROOT / "docs/LACERDA_CORRIDOR_B80.md")})
    for file in ["corridor-slice.json", "slice-engine-contract-b80.json", "upper-boarding-evidence-b80.json"]:
        path = ROOT / "world/areas/mvp-centro-lacerda" / file
        canonical.append({"file": path.relative_to(ROOT).as_posix(), "sha256": digest(path)})
    previous_path = OUT / "reconciliation.json"
    if previous_path.exists():
        for previous in read(previous_path)["canonical_local_reports"]:
            assert digest(ROOT / previous["file"]) == previous["sha256"], (previous["file"], "Baseline documental B80 mudou; não sobrescrever")

    contacts = {(r["cabin_component"], r["obstacle"]): r for r in sweep["contacts"]}
    objects = {r["name"]: r for r in geometry["objects"]}
    groups = {
        "ESTAÇÃO SUPERIOR | plataforma": ("upper-platform", [8, 17, 21, 23, 24, 34]),
        "ESTAÇÃO INFERIOR | cobertura": ("lower-roof", [4, 13, 21, 23, 31]),
        "ESTAÇÃO INFERIOR | plataforma": ("lower-platform", [3, 12, 21, 23]),
    }
    witnesses = []
    for number, original in enumerate(triage["solid_penetration_witnesses"], 1):
        contact = contacts[(original["component"], original["obstacle"])]
        obj = objects[original["obstacle"]]
        group, sheets = groups[original["obstacle"]]
        witnesses.append({
            "witness_id": f"B80-W{number:02d}", "group": group,
            "component": original["component"], "obstacle": original["obstacle"],
            "t_witness": original["t_witness"], "floor_z_scene_units": original["floor_z"],
            "surface_contact_interval": {"first": contact["t_first"], "last": contact["t_last"]},
            "interval_note": "Intervalo de contato de superfícies do par; não afirmar penetração sólida em todo o intervalo.",
            "intersection_type": "strict_vertex_inside_watertight_convex_solid",
            "scene_detection_classification": original["classification"],
            "independent_correction_classification": "NEEDS_REVIEW",
            "scene_source": source, "geometry_export": "artifacts/lacerda-controller/geometry_b80.json",
            "obstacle_bounds": obj["geometry"]["bounds"],
            "complete_mesh": obj["geometry"]["complete_mesh"],
            "object_provenance_properties": obj["properties"],
            "source_binding_verified": False,
            "independent_evidence": [f"source:lacerda-issue22-sucop-{n:02d}" for n in sheets] + ["source:lacerda-issue22-sbqp-2025", "source:lacerda-issue22-sucop-memorial"],
            "justification": "Penetração comprovada na geometria candidata B80. Projeto oficial sustenta relações de acesso/torre/laje, mas não há registro desenho→SSOT por controles nem desenho das cabines atuais. O nome da mesh não prova correspondência arquitetônica. Não é possível atribuir o conflito exclusivamente à laje ou à cabine/posição candidata.",
            "authorized_correction": None,
            "next_evidence": "Registrar pranchas com controles independentes, esclarecer estado executado e obter plano de montagem/levantamento cabine–poço–soleiras.",
        })
    assert len(witnesses) == 27 and len({(r["component"], r["obstacle"]) for r in witnesses}) == 27
    summary = collections.Counter(r["group"] for r in witnesses)
    write(OUT / "witness_triage.json", {"schema": "boas/lacerda-documentary-triage-v1", "source": source, "decision": "NO_SCENE_CHANGE", "movement_enabled": False, "witness_count": 27, "group_counts": dict(summary), "witnesses": witnesses, "other_contacts": {"total_surface_pairs": len(sweep["contacts"]), "without_solid_witness": len(sweep["contacts"]) - len(witnesses), "classification": "NEEDS_REVIEW", "note": "Contato/tangência não vira erro automaticamente; triagem documental não elimina a penetração sólida original."}})

    travel = abs(sweep["motion"]["translation"][2])
    unknowns = []
    for key, purpose in [
        ("upper_door_clear_width", "Largura livre da porta do elevador, não da entrada externa"),
        ("upper_door_and_sill_position", "Posição atual porta/soleira relativamente à cabine"),
        ("sill_gap", "Vão e perfil da soleira, offsets não medidos"),
        ("cabin_width_depth_height", "Dimensões das novas cabines; desenho fabricante não recuperado"),
        ("shaft_internal_profile", "Perfil interno, folgas positivas, pit e topo do poço"),
        ("counterweight_and_equipment_envelope", "Não inferir de vistas externas ou corte esquemático"),
        ("slab_openings_registered_to_ssot", "Contorno e espessuras vinculados a controles verificados"),
        ("current_vertical_alignment", "Alinhamento físico dos dois desembarques após a obra"),
        ("absolute_vertical_datum", "Vinculação do zero local 2023 ao SSOT"),
        ("as_built_2025", "Continuidade do projeto R00 no estado executado atual"),
    ]:
        unknowns.append({"parameter": key, "verified_current_value": None, "classification": "UNKNOWN", "reason": purpose, "gate_effect": "blocked"})
    comparison = read(B80 / "upper_investigation_b80.json")
    write(OUT / "unknown_matrix.json", {"schema": "boas/lacerda-evidence-matrix-v1", "source": source,
        "documented_project": observations, "current_configuration_verified": False,
        "diagnostic": {"scene_travel_design_units": travel, "historical_travel_m": 59.0, "project_level_difference_m": 58.93, "scene_minus_historical_if_units_are_metres": travel-59.0, "scene_minus_project_if_units_are_metres": travel-58.93, "classification": "NEEDS_REVIEW", "authorization": "Nenhuma reescala, offset, recorte ou movimento de Hero autorizado por estas diferenças."},
        "unknowns": unknowns, "B78_comparison": {"canonical": "docs/reports/blender/lacerda-controller-b80/upper_investigation_b80.json", "mesh_count": len(comparison["comparison"]), "scope": comparison["B78_scope"], "new_evidence": "Plantas superiores confirmam organização geral dos acessos; não certificam os retornos/lambris/rodapés/verga alterados nem suas coordenadas B78.", "migrations": [{"object": r["object"], "classification": "NEEDS_REVIEW", "authorized": False} for r in comparison["comparison"]]},
        "ground_following": {"upper_penetrating_segments": 0, "upper_support_pending": 18, "lower_penetrating_segments": 9, "changed": False, "source": "docs/reports/blender/lacerda-controller-b80/ground_following_b80.json"},
        "aleph": {"reused": True, "new_capture": False, "evidence": "world/areas/mvp-centro-lacerda/upper-boarding-evidence-b80.json", "limit": "Panoramas existentes não revelam interiores; OSM/DEM não medem soleiras, cabines ou espessuras das lajes. Não usar essas fontes para certificar dimensões ocultas."}})

    drawings = read(OUT / "drawings_acquisition.json")["documents"]
    registry_path = ROOT / "world/data-provenance.json"
    registry = read(registry_path)
    records = []
    for drawing in drawings:
        number = drawing["prancha"]
        records.append({"resource_id": f"source:lacerda-issue22-sucop-{number:02d}", "provider": "Prefeitura de Salvador / SUCOP; A+P Arquitetos Associados", "dataset": drawing["name"], "capture_id": "lacerda-issue22-20261006", "capture_date": "2026-10-06", "bounds": None, "coordinates": None, "raw_files": [{"path": drawing["raw_file"], "sha256": drawing["sha256"]}], "source_url": drawing["download_url"], "official_distribution": "https://sucop.salvador.ba.gov.br/wp-content/uploads/2023/10/EDITAL-CONCORRENCIA-No-24-2023.pdf", "author": observations["author"], "document_date": observations["sheets"][str(number)]["date"], "sheet": number, "revision": "R00", "scale": observations["sheets"][str(number)], "evidence_class": "OFFICIAL_DRAWING", "release_status": "DEV_REFERENCE_ONLY", "usage_class": "REFERENCIA_INTERNA", "purpose": "Investigação independente B80; nenhuma geometria derivada nesta rodada", "derived_objects": [], "dependencies": [], "as_built_verified": False, "license": "Disponibilização pública não comprova autorização de redistribuição; binário fora do Git/release", "evidence": "docs/reports/research/lacerda-issue22/witness_triage.json", "kind": "document_reference"})
    acquired = read(OUT / "acquisition.json")["sources"]
    for key, resource_id, author, evidence_class, date in [
        ("sucop-concorrencia-24-2023", "source:lacerda-issue22-sucop-edital", "Prefeitura de Salvador / SUCOP", "OFFICIAL_TEXT", "2023-10"),
        ("sbqp-2025-restoration", "source:lacerda-issue22-sbqp-2025", "Nivaldo Vieira de Andrade Junior", "ACADEMIC_SECONDARY", "2025"),
    ]:
        row = next(r for r in acquired if r["id"] == key)
        records.append({"resource_id": resource_id, "provider": author, "author": author, "dataset": key, "capture_date": "2026-10-06", "document_date": date, "bounds": None, "raw_files": [{"path": row["raw_file"], "sha256": row["sha256"]}], "source_url": row["requested_url"], "evidence_class": evidence_class, "release_status": "DEV_REFERENCE_ONLY", "usage_class": "REFERENCIA_INTERNA", "purpose": "Contexto documental e descoberta de pranchas; não autoriza medida fotográfica", "derived_objects": [], "dependencies": [], "kind": "document_reference", "evidence": "docs/reports/research/lacerda-issue22/acquisition.json"})
    memorial_path = OUT / "memorial_acquisition.json"
    if memorial_path.exists():
        for row in read(memorial_path):
            if row["status"] != "pdf_recovered":
                continue
            records.append({"resource_id": "source:lacerda-issue22-" + Path(row["raw_file"]).stem, "provider": "SUCOP / A+P Arquitetos Associados", "dataset": row["name"], "author": observations["author"], "capture_date": "2026-10-06", "document_date": "2023-09" if "Memorial" in row["name"] else "2023-08", "revision": "R00", "pages": row["pages"], "bounds": None, "raw_files": [{"path": row["raw_file"], "sha256": row["sha256"]}], "source_url": row["requested_url"], "evidence_class": "OFFICIAL_TEXT", "release_status": "DEV_REFERENCE_ONLY", "usage_class": "REFERENCIA_INTERNA", "purpose": "Memorial do projeto e especificações; investigação sem derivar objetos", "derived_objects": [], "dependencies": [], "kind": "document_reference", "evidence": "docs/reports/research/lacerda-issue22/memorial_acquisition.json"})
    for record in records:
        for raw in record["raw_files"]:
            assert digest(ROOT / raw["path"]) == raw["sha256"]
    ids = {r["resource_id"] for r in records}
    registry["resources"] = [r for r in registry["resources"] if r["resource_id"] not in ids] + records
    assert len(registry["resources"]) == len({r["resource_id"] for r in registry["resources"]})
    write(registry_path, registry)
    write(OUT / "source_summary.json", {"schema": "boas/documentary-source-summary-v1", "resources": records, "raw_release_allowed": False, "drawing_to_ssot": None, "scene_changed": False})
    write(OUT / "reconciliation.json", {"schema": "boas/issue22-reconciliation-v1", "issue": "https://github.com/washingtonmsdj/game-baia-de-todos-os-santos/issues/22", "branch": "research/lacerda-evidence-2026-10-06", "decision": "NO_SCENE_CHANGE", "protected_revisions": preservation, "canonical_local_reports": canonical, "ssot_sha256": digest(ssot), "objects_preserved": 6294, "objects_evidence": "docs/reports/blender/lacerda-controller-b80/validation_b80.json", "count_not_reexported": True, "B81_created": False, "movement_enabled": False, "authorized_geometry_corrections": [], "production_exported": False, "CCD_repeated": False, "CCD_reuse_reason": "B80 e auditorias canônicas inalteradas por hash; nenhuma geometria ou trajetória modificada; não simular nova aprovação física.", "witness_groups": dict(summary), "registered_resources": len(records)})
    print(json.dumps({"decision": "NO_SCENE_CHANGE", "protected": len(preservation), "witnesses": len(witnesses), "groups": dict(summary), "resources": len(records)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
