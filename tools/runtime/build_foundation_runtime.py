from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

SCHEMA = "bay-of-all-saints/foundation-runtime-v1"
ROOT = Path(__file__).resolve().parents[2]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def parse_number(value):
    if value is None:
        return None
    try:
        text = str(value).strip().lower().replace("m", "").strip()
        return float(text)
    except (TypeError, ValueError):
        return None


def polygon_area(points: list[list[float]]) -> float:
    if len(points) < 3:
        return 0.0
    total = 0.0
    for a, b in zip(points, points[1:] + points[:1]):
        total += a[0] * b[1] - b[0] * a[1]
    return abs(total) * 0.5


def terrain_points(payload: dict) -> np.ndarray:
    rows: list[list[float]] = []
    for obj in payload.get("objects", []):
        for point in obj.get("points_world", []):
            if len(point) >= 3:
                rows.append([float(point[0]), float(point[1]), float(point[2])])
    if not rows:
        raise ValueError("terrain samples are empty")
    return np.asarray(rows, dtype=np.float64)


def terrain_grid(points: np.ndarray, nx: int, nz: int) -> dict:
    min_x, min_z = points[:, 0].min(), points[:, 1].min()
    max_x, max_z = points[:, 0].max(), points[:, 1].max()
    xs = np.linspace(min_x, max_x, nx)
    zs = np.linspace(min_z, max_z, nz)
    queries = np.asarray([(x, z) for z in zs for x in xs], dtype=np.float64)
    out = np.empty(len(queries), dtype=np.float64)
    source_xy = points[:, :2]
    source_h = points[:, 2]
    for start in range(0, len(queries), 256):
        q = queries[start : start + 256]
        d2 = ((q[:, None, :] - source_xy[None, :, :]) ** 2).sum(axis=2)
        nearest = np.argpartition(d2, kth=3, axis=1)[:, :4]
        nd2 = np.take_along_axis(d2, nearest, axis=1)
        weights = 1.0 / np.maximum(nd2, 0.25)
        heights = source_h[nearest]
        out[start : start + len(q)] = (heights * weights).sum(axis=1) / weights.sum(axis=1)
    return {
        "nx": nx,
        "nz": nz,
        "min_x": round(float(min_x), 4),
        "max_x": round(float(max_x), 4),
        "min_z": round(float(min_z), 4),
        "max_z": round(float(max_z), 4),
        "heights": [round(float(v), 3) for v in out],
    }


def in_bounds(point: list[float], bounds: dict, margin: float = 0.0) -> bool:
    x, z = point[:2]
    return (
        bounds["min_x"] - margin <= x <= bounds["max_x"] + margin
        and bounds["min_z"] - margin <= z <= bounds["max_z"] + margin
    )


def clip_polyline(points: list[list[float]], bounds: dict, margin: float = 100.0) -> list[list[list[float]]]:
    runs: list[list[list[float]]] = []
    current: list[list[float]] = []
    for point in points:
        p = [round(float(point[0]), 3), round(float(point[1]), 3)]
        if in_bounds(p, bounds, margin):
            current.append(p)
        elif current:
            if len(current) >= 2:
                runs.append(current)
            current = []
    if len(current) >= 2:
        runs.append(current)
    return runs


def building_height(tags: dict, area: float) -> tuple[float, str]:
    height = parse_number(tags.get("height"))
    if height and 2.0 <= height <= 180.0:
        return height, "osm_height"
    levels = parse_number(tags.get("building:levels"))
    if levels and 1 <= levels <= 50:
        return levels * 3.1, "osm_levels"
    if area > 1800:
        return 16.0, "visual_proxy"
    if area > 650:
        return 11.5, "visual_proxy"
    return 8.0, "visual_proxy"


def build_buildings(features: list[dict], bounds: dict) -> list[dict]:
    buildings: list[dict] = []
    for feature in features:
        if feature.get("layer") != "buildings" or not feature.get("closed"):
            continue
        points = [[float(x), float(z)] for x, z in feature.get("blender_xy", [])]
        if len(points) < 4 or not any(in_bounds(p, bounds, 80.0) for p in points):
            continue
        if points[0] == points[-1]:
            points = points[:-1]
        area = polygon_area(points)
        height, source = building_height(feature.get("tags") or {}, area)
        buildings.append({
            "id": f"{feature.get('osm_type')}:{feature.get('osm_id')}",
            "polygon": [[round(x, 3), round(z, 3)] for x, z in points],
            "height_m": round(height, 2),
            "height_source": source,
            "area_m2_projected": round(area, 2),
        })
    return buildings


