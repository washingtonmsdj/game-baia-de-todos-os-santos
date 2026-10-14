# Centro Histórico — triagem estrutural B82 — 06/10/2026

## Resultado

`NO_SCENE_CHANGE`. Nenhuma B83 criada. B76–B82 e SSOT preservados por 25 hashes. Inventário read-only na mesma janela Blender/PID 10684/porta 9876: 6.296 objetos históricos, sem modificar controller ou camada GAMEPLAY_PROXY B82. Nenhuma investigação interna do Lacerda retomada, exportação ou promoção para produção.

Os 714 registros pendentes são do ciclo B40/B41, principalmente auditoria veicular e metadados de tráfego; não são uma lista atual de 714 defeitos urbanos confirmados. A triagem abaixo é uma família de investigação, não um diagnóstico geométrico definitivo. O ledger original conserva todos os estados e aceita uma referência à auditoria derivada.

## Distribuição dos 714 alertas

| Categoria | Quantidade |
|---|---:|
| XY_OFFSET | 0 |
| TOPOLOGY | 0 |
| ROAD_ALIGNMENT | 283 |
| BUILDING_FOOTPRINT | 0 |
| TERRAIN_INTERSECTION | 0 |
| DUPLICATE | 0 |
| LEGACY_PROXY | 117 |
| HEIGHT_UNKNOWN | 55 |
| EXPECTED_OVERLAP | 0 |
| FALSE_POSITIVE | 0 |
| NEEDS_REVIEW | 259 |

ROAD_ALIGNMENT agrupa sondagens de pavimento, curvas e envelopes de veículo/ônibus; não confirma que a rua esteja deslocada. HEIGHT_UNKNOWN agrupa alertas de perfil/declive/torção cuja causa e fidelidade vertical atual não foram certificadas; não significa que todo Z medido seja nulo. LEGACY_PROXY cobre vínculos dos helpers parciais, sem concluir ausência de pavimento. NEEDS_REVIEW inclui limitações de largura/sentido e apoio/colisão a revisar.

Zero em uma categoria significa que não existe alerta desse tipo identificado nesta lista herdada; não prova ausência do problema na cidade. Achados adicionais de footprints e duplicatas aparecem separadamente.

## Distribuição por subárea analítica

Áreas atribuídas pelos pontos/nós OSM dos alertas e proximidade a controles documentados (até 180 unidades Blender), não limites administrativos. Alertas de way inteiro usam centro médio; vias longas podem atravessar mais de uma região. Os demais permanecem no restante do recorte, sem forçar associação ao núcleo.

| Subárea | ROAD_ALIGNMENT | LEGACY_PROXY | HEIGHT_UNKNOWN | NEEDS_REVIEW | Total |
|---|---:|---:|---:|---:|---:|
| BARROQUINHA | 7 | 17 | 2 | 9 | 35 |
| CAIRU_MERCADO | 18 | 0 | 0 | 36 | 54 |
| OTHER_CENTRO_RECUT | 153 | 71 | 12 | 116 | 352 |
| PELOURINHO | 50 | 12 | 11 | 38 | 111 |
| TOME_RUA_CHILE | 55 | 17 | 30 | 60 | 162 |

## Causas compartilhadas

364 alertas têm causa comum documentada na representação ou na fonte, sem provar erro geométrico:

- 89: helpers R30A7 omitem nós quando a sondagem original não encontra apoio. O inventário atual confirma `boas_partial_source: true` e nós não resolvidos para todos; os nós ausentes continuam presentes no OSM. Genealogia: `automation/blender/r30a7_road_graph.py#create_way`. Não conectar a lacuna sem validar a superfície.
- 28: helper não encontrado pelo prefixo/binding exigido no auditor legado. Isso não comprova rua ausente em todas as camadas.
- 187: largura sem tag/fonte documental na captura OSM atual. Não inventar largura.
- 60: direção sem tag explícita. Não assumir mão dupla.

Os outros 350 alertas não receberam causa raiz comprovada. Foram encontrados **0 falsos positivos comprovados dos 714**; isso não transforma os 714 em bugs. Nenhum foi fechado por ausência de evidência.

## Georreferenciamento e topologia

Fit existente reconciliado com `world/geographic-reference.json` pelo guard compartilhado, sem novo transform. 177 helpers com OSM ID explícito conferidos por distância de seus vértices às linhas da referência: 176 dentro de 0,02 unidade Blender, um candidato local — way/421206045, Ladeira da Conceição da Praia — com até 1,14143 unidade. Não há evidência de deslocamento global comum que autorize mover massas ou alterar SSOT. A divergência local exige comparar genealogia/captura antes de editar o helper ou a rua.

