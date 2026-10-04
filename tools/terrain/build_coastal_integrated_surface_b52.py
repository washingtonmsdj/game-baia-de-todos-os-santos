"""Constrói superfície costeira integrada B52: DEM relativo + costura + vias de gameplay."""
import json,math,heapq
from pathlib import Path
import numpy as np
import rasterio

root=Path(__file__).resolve().parents[2]
contract=json.loads((root/"world/areas/mvp-centro-lacerda/coastal-gameplay-b51.json").read_text(encoding="utf8"))
fit=json.loads((root/"artifacts/structural-pipeline/mvp-centro-lacerda/georef_fit.json").read_text(encoding="utf8"))["robust_fit"]
b48=json.loads((root/"docs/reports/blender/coastal_terrain_r30b48.json").read_text(encoding="utf8"))
seam=json.loads((root/"artifacts/waterfront/coastal_seam_controls_b52.json").read_text(encoding="utf8"))
struct=json.loads((root/"artifacts/structural-pipeline/mvp-centro-lacerda/structural_reference.json").read_text(encoding="utf8"))

step=2.0
gx=np.arange(-560.0,-260.0+0.1,step); gy=np.arange(-510.0,10.0+0.1,step)
X,Y=np.meshgrid(gx,gy); ny,nx=X.shape
# costa B47: primeiros 48 pontos reais + fechamento terrestre leste.
coast=None
stack=[struct]
while stack:
    q=stack.pop()
    if isinstance(q,dict):
        if q.get("osm_id")==354138561: coast=q; break
        stack.extend(q.values())
    elif isinstance(q,list): stack.extend(q)
assert coast
shore=np.asarray(coast["blender_xy"][:48],dtype=float)
poly=np.vstack([shore,[[-260.0,-520.0],[-260.0,20.0]],shore[0]])
# ray casting vetorizado
mask=np.zeros(X.shape,dtype=bool)
for i in range(len(poly)-1):
    x1,y1=poly[i];x2,y2=poly[i+1]
    cond=(y1>Y)!=(y2>Y)
    xcross=(x2-x1)*(Y-y1)/(y2-y1+1e-30)+x1
    mask ^= cond & (X<xcross)

# Blender XY -> EPSG3857.
s=fit["scale_blender_units_per_meter"]; a=math.radians(fit["rotation_epsg3857_to_blender_deg"])
c=math.cos(a); sn=math.sin(a); tx,ty=fit["translation_blender"]
ex=(c*(X-tx)+sn*(Y-ty))/s
ey=(-sn*(X-tx)+c*(Y-ty))/s
dem=Path(r"C:\Users\TONECOS\Documents\github\Tom Oliver\projeto-salvador-elevador-lacerda\data\aleph\aleph-20260924T205631Z-aqqo7pkx\terrain.tif")
coords=list(zip(ex.ravel(),ey.ravel()))
with rasterio.open(dem) as ds:
    vals=np.fromiter((float(v[0]) for v in ds.sample(coords)),dtype=float,count=X.size).reshape(X.shape)
H=vals+float(b48["local_vertical_offset_m"])
H[(vals<-10)|(vals>100)|(~np.isfinite(vals))]=np.nan
H[~mask]=np.nan
# Preenche somente buracos internos isolados (o DEM tinha 1 outlier extremo).
for _ in range(6):
    bad=mask & ~np.isfinite(H)
    if not bad.any():break
    P=np.pad(H,1,constant_values=np.nan)
    neigh=np.stack([P[1:-1,:-2],P[1:-1,2:],P[:-2,1:-1],P[2:,1:-1]])
    with np.errstate(invalid="ignore"):
        avg=np.nanmean(neigh,axis=0)
    fill=bad & np.isfinite(avg); H[fill]=avg[fill]
assert not np.any(mask & ~np.isfinite(H))

