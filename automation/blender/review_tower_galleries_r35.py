"""Três vistas focadas, na sessão visível, para conferir encaixe/profundidade."""
import bpy,json,math
from pathlib import Path
from mathutils import Matrix,Vector
root=Path(__file__).resolve().parents[2];out=root/'artifacts/palacio-rio-branco';source=bpy.context.scene
r=json.loads((root/'docs/reports/blender/torre_galerias_r30b35.json').read_text(encoding='utf8'));r34=json.loads((root/'docs/reports/blender/palacio_rio_branco_r30b34.json').read_text(encoding='utf8'));R=Matrix(r['tower_alignment']['rotation_world'])
review=bpy.data.scenes.new('REVIEW TEMP | Apoio e galerias R35');review.render.engine='CYCLES';review.cycles.device='CPU';review.cycles.samples=4;review.cycles.use_denoising=True;review.render.resolution_x=720;review.render.resolution_y=540;review.render.resolution_percentage=100;review.view_settings.view_transform='AgX'
world=bpy.data.worlds.new('REVIEW TEMP | R35 luz');world.use_nodes=True;review.world=world;bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs['Color'].default_value=(.72,.78,.84,1);bg.inputs['Strength'].default_value=.5
names=set(r34['created_objects']+r34['galleries']['created_objects']+r['created_objects']+r['tower_alignment']['objects']+[r['terrain_names'][0]])
for o in source.objects:
    if o.type in ('MESH','CURVE','FONT') and (o.get('boas_location_id')=='elevador-lacerda' or any(c.name.startswith(('11 ELEVADOR','12 LACERDA','30 LACERDA','31 LACERDA')) for c in o.users_collection) or o.name.startswith('CALIBRADO | passarela piso') or o.name.startswith('CALIBRADO | passarela cobertura')):names.add(o.name)
for name in names:
    o=source.objects.get(name)
    if o and not o.hide_render and not all(c.hide_render for c in o.users_collection):review.collection.objects.link(o)
light=bpy.data.lights.new('REVIEW TEMP | R35 sol','SUN');light.energy=2.2;light.angle=.16;sun=bpy.data.objects.new(light.name,light);review.collection.objects.link(sun);sun.rotation_euler=(.65,-.4,-.9)
camera=bpy.data.cameras.new('REVIEW TEMP | R35 camera');cam=bpy.data.objects.new(camera.name,camera);review.collection.objects.link(cam);review.camera=cam;camera.lens=40;camera.clip_end=1200
views=[('apoio',R@Vector((-62,-14,44)),R@Vector((-12,4.25,56)))]
if globals().get('SUPPORT_ONLY',False):views.append(('conjunto',R@Vector((-128,70,50)),R@Vector((-32,4.25,48))))
for s in r['galleries']['segments']:
    p,u,n=Vector(s['origin_world']),Vector(s['along_world']),Vector(s['outward_world']);x=s['length_from_existing_controls_m']/(2*s['arch_count'])
    pos=p+u*(x+.25)+n*7+Vector((0,0,2.4));target=p+u*x-n*1.7+Vector((0,0,2.6))
    if not globals().get('SUPPORT_ONLY',False):views.append(('interior_'+s['name'].lower().replace('á','a'),pos,target))
try:
    bpy.context.window.scene=review
    for name,pos,target in views:
        camera.lens=24 if name=='conjunto' else 40
        cam.location=pos;cam.rotation_euler=(target-pos).to_track_quat('-Z','Y').to_euler();review.render.filepath=str(out/f'r30b35_{name}.png');bpy.ops.render.render(write_still=True)
finally:
    bpy.context.window.scene=source
    for o in (sun,cam):bpy.data.objects.remove(o,do_unlink=True)
    bpy.data.scenes.remove(review)
    for table,data in ((bpy.data.worlds,world),(bpy.data.cameras,camera),(bpy.data.lights,light)):
        if not data.users:table.remove(data)
print(json.dumps({'views':[f'artifacts/palacio-rio-branco/r30b35_{v[0]}.png' for v in views]}))
