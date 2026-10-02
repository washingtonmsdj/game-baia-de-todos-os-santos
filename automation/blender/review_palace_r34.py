"""Comparação visual na única instância; render CPU e cena temporária."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector,Matrix
root=Path(__file__).resolve().parents[2];out=root/'artifacts/palacio-rio-branco';source=bpy.context.scene
report=json.loads((root/'docs/reports/blender/palacio_rio_branco_r30b34.json').read_text(encoding='utf8'))
T=Matrix(report['palace']['frame_world'])
review=bpy.data.scenes.new('REVIEW TEMP | Palácio R34');review.render.engine='CYCLES';review.cycles.device='CPU';review.cycles.samples=8;review.cycles.use_denoising=True
review.render.resolution_x=960;review.render.resolution_y=720;review.render.resolution_percentage=100;review.view_settings.view_transform='AgX'
world=bpy.data.worlds.new('REVIEW TEMP | luz R34');world.use_nodes=True;review.world=world
bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs['Color'].default_value=(.70,.78,.84,1);bg.inputs['Strength'].default_value=.60
names=set(report['created_objects']);names.add('MVP | terreno corrigido | colisão estática')
if report.get('galleries'):names.update(report['galleries']['created_objects'])
for name in names:
    o=source.objects.get(name)
    if o and not o.hide_render:review.collection.objects.link(o)
light=bpy.data.lights.new('REVIEW TEMP | sol R34','SUN');light.energy=2.5;light.angle=.18
sun=bpy.data.objects.new(light.name,light);review.collection.objects.link(sun);sun.rotation_euler=(.75,-.30,-.90)
camera=bpy.data.cameras.new('REVIEW TEMP | camera R34');cam=bpy.data.objects.new(camera.name,camera);review.collection.objects.link(cam);review.camera=cam;camera.lens=47;camera.clip_end=1000
views=[('frente',T@Vector((0,65,10)),T@Vector((0,-3,13))),('lateral',T@Vector((-59,28,31)),T@Vector((-3,-11,11))),('galerias',Vector((-72,77,83)),Vector((3,4,65)))]
if report.get('galleries'):
    for s in report['galleries']['segments']:
        p=Vector(s['origin_world']);u=Vector(s['along_world']);n=Vector(s['outward_world']);L=s['length_from_existing_controls_m']
        target=p+u*(L*.5)+Vector((0,0,3.6));pos=target+n*max(26,L*1.4)+Vector((0,0,9))
        views.append(('galeria_'+s['name'].lower().replace('á','a'),pos,target))
if globals().get('BOAS_REVIEW_VIEWS'):views=[v for v in views if v[0] in BOAS_REVIEW_VIEWS]
try:
    bpy.context.window.scene=review
    for name,pos,target in views:
        cam.location=pos;cam.rotation_euler=(target-pos).to_track_quat('-Z','Y').to_euler();review.render.filepath=str(out/f'r30b34_{name}.png');bpy.ops.render.render(write_still=True)
finally:
    bpy.context.window.scene=source
    for o in (sun,cam):bpy.data.objects.remove(o,do_unlink=True)
    bpy.data.scenes.remove(review)
    for table,data in ((bpy.data.worlds,world),(bpy.data.cameras,camera),(bpy.data.lights,light)):
        if data.users==0:table.remove(data)
print(json.dumps({'views':[f'artifacts/palacio-rio-branco/r30b34_{v[0]}.png' for v in views]}))
