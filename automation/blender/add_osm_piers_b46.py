"""R30B.46: materializa píeres OSM do waterfront sem inventar largura nos ways lineares."""
import bpy, json, hashlib, statistics, runpy
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

root = Path(__file__).resolve().parents[2]
scene = bpy.context.scene
reg = json.loads((root / "world/areas/mvp-centro-lacerda/blender-revisions.json").read_text(encoding="utf8"))
src = reg["validation_source"]
assert src["revision"] == "R30B.45"
srcfile = root / src["file"]
assert Path(bpy.data.filepath).resolve() == srcfile.resolve()
assert hashlib.sha256(srcfile.read_bytes()).hexdigest() == src["sha256"]
out = root / "blender/salvador_lacerda_r30b46_pieres_osm.blend"
assert not out.exists()

api = runpy.run_path(str(root / "automation/blender/component_fingerprint.py"))
sig = api["signature"]
ref = json.loads((root / "artifacts/structural-pipeline/mvp-centro-lacerda/structural_reference.json").read_text(encoding="utf8"))
production = json.loads((root / "world/areas/mvp-centro-lacerda/production.json").read_text(encoding="utf8"))
water_contract = json.loads((root / "docs/reports/blender/r30a8/water_runtime_contract.json").read_text(encoding="utf8"))

ids = {1321682676, 1321682677, 1426173139, 1426173140}
features = [f for f in ref["features"] if int(f.get("osm_id", -1)) in ids]
assert len(features) == 4
assert all(f.get("layer") == "waterfront" and f.get("tags", {}).get("man_made") == "pier" for f in features)

ground = scene.objects[production["export"]["road_object"]]
water = scene.objects[water_contract["surface_object"]]
quay = next(o for o in scene.objects if o.name.startswith("CAIS | conten"))
protected = {o.name: sig(o) for o in (ground, water, quay)}

me = ground.data
me.calc_loop_triangles()
gtree = BVHTree.FromPolygons(
    [ground.matrix_world @ v.co for v in me.vertices],
    [list(t.vertices) for t in me.loop_triangles],
    all_triangles=True,
)

water_level = float(water_contract["water_level_m"])
land_controls = []
for f in features:
    for x, y in f["blender_xy"]:
        p, n, i, d = gtree.ray_cast(Vector((float(x), float(y), 120)), Vector((0, 0, -1)), 200)
        if p is not None and p.z > water_level + 1.0:
            land_controls.append(float(p.z))
assert len(land_controls) >= 5
deck_z = float(statistics.median(land_controls))
assert 6.5 < deck_z < 8.0

coll = bpy.data.collections.get("WATERFRONT | PIERS OSM | B46")
if coll is None:
    coll = bpy.data.collections.new("WATERFRONT | PIERS OSM | B46")
    scene.collection.children.link(coll)
assert not coll.objects

mat = bpy.data.materials.get("B46 | Pier OSM | referencia estrutural")
if mat is None:
    mat = bpy.data.materials.new("B46 | Pier OSM | referencia estrutural")
    mat.diffuse_color = (0.33, 0.36, 0.38, 1.0)

mat_line = bpy.data.materials.get("B46 | Pier linear | eixo sem largura")
if mat_line is None:
    mat_line = bpy.data.materials.new("B46 | Pier linear | eixo sem largura")
    mat_line.diffuse_color = (0.75, 0.55, 0.15, 1.0)

created = []
for f in sorted(features, key=lambda x: int(x["osm_id"])):
    oid = int(f["osm_id"])
    coords = [(float(x), float(y), deck_z) for x, y in f["blender_xy"]]
    if f["closed"]:
        if len(coords) > 1 and coords[0][:2] == coords[-1][:2]:
            coords = coords[:-1]
        mesh = bpy.data.meshes.new(f"PIER_OSM_{oid}_B46")
        mesh.from_pydata(coords, [], [list(range(len(coords)))])
        mesh.update()
        ob = bpy.data.objects.new(f"PIER OSM | {oid} | footprint real", mesh)
        coll.objects.link(ob)
        ob.data.materials.append(mat)
        role = "reference_surface"
    else:
        curve = bpy.data.curves.new(f"PIER_OSM_{oid}_B46", "CURVE")
        curve.dimensions = "3D"
        curve.resolution_u = 1
        sp = curve.splines.new("POLY")
        sp.points.add(len(coords) - 1)
        for p, co in zip(sp.points, coords):
            p.co = (*co, 1.0)
        curve.bevel_depth = 0.06
        curve.bevel_resolution = 1
        ob = bpy.data.objects.new(f"PIER OSM | {oid} | eixo sem largura", curve)
        coll.objects.link(ob)
        ob.data.materials.append(mat_line)
        role = "reference_centerline_width_unknown"

    ob["boas_osm_type"] = "way"
    ob["boas_osm_id"] = oid
    ob["boas_source_layer"] = "waterfront"
    ob["boas_source_tag"] = "man_made=pier"
    ob["boas_classification"] = "KEEP_REAL_REFERENCE"
    ob["boas_runtime_role"] = role
    ob["boas_gameplay_approved"] = False
    ob["boas_width_verified_m"] = 0.0 if f["closed"] else -1.0
    ob["boas_width_status"] = "footprint_from_osm" if f["closed"] else "unknown_do_not_invent"
    ob["boas_deck_z_candidate_m"] = deck_z
    ob["boas_deck_z_basis"] = "median of current functional land surface hits at OSM pier vertices"
    created.append({
        "name": ob.name,
        "osm_id": oid,
        "closed": bool(f["closed"]),
        "role": role,
        "point_count": len(coords),
        "area_m2_projected": f["metrics"].get("area_m2_projected"),
        "length_m_projected": f["metrics"].get("length_m_projected"),
    })

assert all(sig(scene.objects[n]) == v for n, v in protected.items())
scene["boas_authoring_revision"] = "R30B.46"
scene["boas_waterfront_status"] = "osm_piers_visible_reference_candidate"

bpy.ops.wm.save_as_mainfile(filepath=str(out), compress=True)
sha = hashlib.sha256(out.read_bytes()).hexdigest()
report = {
    "schema": "boas/waterfront-piers-r30b46-v1",
    "source_before": src,
    "source_after": {"file": out.relative_to(root).as_posix(), "revision": "R30B.46", "sha256": sha},
    "classification": "KEEP_REAL_REFERENCE",
    "osm_pier_ids": sorted(ids),
    "created": created,
    "deck_z_candidate_m": deck_z,
    "deck_z_land_controls_m": land_controls,
    "water_level_m": water_level,
    "closed_pier_footprints_created": sum(1 for x in created if x["closed"]),
    "linear_piers_as_centerline_only": sum(1 for x in created if not x["closed"]),
    "linear_width_invented": False,
    "ground_changed": False,
    "water_changed": False,
    "quay_changed": False,
    "runtime_exported": False,
    "approved": False,
    "pending": [
        "Largura dos dois píeres lineares continua sem fonte; não converter os eixos em deck final sem evidência/adaptação registrada.",
        "Validar conexão dos píeres com cais/rotas pedonais e cota do deck em revisão visual.",
        "Expandir e estabilizar coastline/cais e encostas antes de promover gameplay/runtime.",
    ],
}
(root / "docs/reports/blender/waterfront_piers_r30b46.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n",
    encoding="utf8",
)
print(json.dumps({"source_after": report["source_after"], "deck_z_candidate_m": deck_z, "created": created}, ensure_ascii=False))
