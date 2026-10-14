"""Captura a vista que já se estabilizou na mesma janela."""
import bpy,runpy,json
from pathlib import Path
root=Path(__file__).resolve().parents[2]
assert Path(bpy.data.filepath).name=='salvador_lacerda_r30b90_cotas_exteriores_consolidadas.blend'
window=next(w for w in bpy.context.window_manager.windows if w.screen);area=next(a for a in window.screen.areas if a.type=='VIEW_3D');region=next(r for r in area.regions if r.type=='WINDOW')
with bpy.context.temp_override(window=window,area=area,region=region):
    space=area.spaces.active
    rotation=space.region_3d.view_rotation
    mode='map' if not space.local_view else ('plan' if abs(rotation.to_matrix()[2][2])>.99 else 'exterior')
    runpy.run_path(str(root/'automation/blender/capture_current_map_view.py'),init_globals={'BOAS_CAPTURE_FILENAME':'b90-'+mode+'.png'})
print(json.dumps({'file':bpy.data.filepath,'scene':bpy.context.scene.name,'mode':mode}))
