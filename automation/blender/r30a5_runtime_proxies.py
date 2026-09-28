from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import sys
from pathlib import Path

import bpy
from mathutils.bvhtree import BVHTree

REVISION = "R30A.5"
ROOT_NAME = "33 GAMEPLAY | RUNTIME PROXIES R30A5"
SOURCE_TERRAIN_PREFIX = "MVP | terreno corrigido"
RATIOS = (0.12, 0.25, 0.40)
P95_LIMIT_M = 0.25
MAX_LIMIT_M = 1.00
SAMPLE_LIMIT = 5000


def cli_args() -> argparse.Namespace:
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-blend", required=True)
    parser.add_argument("--report", required=True)
    return parser.parse_args(argv)

def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def mesh_totals() -> dict[str, int]:
    meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    return {
        "objects": len(bpy.context.scene.objects),
        "meshes": len(meshes),
        "vertices": sum(len(obj.data.vertices) for obj in meshes),
        "edges": sum(len(obj.data.edges) for obj in meshes),
        "polygons": sum(len(obj.data.polygons) for obj in meshes),
    }


def ensure_collection(name: str, parent: bpy.types.Collection | None = None) -> bpy.types.Collection:
    collection = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    container = parent.children if parent else bpy.context.scene.collection.children
    if collection.name not in container:
        container.link(collection)
    return collection

def delete_generated_root() -> None:
    root = bpy.data.collections.get(ROOT_NAME)
    if not root:
        return
    generated = [obj for obj in root.all_objects if obj.get("boas_generated_revision") == REVISION]
    for obj in generated:
        mesh = obj.data if obj.type == "MESH" else None
        bpy.data.objects.remove(obj, do_unlink=True)
        if mesh and mesh.users == 0:
            bpy.data.meshes.remove(mesh)
    children = list(root.children)
    for child in children:
        root.children.unlink(child)
        if child.users == 0:
            bpy.data.collections.remove(child)
    bpy.context.scene.collection.children.unlink(root)
    if root.users == 0:
        bpy.data.collections.remove(root)


def link_once(obj: bpy.types.Object, collection: bpy.types.Collection) -> None:
    if obj.name not in collection.objects:
        collection.objects.link(obj)


def source_objects(collection_name: str) -> list[bpy.types.Object]:
    collection = bpy.data.collections.get(collection_name)
    return list(collection.objects) if collection else []

def percentile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    position = (len(ordered) - 1) * q
    low = math.floor(position)
    high = math.ceil(position)
    if low == high:
        return ordered[low]
    fraction = position - low
    return ordered[low] * (1.0 - fraction) + ordered[high] * fraction


