"""Apoio geométrico e replay de referência; sem aprovação física/pavimento."""
import bpy,json,numpy as np,math
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];scene=bpy.context.scene
audit=json.loads((root/'docs/reports/blender/rondesp_network_audit_b38.json').read_text(encoding='utf8'))
contacts=np.array(audit['vehicle_contacts_asset_local']);floor=float(audit['vehicle_floor_z'])
ground_objects=[scene.objects['MVP | terreno corrigido | colisão estática'],scene.objects['B62 | GAMEPLAY TERRAIN HQ | pavimento e costura limpa'],BOAS_NEW_GROUND]
trees=[]
for ob in ground_objects:
    me=ob.data;me.calc_loop_triangles()
    vertices=np.empty(len(me.vertices)*3,np.float32);me.vertices.foreach_get('co',vertices);vertices=vertices.reshape(-1,3)
    m=np.array(ob.matrix_world);vertices=vertices@m[:3,:3].T+m[:3,3]
    triangles=np.empty(len(me.loop_triangles)*3,np.int32);me.loop_triangles.foreach_get('vertices',triangles)
    trees.append(BVHTree.FromPolygons(vertices.tolist(),triangles.reshape(-1,3).tolist(),all_triangles=True))
def hit(x,y):
    points=[tree.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),400)[0] for tree in trees]
    points=[p for p in points if p is not None]
    return max(points,key=lambda p:p.z).z if points else None
old=scene.objects['QA | RONDESP | veiculo na pista']
car=bpy.data.objects.new('QA | RONDESP | trajetos de referencia B74',None);BOAS_QA_COLLECTION.objects.link(car)
car.instance_type='COLLECTION';car.instance_collection=old.instance_collection;car.rotation_mode='QUATERNION'
car['boas_role']='reference_traversal_only';car['boas_asset_id']='vehicle-rondesp-pickup'
camera=bpy.data.objects.new('QA | RONDESP | motorista expansao B74',bpy.data.cameras.new('QA | RONDESP | motorista expansao B74'));BOAS_QA_COLLECTION.objects.link(camera)
camera.parent=car;camera.location=(-.43,-.02,1.46);camera.rotation_euler=Vector((0,-1,-.035)).to_track_quat('-Z','Y').to_euler();camera.data.lens=24;camera.data.clip_start=.06;camera.data.clip_end=4000
camera['boas_eye_position_status']='candidate, preserved B39 convention';scene.camera=camera
frame=1000;runs=[];issues=[];details=[];sample_count=0;wheel_count=0;max_twist=0.;max_grade=0.;best=[]
for route in BOAS_ROUTES:
    if 'points' not in route:continue
    poses=[];start=frame;last_good=None;last_z=None;station=0.
    points=route['points'];ways=route['osm_way_ids']
    for segment,(a,b) in enumerate(zip(points,points[1:])):
        length=math.dist(a,b)
        if length<1e-8:continue
        direction=np.array(b)-a;direction/=length
        # Local -Y aponta à frente. Os quatro apoios vêm da biblioteca V25.
        angle=math.atan2(direction[0],-direction[1]);c,s=math.cos(angle),math.sin(angle)
        xy_rotation=np.array([[c,-s],[s,c]])
        for k in range(max(1,math.ceil(length))):
            t=k/max(1,math.ceil(length));xy=np.array(a)+(np.array(b)-a)*t
            wheel_xy=contacts[:,:2]@xy_rotation.T+xy;heights=[hit(*p) for p in wheel_xy]
            wheel_count+=4;sample_count+=1;flags=[]
            if any(z is None for z in heights):
                flags.append('wheel_ground_support_missing');last_good=None;last_z=None
            else:
                local=contacts[:,:2]@xy_rotation.T
                coefficients=np.linalg.lstsq(np.column_stack((local,np.ones(4))),heights,rcond=None)[0]
                residual=np.array(heights)-np.column_stack((local,np.ones(4)))@coefficients
                twist=float(np.max(abs(residual)));grade=float(abs(coefficients[:2]@direction));max_twist=max(max_twist,twist);max_grade=max(max_grade,grade)
                if twist>.08:flags.append('wheel_plane_residual_over_candidate_0_08m')
                if grade>.30:flags.append('grade_over_candidate_30pct')
                z=float(coefficients[2]-floor)
                if last_z is not None and abs(z-last_z)>.5:flags.append('station_height_step_over_candidate_0_5m')
                last_z=z
                n=Vector((-coefficients[0],-coefficients[1],1)).normalized()
                forward=Vector((direction[0],direction[1],float(coefficients[:2]@direction))).normalized();right=n.cross(forward).normalized()
                rotation=Matrix((right,-forward,n)).transposed().to_quaternion()
                pose={'location_id':route['location_id'],'osm_way_id':ways[segment],'xy':xy.tolist(),'location':[float(xy[0]),float(xy[1]),z],'rotation':list(rotation),'frame':frame,'flags':flags,'wheel_plane_residual_m':twist,'grade_candidate':grade}
                poses.append(pose)
                car.location=pose['location'];car.rotation_quaternion=rotation
                car.keyframe_insert(data_path='location',frame=frame);car.keyframe_insert(data_path='rotation_quaternion',frame=frame)
                if last_good is None and poses[:-1]:
                    poses[-2]['hold_after']=True
                last_good=pose
                if not flags:best.append(pose)
            if flags:issues.append({'location_id':route['location_id'],'osm_way_id':ways[segment],'xy':xy.tolist(),'flags':flags,'classification':'NEEDS_REVIEW'})
            station+=length/max(1,math.ceil(length));frame+=6
    if poses:
        poses[-1]['hold_after']=True
        runs.append({'location_id':route['location_id'],'start':start,'end':poses[-1]['frame'],'sampled_poses':len(poses),'widths_verified':route['widths_verified'],'direct_target_access_verified':False,'closest_target_distance_blender_units':route['target_boundary_distance_blender_units'],'approval':'pending_pavement_width_obstacles_physics'})
        scene.timeline_markers.new('B74 | '+route['location_id'],frame=start)
    details.extend(poses);frame+=240
if car.animation_data:
    for layer in car.animation_data.action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for curve in bag.fcurves:
                    hold={p['frame'] for p in details if p.get('hold_after')}
                    for key in curve.keyframe_points:key.interpolation='CONSTANT' if round(key.co.x) in hold else 'LINEAR'
scene.frame_end=max(scene.frame_end,frame);scene.render.fps=24
overview_frame=best[len(best)//2]['frame'] if best else 1000
result={'schema':'boas/rondesp-centro-b74-reference-probe-v1','vehicle':audit['vehicle'],'contacts_asset_local':contacts.tolist(),'routes':runs,'sampled_stations':sample_count,'wheel_rays':wheel_count,'issues':len(issues),'max_wheel_plane_residual_m':max_twist,'max_grade_candidate':max_grade,'dynamic_physics_tested':False,'pavement_widths_verified':False,'obstacle_sweep_done':False,'driver_camera':camera.name,'overview_frame':overview_frame,'production_ready':False,'method':'Apoios verticais sobre terreno original e candidato; eixos OSM não equivalem a pavimento/faixas.'}
folder=root/'docs/reports/blender/centro-expansion'
(folder/'rondesp_ground_probe_b74.json').write_text(json.dumps({'summary':result,'issues':issues,'poses':details},ensure_ascii=False)+'\n',encoding='utf8')
print(json.dumps(result,ensure_ascii=False))
