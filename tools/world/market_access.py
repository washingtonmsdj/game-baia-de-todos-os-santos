"""Avaliação conservadora de candidatos a acesso usando o registro de locais como SSOT.

O resultado não cria coordenadas, vínculos, rotas nem permissão de movimento.
"""
import math


def _number(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{name} requer número finito")
    return float(value)


def evaluate_access_candidates(locations, location_id, portals, *, level_tolerance_m=0.03):
    if not isinstance(locations, dict) or not isinstance(locations.get("locations"), list):
        raise ValueError("Registro de locais inválido")
    matches = [row for row in locations["locations"] if row.get("location_id") == location_id]
    if len(matches) != 1:
        raise ValueError("Local ausente ou ambíguo no SSOT")
    place = matches[0]
    tol = _number(level_tolerance_m, "level_tolerance_m")
    if tol <= 0 or not isinstance(portals, list):
        raise ValueError("Controles de acesso inválidos")
    results = []
    names = set()
    for i, candidate in enumerate(portals):
        if not isinstance(candidate, dict):
            raise ValueError(f"Portal {i} inválido")
        name = candidate.get("name")
        if not isinstance(name, str) or not name or name in names:
            raise ValueError("Portal com nome vazio ou duplicado")
        names.add(name)
        center = candidate.get("center_xy")
        if not isinstance(center, (list, tuple)) or len(center) != 2:
            raise ValueError("Centro XY do portal inválido")
        xy = [_number(v, "center_xy") for v in center]
        width = _number(candidate.get("clear_gap_m"), "clear_gap_m")
        height = _number(candidate.get("headroom_m"), "headroom_m")
        if width < 0 or height < 0:
            raise ValueError("Dimensão física negativa")
        samples = candidate.get("samples")
        if not isinstance(samples, list) or not samples:
            raise ValueError("Sondagens do portal ausentes")
        checks = []
        center_level_match = False
        for j, row in enumerate(samples):
            if not isinstance(row, dict):
                raise ValueError(f"Sondagem {j} inválida")
            offset = _number(row.get("offset_m"), "offset_m")
            terrain = row.get("terrain_z")
            floor = row.get("floor_z")
            terrain = _number(terrain, "terrain_z") if terrain is not None else None
            floor = _number(floor, "floor_z") if floor is not None else None
            dz = floor - terrain if floor is not None and terrain is not None else None
            if offset == 0 and dz is not None and abs(dz) <= tol:
                center_level_match = True
            checks.append({
                "offset_m": offset,
                "terrain_hit": terrain is not None,
                "floor_hit": floor is not None,
                "height_delta_m": round(dz, 6) if dz is not None else None,
            })
        visible = candidate.get("visible") is True
        provisional = "tipológico" in str(candidate.get("reference_status", "")).casefold()
        supported_by_geometry = visible and width > 0 and height > 0 and center_level_match
        blockers = ["SEM_ENSAIO_COMPLETO_DE_COLISAO_E_NAVEGACAO",
                    "SEM_EVIDENCIA_INDEPENDENTE_DA_ENTRADA_REAL"]
        if place.get("blender_binding") is None:
            blockers.append("LOCAL_SEM_BINDING_VERIFICADO")
        if (place.get("osm") or {}).get("verified") is not True:
            blockers.append("REFERENCIA_OSM_NAO_VERIFICADA")
        if provisional:
            blockers.append("MODELO_TIPOLOGICO_NAO_CADASTRAL")
        if not supported_by_geometry:
            blockers.append("GEOMETRIA_OU_NIVEL_SEM_SUPORTE")
        results.append({
            "name": name, "center_xy": xy,
            "clear_gap_m": width, "headroom_m": height,
            "surface_samples": checks,
            "center_levels_match": center_level_match,
            "geometry_candidate": supported_by_geometry,
            "reference_status": candidate.get("reference_status"),
            "blockers": blockers, "route_certified": False,
        })
    return {
        "schema": "boas/access-candidate-audit-v1",
        "area_id": locations.get("area_id"),
        "location_id": location_id,
        "locations_ssot": "world/areas/mvp-centro-lacerda/locations.json",
        "candidates": results,
        "geometry_candidates": sum(v["geometry_candidate"] for v in results),
        "approved_access_count": 0,
        "market_route_approved": False,
        "production_ready": False,
    }
