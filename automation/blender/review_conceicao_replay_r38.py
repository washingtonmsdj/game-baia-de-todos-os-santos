"""Executa replay local em tempo real e confere poses interpoladas no Blender."""
import bpy,json,time,math,runpy,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];scene=bpy.context.scene
assert Path(bpy.data.filepath).name=='salvador_lacerda_r30b38_binding_conceicao.blend'
report_path=root/'docs/reports/blender/conceicao_binding_r30b38.json';report=json.loads(report_path.read_text())
c=json.loads((root/'world/areas/mvp-centro-lacerda/production.json').read_text())
wm=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'))['world_matrix']
terrain=scene.objects[c['export']['road_object']];me=terrain.data;me.calc_loop_triangles()
a=np.empty(len(me.vertices)*3,dtype=np.float32);me.vertices.foreach_get('co',a);M=np.array(wm(terrain));world=a.reshape(-1,3)@M[:3,:3].T+M[:3,3]
a=np.empty(len(me.loop_triangles)*3,dtype=np.int32);me.loop_triangles.foreach_get('vertices',a);tris=a.reshape(-1,3)
tree=BVHTree.FromPolygons(world.tolist(),tris.tolist(),all_triangles=True)
car=scene.objects['GAMEPLAY | carro real V14 | teste Conceicao B38']
plan=json.loads((root/'artifacts/roads/r38/driveable_plan.json').read_text());points=next(p for p in plan['paths'] if p['start_index']==57)['points']
errors=[];missing=0;overspeed=0;prior=None;max_step=0
# Todos os frames, incluindo posições entre keyframes, antes do playback visível.
for frame in range(scene.frame_start,scene.frame_end+1):
    scene.frame_set(frame);matrix=wm(car)
    p=matrix.translation
    if prior is not None:max_step=max(max_step,(p-prior).length)
    prior=p.copy()
    for x,y in [(-.84,-1.61),(.84,-1.61),(-.84,1.61),(.84,1.61)]:
        q=matrix@Vector((x,y,0));h=tree.ray_cast(Vector((q.x,q.y,q.z+.5)),Vector((0,0,-1)),1)[0]
        if h is None:missing+=1
        else:errors.append(abs(q.z-h.z))
assert not missing,'Apoio perdido em pose interpolada'
assert max(errors)<.13,'Torção/interpolação além do limite geométrico candidato'
scene.frame_set(1)
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        rv=area.spaces.active.region_3d;rv.view_location=car.location;rv.view_distance=18
        rv.view_rotation=(Vector((-10,-10,8))).to_track_quat('Z','Y');area.spaces.active.shading.type='MATERIAL'
        break
state={'started':time.monotonic(),'ticks':0,'last_frame':1,'error':None}
duration=(scene.frame_end-1)/scene.render.fps
def advance():
    try:
        elapsed=time.monotonic()-state['started'];frame=min(scene.frame_end,1+round(elapsed*scene.render.fps));scene.frame_set(frame);state['last_frame']=frame;state['ticks']+=1
        for area in bpy.context.screen.areas:
            if area.type=='VIEW_3D':area.spaces.active.region_3d.view_location=car.location;area.tag_redraw()
        if elapsed<duration:return .08
        report['validation']['interpolated_frames']=scene.frame_end
        report['validation']['interpolated_wheel_samples']=len(errors)
        report['validation']['interpolated_missing_support']=missing
        report['validation']['interpolated_max_support_error_m']=max(errors)
        report['validation']['maximum_frame_displacement_m']=max_step
        report['validation']['visible_replay']={'completed':True,'wall_seconds':elapsed,'ticks':state['ticks'],'last_frame':frame,'dynamic_physics':False}
        report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
        (root/'artifacts/roads/r38/replay_complete.json').write_text(json.dumps(report['validation'],ensure_ascii=False,indent=2),encoding='utf8')
        return None
    except Exception as e:
        (root/'artifacts/roads/r38/replay_error.json').write_text(str(e),encoding='utf8');return None
bpy.app.timers.register(advance,first_interval=.08)
print(json.dumps({'frames_checked':scene.frame_end,'wheel_samples':len(errors),'max_support_error_m':max(errors),'visible_replay_started':True,'duration_seconds':duration}))
