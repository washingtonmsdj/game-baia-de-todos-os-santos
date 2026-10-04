# Handoff do Codex — Fidelidade Estrutural

## 04/10/2026 — B41: perfil derivado da Rua da Misericórdia

Autoria candidata: `blender/salvador_lacerda_r30b41_perfil_misericordia.blend`, SHA-256 `5578d54b8c8bdba81216f12745bb3e8a90e38fdec1ae857d17fe5401f38434ef`, pai B40 preservado; produção/runtime continuam B30. A causa do alerta de apoio em `way-803899198-seg-1` foi identificada no helper R30A7: Z era interpolado linearmente entre apenas três nós OSM, enquanto o pavimento da Misericórdia tem perfil vertical intermediário não linear. Reaplicar o transform do terreno foi descartado por prova: o residual mediano dos helpers passaria de ~0,18 m para ~3,38 m.

A correção `ERROR` alterou somente `R30A7 | ROAD | 803899198`: 3 → 224 pontos, drape derivados a cada ≤0,5 m sobre material de via, mantendo os três nós OSM, XY fonte e clearance de 0,18 m. Os 5.453 componentes protegidos permaneceram idênticos; pavimento visual, colisor, largura e runtime não foram alterados. A B41 foi salva e reaberta antes da prova final.

Auditoria integral: 743 segmentos e 73.532 apoios de roda. `center_support_missing` caiu de 86 para 66, exatamente as 20 ocorrências do segmento alvo; `unresolved_endpoint_binding` permaneceu 89. Nenhum outro segmento mudou seu conjunto de issues. A Misericórdia ainda não está aprovada: no segmento corrigido permanecem `crossfall_review=7`, `grade_review=6`, `vertical_discontinuity=1` e `wheel_outside_pavement=1`. Esses valores agora refletem a superfície funcional real e não devem ser zerados por smoothing/offset artificial.

A prova direta de largura B39→B41 comparou os 743 segmentos: delta máximo de largura 0 m, mesma assinatura de malha/material/transform da superfície viária e apenas 0,000618 m de diferença Z numa estação já não resolvida. O contrato de transporte foi regenerado com essa prova: 187 ways, 743 segmentos, 119 vias explicitamente de mão única, 8 explicitamente bidirecionais e 60 sem direção confirmada; 11 paradas OSM e a relação 0429 continuam referências candidatas. O gate permanece `needs_review`, `pending_checks=977`, `production_ready=false`.

Histórico: o issue específico `center_support_missing` da Misericórdia foi confirmado como resolvido após reabertura e auditoria completa; grade, crossfall, descontinuidade e roda fora do pavimento permanecem pendentes. Evidências: `docs/reports/blender/misericordia_profile_r30b41.json`, `docs/reports/blender/road_width_preservation_b39_b41.json`, `docs/reports/blender/rondesp_network_current.json`, `world/areas/mvp-centro-lacerda/transport-network.json` e `road-corrections.json`.

Próximo foco: revisar a geometria funcional/limites da Misericórdia para entender grade e crossfall sem deformação global; depois continuar bindings/apoios restantes, largura real/faixas, conversões e ônibus.


## 04/10/2026 — B40: colisor, larguras e fluxo viário candidato

Autoria candidata `blender/salvador_lacerda_r30b40_fluxos_e_colisao.blend`, SHA-256 `99ecf2a8a091fdbc05d9f4cd28dbecfe3fca467307b8c1f0c3ffd7729943172a`, pai B39 preservado; produção permanece B30. Aplicação por MCP 9876, na única janela PID 19576. Corrigidos 36 contatos locais: erro máximo 0.4969 → 0.0353 m. Refino de faces e seis apoios inseridos, sem deslocar terreno visual ou alargar ruas. 5.452 componentes protegidos preservados; proxy final finito, sem triângulos degenerados. Reabertura confirmou os contatos e a passagem da Montanha (798 frames, 3.192 apoios, zero ausente). Captura interna real conferida em `artifacts/roads/rondesp/b40-driver.png`.

