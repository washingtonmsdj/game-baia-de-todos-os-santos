"""B55: corrige localmente o crossfall residual da Rua Manoel VitÃ³rino, preservando a hard-boundary."""
import json,math
from pathlib import Path
import numpy as np

root=Path(__file__).resolve().parents[2]
d=np.load(root/"artifacts/waterfront/coastal_integrated_surface_b54.npz")
gx=d["gx"].copy();gy=d["gy"].copy();H=d["H"].copy();mask=d["mask"].copy()
surface=d["surface"].copy();under=d["underwater"].copy();waymap=d["waymap"].copy()
contract=json.loads((root/"world/areas/mvp-centro-lacerda/coastal-gameplay-b51.json").read_text(encoding="utf8"))
rec=next(r for r in contract["roads"] if r["osm_way_id"]==456471269)
a=np.asarray(rec["blender_xy"][0],dtype=float);b=np.asarray(rec["blender_xy"][1],dtype=float)
v=b-a;L=float(np.linalg.norm(v));tangent=v/L
normal=np.asarray([-tangent[1],tangent[0]])
half=float(rec["gameplay_width_m"])/2
step=2.0

def smooth01(x):
    x=max(0.0,min(1.0,float(x)))
    return x*x*(3-2*x)

def sample(arr,x,y):
    u=(x-gx[0])/step;vv=(y-gy[0])/step
    if u<0 or vv<0 or u>=len(gx)-1 or vv>=len(gy)-1:return None
    i=int(math.floor(u));j=int(math.floor(vv));aa=u-i;bb=vv-j
    z=[arr[j,i],arr[j,i+1],arr[j+1,i],arr[j+1,i+1]]
    if not all(np.isfinite(z)):return None
    return float(z[0]*(1-aa)*(1-bb)+z[1]*aa*(1-bb)+z[2]*(1-aa)*bb+z[3]*aa*bb)

# Perfil do eixo B54, preservado longitudinalmente.
samples_s=np.linspace(4.0,13.8,99)
center_z=np.array([sample(H,*(a+tangent*s)) for s in samples_s],dtype=float)
assert np.isfinite(center_z).all()
# suavizaÃ§Ã£o mÃ­nima do eixo para nÃ£o importar microtriangulaÃ§Ã£o para a seÃ§Ã£o transversal.
kernel=np.array([1,2,3,2,1],dtype=float);kernel/=kernel.sum()
pad=np.pad(center_z,(2,2),mode="edge");center_smooth=np.convolve(pad,kernel,mode="valid")

def center_height(s):
    return float(np.interp(s,samples_s,center_smooth))

H2=H.copy(); changed=0; max_delta=0.0
X,Y=np.meshgrid(gx,gy)
for j in range(len(gy)):
    for i in range(len(gx)):
        if not mask[j,i] or not np.isfinite(H[j,i]):
            continue
        p=np.asarray([gx[i],gy[j]],dtype=float)
        rel=p-a
        s=float(np.dot(rel,tangent))
        lat=float(np.dot(rel,normal))
        # Atua entre 4 e 15 m do inÃ­cio; nÃºcleo forte 6..13 m.
        if s<4.0 or s>13.8:
            continue
        if abs(lat)>half+4.0:
            continue
        wlong=smooth01((s-4.0)/2.0)*smooth01((13.8-s)/1.8)
        if abs(lat)<=half:
            wlat=1.0
        else:
            wlat=1.0-smooth01((abs(lat)-half)/4.0)
        # A hard-boundary permanece imutÃ¡vel em X=-284; transiÃ§Ã£o comeÃ§a 2 m a oeste.
        if p[0]>=-284.0:
            wbound=0.0
        elif p[0]<=-286.0:
            wbound=1.0
        else:
            wbound=smooth01((-284.0-p[0])/2.0)
        w=wlong*wlat*wbound
        if w<=0:
            continue
        target=center_height(s)
        old=float(H2[j,i])
        H2[j,i]=old*(1-w)+target*w
        delta=abs(float(H2[j,i])-old)
        if delta>1e-9:
            changed+=1;max_delta=max(max_delta,delta)

# Hard-boundary numeric invariant.
ib=int(round((-284.0-gx[0])/step))
boundary_delta=float(np.nanmax(np.abs(H2[:,ib]-H[:,ib])))

# DiagnÃ³stico dos pontos anteriormente problemÃ¡ticos usando a nova superfÃ­cie.
probe=[]
count=max(1,math.ceil(L/2))
for q in (4,5,6):
    p=a+v*(q/count)
    left=p+normal*half;right=p-normal*half
    zl=sample(H2,*left);zr=sample(H2,*right);zc=sample(H2,*p)
    bank=None if zl is None or zr is None else abs((zr-zl)/(half*2))
    probe.append({"q":q,"xy":p.tolist(),"center_z":zc,"left_z":zl,"right_z":zr,"crossfall":bank})

meta={
 "schema":"boas/manoel-vitorino-crossfall-b55-v1",
 "source":"coastal_integrated_surface_b54.npz",
 "osm_way_id":456471269,
 "patch_s_m":[4.0,13.8],
 "core_s_m":[6.0,12.0],
 "gameplay_width_m":float(rec["gameplay_width_m"]),
 "transition_lateral_m":4.0,
 "hard_boundary_x":-284.0,
 "changed_grid_vertices":changed,
 "maximum_vertex_delta_m":max_delta,
 "hard_boundary_max_delta_m":boundary_delta,
 "problem_probe":probe,
 "problem_probe_max_crossfall":max(r["crossfall"] or 0.0 for r in probe),
 "target_vehicle_crossfall_gate":0.15
}
np.savez_compressed(root/"artifacts/waterfront/coastal_integrated_surface_b55.npz",gx=gx,gy=gy,H=H2,mask=mask,surface=surface,underwater=under,waymap=waymap)
(root/"artifacts/waterfront/coastal_integrated_surface_b55.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps(meta,ensure_ascii=False))

