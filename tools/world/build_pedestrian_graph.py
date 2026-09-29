from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

SCHEMA = "bay-of-all-saints/pedestrian-graph-v1"
LAYERS = {"pedestrian", "steps"}


def transform_point(point: list[float], fit: dict) -> list[float]:
    x, y = float(point[0]), float(point[1])
    scale = float(fit["scale_blender_units_per_meter"])
    theta = math.radians(float(fit["rotation_epsg3857_to_blender_deg"]))
    tx, ty = [float(value) for value in fit["translation_blender"]]
    c, s = math.cos(theta), math.sin(theta)
    return [
        scale * (c * x - s * y) + tx,
        scale * (s * x + c * y) + ty,
    ]


def traversal_for(tags: dict) -> str:
    value = str(tags.get("oneway:foot") or "").strip().lower()
    if value in {"yes", "1", "true"}:
        return "forward"
    if value == "-1":
        return "reverse"
    return "both"


def access_for(tags: dict) -> str:
    foot = str(tags.get("foot") or "").strip().lower()
    access = str(tags.get("access") or "").strip().lower()
    if foot in {"no", "private"} or access in {"no", "private"}:
        return "restricted"
    return "candidate"


def build_graph(structure: dict, fit_report: dict) -> dict:
    robust = fit_report["robust_fit"]
    features = [
        feature for feature in structure["features"]
        if feature.get("layer") in LAYERS
    ]
    nodes: dict[str, dict] = {}
    node_way_ids: dict[str, set[int]] = defaultdict(set)
    adjacency: dict[str, set[str]] = defaultdict(set)
    edges: list[dict] = []
    ways: list[dict] = []

    for feature in features:
        refs = [str(value) for value in feature.get("node_refs") or []]
        coords = feature.get("epsg3857") or []
        if len(refs) != len(coords) or len(refs) < 2:
            continue
        layer = str(feature["layer"])
        osm_id = int(feature["osm_id"])
        tags = dict(feature.get("tags") or {})
        traversal = traversal_for(tags)
        access = access_for(tags)
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
                "kind": "steps" if layer == "steps" else "pedestrian",
                "traversal": traversal,
                "access": access,
            })
        ways.append({
            "osm_way_id": osm_id,
            "kind": "steps" if layer == "steps" else "pedestrian",
            "name": tags.get("name"),
            "highway": tags.get("highway"),
            "traversal": traversal,
            "access": access,
            "surface": tags.get("surface"),
            "incline": tags.get("incline"),
            "node_refs": refs,
            "blender_xy": way_points,
        })
    for ref, node in nodes.items():
        node["degree"] = len(adjacency.get(ref, set()))
        node["way_ids"] = sorted(node_way_ids.get(ref, set()))
        node["junction_candidate"] = (
            node["degree"] >= 3 or len(node["way_ids"]) >= 2
        )

    stats = {
        "pedestrian_ways": sum(1 for way in ways if way["kind"] == "pedestrian"),
        "step_ways": sum(1 for way in ways if way["kind"] == "steps"),
        "nodes": len(nodes),
        "edges": len(edges),
        "junction_candidates": sum(
            1 for node in nodes.values() if node["junction_candidate"]
        ),
        "restricted_edges": sum(
            1 for edge in edges if edge["access"] == "restricted"
        ),
        "directed_edges": sum(
            1 for edge in edges if edge["traversal"] != "both"
        ),
    }
    return {
        "schema": SCHEMA,
        "status": "candidate",
        "fit_quality": fit_report.get("quality"),
        "fit_status": fit_report.get("status"),
        "stats": stats,
        "nodes": sorted(nodes.values(), key=lambda item: int(item["id"])),
        "edges": edges,
        "ways": ways,
        "notes": [
            "Grafo representa hints pedonais, não navmesh final.",
            "Travessia só é direcional com oneway:foot explícito.",
            "Escadas permanecem tipo separado para regras futuras de locomoção.",
            "Fit XY permanece candidate e deve ser tratado como referência de produção.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Constrói grafo pedonal a partir do OSM estrutural."
    )
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
    output_path.write_text(
        json.dumps(graph, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(graph["stats"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