OSM original conferido: 187 ways; 119 com mão única explícita, 8 com mão dupla explícita, 60 sem `oneway`. Nenhuma largura numérica cadastrada. Medidos 1.732 cortes transversais do pavimento autoral; não são medidas reais verificadas. Divisão igual de faixas gera apenas guias candidatas de revisão em mão única: 159 splines separadas em `QA B40 | FLUXOS CANDIDATOS`, fora da exportação. Sem inventar distribuição bidirecional. A cena de largura B39 foi reaproveitada com prova de pavimento visual preservado na B40.

Registrados 11 nós de ônibus (bonde excluído), relação 0429 Barra–Iapi parcial e restrição de conversão. Posições de parada e vizinhos são candidatos, sem binding; itinerário atual não confirmado. Ônibus prefere faixa direita no sentido de deslocamento, com exceções registradas; portas à direita precisam de calçada/plataforma acessível. Largura nominal do ônibus 2,55 m e folga de 0,15 m por lado são probes; 16 segmentos apontam revisão de faixa candidata estreita, sem alargamento automático. Física/envelope completo e embarque continuam pendentes.

Varredura posterior: 743 segmentos e 73.452 apoios; 453 segmentos sem alertas de apoio. Alertas de piso/proxy: 58 → 53; maior diferença geral ainda cerca de 2 m. Permanecem 28 segmentos sem curva, 89 sem endpoint resolvido, apoios ausentes e uma descontinuidade na Misericórdia. O falso segundo alerta da Rua Chile foi corrigido no auditor, comparando amostras consecutivas com apoio/distância real; não corrigiu fisicamente a Chile. Curvas B39 mantêm 54 alertas de raio e 16 de apoio. Rede não está aprovada AAA, 100%, para ônibus ou produção.

Fonte de revisão: `world/areas/mvp-centro-lacerda/transport-network.json`; histórico com IDs de área/OSM/nós em `road-corrections.json`. Gates, prioridades e expansão: `docs/ROAD_TRANSPORT_PRODUCTION.md`. Pipeline estrutural passa a extrair grafo, sentidos, faixas, restrições, paradas e ônibus; inclui vias `*_link`. Validação do contrato sem inconsistências, produção bloqueada (retorno 2 esperado). Sem npm/build, suíte geral, exportação runtime, commit ou push. Próximo foco: apoios/bindings e Misericórdia, depois largura real/faixas, fluxos/conversões e ônibus.

## 04/10/2026 — Terreno e Rondesp: auditoria da rede e câmera interna B39

Autoria candidata explícita `blender/salvador_lacerda_r30b39_rondesp_percursos.blend`, SHA-256 `d682741bf61a11cae333a9e8da6cb02c68557b4f4be8dabcb3d163c7dc120049`, pai B38 preservado. Produção e pacote do jogo continuam B30. Janela única PID 19576, MCP 9876. A revisão não aprova AAA, todos os circuitos, física, trânsito ou performance.

Rede registrada: 743 segmentos; 73452 apoios examinados, com quatro contatos extraídos da geometria salva da Rondesp V25. 452 segmentos sem alertas de apoio no critério candidato; 428 faixas independentes também passaram na triagem de obstáculos. A verificação por nove raios no envelope examinou 16420 poses e marcou 291 com contato em malhas visíveis. É triagem de malha base, não varredura volumétrica ou física. O grafo tem 28 segmentos sem curva na cena e 89 com endpoint não resolvido; pares resolvidos foram identificados dentro da mesma OSM way, preservando ordem. Não conectar através de nós sem apoio. Permanecem ocorrências de saída do pavimento, torção, inclinação transversal/longitudinal, apoio ausente, duas descontinuidades e diferenças grandes de colisor (máximo geral cerca de 2 m). Alertas são `NEEDS_REVIEW`/limitação de fonte, sem alargamento ou correção de Z global automáticos.

