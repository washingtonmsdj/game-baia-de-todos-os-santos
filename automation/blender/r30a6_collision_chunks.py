from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import sys
from collections import defaultdict
from pathlib import Path

import bpy

REVISION = "R30A.6"
SOURCE_PROXY = "R30A5 | COLLISION | terrain proxy"
ROOT_NAME = "34 GAMEPLAY | COLLISION CHUNKS R30A6"
CHUNK_SIZES_M = (64, 128, 256)
MAX_CHUNKS = 80
MAX_CHUNK_POLYGONS = 15000
P95_CHUNK_POLYGONS = 10000


def cli_args() -> argparse.Namespace:
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    repo = Path(__file__).resolve().parents[2]
    default_blend = repo / "blender" / "salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a6_collision_chunks.blend"
    default_report = repo / "docs" / "reports" / "blender" / "r30a6" / "collision_chunks.json"
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--output-blend", default=str(default_blend))
    parser.add_argument("--report", default=str(default_report))
    args, _unknown = parser.parse_known_args(argv)
    return args


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def percentile(values: list[int], q: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    position = (len(ordered) - 1) * q
    low = math.floor(position)
    high = math.ceil(position)
    if low == high:
        return float(ordered[low])
    fraction = position - low
    return ordered[low] * (1.0 - fraction) + ordered[high] * fraction


def remove_previous() -> None:
    root = bpy.data.collections.get(ROOT_NAME)
    if not root:
        return
    for obj in list(root.all_objects):
        if obj.get("boas_generated_revision") == REVISION:
            mesh = obj.data if obj.type == "MESH" else None
            bpy.data.objects.remove(obj, do_unlink=True)
            if mesh and mesh.users == 0:
                bpy.data.meshes.remove(mesh)
    if root.name in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.unlink(root)
    if root.users == 0:
        bpy.data.collections.remove(root)


def polygon_cells(source: bpy.types.Object, size_m: int) -> dict[tuple[int, int], list[int]]:
    cells: dict[tuple[int, int], list[int]] = defaultdict(list)
    matrix = source.matrix_world
    for polygon in source.data.polygons:
        center = matrix @ polygon.center
        key = (math.floor(center.x / size_m), math.floor(center.y / size_m))
        cells[key].append(polygon.index)
    return dict(cells)


def distribution(cells: dict[tuple[int, int], list[int]], size_m: int) -> dict[str, object]:
    counts = [len(indices) for indices in cells.values()]
    return {
        "chunk_size_m": size_m,
        "chunk_count": len(counts),
        "min_polygons": min(counts) if counts else 0,
        "median_polygons": statistics.median(counts) if counts else 0.0,
        "p95_polygons": percentile(counts, 0.95),
        "max_polygons": max(counts) if counts else 0,
        "total_polygons": sum(counts),
    }


def choose_size(audits: list[dict[str, object]]) -> int:
    for audit in audits:
        if (
            audit["chunk_count"] <= MAX_CHUNKS
            and audit["max_polygons"] <= MAX_CHUNK_POLYGONS
            and audit["p95_polygons"] <= P95_CHUNK_POLYGONS
        ):
            return int(audit["chunk_size_m"])
    return int(audits[-1]["chunk_size_m"])

def make_chunk(
    source: bpy.types.Object,
    collection: bpy.types.Collection,
    key: tuple[int, int],
    polygon_indices: list[int],
    size_m: int,
) -> tuple[bpy.types.Object, dict[str, object]]:
    source_mesh = source.data
    used_vertices = sorted({vertex for pi in polygon_indices for vertex in source_mesh.polygons[pi].vertices})
    remap = {old: new for new, old in enumerate(used_vertices)}
    vertices = [source_mesh.vertices[index].co.copy() for index in used_vertices]
    faces = [[remap[index] for index in source_mesh.polygons[pi].vertices] for pi in polygon_indices]

    ix, iy = key
    mesh = bpy.data.meshes.new(f"R30A6_COLLISION_CHUNK_{ix}_{iy}")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(f"R30A6 | COLLISION | x{ix:+04d}_y{iy:+04d}", mesh)
    collection.objects.link(obj)
    obj.matrix_world = source.matrix_world.copy()
    obj.hide_render = True
    obj.display_type = "WIRE"
    obj["boas_generated_revision"] = REVISION
    obj["boas_runtime_role"] = "terrain_collision_chunk"
    obj["boas_source_object"] = source.name
    obj["boas_chunk_size_m"] = size_m
    obj["boas_chunk_x"] = ix
    obj["boas_chunk_y"] = iy
    obj["boas_export_candidate"] = True
    return obj, {
        "name": obj.name,
        "grid": [ix, iy],
        "nominal_bounds_xy_m": [
            ix * size_m,
            iy * size_m,
            (ix + 1) * size_m,
            (iy + 1) * size_m,
        ],
        "vertices": len(mesh.vertices),
        "polygons": len(mesh.polygons),
    }


def geometry_totals() -> dict[str, int]:
    meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    return {
        "objects": len(bpy.context.scene.objects),
        "meshes": len(meshes),
        "vertices": sum(len(obj.data.vertices) for obj in meshes),
        "polygons": sum(len(obj.data.polygons) for obj in meshes),
    }


def main() -> None:
    args = cli_args()
    output_blend = Path(args.output_blend).resolve()
    report_path = Path(args.report).resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    source_blend = Path(bpy.data.filepath).resolve()
    source = bpy.data.objects.get(SOURCE_PROXY)
    if not source or source.type != "MESH":
        raise RuntimeError(f"Collision proxy not found: {SOURCE_PROXY}")
    if source.get("boas_proxy_status") != "accepted_candidate":
        raise RuntimeError("R30A5 collision proxy is not an accepted candidate")

    before = geometry_totals()
    source_hash = sha256(source_blend)
    audits: list[dict[str, object]] = []
    cell_maps: dict[int, dict[tuple[int, int], list[int]]] = {}
    for size in CHUNK_SIZES_M:
        cells = polygon_cells(source, size)
        cell_maps[size] = cells
        audits.append(distribution(cells, size))
    selected_size = choose_size(audits)
    selected_cells = cell_maps[selected_size]

    remove_previous()
    root = bpy.data.collections.new(ROOT_NAME)
    bpy.context.scene.collection.children.link(root)
    root["boas_revision"] = REVISION
    root["boas_runtime_role"] = "terrain_collision_streaming_chunks"
    root["boas_chunk_size_m"] = selected_size
    root["boas_engine_binding"] = "unbound"

    chunk_records: list[dict[str, object]] = []
    for key in sorted(selected_cells):
        _, record = make_chunk(source, root, key, selected_cells[key], selected_size)
        chunk_records.append(record)
    polygon_sum = sum(record["polygons"] for record in chunk_records)
    vertex_sum = sum(record["vertices"] for record in chunk_records)
    exact_partition = polygon_sum == len(source.data.polygons)
    if not exact_partition:
        raise RuntimeError(f"Chunk polygon mismatch: {polygon_sum} != {len(source.data.polygons)}")

    selected_audit = next(item for item in audits if item["chunk_size_m"] == selected_size)
    policy_passed = (
        selected_audit["chunk_count"] <= MAX_CHUNKS
        and selected_audit["max_polygons"] <= MAX_CHUNK_POLYGONS
        and selected_audit["p95_polygons"] <= P95_CHUNK_POLYGONS
    )

    bpy.context.scene["boas_revision"] = REVISION
    bpy.context.scene["boas_collision_chunk_size_m"] = selected_size
    bpy.context.scene["boas_collision_chunk_count"] = len(chunk_records)
    bpy.context.scene["boas_engine_binding"] = "unbound"

    report = {
        "schema": "bay-of-all-saints/r30a6-collision-chunks-v1",
        "revision": REVISION,
        "source_blend": str(source_blend),
        "source_sha256": source_hash,
        "source_proxy": SOURCE_PROXY,
        "source_proxy_vertices": len(source.data.vertices),
        "source_proxy_polygons": len(source.data.polygons),
        "candidate_audits": audits,
        "selection_policy": {
            "max_chunks": MAX_CHUNKS,
            "max_chunk_polygons": MAX_CHUNK_POLYGONS,
            "p95_chunk_polygons": P95_CHUNK_POLYGONS,
        },
        "selected_chunk_size_m": selected_size,
        "selection_policy_passed": policy_passed,
        "chunk_count": len(chunk_records),
        "chunk_polygon_sum": polygon_sum,
        "exact_polygon_partition": exact_partition,
        "chunk_vertex_sum_with_boundary_duplication": vertex_sum,
        "vertex_duplication_ratio": vertex_sum / len(source.data.vertices),
        "chunks": chunk_records,
        "before": before,
        "after": geometry_totals(),
        "engine_binding": "unbound_engine_agnostic",
        "warnings": [
            "Chunk size is a production candidate and remains tunable after engine profiling.",
            "Chunks partition polygons by world-space centroid; boundary polygons belong to exactly one chunk.",
            "Road graph, navmesh and NPC navigation remain separate follow-up tasks.",
        ],
    }

    text = bpy.data.texts.get("BOAS_R30A6_COLLISION_CHUNKS") or bpy.data.texts.new("BOAS_R30A6_COLLISION_CHUNKS")
    text.clear()
    text.write(json.dumps(report, ensure_ascii=False, indent=2))

    output_blend.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(output_blend))
    report["output_blend"] = str(output_blend)
    report["output_sha256"] = sha256(output_blend)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "ok": True,
        "selected_chunk_size_m": selected_size,
        "chunk_count": len(chunk_records),
        "selected_audit": selected_audit,
        "exact_polygon_partition": exact_partition,
        "vertex_duplication_ratio": report["vertex_duplication_ratio"],
        "output_blend": str(output_blend),
        "output_sha256": report["output_sha256"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
