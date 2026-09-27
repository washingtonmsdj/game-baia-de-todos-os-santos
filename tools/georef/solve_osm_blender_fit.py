#!/usr/bin/env python3
"""Estima uma transformação 2D EPSG:3857 -> Blender a partir de anchors OSM.

Entrada:
- georef_hints.json exportado por tools/blender/extract_georef_hints.py
- map.osm original da captura Aleph

O script é somente de auditoria: não altera .blend nem area.json.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

R = 6378137.0
MAX_LAT = 85.0511287798066


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def mercator(lat: float, lon: float) -> tuple[float, float]:
    lat = max(-MAX_LAT, min(MAX_LAT, lat))
    x = R * math.radians(lon)
    y = R * math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))
    return x, y


def inverse_mercator(x: float, y: float) -> tuple[float, float]:
    lon = math.degrees(x / R)
    lat = math.degrees(2 * math.atan(math.exp(y / R)) - math.pi / 2)
    return lat, lon


def polygon_centroid(points: list[tuple[float, float]]) -> tuple[float, float]:
    if not points:
        raise ValueError("polígono vazio")
    if len(points) < 3:
        return tuple(sum(p[i] for p in points) / len(points) for i in (0, 1))
    ring = points if points[0] == points[-1] else points + [points[0]]
    twice_area = 0.0
    cx = 0.0
    cy = 0.0
    for (x1, y1), (x2, y2) in zip(ring, ring[1:]):
        cross = x1 * y2 - x2 * y1
        twice_area += cross
        cx += (x1 + x2) * cross
        cy += (y1 + y2) * cross
    if abs(twice_area) < 1e-9:
        return tuple(sum(p[i] for p in points) / len(points) for i in (0, 1))
    return cx / (3 * twice_area), cy / (3 * twice_area)


def parse_osm(path: Path) -> dict[str, dict]:
    nodes: dict[str, tuple[float, float]] = {}
    ways_raw: dict[str, dict] = {}

    for event, elem in ET.iterparse(path, events=("end",)):
        if elem.tag == "node":
            nodes[elem.attrib["id"]] = (float(elem.attrib["lat"]), float(elem.attrib["lon"]))
            elem.clear()
        elif elem.tag == "way":
            refs = [child.attrib["ref"] for child in elem if child.tag == "nd"]
            tags = {child.attrib["k"]: child.attrib["v"] for child in elem if child.tag == "tag"}
            ways_raw[elem.attrib["id"]] = {"refs": refs, "tags": tags}
            elem.clear()

    ways = {}
    for way_id, raw in ways_raw.items():
        coords = [nodes[ref] for ref in raw["refs"] if ref in nodes]
        if len(coords) < 2:
            continue
        projected = [mercator(lat, lon) for lat, lon in coords]
        center = polygon_centroid(projected)
        ways[way_id] = {
            "epsg3857": center,
            "tags": raw["tags"],
            "node_count": len(coords),
        }
    return ways


def object_xy(obj: dict) -> tuple[float, float] | None:
    bounds = obj.get("bounds_world") or {}
    center = bounds.get("center")
    if isinstance(center, list) and len(center) >= 2:
        return float(center[0]), float(center[1])
    location = obj.get("location_world")
    if isinstance(location, list) and len(location) >= 2:
        return float(location[0]), float(location[1])
    return None


def median_point(points: list[tuple[float, float]]) -> tuple[float, float]:
    return statistics.median(p[0] for p in points), statistics.median(p[1] for p in points)


def build_anchors(hints: dict, ways: dict[str, dict], buildings_only: bool) -> list[dict]:
    by_osm: dict[str, list[tuple[float, float]]] = defaultdict(list)
    names: dict[str, list[str]] = defaultdict(list)
    for obj in hints.get("objects", []):
        point = object_xy(obj)
        if point is None:
            continue
        for osm_id in obj.get("osm_ids", []):
            way = ways.get(str(osm_id))
            if not way:
                continue
            if buildings_only and "building" not in way["tags"]:
                continue
            by_osm[str(osm_id)].append(point)
            names[str(osm_id)].append(obj.get("name", ""))

    anchors = []
    for osm_id, targets in by_osm.items():
        source = ways[osm_id]["epsg3857"]
        target = median_point(targets)
        anchors.append({
            "osm_type": "way",
            "osm_id": int(osm_id),
            "epsg3857": [source[0], source[1]],
            "blender_xy": [target[0], target[1]],
            "object_count": len(targets),
            "object_names": sorted(set(names[osm_id]))[:20],
            "osm_tags": ways[osm_id]["tags"],
        })
    return anchors


def fit_similarity(anchors: list[dict]) -> dict:
    if len(anchors) < 2:
        raise ValueError("são necessários pelo menos 2 anchors")

    src = [tuple(a["epsg3857"]) for a in anchors]
    dst = [tuple(a["blender_xy"]) for a in anchors]
    ps = (statistics.fmean(p[0] for p in src), statistics.fmean(p[1] for p in src))
    qs = (statistics.fmean(q[0] for q in dst), statistics.fmean(q[1] for q in dst))

    a_sum = b_sum = den = 0.0
    for p, q in zip(src, dst):
        px, py = p[0] - ps[0], p[1] - ps[1]
        qx, qy = q[0] - qs[0], q[1] - qs[1]
        a_sum += px * qx + py * qy
        b_sum += px * qy - py * qx
        den += px * px + py * py
    if den <= 1e-12:
        raise ValueError("anchors EPSG degenerados")

    ac = a_sum / den
    bs = b_sum / den
    scale = math.hypot(ac, bs)
    if scale <= 1e-12:
        raise ValueError("escala degenerada")
    theta = math.atan2(bs, ac)
    tx = qs[0] - (ac * ps[0] - bs * ps[1])
    ty = qs[1] - (bs * ps[0] + ac * ps[1])

    residuals = []
    enriched = []
    for anchor in anchors:
        x, y = anchor["epsg3857"]
        predicted = (ac * x - bs * y + tx, bs * x + ac * y + ty)
        bx, by = anchor["blender_xy"]
        residual = math.hypot(predicted[0] - bx, predicted[1] - by)
        residuals.append(residual)
        enriched.append({**anchor, "predicted_blender_xy": [predicted[0], predicted[1]], "residual_blender_units": residual})

    rms = math.sqrt(statistics.fmean(r * r for r in residuals))
    median = statistics.median(residuals)
    maximum = max(residuals)

    # EPSG coordinate corresponding to Blender (0, 0).
    det = ac * ac + bs * bs
    origin_x = (-ac * tx - bs * ty) / det
    origin_y = (bs * tx - ac * ty) / det
    origin_lat, origin_lon = inverse_mercator(origin_x, origin_y)

    return {
        "anchor_count": len(anchors),
        "scale_blender_units_per_meter": scale,
        "meters_per_blender_unit": 1.0 / scale,
        "rotation_epsg3857_to_blender_deg": math.degrees(theta),
        "true_north_blender_vector": [-math.sin(theta), math.cos(theta)],
        "true_north_angle_from_blender_x_deg": (math.degrees(theta) + 90.0) % 360.0,
        "translation_blender": [tx, ty],
        "blender_origin_epsg3857": [origin_x, origin_y],
        "blender_origin_wgs84": [origin_lat, origin_lon],
        "rms_residual_blender_units": rms,
        "median_residual_blender_units": median,
        "max_residual_blender_units": maximum,
        "anchors": enriched,
    }


def robust_fit(anchors: list[dict], min_anchors: int, max_residual: float, max_iterations: int = 20) -> dict:
    current = list(anchors)
    removed = []
    for _ in range(max_iterations):
        result = fit_similarity(current)
        worst = max(result["anchors"], key=lambda item: item["residual_blender_units"])
        if worst["residual_blender_units"] <= max_residual or len(current) <= min_anchors:
            result["removed_outliers"] = removed
            return result
        removed.append({
            "osm_id": worst["osm_id"],
            "residual_blender_units": worst["residual_blender_units"],
            "object_names": worst.get("object_names", []),
        })
        current = [a for a in current if a["osm_id"] != worst["osm_id"]]
    result = fit_similarity(current)
    result["removed_outliers"] = removed
    return result


def quality(result: dict, min_anchors: int, target_rms: float) -> str:
    count = result["anchor_count"]
    rms = result["rms_residual_blender_units"]
    if count >= max(8, min_anchors) and rms <= target_rms:
        return "strong_candidate"
    if count >= min_anchors and rms <= target_rms * 2:
        return "candidate"
    return "insufficient"


def main() -> int:
    parser = argparse.ArgumentParser(description="Estima o fit EPSG:3857 -> Blender usando OSM IDs detectados na cena.")
    parser.add_argument("--hints", type=Path, required=True, help="georef_hints.json exportado do Blender")
    parser.add_argument("--osm", type=Path, required=True, help="map.osm original da captura")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--min-anchors", type=int, default=4)
    parser.add_argument("--max-residual", type=float, default=8.0, help="limite de rejeição em unidades Blender")
    parser.add_argument("--target-rms", type=float, default=3.0, help="RMS alvo em unidades Blender")
    parser.add_argument("--all-ways", action="store_true", help="usar ways além de buildings")
    args = parser.parse_args()

    if args.min_anchors < 3:
        raise SystemExit("--min-anchors deve ser >= 3 para validação espacial")
    hints = load_json(args.hints)
    ways = parse_osm(args.osm)

    anchors = build_anchors(hints, ways, buildings_only=not args.all_ways)
    mode = "building_ways"
    if len(anchors) < args.min_anchors and not args.all_ways:
        anchors = build_anchors(hints, ways, buildings_only=False)
        mode = "all_matching_ways_fallback"
    if len(anchors) < args.min_anchors:
        payload = {
            "schema": "bay-of-all-saints/georef-fit-v1",
            "status": "insufficient_anchors",
            "mode": mode,
            "matched_anchor_count": len(anchors),
            "required_anchor_count": args.min_anchors,
            "anchors": anchors,
            "notes": ["Nenhuma transformação foi promovida ou aplicada."],
        }
        write_json(args.output, payload)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 2

    raw = fit_similarity(anchors)
    robust = robust_fit(anchors, args.min_anchors, args.max_residual)
    payload = {
        "schema": "bay-of-all-saints/georef-fit-v1",
        "status": "candidate_only",
        "mode": mode,
        "inputs": {"hints": str(args.hints), "osm": str(args.osm)},
        "thresholds": {
            "min_anchors": args.min_anchors,
            "max_residual_blender_units": args.max_residual,
            "target_rms_blender_units": args.target_rms,
        },
        "raw_fit": raw,
        "robust_fit": robust,
        "quality": quality(robust, args.min_anchors, args.target_rms),
        "notes": [
            "O resultado é candidato e não altera automaticamente a cena ou area.json.",
            "O centro OSM é calculado a partir da geometria do way; o ponto Blender vem do centro de bounds dos objetos detectados.",
            "Validar visualmente múltiplos anchors e resíduos antes de marcar world_anchor_status=verified.",
            "Para maior precisão, substituir/confirmar anchors com binding explícito quando disponível.",
        ],
    }
    write_json(args.output, payload)
    print(json.dumps({
        "status": payload["status"],
        "quality": payload["quality"],
        "raw_anchors": raw["anchor_count"],
        "robust_anchors": robust["anchor_count"],
        "rms": robust["rms_residual_blender_units"],
        "meters_per_blender_unit": robust["meters_per_blender_unit"],
        "rotation_deg": robust["rotation_epsg3857_to_blender_deg"],
        "origin_wgs84": robust["blender_origin_wgs84"],
        "removed_outliers": len(robust["removed_outliers"]),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
