"""Avalia o replay salvo e captura passagem e encontro problemático no Blender."""
import bpy,json
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2];scene=bpy.context.scene
car=scene.objects['TESTE | carro | apoio de quatro rodas']
window=next(w for w in bpy.context.window_manager.windows if any(a.type=='VIEW_3D' for a in w.screen.areas));area=next(a for a in window.screen.areas if a.type=='VIEW_3D');region=next(r for r in area.regions if r.type=='WINDOW');space=area.spaces.active
scene.render.resolution_x=1280;scene.render.resolution_y=720;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';space.overlay.show_overlays=False;space.shading.type='SOLID';space.shading.color_type='MATERIAL';space.shading.light='STUDIO'
directory=root/'artifacts/terrain-vehicle';evaluated=0
for frame in range(scene.frame_start,scene.frame_end+1,8):scene.frame_set(frame);evaluated+=1
views=[]
for label,frame in [('passagem-baixa',600),('ladeira',2200),('encontro',scene.frame_end)]:
    scene.frame_set(frame);target=car.matrix_world.translation.copy()+Vector((0,0,.8));eye=target+Vector((-12,-14,11));r=space.region_3d;r.view_rotation=(target-eye).to_track_quat('-Z','Y');r.view_distance=(target-eye).length;r.view_location=target;r.view_perspective='PERSP';r.update();scene.render.filepath=str(directory/(label+'.png'))
    with bpy.context.temp_override(window=window,screen=window.screen,area=area,region=region):bpy.ops.render.opengl(write_still=True,view_context=True)
    views.append({'frame':frame,'image':(directory/(label+'.png')).relative_to(root).as_posix(),'car_position':list(car.matrix_world.translation)})
report=json.loads((root/'docs/reports/blender/terrain_vehicle_replay.json').read_text());report['evaluated_replay_frames']=evaluated;report['visual_captures']=views;report['visual_review']='pending image inspection';(root/'docs/reports/blender/terrain_vehicle_replay.json').write_text(json.dumps(report,ensure_ascii=False,separators=(',',':')),encoding='utf8')
scene.frame_set(1)
with bpy.context.temp_override(window=window,screen=window.screen,area=area,region=region):bpy.ops.object.select_all(action='DESELECT');car.select_set(True);bpy.context.view_layer.objects.active=car
print(json.dumps({'evaluated_replay_frames':evaluated,'views':views},ensure_ascii=False))
