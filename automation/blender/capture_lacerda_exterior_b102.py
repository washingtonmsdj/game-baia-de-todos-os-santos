"""Duas vistas da mesma cena visível; termina com o mapa completo aberto."""
import bpy,json,runpy
from pathlib import Path
from mathutils import Matrix,Vector
root=Path(__file__).resolve().parents[2]
M=Matrix(json.loads((root/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text())['measurement_frame'])
w=next(w for w in bpy.context.window_manager.windows if w.screen);a=next(a for a in w.screen.areas if a.type=='VIEW_3D');rg=next(r for r in a.regions if r.type=='WINDOW');sp=a.spaces.active
with bpy.context.temp_override(window=w,area=a,region=rg):
 if sp.local_view:bpy.ops.view3d.localview(frame_selected=False)
 bpy.ops.object.select_all(action='DESELECT')
 sp.shading.type='SOLID';sp.shading.color_type='MATERIAL';sp.overlay.show_overlays=False
 for label,direction in (('frente',(-1.2,-1.7,.75)),('encosta',(.8,1.5,.55))):
  sp.region_3d.view_location=M@Vector((-28.,3.,47.));sp.region_3d.view_distance=120.
  sp.region_3d.view_rotation=(M.to_3x3()@Vector(direction)).to_track_quat('Z','Y');sp.region_3d.view_perspective='ORTHO';sp.region_3d.update();a.tag_redraw()
  runpy.run_path(str(root/'automation/blender/capture_current_map_view.py'),init_globals={'BOAS_CAPTURE_FILENAME':'b102-'+label+'.png'})
 sp.region_3d.view_rotation=(M.to_3x3()@Vector((-1.2,-1.7,.75))).to_track_quat('Z','Y');sp.overlay.show_overlays=True;sp.region_3d.update();a.tag_redraw()
print(json.dumps({'file':bpy.data.filepath,'scene':bpy.context.scene.name,'terrain_visible':bpy.context.scene.objects['MVP | terreno corrigido | colisão estática'].visible_get(),'local_view':bool(sp.local_view)}))
