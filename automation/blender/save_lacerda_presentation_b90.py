"""Persiste apenas apresentação do mapa completo; nenhuma nova geometria."""
import bpy,json,hashlib,os
from pathlib import Path
root=Path(__file__).resolve().parents[2];scene=bpy.context.scene;file=Path(bpy.data.filepath)
assert file.name=='salvador_lacerda_r30b90_cotas_exteriores_consolidadas.blend' and scene.name=='SALVADOR | ESBOCO OFICIAL'
window=next(w for w in bpy.context.window_manager.windows if w.screen)
assert all(not a.spaces.active.local_view for a in window.screen.areas if a.type=='VIEW_3D')
assert scene.objects['MVP | terreno corrigido | colisão estática'].visible_get(), 'Terreno principal não está visível'
catalog_path=root/'world/areas/mvp-centro-lacerda/blender-revisions.json';cat=json.loads(catalog_path.read_text())
old_digest=cat['authoring_source']['sha256']
bpy.ops.wm.save_mainfile(compress=True)
with file.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
for key in ('authoring_source','validation_source'):
    cat[key]['sha256']=digest;cat[key]['presentation']='FULL_MAP_NO_LOCAL_VIEW'
entry=next(r for r in cat['revisions'] if r['file']==file.relative_to(root).as_posix());entry['sha256']=digest;entry['presentation']='FULL_MAP_NO_LOCAL_VIEW'
catalog_path.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
report_path=root/'docs/reports/blender/lacerda-massing-b90/application.json';report=json.loads(report_path.read_text())
report['sha256_before_presentation_save']=old_digest;report['sha256']=digest;report['reopened']=False
report['presentation']={'scene':scene.name,'local_view':False,'main_terrain_visible':True,'same_window_pid':os.getpid(),'geometry_changed':False}
report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'file':entry['file'],'sha256':digest,'full_map_visible':True,'geometry_changed':False}))