Correção comprovada `ERROR`: subdivisão local de cinco faces iniciais do proxy, apenas novos vértices projetados na mesma camada a ±0,5 m. 72121 → 72242 vértices; em 16 apoios locais, maior diferença piso/proxy 0.3126 → 0.0278 m. Vértices novos sem projeção confiável conservaram interpolação; terreno visual, larguras e 5452 componentes comparados na mesma pose foram preservados. A limpeza localizada removeu 20 faces degeneradas; oito triângulos nulos já existiam na B38. Contagem final do proxy: 72240 vértices e 137035 polígonos. Reabertura verificou malha finita e sem triângulos degenerados.

Curvas: 617 ligações direcionais candidatas verificadas com passos de até 0,25 m. 548 passaram apoio/raio; 29 melhoradas por arredondamento maior dentro do pavimento existente (`ADAPT_LOCAL`), sem mudar OSM ou largura. 54 ainda têm alerta de raio e 16 de apoio. Limite de direção 35° e raio de cerca de 4,406 m são probes candidatos, não medidas de fábrica. Somente segmentos com apoio auditado entram nessa verificação; não cobre os trechos ausentes ou todos os itinerários.

Montanha: prévia contínua por oito segmentos de `1075624439`, com sete curvas, 97.79 m; 798 frames e 3192 apoios interpolados, zero apoio ausente, desvio máximo plano das rodas 0.0127 m e piso/proxy 0.0074 m. Frames 241–1038; câmera `QA | RONDESP | camera motorista`, pai do veículo instanciado. Espaço reproduz; a animação é cinemática, sem suspensão. A ação com 428 segmentos independentes permanece preservada como `QA | Rondesp | segmentos independentes B39`; seus cortes entre ruas não são conexões dirigíveis. Verificação volumétrica das curvas e sentidos inversos completos continuam pendentes.

Biblioteca relativa da Rondesp V25 separada. Material transparente local nas sete chapas de vidro para a revisão, com geometria e borrachas preservadas; não altera a fonte V25 nem certifica vidro industrial. Câmera sobre assento esquerdo em posição candidata, visor 24 mm. Oito capturas reais da viewport em `artifacts/roads/rondesp/driver-*.png`; Montanha, Conceição, Chile, Carlos Gomes, Castro Rabelo, Lafayete Coutinho, via sem nome e Ruy Barbosa. A vista interna confirma visibilidade da pista, mas também evidencia arte urbana ainda candidata e limites de superfície incompletos na vista de Carlos Gomes. Fontes/relatórios: `rondesp_network_audit_b38.json` (varredura na sessão após refino, sobre a cadeia B38), `rondesp_turn_audit.json`, `rondesp_driver_review_b39.json` em `docs/reports/blender/`. Sem npm, build, suíte geral, exportação runtime, commit ou push.

## Autoria atual de 02/10/2026 — B38

Usar `blender-revisions.json#/authoring_source`: B38, pai B37; produção B30.
Corrigido binding da Conceição na camada da Montanha e refinado colisor em
trecho contínuo, preservando terreno visual, larguras e 5.255 componentes.
Replay cinemático de cerca de 136 m e posições interpoladas conferidos; curva crítica
e circuito completo continuam pendentes. O resíduo histórico de 36 m não
justifica deformação global do terreno. Detalhes e limites em
`docs/reports/blender/conceicao_binding_r30b38.json` e `docs/CODEX_HANDOFF.md`.

## Modelagem de 02/10/2026 — B36

Autoria candidata B36, pai B35 preservado; produção B30. Seguir
`blender-revisions.json#/authoring_source`. Galerias anteriores mantidas nas
posições/geometrias B35 e ligação ao terraço acrescentada separadamente.
Escadas no interior dos terraços; solo/proxy corrigidos localmente com vias
preservadas. Medidas/contagem dos novos vãos candidatas; nenhuma aprovação
global ou de gameplay. Estado final e evidências em
`docs/reports/blender/terracos_palacio_r30b36.json` e `docs/CODEX_HANDOFF.md`.

