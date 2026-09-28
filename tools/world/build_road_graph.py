from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

SCHEMA = "bay-of-all-saints/road-graph-v1"


def transform_point(point: list[float], fit: dict) -> list[float]:
    x, y = float(point[0]), float(point[1])
    scale = float(fit["scale_blender_units_per_meter"])
    theta = math.radians(float(fit["rotation_epsg3857_to_blender_deg"]))
    tx, ty = [float(v) for v in fit["translation_blender"]]
    c, s = math.cos(theta), math.sin(theta)
    return [scale * (c * x - s * y) + tx, scale * (s * x + c * y) + ty]


def direction_for(tags: dict) -> str:
    oneway = str(tags.get("oneway") or "").strip().lower()
    if oneway in {"yes", "1", "true"}:
        return "forward"
    if oneway == "-1":
        return "reverse"
    if str(tags.get("junction") or "").lower() == "roundabout" and oneway != "no":
        return "forward"
    return "both"


def access_class(tags: dict) -> str:
    values = {str(tags.get(k) or "").lower() for k in ("access", "vehicle", "motor_vehicle", "motorcar")}
    if values & {"no", "private"}:
        return "restricted"
    return "candidate"


def build_graph(structure: dict, fit_report: dict) -> dict:
    robust = fit_report["robust_fit"]
    road_features = [f for f in structure["features"] if f.get("layer") == "roads"]
    nodes: dict[str, dict] = {}
    edges: list[dict] = []
    ways: list[dict] = []
    node_way_ids: dict[str, set[int]] = defaultdict(set)
    adjacency: dict[str, set[str]] = defaultdict(set)

    for feature in road_features:
        refs = [str(value) for value in feature.get("node_refs") or []]
        coords = feature.get("epsg3857") or []
        if len(refs) != len(coords) or len(refs) < 2:
            continue
        osm_id = int(feature["osm_id"])
        tags = dict(feature.get("tags") or {})
        direction = direction_for(tags)
        access = access_class(tags)
        way_points: list[list[float]] = []
        for ref, point in zip(refs, coords):
            xy = transform_point(point, robust)
            way_points.append(xy)
            node_way_ids[ref].add(osm_id)
            nodes.setdefault(ref, {
                "id": ref,
                "epsg3857": [float(point[0]), float(point[1])],
                "blender_xy": xy,
            })
        for index in range(len(refs) - 1):
            a, b = refs[index], refs[index + 1]
            adjacency[a].add(b)
            adjacency[b].add(a)
            edges.append({
                "id": f"way-{osm_id}-seg-{index}",
                "osm_way_id": osm_id,
                "from": a,
                "to": b,
                "direction": direction,
                "access": access,
            })
        ways.append({
            "osm_way_id": osm_id,
            "name": tags.get("name"),
            "highway": tags.get("highway"),
            "direction": direction,
            "access": access,
            "lanes_tagged": feature.get("metrics", {}).get("lanes_tagged"),
            "width_m_tagged": feature.get("metrics", {}).get("width_m_tagged"),
            "maxspeed_raw": tags.get("maxspeed"),
            "surface": tags.get("surface"),
            "node_refs": refs,
            "blender_xy": way_points,
        })

    for ref, node in nodes.items():
        node["degree"] = len(adjacency.get(ref, set()))
        node["way_ids"] = sorted(node_way_ids.get(ref, set()))
        node["junction_candidate"] = node["degree"] >= 3 or len(node["way_ids"]) >= 2

    junction_count = sum(1 for node in nodes.values() if node["junction_candidate"])
    restricted_edges = sum(1 for edge in edges if edge["access"] == "restricted")
    one_way_edges = sum(1 for edge in edges if edge["direction"] != "both")
    return {
        "schema": SCHEMA,
        "status": "candidate",
        "fit_quality": fit_report.get("quality"),
        "fit_status": fit_report.get("status"),
        "stats": {
            "road_ways": len(ways),
            "nodes": len(nodes),
            "edges": len(edges),
            "junction_candidates": junction_count,
            "one_way_edges": one_way_edges,
            "restricted_edges": restricted_edges,
        },
        "nodes": sorted(nodes.values(), key=lambda item: int(item["id"])),
        "edges": edges,
        "ways": ways,
        "notes": [
            "O grafo representa topologia OSM, não faixas de trânsito.",
            "Direção usa oneway/junction=roundabout; ausência de tag não inventa mão única.",
            "A posição Blender usa o robust_fit atual, cuja qualidade permanece candidate.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Constrói grafo lógico de vias a partir do OSM estrutural.")
    parser.add_argument("--structure", required=True)
    parser.add_argument("--fit", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    structure_path = Path(args.structure).resolve()
    fit_path = Path(args.fit).resolve()
    output_path = Path(args.output).resolve()
    structure = json.loads(structure_path.read_text(encoding="utf-8"))
    fit_report = json.loads(fit_path.read_text(encoding="utf-8"))
    graph = build_graph(structure, fit_report)
    graph["sources"] = {
        "structure": str(structure_path),
        "fit": str(fit_path),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(graph, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(graph["stats"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
