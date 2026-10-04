"""Constrói contrato auditável de gameplay para a expansão costeira B51."""
import json
from pathlib import Path

root=Path(__file__).resolve().parents[2]
prod=json.loads((root/"world/areas/mvp-centro-lacerda/production.json").read_text(encoding="utf8"))
struct=json.loads((root/"artifacts/structural-pipeline/mvp-centro-lacerda/structural_reference.json").read_text(encoding="utf8"))
widths=prod["runtime"]["road_widths_gameplay_m"]
bbox={"min_x":-560.0,"max_x":-270.0,"min_y":-510.0,"max_y":10.0}

ways=[]
def walk(x):
    if isinstance(x,dict):
        tags=x.get("tags")
        if isinstance(tags,dict) and tags.get("highway") and x.get("blender_xy"):
            ways.append(x)
        for v in x.values(): walk(v)
    elif isinstance(x,list):
        for v in x: walk(v)
walk(struct)

rows=[]
for w in ways:
    pts=w["blender_xy"]
    if not any(bbox["min_x"]<=p[0]<=bbox["max_x"] and bbox["min_y"]<=p[1]<=bbox["max_y"] for p in pts):
        continue
    tags=w["tags"]; kind=tags["highway"]
    if kind=="footway":
        gp_width=2.2
        basis="aleph_historical_gameplay_footway_2.2m"
    else:
        gp_width=float(widths.get(kind,widths["default"]))
        basis=f"production.runtime.road_widths_gameplay_m.{kind if kind in widths else 'default'}"
    rows.append({
        "osm_way_id":int(w["osm_id"]),
        "name":tags.get("name") or "",
        "highway":kind,
        "source_width_m":tags.get("width"),
        "lanes":tags.get("lanes"),
        "oneway":tags.get("oneway"),
        "access":tags.get("access"),
        "surface":tags.get("surface"),
        "blender_xy":[[float(a),float(b)] for a,b in pts],
        "gameplay_width_m":gp_width,
        "gameplay_width_basis":basis,
        "gameplay_width_status":"ADAPT_GAMEPLAY_NOT_SURVEYED" if not tags.get("width") else "SOURCE_TAG_PRESENT_REVIEW_REQUIRED",
        "role":"walkable" if kind=="footway" else "road_driveable",
    })
rows.sort(key=lambda r:r["osm_way_id"])
out={
    "schema":"boas/coastal-gameplay-contract-b51-v1",
    "area_id":"mvp-centro-lacerda",
    "bbox_blender":bbox,
    "source":{
        "aleph_capture":"data/aleph/aleph-20260924T205631Z-aqqo7pkx",
        "osm_source":"Aleph map.osm -> structural_reference.json",
        "terrain_source":"Aleph terrain.tif/terrain_samples -> B48/B49 relative DEM expansion",
        "georef_fit":"artifacts/structural-pipeline/mvp-centro-lacerda/georef_fit.json",
    },
    "terrain":{
        "visual_objects":[
            "EXPANSAO B49 | terra emersa costeira | candidata",
            "EXPANSAO B49 | faixa de transicao costeira | candidata",
            "EXPANSAO B49 | fundo submerso DEM relativo | candidato"
        ],
        "gameplay_required":True,
        "collision_required":True,
        "underwater_collision_required":True,
        "runtime_approved":False,
    },
    "roads":rows,
    "policy":{
        "all_generated_terrain_is_gameplay_surface":True,
        "render_and_collision_share_same_elevation_source":True,
        "road_centerlines_are_osm_authoritative":True,
        "gameplay_widths_do_not_claim_surveyed_real_width":True,
        "do_not_resize_existing_source_geometry":True,
        "restricted_service_roads_remain_restricted":True,
    }
}
p=root/"world/areas/mvp-centro-lacerda/coastal-gameplay-b51.json"
p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps({"roads":len(rows),"ids":[r["osm_way_id"] for r in rows],"roles":{x:sum(r["role"]==x for r in rows) for x in {"road_driveable","walkable"}},"output":str(p)},ensure_ascii=False))
