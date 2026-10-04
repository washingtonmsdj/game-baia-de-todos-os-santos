"""Registra explicitamente a fonte V04 e as referências de contorno utilizadas."""
import json,hashlib,shutil
from pathlib import Path
repo=Path(__file__).resolve().parents[2]
path=repo/'world/vehicles/media-manifest.json';manifest=json.loads(path.read_text(encoding='utf-8'))
dims=json.loads((repo/'world/vehicles/hilux-dimensions.json').read_text(encoding='utf-8'))
refs=[]
for mid,media,view in zip(['hilux-gx-factory-side','hilux-2024-std-dealer-side'],[m for m in dims['media_acquisition'] if 'file' in m],['side','side']):
    refs.append({'media_id':mid,'location_id':'vehicle-rondesp-pickup','source_type':'other','usage_class':'REFERENCIA_INTERNA','view':view,'storage':{'logical_path':media['file'],'sha256':media['sha256']},'provenance':{'source_name':'Toyota / concessionária Toyota','source_url':media['url'],'license_status':'pending','license':None,'notes':'Referência interna de contorno e seções da Hilux; não usada como textura. GX europeu e STD brasileiro distinguidos.'}})
for mid,suffix,view in [('hilux-srx-user-rear','847037','rear'),('hilux-srx-user-front','644939','front'),('hilux-srx-user-side','697928','side')]:
    src=next((Path.home()/'Downloads').glob('*37955116370'+suffix+'.webp'))
    dst=repo/'world-reference/vehicles/hilux'/src.name;shutil.copy2(src,dst)
    refs.append({'media_id':mid,'location_id':'vehicle-rondesp-pickup','source_type':'other','usage_class':'REFERENCIA_INTERNA','view':view,'storage':{'logical_path':'vehicles/hilux/'+dst.name,'sha256':hashlib.sha256(dst.read_bytes()).hexdigest()},'provenance':{'source_name':'Imagem fornecida pelo usuário, Hilux SRX Plus','source_url':None,'license_status':'pending','license':None,'notes':'Contornos compartilhados da cabine e frente. Rodas, alargadores SRX e cromados não transferidos para viatura STD. Não usada como textura.'}})
src=repo/'world-reference/vehicles/hilux/hilux-std-frente.jpg'
if src.exists():refs.append({'media_id':'hilux-std-stock-front','location_id':'vehicle-rondesp-pickup','source_type':'other','usage_class':'REFERENCIA_INTERNA','view':'oblique_front','storage':{'logical_path':'vehicles/hilux/'+src.name,'sha256':hashlib.sha256(src.read_bytes()).hexdigest()},'provenance':{'source_name':'Fotografia Hilux STD reproduzida por AutoPapo','source_url':'https://cdn.autopapo.com.br/box/uploads/2022/09/02185628/toyota-hilux-manual-4x4-1-e1662155837543.jpg','license_status':'pending','license':None,'notes':'Referência interna da máscara STD e curvas; não usada como textura.'}})
for item in refs:manifest['media']=[m for m in manifest['media'] if m['media_id']!=item['media_id']]+[item]
path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
r=json.loads((repo/'docs/reports/blender/rondesp_marrom_v05.json').read_text(encoding='utf-8'))
path=repo/'world/vehicles/catalog.json';catalog=json.loads(path.read_text(encoding='utf-8'))
v=next(v for v in catalog['vehicles'] if v['asset_id']=='vehicle-rondesp-pickup')
v['authoring_base']={k:r[k] for k in ['file','scene','sha256']}
v['variants'][0].update(v['authoring_base']);v['variants'][0]['reference_ids']=['rondesp-31110-front','rondesp-31110-rear']+[m['media_id'] for m in refs]
v['variants'][0]['scope']='Hilux Rondesp 3.1110 V05; casca dianteira contínua esculpida e recortes próprios dos faróis/grade. Medidas nominais Toyota confirmadas. Fidelidade visual ainda candidata; acessórios policiais e brasão detalhado pendentes; sem integração runtime.'
path.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for rel in ['docs/PROJECT_STATUS.md','docs/CODEX_HANDOFF.md','world/vehicles/README.md']:
    p=repo/rel;text=p.read_text(encoding='utf-8')
    note='## 02/10/2026 — Hilux Rondesp: fonte V05\n\nFonte explícita: `blender/assets/vehicles/rondesp-pickup/marrom_v05.blend`, cena `VIATURA | Rondesp Hilux marrom v05`. V01–V04 preservadas como históricas; não retomar por maior sufixo ou mtime.\n\nA V04 foi rejeitada visualmente pelo usuário por continuar quadrada. A V05 substitui a dianteira em painéis fragmentados por casca contínua de seções cúbicas, capô/para-lamas compartilhando curvas e nariz com recortes geométricos da grade e dos faróis. Inscrições conformadas e batentes internos corrigidos. Não declarar equivalência de qualidade ao ônibus nem fidelidade aprovada.\n\nMedidas nominais Toyota em `world/vehicles/hilux-dimensions.json`: comprimento 5,325 m, largura base 1,855 m, altura stock 1,815 m, entre-eixos 3,085 m e pneus 265/65 R17. São especificações do veículo base, separadas de medições da malha e acessórios policiais estimados. Vistas SRX enviadas servem ao contorno; rodas/alargadores da SRX não transferidos à viatura.\n\nStatus `candidate`: aprovação visual final, brasão e mapa exato da camuflagem pendentes; não exportado/integrado no runtime. Relatório `docs/reports/blender/rondesp_marrom_v05.json`; comparação frontal, lateral e oblíqua, sem npm/build/testes gerais nesta etapa, conforme pedido do usuário.\n\n'
    if note.split('\n')[0] not in text:
        title,sep,rest=text.partition('\n');p.write_text(title+'\n\n'+note+rest.lstrip('\n'),encoding='utf-8')
print('V05 e referências registradas; revisões anteriores preservadas.')
