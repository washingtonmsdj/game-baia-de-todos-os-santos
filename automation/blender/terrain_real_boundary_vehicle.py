"""Replay cinemático do carro V14 no trecho real reparado; artefato de teste."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
root=Path(__file__).resolve().parents[2];c=json.loads((root/'world/areas/mvp-centro-lacerda/production.json').read_text())
if c['world_source']['revision']!='R30B.30' or Path(bpy.data.filepath).resolve()!=(root/c['world_source']['file']).resolve():raise RuntimeError('Fonte R30B30 esperada')
r=json.loads((root/'docs/reports/blender/terrain_real_boundary_verify.json').read_text())
if r['status']!='pass_boundary_ground_support':raise RuntimeError('Apoio não passou')
scene=bpy.context.scene;name='TESTE | TERRENO | VEICULO V14'
if bpy.data.collections.get(name):raise RuntimeError('Não duplicar veículo')
vehicle=root/'automation/blender/ordax_car_realistic_v14_reference_cleanup.blend'
with bpy.data.libraries.load(str(vehicle),link=False) as (src,dst):dst.objects=list(src.objects)
coll=bpy.data.collections.new(name);scene.collection.children.link(coll);parts=[]
for o in dst.objects:
    if o.type in {'MESH','CURVE'} and not o.hide_render and not o.hide_viewport and (o.name.startswith(('ORDAX','saloon')) or 'wheel' in o.name.lower()):coll.objects.link(o);parts.append(o)
    else:bpy.data.objects.remove(o,do_unlink=True)
bpy.context.view_layer.update();corners=[o.matrix_world@Vector(v) for o in parts for v in o.bound_box];lo=Vector(tuple(min(v[i] for v in corners) for i in range(3)));hi=Vector(tuple(max(v[i] for v in corners) for i in range(3)));offset=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z))
car=bpy.data.objects.new('TESTE | carro | conexão real Castro Alves',None);coll.objects.link(car);car.rotation_mode='QUATERNION'
for o in parts:
    world=o.matrix_world.copy();o.parent=car;o.matrix_world=world;o.location-=offset
poses=r['poses'];a=Vector((*poses[0]['center_xy'],0));b=Vector((*poses[-1]['center_xy'],0));f=(b-a).normalized();side=Vector((-f.y,f.x,0));frame=1;scene.render.fps=25
for pose in poses:
    zs=pose['wheel_heights'];back=(zs[0]+zs[1])/2;front=(zs[2]+zs[3])/2;left=(zs[0]+zs[2])/2;right=(zs[1]+zs[3])/2
    fw=Vector((f.x,f.y,(front-back)/3.22)).normalized();sx=Vector((side.x,side.y,(right-left)/1.68)).normalized();up=sx.cross(-fw).normalized()
    if up.z<0:up=-up
    sx=(-fw).cross(up).normalized();car.rotation_quaternion=Matrix((sx,-fw,up)).transposed().to_quaternion();car.location=(*pose['center_xy'],sum(zs)/4)
    car.keyframe_insert(data_path='location',frame=frame);car.keyframe_insert(data_path='rotation_quaternion',frame=frame);frame+=5
if car.animation_data and car.animation_data.action:
    for layer in car.animation_data.action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for fc in bag.fcurves:
                    for kp in fc.keyframe_points:kp.interpolation='LINEAR'
scene.frame_start=1;scene.frame_end=frame-5;car['boas_role']='terrain_test_vehicle';car['boas_asset_id']='vehicle-existing-saloon-v14';car['boas_test_method']='Apoio quatro rodas, replay cinemático; sem física de suspensão, sem aprovação de largura.'
evaluated=0
for at in range(1,scene.frame_end+1,5):scene.frame_set(at);bpy.context.view_layer.update();evaluated+=1
scene.frame_set(1)
for window in bpy.context.window_manager.windows:
    for area in window.screen.areas:
        if area.type=='VIEW_3D':
            rv=area.spaces.active.region_3d;target=car.matrix_world.translation.copy()+Vector((0,0,.8));eye=target+Vector((12,-12,10));rv.view_location=target;rv.view_distance=(target-eye).length;rv.view_rotation=(target-eye).to_track_quat('-Z','Y');rv.view_perspective='PERSP';rv.update()
out=root/'artifacts/terrain-vehicle/r30b30_boundary_vehicle_test.blend';out.parent.mkdir(parents=True,exist_ok=True);bpy.ops.wm.save_as_mainfile(filepath=str(out))
report={'source':c['world_source'],'test_file':out.relative_to(root).as_posix(),'test_file_sha256':hashlib.file_digest(out.open('rb'),'sha256').hexdigest(),'osm_edge_id':r['edge_id'],'asset_file':vehicle.relative_to(root).as_posix(),'visible_car_parts':len(parts),'dimensions_measured_m':list(hi-lo),'poses_evaluated':evaluated,'frames':scene.frame_end,'seconds':scene.frame_end/25,'kind':'kinematic Blender replay on actual OSM segment; not rigidbody, suspension, body clearance or traffic simulation','dynamic_physics_tested':False,'road_width_approved':False,'complete_circuit_approved':False,'source_file_modified':False}
(root/'docs/reports/blender/terrain_real_boundary_vehicle.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(report,ensure_ascii=False))
