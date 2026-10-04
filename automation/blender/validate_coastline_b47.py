"""Validação read-only da B47 reaberta: topologia da água, coastline e invariantes B46->B47."""
import bpy,json,hashlib,math,runpy,importlib.util,numpy as np
from pathlib import Path
from mathutils import Vector

root=Path(__file__).resolve().parents[2]; scene=bpy.context.scene
reg=json.loads((root/"world/areas/mvp-centro-lacerda/blender-revisions.json").read_text(encoding="utf8")); src=reg["validation_source"]
assert src["revision"]=="R30B.47"
assert Path(bpy.data.filepath).resolve()==(root/src["file"]).resolve()
assert hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()==src["sha256"]
rep=json.loads((root/"docs/reports/blender/coastline_southwest_r30b47.json").read_text(encoding="utf8"))
wc=json.loads((root/"docs/reports/blender/r30a8/water_runtime_contract.json").read_text(encoding="utf8"))
production=json.loads((root/"world/areas/mvp-centro-lacerda/production.json").read_text(encoding="utf8"))
water=scene.objects[wc["surface_object"]]; me=water.data
assert len(me.vertices)==123

# geometria finita, nível e triângulos
world=np.array([list(water.matrix_world@v.co) for v in me.vertices],dtype=float)
assert np.isfinite(world).all()
assert float(np.max(np.abs(world[:,2]-float(wc["water_level_m"]))))<1e-4
me.calc_loop_triangles()
tri=np.array([list(t.vertices) for t in me.loop_triangles],dtype=int)
areas=np.linalg.norm(np.cross(world[tri[:,1]]-world[tri[:,0]],world[tri[:,2]]-world[tri[:,0]]),axis=1)*.5
assert int(np.sum(areas<1e-8))==0

# boundary e alinhamento dos 48 pontos OSM inseridos
emap={tuple(sorted(e.vertices)):e.index for e in me.edges}; use=[0]*len(me.edges)
for p in me.polygons:
    for a,b in p.edge_keys: use[emap[tuple(sorted((a,b)))]]+=1
boundary=[e for e,u in zip(me.edges,use) if u==1]
segments=[(water.matrix_world@me.vertices[e.vertices[0]].co,water.matrix_world@me.vertices[e.vertices[1]].co) for e in boundary]
spec=importlib.util.spec_from_file_location("bsr",root/"tools/world/build_blender_structure_reference.py"); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
fit=json.loads((root/"artifacts/structural-pipeline/mvp-centro-lacerda/georef_fit.json").read_text(encoding="utf8"))["robust_fit"]
osm=json.loads((root/"artifacts/structural-pipeline/mvp-centro-lacerda/osm_structure.json").read_text(encoding="utf8"))
coast=next(f for f in osm["features"] if int(f.get("osm_id",-1))==354138561)
targets=[Vector((*m.transform_point(p,fit),float(wc["water_level_m"]))) for p in coast["epsg3857"][:48]]
def dseg(p,a,b):
    d=(b-a).to_2d();L2=d.length_squared
    if L2<1e-12:return (p.to_2d()-a.to_2d()).length
    t=max(0,min(1,(p.to_2d()-a.to_2d()).dot(d)/L2));q=a.to_2d()+d*t
    return (p.to_2d()-q).length
errs=[min(dseg(p,a,b) for a,b in segments) for p in targets]
assert max(errs)<1e-4

# objetos que B47 não pode alterar
api=runpy.run_path(str(root/"automation/blender/component_fingerprint.py"))
names=[production["export"]["road_object"],next(o.name for o in scene.objects if o.name.startswith("CAIS | conten")),
       wc["volume_object"]]+[o.name for o in scene.objects if o.name.startswith("PIER OSM |")]
before=api["inspect_file"](root/rep["source_before"]["file"],names)
after={n:api["signature"](scene.objects[n]) for n in names}
assert before==after

result={"schema":"boas/coastline-southwest-r30b47-validation-v1","source_reopened":True,
        "water_vertices":len(me.vertices),"water_polygons":len(me.polygons),"triangles":len(me.loop_triangles),
        "degenerate_triangles_lt_1e8":int(np.sum(areas<1e-8)),"boundary_edges":len(boundary),
        "coastline_points_checked":len(targets),"max_coastline_boundary_error_m":max(errs),
        "protected_objects_identical":True,"protected_count":len(names),"water_level_m":float(wc["water_level_m"]),
        "approved":False,"geometry_changed":False}
(root/"docs/reports/blender/coastline_southwest_r30b47_validation.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps(result,ensure_ascii=False))
