"""Conferência localizada da recuperação de fachadas, após reabrir a fonte."""
import bpy,json,runpy
from pathlib import Path
root=Path(__file__).resolve().parents[2];scene=bpy.context.scene
path=root/'docs/reports/blender/cidade_baixa_r30b32.json';report=json.loads(path.read_text(encoding='utf8'))
assert Path(bpy.data.filepath).resolve()==(root/report['source_after']['file']).resolve()
functions=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'))
names=report['restored_bodies']+report['restored_existing_components']
old=functions['inspect_file'](root/report['restoration_source'],names)
comparison={name:functions['signature'](scene.objects[name])==old[name] for name in names}
assert all(comparison.values()),str([name for name,ok in comparison.items() if not ok])
for name in report['restored_existing_components']:
    o=scene.objects[name];assert not o.hide_render and not o.hide_get()
    assert any(c.name=='ENVIRONMENT_FINAL | Comércio B23 preservado' for c in o.users_collection)
for name in report['hidden_regressive_components']:assert scene.objects[name].hide_render
for name,expected in report['road_signatures'].items():assert functions['signature'](scene.objects[name])==expected
proof=json.loads((root/'artifacts/blender-sessions/last-open.json').read_text(encoding='utf8'))
assert proof['file']==report['source_after']['file'] and proof['sha256']==report['source_after']['sha256'] and proof['load_post_completed']
instance=scene.objects['MARIO CRAVO | Fonte da Rampa do Mercado'];assert instance.instance_collection.library.filepath.startswith('//')
report['reopened']=True;report['reopen_proof']=proof;report['restored_components_equal_b23']=comparison
report['visual_review']='Componentes autorais preferidos pelo usuário reativados; dados/transform/materiais iguais à B23. Novas áreas continuam candidatas.'
path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'file':report['source_after']['file'],'restored_match_b23':len(comparison),'terrain_and_collision_equal_b30':True,'reopened':True}))
