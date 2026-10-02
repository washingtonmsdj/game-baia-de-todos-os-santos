"""Cataloga as nove capturas fornecidas; sem pesquisa ou textura fotográfica."""
import json,hashlib,shutil
from pathlib import Path
root=Path(__file__).resolve().parents[2];area=root/'world/areas/mvp-centro-lacerda'
path=area/'media-manifest.json';manifest=json.loads(path.read_text(encoding='utf8'))
items=[
('b03b2ab2-aed9-4374-b1ff-50c989906cde','oblique_left','Paulo Gomes','cartão fev/2019; rodapé jan/2019'),
('06c40270-c664-428f-b8d9-17fdf6697f1f','front','MuySandy OK','dez/2019; vegetação e instalação natalina ocultam parte da fachada'),
('f97edae3-f69a-498b-8447-e0c5d64aeaa1','oblique_right','Ivan Newton','mar/2020'),
('70840d30-aa99-4ec7-a73c-1a2533071258','right','Raul Guerrero Ávila','out/2021'),
('a14cbfd6-07f5-49c2-a33f-3c938fd5a0f8','oblique_right','Alexandre Sousa Santos','out/2022'),
('4392a820-701c-408b-afa5-ebf72f11097d','street_context','Lancha Salvador','fev/2023'),
('6650de34-8d30-4771-989c-ee5412f856ca','panorama','carlos reis','out/2019'),
('a384bf2b-19ce-4d43-8a9b-3e6b34dba903','front','Ricardo Silva','nov/2018'),
('49b26637-ecdc-4d66-89f8-dec69989add9','detail','Francilene Fonseca','out/2025; galerias sob a Prefeitura no lado oposto ao palácio')]
ids=[]
for stem,view,credit,date_note in items:
    src=Path('C:/Users/TONECOS/AppData/Local/Temp')/('codex-clipboard-'+stem+'.png')
    sha=hashlib.file_digest(src.open('rb'),'sha256').hexdigest()
    found=next((x for x in manifest['media'] if x['storage']['sha256']==sha),None)
    if not found:
        loc='praca-tome-de-sousa' if view=='detail' else 'palacio-rio-branco'
        logical=f'mvp-centro-lacerda/palacio-rio-branco/captura-{sha[:12]}.png'
        dst=root/'world-reference'/logical;dst.parent.mkdir(parents=True,exist_ok=True)
        if not dst.exists():shutil.copy2(src,dst)
        found={'media_id':f'{loc}-{view}-{sha[:12]}','location_id':loc,'source_type':'other','usage_class':'REFERENCIA_INTERNA','view':view,'capture':None,'storage':{'logical_path':logical,'sha256':sha},'provenance':{'source_name':'Google Maps — captura enviada pelo usuário; crédito visível: '+credit,'license_status':'unknown','license':None,'source_url':'https://www.google.com/maps/place/Elevador+Lacerda/','notes':'Data indicada na interface: '+date_note+'; dia e pose não verificados.'},'notes':['Modelagem arquitetônica R30B34. Não usar como textura de produção; nenhuma pesquisa nova.','Excluir pessoas, instalações temporárias e objetos que ocultam elementos permanentes.']}
        manifest['media'].append(found)
    for loc,v in [('praca-tome-de-sousa','detail'),('elevador-lacerda','street_context')]:
        if (loc,v)!=(found['location_id'],found['view']) and not any(x['location_id']==loc and x['view']==v for x in found.get('coverage',[])):
            found.setdefault('coverage',[]).append({'location_id':loc,'view':v,'notes':'Encosta, contenção e galerias visíveis; dimensões não levantadas.'})
    ids.append(found['media_id'])
manifest['media'].sort(key=lambda x:(x['location_id'],x['view'],x['media_id']))
path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
out=root/'artifacts/palacio-rio-branco/reference_pass.json';out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps({'media_ids':ids,'status':'REFERENCIA_INTERNA'},indent=2),encoding='utf8')
print(json.dumps({'registered_or_reused':len(ids),'media_ids':ids}))
