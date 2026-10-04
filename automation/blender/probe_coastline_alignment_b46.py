"""Compara a borda atual da água B46 com a coastline OSM transformada pelo fit registrado."""
import bpy, json, math, importlib.util
from pathlib import Path
from mathutils import Vector

root=Path(__file__).resolve().parents[2]; scene=bpy.context.scene
reg=json.loads((root/"world/areas/mvp-centro-lacerda/blender-revisions.json").read_text(encoding="utf8")); src=reg["validation_source"]
assert src["revision"]=="R30B.46"
assert Path(bpy.data.filepath).resolve()==(root/src["file"]).resolve()

spec=importlib.util.spec_from_file_location("bsr",root/"tools/world/build_blender_structure_reference.py")
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
fit=json.loads((root/"artifacts/structural-pipeline/mvp-centro-lacerda/georef_fit.json").read_text(encoding="utf8"))["robust_fit"]
osm=json.loads((root/"artifacts/structural-pipeline/mvp-centro-lacerda/osm_structure.json").read_text(encoding="utf8"))
water_contract=json.loads((root/"docs/reports/blender/r30a8/water_runtime_contract.json").read_text(encoding="utf8"))
water=scene.objects[water_contract["surface_object"]]
me=water.data

# borda topológica do mesh da água
edge_use=[0]*len(me.edges)
for poly in me.polygons:
    for key in poly.edge_keys:
        # busca index via mapa para evitar depender de ordenação edge_keys
        pass
emap={tuple(sorted(e.vertices)):e.index for e in me.edges}
for poly in me.polygons:
    for a,b in poly.edge_keys:
        idx=emap.get(tuple(sorted((a,b))))
        if idx is not None: edge_use[idx]+=1
boundary_edges=[e for e,u in zip(me.edges,edge_use) if u==1]
boundary_segments=[(water.matrix_world@me.vertices[e.vertices[0]].co,water.matrix_world@me.vertices[e.vertices[1]].co) for e in boundary_edges]

def point_segment_distance(p,a,b):
    d=(b-a).to_2d(); L2=d.length_squared
    if L2<1e-12:return (p.to_2d()-a.to_2d()).length
    t=max(0.0,min(1.0,(p.to_2d()-a.to_2d()).dot(d)/L2))
    q=a.to_2d()+d*t
    return (p.to_2d()-q).length

ids={354138561,609043796,609043797}
rows=[]
for f in osm.get("features",[]):
    oid=int(f.get("osm_id",-1))
    if oid not in ids: continue
    pts=[Vector((*m.transform_point(p,fit),0.0)) for p in f.get("epsg3857",[])]
    # recorta pontos para entorno suportado do DEM/MVP
    local=[p for p in pts if -555<=p.x<=80 and -180<=p.y<=615]
    if not local: continue
    # amostra no máximo 200 pontos para custo previsível
    step=max(1,len(local)//200)
    sampled=local[::step]
    ds=[min(point_segment_distance(p,a,b) for a,b in boundary_segments) for p in sampled]
    rows.append({"osm_id":oid,"source_points":len(pts),"local_points":len(local),"sampled":len(sampled),
                 "distance_to_water_boundary_m":{"min":min(ds),"median":sorted(ds)[len(ds)//2],"max":max(ds)},
                 "local_bounds":[min(p.x for p in local),max(p.x for p in local),min(p.y for p in local),max(p.y for p in local)]})
report={"schema":"boas/coastline-alignment-b46-v1","source":src,"water_object":water.name,
        "water_vertices":len(me.vertices),"water_polygons":len(me.polygons),"water_boundary_edges":len(boundary_edges),
        "coastlines":rows,"geometry_changed":False}
out=root/"artifacts/waterfront/coastline_alignment_b46.json";out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps(report,ensure_ascii=False))
