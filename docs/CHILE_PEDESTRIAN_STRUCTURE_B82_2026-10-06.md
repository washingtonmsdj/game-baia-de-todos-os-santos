# Tomé / Rua Chile — estrutura pedonal B82 — 06/10/2026

## Decisão

NO_SCENE_CHANGE; nenhuma B83. B76–B82, SSOT, GAMEPLAY_PROXY e gates históricos preservados. Somente auditoria e correção do apoio volumétrico no auditor numérico; nenhuma mudança no controller B82, calçada, terreno ou helper da cena. Nenhuma promoção para produção.

## Os 17 alertas legados

São 17 segmentos de 10 ways, não 17 objetos. Todos os nós estão presentes no OSM. Classificações finais após revisão de camada:

| Classificação | Segmentos |
|---|---:|
| MISSING_BINDING | 7 |
| VALID_PARTIAL_HELPER | 6 |
| SOURCE_NODE_PRESENT_SURFACE_VALID | 1 |
| NEEDS_REVIEW | 3 |
| SOURCE_NODE_PRESENT_SURFACE_INVALID | 0 |
| OBSOLETE_HELPER | 0 |

O apoio válido é somente nos dois controles do way 1075624458, não prova de segmento inteiro. Os três segmentos 421206045 saíram da classificação superficial por coluna vertical para NEEDS_REVIEW: a genealogia B38 comprova risco de selecionar Montanha em vez do pavimento inferior. Nos seis helpers parciais, ausência de apoio na camada MVP não prova chão ausente em toda a cena. Os sete sem binding referem-se ao prefixo do auditor legado, não à inexistência física da rua.

| Way OSM | Trechos | Classificação |
|---|---:|---|
| 1075624454 | 1 | MISSING_BINDING |
| 1075624458 | 1 | SOURCE_NODE_PRESENT_SURFACE_VALID |
| 154743329 | 1 | VALID_PARTIAL_HELPER |
| 421206045 | 3 | NEEDS_REVIEW |
| 456471269 | 1 | VALID_PARTIAL_HELPER |
| 562005412 | 2 | VALID_PARTIAL_HELPER |
| 656636750 | 1 | VALID_PARTIAL_HELPER |
| 807410410 | 5 | MISSING_BINDING |
| 807410424 | 1 | VALID_PARTIAL_HELPER |
| 978527848 | 1 | MISSING_BINDING |

Detalhes por issue_id, nós, XY, apoio visual/collider, normal, helper, origem e representações equivalentes em `helpers.json`. O gerador R30A7 descartava grupos sem apoio Z; o fato de o nó existir no OSM não autoriza recriar o grupo. Representações B51–B60 encontradas para Contorno/Conceição/Manoel Vitórino estão ocultas e sem papel físico certificado; não foram ativadas como piso alternativo.

## Metadados

Dos 60 NEEDS_REVIEW locais, 44 são largura sem fonte, 11 direção sem fonte e cinco sondagens de apoio. Os 55 de largura/sentido continuam UNKNOWN quando a fonte não informa. Rua Chile 30968017/231091547 possui oneway=yes e lanes=2 na captura; 258560240 possui oneway=no e lanes=2. Esses valores existentes foram registrados como evidência OSM, não inventados como engenharia de faixa. Nenhuma largura real foi derivada de highway ou de perspectiva. Ausência de metadados não impede medir geometria pedonal, mas não libera tráfego.

## Diagnóstico 421206045

Origem encontrada: `automation/blender/correct_conceicao_binding_r38.py` e `docs/reports/blender/conceicao_binding_r30b38.json`. Em B38, o nó 7520527645 do helper foi adaptado do ponto OSM que atingia Montanha para o asfalto inferior do mesmo asset autoral. Registro explícito ADAPT_LOCAL, source_reference_unchanged=true.

Antes: [-148.4208526611328, -150.15419006347656, 56.002235412597656]. Depois: [-150.03884887695312, -150.0146484375, 19.810096740722656]. A B82 coincide exatamente com o ponto posterior. O residual de 1,14143 é distância à linha da referência; o deslocamento entre pontos é aproximadamente 1,624 unidades XY e −36,192139 em Z. Não houve mudança da captura demonstrada: os graphs antigos e atuais possuem o mesmo XY OSM desse nó.

Classificação: KEEP_GAMEPLAY / adaptação local histórica documentada. Não restaurar XY para reduzir residual nem alterar os outros 176 helpers. Esse registro não certifica a ladeira inteira e não elimina seus três alertas de extremidade.

## Sweep e limites

Fonte exportada na mesma janela B82, sem alteração: collider de terreno registrado, visual correspondente e 66 obstáculos externos candidatos com binding de origem. Internos do Lacerda e GAMEPLAY_PROXY não foram usados na validação externa. Calçadas sem binding funcional completo e obstáculos visuais não classificados permanecem limitação de cobertura: resultado do recorte não aprova toda geometria da cidade.

