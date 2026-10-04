"""Validação read-only da B46 reaberta."""
import bpy, json, hashlib, runpy
from pathlib import Path
from mathutils import Vector

root=Path(__file__).resolve().parents[2]; scene=bpy.context.scene
reg=json.loads((root/"world/areas/mvp-centro-lacerda/blender-revisions.json").read_text(encoding="utf8")); src=reg["validation_source"]
assert src["revision"]=="R30B.46"
assert Path(bpy.data.filepath).resolve()==(root/src["file"]).resolve()
assert hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()==src["sha256"]
rep=json.loads((root/"docs/reports/blender/waterfront_piers_r30b46.json").read_text(encoding="utf8"))
ref=json.loads((root/"artifacts/structural-pipeline/mvp-centro-lacerda/structural_reference.json").read_text(encoding="utf8"))
features={int(f["osm_id"]):f for f in ref["features"] if int(f.get("osm_id",-1)) in set(rep["osm_pier_ids"])}
assert len(features)==4

rows=[]
for item in rep["created"]:
    ob=scene.objects[item["name"]]; oid=int(ob["boas_osm_id"]); f=features[oid]
    assert ob["boas_gameplay_approved"] is False
    if f["closed"]:
        coords=[ob.matrix_world@v.co for v in ob.data.vertices]
        expected=[Vector((float(x),float(y))) for x,y in f["blender_xy"][:-1]]
        assert len(coords)==len(expected)
        max_xy=max((p.to_2d()-q).length for p,q in zip(coords,expected))
        zs=[p.z for p in coords]
        assert max_xy<1e-4 and max(zs)-min(zs)<1e-6
        area=0.0
        for i,p in enumerate(coords):
            q=coords[(i+1)%len(coords)]
            area += p.x*q.y-q.x*p.y
        area=abs(area)*.5
        assert area>1.0
        rows.append({"osm_id":oid,"kind":"footprint","max_xy_error_m":max_xy,"blender_area_m2":area,"source_projected_area_m2":f["metrics"]["area_m2_projected"],"z":zs[0]})
    else:
        pts=[ob.matrix_world@Vector(p.co[:3]) for sp in ob.data.splines for p in sp.points]
        expected=[Vector((float(x),float(y))) for x,y in f["blender_xy"]]
        assert len(pts)==len(expected)
        max_xy=max((p.to_2d()-q).length for p,q in zip(pts,expected))
        assert max_xy<1e-4
        assert ob["boas_width_status"]=="unknown_do_not_invent"
        rows.append({"osm_id":oid,"kind":"centerline","max_xy_error_m":max_xy,"z":pts[0].z})

api=runpy.run_path(str(root/"automation/blender/component_fingerprint.py"))
production=json.loads((root/"world/areas/mvp-centro-lacerda/production.json").read_text(encoding="utf8"))
water_contract=json.loads((root/"docs/reports/blender/r30a8/water_runtime_contract.json").read_text(encoding="utf8"))
names=[production["export"]["road_object"],water_contract["surface_object"],next(o.name for o in scene.objects if o.name.startswith("CAIS | conten"))]
before=api["inspect_file"](root/rep["source_before"]["file"],names)
after={n:api["signature"](scene.objects[n]) for n in names}
assert before==after

result={"schema":"boas/waterfront-piers-r30b46-validation-v2","source_reopened":True,"rows":rows,"protected_objects_identical":True,"protected_objects":names,"area_note":"source_projected_area_m2 pertence ao CRS projetado da fonte; não comparar diretamente com área Blender após fit XY","approved":False,"geometry_changed":False}
(root/"docs/reports/blender/waterfront_piers_r30b46_validation.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps(result,ensure_ascii=False))
