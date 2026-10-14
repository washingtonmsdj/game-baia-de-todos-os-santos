"""Recupera apresentação histórica na mesma janela; não edita malhas nem salva B82."""
import bpy,json,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
assert Path(bpy.data.filepath).name=='salvador_lacerda_r30b82_gameplay_proxy.blend'
historical=bpy.data.scenes['SALVADOR | ESBOCO OFICIAL'];proxy=bpy.data.scenes['BOAS | GAMEPLAY_PROXY B82']
app=json.loads((ROOT/'docs/reports/blender/lacerda-gameplay-proxy/application_b82.json').read_text(encoding='utf8'))
names=[n for n in app['masked_in_proxy_view_only'] if any(k in n.casefold() for k in ('terrain','terreno','pavimento','piso','marquise'))]
before=[{'object':n,'proxy_visible':bpy.data.objects[n].visible_get(view_layer=proxy.view_layers[0]),'historical_visible':bpy.data.objects[n].visible_get(view_layer=historical.view_layers[0])} for n in names if n in bpy.data.objects]
op=bpy.app.driver_namespace.get('boas_proxy_operator')
if op:
    try:op.finish()
    except ReferenceError:pass
if bpy.context.screen.is_animation_playing:bpy.ops.screen.animation_cancel(restore_frame=False)
bpy.context.window.scene=historical
after=[{'object':n,'visible':bpy.data.objects[n].visible_get(view_layer=bpy.context.view_layer)} for n in names if n in bpy.data.objects]
report={'pid':os.getpid(),'file':bpy.data.filepath,'active_scene':bpy.context.scene.name,'before':before,'after':after,'geometry_changed':False,'saved':False,'proxy_preserved':len(bpy.data.collections['GAMEPLAY_PROXY | Lacerda B82'].objects)==70,'controller_stopped_for_model_review':bpy.app.driver_namespace.get('boas_proxy_operator') is None}
out=ROOT/'docs/reports/blender/lacerda-live-diagnostic/restored_view.json';out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(report,ensure_ascii=False))
