"""Inspeção visual real da frente e conjunto, terminando no mapa completo."""
import bpy,json,runpy
from pathlib import Path
from mathutils import Matrix,Vector
root=Path(__file__).resolve().parents[2];assert Path(bpy.data.filepath).name=='salvador_lacerda_r30b98_frente_superior_reconciliada.blend'
M=Matrix(json.loads((root/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text())['measurement_frame'])
window=next(w for w in bpy.context.window_manager.windows if w.screen);area=next(a for a in window.screen.areas if a.type=='VIEW_3D');region=next(r for r in area.regions if r.type=='WINDOW');space=area.spaces.active
runpy.run_path(str(root/'automation/blender/present_lacerda_structure_b91.py'))
views=[('frente',(2.,0.,72.),(1.,-.10,.12),26.),('conjunto',(-28.,3.,47.),(-1.2,-1.7,.75),115.)]
with bpy.context.temp_override(window=window,area=area,region=region):
 for label,center,back,distance in views:
  space.region_3d.view_location=M@Vector(center);space.region_3d.view_rotation=(M.to_3x3()@Vector(back)).to_track_quat('Z','Y');space.region_3d.view_distance=distance;space.region_3d.view_perspective='ORTHO';space.region_3d.update();area.tag_redraw()
  runpy.run_path(str(root/'automation/blender/capture_current_map_view.py'),init_globals={'BOAS_CAPTURE_FILENAME':f'b98-{label}.png'})
runpy.run_path(str(root/'automation/blender/present_lacerda_map_b91.py'))
with bpy.context.temp_override(window=window,area=area,region=region):runpy.run_path(str(root/'automation/blender/capture_current_map_view.py'),init_globals={'BOAS_CAPTURE_FILENAME':'b98-map.png'})
p={'file':Path(bpy.data.filepath).relative_to(root).as_posix(),'scene':bpy.context.scene.name,'local_view':bool(space.local_view),'terrain_visible':bpy.context.scene.objects['MVP | terreno corrigido | colisão estática'].visible_get(),'unsaved_changes':bpy.data.is_dirty}
(root/'docs/reports/blender/lacerda-completion-b98/presentation.json').write_text(json.dumps(p,indent=2)+'\n',encoding='utf8');print(json.dumps(p))