def build_lines(features: list[dict], layer: str, bounds: dict, margin: float = 120.0) -> list[dict]:
    items: list[dict] = []
    for feature in features:
        if feature.get("layer") != layer:
            continue
        points = feature.get("blender_xy") or []
        for index, run in enumerate(clip_polyline(points, bounds, margin)):
            items.append({
                "id": f"{feature.get('osm_type')}:{feature.get('osm_id')}:{index}",
                "points": run,
                "tags": {
                    key: value
                    for key, value in (feature.get("tags") or {}).items()
                    if key in {"name", "highway", "barrier", "natural", "man_made"}
                },
            })
    return items


def road_bounds(road_graph: dict) -> dict:
    coords = [node.get("blender_xy") for node in road_graph.get("nodes", [])]
    coords = [c for c in coords if isinstance(c, list) and len(c) >= 2]
    xs = [float(c[0]) for c in coords]
    zs = [float(c[1]) for c in coords]
    return {
        "min_x": min(xs),
        "max_x": max(xs),
        "min_z": min(zs),
        "max_z": max(zs),
    }


def build_payload(structural: dict, terrain: dict, roads: dict, water: dict, nx: int, nz: int) -> dict:
    bounds = road_bounds(roads)
    points = terrain_points(terrain)
    features = structural.get("features", [])
    buildings = build_buildings(features, bounds)
    waterfront = build_lines(features, "waterfront", bounds, 180.0)
    coastline = build_lines(features, "coastline", bounds, 180.0)
    pedestrian = build_lines(features, "pedestrian", bounds, 80.0)
    steps = build_lines(features, "steps", bounds, 80.0)
    return {
        "schema": SCHEMA,
        "coordinate_space": "blender_world_meters",
        "status": "foundation_candidate",
        "authoritative_notes": {
            "xy": "OSM/georef structural reference candidate",
            "terrain": "sampled from current Blender gameplay terrain; vertical fit still insufficient",
            "building_heights": "OSM height/levels when present, otherwise visual proxy only",
        },
        "bounds": {k: round(float(v), 3) for k, v in bounds.items()},
        "terrain": {
            "source_sample_count": int(len(points)),
            "grid": terrain_grid(points, nx, nz),
        },
        "city": {
            "buildings": buildings,
            "waterfront": waterfront,
            "coastline": coastline,
            "pedestrian": pedestrian,
            "steps": steps,
        },
        "water": {
            "level_m": water.get("water_level_m", 0.35),
            "vertical_range_m": water.get("volume", {}).get("vertical_range_m", [-16.0, 0.35]),
            "swimmable": bool(water.get("gameplay", {}).get("swimmable", True)),
            "diveable": bool(water.get("gameplay", {}).get("diveable", True)),
            "boats_supported": bool(water.get("gameplay", {}).get("boats_supported", True)),
        },
        "stats": {
            "buildings": len(buildings),
            "waterfront_runs": len(waterfront),
            "coastline_runs": len(coastline),
            "pedestrian_runs": len(pedestrian),
            "step_runs": len(steps),
            "road_nodes": len(roads.get("nodes", [])),
            "road_edges": len(roads.get("edges", [])),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--structural", type=Path, default=ROOT / "artifacts/structural-pipeline/mvp-centro-lacerda/structural_reference.json")
    parser.add_argument("--terrain", type=Path, default=ROOT / "docs/reports/blender/r30a1/terrain_samples.json")
    parser.add_argument("--roads", type=Path, default=ROOT / "docs/reports/blender/r30a7/road_graph.json")
    parser.add_argument("--water", type=Path, default=ROOT / "docs/reports/blender/r30a8/water_runtime_contract.json")
    parser.add_argument("--output", type=Path, default=ROOT / "prototypes/threejs-water-lab/public/data/foundation_runtime.json")
    parser.add_argument("--nx", type=int, default=96)
    parser.add_argument("--nz", type=int, default=112)
    args = parser.parse_args()
    payload = build_payload(
        load_json(args.structural), load_json(args.terrain), load_json(args.roads), load_json(args.water), args.nx, args.nz
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(json.dumps({"output": str(args.output), "schema": payload["schema"], "stats": payload["stats"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
