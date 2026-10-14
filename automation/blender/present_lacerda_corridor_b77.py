"""Mostra a revisão na câmera de QA, sem salvar ou alterar geometria."""
import bpy,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
report=json.loads((ROOT/'docs/reports/blender/lacerda-corridor/scene_b77.json').read_text(encoding='utf8'))
scene=bpy.context.scene;scene.frame_start=report['timeline']['start'];scene.frame_end=report['timeline']['end'];scene.frame_set(scene.frame_start)
scene.camera=bpy.data.objects['B77 | QA | personagem']
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        space=area.spaces.active;space.region_3d.view_perspective='CAMERA';space.region_3d.view_camera_zoom=0
print(json.dumps({'frame':scene.frame_current,'camera':scene.camera.name,'saved':False,'preview_only':True}))
