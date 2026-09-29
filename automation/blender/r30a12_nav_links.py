from __future__ import annotations

import hashlib
import json
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

REVISION = "R30A.12"
ROOT_NAME = "38 GAMEPLAY | NAV LINKS R30A12"
CROSSING_LINKS_NAME = "38.1 NAV | REVIEWED CROSSING LINKS"
STEP_ANCHORS_NAME = "38.2 NAV | STEP ENDPOINTS"
RUNTIME_NAV_NAME = "33.7 RUNTIME | NAV HINTS"
SOURCE_COLLIDER = "R30A5 | COLLISION | terrain proxy"

REPO = Path(__file__).resolve().parents[2]
CONTRACT_PATH = REPO / "docs" / "reports" / "blender" / "r30a12" / "nav_links.json"
GRAPH_PATH = REPO / "docs" / "reports" / "blender" / "r30a11" / "pedestrian_graph.json"
REPORT_PATH = REPO / "docs" / "reports" / "blender" / "r30a12" / "nav_links_scene.json"
OUTPUT_BLEND = REPO / "blender" / "salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a12_nav_links.blend"


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


def create_link_curve(
    name: str,
    start: Vector,
    end: Vector,
    collection: bpy.types.Collection,
    material: bpy.types.Material,
) -> bpy.types.Object:
    curve = bpy.data.curves.new(name + "_CURVE", type="CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = 0.18
    curve.bevel_resolution = 0
    spline = curve.splines.new("POLY")
    spline.points.add(1)
    spline.points[0].co = (*start, 1.0)
    spline.points[1].co = (*end, 1.0)
    obj = bpy.data.objects.new(name, curve)
    collection.objects.link(obj)
    curve.materials.append(material)
    obj.hide_render = True
    obj.show_in_front = True
    obj.color = (1.0, 0.82, 0.08, 1.0)
    return obj


def create_crossing_link(
    link: dict,
    node: dict,
    bvh: BVHTree,
    collection: bpy.types.Collection,
    material: bpy.types.Material,
) -> bpy.types.Object | None:
    source = bpy.data.objects.get(str(link.get("source_object") or ""))
    if source is None or source.type != "MESH":
        return None
    x, y = [float(value) for value in node["blender_xy"]]
    z = surface_z(bvh, x, y)
    if z is None:
        return None
    start = world_bounds_center(source) + Vector((0.0, 0.0, 0.32))
    end = Vector((x, y, z + 0.32))
    obj = create_link_curve(
        f"R30A12 | CROSSING LINK | {link['osm_node_id']}",
        start,
        end,
        collection,
        material,
    )
    obj["boas_generated_revision"] = REVISION
    obj["boas_runtime_role"] = "pedestrian_crossing_link_candidate"
    obj["boas_osm_node_id"] = str(link["osm_node_id"])
    obj["boas_nav_node_id"] = str(link["nav_node_id"])
    obj["boas_source_object"] = source.name
    obj["boas_link_evidence"] = str(link["evidence"])
    obj["boas_link_status"] = str(link["status"])
    obj["boas_visual_offset_m"] = float(link["distance_m"])
    return obj


def create_step_anchor(
    anchor: dict,
    bvh: BVHTree,
    collection: bpy.types.Collection,
) -> bpy.types.Object | None:
    xy = anchor.get("blender_xy")
    if not xy:
        return None
    x, y = [float(value) for value in xy]
    z = surface_z(bvh, x, y)
    if z is None:
        return None
    obj = bpy.data.objects.new(
        f"R30A12 | STEP ENDPOINT | {anchor['osm_way_id']} | {anchor['endpoint_role']}",
        None,
    )
    collection.objects.link(obj)
    obj.location = (x, y, z + 0.45)
    obj.empty_display_type = "CUBE"
    obj.empty_display_size = 0.85
    obj.show_in_front = True
    obj.color = (0.78, 0.24, 1.0, 1.0)
    obj["boas_generated_revision"] = REVISION
    obj["boas_runtime_role"] = "navigation_step_endpoint"
    obj["boas_osm_way_id"] = int(anchor["osm_way_id"])
    obj["boas_osm_node_id"] = str(anchor["osm_node_id"])
    obj["boas_endpoint_role"] = str(anchor["endpoint_role"])
    obj["boas_incline"] = str(anchor.get("incline") or "")
    obj["boas_access"] = str(anchor.get("access") or "")
    return obj


def main() -> None:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    graph = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
    nodes = {str(node["id"]): node for node in graph.get("nodes", [])}
    collider = bpy.data.objects.get(SOURCE_COLLIDER)
    if collider is None or collider.type != "MESH":
        raise RuntimeError(f"Collider source not found: {SOURCE_COLLIDER}")

    remove_previous()
    root = bpy.data.collections.new(ROOT_NAME)
    bpy.context.scene.collection.children.link(root)
    crossings_collection = make_collection(CROSSING_LINKS_NAME, root)
    steps_collection = make_collection(STEP_ANCHORS_NAME, root)
    runtime_nav = bpy.data.collections.get(RUNTIME_NAV_NAME)
    root["boas_generated_revision"] = REVISION
    root["boas_runtime_role"] = "reviewed_navigation_links"
    root["boas_engine_binding"] = "unbound"

    material = make_material("R30A12 | reviewed crossing links", (1.0, 0.82, 0.08, 1.0))
    bvh = build_world_bvh(collider)
    crossing_objects = []
    unresolved_crossings = []
    for link in contract.get("crossing_links", []):
        if link.get("status") != "reviewed_candidate":
            continue
        node = nodes.get(str(link.get("nav_node_id") or ""))
        if node is None:
            unresolved_crossings.append(str(link.get("osm_node_id") or ""))
            continue
        obj = create_crossing_link(link, node, bvh, crossings_collection, material)
        if obj is None:
            unresolved_crossings.append(str(link.get("osm_node_id") or ""))
            continue
        crossing_objects.append(obj)
        if runtime_nav is not None and obj.name not in runtime_nav.objects:
            runtime_nav.objects.link(obj)

    step_objects = []
    unresolved_steps = []
    for anchor in contract.get("step_endpoint_anchors", []):
        if anchor.get("status") != "candidate":
            continue
        obj = create_step_anchor(anchor, bvh, steps_collection)
        if obj is None:
            unresolved_steps.append({
                "osm_way_id": anchor.get("osm_way_id"),
                "osm_node_id": anchor.get("osm_node_id"),
                "endpoint_role": anchor.get("endpoint_role"),
            })
            continue
        step_objects.append(obj)
        if runtime_nav is not None and obj.name not in runtime_nav.objects:
            runtime_nav.objects.link(obj)

    bpy.context.scene["boas_revision"] = REVISION
    bpy.context.scene["boas_nav_crossing_links"] = len(crossing_objects)
    bpy.context.scene["boas_nav_step_endpoints"] = len(step_objects)
    bpy.context.scene["boas_engine_binding"] = "unbound"

    report = {
        "schema": "bay-of-all-saints/r30a12-nav-links-scene-v1",
        "revision": REVISION,
        "source_contract": str(CONTRACT_PATH),
        "source_collider": SOURCE_COLLIDER,
        "crossing_links_created": len(crossing_objects),
        "step_endpoint_anchors_created": len(step_objects),
        "unresolved_crossings": unresolved_crossings,
        "unresolved_step_endpoints": unresolved_steps,
        "engine_binding": "unbound_engine_agnostic",
        "notes": [
            "Crossing links are created only from reviewed exact OSM node matches.",
            "Step endpoint anchors preserve OSM start/end semantics without inferring top/bottom.",
            "Objects are navigation helpers, not a final navmesh.",
        ],
    }

    text = bpy.data.texts.get("BOAS_R30A12_NAV_LINKS") or bpy.data.texts.new("BOAS_R30A12_NAV_LINKS")
    text.clear()
    text.write(json.dumps(report, ensure_ascii=False, indent=2))

    OUTPUT_BLEND.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND))
    report["output_blend"] = str(OUTPUT_BLEND)
    report["output_sha256"] = sha256(OUTPUT_BLEND)
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "ok": True,
        "crossing_links_created": len(crossing_objects),
        "step_endpoint_anchors_created": len(step_objects),
        "unresolved_crossings": unresolved_crossings,
        "unresolved_step_endpoints": unresolved_steps,
        "output_blend": str(OUTPUT_BLEND),
        "output_sha256": report["output_sha256"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
