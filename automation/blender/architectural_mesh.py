"""Primitivas de arquitetura em buffers sem juntar componentes semânticos."""
import math,bpy,bmesh
from mathutils import Vector

class Geometry:
    def __init__(self):self.v=[];self.f=[]
    def poly(self,points):
        i=len(self.v);self.v.extend(tuple(p) for p in points);self.f.append(tuple(range(i,i+len(points))))
    def box(self,center,size,axes=None):
        axes=axes or (Vector((1,0,0)),Vector((0,1,0)),Vector((0,0,1)))
        c=Vector(center);a,b,z=[Vector(t)*s/2 for t,s in zip(axes,size)]
        v=[c+sx*a+sy*b+sz*z for sx,sy,sz in ((-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1))]
        i=len(self.v);self.v.extend(tuple(p) for p in v)
        self.f.extend(tuple(i+k for k in f) for f in ((0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)))
    def bar(self,p,q,r,n=8):
        p,q=Vector(p),Vector(q);d=(q-p).normalized();a=d.cross(Vector((0,0,1)))
        if a.length<.01:a=d.cross(Vector((0,1,0)))
        a.normalize();b=d.cross(a);i=len(self.v)
        for c in (p,q):self.v.extend(tuple(c+r*(a*math.cos(j*2*math.pi/n)+b*math.sin(j*2*math.pi/n))) for j in range(n))
        self.f.extend((i+j,i+(j+1)%n,i+n+(j+1)%n,i+n+j) for j in range(n))
        self.f.extend((tuple(i+j for j in reversed(range(n))),tuple(i+n+j for j in range(n))))
    def lathe(self,center,profile,n=48):
        c=Vector(center);i=len(self.v)
        for r,z in profile:self.v.extend(tuple(c+Vector((r*math.cos(j*2*math.pi/n),r*math.sin(j*2*math.pi/n),z))) for j in range(n))
        for k in range(len(profile)-1):self.f.extend((i+k*n+j,i+k*n+(j+1)%n,i+(k+1)*n+(j+1)%n,i+(k+1)*n+j) for j in range(n))
        self.f.extend((tuple(i+j for j in reversed(range(n))),tuple(i+(len(profile)-1)*n+j for j in range(n))))
    def panel(self,p,u,n,x0,x1,z0,z1,depth,holes=()):
        """Parede com vãos retangulares reais; origem p no nível inferior."""
        u,n=Vector(u),Vector(n);p=Vector(p);up=Vector((0,0,1))
        xs=sorted(set([x0,x1]+[max(x0,min(x1,h[i])) for h in holes for i in (0,1)]))
        zs=sorted(set([z0,z1]+[max(z0,min(z1,h[i])) for h in holes for i in (2,3)]))
        for a,b in zip(xs,xs[1:]):
            for c,d in zip(zs,zs[1:]):
                x=(a+b)/2;z=(c+d)/2
                if b-a<.0001 or d-c<.0001 or any(h[0]<x<h[1] and h[2]<z<h[3] for h in holes):continue
                self.box(p+u*x+up*z-n*depth/2,(b-a,depth,d-c),(u,n,up))
    def arch(self,p,u,n,width,spring,base,top,depth,segments=24):
        """Testa in muratura con apertura semicircolare e intradosso reale."""
        p=Vector(p);u,n=Vector(u),Vector(n);up=Vector((0,0,1));r=width/2
        for j in range(segments):
            a=math.pi*j/segments;b=math.pi*(j+1)/segments
            xa=-r*math.cos(a);xb=-r*math.cos(b);za=spring+r*math.sin(a);zb=spring+r*math.sin(b)
            pts=[p+u*xa+up*za,p+u*xb+up*zb,p+u*xb+up*top,p+u*xa+up*top]
            self.poly(pts);self.poly([v-n*depth for v in reversed(pts)])
            self.poly([pts[0],pts[0]-n*depth,pts[1]-n*depth,pts[1]])
        for x in (-r,r):self.poly([p+u*x+up*base,p+u*x+up*spring,p+u*x+up*spring-n*depth,p+u*x+up*base-n*depth])
    def arch_ring(self,p,u,n,r,spring,thickness,depth,segments=32):
        p=Vector(p);u,n=Vector(u),Vector(n);up=Vector((0,0,1))
        for j in range(segments):
            a=math.pi*j/segments;b=math.pi*(j+1)/segments
            points=[p-u*math.cos(a)*r+up*(spring+math.sin(a)*r),p-u*math.cos(b)*r+up*(spring+math.sin(b)*r),p-u*math.cos(b)*(r+thickness)+up*(spring+math.sin(b)*(r+thickness)),p-u*math.cos(a)*(r+thickness)+up*(spring+math.sin(a)*(r+thickness))]
            self.poly(points);self.poly([v+n*depth for v in reversed(points)])
            self.poly([points[0],points[1],points[1]+n*depth,points[0]+n*depth]);self.poly([points[2],points[3],points[3]+n*depth,points[2]+n*depth])
    def object(self,name,col,mat,matrix=None,bevel=0,props=None):
        me=bpy.data.meshes.new(name);me.from_pydata(self.v,[],self.f);me.update()
        bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-5);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
        o=bpy.data.objects.new(name,me);col.objects.link(o);me.materials.append(mat)
        if matrix:o.matrix_world=matrix
        if bevel:
            mod=o.modifiers.new('Acabamento de arestas','BEVEL');mod.width=bevel;mod.segments=2
        for k,v in (props or {}).items():o[k]=v
        return o