> Produção do MVP: consultar primeiro `world/areas/mvp-centro-lacerda/production.json`
> e `docs/MVP_PRODUCTION_PIPELINE.md`. A revisão ativa é explícita; textos históricos
> e scripts antigos não autorizam escolher outro `.blend`. Exportação canônica:
> `automation/blender/export_active_world.py` via MCP na janela única; empacotamento:
> `python tools/runtime/package_world.py`. Não editar arquivos derivados manualmente.


## Objetivo

Executar a evolução estrutural do **Bay of All Saints** de forma reproduzível, priorizando georreferenciamento, terreno, coastline/cais, vias e footprints antes de acabamento visual — **sem confundir fidelidade com réplica milimétrica**.

Antes deste documento, ler obrigatoriamente:

- `AGENTS.md`;
- `docs/PROJECT_STATUS.md`;
- `docs/GAMEPLAY_FIDELITY_POLICY.md`.

A referência real orienta o mundo. A geometria final precisa funcionar como jogo.

## Regra de decisão estrutural

Uma divergência OSM/DEM ↔ Blender não autoriza correção automática.

Antes de mover ou deformar qualquer coisa, classificar a situação como:

- `KEEP_REAL_REFERENCE`;
- `KEEP_GAMEPLAY`;
- `ADAPT_LOCAL`;
- `SOURCE_LIMITATION`;
- `NEEDS_REVIEW`;
- `ERROR`.

Corrigir quando houver ganho real em pelo menos um destes eixos:

- identidade/reconhecimento de Salvador;
- continuidade espacial;
- acesso a local importante;
- dirigibilidade;
- circulação do jogador;
- navegação de NPCs;
- colisão;
- câmera;
- missão/perseguição;
- performance.

Não perseguir RMS mínimo como objetivo artístico.

## 1. Entradas locais

Usar a captura histórica:

```text
aleph-20260924T205631Z-aqqo7pkx/
  manifest.json
  map.osm
  terrain.tif
```

Consultar `docs/PROJECT_STATUS.md` para a cena `.blend` oficial atual e seu SHA-256.

Nunca sobrescrever a captura-fonte nem uma cena validada sem motivo documentado.

## 2. Auditar captura e DEM

```bash
python tools/aleph/inspect_capture.py CAMINHO_DA_CAPTURA \
  --output docs/reports/aleph/mvp-centro-lacerda/source_summary.json

python tools/terrain/audit_dem.py \
  --dem CAMINHO_DA_CAPTURA/terrain.tif \
  --output docs/reports/aleph/mvp-centro-lacerda/dem_audit.json
```

Se CRS/bounds/resolução divergirem do esperado, investigar antes de continuar.

Valores negativos no recorte costeiro não devem ser automaticamente classificados como erro/nodata; o dataset pode conter batimetria. Consultar `SOURCE_REGISTRY.json` e a revisão R30A.2.

## 3. Exportar pistas e auditoria da cena

```bash
blender CENA_VALIDADA.blend --background \
  --python tools/blender/extract_georef_hints.py \
  -- --output docs/reports/blender/georef_hints.json

blender CENA_VALIDADA.blend --background \
  --python tools/blender/audit_structural_scene.py \
  -- --output docs/reports/blender/structural_scene_audit_before.json
```

A auditoria estrutural registra OSM IDs explícitos e exclui objetos `SOURCE_GEOREF`.

## 4. Executar pipeline estrutural

Quando `rasterio` estiver disponível:

```bash
python tools/world/run_structural_pipeline.py \
  --osm CAMINHO_DA_CAPTURA/map.osm \
  --dem CAMINHO_DA_CAPTURA/terrain.tif \
  --hints docs/reports/blender/georef_hints.json \
  --audit-road-profiles \
  --output-dir artifacts/structural-pipeline/mvp-centro-lacerda
```

Sem `rasterio`, omitir `--audit-road-profiles`. Sem DEM, omitir também `--dem`.

Artefatos esperados:

```text
osm_structure.json
osm_topology_audit.json
georef_fit.json
structural_reference.json
dem_audit.json
dem_osm_coverage.json
dem_road_profiles.json
```