# Costura com o terreno oficial: controles medidos no próprio Blender.
ctrl={(float(r["x"]),float(r["y"])):float(r["z"]) for r in seam["rows"]}
for j,y in enumerate(gy):
    for i,x in enumerate(gx):
        z=ctrl.get((float(x),float(y)))
        if z is None or not mask[j,i]:continue
        w=np.clip((x+300.0)/20.0,0,1); w=w*w*(3-2*w)
        H[j,i]=H[j,i]*(1-w)+z*w

# Helpers de amostragem na grade.
def sample_h(x,y):
    u=(x-gx[0])/step; v=(y-gy[0])/step
    if u<0 or v<0 or u>=nx-1 or v>=ny-1:return None
    i=int(math.floor(u));j=int(math.floor(v));aa=u-i;bb=v-j
    z=[H[j,i],H[j,i+1],H[j+1,i],H[j+1,i+1]]
    if not all(np.isfinite(z)):return None
    return float(z[0]*(1-aa)*(1-bb)+z[1]*aa*(1-bb)+z[2]*(1-aa)*bb+z[3]*aa*bb)

# Grafo amostrado ~2m. Nós originais com mesmo XY são compartilhados.
nodes=[]; lookup={}; edges=[]; segmeta=[]
def get_node(key,xy):
    if key not in lookup:
        lookup[key]=len(nodes); nodes.append([float(xy[0]),float(xy[1])])
    return lookup[key]
selected={int(r["osm_way_id"]):r for r in contract["roads"]}
for rec in contract["roads"]:
    pts=np.asarray(rec["blender_xy"],dtype=float); wid=int(rec["osm_way_id"])
    limit=.45 if rec["role"]=="walkable" else .18
    for k,(aa,bb) in enumerate(zip(pts,pts[1:])):
        d=bb-aa; L=float(np.linalg.norm(d))
        if L<.01:continue
        # ignora segmentos totalmente fora da janela ampliada
        if max(aa[0],bb[0])<-565 or min(aa[0],bb[0])>-240 or max(aa[1],bb[1])<-515 or min(aa[1],bb[1])>30:continue
        count=max(1,math.ceil(L/2.0)); ids=[]
        for q in range(count+1):
            xy=aa+d*(q/count)
            key=(round(float(xy[0]),4),round(float(xy[1]),4)) if q in (0,count) else (wid,k,q)
            ids.append(get_node(key,xy))
        for ia,ib in zip(ids,ids[1:]):
            l=float(np.linalg.norm(np.asarray(nodes[ib])-np.asarray(nodes[ia])))
            edges.append((ia,ib,l,limit))
            segmeta.append((ia,ib,wid,float(rec["gameplay_width_m"]),rec["role"]))

xy=np.asarray(nodes,dtype=float)
z=np.array([sample_h(x,y) if sample_h(x,y) is not None else 0.0 for x,y in xy],dtype=float)
# nós fora da máscara: usa DEM relativo direto.
missing=np.where(z==0.0)[0]
if len(missing):
    exn=(c*(xy[missing,0]-tx)+sn*(xy[missing,1]-ty))/s
    eyn=(-sn*(xy[missing,0]-tx)+c*(xy[missing,1]-ty))/s
    with rasterio.open(dem) as ds:
        vz=np.fromiter((float(v[0]) for v in ds.sample(list(zip(exn,eyn)))),dtype=float,count=len(missing))
    z[missing]=vz+float(b48["local_vertical_offset_m"])

adj=[[] for _ in range(len(z))]
for ia,ib,L,lim in edges:
    cost=L*lim; adj[ia].append((ib,cost));adj[ib].append((ia,cost))
def envelope(values):
    out=values.copy(); hp=[(float(v),i) for i,v in enumerate(out)];heapq.heapify(hp)
    while hp:
        h,i=heapq.heappop(hp)
        if h>out[i]+1e-10:continue
        for j,cost in adj[i]:
            cand=h+cost
            if cand<out[j]-1e-10:
                out[j]=cand;heapq.heappush(hp,(cand,j))
    return out
