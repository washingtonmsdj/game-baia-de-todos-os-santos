"""Refina a costura da superfície integrada B52 em hard-boundary B53."""
import json
from pathlib import Path
import numpy as np

root=Path(__file__).resolve().parents[2]
d=np.load(root/"artifacts/waterfront/coastal_integrated_surface_b52.npz")
gx=d["gx"].copy(); gy=d["gy"].copy(); H=d["H"].copy(); mask=d["mask"].copy()
surface=d["surface"].copy(); under=d["underwater"].copy(); waymap=d["waymap"].copy()
seam=json.loads((root/"artifacts/waterfront/coastal_seam_controls_b52.json").read_text(encoding="utf8"))
ctrl={(float(r["x"]),float(r["y"])):float(r["z"]) for r in seam["rows"]}

boundary_x=-284.0
blend_west_x=-324.0
ib=int(round((boundary_x-gx[0])/2.0))
applied=0
before=[]
for j,y in enumerate(gy):
    if y < -280.0:
        continue
    target=ctrl.get((boundary_x,float(y)))
    if target is None or not np.isfinite(H[j,ib]):
        continue
    delta=target-float(H[j,ib])
    before.append(abs(delta))
    for i,x in enumerate(gx):
        if x < blend_west_x or x > boundary_x or not mask[j,i]:
            continue
        t=(x-blend_west_x)/(boundary_x-blend_west_x)
        t=max(0.0,min(1.0,float(t)))
        w=t*t*(3-2*t)
        H[j,i]+=delta*w
    H[j,ib]=target
    applied+=1

# Onde o terreno oficial existe, a expansão termina na hard-boundary.
for j,y in enumerate(gy):
    if y < -280.0:
        continue
    for i,x in enumerate(gx):
        if x > boundary_x:
            mask[j,i]=False
            H[j,i]=np.nan
            waymap[j,i]=0

# zera classificações de células que ficaram fora.
for j in range(surface.shape[0]):
    for i in range(surface.shape[1]):
        valid=(mask[j,i] and mask[j,i+1] and mask[j+1,i] and mask[j+1,i+1])
        if not valid:
            surface[j,i]=0
            under[j,i]=0

after=[]
for j,y in enumerate(gy):
    target=ctrl.get((boundary_x,float(y)))
    if target is not None and mask[j,ib] and np.isfinite(H[j,ib]):
        after.append(abs(float(H[j,ib])-target))

meta={
 "schema":"boas/coastal-seam-b53-v1",
 "source":"artifacts/waterfront/coastal_integrated_surface_b52.npz",
 "boundary_x":boundary_x,
 "official_ground_y_min":-280.0,
 "blend_west_x":blend_west_x,
 "blend_distance_m":boundary_x-blend_west_x,
 "hard_controls_applied":applied,
 "max_boundary_error_before_m":max(before,default=None),
 "median_boundary_error_before_m":float(np.median(before)) if before else None,
 "max_boundary_error_after_m":max(after,default=None),
 "remaining_mask_points":int(mask.sum()),
 "policy":"existing official terrain owns x>-284 for y>=-280; expansion owns the remainder; hard boundary values come from Blender terrain controls"
}
np.savez_compressed(root/"artifacts/waterfront/coastal_integrated_surface_b53.npz",gx=gx,gy=gy,H=H,mask=mask,surface=surface,underwater=under,waymap=waymap)
(root/"artifacts/waterfront/coastal_integrated_surface_b53.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps(meta,ensure_ascii=False))
