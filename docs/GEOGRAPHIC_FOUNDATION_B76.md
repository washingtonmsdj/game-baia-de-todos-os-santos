# Fundação geográfica de Salvador — B76

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
