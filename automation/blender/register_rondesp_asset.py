"""Registra fonte e referências locais, sem exportar para o runtime."""
import hashlib
import json
import shutil
from pathlib import Path

repo=Path(__file__).resolve().parents[2]
manifest_path=repo/'world/vehicles/media-manifest.json'
manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
refs=[
    ('rondesp-pickup-user-front-left','codex-clipboard-1e4491ac-8ace-49b9-b731-e81fafe1664f.png','oblique_left',None,'Fotografia pequena enviada pelo usuário; origem/autoria externas não verificadas.'),
    ('rondesp-31110-front','codex-clipboard-00749df0-90b5-4206-b06c-ee8b894b39cc.png','oblique_left','https://www.instagram.com/p/DV4fernIZKG/?img_index=1','Captura enviada pelo usuário. viaturas_ba_; fotografia creditada a Sotero Filho. Legenda: Toyota Hilux CD 2.8 2024/2025, Rondesp Leste, prefixo 3.1110.'),
    ('rondesp-31110-rear','codex-clipboard-0b73fbc9-b1fa-4ffc-b7cd-6659f92bb261.png','rear','https://www.instagram.com/p/DV4fernIZKG/?img_index=2','Captura enviada pelo usuário. viaturas_ba_; fotografia creditada a Sotero Filho. Documenta capota, tampas laterais, traseira e inscrições da mesma viatura 3.1110.')
]
for rid,name,view,url,notes in refs:
    src=Path.home()/'AppData/Local/Temp'/name
    dst=repo/'world-reference/vehicles/media'/name
    dst.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(src,dst)
    item={'media_id':rid,'location_id':'vehicle-rondesp-pickup','source_type':'other','usage_class':'REFERENCIA_INTERNA','view':view,'storage':{'logical_path':'vehicles/media/'+name,'sha256':hashlib.sha256(dst.read_bytes()).hexdigest()},'provenance':{'source_name':'Imagem fornecida pelo usuário','license_status':'pending','license':None,'source_url':url,'notes':notes+' Uso para orientação visual; não incorporada como textura.'}}
    manifest['media']=[m for m in manifest['media'] if m['media_id']!=rid]+[item]
manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
report_path=repo/'docs/reports/blender/rondesp_marrom_v03.json'
if report_path.exists():
    report=json.loads(report_path.read_text(encoding='utf-8'))
    catalog_path=repo/'world/vehicles/catalog.json'
    catalog=json.loads(catalog_path.read_text(encoding='utf-8'))
    vehicle={'asset_id':'vehicle-rondesp-pickup','authoring_base':{'file':report['file'],'scene':report['scene'],'sha256':report['sha256']},'variants':[{'variant_id':'rondesp-pickup-marrom','color':'marrom','file':report['file'],'scene':report['scene'],'sha256':report['sha256'],'status':'candidate','reference_ids':[r[0] for r in refs],'scope':'Picape própria baseada nas fotografias enviadas; Hilux CD 2.8 2024/2025 e prefixo 3.1110 conforme legenda. Dimensões candidatas, brasão detalhado pendente.'}]}
    catalog['vehicles']=[v for v in catalog['vehicles'] if v['asset_id']!='vehicle-rondesp-pickup']+[vehicle]
    catalog_path.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Referências Rondesp registradas; fonte catalogada quando salva.')
