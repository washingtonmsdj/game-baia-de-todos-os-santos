from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

REVISION = "R30A.11"
ROOT_NAME = "37 GAMEPLAY | NAV HINTS R30A11"
PATHS_NAME = "37.1 NAV | PEDESTRIAN PATHS"
STEPS_NAME = "37.2 NAV | STEPS"
CROSSINGS_NAME = "37.3 NAV | CROSSINGS"
JUNCTIONS_NAME = "37.4 NAV | JUNCTIONS"
SOURCES_NAME = "37.5 NAV | WALKABLE SOURCES"
RUNTIME_NAV_NAME = "33.7 RUNTIME | NAV HINTS"
SOURCE_COLLIDER = "R30A5 | COLLISION | terrain proxy"

REPO = Path(__file__).resolve().parents[2]
GRAPH_PATH = REPO / "docs" / "reports" / "blender" / "r30a11" / "pedestrian_graph.json"
REPORT_PATH = REPO / "docs" / "reports" / "blender" / "r30a11" / "pedestrian_nav_scene.json"
OUTPUT_BLEND = REPO / "blender" / "salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a11_pedestrian_nav.blend"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def remove_previous() -> None:
    root = bpy.data.collections.get(ROOT_NAME)
    if root is None:
        return
    generated = [
        obj for obj in root.all_objects
        if str(obj.get("boas_generated_revision") or "") == REVISION
    ]
    for obj in generated:
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
    collection = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if collection.name not in parent.children:
        parent.children.link(collection)
    return collection


def make_material(name: str, rgba: tuple[float, float, float, float]) -> bpy.types.Material:
    material = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    material.diffuse_color = rgba
    return material


def build_world_bvh(source: bpy.types.Object) -> BVHTree:
    matrix = source.matrix_world
    vertices = [matrix @ vertex.co for vertex in source.data.vertices]
    polygons = [[index for index in poly.vertices] for poly in source.data.polygons]
    return BVHTree.FromPolygons(vertices, polygons, all_triangles=False)


def surface_z(bvh: BVHTree, x: float, y: float) -> float | None:
    hit = bvh.ray_cast(Vector((x, y, 200.0)), Vector((0.0, 0.0, -1.0)), 500.0)
    return float(hit[0].z) if hit[0] is not None else None


def world_bounds_center(obj: bpy.types.Object) -> Vector:
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    return sum(corners, Vector()) / len(corners)


