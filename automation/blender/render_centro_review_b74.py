"""Imagens da geometria/câmera real na janela única, sem depender do screenshot."""
import bpy,json
from pathlib import Path
root=Path(__file__).resolve().parents[2];scene=bpy.context.scene
folder=root/'artifacts/centro-expansion';folder.mkdir(parents=True,exist_ok=True)
audit=json.loads((root/'docs/reports/blender/centro-expansion/rondesp_ground_probe_b74.json').read_text(encoding='utf8'))
settings=scene.render;shade=scene.display.shading
saved={k:getattr(settings,k) for k in ['engine','resolution_x','resolution_y','resolution_percentage','filepath']}
saved_shade={k:getattr(shade,k) for k in ['light','color_type','show_shadows','show_cavity','background_type']}
old_camera=scene.camera;old_frame=scene.frame_current;old_format=settings.image_settings.file_format
shots=[];temp_camera=None;hidden=[]
try:
    settings.engine='BLENDER_WORKBENCH';settings.resolution_x=1000;settings.resolution_y=650;settings.resolution_percentage=100;settings.image_settings.file_format='PNG'
    shade.light='STUDIO';shade.color_type='MATERIAL';shade.show_shadows=False;shade.show_cavity=False;shade.background_type='WORLD'
    scene.camera=scene.objects[audit['summary']['driver_camera']]
    for run in audit['summary']['routes']:
        poses=[p for p in audit['poses'] if p['location_id']==run['location_id'] and not p['flags'] and p['xy'][1]<-350]
        if not poses:continue
        pose=poses[int(len(poses)*.85)];scene.frame_set(pose['frame']);bpy.context.view_layer.update()
        path=folder/('render-motorista-'+run['location_id']+'-b74.png');settings.filepath=str(path)
        bpy.ops.render.render(write_still=True)
        shots.append({'location_id':run['location_id'],'file':path.relative_to(root).as_posix(),'frame':pose['frame'],'osm_way_id':pose['osm_way_id'],'method':'Actual Blender driver camera / Workbench render, no screenshot','references_overlay':False})
    cam_data=bpy.data.cameras.new('TEMP | overview B74');temp_camera=bpy.data.objects.new(cam_data.name,cam_data);scene.collection.objects.link(temp_camera)
    temp_camera.location=(470,-690,3000);cam_data.type='ORTHO';cam_data.ortho_scale=2600;cam_data.clip_end=10000;scene.camera=temp_camera
    settings.resolution_x=1000;settings.resolution_y=1300
    for ob in scene.objects:
        if ob.name.startswith('B74 | OSM |') or ob.type=='FONT' and ob.name.startswith('B74 |'):
            hidden.append((ob,ob.hide_render));ob.hide_render=False
    settings.filepath=str(folder/'render-referencia-geral-b74.png');bpy.ops.render.render(write_still=True)
finally:
    for ob,value in hidden:ob.hide_render=value
    scene.camera=old_camera;scene.frame_set(old_frame)
    for k,v in saved.items():setattr(settings,k,v)
    for k,v in saved_shade.items():setattr(shade,k,v)
    settings.image_settings.file_format=old_format
    if temp_camera:
        cam_data=temp_camera.data;bpy.data.objects.remove(temp_camera,do_unlink=True);bpy.data.cameras.remove(cam_data)
record={'source_file':Path(bpy.data.filepath).relative_to(root).as_posix(),'driver_shots':shots,'overview':'artifacts/centro-expansion/render-referencia-geral-b74.png','overview_reference_axes_not_pavement':True,'scene_saved':False,'viewport_capture_valid':False,'viewport_capture_failure':'All screenshot_area captures were 1x1 pixels','rendered_roads_final':False}
(root/'docs/reports/blender/centro-expansion/visual_review_b74.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(record,ensure_ascii=False))
