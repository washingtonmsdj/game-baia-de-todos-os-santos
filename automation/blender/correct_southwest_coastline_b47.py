"""R30B.47: substitui o fechamento diagonal sudoeste da água por coastline OSM dentro da cobertura DEM."""
import bpy, bmesh, json, hashlib, importlib.util, runpy, math
from pathlib import Path
from mathutils import Vector

root=Path(__file__).resolve().parents[2]; scene=bpy.context.scene
reg=json.loads((root/"world/areas/mvp-centro-lacerda/blender-revisions.json").read_text(encoding="utf8")); src=reg["validation_source"]
assert src["revision"]=="R30B.46"
srcfile=root/src["file"]; assert Path(bpy.data.filepath).resolve()==srcfile.resolve()
assert hashlib.sha256(srcfile.read_bytes()).hexdigest()==src["sha256"]
out=root/"blender/salvador_lacerda_r30b47_coastline_sudoeste.blend"; assert not out.exists()

wc=json.loads((root/"docs/reports/blender/r30a8/water_runtime_contract.json").read_text(encoding="utf8"))
production=json.loads((root/"world/areas/mvp-centro-lacerda/production.json").read_text(encoding="utf8"))
water=scene.objects[wc["surface_object"]]; ground=scene.objects[production["export"]["road_object"]]
quay=next(o for o in scene.objects if o.name.startswith("CAIS | conten"))
api=runpy.run_path(str(root/"automation/blender/component_fingerprint.py")); sig=api["signature"]
protected={o.name:sig(o) for o in (ground,quay)}
protected_piers={o.name:sig(o) for o in scene.objects if o.name.startswith("PIER OSM |")}

spec=importlib.util.spec_from_file_location("bsr",root/"tools/world/build_blender_structure_reference.py")
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
fit=json.loads((root/"artifacts/structural-pipeline/mvp-centro-lacerda/georef_fit.json").read_text(encoding="utf8"))["robust_fit"]
osm=json.loads((root/"artifacts/structural-pipeline/mvp-centro-lacerda/osm_structure.json").read_text(encoding="utf8"))
coast=next(f for f in osm["features"] if int(f.get("osm_id",-1))==354138561)
pts=[Vector((*m.transform_point(p,fit),float(wc["water_level_m"]))) for p in coast["epsg3857"]]
# usar somente a sequência comprovadamente dentro do DEM até o último ponto x >= -555
local=pts[:48]
assert local[0].x>-360 and local[0].y>-100
assert local[-1].x>=-555 and pts[48].x<-555
# último ponto da coastline atual da água e vértice externo do fechamento
me=water.data
v_outer=me.vertices[73]; v_shore=me.vertices[74]
outer=water.matrix_world@v_outer.co; shore=water.matrix_world@v_shore.co
assert (outer.to_2d()-Vector((-430,-850))).length<0.01
assert (shore.to_2d()-Vector((-358.7041626,-94.8433228))).length<0.01
# Coast OSM inicia a ~2.56 m do shore atual; incluir todos os pontos e manter curto conector local ao shore.
assert (local[0].to_2d()-shore.to_2d()).length<3.0

bm=bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table()
a=bm.verts[73]; b=bm.verts[74]
edge=next(e for e in a.link_edges if b in e.verts)
# Dividir sequencialmente na orientação outer -> shore; inserir coastline invertida local[-1]...local[0].
inv=water.matrix_world.inverted()
insert=list(reversed(local))
current=a
created=[]
for i,target_world in enumerate(insert):
    # edge que liga current ao b (após cada split)
    e=next(e for e in current.link_edges if b in e.verts)
    _,nv=bmesh.utils.edge_split(e,current,0.5)
    nv.co=inv@target_world
    created.append(nv)
    current=nv
# triangula apenas as faces tocadas pela cadeia
faces=set()
for v in [a,b,*created]: faces.update(v.link_faces)
bmesh.ops.triangulate(bm,faces=list(faces))
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
bm.to_mesh(me); bm.free(); me.update()

# prova: nível da água e sequência XY
assert max(abs((water.matrix_world@v.co).z-float(wc["water_level_m"])) for v in me.vertices)<1e-4
world_created=[water.matrix_world@me.vertices[75+i].co for i in range(len(created))] if len(me.vertices)>=75+len(created) else []
# Não depender da ordem de índice após bmesh: verificar existência espacial dos targets.
allw=[water.matrix_world@v.co for v in me.vertices]
max_target_error=max(min((q.to_2d()-p.to_2d()).length for q in allw) for p in insert)
assert max_target_error<1e-4
assert all(sig(scene.objects[n])==v for n,v in protected.items())
assert all(sig(scene.objects[n])==v for n,v in protected_piers.items())

# referência visual da coastline usada
coll=bpy.data.collections.get("WATERFRONT | COASTLINE OSM | B47")
if coll is None:
    coll=bpy.data.collections.new("WATERFRONT | COASTLINE OSM | B47"); scene.collection.children.link(coll)
curve=bpy.data.curves.new("COASTLINE_OSM_354138561_B47","CURVE"); curve.dimensions="3D"
sp=curve.splines.new("POLY"); sp.points.add(len(local)-1)
for p,q in zip(sp.points,local): p.co=(*q,1.0)
curve.bevel_depth=0.04; curve.bevel_resolution=0
guide=bpy.data.objects.new("COASTLINE OSM | 354138561 | trecho DEM B47",curve); coll.objects.link(guide)
guide["boas_osm_id"]=354138561; guide["boas_source_tag"]="natural=coastline"; guide["boas_runtime_role"]="reference_only"
guide["boas_cutoff_reason"]="DEM west bound; next source point x < -555 Blender"
guide["boas_gameplay_approved"]=False

scene["boas_authoring_revision"]="R30B.47"
scene["boas_waterfront_status"]="southwest_coastline_osm_applied_candidate"
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
sha=hashlib.sha256(out.read_bytes()).hexdigest()
report={
 "schema":"boas/coastline-southwest-r30b47-v1","source_before":src,
 "source_after":{"file":out.relative_to(root).as_posix(),"revision":"R30B.47","sha256":sha},
 "classification":"ERROR","osm_way_id":354138561,"source_tag":"natural=coastline",
 "source_points_used":len(local),"source_point_range":[0,47],"dem_cutoff_blender_x_m":-555.0,
 "first_source_xy":[local[0].x,local[0].y],"last_source_xy":[local[-1].x,local[-1].y],
 "old_artificial_closure":{"outer_xy":[outer.x,outer.y],"shore_xy":[shore.x,shore.y],"length_m":(shore.to_2d()-outer.to_2d()).length},
 "remaining_outer_closure":{"from_xy":[outer.x,outer.y],"to_xy":[local[-1].x,local[-1].y],"classification":"recorte_externo_nao_coastline"},
 "inserted_vertices":len(created),"maximum_target_xy_error_m":max_target_error,
 "water_level_m":float(wc["water_level_m"]),"ground_changed":False,"quay_changed":False,"piers_changed":False,
 "water_volume_changed":False,"runtime_exported":False,"approved":False,
 "pending":["Reabrir e validar topologia/shoreline B47.","Construir terreno/encosta somente no lado terrestre com DEM; não preencher mar como solo.","Revisar ligação do fechamento externo da água fora da costa modelada."]
}
(root/"docs/reports/blender/coastline_southwest_r30b47.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps({"source_after":report["source_after"],"inserted_vertices":len(created),"old_closure_m":report["old_artificial_closure"]["length_m"],"max_target_error_m":max_target_error},ensure_ascii=False))