def create_path(
    way: dict,
    z_by_node: dict[str, float | None],
    collection: bpy.types.Collection,
    material: bpy.types.Material,
) -> bpy.types.Object | None:
    groups: list[list[tuple[float, float, float]]] = []
    current: list[tuple[float, float, float]] = []
    unresolved = 0
    for ref, xy in zip(way["node_refs"], way["blender_xy"]):
        z = z_by_node.get(str(ref))
        if z is None:
            unresolved += 1
            if len(current) >= 2:
                groups.append(current)
            current = []
            continue
        current.append((float(xy[0]), float(xy[1]), z + 0.24))
    if len(current) >= 2:
        groups.append(current)
    if not groups:
        return None
    curve = bpy.data.curves.new(f"R30A11_NAV_{way['kind']}_{way['osm_way_id']}", type="CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = 0.35 if way["kind"] == "pedestrian" else 0.50
    curve.bevel_resolution = 0
    for points in groups:
        spline = curve.splines.new("POLY")
        spline.points.add(len(points) - 1)
        for item, coordinate in zip(spline.points, points):
            item.co = (*coordinate, 1.0)
    obj = bpy.data.objects.new(
        f"R30A11 | {way['kind'].upper()} | {way['osm_way_id']}", curve
    )
    collection.objects.link(obj)
    curve.materials.append(material)
    obj.hide_render = True
    obj.show_in_front = True
    obj.color = (0.12, 0.95, 0.30, 1.0) if way["kind"] == "pedestrian" else (0.75, 0.20, 1.0, 1.0)
    obj["boas_generated_revision"] = REVISION
    obj["boas_runtime_role"] = "navigation_steps" if way["kind"] == "steps" else "navigation_path"
    obj["boas_osm_way_id"] = int(way["osm_way_id"])
    obj["boas_access"] = str(way["access"])
    obj["boas_traversal"] = str(way["traversal"])
    obj["boas_surface"] = str(way.get("surface") or "")
    obj["boas_partial_source"] = unresolved > 0
    obj["boas_unresolved_nodes"] = unresolved
    return obj


def nearest_node(center: Vector, resolved_nodes: list[tuple[str, float, float, float]]) -> tuple[str | None, float | None]:
    best_id = None
    best_distance = None
    for node_id, x, y, _z in resolved_nodes:
        distance = math.hypot(center.x - x, center.y - y)
        if best_distance is None or distance < best_distance:
            best_id, best_distance = node_id, distance
    return best_id, best_distance


def create_crossing_anchor(
    source: bpy.types.Object,
    collection: bpy.types.Collection,
    resolved_nodes: list[tuple[str, float, float, float]],
) -> bpy.types.Object:
    center = world_bounds_center(source)
    nearest_id, nearest_distance = nearest_node(center, resolved_nodes)
    osm_node_id = str(source.get("osm_node_id") or "")
    obj = bpy.data.objects.new(f"R30A11 | CROSSING | {osm_node_id or source.name}", None)
    collection.objects.link(obj)
    obj.location = center + Vector((0.0, 0.0, 0.35))
    obj.empty_display_type = "CIRCLE"
    obj.empty_display_size = 1.2
    obj.show_in_front = True
    obj.color = (1.0, 0.78, 0.05, 1.0)
    obj["boas_generated_revision"] = REVISION
    obj["boas_runtime_role"] = "pedestrian_crossing_anchor"
    obj["boas_source_object"] = source.name
    obj["boas_osm_node_id"] = osm_node_id
    obj["boas_nearest_nav_node_id"] = nearest_id or ""
    obj["boas_nearest_nav_node_distance_m"] = (
        float(nearest_distance) if nearest_distance is not None else -1.0
    )
    obj["boas_connection_status"] = "review_only_not_connected"
    return obj


def create_junction(node: dict, z: float, collection: bpy.types.Collection) -> bpy.types.Object:
    obj = bpy.data.objects.new(f"R30A11 | NAV JUNCTION | {node['id']}", None)
    collection.objects.link(obj)
    x, y = node["blender_xy"]
    obj.location = (float(x), float(y), z + 0.42)
    obj.empty_display_type = "SPHERE"
    obj.empty_display_size = 0.9
    obj.show_in_front = True
    obj.color = (0.1, 0.85, 0.95, 1.0)
    obj["boas_generated_revision"] = REVISION
    obj["boas_runtime_role"] = "navigation_junction_candidate"
    obj["boas_osm_node_id"] = str(node["id"])
    obj["boas_degree"] = int(node["degree"])
    return obj


def main() -> None:
    graph = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
    collider = bpy.data.objects.get(SOURCE_COLLIDER)
    if collider is None or collider.type != "MESH":
        raise RuntimeError(f"Collider source not found: {SOURCE_COLLIDER}")

    remove_previous()
    root = bpy.data.collections.new(ROOT_NAME)
    bpy.context.scene.collection.children.link(root)
    paths_collection = make_collection(PATHS_NAME, root)
    steps_collection = make_collection(STEPS_NAME, root)
    crossings_collection = make_collection(CROSSINGS_NAME, root)
    junctions_collection = make_collection(JUNCTIONS_NAME, root)
    sources_collection = make_collection(SOURCES_NAME, root)
    runtime_nav = bpy.data.collections.get(RUNTIME_NAV_NAME)
    root["boas_generated_revision"] = REVISION
    root["boas_runtime_role"] = "navigation_hints"
    root["boas_engine_binding"] = "unbound"
    root["boas_fit_quality"] = str(graph.get("fit_quality"))

    path_material = make_material("R30A11 | pedestrian hints", (0.12, 0.95, 0.30, 1.0))
    step_material = make_material("R30A11 | step hints", (0.75, 0.20, 1.0, 1.0))
    bvh = build_world_bvh(collider)
    z_by_node: dict[str, float | None] = {}
    resolved_nodes: list[tuple[str, float, float, float]] = []
    for node in graph["nodes"]:
        x, y = node["blender_xy"]
        z = surface_z(bvh, float(x), float(y))
        z_by_node[str(node["id"])] = z
        if z is not None:
            resolved_nodes.append((str(node["id"]), float(x), float(y), z))
    path_objects = []
    step_objects = []
    for way in graph["ways"]:
        target = steps_collection if way["kind"] == "steps" else paths_collection
        material = step_material if way["kind"] == "steps" else path_material
        obj = create_path(way, z_by_node, target, material)
        if obj is None:
            continue
        (step_objects if way["kind"] == "steps" else path_objects).append(obj)
        if runtime_nav is not None and obj.name not in runtime_nav.objects:
            runtime_nav.objects.link(obj)

    junction_objects = []
    for node in graph["nodes"]:
        if not node["junction_candidate"]:
            continue
        z = z_by_node.get(str(node["id"]))
        if z is None:
            continue
        obj = create_junction(node, z, junctions_collection)
        junction_objects.append(obj)
        if runtime_nav is not None and obj.name not in runtime_nav.objects:
            runtime_nav.objects.link(obj)

    crossing_source = bpy.data.collections.get("32.5 GAMEPLAY | PEDESTRIAN CROSSINGS")
    crossing_objects = []
    if crossing_source is not None:
        for source in crossing_source.objects:
            if source.type != "MESH":
                continue
            obj = create_crossing_anchor(source, crossings_collection, resolved_nodes)
            crossing_objects.append(obj)
            if runtime_nav is not None and obj.name not in runtime_nav.objects:
                runtime_nav.objects.link(obj)
    walkable_source = bpy.data.collections.get("32.4 GAMEPLAY | WALKABLE")
    walkable_sources = []
    if walkable_source is not None:
        for source in walkable_source.objects:
            if source.name not in sources_collection.objects:
                sources_collection.objects.link(source)
            status = str(source.get("status") or "")
            source["boas_navigation_source"] = True
            source["boas_navigation_source_revision"] = REVISION
            source["boas_navigation_source_status"] = (
                "reference_only" if "preservado" in status.lower() else "candidate"
            )
            walkable_sources.append({
                "name": source.name,
                "status": source["boas_navigation_source_status"],
            })

    crossing_distances = [
        float(obj.get("boas_nearest_nav_node_distance_m", -1.0))
        for obj in crossing_objects
        if float(obj.get("boas_nearest_nav_node_distance_m", -1.0)) >= 0.0
    ]
    crossing_details = [
        {
            "source_object": str(obj.get("boas_source_object") or ""),
            "osm_node_id": str(obj.get("boas_osm_node_id") or ""),
            "nearest_nav_node_id": str(obj.get("boas_nearest_nav_node_id") or ""),
            "nearest_nav_node_distance_m": float(obj.get("boas_nearest_nav_node_distance_m", -1.0)),
            "connection_status": str(obj.get("boas_connection_status") or ""),
        }
        for obj in crossing_objects
    ]
    unresolved = sum(1 for value in z_by_node.values() if value is None)
    report = {
        "schema": "bay-of-all-saints/r30a11-pedestrian-nav-scene-v1",
        "revision": REVISION,
        "source_graph": str(GRAPH_PATH),
        "source_collider": SOURCE_COLLIDER,
        "fit_quality": graph.get("fit_quality"),
        "graph_stats": graph.get("stats"),
        "path_helpers_created": len(path_objects),
        "step_helpers_created": len(step_objects),
        "junction_helpers_created": len(junction_objects),
        "crossing_anchors_created": len(crossing_objects),
        "walkable_sources_linked": walkable_sources,
        "nodes_surface_resolved": len(z_by_node) - unresolved,
        "nodes_surface_unresolved": unresolved,
        "crossing_nearest_nav_distance_m": crossing_distances,
        "crossing_anchors": crossing_details,
        "crossing_connection_policy": "review_only_not_connected",
        "engine_binding": "unbound_engine_agnostic",
        "notes": [
            "Hints pedonais não são navmesh final.",
            "Travessias recebem apenas anchor + distância ao nó pedonal mais próximo; nenhuma conexão é inventada.",
            "Escadas permanecem categoria separada para regras futuras de personagem/NPC.",
            "Walkable sources legadas preservadas continuam reference_only quando já marcadas como substituídas.",
        ],
    }
    text = bpy.data.texts.get("BOAS_R30A11_PEDESTRIAN_NAV") or bpy.data.texts.new(
        "BOAS_R30A11_PEDESTRIAN_NAV"
    )
    text.clear()
    text.write(json.dumps(report, ensure_ascii=False, indent=2))

    road_graph = bpy.data.collections.get("35 GAMEPLAY | ROAD GRAPH R30A7")
    if road_graph is not None:
        road_graph.hide_viewport = True
        road_graph["boas_hidden_in_navigation_review"] = True
    qa_collection = bpy.data.collections.get("30 MVP | QA E GUIAS R27")
    if qa_collection is not None:
        qa_collection.hide_viewport = True
        qa_collection["boas_hidden_in_navigation_review"] = True
    for camera in (obj for obj in bpy.data.objects if obj.type == "CAMERA"):
        camera.hide_viewport = True
        camera["boas_hidden_in_navigation_review"] = True
    for helper in (obj for obj in bpy.data.objects if obj.name.startswith(("R27 |", "APOIO TERRENO |"))):
        helper.hide_viewport = True
        helper["boas_hidden_in_navigation_review"] = True
    root.hide_viewport = False
    bpy.context.scene["boas_revision"] = REVISION
    bpy.context.scene["boas_navigation_status"] = "candidate_hints"
    bpy.context.scene["boas_navigation_path_count"] = len(path_objects)
    bpy.context.scene["boas_navigation_step_count"] = len(step_objects)
    bpy.context.scene["boas_navigation_crossing_count"] = len(crossing_objects)
    bpy.context.scene["boas_navigation_review_visibility"] = "r30a11_clean"

    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND))
    report["output_blend"] = str(OUTPUT_BLEND)
    report["output_sha256"] = sha256(OUTPUT_BLEND)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
