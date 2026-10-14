"""Inspecionar a câmera real em três trajetos; capturas da janela, sem salvar fonte."""
import bpy,json
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2];scene=bpy.context.scene
audit=json.loads((root/'docs/reports/blender/centro-expansion/rondesp_ground_probe_b74.json').read_text(encoding='utf8'))
scene.camera=scene.objects[audit['summary']['driver_camera']]
folder=root/'artifacts/centro-expansion';folder.mkdir(parents=True,exist_ok=True)
window=bpy.context.window;area=next(a for a in window.screen.areas if a.type=='VIEW_3D');space=area.spaces.active
space.region_3d.view_perspective='CAMERA';space.shading.type='MATERIAL';space.shading.use_scene_lights=False;space.shading.use_scene_world=False;space.overlay.show_overlays=False
shots=[]
for run in audit['summary']['routes']:
    poses=[p for p in audit['poses'] if p['location_id']==run['location_id'] and not p['flags'] and p['xy'][1]<-350]
    if not poses:continue
    pose=poses[int(len(poses)*.85)];scene.frame_set(pose['frame']);bpy.context.view_layer.update()
    path=folder/('motorista-'+run['location_id']+'-b74.png')
    with bpy.context.temp_override(window=window,area=area):
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP',iterations=2)
        bpy.ops.screen.screenshot_area(filepath=str(path))
    shots.append({'file':path.relative_to(root).as_posix(),'location_id':run['location_id'],'frame':pose['frame'],'osm_way_id':pose['osm_way_id'],'view':'actual_driver_camera','source_reference_only':True})
scene.frame_set(audit['summary']['overview_frame'])
space.region_3d.view_perspective='ORTHO';space.region_3d.view_location=(470,-690,25);space.region_3d.view_distance=2550;space.region_3d.view_rotation=Vector((.3,-.65,1.6)).to_track_quat('Z','Y')
space.shading.type='SOLID';space.shading.color_type='MATERIAL'
with bpy.context.temp_override(window=window,area=area):
    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP',iterations=2)
    bpy.ops.screen.screenshot_area(filepath=str(folder/'visao-geral-b74.png'))
record={'source_file':Path(bpy.data.filepath).relative_to(root).as_posix(),'driver_shots':shots,'overview':'artifacts/centro-expansion/visao-geral-b74.png','scene_saved':False,'rendered_roads_final':False}
(root/'docs/reports/blender/centro-expansion/visual_review_b74.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(record,ensure_ascii=False))
