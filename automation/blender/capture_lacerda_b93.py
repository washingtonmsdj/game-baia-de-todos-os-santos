"""Captura e identidade da B93 na janela efetivamente aberta."""
import bpy,json,runpy
from pathlib import Path
root=Path(__file__).resolve().parents[2]
assert Path(bpy.data.filepath).name=='salvador_lacerda_r30b93_estrutura_inferior_documental.blend'
window=next(w for w in bpy.context.window_manager.windows if w.screen);area=next(a for a in window.screen.areas if a.type=='VIEW_3D');region=next(r for r in area.regions if r.type=='WINDOW')
with bpy.context.temp_override(window=window,area=area,region=region):
    mode='exterior' if area.spaces.active.local_view else 'map'
    runpy.run_path(str(root/'automation/blender/capture_current_map_view.py'),init_globals={'BOAS_CAPTURE_FILENAME':'b93-'+mode+'.png'})
data={'file':Path(bpy.data.filepath).relative_to(root).as_posix(),'scene':bpy.context.scene.name,'mode':mode,'local_view':bool(area.spaces.active.local_view),'terrain_visible':bpy.context.scene.objects['MVP | terreno corrigido | colisão estática'].visible_get(),'unsaved_changes':bpy.data.is_dirty,'snapshot':'artifacts/lacerda-live-diagnostic/b93-'+mode+'.png'}
(root/'docs/reports/blender/lacerda-lower-structure-b93'/('presentation-'+mode+'.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data))
