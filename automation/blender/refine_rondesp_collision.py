"""Corrige somente diferenças comprovadas piso/colisor, na camada certa."""
import bpy,bmesh,json,runpy,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
path=r/'docs/reports/blender/rondesp_network_audit_b38.json';report=json.loads(path.read_text(encoding='utf8'))
backup=r/'artifacts/roads/rondesp/network_before.json'
if not backup.exists():backup.write_bytes(path.read_bytes())
c=json.loads((r/'world/areas/mvp-centro-lacerda/production.json').read_text(encoding='utf8'))
wm=runpy.run_path(str(r/'automation/blender/component_fingerprint.py'))['world_matrix']
terrain=s.objects[c['export']['road_object']];ob=s.objects[c['export']['terrain_proxy']]
assert not ob.parent and all(abs(ob.matrix_world[i][j]-(1 if i==j else 0))<1e-6 for i in range(4) for j in range(4))
terrain.data.calc_loop_triangles();tris=list(terrain.data.loop_triangles)
ground=BVHTree.FromPolygons([wm(terrain)@v.co for v in terrain.data.vertices],[list(t.vertices) for t in tris],all_triangles=True)
slots={i for i,m in enumerate(terrain.data.materials) if m and m.name in c['export']['road_materials']}
def support(p):
    q,n,idx,_=ground.ray_cast(Vector((p.x,p.y,p.z+.5)),Vector((0,0,-1)),1.)
    return q if q is not None and tris[idx].material_index in slots and n.z>.7 else None
points=[]
contacts=report['vehicle_contacts_asset_local'];midy=(min(p[1] for p in contacts)+max(p[1] for p in contacts))/2
for row in report['segments']:
    for sample in row.get('samples',[]):
        if set(sample['issues'])!={'collision_visual_difference'}:continue
        if sample.get('max_proxy_difference_m',10)>.25:continue
        pose=sample['pose'];from mathutils import Quaternion
        rot=Quaternion(pose['rotation']);center=Vector(pose['location'])
        points.extend(center+rot@Vector(p) for p in contacts)
before_vertices=len(ob.data.vertices);iterations=[];skipped=0;best=None;best_error=float('inf')
for iteration in range(5):
    ob.data.calc_loop_triangles();pt=list(ob.data.loop_triangles)
    tree=BVHTree.FromPolygons([v.co for v in ob.data.vertices],[list(t.vertices) for t in pt],all_triangles=True)
    bad=set();errors=[]
    for p in points:
        target=support(p)
        if target is None:continue
        q,n,idx,_=tree.ray_cast(Vector((p.x,p.y,p.z+.5)),Vector((0,0,-1)),1.)
        if q is None:continue
        error=abs(q.z-target.z);errors.append(error)
        if error>.05:bad.add(pt[idx].polygon_index)
    iterations.append({'iteration':iteration,'bad_faces':len(bad),'max_difference_m':max(errors,default=0)})
    if max(errors,default=0)<best_error:
        best=ob.data.copy();best_error=max(errors,default=0)
    if not bad or iteration==4:break
    bm=bmesh.new();bm.from_mesh(ob.data);bm.faces.ensure_lookup_table()
    edges={e for index in bad for e in bm.faces[index].edges};old_coordinates={tuple(round(float(x),9) for x in v.co) for v in bm.verts}
    bmesh.ops.subdivide_edges(bm,edges=list(edges),cuts=1,use_grid_fill=True)
    for v in bm.verts:
        if tuple(round(float(x),9) for x in v.co) in old_coordinates:continue
        target=support(v.co)
        if target is not None:v.co.z=target.z
        else:skipped+=1
    bm.to_mesh(ob.data);bm.free();ob.data.update()
if best is not None:
    ob.data=best;ob.data.update()
inserted=0
for p in points:
    target=support(p)
    if target is None:continue
    ob.data.calc_loop_triangles();pt=list(ob.data.loop_triangles)
    tree=BVHTree.FromPolygons([v.co for v in ob.data.vertices],[list(t.vertices) for t in pt],all_triangles=True)
    q,n,index,_=tree.ray_cast(Vector((p.x,p.y,p.z+.5)),Vector((0,0,-1)),1.)
    if q is None or abs(q.z-target.z)<=.05:continue
    bm=bmesh.new();bm.from_mesh(ob.data);bm.faces.ensure_lookup_table();face=bm.faces[pt[index].polygon_index]
    too_close=False
    for edge in face.edges:
        a,b=[v.co.to_2d() for v in edge.verts];d=b-a
        t=max(0,min(1,(target.to_2d()-a).dot(d)/max(d.length_squared,1e-12)))
        if (target.to_2d()-(a+d*t)).length<.003:too_close=True
    if too_close:bm.free();continue
    result=bmesh.ops.poke(bm,faces=[face],offset=0,use_relative_offset=False)
    result['verts'][0].co=target;inserted+=1
    bm.to_mesh(ob.data);bm.free();ob.data.update()
ob.data.calc_loop_triangles();pt=list(ob.data.loop_triangles)
tree=BVHTree.FromPolygons([v.co for v in ob.data.vertices],[list(t.vertices) for t in pt],all_triangles=True)
final_errors=[]
for p in points:
    target=support(p);q=tree.ray_cast(Vector((p.x,p.y,p.z+.5)),Vector((0,0,-1)),1.)[0]
    if target is not None and q is not None:final_errors.append(abs(q.z-target.z))
summary={'classification' :'ERROR','method':'Subdivisão local de faces do proxy com diferença >5 cm; somente novos vértices projetados no pavimento da mesma camada a ±0,5 m. Sem mover malha visual, eixo ou larguras.',
         'wheel_targets':len(points),'inserted_local_surface_constraints':inserted,'final_target_max_difference_m':max(final_errors,default=0),'vertices_before':before_vertices,'vertices_after':len(ob.data.vertices),'iterations':iterations,
         'new_vertices_not_projected':skipped,'retained_best_max_difference_m':best_error,'unresolved_larger_differences':'needs_review; diferenças >25 cm não corrigidas automaticamente',
         'runtime_exported':False,'visual_geometry_changed':False}
(r/'artifacts/roads/rondesp/collision_refinement.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(summary,ensure_ascii=False))
