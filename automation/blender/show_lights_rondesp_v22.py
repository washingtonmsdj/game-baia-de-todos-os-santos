"""Apresenta a animação na janela existente, sem modificar a fonte salva."""
import bpy, json
from pathlib import Path
r=Path(__file__).resolve().parents[2]
assert not bpy.app.background
assert Path(bpy.data.filepath).resolve()==(r/'blender/assets/vehicles/rondesp-pickup/marrom_v22_luzes.blend').resolve()
window=next(w for w in bpy.context.window_manager.windows if any(a.type=='VIEW_3D' for a in w.screen.areas))
area=next(a for a in window.screen.areas if a.type=='VIEW_3D')
region=next(x for x in area.regions if x.type=='WINDOW')
with bpy.context.temp_override(window=window,area=area,region=region):
 if not window.screen.is_animation_playing:
  bpy.ops.screen.animation_play()
playing=bool(window.screen.is_animation_playing)
rp=r/'docs/reports/blender/rondesp_marrom_v22.json'
report=json.loads(rp.read_text(encoding='utf8'))
report['live_flashing_playback']=playing
report.pop('playback_note',None)
rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'flashing_playback':playing,'windows':len(bpy.context.window_manager.windows),'source_unchanged':True}))
