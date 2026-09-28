from __future__ import annotations

import hashlib
import json
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

REVISION = "R30A.7"
ROOT_NAME = "35 GAMEPLAY | ROAD GRAPH R30A7"
WAYS_NAME = "35.1 GAMEPLAY | ROAD GRAPH WAYS"
JUNCTIONS_NAME = "35.2 GAMEPLAY | ROAD JUNCTIONS"
SOURCE_COLLIDER = "R30A5 | COLLISION | terrain proxy"

REPO = Path(__file__).resolve().parents[2]
GRAPH_PATH = REPO / "docs" / "reports" / "blender" / "r30a7" / "road_graph.json"
REPORT_PATH = REPO / "docs" / "reports" / "blender" / "r30a7" / "road_graph_scene.json"
OUTPUT_BLEND = REPO / "blender" / "salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a7_road_graph.blend"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def remove_previous() -> None:
    root = bpy.data.collections.get(ROOT_NAME)
    if not root:
        return
    for obj in list(root.all_objects):
        data = obj.data if obj.type == "CURVE" else None
        bpy.data.objects.remove(obj, do_unlink=True)
        if data and data.users == 0:
            bpy.data.curves.remove(data)
    for child in list(root.children):
        root.children.unlink(child)
        if child.users == 0:
            bpy.data.collections.remove(child)
    if root.name in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.unlink(root)
    if root.users == 0:
        bpy.data.collections.remove(root)


def make_collection(name: str, parent: bpy.types.Collection) -> bpy.types.Collection:
    collection = bpy.data.collections.new(name)
    parent.children.link(collection)
    return collection


def material(name: str, rgba: tuple[float, float, float, float]) -> bpy.types.Material:
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = rgba
    return mat


def build_world_bvh(source: bpy.types.Object) -> BVHTree:
    matrix = source.matrix_world
    vertices = [matrix @ vertex.co for vertex in source.data.vertices]
    polygons = [[index for index in poly.vertices] for poly in source.data.polygons]
    return BVHTree.FromPolygons(vertices, polygons, all_triangles=False)


def surface_z(bvh: BVHTree, x: float, y: float) -> float | None:
    hit = bvh.ray_cast(Vector((x, y, 200.0)), Vector((0.0, 0.0, -1.0)), 500.0)
    location = hit[0]
    return float(location.z) if location is not None else None