Fit XY `insufficient` deve parar o fluxo. Opções de override são diagnóstico, não promoção automática.

## 5. Revisar topologia da fonte

Antes de usar a sobreposição, revisar `osm_topology_audit.json` nesta ordem:

1. node refs ausentes;
2. buildings não fechados;
3. coastline interrompida internamente;
4. near-misses;
5. endpoints internos de transporte;
6. componentes inesperadamente desconectados;
7. possíveis separações por bridge/tunnel/layer.

Consultar `docs/OSM_TOPOLOGY_QA.md`.

Não deformar o Blender para reproduzir erro comprovado da fonte OSM.

## 6. Revisar fit XY

Conferir:

- anchors usados;
- `meters_per_blender_unit`;
- rotação;
- origem;
- RMS e residual máximo;
- outliers;
- Mercado Modelo way `59392558`;
- Palácio Rio Branco way `402383814` quando presentes.

Nunca promover automaticamente o fit para `verified` apenas por quantidade de anchors.

Um offset pequeno em asset coerente não obriga movimento se a experiência e a relação espacial já estiverem boas.

## 7. Fechar relação vertical DEM ↔ Blender

Exportar amostras da geometria real de terreno:

```bash
blender CENA_VALIDADA.blend --background \
  --python tools/blender/export_terrain_samples.py \
  -- --output docs/reports/blender/terrain_samples.json
```

Se a seleção automática incluir objetos que não representam superfície principal, repetir com `--include-regex` restritivo ou propriedades explícitas.

Calcular o fit vertical:

```bash
python tools/terrain/fit_dem_blender_vertical.py \
  --samples docs/reports/blender/terrain_samples.json \
  --fit artifacts/structural-pipeline/mvp-centro-lacerda/georef_fit.json \
  --dem CAMINHO_DA_CAPTURA/terrain.tif \
  --output docs/reports/blender/terrain_vertical_fit.json
```

Quando aplicável, executar também a análise por domínio da R30A.2:

```bash
python tools/terrain/analyze_vertical_domains.py \
  --samples docs/reports/blender/terrain_samples.json \
  --fit artifacts/structural-pipeline/mvp-centro-lacerda/georef_fit.json \
  --dem CAMINHO_DA_CAPTURA/terrain.tif \
  --output docs/reports/blender/vertical_domains.json
```

Revisar escala, offset, relação vertical/horizontal, RMS, distribuição espacial e maiores resíduos.

**Não aplicar reescala/offset global automaticamente.** Um terreno jogável pode divergir localmente do DEM por razões legítimas.

## 8. Importar referência estrutural

```bash
blender CENA_VALIDADA.blend --background \
  --python tools/blender/import_structural_reference.py \
  -- \
  --reference artifacts/structural-pipeline/mvp-centro-lacerda/structural_reference.json \
  --save-as CENA_structure_ref.blend
```

A coleção `SOURCE_GEOREF | STRUCTURAL_REFERENCE` é somente referência, oculta no render e nunca deve ser convertida automaticamente em arte final.

Camadas possíveis:

```text
REF_ROADS
REF_PEDESTRIAN
REF_STEPS
REF_BUILDINGS
REF_COASTLINE
REF_WATERFRONT
REF_RETAINING_WALLS
REF_EARTHWORKS
REF_CLIFFS
REF_WATER
REF_RAILWAYS
```

## 9. Comparar entidades da cena por OSM ID

```bash
python tools/world/compare_scene_reference_alignment.py \
  --scene-audit docs/reports/blender/structural_scene_audit_before.json \
  --reference artifacts/structural-pipeline/mvp-centro-lacerda/structural_reference.json \
  --output docs/reports/blender/scene_reference_alignment.json
```

Somente IDs explícitos são comparados. Não criar binding por semelhança de nomes.

Flags são triagem, não prova automática de erro.

Consultar `docs/SCENE_REFERENCE_ALIGNMENT_QA.md`.

