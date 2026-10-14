"""Inspeção de aplicação parcial após timeout; nenhuma mutação."""
import bpy,json,runpy
from pathlib import Path
root=Path(__file__).resolve().parents[2]
config=json.loads((root/'world/areas/mvp-centro-lacerda/lacerda-gameplay-proxy.json').read_text(encoding='utf8'))
scene=bpy.data.scenes.get(config['scene_name']);col=bpy.data.collections.get('GAMEPLAY_PROXY | Lacerda B82')
report={'file':bpy.data.filepath,'active_scene':bpy.context.scene.name,'dirty':bpy.data.is_dirty,'proxy_scene_exists':scene is not None,'proxy_frame':scene.frame_current if scene else None,'proxy_scene_properties':list(scene.keys()) if scene else [],'proxy_objects':len(col.objects) if col else 0,'bootstrap_exists':'BOAS_JOGAR_PROXY.py' in bpy.data.texts,'model_progress':[(o.name,len(o.data.polygons) if o.type=='MESH' else None) for o in col.objects if o.name.startswith('B82 | CONTEXT')] if col else []}
before=json.loads((root/'docs/reports/blender/lacerda-gameplay-proxy/protected_original_components.json').read_text(encoding='utf8'))
sig=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'))['signature'];diff=[]
for name in ['FUNCIONAL | 3 piso','SUPERIOR | piso saguão','INFERIOR | piso do saguão','INFERIOR | guia de fila.001','MVP | terreno corrigido | colisão estática']:
 if name in before:
  after=sig(bpy.data.objects[name])
  if after!=before[name]:diff.append({'object':name,'before':before[name],'after':after})
report['selected_component_differences']=diff
(root/'docs/reports/blender/lacerda-gameplay-proxy/diagnostic_partial.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(report,ensure_ascii=False))