Os controles de Rua Chile, Cairu, Pelourinho e Barroquinha participam do mesmo componente da referência OSM por IDs de nós compartilhados. Isso não certifica superfície, permissão pedonal, calçada, nível ou acessibilidade de qualquer rota. Não foram criadas ligações por distância. A auditoria topológica do extrato completo continua sendo referência: 0 features com nós ausentes e 0 footprints abertos; 891 endpoints internos candidatos, 16 near-misses e 3 separações possíveis de nível no extrato inteiro, não 891 bugs do núcleo.

## Sondagem prioritária de apoio

Fontes físicas explícitas do contrato existente: `MVP | terreno corrigido | colisão estática` e `R30A5 | COLLISION | terrain proxy`. Foram sondados os ways 30968017, 231091547, 258560240 (Rua Chile) e 312006925, 1423065746 (Cairu). 210 posições, três apoios por posição (centro e ±0,30): nenhum apoio ausente nessa amostragem; máxima diferença visual/collider **0,004425 m**; nenhum contato excede 0,05 m.

O primeiro processamento integral excedeu timeout; a leitura foi otimizada por recorte de triângulos. O recorte inicial omitia a extremidade de Rua Chile e gerava sete falsos gaps da própria sondagem. Corrigido o recorte derivando bounds de todos os controles + margem de 2 unidades, a leitura foi repetida e todos os apoios encontrados. Esses sete não pertencem aos 714 alertas históricos e não contam como falsos positivos deles. Nenhuma geometria foi preenchida para corrigir a medição.

Sondagem vertical em terreno selecionado não é CCD do personagem: obstáculos laterais, meios-fios, degraus e acesso Mercado ainda precisam de validação física. Nenhuma liberação de navegação resulta deste relatório.

## Footprints, sobreposições e duplicação

Quatro candidatos adicionais de sobreposição fonte: dois caminhos cobertos/passagem de edifício (684497773 e 1426173135 com footprint 498407319), classificados como EXPECTED_OVERLAP candidato; escadaria 1317127244 em relação 18073836 e caminho 312006925 em footprint 1263035777 continuam NEEDS_REVIEW. Teste usa nós estritamente internos a polígonos 2D; não cobre toda interseção segmentar/triangular e não determina Z ou obstrução real. Não reabrir fidelidade interna do Lacerda por esse achado.

46 grupos/95 objetos apresentam hash de geometria e transform idênticos dentro do recorte analítico. São candidatos: referência, visual e collider separados podem compartilhar geometria legitimamente. Nenhuma duplicação física indevida foi comprovada ou apagada. Terreno atravessando edifícios requer função de camada e teste triangular/apoio; AABB ou sobreposição 2D isolada não autoriza rebaixar terreno ou mover edifícios.

## Continuidade e bloqueios

- Tomé → Lacerda → Cairu: GAMEPLAY_PROXY B82 preservado; validação de ida/volta anterior mantém seu escopo aproximado e substituição obrigatória. LACERDA_VERTICAL histórico continua BLOCKED_EXTERNAL_EVIDENCE; 27 testemunhas UNRESOLVED.
- Rua Chile → Tomé: apoio/coerência visual-collider favoráveis na amostragem; calçadas e sweep pedonal ainda não certificados.
- Tomé → Pelourinho/Barroquinha: conexão topológica na fonte confirmada; superfície pedonal, escadas e acesso de cada trecho continuam pendentes.
- Cairu → entrada física do Mercado: gate de entrada/connector ainda não certificado. Não declarar chegada perto do prédio como chegada à entrada.
- Tráfego histórico continua desconhecido; regra provisória da B82 permanece separada.
- Lapa/Campo da Pólvora, Dique e Fonte Nova: GREYBOX, sem mudança nesta rodada.

## Próximo cluster e correções

Correções de cena aplicadas: **0**. Alterações somente em ferramentas de auditoria, relatório/proveniência e índice de triagem do ledger. Próximo cluster prioritário: **Tomé/Rua Chile**, com 162 alertas — conferir as 17 pendências de helpers legados contra apoio atual e limites físicos, depois validar calçada/envelope pedonal e conexões reais em direção à Misericórdia/Pelourinho e Barroquinha. A divergência 421206045 é candidata local separada; não aplicar offset comum em 176 helpers coerentes.

Não criar revisão enquanto houver apenas auditoria. Nenhum fundamento para correção de terreno/transform coletivo foi comprovado. Após fechar estrutura do Centro, ordem: Lapa/Campo → Dique → Fonte Nova, sempre GREYBOX.

## Evidências

- `docs/reports/world/centro-structural-triage/triage.json`: cada um dos 714 IDs, categoria, subárea, causa/evidência.
- `scene_b82.json`: inventário MCP read-only.
- `priority_support_b82.json`: amostras e metadados parciais dos helpers.
- `source_footprint_candidates.json` e `duplicate_candidates.json`: candidatos adicionais separados.
- `preservation.json`: 25 hashes protegidos íntegros.
- Proveniência `derived:centro-structural-triage-b82`, DEV_REFERENCE_ONLY; sem recursos temporários em produção.