def create_way(way: dict, z_by_node: dict[str, float | None], collection: bpy.types.Collection,
               normal_mat: bpy.types.Material, restricted_mat: bpy.types.Material) -> bpy.types.Object | None:
    groups: list[list[tuple[float, float, float]]] = []
    current: list[tuple[float, float, float]] = []
    unresolved_count = 0
    for ref, xy in zip(way["node_refs"], way["blender_xy"]):
        z = z_by_node.get(str(ref))
        if z is None:
            unresolved_count += 1
            if len(current) >= 2:
                groups.append(current)
            current = []
            continue
        current.append((float(xy[0]), float(xy[1]), z + 0.18))
    if len(current) >= 2:
        groups.append(current)
    if not groups:
        return None

    curve = bpy.data.curves.new(f"R30A7_ROAD_{way['osm_way_id']}", type="CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = 0.09
    curve.bevel_resolution = 0
    for points in groups:
        spline = curve.splines.new("POLY")
        spline.points.add(len(points) - 1)
        for item, co in zip(spline.points, points):
            item.co = (*co, 1.0)
    obj = bpy.data.objects.new(f"R30A7 | ROAD | {way['osm_way_id']}", curve)
    collection.objects.link(obj)
    obj.hide_render = True
    obj.show_in_front = True
    obj.color = (0.12, 0.55, 1.0, 1.0) if way["access"] != "restricted" else (1.0, 0.2, 0.12, 1.0)
    curve.materials.append(restricted_mat if way["access"] == "restricted" else normal_mat)
    obj["boas_generated_revision"] = REVISION
    obj["boas_runtime_role"] = "road_graph_way"
    obj["boas_osm_way_id"] = int(way["osm_way_id"])
    obj["boas_direction"] = str(way["direction"])
    obj["boas_access"] = str(way["access"])
    obj["boas_highway"] = str(way.get("highway") or "")
    obj["boas_name"] = str(way.get("name") or "")
    obj["boas_unresolved_nodes"] = unresolved_count
    obj["boas_partial_source"] = unresolved_count > 0
    return obj


def create_junction(node: dict, z: float, collection: bpy.types.Collection) -> bpy.types.Object:
    obj = bpy.data.objects.new(f"R30A7 | JUNCTION | {node['id']}", None)
    collection.objects.link(obj)
    x, y = node["blender_xy"]
    obj.location = (float(x), float(y), z + 0.45)
    obj.empty_display_type = "SPHERE"
    obj.empty_display_size = 0.45
    obj.show_in_front = True
    obj.color = (1.0, 0.72, 0.08, 1.0)
    obj["boas_generated_revision"] = REVISION
    obj["boas_runtime_role"] = "road_junction_candidate"
    obj["boas_osm_node_id"] = str(node["id"])
    obj["boas_degree"] = int(node["degree"])
    obj["boas_way_count"] = len(node["way_ids"])
    return obj


def main() -> None:
    graph = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
    source = bpy.data.objects.get(SOURCE_COLLIDER)
    if source is None or source.type != "MESH":
        raise RuntimeError(f"Collider source not found: {SOURCE_COLLIDER}")

    remove_previous()
    root = bpy.data.collections.new(ROOT_NAME)
    bpy.context.scene.collection.children.link(root)
    ways_collection = make_collection(WAYS_NAME, root)
    junctions_collection = make_collection(JUNCTIONS_NAME, root)
    root["boas_generated_revision"] = REVISION
    root["boas_runtime_role"] = "road_graph"
    root["boas_fit_quality"] = str(graph.get("fit_quality"))
    root["boas_engine_binding"] = "unbound"

    normal_mat = material("R30A7 | road graph", (0.12, 0.55, 1.0, 1.0))
    restricted_mat = material("R30A7 | restricted road", (1.0, 0.2, 0.12, 1.0))
    bvh = build_world_bvh(source)
    z_by_node: dict[str, float | None] = {}
    for node in graph["nodes"]:
        x, y = node["blender_xy"]
        z_by_node[str(node["id"])] = surface_z(bvh, float(x), float(y))

    way_objects = []
    for way in graph["ways"]:
        obj = create_way(way, z_by_node, ways_collection, normal_mat, restricted_mat)
        if obj is not None:
            way_objects.append(obj)

    junction_objects = []
    for node in graph["nodes"]:
        if not node["junction_candidate"]:
            continue
        z = z_by_node.get(str(node["id"]))
        if z is not None:
            junction_objects.append(create_junction(node, z, junctions_collection))
    unresolved = sum(1 for value in z_by_node.values() if value is None)
    report = {
        "schema": "bay-of-all-saints/r30a7-road-graph-scene-v1",
        "revision": REVISION,
        "source_graph": str(GRAPH_PATH),
        "source_collider": SOURCE_COLLIDER,
        "fit_quality": graph.get("fit_quality"),
        "graph_stats": graph.get("stats"),
        "way_helpers_created": len(way_objects),
        "way_splines_created": sum(len(obj.data.splines) for obj in way_objects),
        "partial_way_helpers": sum(1 for obj in way_objects if bool(obj.get("boas_partial_source"))),
        "junction_helpers_created": len(junction_objects),
        "nodes_surface_resolved": len(z_by_node) - unresolved,
        "nodes_surface_unresolved": unresolved,
        "engine_binding": "unbound_engine_agnostic",
        "notes": [
            "Helpers representam topologia OSM, não lane graph final.",
            "Z foi projetado sobre o collider jogável R30A5.",
            "Sentido e restrições permanecem metadados, sem IA de trânsito nesta revisão.",
        ],
    }
    text = bpy.data.texts.get("BOAS_R30A7_ROAD_GRAPH") or bpy.data.texts.new("BOAS_R30A7_ROAD_GRAPH")
    text.clear()
    text.write(json.dumps(report, ensure_ascii=False, indent=2))

    # Gameplay review defaults: preserve helpers but keep collision/reference clutter out of normal viewport.
    for collection_name in (
        "33.1 RUNTIME | TERRAIN COLLISION",
        "SOURCE_GEOREF | STRUCTURAL_REFERENCE",
        "32.8 REFERENCE | GEOREF",
        "34 GAMEPLAY | COLLISION CHUNKS R30A6",
        "30 MVP | QA E GUIAS R27",
    ):
        collection = bpy.data.collections.get(collection_name)
        if collection is not None:
            collection.hide_viewport = True
            collection["boas_hidden_in_gameplay_review"] = True
    for camera in (obj for obj in bpy.data.objects if obj.type == "CAMERA"):
        camera.hide_viewport = True
        camera["boas_hidden_in_gameplay_review"] = True

    bpy.context.scene["boas_gameplay_review_visibility"] = "r30a7_clean"
    bpy.context.scene["boas_revision"] = REVISION
    bpy.context.scene["boas_road_graph_status"] = "candidate"
    bpy.context.scene["boas_road_graph_way_count"] = len(way_objects)
    bpy.context.scene["boas_road_graph_junction_count"] = len(junction_objects)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND))
    report["output_blend"] = str(OUTPUT_BLEND)
    report["output_sha256"] = sha256(OUTPUT_BLEND)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
