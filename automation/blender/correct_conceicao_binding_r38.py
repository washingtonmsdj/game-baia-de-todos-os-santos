"""Corrige ligação de gameplay à camada errada e prepara replay local real.

Não altera OSM, larguras, terreno visual ou ligação entre ruas distintas.
"""
import bpy,bmesh,json,math,runpy,hashlib,shutil,numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];scene=bpy.context.scene
catalog=json.loads((root/'world/areas/mvp-centro-lacerda/blender-revisions.json').read_text())
source=catalog['authoring_source'];assert source['revision']=='R30B.37'
assert Path(bpy.data.filepath).resolve()==(root/source['file']).resolve()
c=json.loads((root/'world/areas/mvp-centro-lacerda/production.json').read_text())
api=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));wm=api['world_matrix'];signature=api['signature']
road=scene.objects['R30A7 | ROAD | 421206045']
protected={o.name:signature(o) for o in scene.objects if o!=road and o.type in {'MESH','CURVE','FONT'} and not o.constraints and not any(p.constraints for p in ([o.parent] if o.parent else []))}
proxy_before=protected.pop(c['export']['terrain_proxy'])
road_before=signature(road)
plan=json.loads((root/'artifacts/roads/r38/driveable_plan.json').read_text())
run=next(p for p in plan['paths'] if p['start_index']==57 and p['end_index']==238)
assert len(run['points'])==182
points=run['points']
assert max(abs(a['point'][2]-b['point'][2]) for a,b in zip(points,points[1:]))<.4
assert all(19<p['point'][2]<46 for p in points)
terrain=scene.objects[c['export']['road_object']];proxy=scene.objects[c['export']['terrain_proxy']]
def tree(o):
    me=o.data;me.calc_loop_triangles();a=np.empty(len(me.vertices)*3,dtype=np.float32);me.vertices.foreach_get('co',a);M=np.array(wm(o));xyz=a.reshape(-1,3)@M[:3,:3].T+M[:3,3]
    a=np.empty(len(me.loop_triangles)*3,dtype=np.int32);me.loop_triangles.foreach_get('vertices',a)
    return BVHTree.FromPolygons(xyz.tolist(),a.reshape(-1,3).tolist(),all_triangles=True)
ground=tree(terrain);collision=tree(proxy)
def h(t,q):
    return t.ray_cast(Vector((q[0],q[1],150)),Vector((0,0,-1)),350)[0]
errors=[];support_samples=[]
for p in points:
    f=np.array(p['forward']);s=np.array([-f[1],f[0]])
    for u,v in [(-1.61,-.84),(-1.61,.84),(1.61,-.84),(1.61,.84),(0,0)]:
        q=np.array(p['point'][:2])+f*u+s*v;a,b=h(ground,q),h(collision,q)
        assert a is not None and b is not None,'Falta apoio; não criar piso fictício'
        errors.append(abs(a.z-b.z));support_samples.append({'xy':q.tolist(),'source_z':a.z,'proxy_z':b.z,'difference':abs(a.z-b.z)})
(root/'artifacts/roads/r38/proxy_support.json').write_text(json.dumps(support_samples),encoding='utf8')
proxy_vertices_before=len(proxy.data.vertices);iterations=[];subdivided_without_reprojection=0
backup=proxy.data.copy()
try:
    for iteration in range(7):
        collision=tree(proxy);bad=set();errors=[];triangles=list(proxy.data.loop_triangles)
        for sample in support_samples:
            q,n,index,d=collision.ray_cast(Vector((*sample['xy'],150)),Vector((0,0,-1)),350)
            assert q is not None,'Collider sem apoio'
            error=abs(q.z-sample['source_z']);errors.append(error)
            if error>.05:bad.add(triangles[index].polygon_index)
        iterations.append({'iteration':iteration,'bad_faces':len(bad),'max_error_m':max(errors)})
        if not bad:break
        assert iteration<6,'Refino não convergiu; não salvar revisão'
        bm=bmesh.new();bm.from_mesh(proxy.data);bm.faces.ensure_lookup_table()
        edges={e for i in bad for e in bm.faces[i].edges};before=set(bm.verts)
        bmesh.ops.subdivide_edges(bm,edges=list(edges),cuts=1,use_grid_fill=True)
        M=wm(proxy);inv=M.inverted()
        for v in set(bm.verts)-before:
            p=M@v.co
            # Sondagem na própria camada, sem saltar à pista de cima.
            q=ground.ray_cast(p+Vector((0,0,.5)),Vector((0,0,-1)),1)[0]
            if q is None:
                # A subdivisão também alcança bordas/contencões fora do corredor.
                # Sem apoio confiável, manter a interpolação da face anterior,
                # não projetar na via superior nem preencher uma abertura.
                subdivided_without_reprojection+=1
            else:v.co=inv@q
        bm.to_mesh(proxy.data);bm.free();proxy.data.update()
