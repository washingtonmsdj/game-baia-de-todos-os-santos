"""Cataloga a referência enviada e os locais deste passe de modelagem."""
import json,hashlib,shutil,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[2];area=root/'world/areas/mvp-centro-lacerda';lp=area/'locations.json';d=json.loads(lp.read_text(encoding='utf8'))
items=[('monumento-mario-cravo','Fonte da Rampa do Mercado — Monumento Mário Cravo','monument',None)]
for id in (1263035779,1220650665,1220650754,1220650857,1220650885,1220650874,574235995,574235997):items.append((f'edificio-baixa-osm-{id}',f'Edifício junto ao acesso inferior do Lacerda — OSM {id}','building',id))
for id,name,category,osm in items:
    if any(v['location_id']==id for v in d['locations']):continue
    d['locations'].append({'location_id':id,'name':name,'category':category,'fidelity_class':'A' if category=='monument' else 'B','priority':4,'model_status':'modeling','reference_status':'partial','osm':{'type':'way','id':osm,'verified':False} if osm else None,'position_wgs84':None,'blender_binding':None,'required_views':['front','oblique_left','oblique_right','roof','street_context'] if osm else ['front','left','right','oblique_left','oblique_right','street_context','detail'],'production_rules':{'geometry_must_be_realigned':False,'manual_review_required':True,'notes':['Preservar implantação existente; leitura arquitetônica fotográfica candidata, sem altura levantada.','Não promover approved sem vistas suficientes e comparação direta.']},'notes':['Passe R30B31; referência panorâmica fornecida pelo usuário.']})
lp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
src=Path('C:/Users/TONECOS/AppData/Local/Temp/codex-clipboard-e7c81af1-89b9-4c0f-bf7c-63445fc4739c.png');dst=root/'world-reference/mvp-centro-lacerda/cidade-baixa/user-googlemaps-panorama-2018.png';dst.parent.mkdir(parents=True,exist_ok=True)
sha=hashlib.file_digest(src.open('rb'),'sha256').hexdigest();manifest=json.loads((area/'media-manifest.json').read_text(encoding='utf8'))
if not any(v['storage']['sha256']==sha for v in manifest['media']):
    if dst.exists() and hashlib.file_digest(dst.open('rb'),'sha256').hexdigest()!=sha:raise RuntimeError('Não sobrescrever outra referência')
    shutil.copy2(src,dst)
    cmd=[sys.executable,str(root/'tools/references/register_media.py'),'--area','mvp-centro-lacerda','--location','elevador-lacerda','--file',str(dst),'--media-root',str(root/'world-reference'),'--view','panorama','--source-type','other','--usage-class','REFERENCIA_INTERNA','--source-name','Google Maps — captura enviada pelo usuário; foto creditada a Esteban Brandan (Alma de Aventuras)','--source-url','https://www.google.com/maps/place/Elevador+Lacerda/','--license-status','unknown','--notes','Vista histórica: rodapé indica fevereiro de 2018; cartão indica março de 2019. Data exata não confirmada. Não usar como textura de produção.']
    for loc,view in [('corredor-cidade-baixa','street_context'),('praca-cairu','street_context'),('monumento-mario-cravo','oblique_left')]+[(id,'oblique_left') for id,_,_,osm in items if osm]:cmd+=['--covers',loc+':'+view]
    subprocess.run(cmd,cwd=root,check=True)
print('Locais e referência panorâmica catalogados; nenhuma aprovação de asset.')
