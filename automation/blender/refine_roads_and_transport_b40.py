"""Refino local comprovado do proxy e guias de trânsito candidatas, sem alargar vias."""
import bpy,bmesh,json,hashlib,runpy,math,numpy as np
from pathlib import Path
from collections import defaultdict
from mathutils import Vector
from mathutils.bvhtree import BVHTree

r=Path(__file__).resolve().parents[2];scene=bpy.context.scene
catalog=json.loads((r/'world/areas/mvp-centro-lacerda/blender-revisions.json').read_text(encoding='utf8'))
before=catalog['authoring_source'];assert before['revision']=='R30B.39'
assert Path(bpy.data.filepath).resolve()==(r/before['file']).resolve()
out=r/'blender/salvador_lacerda_r30b40_fluxos_e_colisao.blend';assert not out.exists()
c=json.loads((r/'world/areas/mvp-centro-lacerda/production.json').read_text(encoding='utf8'))
network=json.loads((r/'world/areas/mvp-centro-lacerda/transport-network.json').read_text(encoding='utf8'))
widths=json.loads((r/'docs/reports/blender/road_width_scene_b39.json').read_text(encoding='utf8'))
targets=json.loads((r/'artifacts/roads/rondesp/collision_priority_targets.json').read_text(encoding='utf8'))
proxy=scene.objects[c['export']['terrain_proxy']];ground=scene.objects[c['export']['road_object']]
assert not proxy.parent and all(abs(proxy.matrix_world[i][j]-(1 if i==j else 0))<1e-6 for i in range(4) for j in range(4))
signature=runpy.run_path(str(r/'automation/blender/component_fingerprint.py'))['signature']
protected={o.name:signature(o) for o in scene.objects if o.type in {'MESH','CURVE','FONT'} and o!=proxy}
ground.data.calc_loop_triangles();gt=list(ground.data.loop_triangles)
surface=BVHTree.FromPolygons([ground.matrix_world@v.co for v in ground.data.vertices],[list(t.vertices) for t in gt],all_triangles=True)
slots={i for i,m in enumerate(ground.data.materials) if m and m.name in c['export']['road_materials']}
def target_height(p):
    q,n,idx,_=surface.ray_cast(p+Vector((0,0,.5)),Vector((0,0,-1)),1.)
    return q if q is not None and n.z>.7 and gt[idx].material_index in slots else None
points=[Vector(item['point']) for item in targets['targets']]
assert points,'Nenhuma correção geométrica comprovada'
before_vertices=len(proxy.data.vertices);before_faces=len(proxy.data.polygons)
iterations=[];best=None;best_error=float('inf');skipped=0
for iteration in range(7):
    proxy.data.calc_loop_triangles();pt=list(proxy.data.loop_triangles)
    tree=BVHTree.FromPolygons([v.co for v in proxy.data.vertices],[list(t.vertices) for t in pt],all_triangles=True)
    bad=set();errors=[];missing=0
    for p in points:
        target=target_height(p);q,n,idx,_=tree.ray_cast(p+Vector((0,0,.5)),Vector((0,0,-1)),1.)
        if q is None or target is None:missing+=1;continue
        error=abs(q.z-target.z);errors.append(error)
        if error>.05:bad.add(pt[idx].polygon_index)
    assert missing==0,'Refino perdeu apoio local'
    value=max(errors,default=0);iterations.append({'iteration':iteration,'bad_faces':len(bad),'maximum_difference_m':value,'missing_support':missing})
    if value<best_error:
        best=proxy.data.copy();best_error=value
    if not bad or iteration==6:break
    bm=bmesh.new();bm.from_mesh(proxy.data);bm.faces.ensure_lookup_table()
    edges={edge for idx in bad for edge in bm.faces[idx].edges}
    old={tuple(round(float(x),9) for x in v.co) for v in bm.verts}
    bmesh.ops.subdivide_edges(bm,edges=list(edges),cuts=1,use_grid_fill=True)
    for v in bm.verts:
        if tuple(round(float(x),9) for x in v.co) in old:continue
        target=target_height(v.co)
        if target is not None:v.co.z=target.z
        else:skipped+=1
    bm.to_mesh(proxy.data);bm.free();proxy.data.update()
proxy.data=best;proxy.data.update()
assert best_error<iterations[0]['maximum_difference_m']*.98,'Não salvar revisão sem melhoria real'
# Only polygons containing a zero-area triangle are touched.
def degenerate_polygons():
    me=proxy.data;me.calc_loop_triangles();xyz=np.array([list(v.co) for v in me.vertices],dtype=np.float64)
    tri=np.array([list(t.vertices) for t in me.loop_triangles],dtype=np.int32)
    areas=np.linalg.norm(np.cross(xyz[tri[:,1]]-xyz[tri[:,0]],xyz[tri[:,2]]-xyz[tri[:,0]]),axis=1)*.5
    return sorted({me.loop_triangles[int(i)].polygon_index for i in np.flatnonzero(areas<1e-9)})
