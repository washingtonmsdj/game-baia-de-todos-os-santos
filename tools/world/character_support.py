"""Apoio da esfera inferior da cápsula em faces/arestas finitas de chão.

Retorna Z da base da cápsula com skin radial. Não cria superfícies ou rotas.
"""
import numpy as np


def capsule_support(x,y,triangles,minimum,maximum,radius=.30,skin=.015):
    t=np.asarray(triangles,float)
    if not len(t):return None
    normal=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);length=np.linalg.norm(normal,axis=1)
    normal/=np.maximum(length[:,None],1e-30);normal*=np.where(normal[:,2]<0,-1.,1.)[:,None]
    t=t[(normal[:,2]>=.65)&(length>1e-12)];normal=normal[(normal[:,2]>=.65)&(length>1e-12)]
    if not len(t):return None
    shell=radius+skin;values=[];xy=np.array([x,y])
    zplane=t[:,0,2]-np.sum((xy-t[:,0,:2])*normal[:,:2],axis=1)/normal[:,2]
    base=zplane+shell/normal[:,2]-radius
    contacts=np.column_stack((np.full(len(t),x),np.full(len(t),y),base+radius))-shell*normal
    a,b,c=t[:,0],t[:,1],t[:,2];u=b-a;v=c-a;w=contacts-a
    uu=np.sum(u*u,axis=1);uv=np.sum(u*v,axis=1);vv=np.sum(v*v,axis=1);wu=np.sum(w*u,axis=1);wv=np.sum(w*v,axis=1)
    den=uu*vv-uv*uv;s=(wu*vv-wv*uv)/np.maximum(den,1e-30);q=(wv*uu-wu*uv)/np.maximum(den,1e-30)
    values.extend(base[(s>=-1e-9)&(q>=-1e-9)&(s+q<=1+1e-9)].tolist())
    for i,j in ((0,1),(1,2),(2,0)):
        a=t[:,i];e=t[:,j]-a;horizontal=np.linalg.norm(e[:,:2],axis=1)
        unit=e[:,:2]/np.maximum(horizontal[:,None],1e-30);s0=np.sum((xy-a[:,:2])*unit,axis=1)
        perpendicular2=np.sum((xy-a[:,:2])**2,axis=1)-s0*s0
        slope=e[:,2]/np.maximum(horizontal,1e-30);rem=np.maximum(shell*shell-perpendicular2,0.)
        position=np.clip(s0+slope*np.sqrt(rem)/np.sqrt(1+slope*slope),0.,horizontal)
        point=a+e*(position/np.maximum(horizontal,1e-30))[:,None]
        d2=np.sum((point[:,:2]-xy)**2,axis=1);valid=d2<=shell*shell
        values.extend((point[:,2]+np.sqrt(np.maximum(shell*shell-d2,0))-radius)[valid].tolist())
    valid=[z for z in values if minimum<=z<=maximum+1e-8]
    return max(valid) if valid else None
