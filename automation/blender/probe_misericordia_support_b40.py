"""Sonda read-only da falha de apoio na Rua da Misericórdia antes da B41."""
import bpy, json, math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

root = Path(__file__).resolve().parents[2]
scene = bpy.context.scene
catalog = json.loads((root / "world/areas/mvp-centro-lacerda/blender-revisions.json").read_text(encoding="utf8"))
source = catalog["authoring_source"]
assert source["revision"] == "R30B.40"
assert Path(bpy.data.filepath).resolve() == (root / source["file"]).resolve()

contract = json.loads((root / "world/areas/mvp-centro-lacerda/production.json").read_text(encoding="utf8"))
audit = json.loads((root / "docs/reports/blender/rondesp_network_current.json").read_text(encoding="utf8"))
segment = next(row for row in audit["segments"] if row["edge_id"] == "way-803899198-seg-1")
ground = scene.objects[contract["export"]["road_object"]]
proxy = scene.objects[contract["export"]["terrain_proxy"]]
road_slots = {i for i, m in enumerate(ground.data.materials) if m and m.name in contract["export"]["road_materials"]}

def build_tree(ob):
    me = ob.data
    me.calc_loop_triangles()
    verts = [ob.matrix_world @ v.co for v in me.vertices]
    tris = [list(t.vertices) for t in me.loop_triangles]
    poly_material = [p.material_index for p in me.polygons]
    tri_material = [poly_material[t.polygon_index] for t in me.loop_triangles]
    return BVHTree.FromPolygons(verts, tris, all_triangles=True), tri_material

ground_tree, ground_mats = build_tree(ground)
proxy_tree, proxy_mats = build_tree(proxy)

def hit(tree, mats, ob, point, start=4.0, distance=8.0):
    co, normal, tri, _ = tree.ray_cast(point + Vector((0, 0, start)), Vector((0, 0, -1)), distance)
    if co is None:
        return None
    mat_index = mats[tri]
    material = ob.data.materials[mat_index].name if mat_index < len(ob.data.materials) and ob.data.materials[mat_index] else None
    return {
        "z": float(co.z),
        "delta_z_m": float(co.z - point.z),
        "normal_z": float(normal.z),
        "material_index": int(mat_index),
        "material": material,
        "road_material": bool(ob == ground and mat_index in road_slots),
    }

problem_samples = [
    row for row in segment["samples"]
    if any(issue in row.get("issues", []) for issue in ("vertical_discontinuity", "center_support_missing"))
]
candidate_objects = {}
bounds = {}
for ob in scene.objects:
    if ob.type != "MESH" or not ob.data or len(ob.data.vertices) == 0:
        continue
    coords = [ob.matrix_world @ Vector(corner) for corner in ob.bound_box]
    bounds[ob.name] = (
        min(p.x for p in coords), max(p.x for p in coords),
        min(p.y for p in coords), max(p.y for p in coords),
        min(p.z for p in coords), max(p.z for p in coords),
    )

for row in problem_samples:
    p = Vector(row["point"])
    for name, (minx, maxx, miny, maxy, minz, maxz) in bounds.items():
        if minx - 0.35 <= p.x <= maxx + 0.35 and miny - 0.35 <= p.y <= maxy + 0.35 and minz - 8 <= p.z <= maxz + 8:
            candidate_objects[name] = scene.objects[name]

candidate_trees = {}
for name, ob in candidate_objects.items():
    try:
        candidate_trees[name] = (*build_tree(ob), ob)
    except Exception:
        pass

samples = []
for row in problem_samples:
    point = Vector(row["point"])
    nearby = []
    for name, (tree, mats, ob) in candidate_trees.items():
        data = hit(tree, mats, ob, point)
        if data is None:
            continue
        data.update({"object": name, "collections": [c.name for c in ob.users_collection]})
        nearby.append(data)
    nearby.sort(key=lambda item: (abs(item["delta_z_m"]), item["object"]))
    samples.append({
        "fraction": row["fraction"],
        "point": row["point"],
        "issues": row["issues"],
        "audit_grade": row.get("grade"),
        "audit_bank": row.get("bank"),
        "ground": hit(ground_tree, ground_mats, ground, point, start=2.0, distance=4.0),
        "proxy": hit(proxy_tree, proxy_mats, proxy, point, start=2.0, distance=4.0),
        "nearby_hits": nearby[:10],
    })

road = next(
    (ob for ob in scene.objects if ob.name.startswith("R30A7 | ROAD |") and ob.get("boas_osm_way_id") == 803899198),
    None,
)
road_info = None
if road is not None:
    points = [
        list(road.matrix_world @ Vector(p.co[:3]))
        for spline in road.data.splines
        for p in spline.points
    ]
    road_info = {"object": road.name, "point_count": len(points), "points": points}

report = {
    "schema": "boas/misericordia-support-probe-v1",
    "source": source,
    "edge_id": segment["edge_id"],
    "osm_way_id": segment["osm_way_id"],
    "name": segment["name"],
    "segment_issues": segment["issues"],
    "road_curve": road_info,
    "problem_sample_count": len(samples),
    "candidate_mesh_count": len(candidate_trees),
    "samples": samples,
    "geometry_changed": False,
    "approved": False,
}
out = root / "artifacts/roads/rondesp/misericordia_b40_probe.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
print(json.dumps({
    "edge_id": report["edge_id"],
    "problem_sample_count": report["problem_sample_count"],
    "candidate_mesh_count": report["candidate_mesh_count"],
    "first_problem": report["samples"][0] if report["samples"] else None,
}, ensure_ascii=False))
