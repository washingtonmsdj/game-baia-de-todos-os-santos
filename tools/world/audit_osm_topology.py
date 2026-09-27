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
                "osm_id": feature.get("osm_id"),
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
        # Nós internos também conectam ways que usam o mesmo node; registrar presença.
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
    meaningful = any(value not in (None, "no", "0") for value in sig_a + sig_b)
    return meaningful


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
                    if endpoint["osm_id"] == other["osm_id"]:
                        continue
                    key = tuple(sorted((
                        (endpoint["osm_id"], endpoint["endpoint"]),
                        (other["osm_id"], other["endpoint"]),
                    )))
                    if key in seen_pairs:
                        continue
                    dist = euclidean(endpoint["xy"], other["xy"])
                    if dist > tolerance_m:
                        continue
                    seen_pairs.add(key)
                    row = {
                        "group": group,
                        "distance_m_projected": dist,
                        "a": {k: endpoint[k] for k in ("osm_id", "layer", "node_ref", "endpoint")},
                        "b": {k: other[k] for k in ("osm_id", "layer", "node_ref", "endpoint")},
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


def connected_components(features: list[dict], group_name: str) -> list[list[int]]:
    selected = []
    for feature in features:
        layer = feature.get("layer")
        if layer_group(layer) != group_name:
            continue
        refs = {int(ref) for ref in (feature.get("node_refs") or [])}
        if refs:
            selected.append((int(feature["osm_id"]), refs))
    if not selected:
        return []

    parent = {osm_id: osm_id for osm_id, _ in selected}

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
    for osm_id, refs in selected:
        for ref in refs:
            if ref in node_owner:
                union(osm_id, node_owner[ref])
            else:
                node_owner[ref] = osm_id

    components: dict[int, list[int]] = defaultdict(list)
    for osm_id, _ in selected:
        components[find(osm_id)].append(osm_id)
    result = [sorted(values) for values in components.values()]
    result.sort(key=lambda values: (-len(values), values[0]))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Audita gaps e continuidade do osm_structure.json.")
    parser.add_argument("--structure", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--boundary-margin-m", type=float, default=15.0)
    parser.add_argument("--near-miss-m", type=float, default=1.5)
    args = parser.parse_args()

    structure = load_json(args.structure)
    if structure.get("schema") != "bay-of-all-saints/osm-structure-v1":
        raise SystemExit("schema estrutural não suportado")
    features = structure.get("features") or []
    bounds = structure.get("bounds_epsg3857")
    if not bounds:
        raise SystemExit("osm_structure.json não contém bounds_epsg3857")

    unclosed_buildings = [
        {"osm_id": item.get("osm_id"), "tags": item.get("tags", {})}
        for item in features
        if item.get("layer") == "buildings" and not item.get("closed")
    ]
    missing_nodes = [
        {"osm_id": item.get("osm_id"), "layer": item.get("layer"), "missing_node_ref_count": item.get("missing_node_ref_count")}
        for item in features
        if (item.get("missing_node_ref_count") or 0) > 0
    ]

    endpoints = endpoint_rows(features)
    degrees = build_degrees(features)
    dangling_internal = []
    dangling_boundary = []
    for endpoint in endpoints:
        if degrees.get((endpoint["group"], endpoint["node_ref"]), 0) != 1:
            continue
        row = {
            "group": endpoint["group"],
            "layer": endpoint["layer"],
            "osm_id": endpoint["osm_id"],
            "node_ref": endpoint["node_ref"],
            "endpoint": endpoint["endpoint"],
            "xy": list(endpoint["xy"]),
            "name": endpoint["tags"].get("name"),
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
    for item in unclosed_buildings:
        review_queue.append({"kind": "unclosed_building_way", "severity": "high", **item})
    for item in coastline_internal:
        review_queue.append({"kind": "internal_coastline_endpoint", "severity": "high", **item})
    for item in near_misses:
        review_queue.append({"kind": "near_miss_endpoint", "severity": "medium", **item})
    for item in transport_internal:
        review_queue.append({"kind": "internal_transport_dangling", "severity": "review", **item})

    payload = {
        "schema": "bay-of-all-saints/osm-topology-audit-v1",
        "source": str(args.structure.resolve()),
        "thresholds": {
            "boundary_margin_m_projected": args.boundary_margin_m,
            "near_miss_m_projected": args.near_miss_m,
        },
        "summary": {
            "features": len(features),
            "missing_node_ref_features": len(missing_nodes),
            "unclosed_buildings": len(unclosed_buildings),
            "internal_dangling_endpoints": len(dangling_internal),
            "boundary_dangling_endpoints": len(dangling_boundary),
            "near_miss_pairs": len(near_misses),
            "possible_grade_separation_pairs": len(grade_separated),
            "transport_components": len(transport_components),
            "coastline_components": len(coastline_components),
            "review_items": len(review_queue),
        },
        "network": {
            "transport_components": transport_components,
            "coastline_components": coastline_components,
        },
        "issues": {
            "missing_node_refs": missing_nodes,
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
            "Auditoria não modifica OSM nem geometria Blender.",
        ],
    }
    write_json(args.output, payload)
    print(json.dumps(payload["summary"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
