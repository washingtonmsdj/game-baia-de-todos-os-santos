"""Gera grade DEM local para expansão costeira B48 sem autorizar Z absoluto."""
import json, math
from pathlib import Path
import numpy as np
import rasterio

root=Path(__file__).resolve().parents[2]
fit=json.loads((root/"artifacts/structural-pipeline/mvp-centro-lacerda/georef_fit.json").read_text(encoding="utf8"))["robust_fit"]
s=fit["scale_blender_units_per_meter"]
ang=math.radians(fit["rotation_epsg3857_to_blender_deg"])
tx,ty=fit["translation_blender"]
c=math.cos(ang); sn=math.sin(ang)
def inv(xb,yb):
    return ((c*(xb-tx)+sn*(yb-ty))/s,(-sn*(xb-tx)+c*(yb-ty))/s)

struct=json.loads((root/"artifacts/structural-pipeline/mvp-centro-lacerda/structural_reference.json").read_text(encoding="utf8"))
def find_coast(x):
    if isinstance(x,dict):
        if x.get("osm_id")==354138561:return x
        for v in x.values():
            r=find_coast(v)
            if r:return r
    elif isinstance(x,list):
        for v in x:
            r=find_coast(v)
            if r:return r
    return None
coast=find_coast(struct); assert coast
shore=[list(map(float,p)) for p in coast["blender_xy"][:48]]
poly=shore+[[-260.0,-520.0],[-260.0,20.0],shore[0]]
def inside(px,py):
    hit=False
    for i in range(len(poly)-1):
        x1,y1=poly[i];x2,y2=poly[i+1]
        if ((y1>py)!=(y2>py)) and px < (x2-x1)*(py-y1)/(y2-y1+1e-20)+x1:
            hit=not hit
    return hit

dem=Path(r"C:\Users\TONECOS\Documents\github\Tom Oliver\projeto-salvador-elevador-lacerda\data\aleph\aleph-20260924T205631Z-aqqo7pkx\terrain.tif")
spacing=10.0; rows=[]
with rasterio.open(dem) as ds:
    nodata=ds.nodata
    for iy in range(int(round((10-(-510))/spacing))+1):
        y=-510+iy*spacing
        for ix in range(int(round((-270-(-560))/spacing))+1):
            x=-560+ix*spacing
            if not inside(x,y):continue
            ex,ey=inv(x,y)
            val=float(next(ds.sample([(ex,ey)]))[0])
            if not np.isfinite(val):continue
            if nodata is not None and val==nodata:continue
            rows.append({"ix":ix,"iy":iy,"xy":[x,y],"dem_z":val})
out={
 "schema":"boas/coastal-dem-grid-b48-v1","spacing_m":spacing,
 "shoreline_osm_way_id":354138561,"shoreline_points":shore,
 "land_closure_x":-260.0,"grid_points":rows,
 "dem_sha256":"674fe65e08c761f879f1fa02a5560a62c9e836c09e1dfacb2aa805e9def15ca7",
 "horizontal_fit":{"scale_blender_units_per_meter":s,"rotation_epsg3857_to_blender_deg":fit["rotation_epsg3857_to_blender_deg"],"translation_blender":[tx,ty]},
 "absolute_vertical_authorized":False,
 "notes":["DEM usado somente como forma relativa candidata; Z absoluto continua não aprovado.","Polígono terrestre local fecha pelo lado leste; mar não deve receber terreno."]
}
p=root/"artifacts/waterfront/coastal_dem_grid_b48.json"
p.parent.mkdir(parents=True,exist_ok=True)
p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps({"points":len(rows),"dem_min":min(r["dem_z"] for r in rows),"dem_max":max(r["dem_z"] for r in rows),"output":str(p)},ensure_ascii=False))
