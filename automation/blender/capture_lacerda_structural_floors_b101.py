"""Vistas da estrutura e dos pavimentos na cena real; restaura o mapa completo."""
import bpy,json,runpy
from pathlib import Path
from mathutils import Matrix,Vector

root=Path(__file__).resolve().parents[2]
assert Path(bpy.data.filepath).name=='salvador_lacerda_r30b101_pavimentos_estruturais.blend'
scene=bpy.context.scene; window=next(w for w in bpy.context.window_manager.windows if w.screen)
area=next(a for a in window.screen.areas if a.type=='VIEW_3D'); region=next(r for r in area.regions if r.type=='WINDOW'); space=area.spaces.active
M=Matrix(json.loads((root/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text())['measurement_frame'])
runpy.run_path(str(root/'automation/blender/present_lacerda_structure_b91.py'))
with bpy.context.temp_override(window=window,area=area,region=region):
    runpy.run_path(str(root/'automation/blender/capture_current_map_view.py'),init_globals={'BOAS_CAPTURE_FILENAME':'b101-estrutura.png'})
    bpy.ops.view3d.localview(frame_selected=False)
    bpy.ops.object.select_all(action='DESELECT')
    floors=[o for o in scene.objects if o.visible_get() and o.type=='MESH' and any(o.name.startswith(v) for v in ('B101 |','B100 | cidade alta | laje','B99 | cidade alta | laje'))]
    for o in floors:o.select_set(True)
    bpy.context.view_layer.objects.active=floors[0]; bpy.ops.view3d.localview(frame_selected=False)
    space.region_3d.view_location=M@Vector((-8.,0.,66.)); space.region_3d.view_rotation=(M.to_3x3()@Vector((-.8,-1.3,.6))).to_track_quat('Z','Y')
    space.region_3d.view_distance=60.; space.region_3d.view_perspective='ORTHO'; space.region_3d.update()
    bpy.ops.object.select_all(action='DESELECT')
    runpy.run_path(str(root/'automation/blender/capture_current_map_view.py'),init_globals={'BOAS_CAPTURE_FILENAME':'b101-pavimentos.png'})
runpy.run_path(str(root/'automation/blender/present_lacerda_map_b91.py'))
with bpy.context.temp_override(window=window,area=area,region=region):
    runpy.run_path(str(root/'automation/blender/capture_current_map_view.py'),init_globals={'BOAS_CAPTURE_FILENAME':'b101-map.png'})
p={'file':Path(bpy.data.filepath).relative_to(root).as_posix(),'scene':scene.name,'local_view':bool(space.local_view),
   'terrain_visible':scene.objects['MVP | terreno corrigido | colisão estática'].visible_get(),'unsaved_changes':bpy.data.is_dirty}
(root/'docs/reports/blender/lacerda-floors-b101/presentation.json').write_text(json.dumps(p,indent=2)+'\n',encoding='utf8')
print(json.dumps(p))
