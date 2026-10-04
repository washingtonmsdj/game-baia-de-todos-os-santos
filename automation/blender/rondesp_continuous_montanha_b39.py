"""Percurso contínuo pela Montanha com curvas e verificação de todos os frames."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector,Quaternion
from mathutils.bvhtree import BVHTree
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
rp=r/'docs/reports/blender/rondesp_driver_review_b39.json';report=json.loads(rp.read_text(encoding='utf8'))
audit=json.loads((r/'docs/reports/blender/rondesp_network_audit_b38.json').read_text(encoding='utf8'))
turns=json.loads((r/'artifacts/roads/rondesp/turns_baseline.json').read_text(encoding='utf8'))['turns']
lookup={(t['from'],t['to']):t for t in turns if not t['issues']}
rows={p['edge_id']:p for p in audit['poses'] if p['full_segment_clear']}
range_ids={p['edge_id'] for p in report['route_ranges']}
chain=[f'way-1075624439-seg-{i}' for i in range(8)]
assert all(e in rows and e in range_ids for e in chain)
assert all((a,b) in lookup for a,b in zip(chain,chain[1:]))
path=[]
for i,edge in enumerate(chain):
    samples=rows[edge]['samples'];assert rows[edge]['direction']=='forward'
    a=Vector(samples[0]['location']);b=Vector(samples[-1]['location']);d=b-a
    def fraction(p):return (Vector(p)-a).dot(d)/d.length_squared
    lo=fraction(lookup[chain[i-1],edge]['poses'][-1]['location']) if i else 0.
    hi=fraction(lookup[edge,chain[i+1]]['poses'][0]['location']) if i<len(chain)-1 else 1.
    assert lo<=hi,'Arcos se sobrepõem; não costurar por teleporte'
    path.extend(p for p in samples if lo-.001<=fraction(p['location'])<=hi+.001)
    if i<len(chain)-1:path.extend(lookup[edge,chain[i+1]]['poses'])
assert len(path)>20
actor=s.objects['QA | RONDESP | veiculo na pista'];old_action=actor.animation_data.action;old_action.use_fake_user=True
old_action.name='QA | Rondesp | segmentos independentes B39';actor.animation_data.action=None
frame=241;distance=0.;prior=None
for p in path:
    if prior is not None:
        step=math.dist(prior,p['location']);assert step<2.,'Descontinuidade espacial';distance+=step;frame+=max(1,round(step*24/3.))
    actor.location=p['location'];actor.rotation_quaternion=p['rotation']
    actor.keyframe_insert(data_path='location',frame=frame);actor.keyframe_insert(data_path='rotation_quaternion',frame=frame);prior=p['location']
actor.animation_data.action.name='QA | Rondesp | Montanha continua B39'
for layer in actor.animation_data.action.layers:
    for strip in layer.strips:
        for bag in strip.channelbags:
            for f in bag.fcurves:
                for key in f.keyframe_points:key.interpolation='LINEAR'
s.frame_start=241;s.frame_end=frame
c=json.loads((r/'world/areas/mvp-centro-lacerda/production.json').read_text(encoding='utf8'))
terrain=s.objects[c['export']['road_object']];terrain.data.calc_loop_triangles()
ground=BVHTree.FromPolygons([terrain.matrix_world@v.co for v in terrain.data.vertices],[list(t.vertices) for t in terrain.data.loop_triangles],all_triangles=True)
proxy=s.objects[c['export']['terrain_proxy']];proxy.data.calc_loop_triangles()
ptree=BVHTree.FromPolygons([proxy.matrix_world@v.co for v in proxy.data.vertices],[list(t.vertices) for t in proxy.data.loop_triangles],all_triangles=True)
errors=[];proxy_errors=[];missing=0;maxstep=0;previous=None
for f in range(241,frame+1):
    s.frame_set(f);m=actor.matrix_world
    if previous is not None:maxstep=max(maxstep,(m.translation-previous).length)
    previous=m.translation.copy()
    for contact in audit['vehicle_contacts_asset_local']:
        p=m@Vector(contact);q=ground.ray_cast(p+Vector((0,0,.5)),Vector((0,0,-1)),1.)[0]
        pq=ptree.ray_cast(p+Vector((0,0,.5)),Vector((0,0,-1)),1.)[0]
        if q is None:missing+=1
        else:
            errors.append(abs(q.z-p.z))
            if pq is not None:proxy_errors.append(abs(q.z-pq.z))
assert not missing and max(errors)<.13,'Apoio interpolado não aceito; manter revisão pendente'
s.frame_set(241)
continuous={'edge_ids':chain,'turns':7,'points':len(path),'frames':frame-240,'frame_start':241,'frame_end':frame,'distance_m':distance,
            'wheel_samples':len(errors),'missing_support':missing,'maximum_wheel_plane_error_m':max(errors),
            'maximum_collision_visual_error_m':max(proxy_errors,default=None),'maximum_frame_step_m':maxstep,
            'method':'Percurso cinemático contínuo, 3 m/s nominais, quatro apoios em todos os frames. Sem teleporte entre os oito segmentos.','approved':False,'dynamic_physics':False,'obstacle_curve_sweep_pending':True}
report['continuous_preview']=continuous
report['preview_range']={'name':'Montanha — oito segmentos contínuos','start':241,'end':frame}
report['driver_view_review']='reviewed: Montanha, Rua Chile e Av. Lafayete Coutinho; câmera interna vê pista e bordas. Arte urbana e demais pontos permanecem candidatos.'
report['source_reopened']=False
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
report['source_after']['sha256']=hashlib.sha256((r/report['source_after']['file']).read_bytes()).hexdigest()
rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(continuous,ensure_ascii=False))