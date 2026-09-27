#!/usr/bin/env python3
"""Extrai camadas estruturais do map.osm sem dependências externas.

O resultado é uma referência geográfica auditável. Não gera geometria final de jogo.
"""

from __future__ import annotations

import argparse
import json
import math
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

EARTH_RADIUS = 6378137.0
MAX_LAT = 85.0511287798066

ROAD_VALUES = {
    "motorway", "trunk", "primary", "secondary", "tertiary", "unclassified", "residential",
    "service", "living_street", "pedestrian", "track", "path", "footway", "cycleway", "steps"
}


def mercator(lat: float, lon: float) -> tuple[float, float]:
    lat = max(-MAX_LAT, min(MAX_LAT, lat))
    x = EARTH_RADIUS * math.radians(lon)
    y = EARTH_RADIUS * math.log(math.tan(math.pi / 4.0 + math.radians(lat) / 2.0))
    return x, y


def parse_number(value: str | None) -> float | None:
    if not value:
        return None
    text = value.strip().lower().replace(",", ".")
    for suffix in (" meters", " meter", " metres", " metre", " m"):
        if text.endswith(suffix):
            text = text[: -len(suffix)].strip()
            break
    try:
        return float(text)
    except ValueError:
        return None


def classify_way(tags: dict[str, str]) -> str | None:
    highway = tags.get("highway")
    if highway in ROAD_VALUES:
        if highway == "steps":
            return "steps"
        if highway in {"pedestrian", "footway", "path"}:
            return "pedestrian"
        return "roads"
    if "building" in tags and tags.get("building") != "no":
        return "buildings"
    if tags.get("natural") == "coastline":
        return "coastline"
    if tags.get("man_made") in {"pier", "breakwater", "groyne"}:
        return "waterfront"
    if tags.get("barrier") in {"retaining_wall", "wall", "city_wall"}:
        return "retaining_walls"
    if tags.get("natural") == "water" or tags.get("waterway") in {"riverbank", "dock"}:
        return "water"
    if tags.get("railway"):
        return "railways"
    return None


def line_length(points: list[tuple[float, float]]) -> float:
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(points, points[1:]))


def polygon_area(points: list[tuple[float, float]]) -> float | None:
    if len(points) < 4 or points[0] != points[-1]:
        return None
    total = 0.0
    for (x1, y1), (x2, y2) in zip(points, points[1:]):
        total += x1 * y2 - x2 * y1
    return abs(total) * 0.5


def parse_osm(path: Path) -> tuple[dict[str, tuple[float, float]], list[dict]]:
    nodes: dict[str, tuple[float, float]] = {}
    ways: list[dict] = []
    for event, elem in ET.iterparse(path, events=("end",)):
        if elem.tag == "node":
            nodes[elem.attrib["id"]] = (float(elem.attrib["lat"]), float(elem.attrib["lon"]))
            elem.clear()
        elif elem.tag == "way":
            refs = [child.attrib["ref"] for child in elem if child.tag == "nd"]
            tags = {child.attrib["k"]: child.attrib["v"] for child in elem if child.tag == "tag"}
            layer = classify_way(tags)
            if layer:
                ways.append({"id": int(elem.attrib["id"]), "refs": refs, "tags": tags, "layer": layer})
            elem.clear()
    return nodes, ways


def build_feature(way: dict, nodes: dict[str, tuple[float, float]]) -> dict | None:
    coords_wgs84 = [nodes[ref] for ref in way["refs"] if ref in nodes]
    if len(coords_wgs84) < 2:
        return None
    coords_3857 = [mercator(lat, lon) for lat, lon in coords_wgs84]
    tags = way["tags"]
    width = parse_number(tags.get("width"))
    lanes = None
    try:
        lanes = int(tags["lanes"]) if "lanes" in tags else None
    except ValueError:
        lanes = None
    closed = len(coords_wgs84) >= 4 and coords_wgs84[0] == coords_wgs84[-1]
    feature = {
        "osm_type": "way",
        "osm_id": way["id"],
        "layer": way["layer"],
        "closed": closed,
        "wgs84": [[lat, lon] for lat, lon in coords_wgs84],
        "epsg3857": [[x, y] for x, y in coords_3857],
        "metrics": {
            "length_m_projected": line_length(coords_3857),
            "area_m2_projected": polygon_area(coords_3857),
            "width_m_tagged": width,
            "lanes_tagged": lanes,
        },
        "tags": tags,
    }
    return feature


def compute_bounds(features: list[dict], key: str) -> dict | None:
    points = [point for feature in features for point in feature[key]]
    if not points:
        return None
    if key == "wgs84":
        lats = [p[0] for p in points]
        lons = [p[1] for p in points]
        return {"south": min(lats), "west": min(lons), "north": max(lats), "east": max(lons)}
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return {"min_x": min(xs), "min_y": min(ys), "max_x": max(xs), "max_y": max(ys)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Extrai ruas, footprints, coastline e outras camadas estruturais de um map.osm.")
    parser.add_argument("--osm", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    osm = args.osm.resolve()
    if not osm.is_file():
        raise SystemExit(f"map.osm não encontrado: {osm}")

    nodes, ways = parse_osm(osm)
    features = []
    skipped = 0
    for way in ways:
        feature = build_feature(way, nodes)
        if feature:
            features.append(feature)
        else:
            skipped += 1

    features.sort(key=lambda item: (item["layer"], item["osm_id"]))
    layer_counts = Counter(item["layer"] for item in features)
    payload = {
        "schema": "bay-of-all-saints/osm-structure-v1",
        "source": {"osm_path": str(osm), "crs_source": "EPSG:4326", "crs_projected": "EPSG:3857"},
        "bounds_wgs84": compute_bounds(features, "wgs84"),
        "bounds_epsg3857": compute_bounds(features, "epsg3857"),
        "stats": {
            "nodes_loaded": len(nodes),
            "ways_classified": len(ways),
            "features_emitted": len(features),
            "features_skipped_missing_nodes": skipped,
            "layers": dict(sorted(layer_counts.items())),
        },
        "features": features,
        "notes": [
            "Geometrias são referência estrutural derivada de OSM, não arte final.",
            "width_m_tagged e lanes_tagged só são preenchidos quando existem explicitamente no OSM.",
            "length/area usam EPSG:3857 e servem para auditoria relativa; não são levantamento cadastral.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["stats"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
