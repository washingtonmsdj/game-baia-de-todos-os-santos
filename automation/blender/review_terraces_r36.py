"""Duas vistas de conjunto, encosta e retaguarda; mesma janela, sem gameplay."""
import bpy,json
from pathlib import Path
from mathutils import Matrix,Vector
root=Path(__file__).resolve().parents[2];out=root/'artifacts/palacio-rio-branco';source=bpy.context.scene
r=json.loads((root/'docs/reports/blender/terracos_palacio_r30b36.json').read_text(encoding='utf8'));r34=json.loads((root/'docs/reports/blender/palacio_rio_branco_r30b34.json').read_text(encoding='utf8'));r35=json.loads((root/'docs/reports/blender/torre_galerias_r30b35.json').read_text(encoding='utf8'));S=Matrix(r['layout']['frame_world'])
review=bpy.data.scenes.new('REVIEW TEMP | Terraços R36');review.render.engine='BLENDER_WORKBENCH';review.display.shading.light='STUDIO';review.display.shading.color_type='MATERIAL';review.display.shading.show_shadows=True;review.display.shading.show_cavity=True;review.display.shading.cavity_type='BOTH';review.render.resolution_x=900;review.render.resolution_y=650;review.render.resolution_percentage=100;review.view_settings.view_transform='AgX'
names=set(r['created_objects']+r34['created_objects']+r34['galleries']['created_objects']+r35['created_objects']+r35['tower_alignment']['objects']+['MVP | terreno corrigido | colisão estática','PRAÇA | OSM 1263035782'])
for name in names:
    o=source.objects.get(name)
    if o and not o.hide_render and not all(c.hide_render for c in o.users_collection):review.collection.objects.link(o)
world=bpy.data.worlds.new('REVIEW TEMP | luz terraços');world.use_nodes=True;review.world=world;bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs['Color'].default_value=(.65,.74,.85,1);bg.inputs['Strength'].default_value=.65
light=bpy.data.lights.new('REVIEW TEMP | sol terraços','SUN');light.energy=2.3;light.angle=.12;sun=bpy.data.objects.new(light.name,light);review.collection.objects.link(sun);sun.rotation_euler=(.7,-.4,-.9)
camera=bpy.data.cameras.new('REVIEW TEMP | camera terraços');cam=bpy.data.objects.new(camera.name,camera);review.collection.objects.link(cam);review.camera=cam;camera.lens=40;camera.clip_end=1600
views=[('terracos',S@Vector((-25,74,81)),S@Vector((17,15,65))),('retaguarda',S@Vector((-23,-92,90)),S@Vector((15,-13,78))),('colunata',S@Vector((14,52,49)),S@Vector((14,29,48.4))),('escada_interna',S@Vector((1,45,67)),S@Vector((14,29,50))),('encontro',S@Vector((48,45,79)),S@Vector((26,5,65)))]
if globals().get('review_view_names'):
    views=[v for v in views if v[0] in review_view_names]
try:
    bpy.context.window.scene=review
    for name,eye,target in views:
        cam.location=eye;cam.rotation_euler=(target-eye).to_track_quat('-Z','Y').to_euler();review.render.filepath=str(out/f'r30b36_{name}.png');bpy.ops.render.render(write_still=True)
finally:
    bpy.context.window.scene=source
    for o in (sun,cam):bpy.data.objects.remove(o,do_unlink=True)
    bpy.data.scenes.remove(review)
    for table,item in ((bpy.data.worlds,world),(bpy.data.cameras,camera),(bpy.data.lights,light)):
        if not item.users:table.remove(item)
