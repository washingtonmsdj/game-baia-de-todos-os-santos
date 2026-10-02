"""Duas vistas de revisão de modelagem na mesma instância; cenário de estúdio descartável."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector,Matrix
root=Path(__file__).resolve().parents[2];source=bpy.context.scene
if not bpy.data.filepath.endswith('salvador_lacerda_r30b31_cidade_baixa_fachadas_cravo.blend'):raise RuntimeError('Abrir revisão R31')
out=root/'artifacts/cidade-baixa';out.mkdir(parents=True,exist_ok=True)
review=bpy.data.scenes.new('REVIEW TEMP | Cidade Baixa');review.render.engine='CYCLES';review.cycles.device='CPU';review.cycles.samples=8;review.cycles.use_denoising=True;review.render.resolution_x=900;review.render.resolution_y=600;review.render.resolution_percentage=100
review.world=bpy.data.worlds.new('REVIEW TEMP | luz');review.world.use_nodes=True
bg=next(n for n in review.world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs['Color'].default_value=(.65,.72,.82,1);bg.inputs['Strength'].default_value=.6
review.view_settings.view_transform='AgX'
ids={'1263035779','1220650665','1220650754','1220650857','1220650885','574235997','574235995'}
linked=[]
for o in source.objects:
    if (str(o.get('osm_way_id','')) in ids and o.get('game_role')=='static_building_blockout') or o.name.startswith('BAIXA R31 |') or o.name in ('CAIRU | bacia da fonte OSM','CAIRU | fundo da bacia','MARIO CRAVO | Fonte da Rampa do Mercado'):
        review.collection.objects.link(o);linked.append(o)
light=bpy.data.lights.new('REVIEW TEMP | sol','SUN');light.energy=2.3;light.angle=.15;sun=bpy.data.objects.new(light.name,light);review.collection.objects.link(sun);sun.rotation_euler=(.5,-.3,-.5)
camera=bpy.data.cameras.new('REVIEW TEMP | camera');cam=bpy.data.objects.new(camera.name,camera);review.collection.objects.link(cam);review.camera=cam;camera.lens=48;camera.clip_end=700
# Piso de estúdio somente nesta cena temporária; não é terreno de produção.
me=bpy.data.meshes.new('REVIEW TEMP | piso');me.from_pydata([(-250,0,6.95),(80,0,6.95),(80,200,6.95),(-250,200,6.95)],[],[(0,1,2,3)]);me.update();floor=bpy.data.objects.new(me.name,me);review.collection.objects.link(floor)
mat=bpy.data.materials.new('REVIEW TEMP | piso neutro');mat.diffuse_color=(.28,.30,.32,1);me.materials.append(mat)
R=Matrix.Rotation(source.objects['CASCA | parede lateral'].rotation_euler.z,4,'Z');center=source.objects['MARIO CRAVO | Fonte da Rampa do Mercado'].location.copy()
views=[('predios',Vector((-83,161,35)),Vector((-20,80,18))),('cravo',center+R@Vector((9,39,14)),center+Vector((0,0,8)))]
try:
    bpy.context.window.scene=review
    for name,pos,target in views:
        cam.location=pos;cam.rotation_euler=(target-pos).to_track_quat('-Z','Y').to_euler();review.render.filepath=str(out/f'r30b31_{name}.png');bpy.ops.render.render(write_still=True)
finally:
    bpy.context.window.scene=source
    for o in (cam,sun,floor):bpy.data.objects.remove(o,do_unlink=True)
    bpy.data.scenes.remove(review)
print(json.dumps({'views':[str(out/f'r30b31_{v[0]}.png') for v in views],'presentation_only':True}))