except Exception:
    changed_mesh=proxy.data;proxy.data=backup;bpy.data.meshes.remove(changed_mesh);raise
else:bpy.data.meshes.remove(backup)
proxy['boas_conceicao_refinement']='R30B.38: subdivisão local nas faces com diferença >5 cm; novos vértices com apoio confiável projetados na mesma camada visual, restantes mantêm interpolação anterior; XY e pista visual preservados.'
# O nó é identificado pela ordem explícita do mesmo OSM way e pelo XY registrado.
g=json.loads((root/c['staging']['roads']).read_text());way=next(w for w in g['ways'] if w['osm_way_id']==421206045)
node_index=[str(n) for n in way['node_refs']].index('7520527645');original_xy=way['blender_xy'][node_index]
legacy=scene.objects['Ladeira da Conceição da Praia.001'];assert str(legacy.get('osm_id'))=='421206045'
assert len(legacy.data.splines[0].points)==len(way['node_refs'])
target=wm(legacy)@Vector(legacy.data.splines[0].points[node_index].co[:3]);support=h(ground,target)
assert support is not None and 19<support.z<20
matches=[p for s in road.data.splines for p in s.points if math.dist((wm(road)@Vector(p.co[:3])).xy,original_xy)<.001]
assert len(matches)==1
old=list(wm(road)@Vector(matches[0].co[:3]));target.z=support.z+.18
local=wm(road).inverted()@target;matches[0].co=(*local,1)
road['boas_binding_revision']='R30B.38';road['boas_binding_classification']='ADAPT_LOCAL'
road['boas_binding_node_id']='7520527645';road['boas_binding_reference_xy']=json.dumps(original_xy)
road['boas_binding_reason']='Fit XY candidato atingia Montanha; binding local ao asfalto inferior da mesma via autoral por OSM ID e ordem dos nós. Referência OSM preservada.'
road['boas_binding_visual_clearance_m']=.18
road['boas_gameplay_approved']=False;road['boas_route_status']='partial_clearance_review'
coll=bpy.data.collections.new('GAMEPLAY | VALIDACAO | Conceicao B38');scene.collection.children.link(coll)
coll['boas_export']=False;coll['boas_role']='validation_only';coll.hide_render=True
data=bpy.data.curves.new('Conceicao | corredor verificado parcial','CURVE');data.dimensions='3D'
s=data.splines.new('POLY');s.points.add(len(points)-1)
for q,p in zip(s.points,points):q.co=(*p['point'],1)
path=bpy.data.objects.new('GAMEPLAY | Conceicao | percurso parcial B38',data);coll.objects.link(path)
path['boas_osm_way_id']='421206045';path['boas_role']='navigation_validation_candidate';path['boas_export']=False
path['boas_direction']='forward';path['boas_width_verified_m']='null';path['boas_approved']=False
path['boas_provenance']='artifacts/roads/r38/driveable_plan.json; pavimento existente; nenhum alargamento'
# Asset existente, mantido separado da arte final da cidade.
asset=root/'automation/blender/ordax_car_realistic_v14_reference_cleanup.blend'
assert asset.is_file()
existing=set(bpy.data.objects)
with bpy.data.libraries.load(str(asset),link=False) as (src,dst):dst.objects=list(src.objects)
parts=[];worlds={}
for o in dst.objects:
    if o.type in {'MESH','CURVE'} and not o.hide_render and not o.hide_viewport and (o.name.startswith(('ORDAX','saloon')) or 'wheel' in o.name.lower()):
        worlds[o]=wm(o);parts.append(o)
