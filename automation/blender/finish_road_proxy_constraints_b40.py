"""Insere apoios locais comprovados nas faces/arestas que ainda divergem."""
import bpy,bmesh,json,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
r=Path(__file__).resolve().parents[2];scene=bpy.context.scene
rp=r/'docs/reports/blender/road_transport_b40.json';report=json.loads(rp.read_text(encoding='utf8'))
assert Path(bpy.data.filepath).resolve()==(r/report['source_after']['file']).resolve()
c=json.loads((r/'world/areas/mvp-centro-lacerda/production.json').read_text(encoding='utf8'))
p=scene.objects[c['export']['terrain_proxy']];g=scene.objects[c['export']['road_object']]
g.data.calc_loop_triangles();gt=list(g.data.loop_triangles)
ground=BVHTree.FromPolygons([g.matrix_world@v.co for v in g.data.vertices],[list(t.vertices) for t in gt],all_triangles=True)
slots={i for i,m in enumerate(g.data.materials) if m and m.name in c['export']['road_materials']}
def target(point):
    q,n,i,_=ground.ray_cast(point+Vector((0,0,.5)),Vector((0,0,-1)),1.)
    return q if q is not None and n.z>.7 and gt[i].material_index in slots else None
def proxy_tree():
    p.data.calc_loop_triangles();tri=list(p.data.loop_triangles)
    return BVHTree.FromPolygons([v.co for v in p.data.vertices],[list(t.vertices) for t in tri],all_triangles=True),tri
points=[Vector(item['point']) for item in json.loads((r/'artifacts/roads/rondesp/collision_priority_targets.json').read_text(encoding='utf8'))['targets']]
pokes=0;splits=0;skipped=[]
for point in points:
    q=target(point);tree,tri=proxy_tree();hit,n,idx,_=tree.ray_cast(point+Vector((0,0,.5)),Vector((0,0,-1)),1.)
    if q is None or hit is None:skipped.append({'point':list(point),'reason':'missing_layer_support'});continue
    if abs(q.z-hit.z)<=.05:continue
    bm=bmesh.new();bm.from_mesh(p.data);bm.faces.ensure_lookup_table();face=bm.faces[tri[idx].polygon_index]
    candidates=[]
    for edge in face.edges:
        a,b=[v.co.to_2d() for v in edge.verts];d=b-a
        t=max(0,min(1,(q.to_2d()-a).dot(d)/max(d.length_squared,1e-12)))
        xy=a+d*t;candidates.append(((q.to_2d()-xy).length,edge,t,xy))
    distance,edge,t,xy=min(candidates,key=lambda item:item[0])
    if distance<.003:
        # Keep the existing edge XY exactly; shared faces follow the same split.
        new_point=Vector((xy.x,xy.y,hit.z));projection=target(new_point)
        if projection is None or not .0001<t<.9999:
            bm.free();skipped.append({'point':list(point),'reason':'edge_endpoint_or_unreliable_projection'});continue
        _,v=bmesh.utils.edge_split(edge,edge.verts[0],t);v.co=projection;splits+=1
    else:
        created=bmesh.ops.poke(bm,faces=[face],offset=0,use_relative_offset=False)
        created['verts'][0].co=q;pokes+=1
    bm.to_mesh(p.data);bm.free();p.data.update()
tree,tri=proxy_tree();errors=[];missing=0
for point in points:
    q=target(point);hit=tree.ray_cast(point+Vector((0,0,.5)),Vector((0,0,-1)),1.)[0]
    if q is None or hit is None:missing+=1
    else:errors.append(abs(q.z-hit.z))
assert not missing and max(errors)<report['best_maximum_difference_m'],'Não salvar sem melhoria'
me=p.data;me.calc_loop_triangles();xyz=np.array([list(v.co) for v in me.vertices],dtype=np.float64);ts=np.array([list(t.vertices) for t in me.loop_triangles],dtype=np.int32)
areas=np.linalg.norm(np.cross(xyz[ts[:,1]]-xyz[ts[:,0]],xyz[ts[:,2]]-xyz[ts[:,0]]),axis=1)*.5
assert np.isfinite(xyz).all() and not np.any(areas<1e-9),'Revisar topologia antes de salvar'
report['local_support_constraints']={'face_points_inserted':pokes,'shared_edges_split':splits,'skipped':skipped,'wheel_targets':len(points),'maximum_difference_m':max(errors),'missing_support':missing,'degenerate_triangles':0,'vertices_after':len(me.vertices),'faces_after':len(me.polygons)}
report['best_maximum_difference_m']=max(errors);report['vertices_after']=len(me.vertices);report['faces_after']=len(me.polygons)
report['source_reopened']=False
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
report['source_after']['sha256']=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()
rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(report['local_support_constraints']))
