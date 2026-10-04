"""Leitura de interseções não locais da chapa na sessão visível."""
import bpy, json, collections
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_ray_tri
r=Path(__file__).resolve().parents[2]
assert not bpy.app.background and Path(bpy.data.filepath).name=='hilux_carroceria_v17.blend'
o=bpy.context.scene.objects['HILUX | CARROCERIA PRINCIPAL'];m=o.data
m.calc_loop_triangles()
vs=[v.co.copy() for v in m.vertices]
ts=[tuple(t.vertices) for t in m.loop_triangles]
faceids=[t.polygon_index for t in m.loop_triangles]
normals=[]
for tri in ts:
    a,b,c=[vs[i] for i in tri];normals.append((b-a).cross(c-a).normalized())
tree=BVHTree.FromPolygons(vs,ts,all_triangles=True,epsilon=0.)
attr=m.attributes['boas_panel_id'];labels=json.loads(o['boas_panel_id_map'])

def coplanar_area(pa,pb,n):
    axis=max(range(3),key=lambda i:abs(n[i]));axes=[i for i in range(3) if i!=axis]
    aa=[Vector((p[axes[0]],p[axes[1]])) for p in pa]
    bb=[Vector((p[axes[0]],p[axes[1]])) for p in pb]
    def cross(a,b): return a.x*b.y-a.y*b.x
    if cross(bb[1]-bb[0],bb[2]-bb[0])<0:bb.reverse()
    poly=aa
    for start,end in zip(bb,bb[1:]+bb[:1]):
        edge=end-start;clipped=[]
        for p,q in zip(poly,poly[1:]+poly[:1]):
            dp=cross(edge,p-start);dq=cross(edge,q-start)
            if dp>=0:clipped.append(p)
            if (dp>0)!=(dq>0) and abs(dp-dq)>1e-15:clipped.append(p.lerp(q,dp/(dp-dq)))
        poly=clipped
        if len(poly)<3:return 0.
    return abs(sum(cross(p,q) for p,q in zip(poly,poly[1:]+poly[:1])))/2

def shared_boundary_contact(face_a,face_b,point):
    edges=set(m.polygons[face_a].edge_keys).intersection(m.polygons[face_b].edge_keys)
    for ia,ib in edges:
        a,b=vs[ia],vs[ib];d=b-a
        if d.length_squared<1e-20:continue
        t=max(0,min(1,(point-a).dot(d)/d.length_squared))
        if (point-a-d*t).length<=1e-6:return True
    return False

pairs=set(); intersections=[];near_contacts=0
for ia,ib in tree.overlap(tree):
    if ia>=ib or faceids[ia]==faceids[ib] or set(ts[ia]).intersection(ts[ib]):continue
    pa,pb=([vs[i] for i in ts[t]] for t in [ia,ib]);na,nb=normals[ia],normals[ib]
    da=[(p-pb[0]).dot(nb) for p in pa];db=[(p-pa[0]).dot(na) for p in pb]
    if min(da)>1e-7 or max(da)<-1e-7 or min(db)>1e-7 or max(db)<-1e-7:continue
    hit=None;coplanar=na.cross(nb).length<1e-6 and max(abs(d) for d in da)<1e-7
    if coplanar:
        if coplanar_area(pa,pb,na)>1e-10:hit=sum(pa,Vector())/3
    else:
        for tri,other in [(pa,pb),(pb,pa)]:
            for p,q in zip(tri,tri[1:]+tri[:1]):
                d=q-p
                point=intersect_ray_tri(*other,d,p,True)
                if point is None or d.length_squared<1e-14:continue
                t=(point-p).dot(d)/d.length_squared
                # Um ponto sobre a aresta de outra chapa ligada é contato,
                # não penetração. Exigir também o interior do triângulo alvo
                # evita classificar erro numérico da borda como cruzamento.
                a,b,c=other;v0=b-a;v1=c-a;v2=point-a
                d00,d01,d11=v0.dot(v0),v0.dot(v1),v1.dot(v1)
                den=d00*d11-d01*d01
                if abs(den)<1e-20:continue
                u=(d11*v2.dot(v0)-d01*v2.dot(v1))/den
                v=(d00*v2.dot(v1)-d01*v2.dot(v0))/den
                if 1e-6<t<1-1e-6 and min(u,v,1-u-v)>1e-6:hit=point;break
            if hit is not None:break
    if hit is None:continue
    key=tuple(sorted((faceids[ia],faceids[ib])))
    if shared_boundary_contact(*key,hit):
        near_contacts+=1;continue
    if key in pairs:continue
    pairs.add(key)
    intersections.append({'faces':list(key),'panels':[attr.data[i].value for i in key],
        'point':list(hit),'coplanar':coplanar})
counts=collections.Counter(' + '.join(labels[str(p)] for p in sorted(v['panels'])) for v in intersections)
report={'source':'base_mesh','tolerance_m':1e-7,'non_adjacent_intersecting_face_pairs':len(intersections),
    'shared_edge_contact_tolerance_m':1e-6,'shared_edge_triangle_contacts_excluded':near_contacts,
    'panel_counts':dict(counts),'intersections':intersections,
    'scope':'Penetração no interior de triângulos sem vértices compartilhados; exclui contato de bordas e não substitui conferência dos conjuntos reservados.'}
(r/'artifacts/vehicles/rondesp/v17-intersections.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
