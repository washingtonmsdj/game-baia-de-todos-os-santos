"""Contornos de vidro sem overshoot nas transições curtas/longas do desenho."""
import bpy,math,bmesh
from mathutils import Vector
s=bpy.context.scene
def depth(x,z,end,off):return (-6.045+.205*(abs(x)/1.25)**4+.145*max(0,z-1.12)+.08*max(0,.67-z)-off) if end<0 else (6.025-.19*(abs(x)/1.25)**4-.075*max(0,z-1.8)+off)
def rounded(pts,r=.075):
    out=[]
    for i,p in enumerate(pts):
        p=Vector(p);a=Vector(pts[i-1]);b=Vector(pts[(i+1)%len(pts)]);v1=(a-p);v2=(b-p)
        q1=p+v1.normalized()*min(r,v1.length*.3);q2=p+v2.normalized()*min(r,v2.length*.3)
        for j in range(7):t=j/6;v=(1-t)**2*q1+2*(1-t)*t*p+t*t*q2;out.append(tuple(v))
    return out
def scale(pts,k):
    cx=sum(x for x,z in pts)/len(pts);cz=sum(z for x,z in pts)/len(pts);return [(cx+(x-cx)*k,cz+(z-cz)*k) for x,z in pts]
def replace(o,vs,fs):
    me=bpy.data.meshes.new(o.name+' contorno continuo');me.from_pydata(vs,[],fs);me.update();me.materials.append(o.data.materials[0]);o.data=me;o.hide_render=False
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    for p in me.polygons:p.use_smooth=True
    for m in o.modifiers:
        if m.type=='SOLIDIFY':m.show_render=True;m.show_viewport=True;m.use_rim=True
for label,end,pts in [('Dianteira',-1,[(-1.08,2.62),(-1.035,2.65),(1.035,2.65),(1.08,2.62),(1.085,1.66),(.93,1.4),(.62,1.255),(-.62,1.255),(-.93,1.4),(-1.085,1.66)]),('Traseira',1,[(-1.065,2.82),(1.065,2.82),(1.1,2.69),(1.105,2.07),(.88,2.10),(0,2.135),(-.88,2.10),(-1.105,2.07),(-1.1,2.69)])]:
    pts=rounded(pts)
    for part,k1,k2,off in [('vedacao vidro',1,.964,.024),('filete vidro',.985,.977,.029)]:
        o=bpy.data.objects['TOR04 | '+label+' '+part];a,b=scale(pts,k1),scale(pts,k2);N=len(pts)
        vs=[(x,depth(x,z,end,off),z) for x,z in a+b];fs=[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)];replace(o,vs,fs)
    inner=scale(pts,.964);dense=[]
    for p,q in zip(inner,inner[1:]+inner[:1]):
        count=max(1,int(Vector((q[0]-p[0],q[1]-p[1])).length/.028))
        for j in range(count):t=j/count;dense.append((p[0]*(1-t)+q[0]*t,p[1]*(1-t)+q[1]*t))
    cx=sum(x for x,z in dense)/len(dense);cz=sum(z for x,z in dense)/len(dense);N=len(dense);vs=[(cx,depth(cx,cz,end,.025),cz)];fs=[]
    for k in range(1,25):
        for x,z in dense:
            xx=cx+(x-cx)*k/24;zz=cz+(z-cz)*k/24;vs.append((xx,depth(xx,zz,end,.025),zz))
    fs.extend((0,1+i,1+(i+1)%N) for i in range(N))
    for k in range(23):
        a=1+k*N;b=a+N;fs.extend((a+i,a+(i+1)%N,b+(i+1)%N,b+i) for i in range(N))
    replace(bpy.data.objects['TOR04 | '+label+' vidro curvo'],vs,fs)
print('Vidros sem autointerseções de contorno.')
