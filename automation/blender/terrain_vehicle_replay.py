"""Teste geométrico com o asset real e replay contínuo na janela Blender.

Preserva a R30B23. O replay fica em uma revisão de teste separada, sem promoção
ao contrato. Não é simulação de suspensão, tráfego ou aprovação de largura real.
"""
import bpy,json,math,heapq,hashlib,itertools
from pathlib import Path
from collections import Counter
from mathutils import Vector,Matrix,Quaternion
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2]
c=json.loads((root/'world/areas/mvp-centro-lacerda/production.json').read_text())
if Path(bpy.data.filepath).resolve()!=(root/c['world_source']['file']).resolve():raise RuntimeError('Fonte ativa incorreta')
scene=bpy.context.scene;terrain=scene.objects[c['export']['road_object']];terrain.data.calc_loop_triangles()
ps=[terrain.matrix_world@v.co for v in terrain.data.vertices]
slots={i for i,m in enumerate(terrain.data.materials) if m and m.name in c['export']['road_materials']}
tree=BVHTree.FromPolygons(ps,[list(t.vertices) for t in terrain.data.loop_triangles if t.material_index in slots],all_triangles=True)
ground=BVHTree.FromPolygons(ps,[list(t.vertices) for t in terrain.data.loop_triangles],all_triangles=True)
def h(x,y):
    p=ground.ray_cast(Vector((x,y,160)),Vector((0,0,-1)),350)[0]
    return p.z if p else None
graph=json.loads((root/c['staging']['roads']).read_text());nodes={n['id']:n for n in graph['nodes']};ways={w['osm_way_id']:w for w in graph['ways']}
suffix=c['world_source']['revision'].lower().replace('.','')
audit=json.loads((root/f'docs/reports/blender/terrain_vehicle_audit_{suffix}.json').read_text())
covered={r['edge_id'] for r in audit['segments'] if all(s[2] is not None for s in r['samples']) and sum(s[3] is not None for s in r['samples'])/len(r['samples'])>=.95}
if bpy.data.collections.get('TESTE | TERRENO | VEICULO V14'):raise RuntimeError('Não duplicar veículo de teste; abrir fonte sem o replay')
# Load only actual visible car parts, never studio geometry/lights/cameras.
vehicle=root/'automation/blender/ordax_car_realistic_v14_reference_cleanup.blend'
with bpy.data.libraries.load(str(vehicle),link=False) as (src,dst):dst.objects=list(src.objects)
coll=bpy.data.collections.new('TESTE | TERRENO | VEICULO V14');scene.collection.children.link(coll)
parts=[]
for o in dst.objects:
    if o.type in {'MESH','CURVE'} and not o.hide_render and not o.hide_viewport and (o.name.startswith(('ORDAX','saloon')) or 'wheel' in o.name.lower()):coll.objects.link(o);parts.append(o)
    else:bpy.data.objects.remove(o,do_unlink=True)
bpy.context.view_layer.update()
corners=[o.matrix_world@Vector(v) for o in parts for v in o.bound_box];lo=Vector(tuple(min(p[i] for p in corners) for i in range(3)));hi=Vector(tuple(max(p[i] for p in corners) for i in range(3)));offset=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z))
car=bpy.data.objects.new('TESTE | carro | apoio de quatro rodas',None);coll.objects.link(car);car.rotation_mode='QUATERNION'
for o in parts:
    world=o.matrix_world.copy();o.parent=car;o.matrix_world=world; o.location-=offset
# Wheelbase is extracted from wheel/tire components, not a manufacturer claim.
wheelparts=[o for o in parts if 'wheel' in o.name.lower() or 'tire' in o.name.lower() or 'pneu' in o.name.lower()]
wheel_y=sorted({round(o.location.y,2) for o in wheelparts if abs(o.location.x)>.4})
wheelbase=max(wheel_y)-min(wheel_y) if len(wheel_y)>1 else None
halfbase=wheelbase/2 if wheelbase and 1.8<wheelbase<4.2 else 1.45
track=.84
metrics=Counter();tested=[];safe=set();frames=[];adj={}
for edge in graph['edges']:
    if edge['id'] not in covered:continue
    a=Vector((*nodes[edge['from']]['blender_xy'],0));b=Vector((*nodes[edge['to']]['blender_xy'],0));d=b-a;length=d.length
    if length<.01:continue
    f=d.normalized();side=Vector((-f.y,f.x,0));steps=math.ceil(length/1.5);poses=[];issues=[]
    for i in range(steps+1):
        p=a.lerp(b,i/steps);zs=[h(*(p+f*u+side*v).to_2d()) for u,v in [(-halfbase,-track),(-halfbase,track),(halfbase,-track),(halfbase,track)]]
        if any(z is None for z in zs):issues.append({'sample':i,'type':'wheel_support_missing'});metrics['wheel_support_missing']+=1;continue
        back=(zs[0]+zs[1])/2;front=(zs[2]+zs[3])/2;left=(zs[0]+zs[2])/2;right=(zs[1]+zs[3])/2
        fw=Vector((f.x,f.y,(front-back)/(2*halfbase))).normalized();sx=Vector((side.x,side.y,(right-left)/(2*track))).normalized();up=sx.cross(-fw).normalized()
        if up.z<0:up=-up
        sx=(-fw).cross(up).normalized();rotation=Matrix((sx,-fw,up)).transposed().to_quaternion();z=sum(zs)/4
        residual=max(abs(zs[j]-(z+(-halfbase if j<2 else halfbase)*(front-back)/(2*halfbase)+(-track if j%2==0 else track)*(right-left)/(2*track))) for j in range(4))
        if residual>.08:issues.append({'sample':i,'type':'four_wheel_nonplanar','residual_m':round(residual,4)});metrics['four_wheel_nonplanar']+=1
        if abs(front-back)/(2*halfbase)>.20:issues.append({'sample':i,'type':'pitch_review'});metrics['pitch_review']+=1
        poses.append((tuple((p.x,p.y,z)),tuple(rotation)))
    tested.append({'edge_id':edge['id'],'osm_way_id':edge['osm_way_id'],'name':ways[edge['osm_way_id']].get('name'),'length_m':length,'tested_poses':len(poses),'issues':issues})
    # Apoio encontrado não autoriza atravessar um degrau/cliff. Inclinações
    # permanecem alertas; torção acima de 20 cm bloqueia o replay geométrico.
    invalid=any(x['type']=='wheel_support_missing' or
                (x['type']=='four_wheel_nonplanar' and x['residual_m']>.20)
                for x in issues)
    tested[-1]['replay_allowed']=bool(poses) and not invalid
    tested[-1]['geometric_block_threshold_m']=.20
    if poses and not invalid:
        safe.add(edge['id'])
        if edge.get('access')=='restricted':continue
        # Uma aresta física pode admitir dois sentidos. Não criar outra rua:
        # derivar arcos de circulação da direção registrada no OSM.
        if edge['direction'] in ('forward','both'):
            arc={**edge,'traversal':'forward'}
            adj.setdefault(edge['from'],[]).append((edge['to'],length,arc,poses))
        if edge['direction'] in ('reverse','both'):
            arc={**edge,'from':edge['to'],'to':edge['from'],'traversal':'reverse'}
            reverse_poses=[(p,tuple(Quaternion(q)@Quaternion((0,0,1),math.pi))) for p,q in reversed(poses)]
            adj.setdefault(edge['to'],[]).append((edge['from'],length,arc,reverse_poses))
