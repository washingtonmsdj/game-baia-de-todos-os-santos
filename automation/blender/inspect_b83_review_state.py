"""Estado final visível da candidata, sem mudar a revisão."""
import bpy,json,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
assert Path(bpy.data.filepath).name=='salvador_lacerda_r30b83_encontro_superior_consolidado.blend'
source=bpy.data.scenes['SALVADOR | ESBOCO OFICIAL'];proxy=bpy.data.scenes['BOAS | GAMEPLAY_PROXY B82']
assert bpy.context.scene==source
assert len(source.objects)==6298
colliders=[{'name':o.name,'historical_visible':o.visible_get(view_layer=source.view_layers[0]),'proxy_visible':o.visible_get(view_layer=proxy.view_layers[0]),'hide_render':o.hide_render} for o in source.objects if o.name.startswith('B83 | COLLISION |')]
report={'pid':os.getpid(),'file':bpy.data.filepath,'scene':bpy.context.scene.name,'historical_objects':len(source.objects),'proxy_objects':len(bpy.data.collections['GAMEPLAY_PROXY | Lacerda B82'].objects),'colliders':colliders,'ground_visible':bpy.data.objects['MVP | terreno corrigido | colisão estática'].visible_get(view_layer=source.view_layers[0]),'geometry_changed':False}
(ROOT/'docs/reports/blender/lacerda-consolidation-b83/final_view_state.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(report,ensure_ascii=False))
