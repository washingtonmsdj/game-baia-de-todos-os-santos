"""Reutiliza a foto já catalogada; adiciona cobertura sem duplicar a imagem."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[2];area=root/'world/areas/mvp-centro-lacerda'
lp=area/'locations.json';d=json.loads(lp.read_text(encoding='utf8'))
mp=area/'media-manifest.json';m=json.loads(mp.read_text(encoding='utf8'))
photo=next(x for x in m['media'] if x['media_id']=='elevador-lacerda-panorama-783a31279c0d')
for oid in (1263035780,1220650507,1220650503):
    location=f'edificio-baixa-osm-{oid}'
    if not any(x['location_id']==location for x in d['locations']):
        d['locations'].append({'location_id':location,'name':f'Edifício Cidade Baixa — OSM {oid}','category':'building','fidelity_class':'B','priority':4,'model_status':'modeling','reference_status':'partial','osm':{'type':'way','id':oid,'verified':False},'position_wgs84':None,'blender_binding':None,'required_views':['front','oblique_left','oblique_right','roof','street_context'],'production_rules':{'geometry_must_be_realigned':False,'manual_review_required':True,'notes':['Planta OSM existente preservada; correspondência fotográfica candidata.','Altura proporcional à foto, não medida; não aprovar com apenas a vista panorâmica.']},'notes':['Passe R30B33, fonte B32; fachada observável na foto enviada pelo usuário.']})
    if not any(x['location_id']==location and x['view']=='oblique_left' for x in photo.get('coverage',[])):
        photo.setdefault('coverage',[]).append({'location_id':location,'view':'oblique_left','notes':'Associação fotográfica candidata; implantação pela parcela existente, sem inventar footprint.'})
lp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8');mp.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Três locais candidatos e cobertura na mesma foto; nenhum binário duplicado ou aprovação nova.')
