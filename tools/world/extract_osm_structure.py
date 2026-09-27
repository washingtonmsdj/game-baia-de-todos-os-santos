#!/usr/bin/env python3
"""Extrai camadas estruturais do map.osm sem dependências externas.

Suporta ways e relations `type=multipolygon` para não perder footprints/áreas
compostas. O resultado é referência geográfica auditável, nunca arte final.
"""

from __future__ import annotations

import argparse
import json
import math
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

EARTH_RADIUS = 6378137.0
MAX_LAT = 85.0511287798066

ROAD_VALUES = {
    "motorway", "trunk", "primary", "secondary", "tertiary", "unclassified", "residential",
    "service", "living_street", "pedestrian", "track", "path", "footway", "cycleway", "steps"
}
VALID_MULTIPOLYGON_ROLES = {"outer", "inner"}


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
    """Classifica tags de way ou relation; nome mantido por compatibilidade."""
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


def parse_osm_document(path: Path) -> tuple[dict[str, tuple[float, float]], dict[int, dict], list[dict]]:
    nodes: dict[str, tuple[float, float]] = {}
    raw_ways: dict[int, dict] = {}
    relations: list[dict] = []

    for _event, elem in ET.iterparse(path, events=("end",)):
        if elem.tag == "node":
            nodes[elem.attrib["id"]] = (float(elem.attrib["lat"]), float(elem.attrib["lon"]))
            elem.clear()
        elif elem.tag == "way":
            way_id = int(elem.attrib["id"])
            refs = [child.attrib["ref"] for child in elem if child.tag == "nd"]
            tags = {child.attrib["k"]: child.attrib["v"] for child in elem if child.tag == "tag"}
            raw_ways[way_id] = {"id": way_id, "refs": refs, "tags": tags, "layer": classify_way(tags)}
            elem.clear()
        elif elem.tag == "relation":
            relation_id = int(elem.attrib["id"])
            members = [
                {
                    "type": child.attrib.get("type", ""),
                    "ref": int(child.attrib["ref"]),
                    "role": child.attrib.get("role", ""),
                }
                for child in elem
                if child.tag == "member" and child.attrib.get("ref", "").lstrip("-").isdigit()
            ]
            tags = {child.attrib["k"]: child.attrib["v"] for child in elem if child.tag == "tag"}
            relations.append({"id": relation_id, "members": members, "tags": tags, "layer": classify_way(tags)})
            elem.clear()
    return nodes, raw_ways, relations


def parse_osm(path: Path) -> tuple[dict[str, tuple[float, float]], list[dict]]:
    """API histórica: retorna nodes + ways diretamente classificáveis."""
    nodes, raw_ways, _relations = parse_osm_document(path)
    ways = [way for way in raw_ways.values() if way.get("layer")]
    ways.sort(key=lambda item: item["id"])
    return nodes, ways


def build_feature(way: dict, nodes: dict[str, tuple[float, float]]) -> dict | None:
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
        "osm_key": f"way/{way['id']}",
        "layer": way["layer"],
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


def _join_chain(chain: list[str], refs: list[str]) -> tuple[list[str], bool]:
    if not chain or not refs:
        return chain, False
    if refs[0] == chain[-1]:
        return chain + refs[1:], True
    if refs[-1] == chain[-1]:
        reversed_refs = list(reversed(refs))
        return chain + reversed_refs[1:], True
    if refs[-1] == chain[0]:
        return refs[:-1] + chain, True
    if refs[0] == chain[0]:
        reversed_refs = list(reversed(refs))
        return reversed_refs[:-1] + chain, True
    return chain, False


def assemble_member_rings(member_way_ids: list[int], raw_ways: dict[int, dict]) -> tuple[list[dict], list[int]]:
    """Monta cadeias/rings usando somente igualdade exata de node refs."""
    missing_members = sorted({way_id for way_id in member_way_ids if way_id not in raw_ways})
    remaining = {way_id: list(raw_ways[way_id]["refs"]) for way_id in member_way_ids if way_id in raw_ways}
    rings = []

    while remaining:
        first_id = next(iter(remaining))
        chain = remaining.pop(first_id)
        used = [first_id]
        progress = True
        while progress and remaining and not (len(chain) >= 4 and chain[0] == chain[-1]):
            progress = False
            for way_id, refs in list(remaining.items()):
                joined, ok = _join_chain(chain, refs)
                if ok:
                    chain = joined
                    used.append(way_id)
                    remaining.pop(way_id)
                    progress = True
                    break
        rings.append({
            "refs": chain,
            "member_way_ids": used,
            "closed": len(chain) >= 4 and chain[0] == chain[-1],
        })
    return rings, missing_members


