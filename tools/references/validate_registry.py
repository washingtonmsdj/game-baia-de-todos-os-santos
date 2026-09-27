#!/usr/bin/env python3
"""Valida o catálogo de referências do Bay of All Saints sem dependências externas."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

VALID_MODEL_STATUS = {"not_started", "proxy", "blockout", "modeling", "review", "approved", "needs_rework", "deprecated"}
VALID_REFERENCE_STATUS = {"missing", "partial", "sufficient", "verified"}
VALID_USAGE_CLASS = {"PRODUCAO_APROVADA", "REFERENCIA_INTERNA", "TEMPORARIA", "PROIBIDO_PRODUCAO"}
PRODUCTION_MEDIA = {"PRODUCAO_APROVADA", "REFERENCIA_INTERNA"}
VALID_VIEWS = {"front", "rear", "left", "right", "oblique_left", "oblique_right", "roof", "access", "street_context", "waterfront_context", "detail", "panorama", "map"}
VALID_CANDIDATE_STATUS = {"candidate", "accepted", "rejected", "imported"}


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ValueError(f"arquivo ausente: {path}")
    except json.JSONDecodeError as exc:
        raise ValueError(f"JSON inválido em {path}: {exc}") from exc


def is_relative_safe(path: str) -> bool:
    candidate = Path(path)
    return bool(path) and not candidate.is_absolute() and ".." not in candidate.parts


def validate_coverage(items, prefix, locations, primary, errors):
    if items is None:
        return []
    if not isinstance(items, list):
        errors.append(f"{prefix}: coverage deve ser lista")
        return []
    seen = {primary}
    valid = []
    for index, item in enumerate(items):
        p = f"{prefix}.coverage[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{p}: item inválido")
            continue
        pair = (item.get("location_id"), item.get("view"))
        if pair[0] not in locations:
            errors.append(f"{p}: location_id inexistente: {pair[0]}")
        if pair[1] not in VALID_VIEWS:
            errors.append(f"{p}: view inválida: {pair[1]}")
        if pair in seen:
            errors.append(f"{p}: cobertura duplicada ou igual à cobertura principal")
        seen.add(pair)
        valid.append(pair)
    return valid


def validate_area(area, source, errors, warnings):
    area_id = area.get("area_id")
    if area.get("schema_version") != 1:
        errors.append(f"{source}: schema_version deve ser 1")
    if not isinstance(area_id, str) or not area_id:
        errors.append(f"{source}: area_id ausente")
    bounds = area.get("bounds_wgs84") or {}
    values = [bounds.get(k) for k in ("south", "west", "north", "east")]
    if all(v is None for v in values):
        warnings.append(f"{source}: bounds WGS84 ainda não fechados")
    elif any(v is None for v in values):
        errors.append(f"{source}: bounds devem estar todos preenchidos ou todos nulos")
    else:
        south, west, north, east = values
        if not (-90 <= south < north <= 90): errors.append(f"{source}: latitude bounds inválida")
        if not (-180 <= west < east <= 180): errors.append(f"{source}: longitude bounds inválida")
    coord = area.get("coordinate_system") or {}
    status = coord.get("world_anchor_status")
    if status not in {"unknown", "candidate", "verified"}:
        errors.append(f"{source}: world_anchor_status inválido")
    if status == "verified":
        if any(v is None for v in values): errors.append(f"{source}: anchor verificado exige bounds completos")
        if coord.get("meters_per_blender_unit") is None: errors.append(f"{source}: anchor verificado exige meters_per_blender_unit")
        if coord.get("rotation_true_north_deg") is None: errors.append(f"{source}: anchor verificado exige rotation_true_north_deg")


def validate_locations(data, source, errors, warnings):
    if data.get("schema_version") != 1: errors.append(f"{source}: schema_version deve ser 1")
    locations = data.get("locations")
    if not isinstance(locations, list):
        errors.append(f"{source}: locations deve ser uma lista"); return {}, {}
    by_id, required = {}, {}
    for index, loc in enumerate(locations):
        prefix = f"{source}: locations[{index}]"; lid = loc.get("location_id")
        if not isinstance(lid, str) or not lid: errors.append(f"{prefix}: location_id ausente"); continue
        if lid in by_id: errors.append(f"{prefix}: location_id duplicado: {lid}")
        by_id[lid] = loc
        if loc.get("model_status") not in VALID_MODEL_STATUS: errors.append(f"{prefix}: model_status inválido")
        if loc.get("reference_status") not in VALID_REFERENCE_STATUS: errors.append(f"{prefix}: reference_status inválido")
        if loc.get("fidelity_class") not in {"A", "B", "C"}: errors.append(f"{prefix}: fidelity_class inválida")
        priority = loc.get("priority")
        if not isinstance(priority, int) or not 1 <= priority <= 5: errors.append(f"{prefix}: priority deve estar entre 1 e 5")
        views = loc.get("required_views", [])
        if not isinstance(views, list) or len(views) != len(set(views)): errors.append(f"{prefix}: required_views deve ser lista sem duplicações"); views = []
        bad = set(views) - VALID_VIEWS
        if bad: errors.append(f"{prefix}: required_views inválidas: {', '.join(sorted(bad))}")
        required[lid] = set(views)
        osm = loc.get("osm")
        if osm is not None and (osm.get("type") not in {"node", "way", "relation"} or not isinstance(osm.get("id"), int)): errors.append(f"{prefix}: referência OSM inválida")
        binding = loc.get("blender_binding")
        if binding is not None and binding.get("custom_property") != "boas_location_id": errors.append(f"{prefix}: blender_binding deve usar boas_location_id")
        if loc.get("model_status") == "approved":
            if loc.get("reference_status") != "verified": errors.append(f"{prefix}: asset approved exige reference_status=verified")
            if (loc.get("production_rules") or {}).get("manual_review_required"): warnings.append(f"{prefix}: asset approved ainda declara manual_review_required=true")
    return by_id, required


def validate_media(data, source, locations, errors, warnings):
    if data.get("schema_version") != 1: errors.append(f"{source}: schema_version deve ser 1")
    media = data.get("media")
    if not isinstance(media, list): errors.append(f"{source}: media deve ser uma lista"); return {}
    by_location = {}; seen_ids = set()
    for index, item in enumerate(media):
        prefix = f"{source}: media[{index}]"; mid = item.get("media_id"); lid = item.get("location_id"); view = item.get("view")
        if not isinstance(mid, str) or not mid: errors.append(f"{prefix}: media_id ausente"); continue
        if mid in seen_ids: errors.append(f"{prefix}: media_id duplicado: {mid}")
        seen_ids.add(mid)
        if lid not in locations: errors.append(f"{prefix}: location_id inexistente: {lid}")
        else: by_location.setdefault(lid, []).append((item, view))
        if view not in VALID_VIEWS: errors.append(f"{prefix}: view inválida")
        for cov_lid, cov_view in validate_coverage(item.get("coverage"), prefix, locations, (lid, view), errors):
            if cov_lid in locations: by_location.setdefault(cov_lid, []).append((item, cov_view))
        usage = item.get("usage_class")
        if usage not in VALID_USAGE_CLASS: errors.append(f"{prefix}: usage_class inválida")
        storage = item.get("storage") or {}; logical_path = storage.get("logical_path")
        if not isinstance(logical_path, str) or not is_relative_safe(logical_path): errors.append(f"{prefix}: logical_path deve ser relativo e não pode conter '..'")
        provenance = item.get("provenance") or {}; license_status = provenance.get("license_status")
        if usage == "PRODUCAO_APROVADA" and license_status != "verified": errors.append(f"{prefix}: PRODUCAO_APROVADA exige license_status=verified")
        if usage == "PROIBIDO_PRODUCAO": warnings.append(f"{prefix}: mídia proibida para produção está catalogada apenas como referência controlada")
    return by_location


def validate_candidates(data, source, area_id, locations, errors, warnings):
    if data.get("schema_version") != 1: errors.append(f"{source}: schema_version deve ser 1")
    if data.get("area_id") != area_id: errors.append(f"{source}: area_id diverge dos demais arquivos")
    candidates = data.get("candidates")
    if not isinstance(candidates, list): errors.append(f"{source}: candidates deve ser uma lista"); return
    seen = set()
    for index, item in enumerate(candidates):
        prefix = f"{source}: candidates[{index}]"; cid = item.get("candidate_id"); lid = item.get("location_id"); view = item.get("suggested_view")
        if not isinstance(cid, str) or not cid: errors.append(f"{prefix}: candidate_id ausente"); continue
        if cid in seen: errors.append(f"{prefix}: candidate_id duplicado: {cid}")
        seen.add(cid)
        if lid not in locations: errors.append(f"{prefix}: location_id inexistente: {lid}")
        if item.get("provider") != "wikimedia_commons": errors.append(f"{prefix}: provider não suportado")
        title = item.get("file_title")
        if not isinstance(title, str) or not title.startswith("File:"): errors.append(f"{prefix}: file_title precisa começar com File:")
        page_url = item.get("page_url")
        if not isinstance(page_url, str) or not page_url.startswith("https://commons.wikimedia.org/"): errors.append(f"{prefix}: page_url precisa apontar para commons.wikimedia.org")
        if view not in VALID_VIEWS: errors.append(f"{prefix}: suggested_view inválida")
        validate_coverage(item.get("coverage"), prefix, locations, (lid, view), errors)
        if item.get("status") not in VALID_CANDIDATE_STATUS: errors.append(f"{prefix}: status inválido")
        if item.get("status") == "candidate" and not item.get("expected_license"): warnings.append(f"{prefix}: candidato sem expectativa de licença registrada")


def validate_cross(area, loc_data, media_data, candidates_data, source_dir, errors, warnings):
    area_id = area.get("area_id")
    if loc_data.get("area_id") != area_id or media_data.get("area_id") != area_id: errors.append(f"{source_dir}: area_id diverge entre arquivos")
    locations, required = validate_locations(loc_data, source_dir / "locations.json", errors, warnings)
    media_by_location = validate_media(media_data, source_dir / "media-manifest.json", locations, errors, warnings)
    if candidates_data is not None: validate_candidates(candidates_data, source_dir / "reference-candidates.json", area_id, locations, errors, warnings)
    for lid, loc in locations.items():
        entries = media_by_location.get(lid, [])
        usable_views = {view for item, view in entries if item.get("usage_class") in PRODUCTION_MEDIA and (item.get("provenance") or {}).get("license_status") in {"verified", "pending"}}
        if loc.get("reference_status") in {"sufficient", "verified"} and not entries: errors.append(f"{source_dir}: {lid} declara referência {loc.get('reference_status')} mas não possui mídia catalogada")
        if loc.get("model_status") == "approved":
            missing = sorted(required.get(lid, set()) - usable_views)
            if missing: errors.append(f"{source_dir}: {lid} approved sem vistas obrigatórias: {', '.join(missing)}")
        if loc.get("fidelity_class") == "A" and loc.get("reference_status") == "missing": warnings.append(f"{source_dir}: Hero/Classe A sem referência suficiente: {lid}")


def validate_area_dir(area_dir):
    errors, warnings = [], []
    try:
        area = load_json(area_dir / "area.json"); loc_data = load_json(area_dir / "locations.json"); media_data = load_json(area_dir / "media-manifest.json")
        cp = area_dir / "reference-candidates.json"; candidates_data = load_json(cp) if cp.is_file() else None
    except ValueError as exc: return [str(exc)], warnings
    validate_area(area, area_dir / "area.json", errors, warnings)
    validate_cross(area, loc_data, media_data, candidates_data, area_dir, errors, warnings)
    return errors, warnings


def main():
    parser = argparse.ArgumentParser(description="Valida os catálogos de referência do Bay of All Saints.")
    parser.add_argument("--root", type=Path, default=Path(".")); parser.add_argument("--area")
    args = parser.parse_args(); areas_root = args.root.resolve() / "world" / "areas"
    area_dirs = [areas_root / args.area] if args.area else (sorted(p for p in areas_root.iterdir() if p.is_dir()) if areas_root.is_dir() else [])
    if not area_dirs: print("Nenhuma área encontrada em world/areas.", file=sys.stderr); return 2
    all_errors, all_warnings = [], []
    for area_dir in area_dirs:
        errors, warnings = validate_area_dir(area_dir); all_errors.extend(errors); all_warnings.extend(warnings)
    for warning in all_warnings: print(f"WARNING: {warning}")
    for error in all_errors: print(f"ERROR: {error}", file=sys.stderr)
    print(f"Áreas validadas: {len(area_dirs)} | erros: {len(all_errors)} | avisos: {len(all_warnings)}")
    return 1 if all_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
