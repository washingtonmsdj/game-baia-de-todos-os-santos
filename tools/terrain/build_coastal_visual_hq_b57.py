"""Gera terreno HQ B57 com visual e colisão na mesma geometria.
O DEM Aleph fornece micro-relevo; B55 preserva gameplay, vias, costura e fundo submerso.
"""
import json, math
from pathlib import Path
import numpy as np
import rasterio

root=Path(__file__).resolve().parents[2]
b55=np.load(root/"artifacts/waterfront/coastal_integrated_surface_b55.npz")
cgx=np.asarray(b55["gx"],dtype=float)
cgy=np.asarray(b55["gy"],dtype=float)
CH=np.asarray(b55["H"],dtype=float)
CM=np.asarray(b55["mask"],dtype=bool)
contract=json.loads((root/"world/areas/mvp-centro-lacerda/coastal-gameplay-b51.json").read_text(encoding="utf8"))
fit=json.loads((root/"artifacts/structural-pipeline/mvp-centro-lacerda/georef_fit.json").read_text(encoding="utf8"))["robust_fit"]
struct=json.loads((root/"artifacts/structural-pipeline/mvp-centro-lacerda/structural_reference.json").read_text(encoding="utf8"))

step=0.75
gx=np.arange(-560.0,-260.0+1e-6,step)
gy=np.arange(-510.0,10.0+1e-6,step)
X,Y=np.meshgrid(gx,gy)
ny,nx=X.shape

# Mesmo polígono costeiro OSM usado pelas revisões B52-B55.
coast=None
stack=[struct]
while stack:
    q=stack.pop()
    if isinstance(q,dict):
        if q.get("osm_id")==354138561:
            coast=q
            break
        stack.extend(q.values())
    elif isinstance(q,list):
        stack.extend(q)
assert coast is not None
shore=np.asarray(coast["blender_xy"][:48],dtype=float)
poly=np.vstack([shore,[[-260.0,-520.0],[-260.0,20.0]],shore[0]])
mask=np.zeros(X.shape,dtype=bool)
for i in range(len(poly)-1):
    x1,y1=poly[i]
    x2,y2=poly[i+1]
    cond=(y1>Y)!=(y2>Y)
    xcross=(x2-x1)*(Y-y1)/(y2-y1+1e-30)+x1
    mask ^= cond & (X<xcross)

# Blender XY -> EPSG3857.
s=fit["scale_blender_units_per_meter"]
a=math.radians(fit["rotation_epsg3857_to_blender_deg"])
ca=math.cos(a)
sa=math.sin(a)
tx,ty=fit["translation_blender"]

def to_epsg(x,y):
    return (
        (ca*(x-tx)+sa*(y-ty))/s,
        (-sa*(x-tx)+ca*(y-ty))/s,
    )

# Amostragem bilinear vetorizada do GeoTIFF Aleph.
dem_path=Path(r"C:\Users\TONECOS\Documents\github\Tom Oliver\projeto-salvador-elevador-lacerda\data\aleph\aleph-20260924T205631Z-aqqo7pkx\terrain.tif")
with rasterio.open(dem_path) as ds:
    arr=ds.read(1).astype(np.float64)
    nodata=ds.nodata
    inv=~ds.transform

    def sample_dem(x,y):
        ex,ey=to_epsg(x,y)
        col=inv.a*ex+inv.b*ey+inv.c
        row=inv.d*ex+inv.e*ey+inv.f
        i=np.floor(col).astype(np.int64)
        j=np.floor(row).astype(np.int64)
        u=col-i
        v=row-j
        valid=(i>=0)&(j>=0)&(i<arr.shape[1]-1)&(j<arr.shape[0]-1)
        i=np.clip(i,0,arr.shape[1]-2)
        j=np.clip(j,0,arr.shape[0]-2)
        a00=arr[j,i]
        a10=arr[j,i+1]
        a01=arr[j+1,i]
        a11=arr[j+1,i+1]
        z=a00*(1-u)*(1-v)+a10*u*(1-v)+a01*(1-u)*v+a11*u*v
        if nodata is not None:
            valid &= (a00!=nodata)&(a10!=nodata)&(a01!=nodata)&(a11!=nodata)
        valid &= np.isfinite(z)
        return z,valid

    cX,cY=np.meshgrid(cgx,cgy)
    cdem,cvalid=sample_dem(cX,cY)
    hdem,hvalid=sample_dem(X,Y)
    # Mesma proteção adotada na B48 contra outliers da captura.
    cvalid &= (cdem>=-10.0)&(cdem<=100.0)
    hvalid &= (hdem>=-10.0)&(hdem<=100.0)

# Campo de correção gameplay = B55 - DEM, no grid de 2m.
C=CH-cdem
C[~CM | ~cvalid | ~np.isfinite(CH)]=np.nan
fallback=float(np.nanmedian(C))

# Índices para interpolar o grid B55 no grid HQ.
cu=(X-cgx[0])/(cgx[1]-cgx[0])
cv=(Y-cgy[0])/(cgy[1]-cgy[0])
ci=np.floor(cu).astype(int)
cj=np.floor(cv).astype(int)
fu=cu-ci
fv=cv-cj
ci=np.clip(ci,0,len(cgx)-2)
cj=np.clip(cj,0,len(cgy)-2)
weights=[
    (1-fu)*(1-fv),
    fu*(1-fv),
    (1-fu)*fv,
    fu*fv,
]

