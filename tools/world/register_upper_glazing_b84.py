"""Registra evidência fornecida e a candidata B84, sem promover para produção."""
import json,hashlib,shutil,argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
parser=argparse.ArgumentParser();parser.add_argument('attachment',type=Path);attachment=parser.parse_args().attachment
digest=hashlib.sha256(attachment.read_bytes()).hexdigest()
logical='mvp-centro-lacerda/elevador-lacerda/fechamento-envidracado-'+digest[:12]+'.png'
target=ROOT/'world-reference'/logical;target.parent.mkdir(parents=True,exist_ok=True)
if not target.exists():shutil.copyfile(attachment,target)
assert hashlib.sha256(target.read_bytes()).hexdigest()==digest
mid='elevador-lacerda-detail-'+digest[:12]
manifestpath=ROOT/'world/areas/mvp-centro-lacerda/media-manifest.json';manifest=json.loads(manifestpath.read_text(encoding='utf8'))
if not any(m['media_id']==mid for m in manifest['media']):
    manifest['media'].append({'media_id':mid,'location_id':'elevador-lacerda','source_type':'other','usage_class':'REFERENCIA_INTERNA','view':'detail','capture':None,'storage':{'logical_path':logical,'sha256':digest},'provenance':{'source_name':'Fotografia enviada pelo usuário em 06/10/2026','license_status':'unknown','license':None,'source_url':None,'notes':'Autor e data da foto desconhecidos. Referência visual de desenvolvimento, não textura final.'},'notes':['Faixa envidraçada e esquadrias claras contornam volumes junto à passarela.','A foto não comprova medidas, espessuras ou número exato de módulos.']})
manifestpath.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
pp=ROOT/'world/data-provenance.json';p=json.loads(pp.read_text(encoding='utf8'));sourceid='source:lacerda-upper-glazing-photo-20261006'
new=[{'resource_id':sourceid,'provider':'Usuário / autoria da fotografia desconhecida','dataset':'Foto exterior do fechamento envidraçado do Elevador Lacerda','capture_date':None,'bounds':None,'raw_files':[{'path':'world-reference/'+logical,'sha256':digest}],'derived_files':[],'usage_class':'REFERENCIA_INTERNA','release_status':'DEV_REFERENCE_ONLY','purpose':'Comparação do padrão de vidro/esquadria, sem medição por perspectiva','dependencies':[],'kind':'reference','media_id':mid}, {'resource_id':'derived:lacerda-upper-glazing-b84','provider':'Bay of All Saints / malha autoral e referência enviada','dataset':'Dois retornos envidraçados com lambris reconciliados','capture_date':'2026-10-06','bounds':None,'raw_files':[],'derived_files':['blender/salvador_lacerda_r30b84_fechamento_envidracado.blend','docs/reports/blender/lacerda-glazing-b84/application.json','docs/reports/blender/lacerda-glazing-b84/validation.json'],'usage_class':'PENDENTE_VERIFICACAO','release_status':'REPLACE_BEFORE_RELEASE','purpose':'Restituir faixa envidraçada visível; proporções e subdivisão aproximadas, sem certificado arquitetônico','dependencies':[sourceid,'derived:lacerda-consolidation-b83'],'kind':'geometry','evidence':'docs/LACERDA_UPPER_GLAZING_B84_2026-10-06.md'}]
for entry in new:
    if not any(r['resource_id']==entry['resource_id'] for r in p['resources']):p['resources'].append(entry)
pp.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'media_id':mid,'sha256':digest,'raw_file':'world-reference/'+logical},ensure_ascii=False))
