"""Inputs no controller B82 e poses ao vivo; não inventa entrada do Mercado."""
import bpy,json,math,runpy,sys,os,time,traceback
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/world'))
from lacerda_gameplay_proxy import ProxyController
cfg=json.loads((ROOT/'world/areas/mvp-centro-lacerda/lacerda-gameplay-proxy.json').read_text(encoding='utf8'))
assert Path(bpy.data.filepath).resolve()==(ROOT/cfg['scene_file']).resolve()
assert not bpy.app.driver_namespace.get('boas_current_route_test'),'Teste já ativo'
old_scene=bpy.context.window.scene
module=runpy.run_path(str(ROOT/'automation/blender/play_lacerda_gameplay_proxy.py'),run_name='__main__')
runpy.run_path(str(ROOT/'automation/blender/repair_proxy_ground_visibility.py'),init_globals={'BOAS_CAPTURE':False})
scene=bpy.data.scenes[cfg['scene_name']];bpy.context.window.scene=scene
area=next(a for a in bpy.context.screen.areas if a.type=='VIEW_3D');space=area.spaces.active;rv=space.region_3d
old_view=(rv.view_location.copy(),rv.view_rotation.copy(),rv.view_distance,rv.view_perspective)
dynamic=[o for o in scene.objects if o.get('boas_proxy_dynamic')]
poses={o.name:o.location.copy() for o in dynamic}
player=bpy.data.objects['B82 | personagem proxy'];old_hidden=player.hide_get();player.hide_set(True)
controller=ProxyController(cfg);yaw=math.pi;frames=0;max_pose_error=0.;max_carry_error=0.;milestones=[];phase='spawn';start=time.monotonic()
OUT=ROOT/'docs/reports/blender/lacerda-current-playtest';OUT.mkdir(parents=True,exist_ok=True)
report={'status':'RUNNING','pid':os.getpid(),'fixed_dt':1/60,'display_acceleration':10,'physics_scope':'B82 proxy OBB/floors only; not collision against full historical visual geometry','market_entrance_connector':'NOT_IMPLEMENTED_NOT_TESTABLE','engine_certified':False,'geometry_changed':False,'saved':False}

def camera():
    angle=cfg['local_frame']['angle']+yaw;direction=Vector((math.cos(angle),math.sin(angle),0))
    eye=module['world'](controller.player)+Vector((0,0,1.63));rv.view_perspective='PERSP';rv.view_rotation=direction.to_track_quat('-Z','Y');rv.view_distance=1.;rv.view_location=eye+direction;area.tag_redraw()

def milestone(tag):
    module['sync'](controller);scene.view_layers[0].update();camera()
    capture=runpy.run_path(str(ROOT/'automation/blender/capture_current_map_view.py'),init_globals={'BOAS_CAPTURE_FILENAME':'playtest-'+tag+'.png'})['report']
    milestones.append({'tag':tag,'frame':frames,'position':controller.player[:],'car_z':controller.car_z,'mode':controller.mode,'screenshot':capture.get('screenshot'),'capture_error':capture.get('capture_error')})

def walk(points):
    global yaw
    for point in points:
        for _ in range(20000):
            dx,dy=point[0]-controller.player[0],point[1]-controller.player[1];dist=math.hypot(dx,dy)
            if dist<.04:break
            yaw=math.atan2(dy,dx);scale=min(dist,2.5/60)/dist;before=controller.player[:]
            controller.update(1/60);controller.move(dx*scale,dy*scale,0.)
            assert controller.blocked(controller.player) is None,'Penetração no proxy'
            assert controller.player!=before,'Bloqueio: '+controller.message
            yield None
        else:raise RuntimeError('Controle de rota não alcançado')

def dock(level):
    global max_carry_error
    assert controller.request(),'Pedido recusado'
    for i in range(2000):
        previous=controller.car_z;controller.update(1/60)
        if controller.car_z!=previous:
            assert controller.openness==0.,'Movimento com portas abertas'
            assert controller.in_cabin(),'Passageiro fora da cabine durante viagem'
            max_carry_error=max(max_carry_error,abs(controller.player[2]-controller.car_z-.015))
        yield None
        if i==400 and level=='lower':yield 'descending'
        if controller.mode=='OPEN' and controller.station==level:return
    raise RuntimeError('Desembarque não alcançado')

def sequence():
    global phase
    yield 'spawn'
    phase='upper_lobby_to_door';yield from walk(cfg['upper_route'])
    assert controller.request()
    for _ in range(61):controller.update(1/60);yield None
    assert controller.mode=='OPEN'
    phase='boarding';yield from walk([[0,0]]);yield 'upper_cabin'
    phase='descent';yield from dock('lower');yield 'lower_docked'
    phase='lower_lobby_to_cairu';yield from walk(cfg['lower_route']);yield 'cairu'
    phase='return_to_cabin';yield from walk(list(reversed(cfg['lower_route']))+[[0,0]])
    phase='ascent';yield from dock('upper')
    phase='return_to_spawn';yield from walk(list(reversed(cfg['upper_route'])));yield 'upper_return'
    assert math.dist(controller.player[:2],cfg['spawn'][:2])<.05

iterator=sequence()

def finish(status,error=None):
    report.update({'status':status,'phase':phase,'simulation_frames':frames,'wall_seconds':time.monotonic()-start,'maximum_live_player_pose_error':max_pose_error,'maximum_passenger_relative_z_error':max_carry_error,'events':controller.events,'milestones':milestones,'market_route_approved':False,'error':error})
    for o in dynamic:o.location=poses[o.name]
    player.hide_set(old_hidden);bpy.context.window.scene=old_scene
    rv.view_location,rv.view_rotation,rv.view_distance,rv.view_perspective=old_view
    bpy.app.driver_namespace.pop('boas_current_route_test',None)
    (OUT/'live.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

def tick():
    global frames,max_pose_error
    try:
        assert bpy.context.window.scene==scene,'Cena alterada durante teste'
        for _ in range(30):
            tag=next(iterator);frames+=1
            if tag:milestone(tag)
        module['sync'](controller);scene.view_layers[0].update();camera()
        max_pose_error=max(max_pose_error,(player.matrix_world.translation-module['world'](controller.player)).length)
        assert max_pose_error<1e-4,'Pose do personagem dessincronizada'
        report.update({'phase':phase,'simulation_frames':frames,'mode':controller.mode})
        (OUT/'progress.json').write_text(json.dumps(report,ensure_ascii=False),encoding='utf8')
        return .05
    except StopIteration:finish('PASS_LIVE_BLENDER_PROXY_ONLY');return None
    except Exception:finish('FAIL',traceback.format_exc());return None

bpy.app.driver_namespace['boas_current_route_test']=tick
bpy.app.timers.register(tick,first_interval=.1)
print(json.dumps({'started':True,'pid':os.getpid(),'scope':'Tomé–Cairu and return; Mercado not implemented','accelerated_display':True}))