z_relaxed=(envelope(z)-envelope(-z))*.5

# Estampa plataformas: núcleo plano transversal + transição suave.
best=np.full(H.shape,np.inf); profile=H.copy(); stype=np.zeros(H.shape,dtype=np.int8); waymap=np.zeros(H.shape,dtype=np.int64)
for ia,ib,wid,width,role in segmeta:
    p=xy[ia];q=xy[ib]; d=q-p; L2=float(np.dot(d,d))
    if L2<1e-9:continue
    outer=4.0 if role=="walkable" else 8.0; pad=width/2+outer+step
    i0=max(0,int(math.floor((min(p[0],q[0])-pad-gx[0])/step)));i1=min(nx,int(math.ceil((max(p[0],q[0])+pad-gx[0])/step))+1)
    j0=max(0,int(math.floor((min(p[1],q[1])-pad-gy[0])/step)));j1=min(ny,int(math.ceil((max(p[1],q[1])+pad-gy[0])/step))+1)
    if i1<=i0 or j1<=j0:continue
    sl=np.s_[j0:j1,i0:i1]
    t=np.clip(((X[sl]-p[0])*d[0]+(Y[sl]-p[1])*d[1])/L2,0,1)
    cx=p[0]+t*d[0];cy=p[1]+t*d[1]
    dist=np.hypot(X[sl]-cx,Y[sl]-cy)-width/2
    choose=dist<best[sl]
    best[sl][choose]=dist[choose]
    prof=z_relaxed[ia]+t*(z_relaxed[ib]-z_relaxed[ia])
    profile[sl][choose]=prof[choose]
    stype[sl][choose]=2 if role=="walkable" else 1
    waymap[sl][choose]=wid
outer=np.where(stype==2,4.0,8.0)
blend=np.clip(1-np.maximum(best,0)/np.maximum(outer,1e-6),0,1)
blend=blend*blend*(3-2*blend); blend[~mask]=0
H2=H*(1-blend)+profile*blend

# Face-role por célula: centro da célula usa menor distância dos 4 cantos.
surface=np.zeros((ny-1,nx-1),dtype=np.int8)
under=np.zeros_like(surface,dtype=np.int8)
for j in range(ny-1):
    for i in range(nx-1):
        if not (mask[j,i] and mask[j,i+1] and mask[j+1,i] and mask[j+1,i+1]):continue
        types=[stype[j,i],stype[j,i+1],stype[j+1,i],stype[j+1,i+1]]
        surface[j,i]=max(types)
        zc=(H2[j,i]+H2[j,i+1]+H2[j+1,i]+H2[j+1,i+1])/4
        under[j,i]=1 if zc<0.30 else 0

# Métricas do grafo relaxado.
edge_grades=[abs((z_relaxed[b]-z_relaxed[a])/L) for a,b,L,lim in edges if L>1e-6]
meta={
 "schema":"boas/coastal-integrated-surface-b52-v1","step_m":step,
 "shape":[int(ny),int(nx)],"bbox":[float(gx[0]),float(gx[-1]),float(gy[0]),float(gy[-1])],
 "mask_points":int(mask.sum()),"road_graph_nodes":len(nodes),"road_graph_edges":len(edges),
 "max_relaxed_edge_grade":float(max(edge_grades,default=0)),
 "vehicle_grade_limit":0.18,"pedestrian_grade_limit":0.45,
 "seam_controls":len(ctrl),"source_revision":"R30B.51",
 "source_method":"Aleph continuous-surface method adapted: shared elevation source, graph grade envelope, flat road core, smooth terrain blend",
 "absolute_dem_vertical_approved":False
}
np.savez_compressed(root/"artifacts/waterfront/coastal_integrated_surface_b52.npz",gx=gx,gy=gy,H=H2,mask=mask,surface=surface,underwater=under,waymap=waymap)
(root/"artifacts/waterfront/coastal_integrated_surface_b52.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps(meta,ensure_ascii=False))