for o in parts:o.parent=None;o.matrix_world=worlds[o];coll.objects.link(o)
for o in set(bpy.data.objects)-existing-set(parts):bpy.data.objects.remove(o,do_unlink=True)
bpy.context.view_layer.update()
corners=[wm(o)@Vector(v) for o in parts for v in o.bound_box]
lo=Vector([min(v[i] for v in corners) for i in range(3)]);hi=Vector([max(v[i] for v in corners) for i in range(3)])
assert max(abs(a-b) for a,b in zip(hi-lo,plan['vehicle_asset_dimensions']))<.01
center=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z))
car=bpy.data.objects.new('GAMEPLAY | carro real V14 | teste Conceicao B38',None);coll.objects.link(car);car.rotation_mode='QUATERNION'
for o in parts:
    m=wm(o);m.translation-=center;o.parent=car;o.matrix_parent_inverse=Matrix.Identity(4);o.matrix_basis=m
car['boas_asset_id']='vehicle-existing-saloon-v14';car['boas_export']=False;car['boas_test_method']='replay cinemático de quatro apoios; não física dinâmica'
fps=25;speed=3;distance=0;frame=1
for i,p in enumerate(points):
    if i:distance+=math.dist(p['point'][:2],points[i-1]['point'][:2])
    frame=1+round(distance/speed*fps)
    f=Vector((*p['forward'],p['grade'])).normalized();s=Vector((-p['forward'][1],p['forward'][0],p['bank'])).normalized();up=s.cross(-f).normalized();s=(-f).cross(up).normalized()
    car.location=p['point'];car.rotation_quaternion=Matrix((s,-f,up)).transposed().to_quaternion()
    car.keyframe_insert(data_path='location',frame=frame);car.keyframe_insert(data_path='rotation_quaternion',frame=frame)
for layer in car.animation_data.action.layers:
    for strip in layer.strips:
        for bag in strip.channelbags:
            for fc in bag.fcurves:
                for k in fc.keyframe_points:k.interpolation='LINEAR'
scene.render.fps=fps;scene.frame_start=1;scene.frame_end=frame;scene.frame_set(1)
changed=[name for name,before in protected.items() if signature(scene.objects[name])!=before]
assert not changed,'Alteração indevida em componentes protegidos: '+str(changed)
out=root/'blender/salvador_lacerda_r30b38_binding_conceicao.blend';assert not out.exists()
bpy.ops.wm.save_as_mainfile(filepath=str(out))
# Leitura do componente salvo por biblioteca, sem abrir outra instância nem remontar toda a cidade.
copy=root/'artifacts/roads/r38/saved_readback.blend';shutil.copyfile(out,copy)
try:readback=api['inspect_file'](copy,[road.name,path.name,terrain.name,proxy.name])
finally:copy.unlink()
assert all(readback[o.name]==signature(o) for o in (road,path,terrain,proxy))
r={'source_before':source,'source_after':{'file':out.relative_to(root).as_posix(),'revision':'R30B.38','sha256':hashlib.file_digest(out.open('rb'),'sha256').hexdigest()},'classification':'ADAPT_LOCAL','binding':{'osm_way_id':421206045,'osm_node_id':7520527645,'before':old,'after':list(target),'visual_clearance_m':.18,'source_reference_unchanged':True,'reason':road['boas_binding_reason']},'city_visual_geometry_changed':False,'road_widths_changed':False,'terrain_visual_changed':False,'collision_changed':True,'collision_refinement':{'classification':'ERROR','vertices_before':proxy_vertices_before,'vertices_after':len(proxy.data.vertices),'iterations':iterations},'protected_components':len(protected),'protected_changes':changed,'saved_readback_components':list(readback),'validation':{'method':'sweep de apoio e envelope sobre pavimento; replay cinemático com asset existente','poses':len(points),'distance_xy_m':distance,'seconds':frame/fps,'proxy_samples':len(errors),'max_proxy_error_m':max(errors),'four_wheel_max_nonplanarity_m':max(p['wheel_residual'] for p in points),'vehicle_dimensions_asset_m':list(hi-lo),'track_probe_m':1.68,'track_status':'nominal_not_measured','steering_limit_probe_deg':35,'maximum_heading_slip_probe_deg':15,'dynamic_physics_tested':False,'full_route_approved':False},'excluded_wrong_level_runs':[[239,250]],'remaining':'Curvas/extremos sem envelope contínuo suficiente; não unir runs nem criar rua de retorno. Fit XY candidato, largura real null. Teste não cobre colisão com todos os edifícios, suspensão, tráfego ou gameplay no runtime.','runtime_exported':False}
(root/'docs/reports/blender/conceicao_binding_r30b38.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(r,ensure_ascii=False))
