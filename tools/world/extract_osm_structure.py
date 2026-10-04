#!/usr/bin/env python3
"""Extrai camadas estruturais do map.osm sem dependências externas.

O resultado é uma referência geográfica auditável. Não gera geometria final de jogo.
Suporta ways e relações multipolygon simples/compostas, preservando rastreabilidade OSM.
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
    "motorway_link", "trunk_link", "primary_link", "secondary_link", "tertiary_link",
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
    if tags.get("natural") == "cliff":
        return "cliffs"
    if tags.get("man_made") in {"pier", "breakwater", "groyne", "quay"}:
        return "waterfront"
    if tags.get("barrier") in {"retaining_wall", "wall", "city_wall"} or tags.get("man_made") == "retaining_wall":
        return "retaining_walls"
    if tags.get("man_made") == "embankment" or tags.get("embankment") == "yes" or tags.get("cutting") == "yes":
        return "earthworks"
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


def parse_osm(path: Path) -> tuple[dict[str, tuple[float, float]], dict[int, dict], list[dict]]:
    nodes: dict[str, tuple[float, float]] = {}
    ways: dict[int, dict] = {}
    relations: list[dict] = []
    for _, elem in ET.iterparse(path, events=("end",)):
        if elem.tag == "node":
            nodes[elem.attrib["id"]] = (float(elem.attrib["lat"]), float(elem.attrib["lon"]))
            elem.clear()
        elif elem.tag == "way":
            refs = [child.attrib["ref"] for child in elem if child.tag == "nd"]
            tags = {child.attrib["k"]: child.attrib["v"] for child in elem if child.tag == "tag"}
            ways[int(elem.attrib["id"])] = {"id": int(elem.attrib["id"]), "refs": refs, "tags": tags}
            elem.clear()
        elif elem.tag == "relation":
            tags = {child.attrib["k"]: child.attrib["v"] for child in elem if child.tag == "tag"}
            if tags.get("type") == "multipolygon":
                members = [
                    {
                        "type": child.attrib.get("type"),
                        "ref": int(child.attrib["ref"]),
                        "role": child.attrib.get("role", ""),
                    }
                    for child in elem if child.tag == "member" and child.attrib.get("ref", "").isdigit()
                ]
                relations.append({"id": int(elem.attrib["id"]), "members": members, "tags": tags})
            elem.clear()
    return nodes, ways, relations


def build_way_feature(way: dict, nodes: dict[str, tuple[float, float]]) -> dict | None:
    layer = classify_way(way["tags"])
    if not layer:
        return None
    valid_refs = [ref for ref in way["refs"] if ref in nodes]
    coords_wgs84 = [nodes[ref] for ref in valid_refs]
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
    closed = len(valid_refs) >= 4 and valid_refs[0] == valid_refs[-1]
    return {
        "osm_type": "way",
        "osm_id": way["id"],
        "layer": layer,
        "closed": closed,
        "node_refs": [int(ref) for ref in valid_refs],
        "missing_node_ref_count": len(way["refs"]) - len(valid_refs),
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


def stitch_way_refs(parts: list[list[str]]) -> tuple[list[list[str]], list[list[str]]]:
    """Monta anéis/linhas conectando way refs pelos endpoints, sem heurística espacial."""
    remaining = [list(p) for p in parts if len(p) >= 2]
    completed: list[list[str]] = []
    incomplete: list[list[str]] = []
    while remaining:
        chain = remaining.pop(0)
        changed = True
        while changed and chain[0] != chain[-1]:
            changed = False
            for i, part in enumerate(remaining):
                if chain[-1] == part[0]:
                    chain.extend(part[1:])
                elif chain[-1] == part[-1]:
                    chain.extend(reversed(part[:-1]))
                elif chain[0] == part[-1]:
                    chain = part[:-1] + chain
                elif chain[0] == part[0]:
                    chain = list(reversed(part[1:])) + chain
                else:
                    continue
                remaining.pop(i)
                changed = True
                break
        if len(chain) >= 4 and chain[0] == chain[-1]:
            completed.append(chain)
        else:
            incomplete.append(chain)
    return completed, incomplete


def build_relation_features(relation: dict, ways: dict[int, dict], nodes: dict[str, tuple[float, float]]) -> tuple[list[dict], dict]:
    layer = classify_way(relation["tags"])
    diagnostics = {
        "relation_id": relation["id"],
        "layer": layer,
        "missing_way_members": [],
        "outer_rings": 0,
        "inner_rings": 0,
        "incomplete_outer_chains": 0,
        "incomplete_inner_chains": 0,
    }
    if not layer:
        return [], diagnostics

    outer_parts: list[list[str]] = []
    inner_parts: list[list[str]] = []
    member_way_ids: list[int] = []
    for member in relation["members"]:
        if member["type"] != "way":
            continue
        way = ways.get(member["ref"])
        if not way:
            diagnostics["missing_way_members"].append(member["ref"])
            continue
        member_way_ids.append(member["ref"])
        role = member.get("role") or "outer"
        if role == "inner":
            inner_parts.append(way["refs"])
        elif role in {"outer", ""}:
            outer_parts.append(way["refs"])

    outer_rings, outer_incomplete = stitch_way_refs(outer_parts)
    inner_rings, inner_incomplete = stitch_way_refs(inner_parts)
    diagnostics["outer_rings"] = len(outer_rings)
    diagnostics["inner_rings"] = len(inner_rings)
    diagnostics["incomplete_outer_chains"] = len(outer_incomplete)
    diagnostics["incomplete_inner_chains"] = len(inner_incomplete)

    features = []
    for part_index, refs in enumerate(outer_rings):
        valid_refs = [ref for ref in refs if ref in nodes]
        coords_wgs84 = [nodes[ref] for ref in valid_refs]
        if len(coords_wgs84) < 4 or valid_refs[0] != valid_refs[-1]:
            continue
        coords_3857 = [mercator(lat, lon) for lat, lon in coords_wgs84]
        features.append({
            "osm_type": "relation",
            "osm_id": relation["id"],
            "relation_part_index": part_index,
            "layer": layer,
            "closed": True,
            "node_refs": [int(ref) for ref in valid_refs],
            "member_way_ids": member_way_ids,
            "missing_node_ref_count": len(refs) - len(valid_refs),
            "wgs84": [[lat, lon] for lat, lon in coords_wgs84],
            "epsg3857": [[x, y] for x, y in coords_3857],
            "metrics": {
                "length_m_projected": line_length(coords_3857),
                "area_m2_projected": polygon_area(coords_3857),
                "width_m_tagged": parse_number(relation["tags"].get("width")),
                "lanes_tagged": None,
            },
            "tags": relation["tags"],
            "relation_hole_count": len(inner_rings),
        })
    return features, diagnostics


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

    nodes, ways, relations = parse_osm(osm)
    features = []
    skipped = 0
    for way in ways.values():
        feature = build_way_feature(way, nodes)
        if feature:
            features.append(feature)
        elif classify_way(way["tags"]):
            skipped += 1

    relation_diagnostics = []
    for relation in relations:
        rel_features, diagnostics = build_relation_features(relation, ways, nodes)
        features.extend(rel_features)
        if diagnostics["layer"]:
            relation_diagnostics.append(diagnostics)

    features.sort(key=lambda item: (item["layer"], item["osm_type"], item["osm_id"], item.get("relation_part_index", -1)))
    layer_counts = Counter(item["layer"] for item in features)
    relation_feature_count = sum(1 for item in features if item["osm_type"] == "relation")
    payload = {
        "schema": "bay-of-all-saints/osm-structure-v2",
        "source": {"osm_path": str(osm), "crs_source": "EPSG:4326", "crs_projected": "EPSG:3857"},
        "bounds_wgs84": compute_bounds(features, "wgs84"),
        "bounds_epsg3857": compute_bounds(features, "epsg3857"),
        "stats": {
            "nodes_loaded": len(nodes),
            "ways_loaded": len(ways),
            "ways_classified": sum(1 for way in ways.values() if classify_way(way["tags"])),
            "multipolygon_relations_loaded": len(relations),
            "multipolygon_relations_classified": len(relation_diagnostics),
            "relation_features_emitted": relation_feature_count,
            "features_emitted": len(features),
            "features_skipped_missing_nodes": skipped,
            "features_with_missing_node_refs": sum(1 for item in features if item["missing_node_ref_count"]),
            "relations_with_missing_way_members": sum(1 for item in relation_diagnostics if item["missing_way_members"]),
            "relations_with_incomplete_outer_chains": sum(1 for item in relation_diagnostics if item["incomplete_outer_chains"]),
            "layers": dict(sorted(layer_counts.items())),
        },
        "relation_diagnostics": relation_diagnostics,
        "features": features,
        "notes": [
            "Geometrias são referência estrutural derivada de OSM, não arte final.",
            "node_refs são preservados para auditoria topológica e continuidade.",
            "Relações multipolygon classificadas têm seus anéis externos emitidos como features relation separadas por part_index.",
            "Anéis internos são contados como holes, mas não viram spline independente nesta versão; não preencher buracos automaticamente no Blender.",
            "Relações incompletas permanecem explicitamente registradas em relation_diagnostics.",
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
