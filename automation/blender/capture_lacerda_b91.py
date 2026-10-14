"""Captura estabilizada da mesma janela B91, sem cena alternativa."""
import bpy,runpy,json
from pathlib import Path
root=Path(__file__).resolve().parents[2]
assert Path(bpy.data.filepath).name in ('salvador_lacerda_r30b91_integridade_malha_e_apoios.blend','salvador_lacerda_r30b92_ponte_estrutural_consolidada.blend')
window=next(w for w in bpy.context.window_manager.windows if w.screen);area=next(a for a in window.screen.areas if a.type=='VIEW_3D');region=next(r for r in area.regions if r.type=='WINDOW')
with bpy.context.temp_override(window=window,area=area,region=region):
 mode='exterior' if area.spaces.active.local_view else 'map'
 revision='b92' if 'b92_' in Path(bpy.data.filepath).name else 'b91'
 runpy.run_path(str(root/'automation/blender/capture_current_map_view.py'),init_globals={'BOAS_CAPTURE_FILENAME':revision+'-'+mode+'.png'})
status={'scene':bpy.context.scene.name,'file':Path(bpy.data.filepath).relative_to(root).as_posix(),'mode':mode,'local_view':bool(area.spaces.active.local_view),'terrain_visible':bpy.context.scene.objects['MVP | terreno corrigido | colisão estática'].visible_get(),'unsaved_changes':bpy.data.is_dirty,'snapshot':'artifacts/lacerda-live-diagnostic/'+revision+'-'+mode+'.png'}
folder=root/'docs/reports/blender'/('lacerda-bridge-b92' if revision=='b92' else 'lacerda-mesh-b91')
(folder/('presentation-'+mode+'.json')).write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(status))