def normalized_multipolygon_members(relation: dict) -> tuple[dict[str, list[int]], list[dict]]:
    """Separa membros suportados sem reinterpretar role desconhecido."""
    members_by_role: dict[str, list[int]] = defaultdict(list)
    unsupported = []
    for member in relation.get("members", []):
        if member.get("type") != "way":
            unsupported.append({**member, "reason": "member_type_not_way"})
            continue
        raw_role = member.get("role") or ""
        role = raw_role or "outer"
        if role not in VALID_MULTIPOLYGON_ROLES:
            unsupported.append({**member, "reason": "unsupported_role"})
            continue
        members_by_role[role].append(int(member["ref"]))
    return members_by_role, unsupported


def build_relation_features(relation: dict, raw_ways: dict[int, dict], nodes: dict[str, tuple[float, float]]) -> list[dict]:
    tags = relation.get("tags") or {}
    if tags.get("type") != "multipolygon" or not relation.get("layer"):
        return []

    members_by_role, unsupported_members = normalized_multipolygon_members(relation)
    features = []
    for role in ("outer", "inner"):
        way_ids = members_by_role.get(role, [])
        if not way_ids:
            continue
        rings, missing_members = assemble_member_rings(way_ids, raw_ways)
        for ring_index, ring in enumerate(rings):
            refs = ring["refs"]
            valid_refs = [ref for ref in refs if ref in nodes]
            if len(valid_refs) < 2:
                continue
            coords_wgs84 = [nodes[ref] for ref in valid_refs]
            coords_3857 = [mercator(lat, lon) for lat, lon in coords_wgs84]
            closed = len(valid_refs) >= 4 and valid_refs[0] == valid_refs[-1]
            features.append({
                "osm_type": "relation",
                "osm_id": relation["id"],
                "osm_key": f"relation/{relation['id']}",
                "layer": relation["layer"],
                "closed": closed,
                "relation_role": role,
                "relation_ring_index": ring_index,
                "member_way_ids": ring["member_way_ids"],
                "missing_member_way_ids": missing_members,
                "missing_member_way_count": len(missing_members),
                "unsupported_relation_members": unsupported_members,
                "node_refs": [int(ref) for ref in valid_refs],
                "missing_node_ref_count": len(refs) - len(valid_refs),
                "wgs84": [[lat, lon] for lat, lon in coords_wgs84],
                "epsg3857": [[x, y] for x, y in coords_3857],
                "metrics": {
                    "length_m_projected": line_length(coords_3857),
                    "area_m2_projected": polygon_area(coords_3857),
                    "width_m_tagged": None,
                    "lanes_tagged": None,
                },
                "tags": tags,
            })
    return features


def relation_diagnostic(relation: dict, raw_ways: dict[int, dict], built_features: list[dict]) -> dict:
    members_by_role, unsupported = normalized_multipolygon_members(relation)
    supported_way_ids = sorted({way_id for ids in members_by_role.values() for way_id in ids})
    missing = sorted(way_id for way_id in supported_way_ids if way_id not in raw_ways)
    return {
        "osm_key": f"relation/{relation['id']}",
        "osm_id": relation["id"],
        "layer": relation.get("layer"),
        "supported_member_way_count": len(supported_way_ids),
        "missing_member_way_ids": missing,
        "unsupported_members": unsupported,
        "emitted_ring_features": len(built_features),
        "open_ring_features": sum(1 for feature in built_features if not feature.get("closed")),
        "outer_ring_features": sum(1 for feature in built_features if feature.get("relation_role") == "outer"),
        "inner_ring_features": sum(1 for feature in built_features if feature.get("relation_role") == "inner"),
    }


