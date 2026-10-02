"""Confere os componentes gravados e mostra duas vistas; não muda geometria."""
import bpy, json, runpy, shutil
from pathlib import Path
root=Path(__file__).resolve().parents[2]
rp=root/'docs/reports/blender/cidade_baixa_r30b37.json'
report=json.loads(rp.read_text(encoding='utf8'))
source=root/report['source_after']['file']
assert Path(bpy.data.filepath).resolve()==source.resolve()
helpers=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'))
names=list(report['changed_objects'])
temp=root/'artifacts/cidade-baixa/readback_r37.blend'
shutil.copyfile(source,temp)
try:
    saved=helpers['inspect_file'](temp,names)
    for name in names:
        assert saved[name]==report['changed_objects'][name]['after'], 'Gravação divergente: '+name
        assert helpers['signature'](bpy.context.scene.objects[name])==saved[name]
    report['saved_datablocks_readback']={'status':'passed','components':len(names),'method':'Leitura dos objetos do .blend salvo na mesma instância; sem recarregar a cena inteira.'}
finally:
    temp.unlink()
rp.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
runpy.run_path(str(root/'automation/blender/review_baixa_frontages_r37.py'),init_globals={'r37_include_new':True})
print(json.dumps({'saved_components_verified':len(names),'views':['conjunto','frente']},ensure_ascii=False))
