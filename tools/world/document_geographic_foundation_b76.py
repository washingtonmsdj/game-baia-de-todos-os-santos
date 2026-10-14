"""Fechar documentação da rodada com evidências e limitações explícitas."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def read(p):return json.loads((ROOT/p).read_text(encoding='utf8'))
def write(p,d):(ROOT/p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def main():
    validation=read('docs/reports/blender/geographic-foundation/validation_b76.json')
    assert validation['source_reopened'] and not validation['differences']
    before=read('docs/reports/blender/geographic-foundation/foundation_before.json')
    alignment=read('docs/reports/blender/geographic-foundation/scene_reference_alignment_before.json')
    report={'schema':'boas/geographic-foundation-review-v1','revision':'R30B.76','ssot':'world/geographic-reference.json','status':'relative_xy_consolidated_vertical_pending','source':validation['source'],
      'preserved_objects':validation['preserved_objects'],
      'regions':[
       {'region':'Lacerda, Prefeitura, Palácio Rio Branco, Tomé de Souza, Cidade Alta/Baixa, Cairu, Mercado Modelo','status':'existing_core_preserved','geometry_changed':False},
       {'region':'Centro Histórico → Lapa','status':'terrain_and_osm_reference_candidate','roads_finished':False},
       {'region':'Center Lapa','status':'real_footprint_reference','osm_type':'way','osm_id':257113955,'height_verified':False},
       {'region':'Campo da Pólvora','status':'real_park_outline_reference','osm_type':'way','osm_id':257336400,'z':'sampled_candidate_ground'},
       {'region':'Dique do Tororó','status':'real_outline_candidate_water_unfinished_shore','osm_type':'relation','osm_id':15601931,'absolute_water_level_verified':False},
       {'region':'Arena Fonte Nova','status':'real_outer_and_inner_reference','osm_type':'relation','osm_id':3346613,'architecture':'not_detailed'}],
      'corrections':[
       {'classification':'ERROR','issue':'Referência compartilhada não centralizada nos contratos de área','action':'Ambas as áreas apontam para o mesmo SSOT; nenhum deslocamento geométrico'},
       {'classification':'ERROR','issue':'Campo da Pólvora sem binding explícito de local','action':'Polígono OSM 257336400 e location_id catalogados, guia amostrado sobre terreno candidato'},
       {'classification':'ADAPT_LOCAL','issue':'Níveis de detalhe implícitos','action':'Propriedades nas coleções equivalentes existentes; nenhum reparent/renomeação'}],
      'pending':[
       {'classification':'NEEDS_REVIEW','issue':'Datum/escala física absolutos ainda não verificados','action':'Manter coordenadas e Z local existentes; não aplicar ajuste global'},
       {'classification':'SOURCE_LIMITATION','issue':'Margem do Dique aberta, delta máximo terreno/água de 23.992286682128906 unidades','evidence':'docs/reports/blender/centro-expansion/dique_shore_height_b75.json'},
       {'classification':'NEEDS_REVIEW','issue':'Triagem edifício/terreno por AABB','count':len(before['building_ground_review']),'action':'Revisar referência/visibilidade/footprint antes de mover edifícios'},
       {'classification':'NEEDS_REVIEW','issue':'Transforms não uniformes/refletidos','count':len(before['transforms_review']),'action':'Não aplicar escala em massa'},
       {'classification':'NEEDS_REVIEW','issue':'Comparação de bindings e centros','count':alignment['summary']['review_items'],'action':'Proxies, colisores e referências compartilham IDs; revisão não é prova de erro'},
       {'classification':'SOURCE_LIMITATION','issue':'Vias finais da expansão, larguras ausentes, cruzamentos e acessos não aprovados','action':'Permanecem referência; replay de veículo não é teste físico'}],
      'aleph':{'method':'GeoTIFF Float32 do provedor usado pelo commit pinado; OSM existente preservado','evidence':'docs/reports/aleph/centro-lapa-tororo-fontenova/source_summary.json','vertical_candidate_rms':1.6279955763891554,'old_terrarium_vertical_rms':2.4004872,'replaced_scene_dem':False,'absolute_accuracy_verified':False},
      'validation_scope':'Conservação de objetos e reabertura, igualdade de fits, auditorias DEM/XY/topologia anteriores e triagem espacial. Sem npm/build/suíte unitária; sem física ou aprovação de navegação.',
      'next_core_segment':'Praça Tomé de Souza e desembarque superior do Elevador → base do Elevador → Praça Cairu/Mercado Modelo: continuidade Z, pavimento/collision e ligações reais.',
      'next_command_category':'topography_ssot_before_architectural_detail','production_ready':False}
    write('docs/reports/blender/geographic-foundation/review_b76.json',report)
    text='''# Fundação geográfica de Salvador — B76

## Resultado e fonte ativa

B76 salva e reaberta na única janela do Blender, MCP 9876. É fonte de validação; autoria B41 e produção B30 não foram promovidas. B75 preservada. Os 6.068 objetos anteriores conservam geometria, materiais, transforms e vínculos de hierarquia/coleções nos limites do snapshot. Único objeto novo: guia do Campo da Pólvora. Sem detalhe cosmético ou arquitetura nova.

## SSOT

`world/geographic-reference.json` é o contrato único usado pelas áreas MVP e Centro/Lapa/Tororó/Fonte Nova. Origem WGS84 (latitude, longitude): **(-12,974541080934225; -38,51293456074336)**. CRS horizontal EPSG:3857; transformação para Blender: escala **0,9701734817753527** unidade por metro projetado, rotação **-0,05099045551313879°**, translação **(4160622,9992154283; 1409669,6244045058)**. Unidade nominal da cena: 1 metro. Escala Mercator projetada não equivale à distância física no solo. Núcleo e expansão usam exatamente o mesmo fit; nenhuma região foi alinhada visualmente ou refitada.

Referência vertical única: **Z local da cena existente**. Datum absoluto desconhecido (`null`). O GeoTIFF do Aleph fornece um candidato `Z = 0,9765113677655543 × DEM - 3,249092039440118`, RMS robusto 1,628 unidade, com 3.181 amostras rejeitadas entre 9.811. Não aplicado globalmente ou à expansão. A receita Terrarium B74/B75 e suas transições permanecem documentadas; não equivale a altimetria validada. A diferença entre DEMs pode ser limitação de fonte, não erro da geometria jogável.

Aleph não substitui OSM: seu código pinado coleta OSM e terrain de provedores externos. Foram adquiridos seis GeoTIFFs reais com pixel 4,7773 m projetados (Terrarium anterior: 9,5546), preservando tiles, hashes e proveniência. Menor pixel e menor residual não provam resolução nativa, datum ou exatidão física. Captura histórica ausente não foi apresentada como recuperada.

## Regiões e níveis de detalhe

| Região | Implantação atual |
|---|---|
| Lacerda/Prefeitura/Palácio/Tomé/Cairu/Mercado | Núcleo existente integralmente preservado |
| Centro Histórico → Lapa | Terreno candidato e eixos/footprints OSM; vias finais ausentes |
| Center Lapa | Footprint real way 257113955; altura desconhecida |
| Campo da Pólvora | Parque way 257336400, contorno real; Z amostrado da superfície candidata |
| Dique | Relation 15601931, água plana candidata; margem ainda incompleta |
| Fonte Nova | Relation 3346613, contornos externo/interno de referência; sem arquitetura detalhada |

A expansão continua greybox/referência: terreno, água, eixos, footprints e proxies, sem fachadas, interiores ou mobiliário. Não foram fabricados volumes de altura desconhecida. `boas_detail_level` anota WORLD, CITY_MASSING, PLAYABLE_CORE e HERO_ASSETS nas coleções equivalentes existentes; `boas_role` e hierarquia preservados. Fontes continuam GEOGRAPHIC_REFERENCE, sem promoção silenciosa para arte final. Um nome histórico opcional NAV HINTS não correspondeu; não foi criada coleção substituta.

## Auditoria e correções

Corrigidos: contratos regionais sem apontamento canônico único; ausência de binding explícito do Campo da Pólvora; classificação de níveis de detalhe antes implícita. Nenhuma divergência de mesh anterior foi corrigida sem prova suficiente.

118 casos edifício/terreno e 234 transforms exigem revisão; são triagem por AABB e configuração, não 118 interseções graves comprovadas. Referências históricas ocultas entram nessa contagem. Nenhum grupo de duplicados com **mesh compartilhada e matrix igual** foi encontrado; malhas distintas coincidentes não foram auditadas exaustivamente. Um objeto distante é REF_COASTLINE legado. A comparação por OSM ID encontra 902 itens de revisão/847 conflitos de binding; proxies, colisores e fontes podem usar o mesmo ID. Não autoriza mover Hero assets ou parear por nome.

Permanece a margem aberta do Dique, com diferença máxima candidata de 23,9923 unidades entre terreno e água. Não foi criado muro, elevado lago ou achatado terreno para esconder a falta. Vias finais, cruzamentos, caminhabilidade e física de veículo não estão aprovados. Os replays RONDESP anteriores são cinemáticos; não substituem validação física. Nenhuma suíte de testes, npm ou build nesta rodada.

## Decisão para o próximo trabalho

**Ainda corrigir/verificar topografia e SSOT vertical antes de voltar ao detalhe arquitetônico.** Primeiro fechar o trecho Praça Tomé de Souza/desembarque superior do Lacerda → base do Elevador → Cairu/Mercado: relações de altura, transições do chão, colisão e circulação real. A expansão permanece secundária; seu bloqueio específico é o perfil hidrológico da margem do Dique e as vias finais. Não declarar Salvador pronta ou fidelidade absoluta nesta revisão.

Evidências: `docs/reports/blender/geographic-foundation/{application_b76,validation_b76,review_b76,foundation_before,scene_reference_alignment_before,vertical_fit_aleph}.json`; aquisição em `docs/reports/aleph/centro-lapa-tororo-fontenova/`. Guardas de transformação em `tools/georef/world_reference.py`; pipeline estrutural aceita `--geographic-ssot world/geographic-reference.json` e recusa fit regional divergente.
'''
    (ROOT/'docs/GEOGRAPHIC_FOUNDATION_B76.md').write_text(text,encoding='utf8')
    section='''## 05/10/2026 — B76: contrato geográfico único; vertical ainda pendente

B76 salva/reaberta via MCP 9876; 6.068 objetos anteriores conservados, núcleo intacto. `world/geographic-reference.json` centraliza o fit XY compartilhado e Z local candidato; contratos das duas áreas usam esse SSOT. Incluído Campo da Pólvora pelo way 257336400. Níveis de detalhe anotados nas coleções existentes; expansão permanece greybox/referência. Aleph GeoTIFF adquirido e auditado com proveniência, sem substituir silenciosamente DEM/OSM. Datum, margem do Dique e vias finais ainda pendentes. Autoria B41/produção B30 mantidas.

Relatório: `docs/GEOGRAPHIC_FOUNDATION_B76.md`; validação: `docs/reports/blender/geographic-foundation/validation_b76.json`. Próxima prioridade: topografia e continuidade Tomé de Souza → Lacerda → Cairu/Mercado, antes de detalhe arquitetônico. Sem npm/build/suíte unitária ou aprovação de física.

'''
    for p in ('docs/PROJECT_STATUS.md','docs/CODEX_HANDOFF.md','docs/CODEX_STRUCTURE_HANDOFF.md'):
        path=ROOT/p;content=path.read_text(encoding='utf8')
        if '## 05/10/2026 — B76:' not in content:path.write_text(section+content,encoding='utf8')
    p='world/areas/centro-lapa-tororo-fontenova/README.md';path=ROOT/p;content=path.read_text(encoding='utf8')
    if 'GEOGRAPHIC_FOUNDATION_B76' not in content:path.write_text(content+'\nReferencial único e decisão B76: `docs/GEOGRAPHIC_FOUNDATION_B76.md`. Campo da Pólvora incluído como referência real; expansão sem detalhamento. Z absoluto, margem do Dique e vias finais continuam pendentes.\n',encoding='utf8')
    print(json.dumps({'revision':'R30B.76','verdict':report['status'],'next':report['next_command_category']},ensure_ascii=False))
if __name__=='__main__':main()
