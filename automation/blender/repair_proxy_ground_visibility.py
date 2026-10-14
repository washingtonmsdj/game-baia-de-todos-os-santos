"""Repara apenas visibilidade da B82; preserva chão histórico e malhas/colisão."""
import bpy,json,runpy,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
assert Path(bpy.data.filepath).name=='salvador_lacerda_r30b82_gameplay_proxy.blend'
source=bpy.data.scenes['SALVADOR | ESBOCO OFICIAL'];proxy=bpy.data.scenes['BOAS | GAMEPLAY_PROXY B82']
assert bpy.app.driver_namespace.get('boas_proxy_operator') is None,'Encerrar controller antes de revisão visual'
# Estes dois objetos foram comprovadamente ocultados como malhas inteiras pelo
# AABB da apresentação B82; não inferir identidade apenas por prefixo de nome.
config=json.loads((ROOT/'world/areas/mvp-centro-lacerda/lacerda-gameplay-proxy.json').read_text(encoding='utf8'))
targets=config['presentation']['keep_context_visible']
changes=[]
for name in targets:
    ob=bpy.data.objects[name]
    assert ob.visible_get(view_layer=source.view_layers[0]),'Fonte histórica não visível: '+name
    assert name in proxy.view_layers[0].objects
    before=ob.hide_get(view_layer=proxy.view_layers[0])
    ob.hide_set(False,view_layer=proxy.view_layers[0])
    changes.append({'object':name,'hidden_before':before,'hidden_after':ob.hide_get(view_layer=proxy.view_layers[0]),'historical_visible':ob.visible_get(view_layer=source.view_layers[0])})
assert len(bpy.data.collections['GAMEPLAY_PROXY | Lacerda B82'].objects)==70
report={'pid':os.getpid(),'changes':changes,'geometry_changed':False,'physics_changed':False,'saved':False,'new_revision':None,'presentation_patch_only':True}
try:
    bpy.context.window.scene=proxy
    if globals().get('BOAS_CAPTURE',True):
        runpy.run_path(str(ROOT/'automation/blender/capture_current_map_view.py'),init_globals={'BOAS_CAPTURE_FILENAME':'proxy-ground-restored.png'})
finally:
    bpy.context.window.scene=source
report['active_scene']=bpy.context.scene.name
out=ROOT/'docs/reports/blender/lacerda-live-diagnostic/ground_visibility_patch.json'
out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(report,ensure_ascii=False))
