"""Vistas diretas de comparação fotográfica, na mesma janela Blender."""
import bpy,json,runpy
from pathlib import Path
from mathutils import Matrix,Vector
root=Path(__file__).resolve().parents[2];out=root/'artifacts/palacio-rio-branco';source=bpy.context.scene
r=json.loads((root/'docs/reports/blender/torre_galerias_r30b35.json').read_text(encoding='utf8'));r34=json.loads((root/'docs/reports/blender/palacio_rio_branco_r30b34.json').read_text(encoding='utf8'))
T=Matrix(r34['palace']['frame_world']);R=Matrix(r['tower_alignment']['rotation_world'])
if not globals().get('BOAS_REVIEW_NAMES'):runpy.run_path(str(root/'automation/blender/inspect_context_r35.py'))
data=json.loads((out/'context_r35.json').read_text(encoding='utf8'))
full=[]
for row in data['objects']:
    o=source.objects.get(row['name'])
    if o is None or o.hide_render or o.get('boas_role') in ('static_collider','reference','navigation'):continue
    if o.name!='MVP | terreno corrigido | colisão estática' and any(k in c.lower() for c in row['collections'] for k in ('collision','source_georef','reference','navmesh','gameplay','arquivo','archive','apresenta','referência')):continue
    full.append(o)
names=set(r34['created_objects']+r['palace_facade_refinement']['created_objects']+['MVP | terreno corrigido | colisão estática','PRAÇA | OSM 1263035782'])
palace=[source.objects[n] for n in names if n in source.objects and not source.objects[n].hide_render]
review=bpy.data.scenes.new('REVIEW TEMP | Fachada e conjunto R35');review.render.engine='CYCLES';review.cycles.device='CPU';review.cycles.samples=8;review.cycles.use_denoising=True
review.render.resolution_x=1000;review.render.resolution_y=700;review.render.resolution_percentage=100;review.view_settings.view_transform='AgX'
world=bpy.data.worlds.new('REVIEW TEMP | luz fachada R35');world.use_nodes=True;review.world=world
bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs['Color'].default_value=(.70,.78,.84,1);bg.inputs['Strength'].default_value=.65
light=bpy.data.lights.new('REVIEW TEMP | sol fachada R35','SUN');light.energy=2.5;light.angle=.12
sun=bpy.data.objects.new(light.name,light);review.collection.objects.link(sun);sun.rotation_euler=(.75,-.3,-.9)
camera=bpy.data.cameras.new('REVIEW TEMP | camera fachada R35');cam=bpy.data.objects.new(camera.name,camera);review.collection.objects.link(cam);review.camera=cam;camera.clip_end=1800
views=[('frente',T@Vector((0,61,11)),T@Vector((0,-3,13)),47,palace),('lateral',T@Vector((-53,25,29)),T@Vector((-3,-11,12)),47,palace),('panorama_completo',R@Vector((-310,-145,127)),R@Vector((-72,-20,43)),32,full),('praca',T@Vector((8,47,3.2)),T@Vector((0,-4,9)),29,full)]
if globals().get('BOAS_REVIEW_NAMES'):
    views=[v for v in views if v[0] in BOAS_REVIEW_NAMES]
    review.cycles.samples=4;review.render.resolution_x=850;review.render.resolution_y=650
linked=[]
try:
    bpy.context.window.scene=review
    for name,pos,target,lens,objects in views:
        for o in linked:review.collection.objects.unlink(o)
        linked=[]
        for o in objects:review.collection.objects.link(o);linked.append(o)
        camera.lens=lens;cam.location=pos;cam.rotation_euler=(target-pos).to_track_quat('-Z','Y').to_euler();review.render.filepath=str(out/f'r30b35_{name}.png');bpy.ops.render.render(write_still=True)
finally:
    bpy.context.window.scene=source
    for o in (sun,cam):bpy.data.objects.remove(o,do_unlink=True)
    bpy.data.scenes.remove(review)
    for table,item in ((bpy.data.worlds,world),(bpy.data.cameras,camera),(bpy.data.lights,light)):
        if not item.users:table.remove(item)
(out/'facade_context_visual_r35.json').write_text(json.dumps({'views':[f'artifacts/palacio-rio-branco/r30b35_{v[0]}.png' for v in views],'usage':'Comparação arquitetônica candidata; não validação de runtime'},ensure_ascii=False,indent=2),encoding='utf8')
