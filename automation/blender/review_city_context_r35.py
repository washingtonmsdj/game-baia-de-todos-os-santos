"""Vista completa do recorte fotografado; inclui o entorno, não só o elevador."""
import bpy,json,runpy
from pathlib import Path
from mathutils import Matrix,Vector
root=Path(__file__).resolve().parents[2];out=root/'artifacts/palacio-rio-branco';source=bpy.context.scene
r=json.loads((root/'docs/reports/blender/torre_galerias_r30b35.json').read_text(encoding='utf8'));R=Matrix(r['tower_alignment']['rotation_world'])
data=json.loads((out/'context_r35.json').read_text(encoding='utf8'))
review=bpy.data.scenes.new('REVIEW TEMP | Conjunto urbano R35');review.render.engine='CYCLES';review.cycles.device='CPU';review.cycles.samples=6;review.cycles.use_denoising=True;review.render.resolution_x=1100;review.render.resolution_y=720;review.render.resolution_percentage=100;review.view_settings.view_transform='AgX'
world=bpy.data.worlds.new('REVIEW TEMP | luz conjunto R35');world.use_nodes=True;review.world=world;bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs['Color'].default_value=(.55,.72,.85,1);bg.inputs['Strength'].default_value=.7
names=[]
for row in data['objects']:
    o=source.objects.get(row['name'])
    if o is None or o.hide_render or o.get('boas_role') in ('static_collider','reference','navigation'):continue
    if o.name!='MVP | terreno corrigido | colisão estática' and any(k in c.lower() for c in row['collections'] for k in ('collision','source_georef','reference','navmesh','gameplay','arquivo','archive','apresenta','referência')):continue
    review.collection.objects.link(o);names.append(o.name)
light=bpy.data.lights.new('REVIEW TEMP | sol conjunto R35','SUN');light.energy=2.4;light.angle=.12;sun=bpy.data.objects.new(light.name,light);review.collection.objects.link(sun);sun.rotation_euler=(.7,-.4,-1.0)
camera=bpy.data.cameras.new('REVIEW TEMP | camera conjunto R35');cam=bpy.data.objects.new(camera.name,camera);review.collection.objects.link(cam);review.camera=cam;camera.lens=44;camera.clip_end=1800
views=[('panorama_completo',R@Vector((-280,-140,120)),R@Vector((-75,-2,44)))]
try:
    bpy.context.window.scene=review
    for name,pos,target in views:
        cam.location=pos;cam.rotation_euler=(target-pos).to_track_quat('-Z','Y').to_euler();review.render.filepath=str(out/f'r30b35_{name}.png');bpy.ops.render.render(write_still=True)
finally:
    bpy.context.window.scene=source
    for o in (sun,cam):bpy.data.objects.remove(o,do_unlink=True)
    bpy.data.scenes.remove(review)
    for table,item in ((bpy.data.worlds,world),(bpy.data.cameras,camera),(bpy.data.lights,light)):
        if not item.users:table.remove(item)
(out/'context_visual_r35.json').write_text(json.dumps({'objects_in_view':names,'views':[f'artifacts/palacio-rio-branco/r30b35_{v[0]}.png' for v in views]},ensure_ascii=False,indent=2),encoding='utf8')
