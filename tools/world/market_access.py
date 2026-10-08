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


def evaluate_direct_approach(gameplay_proxy, target_xy, terrain_samples, visual_hits,
                             *, nav_bounds=None):
    """Diagnostica apenas o segmento reto B82 -> fachada, sem propor rota.

    Rays em malhas visíveis são evidência geométrica, não colisores certificados.
    Um segmento sem hits também NÃO aprova navegação ou acesso ao edifício.
    """
    frame = gameplay_proxy.get("local_frame")
    route = gameplay_proxy.get("lower_route")
    if not isinstance(frame, dict) or not isinstance(route, list) or not route:
        raise ValueError("Percurso B82 ou frame ausente")
    origin = frame.get("origin_xy")
    if not isinstance(origin, (list, tuple)) or len(origin) != 2:
        raise ValueError("Origem do frame inválida")
    if not isinstance(target_xy, (list, tuple)) or len(target_xy) != 2:
        raise ValueError("Alvo da abordagem inválido")
    angle = _number(frame.get("angle"), "angle")
    x0, y0 = (_number(x, "origin_xy") for x in origin)
    local = route[-1]
    if not isinstance(local, (list, tuple)) or len(local) < 2:
        raise ValueError("Último waypoint B82 inválido")
    local_x, local_y = (_number(v, "lower_route") for v in local[:2])
    start = [x0 + math.cos(angle)*local_x - math.sin(angle)*local_y,
             y0 + math.sin(angle)*local_x + math.cos(angle)*local_y]
    target = [_number(v, "target_xy") for v in target_xy]
    length = math.hypot(target[0]-start[0], target[1]-start[1])
    if length <= 0.001:
        raise ValueError("Segmento de abordagem degenerado")
    if not isinstance(terrain_samples, list) or len(terrain_samples) < 2:
        raise ValueError("Sondagens do solo insuficientes")
    if not isinstance(visual_hits, list):
        raise ValueError("Interseções geométricas inválidas")
    samples = []
    last_t = -1.0
    for item in terrain_samples:
        if not isinstance(item, dict):
            raise ValueError("Sondagem do solo inválida")
        t = _number(item.get("t"), "t")
        if t < 0 or t > 1 or t <= last_t:
            raise ValueError("Sondagens fora de sequência")
        last_t = t
        z = item.get("terrain_z")
        samples.append({"t": t, "terrain_z": _number(z, "terrain_z") if z is not None else None})
    if abs(samples[0]["t"]) > 1e-7 or abs(samples[-1]["t"] - 1) > 1e-7:
        raise ValueError("Sondagens não cobrem ambas as extremidades")
    hits = []
    for item in visual_hits:
        if not isinstance(item, dict) or not isinstance(item.get("name"), str) or not item["name"]:
            raise ValueError("Interseção sem objeto")
        distance = _number(item.get("distance_m"), "distance_m")
        z = _number(item.get("ray_z"), "ray_z")
        if distance < 0 or distance > length + 1e-4:
            raise ValueError("Interseção fora do segmento")
        hits.append({"name": item["name"], "distance_m": round(distance, 4),
                     "ray_z": z})
    hits.sort(key=lambda row: (row["distance_m"], row["name"]))
    bounds = None
    if nav_bounds is not None:
        if not isinstance(nav_bounds, (list, tuple)) or len(nav_bounds) != 2:
            raise ValueError("Bounds de navegação inválidos")
        bounds = [[_number(v, "nav_bounds") for v in extent] for extent in nav_bounds]
        if any(len(extent) != 2 or extent[0] > extent[1] for extent in bounds):
            raise ValueError("Extensão de navegação inválida")
    def inside(point):
        return bounds is not None and all(bounds[i][0] <= point[i] <= bounds[i][1]
                                          for i in (0, 1))
    return {
        "schema": "boas/market-direct-approach-v1",
        "source_proxy": gameplay_proxy.get("scene_file"),
        "segment": {"start_world_xy": [round(v, 6) for v in start],
                    "target_world_xy": [round(v, 6) for v in target],
                    "length_m": round(length, 4)},
        "terrain_sample_count": len(samples),
        "terrain_missing": sum(v["terrain_z"] is None for v in samples),
        "terrain_min_z": min((v["terrain_z"] for v in samples if v["terrain_z"] is not None), default=None),
        "terrain_max_z": max((v["terrain_z"] for v in samples if v["terrain_z"] is not None), default=None),
        "nav_hint_start_inside_bbox": inside(start),
        "nav_hint_target_inside_bbox": inside(target),
        "visual_ray_hits": hits,
        "visual_line_clear": len(hits) == 0,
        "status": "DIRECT_LINE_INTERSECTS_VISIBLE_GEOMETRY" if hits else "NO_VISUAL_HIT_NOT_CERTIFIED",
        "complete_collision_test": False,
        "route_approved": False,
        "navigation_approved": False,
    }
