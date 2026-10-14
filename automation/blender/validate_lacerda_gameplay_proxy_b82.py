"""Confere reabertura e equivalência de caixas/floors visíveis com o controller."""
import bpy,json,math,runpy,sys,os
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/reports/blender/lacerda-gameplay-proxy'
config=json.loads((ROOT/'world/areas/mvp-centro-lacerda/lacerda-gameplay-proxy.json').read_text(encoding='utf8'))
assert Path(bpy.data.filepath).resolve()==(ROOT/config['scene_file']).resolve()
scene=bpy.data.scenes[config['scene_name']];source=bpy.data.scenes['SALVADOR | ESBOCO OFICIAL']
sys.path.insert(0,str(ROOT/'tools/world'))
from lacerda_gameplay_proxy import validate_round_trip, ProxyController
from validate_lacerda_gameplay_proxy import validate
before=json.loads((OUT/'protected_original_components.json').read_text(encoding='utf8'))
sig=runpy.run_path(str(ROOT/'automation/blender/component_fingerprint.py'))['signature']
bpy.context.window.scene=source;source.view_layers[0].update();changed=[]
for name,value in before.items():
    ob=bpy.data.objects[name]
    try:actual=sig(ob)
    except RuntimeError:actual={'type':ob.type,'basis':[list(r) for r in ob.matrix_basis],'data':ob.data.name if ob.data else None}
    if actual!=value:changed.append(name)
assert not changed, str(changed)
bpy.context.window.scene=scene;scene.view_layers[0].update()
col=bpy.data.collections['GAMEPLAY_PROXY | Lacerda B82'];ids={o.get('boas_proxy_id'):o for o in col.objects}
checks=[]
for row in config['obstacles']:
    ob=ids[row['id']];center=ob.matrix_world.translation;a=config['local_frame']['angle'];c,s=math.cos(a),math.sin(a);origin=config['local_frame']['origin_xy']
    expected=Vector((origin[0]+c*row['center'][0]-s*row['center'][1],origin[1]+s*row['center'][0]+c*row['center'][1],row['center'][2]))
    error=(center-expected).length;size_error=max(abs(ob.dimensions[i]-row['size'][i]) for i in range(3))
    assert error<1e-4 and size_error<1e-4,(ob.name,error,size_error)
    checks.append({'object':ob.name,'center_error':error,'size_error':size_error})
floor_errors=[]
for row in config['floors']:
    ob=ids[row['id']];top=[v.co.z for v in ob.data.vertices[4:]]
    expected=[.09+x*row.get('slope',0.) for x in [-row['size'][0]/2,row['size'][0]/2,row['size'][0]/2,-row['size'][0]/2]]
    error=max(abs(x-y) for x,y in zip(top,expected));assert error<1e-5
    floor_errors.append({'object':ob.name,'top_profile_error':error})
assert all(o.get('status')=='GAMEPLAY_PROXY' and o.get('accuracy')=='APPROXIMATE' and o.get('replacement_required') for o in col.objects)
trip=validate_round_trip(config);interlocks=validate(config,trip)
module=runpy.run_path(str(ROOT/'automation/blender/play_lacerda_gameplay_proxy.py'),run_name='__main__')
controller=ProxyController(config)
# Poses reais da cabine e cápsula na mesma cena visível, não apenas números de JSON.
poses=[]
for tag,point in [('upper_ready',trip['trace'][0]),('descending',next(x for x in trip['trace'] if x['mode']=='TRAVELLING' and x['car_z']<35)),('cairu',max(trip['trace'],key=lambda x:math.dist(x['position'][:2],[0,0]) if x['position'][2]<10 else -1))]:
    controller.player=point['position'][:];controller.car_z=point['car_z'];module['sync'](controller);scene.view_layers[0].update()
    foot=bpy.data.objects['B82 | personagem proxy'].matrix_world.translation;floor=bpy.data.objects['B82 | cabin_floor'].matrix_world.translation
    if tag=='descending':assert abs(foot.z-floor.z-.09-.015)<1e-4
    poses.append({'tag':tag,'foot_world':list(foot),'cabin_floor_world':list(floor)})
controller=ProxyController(config);module['sync'](controller);scene.view_layers[0].update()
report={'revision':'R30B.82','source_reopened':True,'pid':os.getpid(),'historical_objects':len(before),
        'historical_components_changed':changed,'proxy_objects':len(col.objects),'obstacle_equivalence':checks,
        'floor_equivalence':floor_errors,'live_poses':poses,'round_trip':trip['status'],'interlocks':interlocks,
        'gameplay_status':'FUNCTIONAL_BLENDER_PROXY','historical_fidelity_resolved':False,'production_ready':False}
(OUT/'validation_b82.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'reopened':True,'historical_changed':len(changed),'boxes':len(checks),'floors':len(floor_errors),'round_trip':trip['status'],'interlocks':len(interlocks['cases'])}))