def sampled_proxy_error(source: bpy.types.Object, proxy: bpy.types.Object) -> dict[str, float | int]:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    tree = BVHTree.FromObject(proxy, depsgraph)
    vertices = source.data.vertices
    stride = max(1, len(vertices) // SAMPLE_LIMIT)
    distances: list[float] = []
    for index in range(0, len(vertices), stride):
        nearest = tree.find_nearest(vertices[index].co)
        if nearest and nearest[0] is not None:
            distances.append(float((vertices[index].co - nearest[0]).length))
    unit_scale = bpy.context.scene.unit_settings.scale_length or 1.0
    return {
        "samples": len(distances),
        "median_m": (statistics.median(distances) if distances else 0.0) * unit_scale,
        "p95_m": percentile(distances, 0.95) * unit_scale,
        "max_m": (max(distances) if distances else 0.0) * unit_scale,
    }

def create_collision_candidate(
    source: bpy.types.Object,
    collection: bpy.types.Collection,
    ratio: float,
) -> tuple[bpy.types.Object, dict[str, object]]:
    proxy = source.copy()
    proxy.data = source.data.copy()
    proxy.name = f"R30A5 | COLLISION | terrain proxy r{ratio:.2f}"
    collection.objects.link(proxy)
    proxy["boas_generated_revision"] = REVISION
    proxy["boas_source_object"] = source.name
    proxy["boas_runtime_role"] = "terrain_collision_proxy_candidate"
    proxy["boas_decimate_ratio"] = ratio

    modifier = proxy.modifiers.new(name="R30A5 | collision decimate", type="DECIMATE")
    modifier.decimate_type = "COLLAPSE"
    modifier.ratio = ratio
    modifier.use_collapse_triangulate = True
    bpy.ops.object.select_all(action="DESELECT")
    proxy.select_set(True)
    bpy.context.view_layer.objects.active = proxy
    bpy.ops.object.modifier_apply(modifier=modifier.name)

    proxy.data.materials.clear()
    proxy.hide_render = True
    proxy.display_type = "WIRE"
    error = sampled_proxy_error(source, proxy)
    error["ratio"] = ratio
    error["polygons"] = len(proxy.data.polygons)
    error["vertices"] = len(proxy.data.vertices)
    error["reduction_percent"] = 100.0 * (1.0 - len(proxy.data.polygons) / len(source.data.polygons))
    return proxy, error

def remove_proxy(proxy: bpy.types.Object) -> None:
    mesh = proxy.data
    bpy.data.objects.remove(proxy, do_unlink=True)
    if mesh.users == 0:
        bpy.data.meshes.remove(mesh)


def build_collision_proxy(source: bpy.types.Object, collection: bpy.types.Collection) -> tuple[bpy.types.Object, list[dict[str, object]], bool]:
    attempts: list[dict[str, object]] = []
    chosen: bpy.types.Object | None = None
    accepted = False
    for index, ratio in enumerate(RATIOS):
        proxy, metrics = create_collision_candidate(source, collection, ratio)
        passed = metrics["p95_m"] <= P95_LIMIT_M and metrics["max_m"] <= MAX_LIMIT_M
        metrics["passed_quality_gate"] = passed
        attempts.append(metrics)
        if passed:
            chosen = proxy
            accepted = True
            break
        if index < len(RATIOS) - 1:
            remove_proxy(proxy)
        else:
            chosen = proxy
    assert chosen is not None
    chosen.name = "R30A5 | COLLISION | terrain proxy"
    chosen["boas_proxy_status"] = "accepted_candidate" if accepted else "review_required"
    chosen["boas_proxy_p95_limit_m"] = P95_LIMIT_M
    chosen["boas_proxy_max_limit_m"] = MAX_LIMIT_M
    chosen["boas_proxy_p95_m"] = float(attempts[-1 if not accepted else len(attempts) - 1]["p95_m"])
    chosen["boas_proxy_max_m"] = float(attempts[-1 if not accepted else len(attempts) - 1]["max_m"])
    return chosen, attempts, accepted

def object_stats(objects: list[bpy.types.Object]) -> dict[str, object]:
    meshes = [obj for obj in objects if obj.type == "MESH"]
    return {
        "count": len(objects),
        "mesh_count": len(meshes),
        "vertices": sum(len(obj.data.vertices) for obj in meshes),
        "polygons": sum(len(obj.data.polygons) for obj in meshes),
        "objects": [obj.name for obj in objects],
    }


def find_source_terrain() -> bpy.types.Object:
    matches = [
        obj for obj in bpy.data.objects
        if obj.type == "MESH" and obj.name.startswith(SOURCE_TERRAIN_PREFIX)
    ]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one terrain source, found {len(matches)}: {[obj.name for obj in matches]}")
    return matches[0]


def mark_runtime_sources(objects: list[bpy.types.Object], collection: bpy.types.Collection, role: str) -> None:
    for obj in objects:
        link_once(obj, collection)
        obj["boas_runtime_role"] = role
        obj["boas_runtime_source_revision"] = "R30A.4"
        obj["boas_export_candidate"] = True

def main() -> None:
    args = cli_args()
    output_blend = Path(args.output_blend).resolve()
    report_path = Path(args.report).resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    source_blend = Path(bpy.data.filepath).resolve()
    before = mesh_totals()
    source_hash = sha256(source_blend)

    delete_generated_root()
    root = ensure_collection(ROOT_NAME)
    root["boas_revision"] = REVISION
    root["boas_runtime_engine"] = "engine_agnostic"
    root["boas_non_destructive_source"] = True

    names = {
        "collision": "33.1 RUNTIME | TERRAIN COLLISION",
        "road": "33.2 RUNTIME | ROAD DRIVEABLE",
        "walkable": "33.3 RUNTIME | WALKABLE",
        "crossing": "33.4 RUNTIME | CROSSINGS",
        "curb": "33.5 RUNTIME | CURBS",
        "water": "33.6 RUNTIME | WATER",
        "nav": "33.7 RUNTIME | NAV HINTS",
    }
    layers = {key: ensure_collection(name, root) for key, name in names.items()}

    terrain = find_source_terrain()
    proxy, proxy_attempts, proxy_accepted = build_collision_proxy(terrain, layers["collision"])
    proxy["boas_export_candidate"] = proxy_accepted
    proxy["boas_runtime_engine"] = "engine_agnostic"

    semantic_sources = {
        "road": source_objects("32.3 GAMEPLAY | ROAD DRIVEABLE"),
        "walkable": source_objects("32.4 GAMEPLAY | WALKABLE"),
        "crossing": source_objects("32.5 GAMEPLAY | PEDESTRIAN CROSSINGS"),
        "curb": source_objects("32.6 GAMEPLAY | CURB BOUNDARIES"),
        "water": source_objects("32.7 GAMEPLAY | WATER"),
    }
    roles = {
        "road": "road_driveable",
        "walkable": "walkable_surface",
        "crossing": "pedestrian_crossing",
        "curb": "curb_boundary",
        "water": "water_surface",
    }
    for key, objects in semantic_sources.items():
        mark_runtime_sources(objects, layers[key], roles[key])

    bpy.context.scene["boas_revision"] = REVISION
    bpy.context.scene["boas_runtime_pipeline"] = "semantic_sources_plus_derived_collision_proxy"
    bpy.context.scene["boas_engine_binding"] = "unbound"

    runtime_stats = {key: object_stats(objects) for key, objects in semantic_sources.items()}
    report = {
        "schema": "bay-of-all-saints/r30a5-runtime-proxies-v1",
        "revision": REVISION,
        "source_blend": str(source_blend),
        "source_sha256": source_hash,
        "source_terrain": {
            "name": terrain.name,
            "vertices": len(terrain.data.vertices),
            "polygons": len(terrain.data.polygons),
        },
        "collision_proxy": {
            "name": proxy.name,
            "accepted_candidate": proxy_accepted,
            "quality_limits_m": {"p95": P95_LIMIT_M, "max": MAX_LIMIT_M},
            "attempts": proxy_attempts,
            "final": {
                "vertices": len(proxy.data.vertices),
                "polygons": len(proxy.data.polygons),
                "status": proxy.get("boas_proxy_status"),
            },
        },
        "runtime_sources": runtime_stats,
        "nav_hints": {"count": 0, "status": "pending_next_revision"},
        "engine_binding": "unbound_engine_agnostic",
        "before": before,
        "after": mesh_totals(),
    }

    report["source_geometry_preserved"] = (
        len(terrain.data.vertices) == report["source_terrain"]["vertices"]
        and len(terrain.data.polygons) == report["source_terrain"]["polygons"]
    )
    report["warnings"] = [
        "Collision proxy is a runtime candidate, not final engine collision.",
        "Terrain collision still needs spatial chunking before large-world production.",
        "Road graph, navmesh and NPC navigation are not generated in this revision.",
    ]

    text = bpy.data.texts.get("BOAS_R30A5_RUNTIME_MANIFEST") or bpy.data.texts.new("BOAS_R30A5_RUNTIME_MANIFEST")
    text.clear()
    text.write(json.dumps(report, ensure_ascii=False, indent=2))

    output_blend.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(output_blend))
    report["output_blend"] = str(output_blend)
    report["output_sha256"] = sha256(output_blend)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "ok": True,
        "output_blend": str(output_blend),
        "output_sha256": report["output_sha256"],
        "collision_proxy_accepted": proxy_accepted,
        "collision_proxy_polygons": len(proxy.data.polygons),
        "attempts": proxy_attempts,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