def relation_features_and_covered_ways(
    relations: list[dict],
    raw_ways: dict[int, dict],
    nodes: dict[str, tuple[float, float]],
) -> tuple[list[dict], dict[int, set[str]], list[dict]]:
    relation_features = []
    covered: dict[int, set[str]] = defaultdict(set)
    diagnostics = []
    for relation in relations:
        tags = relation.get("tags") or {}
        if tags.get("type") != "multipolygon" or not relation.get("layer"):
            continue
        built = build_relation_features(relation, raw_ways, nodes)
        relation_features.extend(built)
        diagnostics.append(relation_diagnostic(relation, raw_ways, built))
        for feature in built:
            if not feature.get("closed"):
                continue
            if feature.get("missing_member_way_count") or feature.get("unsupported_relation_members"):
                continue
            layer = feature.get("layer")
            for way_id in feature.get("member_way_ids", []):
                covered[int(way_id)].add(layer)
    return relation_features, covered, diagnostics


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
    parser = argparse.ArgumentParser(description="Extrai ways/relations de ruas, footprints, coastline e outras camadas estruturais.")
    parser.add_argument("--osm", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    osm = args.osm.resolve()
    if not osm.is_file():
        raise SystemExit(f"map.osm não encontrado: {osm}")

    nodes, raw_ways, relations = parse_osm_document(osm)
    relation_features, covered_ways, relation_diagnostics = relation_features_and_covered_ways(relations, raw_ways, nodes)

    features = []
    skipped = 0
    duplicate_way_features_suppressed = 0
    classified_ways = [way for way in raw_ways.values() if way.get("layer")]
    for way in classified_ways:
        if way["layer"] in covered_ways.get(way["id"], set()):
            duplicate_way_features_suppressed += 1
            continue
        feature = build_feature(way, nodes)
        if feature:
            features.append(feature)
        else:
            skipped += 1
    features.extend(relation_features)

    features.sort(key=lambda item: (
        item["layer"], item["osm_type"], item["osm_id"], item.get("relation_role", ""), item.get("relation_ring_index", -1)
    ))
    layer_counts = Counter(item["layer"] for item in features)
    relations_with_issues = [
        diag for diag in relation_diagnostics
        if diag["missing_member_way_ids"] or diag["unsupported_members"] or diag["open_ring_features"] or diag["outer_ring_features"] == 0
    ]
    payload = {
        "schema": "bay-of-all-saints/osm-structure-v1",
        "source": {"osm_path": str(osm), "crs_source": "EPSG:4326", "crs_projected": "EPSG:3857"},
        "bounds_wgs84": compute_bounds(features, "wgs84"),
        "bounds_epsg3857": compute_bounds(features, "epsg3857"),
        "stats": {
            "nodes_loaded": len(nodes),
            "ways_loaded": len(raw_ways),
            "ways_classified": len(classified_ways),
            "relations_loaded": len(relations),
            "multipolygon_relations_classified": len(relation_diagnostics),
            "multipolygon_relations_with_issues": len(relations_with_issues),
            "relation_ring_features": len(relation_features),
            "unsupported_relation_members": sum(len(diag["unsupported_members"]) for diag in relation_diagnostics),
            "duplicate_way_features_suppressed": duplicate_way_features_suppressed,
            "features_emitted": len(features),
            "features_skipped_missing_nodes": skipped,
            "features_with_missing_node_refs": sum(1 for item in features if item.get("missing_node_ref_count")),
            "relation_features_with_missing_members": sum(1 for item in relation_features if item.get("missing_member_way_count")),
            "unclosed_relation_rings": sum(1 for item in relation_features if not item.get("closed")),
            "layers": dict(sorted(layer_counts.items())),
        },
        "relation_diagnostics": relation_diagnostics,
        "features": features,
        "notes": [
            "Geometrias são referência estrutural derivada de OSM, não arte final.",
            "Relations type=multipolygon são montadas somente por node refs exatos; nenhuma ponta é aproximada/encaixada por distância.",
            "Role vazio de member way é tratado como outer; roles não vazios desconhecidos são registrados como unsupported e nunca reinterpretados.",
            "Rings outer e inner permanecem separados e rastreáveis por relation ID + role + ring index.",
            "Way membro só é suprimido como duplicata quando participa de ring relation fechado, completo e sem member/role ambíguo da mesma layer.",
            "node_refs são preservados para auditoria topológica e continuidade.",
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