# Interpola campo de correção ignorando cantos inválidos.
vals=[C[cj,ci],C[cj,ci+1],C[cj+1,ci],C[cj+1,ci+1]]
num=np.zeros(X.shape,dtype=float)
den=np.zeros(X.shape,dtype=float)
for vv,ww in zip(vals,weights):
    ok=np.isfinite(vv)
    num[ok]+=vv[ok]*ww[ok]
    den[ok]+=ww[ok]
corr=np.full(X.shape,fallback,dtype=float)
ok=den>1e-9
corr[ok]=num[ok]/den[ok]

# Interpola a própria B55: é a referência de gameplay/collision.
hvals=[CH[cj,ci],CH[cj,ci+1],CH[cj+1,ci],CH[cj+1,ci+1]]
num.fill(0.0)
den.fill(0.0)
for vv,ww in zip(hvals,weights):
    good=np.isfinite(vv)
    num[good]+=vv[good]*ww[good]
    den[good]+=ww[good]
Hgame=np.full(X.shape,np.nan,dtype=float)
good=den>1e-9
Hgame[good]=num[good]/den[good]

# Base DEM de alta densidade.
H=hdem+corr
H[~hvalid]=Hgame[~hvalid]
H[~mask]=np.nan
assert not np.any(mask & ~np.isfinite(H)), "HQ DEM/correção deixou buracos"

# Peso de trava das vias: núcleo e transição permanecem B55.
road_weight=np.zeros(X.shape,dtype=np.float32)
for rec in contract["roads"]:
    pts=np.asarray(rec["blender_xy"],dtype=float)
    width=float(rec["gameplay_width_m"])
    core=width/2+0.15
    outer=core+(1.25 if rec["role"]=="walkable" else 2.0)
    for p,q in zip(pts,pts[1:]):
        d=q-p
        L2=float(np.dot(d,d))
        if L2<1e-9:
            continue
        pad=outer+step
        i0=max(0,int(math.floor((min(p[0],q[0])-pad-gx[0])/step)))
        i1=min(nx,int(math.ceil((max(p[0],q[0])+pad-gx[0])/step))+1)
        j0=max(0,int(math.floor((min(p[1],q[1])-pad-gy[0])/step)))
        j1=min(ny,int(math.ceil((max(p[1],q[1])+pad-gy[0])/step))+1)
        if i1<=i0 or j1<=j0:
            continue
        sl=np.s_[j0:j1,i0:i1]
        t=np.clip(((X[sl]-p[0])*d[0]+(Y[sl]-p[1])*d[1])/L2,0,1)
        cx=p[0]+t*d[0]
        cy=p[1]+t*d[1]
        dist=np.hypot(X[sl]-cx,Y[sl]-cy)
        w=np.clip((outer-dist)/max(outer-core,1e-6),0,1)
        w=w*w*(3-2*w)
        road_weight[sl]=np.maximum(road_weight[sl],w.astype(np.float32))

# Hard-boundary do terreno antigo: também fica B55/official.
seam=np.zeros(X.shape,dtype=np.float32)
region=(Y>=-280)&(X>=-300)
w=np.clip((X+300)/16.0,0,1)
w=w*w*(3-2*w)
seam[region]=w[region].astype(np.float32)
lock=np.maximum(road_weight,seam)

# DEM só adiciona micro-relevo jogável controlado, nunca uma segunda superfície conflitante.
valid=mask&np.isfinite(Hgame)
delta=np.zeros(X.shape,dtype=np.float64)
delta[valid]=H[valid]-Hgame[valid]
delta=np.clip(delta,-0.25,0.25)

# Suaviza ruído sem apagar a informação do DEM.
P=np.pad(delta,1,mode="edge")
avg=sum(P[dy:dy+ny,dx:dx+nx] for dy in range(3) for dx in range(3))/9.0
delta=0.65*delta+0.35*avg

# Via/costura não recebem micro-relevo. Fundo submerso continua B55 até batimetria confiável.
delta*=np.clip(1.0-lock,0,1)
underwater=valid&(Hgame<0.30)
delta[underwater]=0.0
H[valid]=Hgame[valid]+delta[valid]
H[~mask]=np.nan
max_delta=float(np.max(np.abs(delta[valid]))) if np.any(valid) else 0.0

meta={
    "schema":"boas/coastal-visual-hq-b57-v2",
    "step_m":step,
    "shape":[int(ny),int(nx)],
    "bbox":[float(gx[0]),float(gx[-1]),float(gy[0]),float(gy[-1])],
    "mask_points":int(mask.sum()),
    "source_gameplay":"coastal_integrated_surface_b55.npz",
    "source_dem":str(dem_path),
    "correction_median_m":fallback,
    "road_locked_points":int(np.sum(road_weight>.99)),
    "seam_locked_points":int(np.sum(seam>.99)),
    "underwater_points_locked_to_b55":int(np.sum(underwater)),
    "z_min_m":float(np.nanmin(H)),
    "z_max_m":float(np.nanmax(H)),
    "max_abs_delta_from_b55_m":max_delta,
    "policy":"B57 visual and collision must use this same HQ surface; B55 provides gameplay constraints.",
}
np.savez_compressed(
    root/"artifacts/waterfront/coastal_visual_hq_b57.npz",
    gx=gx,gy=gy,H=H,mask=mask,underwater=underwater,
    road_weight=road_weight,Hgame=Hgame,
)
(root/"artifacts/waterfront/coastal_visual_hq_b57.json").write_text(
    json.dumps(meta,ensure_ascii=False,indent=2)+"\n",encoding="utf8"
)
print(json.dumps(meta,ensure_ascii=False))
