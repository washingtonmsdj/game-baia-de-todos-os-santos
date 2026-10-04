"""B54: reimpõe plataformas viárias após hard-boundary B53, com âncoras fixas na costura."""
import json,math
from pathlib import Path
import numpy as np

root=Path(__file__).resolve().parents[2]
d=np.load(root/"artifacts/waterfront/coastal_integrated_surface_b53.npz")
gx=d["gx"].copy();gy=d["gy"].copy();H=d["H"].copy();mask=d["mask"].copy()
surface=d["surface"].copy();under=d["underwater"].copy();waymap=d["waymap"].copy()
contract=json.loads((root/"world/areas/mvp-centro-lacerda/coastal-gameplay-b51.json").read_text(encoding="utf8"))
seam=json.loads((root/"artifacts/waterfront/coastal_seam_controls_b52.json").read_text(encoding="utf8"))
ctrl={(float(r["x"]),float(r["y"])):float(r["z"]) for r in seam["rows"]}
step=2.0;ny,nx=H.shape;X,Y=np.meshgrid(gx,gy)
boundary=-284.0

def sample_h(x,y):
    u=(x-gx[0])/step;v=(y-gy[0])/step
    if u<0 or v<0 or u>=nx-1 or v>=ny-1:return None
    i=int(math.floor(u));j=int(math.floor(v));a=u-i;b=v-j
    z=[H[j,i],H[j,i+1],H[j+1,i],H[j+1,i+1]]
    if not all(np.isfinite(z)):return None
    return float(z[0]*(1-a)*(1-b)+z[1]*a*(1-b)+z[2]*(1-a)*b+z[3]*a*b)

nodes=[];zbase_list=[];lookup={};edges=[];meta_edges=[];anchors={};skipped_samples=0
def node(key,xy,zval):
    if key not in lookup:
        lookup[key]=len(nodes)
        nodes.append([float(xy[0]),float(xy[1])])
        zbase_list.append(float(zval))
    return lookup[key]

for rec in contract["roads"]:
    pts=np.asarray(rec["blender_xy"],dtype=float);wid=int(rec["osm_way_id"])
    limit=.45 if rec["role"]=="walkable" else .18
    for k,(aa,bb) in enumerate(zip(pts,pts[1:])):
        dxy=bb-aa;L=float(np.linalg.norm(dxy))
        if L<.01:continue
        count=max(1,math.ceil(L/2));ts=[q/count for q in range(count+1)]
        if (aa[0]-boundary)*(bb[0]-boundary)<0:
            t=(boundary-aa[0])/(bb[0]-aa[0]);y=aa[1]+t*(bb[1]-aa[1])
            if y>=-280.0:ts.append(float(t))
        ts=sorted(set(round(t,10) for t in ts))
        prev_idx=None
        for qi,t in enumerate(ts):
            pxy=aa+dxy*t
            if pxy[1]>=-280.0 and pxy[0]>boundary+1e-6:
                prev_idx=None;continue
            if pxy[0]<gx[0]-2 or pxy[0]>gx[-1]+2 or pxy[1]<gy[0]-2 or pxy[1]>gy[-1]+2:
                prev_idx=None;continue
            zh=sample_h(float(pxy[0]),float(pxy[1]))
            if zh is None:
                skipped_samples+=1;prev_idx=None;continue
            key=(round(float(pxy[0]),5),round(float(pxy[1]),5)) if qi in (0,len(ts)-1) or abs(pxy[0]-boundary)<1e-5 else (wid,k,qi)
            idx=node(key,pxy,zh)
            if abs(float(pxy[0])-boundary)<1e-5 and pxy[1]>=-280.0:
                anchors[idx]=float(zh)
            if prev_idx is not None and prev_idx!=idx:
                axy=np.asarray(nodes[prev_idx]);bxy=np.asarray(nodes[idx]);L2=float(np.linalg.norm(bxy-axy))
                if .01<L2<=4.5:
                    edges.append((prev_idx,idx,L2,limit))
                    meta_edges.append((prev_idx,idx,wid,float(rec["gameplay_width_m"]),rec["role"]))
            prev_idx=idx

xy=np.asarray(nodes,dtype=float)
zbase=np.asarray(zbase_list,dtype=float)
assert len(zbase) and np.isfinite(zbase).all()
z=zbase.copy()
for i,v in anchors.items():z[i]=v
anch=set(anchors)

