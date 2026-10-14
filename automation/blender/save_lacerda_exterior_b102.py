"""Salva revisão real e registra origem sem promover produção."""
import bpy,json,hashlib,os,shutil,runpy
from pathlib import Path
root=Path(__file__).resolve().parents[2];out=root/'docs/reports/blender/lacerda-exterior-b102'
r=json.loads((out/'application.json').read_text());q=json.loads((out/'validation.json').read_text())
base=Path(bpy.data.filepath);dest=root/'blender/salvador_lacerda_r30b102_corpo_encosta_quatro_elevadores.blend'
catpath=root/'world/areas/mvp-centro-lacerda/blender-revisions.json';cat=json.loads(catpath.read_text())
assert base.name=='salvador_lacerda_r30b101_pavimentos_estruturais.blend' and not dest.exists()
assert q['revision']=='R30B.102' and r['pid']==os.getpid() and r['clearance_reconciled']
with base.open('rb') as f:parenthash=hashlib.file_digest(f,'sha256').hexdigest()
assert parenthash==cat['authoring_source']['sha256']
assert hashlib.sha256((root/'world/geographic-reference.json').read_bytes()).hexdigest()==r['ssot_sha256']
assert shutil.disk_usage(root).free>base.stat().st_size*2
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));sig=h['signature']
for n,s in r['preserved_signatures'].items():assert sig(bpy.context.scene.objects[n])==s,n
assert sig(bpy.context.scene.objects['MVP | terreno corrigido | colisão estática'])==r['terrain_after_signature']
for row in r['added']:assert sig(bpy.context.scene.objects[row['object']])==row['after']['signature'],row['object']
scene=bpy.context.scene;scene['lacerda_revision']='R30B.102 | corpo exterior/encosta e quatro equipamentos proxy'
scene['boas_historic_movement_enabled']=False;scene['boas_four_lifts_contract']='world/areas/mvp-centro-lacerda/lacerda-four-lifts.json'
scene['boas_four_lifts_pedestrian_route']='NOT_INTEGRATED';scene['boas_historic_witnesses']=27
text=bpy.data.texts.get('BOAS | quatro elevadores | iniciar.py') or bpy.data.texts.new('BOAS | quatro elevadores | iniciar.py')
text.clear();text.write("from pathlib import Path\nimport bpy, runpy\nroot = Path(bpy.data.filepath).resolve().parent.parent\nrunpy.run_path(str(root / 'automation/blender/play_lacerda_four_lifts.py'))\n")
text.use_module=False
r.update(file=dest.relative_to(root).as_posix(),parent_sha256=parenthash,saved=True)
(out/'application.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
profilepath=root/'world/areas/mvp-centro-lacerda/corridor-slice.json';profile=json.loads(profilepath.read_text())
profile.setdefault('revision_history',[]).append({'revision':'R30B.102','scope':'Exterior/alas/contensão documental; recorte local do terreno no núcleo antigo; quatro equipamentos GAMEPLAY_PROXY com CCD independente','movement_enabled':False,'evidence':'docs/reports/blender/lacerda-exterior-b102/application.json'})
profilepath.write_text(json.dumps(profile,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
with dest.open('rb') as f:r['sha256']=hashlib.file_digest(f,'sha256').hexdigest()
(out/'application.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
entry={'file':r['file'],'revision':'R30B.102','parent_file':r['parent_file'],'sha256':r['sha256'],'scene':scene.name,
 'status':'architectural_candidate_with_four_gameplay_lifts','production_ready':False,'evidence':'docs/reports/blender/lacerda-exterior-b102/application.json',
 'notes':'Resíduos R10 arquivados; corpo exterior separado do núcleo; encontro14/23 candidato; quatro equipamentos provisórios com gates individuais; não certificação/produção.'}
cat['revisions'].append(entry)
for key in ('authoring_source','validation_source'):cat[key]=entry.copy()
catpath.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'file':r['file'],'sha256':r['sha256'],'equipment':[{'id':v['id'],'status':v['status']} for v in q['equipment']]}))
