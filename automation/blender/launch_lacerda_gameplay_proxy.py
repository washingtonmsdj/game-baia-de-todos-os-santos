"""Inicia o personagem na view 3D existente; mesma janela e revisão explícita."""
import bpy,runpy,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
runpy.run_path(str(ROOT/'automation/blender/play_lacerda_gameplay_proxy.py'),run_name='__main__')
runpy.run_path(str(ROOT/'automation/blender/repair_proxy_ground_visibility.py'),init_globals={'BOAS_CAPTURE':False})
config=json.loads((ROOT/'world/areas/mvp-centro-lacerda/lacerda-gameplay-proxy.json').read_text(encoding='utf8'))
bpy.context.window.scene=bpy.data.scenes[config['scene_name']]
area=next(a for a in bpy.context.screen.areas if a.type=='VIEW_3D')
region=next(r for r in area.regions if r.type=='WINDOW')
with bpy.context.temp_override(area=area,region=region):
    result=bpy.ops.boas.proxy_play('INVOKE_DEFAULT')
print('Personagem ativo: '+str(result))