# Projeção iterativa das restrições de declive com anchors imutáveis.
for iteration in range(3000):
    max_ex=0.0
    for a,b,L,lim in edges:
        diff=z[b]-z[a];cap=L*lim
        if diff>cap:
            ex=diff-cap;max_ex=max(max_ex,ex)
            if a in anch and b in anch:continue
            if a in anch:z[b]-=ex
            elif b in anch:z[a]+=ex
            else:z[a]+=ex*.5;z[b]-=ex*.5
        elif diff<-cap:
            ex=-cap-diff;max_ex=max(max_ex,ex)
            if a in anch and b in anch:continue
            if a in anch:z[b]+=ex
            elif b in anch:z[a]-=ex
            else:z[a]-=ex*.5;z[b]+=ex*.5
    for i,v in anchors.items():z[i]=v
    if max_ex<1e-6:break

best=np.full(H.shape,np.inf);profile=H.copy();stype=np.zeros(H.shape,dtype=np.int8);wmap=np.zeros(H.shape,dtype=np.int64)
for ia,ib,wid,width,role in meta_edges:
    p=xy[ia];q=xy[ib];dxy=q-p;L2=float(np.dot(dxy,dxy))
    if L2<1e-9:continue
    outer=4.0 if role=="walkable" else 8.0;pad=width/2+outer+step
    i0=max(0,int(math.floor((min(p[0],q[0])-pad-gx[0])/step)));i1=min(nx,int(math.ceil((max(p[0],q[0])+pad-gx[0])/step))+1)
    j0=max(0,int(math.floor((min(p[1],q[1])-pad-gy[0])/step)));j1=min(ny,int(math.ceil((max(p[1],q[1])+pad-gy[0])/step))+1)
    if i1<=i0 or j1<=j0:continue
    sl=np.s_[j0:j1,i0:i1]
    t=np.clip(((X[sl]-p[0])*dxy[0]+(Y[sl]-p[1])*dxy[1])/L2,0,1)
    cx=p[0]+t*dxy[0];cy=p[1]+t*dxy[1]
    dist=np.hypot(X[sl]-cx,Y[sl]-cy)-width/2
    choose=dist<best[sl]
    best[sl][choose]=dist[choose]
    prof=z[ia]+t*(z[ib]-z[ia])
    profile[sl][choose]=prof[choose]
    stype[sl][choose]=2 if role=="walkable" else 1
    wmap[sl][choose]=wid

outer=np.where(stype==2,4.0,8.0)
blend=np.clip(1-np.maximum(best,0)/np.maximum(outer,1e-6),0,1)
blend=blend*blend*(3-2*blend);blend[~mask]=0
H2=H*(1-blend)+profile*blend

# Hard-boundary final, distribuindo qualquer residual só 12 m para oeste.
ib=int(round((boundary-gx[0])/step));boundary_residuals=[]
for j,y in enumerate(gy):
    target=ctrl.get((boundary,float(y)))
    if target is None or not mask[j,ib]:continue
    delta=target-float(H2[j,ib]);boundary_residuals.append(abs(delta))
    for i,x in enumerate(gx):
        if x<-296 or x>boundary or not mask[j,i]:continue
        t=(x+296)/12.0;t=max(0,min(1,float(t)));w=t*t*(3-2*t)
        H2[j,i]+=delta*w
    H2[j,ib]=target

for j in range(surface.shape[0]):
    for i in range(surface.shape[1]):
        if not (mask[j,i] and mask[j,i+1] and mask[j+1,i] and mask[j+1,i+1]):
            surface[j,i]=0;under[j,i]=0;continue
        typ=max(stype[j,i],stype[j,i+1],stype[j+1,i],stype[j+1,i+1])
        if typ:surface[j,i]=typ
        zc=(H2[j,i]+H2[j,i+1]+H2[j+1,i]+H2[j+1,i+1])/4
        under[j,i]=1 if zc<.30 else 0
waymap=np.where(wmap!=0,wmap,waymap)

grades=[abs((z[b]-z[a])/L) for a,b,L,lim in edges if L>1e-6]
vehicle_grades=[abs((z[b]-z[a])/L) for a,b,L,lim in edges if L>1e-6 and lim<=.181]
meta={
 "schema":"boas/coastal-road-platform-b54-v2",
 "source":"coastal_integrated_surface_b53.npz",
 "graph_nodes":len(nodes),"graph_edges":len(edges),"hard_anchor_nodes":len(anchors),
 "skipped_surface_samples":skipped_samples,"iterations":iteration+1,
 "max_graph_grade":max(grades,default=0.0),
 "max_vehicle_graph_grade":max(vehicle_grades,default=0.0),
 "vehicle_grade_limit":.18,"boundary_x":boundary,
 "max_boundary_residual_before_final_lock_m":max(boundary_residuals,default=0.0),
 "final_boundary_error_m":0.0
}
np.savez_compressed(root/"artifacts/waterfront/coastal_integrated_surface_b54.npz",gx=gx,gy=gy,H=H2,mask=mask,surface=surface,underwater=under,waymap=waymap)
(root/"artifacts/waterfront/coastal_integrated_surface_b54.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps(meta,ensure_ascii=False))