## 10. Decidir se a correção vale a pena

Para cada divergência relevante, registrar:

```text
fonte real
objeto Blender
métrica/erro observado
impacto visual
impacto a pé
impacto veicular
impacto NPC/navmesh
impacto colisão/câmera
classificação
mudança proposta
risco
```

Exemplos:

- encosta com erro grande mas inacessível: pode ser `KEEP_GAMEPLAY` ou `SOURCE_LIMITATION`;
- rua com pequeno erro que quebra entrada importante: pode ser `ADAPT_LOCAL`;
- prédio com binding falso: `ERROR`;
- curva real estreita que impede carro/câmera: adaptação jogável local pode ser correta.

## 11. Corrigir a cena na ordem correta

A ordem não é “zerar referência”. É estabilizar o jogo:

1. erros inequívocos de binding/fonte/implantação;
2. interfaces críticas do terreno;
3. coastline e waterfront/cais onde afetam leitura/acesso;
4. eixos viários e cruzamentos;
5. dirigibilidade das vias prioritárias;
6. áreas pedonais, escadas e calçadas;
7. colisão funcional;
8. conectividade de NPCs;
9. footprints relevantes;
10. integração conservadora com Hero assets;
11. detalhe visual somente depois.

### Terreno

Nunca editar silenciosamente `terrain.tif`. Artefato comprovado deve virar correção derivada/local documentada.

Não suavizar globalmente a escarpa para reduzir resíduos.

A superfície visual pode ser detalhada; a superfície de gameplay/colisão pode ser mais limpa.

### Vias

Priorizar:

1. conectividade;
2. eixo reconhecível;
3. cruzamentos;
4. dirigibilidade;
5. largura funcional;
6. calçadas/travessias;
7. detalhe.

Largura real desconhecida pode receber aproximação de gameplay documentada; não chamar de medida real.

### Coastline

Manter separados:

```text
coastline geográfica
waterfront construído
water surface visual
```

A água visual se adapta à estrutura; a estrutura não deve ser movida apenas para servir ao shader.

### Colisão e navegação

Não usar a malha visual detalhada como única colisão/navmesh.

Preferir colliders simplificados e superfícies funcionais dedicadas.

## 12. Auditoria depois

```bash
blender CENA_NOVA.blend --background \
  --python tools/blender/audit_structural_scene.py \
  -- --output docs/reports/blender/structural_scene_audit_after.json
```

Registrar diferenças antes/depois e motivo de cada adaptação relevante.

## 13. Gate de conclusão estrutural do MVP

O recorte só deve avançar para arte pesada quando:

- topologia crítica estiver classificada;
- fit XY estiver entendido o suficiente para controle estrutural;
- problemas verticais relevantes estiverem classificados por região;
- coastline/cais prioritários estiverem coerentes;
- Praça Cairu conectar corretamente Elevador, Mercado, vias e waterfront;
- vias prioritárias forem caminháveis/dirigíveis conforme intenção;
- áreas críticas tiverem colisão planejada;
- navegação de pedestres/NPCs tiver caminho claro para implementação;
- Hero assets não tiverem sido movidos para mascarar erro de base;
- adaptações de gameplay relevantes estiverem registradas.

## 14. Próxima fronteira: vertical slice em engine

Quando o recorte estrutural e funcional estiver estável, preparar o corredor:

**Cidade Alta → Elevador Lacerda → Praça Cairu → Mercado Modelo → Cidade Baixa/waterfront**

para teste com:

- personagem;
- veículo;
- pedestres/NPCs;
- navmesh;
- rede de tráfego mínima;
- colisão;
- água;
- streaming;
- performance.

A escolha de Godot/Unity/Unreal deve ser decidida depois desse teste, conforme `docs/GAMEPLAY_FIDELITY_POLICY.md`.

## 15. Manutenção documental

Após qualquer mudança material, atualizar `docs/PROJECT_STATUS.md` e os documentos afetados.

Não deixar decisões de direção apenas em mensagens de chat.
