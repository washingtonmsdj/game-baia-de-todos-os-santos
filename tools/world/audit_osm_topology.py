#!/usr/bin/env python3
"""Audita continuidade/topologia do osm_structure.json.

Somente QA. Não edita OSM, não fecha gaps e não cria conexões automaticamente.
"""

from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

TRANSPORT_LAYERS = {"roads", "pedestrian", "steps"}
LINEAR_REVIEW_LAYERS = TRANSPORT_LAYERS | {"coastline", "waterfront", "retaining_walls", "earthworks", "cliffs", "railways"}
SUPPORTED_STRUCTURE_SCHEMAS = {
    "bay-of-all-saints/osm-structure-v1",
    "bay-of-all-saints/osm-structure-v2",
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def euclidean(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot(b[0] - a[0], b[1] - a[1])


def near_boundary(point: tuple[float, float], bounds: dict, margin_m: float) -> bool:
    return (
        abs(point[0] - bounds["min_x"]) <= margin_m
        or abs(point[0] - bounds["max_x"]) <= margin_m
        or abs(point[1] - bounds["min_y"]) <= margin_m
        or abs(point[1] - bounds["max_y"]) <= margin_m
    )


def layer_group(layer: str) -> str:
    if layer in TRANSPORT_LAYERS:
        return "transport"
    return layer


def feature_identity(feature: dict) -> dict:
    value = {"osm_type": feature.get("osm_type", "way"), "osm_id": feature.get("osm_id")}
    if feature.get("relation_part_index") is not None:
        value["relation_part_index"] = feature.get("relation_part_index")
    return value


def endpoint_rows(features: list[dict]) -> list[dict]:
    rows = []
    for feature in features:
        layer = feature.get("layer")
        refs = feature.get("node_refs") or []
        coords = feature.get("epsg3857") or []
        if layer not in LINEAR_REVIEW_LAYERS or len(refs) < 2 or len(coords) < 2:
            continue
        if feature.get("closed"):
            continue
        for endpoint_name, ref_index, coord_index in (("start", 0, 0), ("end", -1, -1)):
            rows.append({
                "group": layer_group(layer),
                "layer": layer,
                **feature_identity(feature),
                "node_ref": int(refs[ref_index]),
                "endpoint": endpoint_name,
                "xy": (float(coords[coord_index][0]), float(coords[coord_index][1])),
                "tags": feature.get("tags") or {},
            })
    return rows


def build_degrees(features: list[dict]) -> dict[tuple[str, int], int]:
    degrees: dict[tuple[str, int], int] = defaultdict(int)
    for feature in features:
        layer = feature.get("layer")
        refs = feature.get("node_refs") or []
        if layer not in LINEAR_REVIEW_LAYERS or len(refs) < 2 or feature.get("closed"):
            continue
        group = layer_group(layer)
        degrees[(group, int(refs[0]))] += 1
        degrees[(group, int(refs[-1]))] += 1
        for ref in refs[1:-1]:
            degrees[(group, int(ref))] += 2
    return degrees


def separation_signature(tags: dict) -> tuple[str | None, str | None, str | None]:
    return tags.get("layer"), tags.get("bridge"), tags.get("tunnel")


def likely_grade_separated(a: dict, b: dict) -> bool:
    sig_a = separation_signature(a.get("tags") or {})
    sig_b = separation_signature(b.get("tags") or {})
    if sig_a == sig_b:
        return False
    return any(value not in (None, "no", "0") for value in sig_a + sig_b)


def endpoint_identity(endpoint: dict) -> tuple:
    return (
        endpoint.get("osm_type", "way"), endpoint.get("osm_id"),
        endpoint.get("relation_part_index", -1), endpoint.get("endpoint"),
    )


def spatial_near_misses(endpoints: list[dict], tolerance_m: float) -> tuple[list[dict], list[dict]]:
    if tolerance_m <= 0:
        return [], []
    cell_size = tolerance_m
    grid: dict[tuple[int, int, str], list[int]] = defaultdict(list)
    pairs = []
    grade_separated = []
    seen_pairs = set()

    def cell(point):
        return (math.floor(point[0] / cell_size), math.floor(point[1] / cell_size))

    for index, endpoint in enumerate(endpoints):
        cx, cy = cell(endpoint["xy"])
        group = endpoint["group"]
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for other_index in grid.get((cx + dx, cy + dy, group), []):
                    other = endpoints[other_index]
                    if endpoint["node_ref"] == other["node_ref"]:
                        continue
                    if endpoint_identity(endpoint)[:-1] == endpoint_identity(other)[:-1]:
                        continue
                    key = tuple(sorted((endpoint_identity(endpoint), endpoint_identity(other))))
                    if key in seen_pairs:
                        continue
                    dist = euclidean(endpoint["xy"], other["xy"])
                    if dist > tolerance_m:
                        continue
                    seen_pairs.add(key)
                    def compact(value):
                        return {
                            "osm_type": value.get("osm_type", "way"),
                            "osm_id": value.get("osm_id"),
                            "relation_part_index": value.get("relation_part_index"),
                            "layer": value.get("layer"),
                            "node_ref": value.get("node_ref"),
                            "endpoint": value.get("endpoint"),
                        }
                    row = {
                        "group": group,
                        "distance_m_projected": dist,
                        "a": compact(endpoint),
                        "b": compact(other),
                        "xy_a": list(endpoint["xy"]),
                        "xy_b": list(other["xy"]),
                    }
                    if likely_grade_separated(endpoint, other):
                        row["reason"] = "possible_grade_separation"
                        grade_separated.append(row)
                    else:
                        row["reason"] = "distinct_nodes_within_tolerance"
                        pairs.append(row)
        grid[(cx, cy, group)].append(index)
    pairs.sort(key=lambda item: item["distance_m_projected"])
    grade_separated.sort(key=lambda item: item["distance_m_projected"])
    return pairs, grade_separated


def connected_components(features: list[dict], group_name: str) -> list[list[dict]]:
    selected = []
    for index, feature in enumerate(features):
        layer = feature.get("layer")
        if layer_group(layer) != group_name:
            continue
        refs = {int(ref) for ref in (feature.get("node_refs") or [])}
        if refs:
            selected.append((index, feature_identity(feature), refs))
    if not selected:
        return []

    parent = {index: index for index, _, _ in selected}

    def find(value):
        while parent[value] != value:
            parent[value] = parent[parent[value]]
            value = parent[value]
        return value

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    node_owner: dict[int, int] = {}
    for index, _, refs in selected:
        for ref in refs:
            if ref in node_owner:
                union(index, node_owner[ref])
            else:
                node_owner[ref] = index

    components: dict[int, list[dict]] = defaultdict(list)
    for index, identity, _ in selected:
        components[find(index)].append(identity)
    result = [sorted(values, key=lambda v: (str(v.get("osm_type")), int(v.get("osm_id") or 0), int(v.get("relation_part_index") or -1))) for values in components.values()]
    result.sort(key=lambda values: (-len(values), str(values[0])))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Audita gaps e continuidade do osm_structure.json.")
    parser.add_argument("--structure", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--boundary-margin-m", type=float, default=15.0)
    parser.add_argument("--near-miss-m", type=float, default=1.5)
    args = parser.parse_args()

    structure = load_json(args.structure)
    if structure.get("schema") not in SUPPORTED_STRUCTURE_SCHEMAS:
        raise SystemExit("schema estrutural não suportado")
    features = structure.get("features") or []
    bounds = structure.get("bounds_epsg3857")
    if not bounds:
        raise SystemExit("osm_structure.json não contém bounds_epsg3857")

    unclosed_buildings = [
        {**feature_identity(item), "tags": item.get("tags", {})}
        for item in features
        if item.get("layer") == "buildings" and not item.get("closed")
    ]
    missing_nodes = [
        {**feature_identity(item), "layer": item.get("layer"), "missing_node_ref_count": item.get("missing_node_ref_count")}
        for item in features
        if (item.get("missing_node_ref_count") or 0) > 0
    ]

    relation_diagnostics = structure.get("relation_diagnostics") or []
    incomplete_relations = [
        item for item in relation_diagnostics
        if item.get("missing_way_members") or item.get("incomplete_outer_chains") or item.get("incomplete_inner_chains")
    ]

    endpoints = endpoint_rows(features)
    degrees = build_degrees(features)
    dangling_internal = []
    dangling_boundary = []
    for endpoint in endpoints:
        if degrees.get((endpoint["group"], endpoint["node_ref"]), 0) != 1:
            continue
        row = {
            "group": endpoint["group"], "layer": endpoint["layer"],
            "osm_type": endpoint.get("osm_type", "way"), "osm_id": endpoint["osm_id"],
            "relation_part_index": endpoint.get("relation_part_index"),
            "node_ref": endpoint["node_ref"], "endpoint": endpoint["endpoint"],
            "xy": list(endpoint["xy"]), "name": endpoint["tags"].get("name"),
            "highway": endpoint["tags"].get("highway"),
        }
        if near_boundary(endpoint["xy"], bounds, args.boundary_margin_m):
            row["classification"] = "boundary_or_extract_edge"
            dangling_boundary.append(row)
        else:
            row["classification"] = "internal_dangling_review"
            dangling_internal.append(row)

    near_misses, grade_separated = spatial_near_misses(endpoints, args.near_miss_m)
    transport_components = connected_components(features, "transport")
    coastline_components = connected_components(features, "coastline")
    coastline_internal = [item for item in dangling_internal if item["group"] == "coastline"]
    transport_internal = [item for item in dangling_internal if item["group"] == "transport"]

    review_queue = []
    for item in missing_nodes:
        review_queue.append({"kind": "missing_node_refs", "severity": "high", **item})
    for item in incomplete_relations:
        review_queue.append({"kind": "incomplete_multipolygon_relation", "severity": "high", **item})
    for item in unclosed_buildings:
        review_queue.append({"kind": "unclosed_building_feature", "severity": "high", **item})
    for item in coastline_internal:
        review_queue.append({"kind": "internal_coastline_endpoint", "severity": "high", **item})
    for item in near_misses:
        review_queue.append({"kind": "near_miss_endpoint", "severity": "medium", **item})
    for item in transport_internal:
        review_queue.append({"kind": "internal_transport_dangling", "severity": "review", **item})

    payload = {
        "schema": "bay-of-all-saints/osm-topology-audit-v2",
        "source": str(args.structure.resolve()),
        "source_structure_schema": structure.get("schema"),
        "thresholds": {"boundary_margin_m_projected": args.boundary_margin_m, "near_miss_m_projected": args.near_miss_m},
        "summary": {
            "features": len(features),
            "missing_node_ref_features": len(missing_nodes),
            "incomplete_multipolygon_relations": len(incomplete_relations),
            "unclosed_buildings": len(unclosed_buildings),
            "internal_dangling_endpoints": len(dangling_internal),
            "boundary_dangling_endpoints": len(dangling_boundary),
            "near_miss_pairs": len(near_misses),
            "possible_grade_separation_pairs": len(grade_separated),
            "transport_components": len(transport_components),
            "coastline_components": len(coastline_components),
            "review_items": len(review_queue),
        },
        "network": {"transport_components": transport_components, "coastline_components": coastline_components},
        "issues": {
            "missing_node_refs": missing_nodes,
            "incomplete_multipolygon_relations": incomplete_relations,
            "unclosed_buildings": unclosed_buildings,
            "internal_dangling_endpoints": dangling_internal,
            "boundary_dangling_endpoints": dangling_boundary,
            "near_misses": near_misses,
            "possible_grade_separations": grade_separated,
        },
        "review_queue": review_queue,
        "notes": [
            "Dangling endpoint não é automaticamente erro: pode ser rua sem saída, acesso privado ou limite do recorte.",
            "Near-miss não é conectado automaticamente; pontes/túneis/layers podem justificar separação.",
            "Coastline pode terminar na borda do extrato; endpoints internos merecem revisão prioritária.",
            "Relações multipolygon incompletas são reportadas e nunca fechadas por proximidade espacial.",
            "Auditoria não modifica OSM nem geometria Blender.",
        ],
    }
    write_json(args.output, payload)
    print(json.dumps(payload["summary"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
