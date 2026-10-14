"""Catalogação das duas fotografias fornecidas, sem promover mídia para release."""
import json,hashlib,shutil,argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
parser=argparse.ArgumentParser();parser.add_argument('photos',nargs=2,type=Path);args=parser.parse_args()
mp=ROOT/'world/areas/mvp-centro-lacerda/media-manifest.json';m=json.loads(mp.read_text(encoding='utf8'));pp=ROOT/'world/data-provenance.json';p=json.loads(pp.read_text(encoding='utf8'));ids=[];records=[]
for i,photo in enumerate(args.photos,1):
    digest=hashlib.sha256(photo.read_bytes()).hexdigest();logical='mvp-centro-lacerda/elevador-lacerda/estrutura-encosta-'+digest[:12]+'.png';dest=ROOT/'world-reference'/logical;dest.parent.mkdir(parents=True,exist_ok=True)
    if not dest.exists():shutil.copyfile(photo,dest)
    assert hashlib.sha256(dest.read_bytes()).hexdigest()==digest
    mid='elevador-lacerda-detail-'+digest[:12];rid='source:lacerda-exterior-proportions-photo-'+digest[:12];ids.append(rid)
    if not any(x['media_id']==mid for x in m['media']):m['media'].append({'media_id':mid,'location_id':'elevador-lacerda','source_type':'other','usage_class':'REFERENCIA_INTERNA','view':'detail','capture':None,'storage':{'logical_path':logical,'sha256':digest},'provenance':{'source_name':'Fotografia enviada pelo usuário em 07/10/2026','license_status':'unknown','license':None,'source_url':None,'notes':'Autoria e data da captura desconhecidas; referência externa, sem medição métrica pela perspectiva.'},'notes':['Comprova relação visual entre torre junto à encosta, corpo superior e galeria; proporções métricas continuam candidatas.']})
    entry={'resource_id':rid,'provider':'Usuário / autoria da fotografia desconhecida','dataset':'Vista exterior '+str(i)+' do conjunto Elevador Lacerda','capture_date':None,'bounds':None,'raw_files':[{'path':'world-reference/'+logical,'sha256':digest}],'derived_files':[],'usage_class':'REFERENCIA_INTERNA','release_status':'DEV_REFERENCE_ONLY','purpose':'Comparação qualitativa dos volumes e limites permanentes; não textura final ou levantamento físico','dependencies':[],'kind':'reference','media_id':mid}
    if not any(x['resource_id']==rid for x in p['resources']):p['resources'].append(entry)
    records.append({'media_id':mid,'resource_id':rid,'sha256':digest,'file':'world-reference/'+logical})
derived={'resource_id':'derived:lacerda-encosta-support-b85','provider':'Bay of All Saints / adequação local autoral','dataset':'Compatibilização lateral do apoio e dependências com corpo superior existente','capture_date':'2026-10-07','bounds':None,'raw_files':[],'derived_files':['blender/salvador_lacerda_r30b85_apoio_encosta_proporcoes.blend','docs/reports/blender/lacerda-proportions-b85/application.json','docs/reports/blender/lacerda-proportions-b85/validation.json'],'usage_class':'PENDENTE_VERIFICACAO','release_status':'REPLACE_BEFORE_RELEASE','purpose':'Melhorar relação estrutural reconhecível; não certificar medidas nem reposicionar torres para obter o vão histórico','dependencies':ids+['source:lacerda-issue22-sucop-17','source:lacerda-issue22-sucop-23','derived:lacerda-upper-glazing-b84'],'kind':'geometry','evidence':'docs/LACERDA_EXTERNAL_PROPORTIONS_B85_2026-10-07.md'}
if not any(x['resource_id']==derived['resource_id'] for x in p['resources']):p['resources'].append(derived)
mp.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf8');pp.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
out=ROOT/'docs/reports/blender/lacerda-proportions-b85';out.mkdir(parents=True,exist_ok=True);(out/'photo_evidence.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(records,ensure_ascii=False))
