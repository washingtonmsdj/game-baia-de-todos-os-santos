"""Revisão visual localizada, CPU na mesma janela MCP; cena temporária descartada."""
import bpy,json
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2];report=json.loads((root/'docs/reports/blender/cidade_baixa_r30b33.json').read_text(encoding='utf8'))
assert Path(bpy.data.filepath).resolve()==(root/report['source_after']['file']).resolve()
source=bpy.context.scene;folder=root/'artifacts/cidade-baixa';folder.mkdir(exist_ok=True)
review=bpy.data.scenes.new('REVIEW TEMP | Foto Cidade Baixa R33');review.render.engine='CYCLES';review.cycles.device='CPU';review.cycles.samples=6;review.cycles.use_denoising=True
review.render.resolution_x=800;review.render.resolution_y=600;review.render.resolution_percentage=100;review.view_settings.view_transform='AgX'
world=bpy.data.worlds.new('REVIEW TEMP | luz R33');review.world=world;world.use_nodes=True
bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs['Color'].default_value=(.70,.75,.80,1);bg.inputs['Strength'].default_value=.6
names=[row['body'] for row in report['buildings']]+report['created_objects']+['MVP | terreno corrigido | colisão estática','CAIRU | bacia da fonte OSM','CAIRU | fundo da bacia','MARIO CRAVO | Fonte da Rampa do Mercado']
for name in names:review.collection.objects.link(source.objects[name])
light=bpy.data.lights.new('REVIEW TEMP | sol R33','SUN');light.energy=2.;light.angle=.12
sun=bpy.data.objects.new(light.name,light);review.collection.objects.link(sun);sun.rotation_euler=(.6,-.3,-.8)
camera=bpy.data.cameras.new('REVIEW TEMP | camera R33');cam=bpy.data.objects.new(camera.name,camera);review.collection.objects.link(cam);review.camera=cam;camera.lens=48;camera.clip_end=600
center=source.objects['MARIO CRAVO | Fonte da Rampa do Mercado'].location.copy()
views=[('fachadas',Vector((-106,95,25)),Vector((-72,36,14))),('fonte',center+Vector((-25,26,23)),center+Vector((0,0,7)))]
if globals().get('BOAS_REVIEW_VIEWS'):views=[v for v in views if v[0] in BOAS_REVIEW_VIEWS]
try:
    bpy.context.window.scene=review
    for label,pos,target in views:
        cam.location=pos;cam.rotation_euler=(target-pos).to_track_quat('-Z','Y').to_euler();review.render.filepath=str(folder/f'r30b33_{label}.png');bpy.ops.render.render(write_still=True)
finally:
    bpy.context.window.scene=source
    for o in (sun,cam):bpy.data.objects.remove(o,do_unlink=True)
    bpy.data.scenes.remove(review)
    for table,data in ((bpy.data.cameras,camera),(bpy.data.lights,light),(bpy.data.worlds,world)):
        if data.users==0:table.remove(data)
print(json.dumps({'views':[f'artifacts/cidade-baixa/r30b33_{v[0]}.png' for v in views],'geometry_not_saved':True}))
