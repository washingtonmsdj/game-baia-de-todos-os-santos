"""Revisão visual da nova superfície, sem salvar outra revisão nem mudar malhas."""
import bpy,json
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2];scene=bpy.context.scene
assert scene.get('boas_validation_revision')=='R30B.75'
folder=root/'artifacts/centro-expansion';folder.mkdir(parents=True,exist_ok=True)
settings=scene.render;shade=scene.display.shading
saved={k:getattr(settings,k) for k in ('engine','resolution_x','resolution_y','resolution_percentage','filepath')}
saved_shade={k:getattr(shade,k) for k in ('light','color_type','show_shadows','show_cavity','background_type')}
old_camera=scene.camera;old_frame=scene.frame_current;old_format=settings.image_settings.file_format
camera_data=bpy.data.cameras.new('TEMP | revisão passeios B75')
camera=bpy.data.objects.new(camera_data.name,camera_data);scene.collection.objects.link(camera)
shots=[]
try:
    settings.engine='BLENDER_WORKBENCH';settings.resolution_x=1200;settings.resolution_y=850;settings.resolution_percentage=100
    settings.image_settings.file_format='PNG';shade.light='STUDIO';shade.color_type='MATERIAL';shade.show_shadows=False;shade.show_cavity=False;shade.background_type='WORLD'
    scene.camera=camera;camera_data.type='ORTHO';camera_data.clip_end=10000
    for name,location,target,scale in [
        ('render-dique-passeios-b75',(1400,-2100,1700),(740,-1140,30),1250),
        ('render-encontros-passeios-b75',(940,-1430,300),(650,-1240,35),300)]:
        camera.location=location;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler();camera_data.ortho_scale=scale
        path=folder/(name+'.png');settings.filepath=str(path);bpy.ops.render.render(write_still=True)
        shots.append(path.relative_to(root).as_posix())
finally:
    scene.camera=old_camera;scene.frame_set(old_frame)
    for k,v in saved.items():setattr(settings,k,v)
    for k,v in saved_shade.items():setattr(shade,k,v)
    settings.image_settings.file_format=old_format
    bpy.data.objects.remove(camera,do_unlink=True);bpy.data.cameras.remove(camera_data)
record={'source_file':Path(bpy.data.filepath).relative_to(root).as_posix(),'images':shots,'method':'Câmeras reais Blender / Workbench, sem simular conteúdo ausente','scene_saved':False,'motor_roads_built':False,'production_ready':False}
(root/'docs/reports/blender/centro-expansion/visual_review_b75.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(record,ensure_ascii=False))
