from __future__ import annotations

import argparse
import json
from pathlib import Path

CROSSING_MAX_DISTANCE_M = 2.5
SCHEMA = "bay-of-all-saints/r30a12-nav-links-v1"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build reviewed pedestrian nav links from R30A.11 evidence")
    parser.add_argument("--graph", required=True, help="R30A.11 pedestrian_graph.json")
    parser.add_argument("--scene", required=True, help="R30A.11 pedestrian_nav_scene.json")
    parser.add_argument("--output", required=True)
    parser.add_argument("--crossing-max-distance", type=float, default=CROSSING_MAX_DISTANCE_M)
    return parser.parse_args()


def crossing_link(anchor: dict, nodes: dict[str, dict], max_distance: float) -> dict:
    crossing_id = str(anchor.get("osm_node_id") or "")
    nearest_id = str(anchor.get("nearest_nav_node_id") or "")
    distance = float(anchor.get("nearest_nav_node_distance_m") or 0.0)
    exact_id = bool(crossing_id) and crossing_id == nearest_id and crossing_id in nodes
    within_threshold = distance <= max_distance
    approved = exact_id and within_threshold
    return {
        "source_object": anchor.get("source_object"),
        "osm_node_id": crossing_id,
        "nav_node_id": nearest_id,
        "distance_m": distance,
        "exact_osm_node_match": exact_id,
        "within_distance_threshold": within_threshold,
        "status": "reviewed_candidate" if approved else "blocked",
        "evidence": "exact_osm_node_id" if exact_id else "insufficient",
    }


def step_endpoint_anchors(graph: dict, nodes: dict[str, dict]) -> list[dict]:
    anchors: list[dict] = []
    for way in graph.get("ways", []):
        if way.get("kind") != "steps":
            continue
        refs = [str(value) for value in way.get("node_refs", [])]
        if len(refs) < 2:
            continue
        for endpoint_role, node_id in (("start", refs[0]), ("end", refs[-1])):
            node = nodes.get(node_id)
            if not node:
                anchors.append({
                    "osm_way_id": way.get("osm_way_id"),
                    "name": way.get("name"),
                    "endpoint_role": endpoint_role,
                    "osm_node_id": node_id,
                    "status": "blocked_missing_node",
                })
                continue
            anchors.append({
                "osm_way_id": way.get("osm_way_id"),
                "name": way.get("name"),
                "endpoint_role": endpoint_role,
                "osm_node_id": node_id,
                "blender_xy": node.get("blender_xy"),
                "incline": way.get("incline"),
                "access": way.get("access"),
                "status": "candidate",
            })
    return anchors


def build_contract(graph: dict, scene: dict, max_distance: float = CROSSING_MAX_DISTANCE_M) -> dict:
    nodes = {str(node["id"]): node for node in graph.get("nodes", [])}
    crossings = [crossing_link(anchor, nodes, max_distance) for anchor in scene.get("crossing_anchors", [])]
    steps = step_endpoint_anchors(graph, nodes)
    approved_crossings = sum(link["status"] == "reviewed_candidate" for link in crossings)
    blocked_crossings = len(crossings) - approved_crossings
    candidate_steps = sum(anchor["status"] == "candidate" for anchor in steps)
    return {
        "schema": SCHEMA,
        "revision": "R30A.12",
        "fit_quality": graph.get("fit_quality"),
        "crossing_max_distance_m": max_distance,
        "stats": {
            "crossing_links": len(crossings),
            "approved_crossing_links": approved_crossings,
            "blocked_crossing_links": blocked_crossings,
            "step_endpoint_anchors": len(steps),
            "candidate_step_endpoint_anchors": candidate_steps,
        },
        "crossing_links": crossings,
        "step_endpoint_anchors": steps,
        "notes": [
            "Crossing links require exact OSM node ID evidence and a bounded visual offset.",
            "Step endpoints preserve OSM way endpoints; start/end are not interpreted as top/bottom without vertical evidence.",
            "This contract is engine-agnostic and does not create a navmesh.",
        ],
    }


def main() -> None:
    args = parse_args()
    graph_path = Path(args.graph)
    scene_path = Path(args.scene)
    output_path = Path(args.output)
    graph = json.loads(graph_path.read_text(encoding="utf-8"))
    scene = json.loads(scene_path.read_text(encoding="utf-8"))
    contract = build_contract(graph, scene, args.crossing_max_distance)
    contract["sources"] = {
        "graph": str(graph_path.resolve()),
        "scene": str(scene_path.resolve()),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(contract, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(contract["stats"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
