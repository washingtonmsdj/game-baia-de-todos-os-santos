"""Três referências novas fornecidas pelo usuário; somente referência interna."""
import hashlib,json,shutil
from pathlib import Path
root=Path(__file__).resolve().parents[2];path=root/'world/areas/mvp-centro-lacerda/media-manifest.json';r=json.loads(path.read_text(encoding='utf8'));ids=[]
for stem,view,credit,date in [('7b789140-cfe0-4cff-a0c3-fe69e2d990cc','detail','Paula Monte Verde','Vídeo jan/2023; frame da fachada envidraçada do apoio'),('6eca5fd8-fe2b-4119-ba9b-9fd790c08508','panorama','Arnaldo Rodrigues do Prado','Cartão out/2019; rodapé nov/2019; datas divergentes'),('54231ad7-4d0c-4a7c-9611-8761089062aa','street_context','Esteban Brandan (Alma de Aventuras)','Cartão mar/2019; rodapé fev/2018; datas divergentes')]:
    src=Path('C:/Users/TONECOS/AppData/Local/Temp')/f'codex-clipboard-{stem}.png'
    with src.open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
    item=next((x for x in r['media'] if x['storage']['sha256']==sha),None)
    if not item:
        logical=f'mvp-centro-lacerda/elevador-lacerda/detalhe-{sha[:12]}.png';dst=root/'world-reference'/logical;dst.parent.mkdir(parents=True,exist_ok=True)
        if not dst.exists():shutil.copy2(src,dst)
        item={'media_id':f'elevador-lacerda-{view}-{sha[:12]}','location_id':'elevador-lacerda','source_type':'other','usage_class':'REFERENCIA_INTERNA','view':view,'capture':None,'storage':{'logical_path':logical,'sha256':sha},'provenance':{'source_name':'Google Maps — captura enviada pelo usuário; crédito visível: '+credit,'license_status':'unknown','license':None,'source_url':'https://www.google.com/maps/place/Elevador+Lacerda/','notes':date+'. Pose e dimensões não verificadas.'},'coverage':[{'location_id':'praca-tome-de-sousa','view':'street_context','notes':'Galerias, barranco e contenção visíveis.'}],'notes':['Corrigir proporções e estrutura; nenhuma licença de textura de produção. Não reproduzir pessoas, obras, veículos ou instalações temporárias.']};r['media'].append(item)
    ids.append(item['media_id'])
r['media'].sort(key=lambda x:(x['location_id'],x['view'],x['media_id']));path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8');out=root/'artifacts/palacio-rio-branco/reference_detail_r35.json';out.write_text(json.dumps({'media_ids':ids,'usage_class':'REFERENCIA_INTERNA'},ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'media_ids':ids},ensure_ascii=False))