def path(start,end):
    counter=itertools.count();queue=[(0,next(counter),start,[])];visited=set()
    while queue:
        distance,_,node,route=heapq.heappop(queue)
        if node==end:return route
        if node in visited:continue
        visited.add(node)
        for other,length,e,poses in adj.get(node,[]):
            if other not in visited:heapq.heappush(queue,(distance+length,next(counter),other,route+[(e,poses)]))
    return None
# Main demonstrator tries the entire Montanha in its recorded direction, joined
# by actual graph edges. Missing support stops the itinerary, never teleports.
ordered=[e for e in graph['edges'] if e['osm_way_id'] in (1075624439,48846625,978481515)]
ordered.sort(key=lambda e:(0 if e['osm_way_id']==1075624439 else 1 if e['osm_way_id']==48846625 else 2,int(e['id'].rsplit('-',1)[-1])))
route=[];blocked=[];at=ordered[0]['from'] if ordered else None
for e in ordered:
    if e['id'] not in safe:blocked.append(e['id']);break
    start=e['to'] if e['direction']=='reverse' else e['from']
    end=e['from'] if e['direction']=='reverse' else e['to']
    link=path(at,start)
    if link is None:blocked.append(e['id']);break
    route+=link
    leg=next(x for x in adj[start] if x[2]['id']==e['id']);route.append((leg[2],leg[3]));at=end
frame=1;scene.render.fps=25;speed=5
for edge,poses in route:
    for position,rotation in poses:
        car.location=position;car.rotation_quaternion=rotation;car.keyframe_insert(data_path='location',frame=frame);car.keyframe_insert(data_path='rotation_quaternion',frame=frame);frame+=8
if car.animation_data and car.animation_data.action:
    action=car.animation_data.action
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for fc in bag.fcurves:
                    for kp in fc.keyframe_points:kp.interpolation='LINEAR'
scene.frame_start=1;scene.frame_end=max(2,frame-8);scene.frame_set(1)
car['boas_role']='terrain_test_vehicle';car['boas_asset_id']='vehicle-existing-saloon-v14';car['boas_test_method']='Quatro apoios na mesh de pista; replay cinemático. Sem física de suspensão.'
report={'source':c['world_source'],'test_kind':'four-wheel support sweep with existing vehicle asset and continuous kinematic Blender replay','dynamic_physics_tested':False,'terrain_changed':False,'widths_changed':False,'road_segments_tested':len(tested),'wheel_poses':sum(r['tested_poses'] for r in tested),'issue_counts':dict(metrics),'vehicle_dimensions_measured_m':list(hi-lo),'wheelbase_measured_m':wheelbase,'wheelbase_probe_m':2*halfbase,'wheelbase_status':'asset_geometry' if wheelbase and halfbase==wheelbase/2 else 'nominal_probe_not_verified','replay_route_edges':[e['id'] for e,p in route],'replay_blocked_edges':blocked,'replay_frames':scene.frame_end,'replay_seconds':scene.frame_end/25,'segments':tested,'approved':False}
directory=root/'artifacts/terrain-vehicle';directory.mkdir(parents=True,exist_ok=True)
output=directory/f'{suffix}_vehicle_test.blend';bpy.ops.wm.save_as_mainfile(filepath=str(output))
report['test_blend']=output.relative_to(root).as_posix();report['test_blend_sha256']=hashlib.file_digest(output.open('rb'),'sha256').hexdigest()
(root/f'docs/reports/blender/terrain_vehicle_replay_{suffix}.json').write_text(json.dumps(report,ensure_ascii=False,separators=(',',':')),encoding='utf8')
print(json.dumps({k:v for k,v in report.items() if k!='segments'},ensure_ascii=False))