Cápsula r=0,30, H=1,80, step=0,25, skin=0,015; gravidade 9,81; CCD por subdivisão conservadora, tentativas de step/slide e apoio real. O apoio central antigo foi preservado como baseline: eixo Rua Chile passou; sidewalk 1321755864 parou após 8005 movimentos, Misericórdia após 1378, ambos no terrain proxy e sem normal lateral. Penetrações de 15,018 e 15,064 mm estavam apenas 0,018/0,064 mm além do skin: não são prova de erro arquitetônico.

Correção técnica no auditor: apoio pela esfera inferior sobre faces e arestas finitas, skin radial, snap limitado ao step e toda translação sujeita ao CCD; não troca de superfície por terreno invisível. Verificação independente em planos com declives 0,25/0,55 e chão plano retornou distância cápsula–triângulo de 0,315; fora de faces finitas não retorna apoio. Código em `tools/world/character_support.py`, evidência `support_math.json`. Resultado final dos sweeps deve ser lido junto com as limitações de cobertura abaixo.

## Resultado final e gates separados

| Trecho | TOPOLOGY_VALID | SURFACE_VALID | PEDESTRIAN_CLEARANCE_VALID | GAMEPLAY_VALID |
|---|---|---|---|---|
| Eixo OSM Chile, 258560240 → 231091547 → 30968017 | sim, cadeia de nós compartilhados | candidato parcial | não comprovado | não |
| Calçada OSM 1321755864 | sim, somente o way | não reconciliada | não comprovado | não |
| Direção Misericórdia, 803899198 | sim, somente o way | bloqueada no recorte | não comprovado | não |
| Tomé → Barroquinha | componente topológico identificado | pendente | pendente | não |

O eixo passou em 7.743 movimentos com velocidade 2,5 m/s e 60 Hz. É eixo de via, não calçada nem autorização pedonal; a conexão exata com a praça não foi certificada. Portanto **Rua Chile → Tomé permanece parcial**, sem aprovação de corredor completo.

A calçada parou após 4.599 movimentos em XY [97,627372; 47,578813]: apoio da base da cápsula no collider Z=66,676686 contra visual Z=66,616574, diferença 60,112 mm. O limiar QA de correspondência é 50 mm, não tolerância arquitetônica oficialmente medida. Há divergência local que exige reconciliar a fonte das duas superfícies, sem assumir que o visual ou o proxy esteja correto.

Misericórdia parou após 1.535 movimentos. Testemunha XY [99,764333; 45,939965], Z=65,735267, penetração de 27,719 mm em `R30A5 | COLLISION | terrain proxy`. A face tem normal [0,067010; −0,951155; 0,301352], portanto não é chão de apoio com o critério atual. Step de 0,25 m e slide lateral foram tentados; o slide encontrou normal lateral mas seu CCD permaneceu bloqueado. Apoios visual/physical locais diferem apenas 0,953 mm; a cápsula também encontra visual próximo com distância mínima 0,314130 m. Isso sugere uma divergência de **envelope lateral do proxy**, ainda sem identidade comprovada de meio-fio/degrau/estrutura permanente. Classificação NEEDS_REVIEW, não ERROR. Não apagar collider nem achatar terreno.

**Tomé → Pelourinho não foi fechado**: o way testado vai em direção à Misericórdia e não prova chegada ao Pelourinho. **Tomé → Barroquinha permanece topologia apenas**: não foi criada rota física interpolada. O recorte de obstáculos não cobre toda geometria visual não classificada; mesmo um replay numérico aprovado não seria GAMEPLAY_VALID.

Primeira causa histórica esclarecida: adaptação local B38 do helper 421206045, a preservar. Primeiros candidatos atuais de causa estrutural: correspondência visual/collider na calçada e envelope lateral do terrain proxy na ligação Misericórdia. A auditoria localiza as falhas, mas não determina independentemente qual geometria corrigir. Nenhuma alteração da cena autorizada por essas métricas isoladas.

## Revisão e próxima frente

Nenhum dos 162 alertas foi fechado por esta rodada. Nenhuma nova causa comprovada autoriza mover terreno ou recriar calçada. Falhas de cobertura/binding e seleção de nível precisam de triagem física; a adaptação B38 permanece registrada, não revertida. Os 46 grupos de duplicatas e EXPECTED_OVERLAP anteriores não foram tocados.

Próxima região: Pelourinho, usando Misericórdia como ligação estrutural, sem saltar para Lapa. Antes de qualquer aprovação de gameplay, completar vínculos de calçadas/obstáculos e a conexão física da praça aos controles OSM. Toda expansão permanece GREYBOX.

## Evidências

- `docs/reports/world/chile-pedestrian-b82/helpers.json`
- `docs/reports/world/chile-pedestrian-b82/way421206045_diagnosis.json`
- `docs/reports/world/chile-pedestrian-b82/sweeps_central_ray_baseline.json`
- `docs/reports/world/chile-pedestrian-b82/support_math.json`
- `docs/reports/world/chile-pedestrian-b82/sweeps.json`
- `docs/reports/world/chile-pedestrian-b82/contact_diagnosis.json`
- `docs/reports/world/chile-pedestrian-b82/preservation.json`
- `artifacts/chile-pedestrian-b82/physics.npz`: derivado QA, DEV_REFERENCE_ONLY; nunca asset físico de produção.
