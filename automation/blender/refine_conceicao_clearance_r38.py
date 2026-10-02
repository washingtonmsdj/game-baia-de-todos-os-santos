"""Ajusta suavemente 3,5 cm do percurso de teste, dentro do pavimento existente."""
import bpy,json,runpy,math,hashlib,shutil,numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];scene=bpy.context.scene
assert Path(bpy.data.filepath).name=='salvador_lacerda_r30b38_binding_conceicao.blend'
api=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));wm=api['world_matrix']
c=json.loads((root/'world/areas/mvp-centro-lacerda/production.json').read_text());terrain=scene.objects[c['export']['road_object']];me=terrain.data;me.calc_loop_triangles()
a=np.empty(len(me.vertices)*3,dtype=np.float32);me.vertices.foreach_get('co',a);M=np.array(wm(terrain));world=a.reshape(-1,3)@M[:3,:3].T+M[:3,3]
a=np.empty(len(me.loop_triangles)*3,dtype=np.int32);me.loop_triangles.foreach_get('vertices',a);tris=a.reshape(-1,3)
tree=BVHTree.FromPolygons(world.tolist(),tris.tolist(),all_triangles=True)
slots={i for i,m in enumerate(me.materials) if m and m.name in c['export']['road_materials']}
car=scene.objects['GAMEPLAY | carro real V14 | teste Conceicao B38'];path=scene.objects['GAMEPLAY | Conceicao | percurso parcial B38']
plan=json.loads((root/'artifacts/roads/r38/driveable_plan.json').read_text());points=next(p for p in plan['paths'] if p['start_index']==57)['points']
distance=0;corrections=[]
for i,p in enumerate(points):
    if i:distance+=math.dist(p['point'][:2],points[i-1]['point'][:2])
    frame=1+round(distance/3*25)
    if i<len(points)-12:continue
    t=(i-(len(points)-12))/11;offset=.035*t*t*(3-2*t)
    f=np.array(p['forward']);side=np.array([-f[1],f[0]]);xy=np.array(p['point'][:2])+side*offset
    wheel=[]
    for u,v in [(-1.61,-.84),(-1.61,.84),(1.61,-.84),(1.61,.84)]:
        q=xy+f*u+side*v;h,n,idx,d=tree.ray_cast(Vector((*q,150)),Vector((0,0,-1)),350)
        assert h is not None and me.loop_triangles[idx].material_index in slots and n.z>.65
        wheel.append(h.z)
    mean=sum(wheel)/4;grade=((wheel[2]+wheel[3])-(wheel[0]+wheel[1]))/6.44;bank=((wheel[1]+wheel[3])-(wheel[0]+wheel[2]))/3.36
    fw=Vector((*f,grade)).normalized();sx=Vector((*side,bank)).normalized();up=sx.cross(-fw).normalized();sx=(-fw).cross(up).normalized()
    car.location=(*xy,mean);car.rotation_quaternion=Matrix((sx,-fw,up)).transposed().to_quaternion()
    car.keyframe_insert(data_path='location',frame=frame);car.keyframe_insert(data_path='rotation_quaternion',frame=frame)
    path.data.splines[0].points[i].co=(*xy,mean,1)
    corrections.append({'pose':i,'frame':frame,'offset_m':offset,'position':[float(xy[0]),float(xy[1]),mean]})
path['boas_clearance_adaptation']='ADAPT_LOCAL: rampa suave até 3,5 cm nos últimos 12 apoios, dentro do asfalto existente, para retirar contato do envelope com contenção. Nenhuma alteração de geografia/largura.'
for layer in car.animation_data.action.layers:
    for strip in layer.strips:
        for bag in strip.channelbags:
            for fc in bag.fcurves:
                for kp in fc.keyframe_points:kp.interpolation='LINEAR'
scene.frame_set(1)
output=Path(bpy.data.filepath);bpy.ops.wm.save_as_mainfile(filepath=str(output))
temp=root/'artifacts/roads/r38/clearance_readback.blend';shutil.copyfile(output,temp)
try:
    readback=api['inspect_file'](temp,[path.name]);assert readback[path.name]==api['signature'](path)
finally:temp.unlink()
rp=root/'docs/reports/blender/conceicao_binding_r30b38.json';r=json.loads(rp.read_text());r['source_after']['sha256']=hashlib.file_digest(output.open('rb'),'sha256').hexdigest()
r['validation']['initial_body_clearance']=r['validation'].pop('terrain_body_clearance')
r['validation']['local_clearance_adaptation']={'classification':'ADAPT_LOCAL','maximum_xy_shift_m':.035,'reason':'Contato de até 5,5 mm do envelope superior com a contenção; trajetória ajustada dentro do pavimento sem mover rua/parede.','wheel_support_rechecked':True,'poses':corrections,'saved_curve_readback':True}
r['validation'].pop('visible_replay',None)
rp.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8')
(root/'artifacts/roads/r38/replay_complete.json').unlink(missing_ok=True)
print(json.dumps({'saved':output.name,'corrected_poses':len(corrections),'maximum_xy_shift_m':.035}))
