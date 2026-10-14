"""Geometria numérica para CCD translacional e distância cápsula/triângulo.

Não exige engine. Tolerâncias e limites de convergência são explícitos nos relatórios.
"""
import numpy as np

def point_segment_sq(p, a, b):
    ab=b-a; t=np.clip(np.sum((p-a)*ab,axis=-1)/np.maximum(np.sum(ab*ab,axis=-1),1e-30),0,1)
    return np.sum((p-a-t[...,None]*ab)**2,axis=-1)

def point_triangle_sq(p, tri):
    a,b,c=tri[:,0],tri[:,1],tri[:,2];u=b-a;v=c-a;n=np.cross(u,v)
    n2=np.sum(n*n,axis=1); ap=p-a; t=np.sum(ap*n,axis=1)/np.maximum(n2,1e-30)
    projection=p-t[:,None]*n;w=projection-a
    uu=np.sum(u*u,axis=1);vv=np.sum(v*v,axis=1);uv=np.sum(u*v,axis=1)
    wu=np.sum(w*u,axis=1);wv=np.sum(w*v,axis=1);den=uu*vv-uv*uv
    s=(wu*vv-wv*uv)/np.maximum(den,1e-30);q=(wv*uu-wu*uv)/np.maximum(den,1e-30)
    inside=(s>=-1e-10)&(q>=-1e-10)&(s+q<=1+1e-10)&(n2>1e-20)
    edge=np.minimum.reduce([point_segment_sq(p,a,b),point_segment_sq(p,b,c),point_segment_sq(p,c,a)])
    return np.where(inside,t*t*n2,edge)

def segment_segment_sq(p,q,a,b):
    # Mínimo quadrático restrito: solução interior + quatro bordas do retângulo.
    u=q-p;v=b-a;w=p-a;aa=np.dot(u,u);bb=np.sum(u*v,axis=1);cc=np.sum(v*v,axis=1)
    dd=np.sum(w*u,axis=1);ee=np.sum(w*v,axis=1);den=aa*cc-bb*bb
    s=(bb*ee-cc*dd)/np.maximum(den,1e-30);t=(aa*ee-bb*dd)/np.maximum(den,1e-30)
    interior=(den>1e-20)&(s>=0)&(s<=1)&(t>=0)&(t<=1)
    d=np.sum((w+s[:,None]*u-t[:,None]*v)**2,axis=1)
    edges=np.minimum.reduce([point_segment_sq(p,a,b),point_segment_sq(q,a,b),
                             point_segment_sq(a,np.broadcast_to(p,a.shape),np.broadcast_to(q,a.shape)),
                             point_segment_sq(b,np.broadcast_to(p,b.shape),np.broadcast_to(q,b.shape))])
    return np.where(interior,np.minimum(d,edges),edges)

def capsule_distances(base,tri,radius=.3,height=1.8):
    p=np.asarray(base)+[0,0,radius];q=np.asarray(base)+[0,0,height-radius]
    a,b,c=tri[:,0],tri[:,1],tri[:,2]
    d=np.minimum(point_triangle_sq(p,tri),point_triangle_sq(q,tri))
    for x,y in ((a,b),(b,c),(c,a)):d=np.minimum(d,segment_segment_sq(p,q,x,y))
    n=np.cross(b-a,c-a);den=n@(q-p);t=np.sum((a-p)*n,axis=1)/np.where(abs(den)>1e-20,den,1)
    hit=p+t[:,None]*(q-p);on=(t>=0)&(t<=1)&(abs(den)>1e-20)&(point_triangle_sq(hit,tri)<1e-16)
    return np.sqrt(np.maximum(np.where(on,0,d),0))

def continuous_triangle_pair(moving,static,delta,tolerance=1e-7):
    """CCD SAT exato para pares de triângulos sob uma única translação linear.

    Axes adicionais resolvem triângulos coplanares; contato é reportado, não
    necessariamente penetração. Retorna intervalos em t normalizado [0,1].
    """
    n=len(static);a=np.broadcast_to(moving,(n,3,3));b=static
    ea=np.roll(a,-1,axis=1)-a;eb=np.roll(b,-1,axis=1)-b
    na=np.cross(ea[:,0],ea[:,1]);nb=np.cross(eb[:,0],eb[:,1])
    axes=[na,nb]
    axes += [np.cross(ea[:,i],eb[:,j]) for i in range(3) for j in range(3)]
    axes += [np.cross(na,ea[:,i]) for i in range(3)]
    axes += [np.cross(nb,eb[:,i]) for i in range(3)]
    enter=np.zeros(n);leave=np.ones(n);valid=np.ones(n,dtype=bool)
    for axis in axes:
        norm=np.linalg.norm(axis,axis=1);axis=axis/np.maximum(norm[:,None],1e-30)
        pa=np.einsum('nvc,nc->nv',a,axis);pb=np.einsum('nvc,nc->nv',b,axis)
        amin=pa.min(axis=1);amax=pa.max(axis=1);bmin=pb.min(axis=1);bmax=pb.max(axis=1)
        velocity=axis@delta;moving_axis=abs(velocity)>1e-12
        stationary_overlap=(amax>=bmin-tolerance)&(bmax>=amin-tolerance)
        valid &= (norm<1e-12)|moving_axis|stationary_overlap
        v=np.where(moving_axis,velocity,1)
        t0=(bmin-amax-tolerance)/v;t1=(bmax-amin+tolerance)/v
        enter=np.maximum(enter,np.where(moving_axis,np.minimum(t0,t1),0))
        leave=np.minimum(leave,np.where(moving_axis,np.maximum(t0,t1),1))
        valid &= enter<=leave
    return valid,enter,leave

def support_hits(x,y,tri,low,high):
    a,b,c=tri[:,0],tri[:,1],tri[:,2];n=np.cross(b-a,c-a)
    norm=np.linalg.norm(n,axis=1);walkable=np.abs(n[:,2])>=.7*norm
    den=(b[:,1]-c[:,1])*(a[:,0]-c[:,0])+(c[:,0]-b[:,0])*(a[:,1]-c[:,1])
    safe=np.where(abs(den)>1e-14,den,1)
    u=((b[:,1]-c[:,1])*(x-c[:,0])+(c[:,0]-b[:,0])*(y-c[:,1]))/safe
    v=((c[:,1]-a[:,1])*(x-c[:,0])+(a[:,0]-c[:,0])*(y-c[:,1]))/safe
    z=u*a[:,2]+v*b[:,2]+(1-u-v)*c[:,2]
    mask=walkable&(abs(den)>1e-14)&(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8)&(z>=low)&(z<=high)
    return np.flatnonzero(mask),z[mask]
