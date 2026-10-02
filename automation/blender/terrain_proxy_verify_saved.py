"""Conferência após reabrir: colisor simplificado vs pista visível da Montanha."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];c=json.loads((root/'world/areas/mvp-centro-lacerda/production.json').read_text())
if c['world_source']['revision'] not in ('R30B.26','R30B.27','R30B.28'):raise RuntimeError('Revisão R30B26/R30B27/R30B28 esperada')
bpy.ops.wm.open_mainfile(filepath=str(root/c['world_source']['file']))
bpy.context.view_layer.update()
scene=bpy.context.scene
def tree(name):
    o=scene.objects[name];o.data.calc_loop_triangles();return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(t.vertices) for t in o.data.loop_triangles],all_triangles=True)
ground=tree(c['export']['road_object']);proxy=tree(c['export']['terrain_proxy'])
graph=json.loads((root/c['staging']['roads']).read_text());nodes={n['id']:n for n in graph['nodes']};ways={w['osm_way_id']:w for w in graph['ways']};samples=0;missing=[];errors=[];maxerror=0
def height(tree,p):
    q=tree.ray_cast(Vector((p.x,p.y,160)),Vector((0,0,-1)),350)[0];return q.z if q else None
for e in graph['edges']:
    if 'Montanha' not in (ways[e['osm_way_id']].get('name') or '') and e['id']!='way-231091555-seg-5':continue
    a=Vector((*nodes[e['from']]['blender_xy'],0));b=Vector((*nodes[e['to']]['blender_xy'],0));d=b-a;length=d.length;side=Vector((-d.y,d.x,0)).normalized();steps=max(1,math.ceil(length/1.5))
    for i in range(steps+1):
        for offset in [-.84,0,.84]:
            p=a.lerp(b,i/steps)+side*offset;visual=height(ground,p);collision=height(proxy,p);samples+=1
            if visual is None or collision is None:missing.append({'edge':e['id'],'xy':list(p.to_2d()),'visual':visual,'collision':collision});continue
            delta=abs(visual-collision);maxerror=max(maxerror,delta)
            if delta>.10:errors.append({'edge':e['id'],'xy':list(p.to_2d()),'error_m':delta})
r={'source':c['world_source'],'reopened':True,'samples':samples,'missing_support_samples':len(missing),'maximum_visual_collision_delta_m':maxerror,'review_threshold_m':.10,'samples_above_threshold':len(errors),'errors':errors,'missing':missing,'status':'pass_geometric_support_only' if not missing and not errors else 'NEEDS_REVIEW','dynamic_physics_tested':False,'runtime_exported':False}
(root/'docs/reports/blender/terrain_proxy_verify.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8')
for w in bpy.context.window_manager.windows:
    for area in w.screen.areas:
        if area.type=='VIEW_3D':
            target=Vector((-165,-172,58));eye=Vector((-192,-195,82));v=area.spaces.active.region_3d;v.view_location=target;v.view_distance=(eye-target).length;v.view_rotation=(target-eye).to_track_quat('-Z','Y');v.view_perspective='PERSP';v.update()
print(json.dumps({k:v for k,v in r.items() if k not in ('errors','missing')},ensure_ascii=False))
