"""Catalogação e diagnóstico documental; não modifica cena nem SSOT."""
import argparse,hashlib,json,math,shutil
from pathlib import Path
root=Path(__file__).resolve().parents[2]
parser=argparse.ArgumentParser();parser.add_argument('photos',nargs=4,type=Path);args=parser.parse_args()
mp=root/'world/areas/mvp-centro-lacerda/media-manifest.json';pp=root/'world/data-provenance.json'
m=json.loads(mp.read_text(encoding='utf8'));p=json.loads(pp.read_text(encoding='utf8'));records=[]
for photo in args.photos:
    digest=hashlib.sha256(photo.read_bytes()).hexdigest();logical=f'mvp-centro-lacerda/elevador-lacerda/conjunto-torres-{digest[:12]}.png'
    dest=root/'world-reference'/logical;dest.parent.mkdir(parents=True,exist_ok=True)
    if not dest.exists():shutil.copyfile(photo,dest)
    assert hashlib.sha256(dest.read_bytes()).hexdigest()==digest
    mid='elevador-lacerda-detail-'+digest[:12];rid='source:lacerda-exterior-photo-'+digest[:12]
    if not any(r['media_id']==mid for r in m['media']):m['media'].append({'media_id':mid,'location_id':'elevador-lacerda','source_type':'other','usage_class':'REFERENCIA_INTERNA','view':'detail','capture':None,'storage':{'logical_path':logical,'sha256':digest},'provenance':{'source_name':'Imagem fornecida pelo usuário em 07/10/2026','license_status':'unknown','license':None,'source_url':None,'notes':'Autor e captura desconhecidos; legendas sobrepostas não são evidência dimensional.'},'notes':['Referência qualitativa das duas torres, orientação, passarela e bloco superior; sem medição por perspectiva.']})
    if not any(r['resource_id']==rid for r in p['resources']):p['resources'].append({'resource_id':rid,'provider':'Usuário / autoria desconhecida','dataset':'Exterior do Elevador Lacerda','capture_date':None,'bounds':None,'raw_files':[{'path':'world-reference/'+logical,'sha256':digest}],'derived_files':[],'usage_class':'REFERENCIA_INTERNA','release_status':'DEV_REFERENCE_ONLY','purpose':'Comparação qualitativa com SUCOP 12/17/23','dependencies':[],'kind':'reference','media_id':mid})
    records.append({'resource_id':rid,'sha256':digest,'logical_path':logical})
data=json.loads((root/'artifacts/lacerda-proportions/sheet17-vectors.json').read_text())
curve=lambda i:next(r for r in data['items'] if r['kind']=='curve' and r['index']==i)
a,b=curve(1682)['points'][12:14]
segments=[(u,v) for u,v in zip(curve(1780)['points'],curve(1780)['points'][1:]) if 700<math.dist(u,v)<1100]
assert len(segments)==2
u,v=segments[0];angle=lambda x,y:math.degrees(math.atan2(y[1]-x[1],y[0]-x[0]))%180
difference=abs(angle(a,b)-angle(u,v));difference=min(difference,180-difference)
out=root/'docs/reports/blender/lacerda-proportions-b85'
report={'scene_changed':False,'photos':records,'drawing':'source:lacerda-issue22-sucop-17','documentary_orientation':{'status':'CANDIDATE_SEGMENT_COMPARISON_NOT_REGISTERED_TO_SCENE','shaft_curve_index':1682,'shaft_segment':[a,b],'longitudinal_curve_index':1780,'longitudinal_segment':[u,v],'acute_difference_degrees':difference,'note':'Não é rotação autorizada da torre: conferir correspondência física e encontro da passarela.'},'printed_dimensions_m':[5.20,1.99,2.20],'printed_area_m2':{'upper_salon':117.50,'upper_exit_circulation':86.61,'upper_entry_circulation':61.93,'lower_lobby':265.56,'lower_tunnel_circulation':90.99},'accepted_drawing_to_ssot_transform':None,'all_architectural_dimensions_known':False,'full_model_correction_completed':False,'production_ready':False}
(out/'plan_review_20261007.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
mp.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf8');pp.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
doc=root/'docs/LACERDA_EXTERNAL_PROPORTIONS_B85_2026-10-07.md'
doc.write_text(doc.read_text(encoding='utf8').replace('5,20 / 1,99 / 2,00','5,20 / 1,99 / 2,20'),encoding='utf8')
print(json.dumps({'photos_catalogued':len(records),'candidate_relative_angle':difference,'scene_changed':False}))