removed=0
for _ in range(5):
    bad=degenerate_polygons()
    if not bad:break
    bm=bmesh.new();bm.from_mesh(proxy.data);bm.faces.ensure_lookup_table()
    bmesh.ops.triangulate(bm,faces=[bm.faces[i] for i in bad],quad_method='BEAUTY',ngon_method='EAR_CLIP')
    bm.to_mesh(proxy.data);bm.free();proxy.data.update()
    bad=degenerate_polygons()
    if not bad:break
    bm=bmesh.new();bm.from_mesh(proxy.data);bm.faces.ensure_lookup_table();faces=[bm.faces[i] for i in bad]
    assert all(len(f.verts)==3 for f in faces)
    removed+=len(faces);bmesh.ops.delete(bm,geom=faces,context='FACES')
    bm.to_mesh(proxy.data);bm.free();proxy.data.update()
assert not degenerate_polygons()
# Candidate rightmost lane guides: incomplete stations/segments never get bridged.
collection=bpy.data.collections.new('QA B40 | FLUXOS CANDIDATOS');scene.collection.children.link(collection)
collection.hide_render=True;collection['boas_role']='reference_transport_candidate_exclude_from_runtime_export'
collection['boas_source_manifest']='world/areas/mvp-centro-lacerda/transport-network.json'
collection['boas_approved']=False
curves=bpy.data.curves.new('QA B40 | faixas direitas candidatas','CURVE');curves.dimensions='3D';curves.bevel_depth=.022;curves.bevel_resolution=0
ob=bpy.data.objects.new('QA B40 | GUIAS | direita no sentido da via',curves);collection.objects.link(ob)
ob['boas_role']='reference_transport_candidate';ob['boas_approved']=False
mat=bpy.data.materials.new('QA B40 | cyan de inspeção');mat.diffuse_color=(.01,.55,.9,1);curves.materials.append(mat)
width_map={e['edge_id']:e for e in widths['segments']};guide_count=0;guide_gaps=0
for edge in network['segments']:
    if edge['support_issues'] or not edge['bus_candidate']:continue
    row=width_map.get(edge['id']);lane=[p for p in edge['lane_preview'] if p['index_from_driver_right']==1]
    if row is None or len(lane)!=3:continue
    stations={p['fraction']:p for p in row['stations']};p0=Vector(stations[.25]['position']);p1=Vector(stations[.75]['position'])
    f=(p1-p0).to_2d()
    if f.length<.001:continue
    f.normalize();right=Vector((f.y,-f.x,0));positions=[]
    for p in sorted(lane,key=lambda x:x['fraction']):
        base=Vector(stations[p['fraction']]['position']);point=base+right*p['offset_osm_right_m']
        target=target_height(point)
        if target is None:positions=[];guide_gaps+=1;break
        positions.append(target+Vector((0,0,.04)))
    if len(positions)!=3:continue
    spline=curves.splines.new('POLY');spline.points.add(2)
    for vertex,point in zip(spline.points,positions):vertex.co=(*point,1)
    guide_count+=1
changed=[name for name,value in protected.items() if name not in scene.objects or signature(scene.objects[name])!=value]
assert not changed,'Geometria visual protegida foi alterada'
proxy['boas_refinement']='B40 local same-layer supports; no real-width resizing'
scene['boas_transport_manifest']='world/areas/mvp-centro-lacerda/transport-network.json'
scene['boas_transport_status']='candidate_widths_unknown_bus_routes_and_stops_pending'
text=bpy.data.texts.new('B40 | Registro de vias e fluxos');text.write('Refino local de colisor e guias de faixa direita candidatas. Larguras reais ausentes na captura, sem redimensionamento. Fonte/QA em transport-network.json e road_transport_b40.json. Produção B30 preservada.\n')
report={'source_before':before,'classification':'ERROR','targets':len(points),'iterations':iterations,'best_maximum_difference_m':best_error,
        'new_vertices_without_projection':skipped,'vertices_before':before_vertices,'vertices_after':len(proxy.data.vertices),
        'faces_before':before_faces,'faces_after':len(proxy.data.polygons),'zero_area_faces_removed':removed,
        'protected_visual_components':len(protected),'protected_visual_differences':changed,'road_widths_changed':False,
        'guide_splines':guide_count,'guide_gaps':guide_gaps,'guides_status':'rightmost_preview_only_not_lane_markings_or_approved_traffic',
        'runtime_exported':False,'approved':False,'source_reopened':False,
        'pending':['Larguras reais e distribuição de faixas por evidência','Misericórdia, bindings e falhas restantes de pavimento','Fluxos e conversões legais, trajetos atuais e binding das paradas','Envelope completo de ônibus, física e sentidos inversos'],
        'transport_network':'world/areas/mvp-centro-lacerda/transport-network.json'}
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
report['source_after']={'file':out.relative_to(r).as_posix(),'revision':'R30B.40','sha256':hashlib.sha256(out.read_bytes()).hexdigest()}
(r/'docs/reports/blender/road_transport_b40.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in report.items() if k not in {'iterations','pending'}},ensure_ascii=False))
