"""Captura B95 na janela existente e termina com mapa completo visível."""
import bpy,json,runpy
from pathlib import Path
from mathutils import Matrix,Vector
root=Path(__file__).resolve().parents[2];revision=globals().get('BOAS_CAPTURE_REVISION',95)
assert Path(bpy.data.filepath).name=={95:'salvador_lacerda_r30b95_limites_circulacoes_superiores.blend',96:'salvador_lacerda_r30b96_encontro_corpo_cobertura.blend'}[revision]
M=Matrix(json.loads((root/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text())['measurement_frame'])
window=next(w for w in bpy.context.window_manager.windows if w.screen);area=next(a for a in window.screen.areas if a.type=='VIEW_3D');region=next(r for r in area.regions if r.type=='WINDOW');space=area.spaces.active
runpy.run_path(str(root/'automation/blender/present_lacerda_structure_b91.py'))
with bpy.context.temp_override(window=window,area=area,region=region):
    views=[('rear-roof',(-8.5,0.,82.),(-1.,-.4,.6),17.)] if revision==96 else [('upper-junction',(-19.8,0.,72.),(-1.,-.15,.15),11.),('north-circulation',(-7.5,7.,72.),(.1,1.,.12),25.)]
    for label,center,back,distance in views:
        space.region_3d.view_location=M@Vector(center);space.region_3d.view_rotation=(M.to_3x3()@Vector(back)).to_track_quat('Z','Y');space.region_3d.view_distance=distance;space.region_3d.view_perspective='ORTHO';space.region_3d.update();area.tag_redraw()
        runpy.run_path(str(root/'automation/blender/capture_current_map_view.py'),init_globals={'BOAS_CAPTURE_FILENAME':f'b{revision}-'+label+'.png'})
runpy.run_path(str(root/'automation/blender/present_lacerda_map_b91.py'))
with bpy.context.temp_override(window=window,area=area,region=region):
    runpy.run_path(str(root/'automation/blender/capture_current_map_view.py'),init_globals={'BOAS_CAPTURE_FILENAME':f'b{revision}-map.png'})
data={'file':Path(bpy.data.filepath).relative_to(root).as_posix(),'scene':bpy.context.scene.name,'local_view':bool(space.local_view),'terrain_visible':bpy.context.scene.objects['MVP | terreno corrigido | colisão estática'].visible_get(),'unsaved_changes':bpy.data.is_dirty,'snapshots':[f'artifacts/lacerda-live-diagnostic/b{revision}-'+v+'.png' for v in [item[0] for item in views]+['map']]}
assert not data['local_view'] and data['terrain_visible']
(root/f'docs/reports/blender/{"lacerda-body-b96" if revision==96 else "lacerda-enclosure-b95"}/presentation.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data))
