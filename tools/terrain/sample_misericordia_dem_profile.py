"""Amostra densamente o DEM-fonte ao longo da Rua da Misericórdia, sem alterar Blender."""
import argparse,json,math,hashlib
from pathlib import Path
from PIL import Image

parser=argparse.ArgumentParser()
parser.add_argument("--capture",type=Path,required=True)
parser.add_argument("--spacing-m",type=float,default=0.5)
args=parser.parse_args()
root=Path(__file__).resolve().parents[2]
graph=json.loads((root/"prototypes/threejs-water-lab/public/data/road_graph.json").read_text(encoding="utf8"))
nodes={str(n["id"]):n for n in graph["nodes"]}
way=next(w for w in graph["ways"] if int(w["osm_way_id"])==803899198)
im=Image.open(args.capture/"terrain.tif")
scale=im.tag_v2[33550]; tie=im.tag_v2[33922]; keys=im.tag_v2[34735]
entries={keys[4+i*4]:list(keys[5+i*4:8+i*4]) for i in range(keys[3])}
if entries.get(3072)!=[0,1,3857]: raise RuntimeError("DEM precisa de EPSG:3857")
kind=entries.get(1025)
if kind not in ([0,1,1],[0,1,2]): raise RuntimeError("Convenção raster não suportada")
shift=.5 if kind==[0,1,2] else 0
nodata=float(im.tag_v2[42113]) if 42113 in im.tag_v2 else None
if im.mode!="F": raise RuntimeError("DEM float esperado")
pix=im.load()

def sample(x,y):
    col=(x-tie[3])/scale[0]+tie[0]+shift
    row=(tie[4]-y)/scale[1]+tie[1]+shift
    # bilinear in raster index space; reject outside/nodata.
    c0=math.floor(col); r0=math.floor(row); tx=col-c0; ty=row-r0
    vals=[]
    for rr in (r0,r0+1):
        rowv=[]
        for cc in (c0,c0+1):
            if not (0<=cc<im.width and 0<=rr<im.height): return None
            z=float(pix[cc,rr])
            if not math.isfinite(z) or (nodata is not None and z==nodata): return None
            rowv.append(z)
        vals.append(rowv)
    z0=vals[0][0]*(1-tx)+vals[0][1]*tx
    z1=vals[1][0]*(1-tx)+vals[1][1]*tx
    return z0*(1-ty)+z1*ty

rows=[]; cumulative=0.0
refs=[str(x) for x in way["node_refs"]]
for seg in range(len(refs)-1):
    a=nodes[refs[seg]]; b=nodes[refs[seg+1]]
    ax,ay=map(float,a["epsg3857"]); bx,by=map(float,b["epsg3857"])
    abx,aby=bx-ax,by-ay; length=math.hypot(abx,aby); steps=max(1,math.ceil(length/args.spacing_m))
    for i in range(steps+1):
        if seg and i==0: continue
        t=i/steps; x=ax+abx*t; y=ay+aby*t
        bx0,by0=map(float,a["blender_xy"]); bx1,by1=map(float,b["blender_xy"])
        blender=[bx0+(bx1-bx0)*t,by0+(by1-by0)*t]
        dist=cumulative+length*t
        rows.append({"segment":seg,"fraction":t,"distance_m":dist,"epsg3857":[x,y],"blender_xy":blender,"dem_m":sample(x,y)})
    cumulative+=length
valid=[r for r in rows if r["dem_m"] is not None]
grades=[]
for a,b in zip(valid,valid[1:]):
    dd=b["distance_m"]-a["distance_m"]
    if dd>0: grades.append((b["dem_m"]-a["dem_m"])/dd)
report={
 "schema":"boas/misericordia-dem-profile-v1",
 "capture_id":args.capture.name,
 "dem_sha256":hashlib.file_digest((args.capture/"terrain.tif").open("rb"),"sha256").hexdigest(),
 "osm_way_id":803899198,"node_refs":refs,"spacing_requested_m":args.spacing_m,
 "sampling_method":"bilinear GeoTIFF EPSG:3857; source shape only, absolute vertical fit not approved",
 "rows":rows,
 "summary":{"samples":len(rows),"valid":len(valid),"distance_m":cumulative,
            "z_min_m":min(r["dem_m"] for r in valid),"z_max_m":max(r["dem_m"] for r in valid),
            "max_abs_local_grade":max(abs(x) for x in grades) if grades else None},
 "scene_changed":False,"approved_as_absolute_elevation":False
}
out=root/"artifacts/roads/rondesp/misericordia_dem_profile.json"; out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps(report["summary"],ensure_ascii=False))
