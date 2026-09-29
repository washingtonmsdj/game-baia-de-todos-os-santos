# Estado Atual do Projeto — Bay of All Saints

> Documento vivo. Atualizar quando houver mudança relevante de revisão, direção, pipeline, bloqueios, engine, vertical slice ou critério de produção.

**Atualizado em:** 2026-09-29

## Resumo executivo

Bay of All Saints é um jogo de ação em mundo aberto ambientado em Salvador. O objetivo é construir uma cidade reconhecível e estruturalmente coerente com Salvador, mas **adaptada conscientemente para gameplay**.

O projeto não busca réplica cadastral/milimétrica. O mundo real fornece referência; a versão final deve funcionar para personagem, carros, NPCs, câmera, colisão, navegação, trânsito, missões e performance.

Diretriz obrigatória: `docs/GAMEPLAY_FIDELITY_POLICY.md`.

## Repositório

`washingtonmsdj/game-baia-de-todos-os-santos`

Branch de produção: `main`.

## Fonte ativa do MVP e contrato de produção

**SSOT executável:** `world/areas/mvp-centro-lacerda/production.json`.
Fluxo obrigatório: `docs/MVP_PRODUCTION_PIPELINE.md`.

A composição ativa para o MVP Three.js é a **R30A.11**, escolhida explicitamente
pelo usuário: `blender/salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a11_pedestrian_nav.blend`.
O contrato registra o SHA-256; exportadores e runtime derivado usam essa mesma fonte.
A R30A.12 permanece preservada, mas não pode substituir a fonte ativa apenas por
ter um número de revisão maior. Não há promoção automática.

O ônibus tem fonte editável própria em `blender/assets/onibus_torino_31065_v03.blend`.
Os Hero assets existentes continuam em coleções da composição: não foram cortados,
reposicionados ou migrados destrutivamente para novas bibliotecas.

O pipeline agora separa fonte Blender, staging de exportação e releases de runtime.
O carregador usa manifesto com hashes, setores espaciais, fila limitada e descarte
de recursos. Terreno visual amplo/core e colisão integral ainda não têm streaming
geométrico completo. LOD, rig e medição de performance permanecem pendentes.

## Histórico das revisões (não determina a fonte ativa)

### R30A.12 — links revisados de navegação

A camada pedonal agora possui conexões promovidas somente quando existe evidência suficiente: `5/5` travessias têm match exato de OSM node ID e deslocamento visual ≤ `2,5 m`, portanto receberam links curtos de navegação revisados.

Os 6 ways de escada produziram `12` endpoints candidatos; `11` foram materializados sobre o collider. O endpoint inicial da `Escadaria do Passo` (`way 530127473`, node `5148629906`) permanece unresolved porque não há superfície jogável no ponto atual.

Cena oficial: `blender/salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a12_nav_links.blend`. Relatório: `docs/reports/blender/r30a12/R30A12_REPORT.md`. Contrato: `docs/reports/blender/r30a12/nav_links.json`.

Próximo foco: vertical slice funcional de locomoção de jogador/NPC usando caminhos, travessias e escadas já revisados.
### R30A.11 — navigation hints de pedestres

A base pedonal do vertical slice foi materializada de forma engine-agnostic: `126` caminhos OSM, `6` escadarias, `487` nós e `488` segmentos. A cena cria `125` helpers de caminho, `5` de escada, `106` junctions e `5` crossing anchors sem gerar navmesh final.

`471` nós foram resolvidos sobre o collider jogável; `16` ficaram fora/sem contato. As cinco travessias existentes têm match exato de `osm_node_id` com o grafo pedonal, mas continuam `review_only_not_connected` até validação da camada de navegação da engine.

Cena oficial: `blender/salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a11_pedestrian_nav.blend`. Relatório: `docs/reports/blender/r30a11/R30A11_REPORT.md`. Revisão: `docs/revisions/R30A11_PEDESTRIAN_NAV.md`.

Próximo foco: vertical slice funcional de locomoção, links revisados de travessias/escadas e entrada/saída de áreas jogáveis.
### R30A.8 ? oceano visual e ?gua de gameplay

A ?gua da Ba?a de Todos-os-Santos foi separada em autoria visual, superf?cie de refer?ncia e volume de gameplay. O n?vel f?sico permanece determin?stico em `0,35 m`; o volume atual permite nado/mergulho at? `-16 m` no recorte existente.

A camada visual usa material PBR animado e espuma derivada da borda real da malha de ?gua. Uma tentativa baseada em `REF_WATERFRONT` foi rejeitada visualmente por desalinhamento e n?o foi mantida como fonte final.

O runtime permanece engine-agnostic: ondas, consulta de superf?cie, nata??o, mergulho, buoyancy, correntes, c?mera submersa, c?usticas e p?s-processamento devem ser implementados no motor, n?o como f?sica Blender.

Cena oficial: `blender/salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a11_pedestrian_nav.blend`. Relat?rio: `docs/reports/blender/r30a8/R30A8_REPORT.md`. Contrato: `docs/reports/blender/r30a8/water_runtime_contract.json`.

Pr?ximo foco: refer?ncia de ondas de larga escala, zonas de corrente/profundidade e vertical slice runtime de nata??o/mergulho quando a engine for selecionada.

### R30A.7 — grafo lógico de vias e cruzamentos

O OSM estrutural foi convertido em uma camada lógica engine-agnostic: `187` vias, `677` nós, `743` segmentos e `174` candidatos a cruzamento. A cena materializa `177` helpers de via e `164` marcadores de cruzamento sobre o collider jogável.

Foram resolvidos `572` nós sobre a superfície de gameplay; `105` ficaram fora/sem contato com o collider. Vias parciais são divididas em sequências contíguas, sem criar pontes artificiais através de gaps.

A revisão preserva `oneway`, rotatórias, restrições e tags existentes, mas não inventa faixas, larguras ou IA de trânsito. O fit XY ainda é `candidate`.

Cena oficial: `blender/salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a7_road_graph.blend`. Relatório: `docs/reports/blender/r30a7/R30A7_REPORT.md`.

Próximo foco: navigation hints de pedestres, travessias e escadas do vertical slice.

### R30A.6 — collision chunks para runtime

O collider otimizado da R30A.5 foi dividido ao vivo, na única janela visível do Blender, em `63` chunks de `128 m`. A partição preserva exatamente os `131.097` polígonos do proxy, com razão de duplicação de vértices `1,0468577`.

Foram comparadas grades de 64/128/256 m. A grade de 128 m foi a primeira a cumprir simultaneamente os limites de quantidade de chunks, máximo de polígonos e P95 por chunk.

Cena: `blender/salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a6_collision_chunks.blend`. Relatório: `docs/reports/blender/r30a6/R30A6_REPORT.md`.

A sessão de produção usa uma única instância visível do Blender com OrdaX e BlendMCP 1.4.4 na mesma janela.

### R30A.5 — proxies de runtime e primeira colisão otimizada

A R30A.5 criou a primeira geometria derivada especificamente para runtime sem alterar a malha-fonte R30A.4. O collider do terreno reduziu de 1.082.745 para 131.097 polígonos (`-87,8922%`) e passou o gate geométrico com 5.023 amostras: erro P95 `0,0018215 m` e máximo `0,180078 m`.

A cena agora também expõe fontes engine-agnostic para vias dirigíveis, superfícies caminháveis, travessias, guias/meio-fio e água. Nenhuma engine foi escolhida e nenhum navmesh/grafo de tráfego foi inventado nesta etapa.

Cena oficial: `blender/salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a5_runtime_proxies.blend`. Relatórios: `docs/reports/blender/r30a5/R30A5_REPORT.md` e `docs/reports/blender/r30a5/runtime_manifest.json`.

O BlendMCP fallback foi revalidado na R30A.5 com addon `1.4.4`, porta `9877`, `get_addon_version`, `get_scene_info` e `get_object_info`. O launcher usa `--factory-startup --disable-autoexec` e timeout de 120 s.

Próximo foco: chunking da colisão, grafo de vias/cruzamentos e hints de navegação do vertical slice.

### R30A.4 — camadas semânticas de gameplay aplicadas

A primeira separação funcional foi aplicada diretamente no Blender por coleções e metadados não destrutivos. A geometria permaneceu invariável: 4.677 objetos, 4.137 meshes, 839.684 vértices, 2.044.767 arestas e 1.238.783 polígonos.

Camadas criadas: terreno, fonte de colisão, pistas dirigíveis, superfícies caminháveis, travessias, guias/meio-fio, água, referência geográfica e proxies legados. O terreno principal continua marcado como composto `GAMEPLAY_TERRAIN + COLLISION_SOURCE`; nenhum split destrutivo foi feito.

Cena oficial: `blender/salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a4_semantic_layers.blend`. Relatório: `docs/reports/blender/r30a4/R30A4_REPORT.md`.

Fallback Blender MCP validado em `docs/BLENDMCP_FALLBACK.md`: BlendMCP 1.4.4 na porta 9877, isolado da sessão histórica da porta 9876.

### R30A.3 — auditoria semântica direta via OrdaX concluída

A cena oficial foi inspecionada diretamente pelo ChatGPT através de OrdaX Device Agent / Blender Live, sem Codex como intermediário. Foi criado o checkpoint `pre-r30a3-direct-chatgpt`; a cena permaneceu `is_dirty=false` e nenhuma geometria foi salva.

A auditoria confirmou 4.677 objetos, 4.137 meshes e 135 materiais. O objeto `MVP | terreno corrigido | colisão estática` concentra 547.464 vértices / 1.082.745 polígonos e hoje acumula terreno jogável, colisão, asfalto, percurso pedonal, Praça Cairu, passeios e contenções.

Isso confirma que o próximo trabalho não é forçar novo fit global nem cortar a malha imediatamente. A prioridade passa a ser separar responsabilidades semanticamente e criar camadas funcionais não destrutivas para `GAMEPLAY_TERRAIN`, `ROAD_DRIVEABLE`, `SIDEWALK_WALKABLE` e `COLLISION`.

Relatórios: `docs/reports/blender/r30a3/R30A3_REPORT.md` e `docs/reports/blender/r30a3/semantic_scene_audit.json`.


### R30A.2 — diagnóstico vertical por domínio concluído

Pipeline integrado em:

`cc2de0c3bc311ba861fa9819440cd7e533704844`

Execução/relatório concluído em:

`450c377ee0fdbb385e64464959091b72bfdb195b`

Relatórios:

- `docs/reports/blender/r30a2/R30A2_REPORT.md`;
- `docs/reports/blender/r30a2/r30a2_status.json`;
- `docs/reports/blender/r30a2/vertical_domains.json`.

Estado final da rodada:

`diagnostic_complete_vertical_domain_split_insufficient`

Nenhuma correção geométrica local foi autorizada pela R30A.2.

## Principais conclusões da R30A.2

### Batimetria não explica o erro vertical

Foram 4.978 amostras DEM válidas:

- 2 abaixo de 0 m (`0,0402%`);
- 4.976 no domínio terrestre não negativo (`99,9598%`).

O robust fit já rejeitava os dois valores negativos. Separar batimetria não alterou os parâmetros do fit.

Portanto, a hipótese “a batimetria é a principal causa do RMS vertical ruim” foi descartada.

### Fit vertical continua insuficiente

R30A.2 terrestre:

- entrada: 4.976 amostras;
- mantidas: 4.900;
- outliers: 76;
- escala Z candidata: `1,0253290`;
- offset Z candidato: `-4,6316455`;
- RMS: `9,2106683`;
- mediana absoluta: `5,2179134`;
- máximo residual: `29,3265740`;
- razão vertical/horizontal: `1,0568512`;
- quality: `insufficient`.

Nenhuma escala/offset Z foi aplicado.

### A malha amostrada não é topografia pura

O objeto usado no fit foi:

`MVP | terreno corrigido | colisão estática`

Evidências da própria cena indicam que ele é uma superfície funcional/histórica de MVP:

- `game_role: static_terrain_collision`;
- derivado de `Aleph DEM + OSM`;
- contém patamares adaptados aos pisos do esboço;
- altimetria foi filtrada/corrigida para MVP;
- inclui plataformas fixas e aproximações.

Isso é decisivo para a direção do projeto: **não devemos tentar deformar essa superfície de gameplay para coincidir globalmente com o DEM**.

A partir de agora, referência topográfica e terreno jogável devem ser tratados como responsabilidades diferentes.

### Regiões críticas detectadas

A grade espacial encontrou 157 células terrestres para revisão, com destaque para:

- base da escarpa/Cidade Baixa;
- waterfront/cais;
- plataformas baixas do MVP;
- platôs da Cidade Alta;
- transições junto à escarpa/ladeiras.

Os maiores resíduos aparecem frequentemente onde a malha atual contém patamares funcionais deliberados ou onde o DEM tem dificuldade para representar transições urbanas abruptas.

Nenhuma das dez células mais críticas apontou diretamente Praça Cairu ou o footprint do Mercado Modelo como alvo de correção.

### Mercado Modelo permanece controle, não alvo

OSM way:

`59392558`

Footprint real observado com offset aproximado de:

`1,878 m`

Não mover automaticamente.

## Cobertura DEM

O falso diagnóstico histórico de `0,1584%` foi corrigido na R30A.1.

A janela real da captura Aleph está:

- `covered_with_margin`;
- cobertura: `100%`.

Captura histórica:

`data/aleph/aleph-20260924T205631Z-aqqo7pkx/`

Arquivos principais:

- `manifest.json`;
- `map.osm`;
- `terrain.tif`.

## Fit XY

Estado conhecido:

- quality: `candidate`;
- status: `candidate_only`;
- escala horizontal: `0,9701734818` unidades Blender por metro;
- rotação EPSG:3857 → Blender: aproximadamente `-0,050990°`;
- RMS: aproximadamente `4,168632` unidades Blender;
- anchors robustos: `1.012`.

Não tratar como transformação final/verificada sem revisão adicional.

## Decisão estrutural após R30A.2

Ainda **não existe evidência suficiente para autorizar uma primeira correção geométrica local baseada apenas no DEM**.

Próximo foco recomendado:

1. separar semanticamente referência física/topográfica de `GAMEPLAY_TERRAIN`/colisão;
2. obter ou validar referência vertical terrestre independente para regiões prioritárias;
3. revisar regionalmente escarpa e waterfront;
4. testar quais patamares são adaptações deliberadas de gameplay e quais são erros reais;
5. só então propor correções locais.

Importante: um patamar funcional pode permanecer diferente do DEM se ele melhora circulação/veículos/NPCs sem destruir a identidade de Salvador.

## DEM e batimetria

O `terrain.tif` histórico é derivado do conjunto Mapzen/Tilezen Terrain Tiles usado pelo Aleph.

O recorte inclui a Baía de Todos-os-Santos. Valores DEM profundamente negativos podem representar batimetria e **não devem ser classificados automaticamente como nodata/erro**.

A R30A.2 confirmou que esses pontos negativos não dominam o fit vertical.

Não editar o `terrain.tif` original.

## Filosofia de fidelidade

A pergunta de produção não é:

> “Como fazer o Blender coincidir 100% com OSM/DEM?”

A pergunta é:

> “A divergência prejudica a identidade de Salvador, a continuidade do mundo ou a jogabilidade?”

Classificações recomendadas:

- `KEEP_REAL_REFERENCE`;
- `KEEP_GAMEPLAY`;
- `ADAPT_LOCAL`;
- `SOURCE_LIMITATION`;
- `NEEDS_REVIEW`;
- `ERROR`.

Detalhes em `docs/GAMEPLAY_FIDELITY_POLICY.md`.

## Gameplay e arquitetura futura

O jogo é planejado para suportar, progressivamente:

- personagem a pé;
- veículos;
- tráfego;
- pedestres/NPCs;
- resposta policial/facções;
- missões;
- economia/atividades;
- mundo urbano sistêmico.

A geometria visual deve ser separada das camadas funcionais. Planejar equivalentes a:

```text
SOURCE_GEOREF
REFERENCE_OSM
REFERENCE_TERRAIN
ENVIRONMENT_FINAL
GAMEPLAY_TERRAIN
ROAD_DRIVEABLE
SIDEWALK_WALKABLE
NAVIGATION_HINTS
COLLISION
HERO
WATER
STREAMING
```

A R30A.2 reforçou especialmente a necessidade de separar `REFERENCE_TERRAIN` de `GAMEPLAY_TERRAIN`/`COLLISION`.

Ruas visuais não são, por si só, rede de tráfego. Calçadas visuais não são, por si só, navmesh.

## Engine

Nenhuma engine foi escolhida definitivamente.

Candidatas futuras podem incluir Godot, Unity ou Unreal, mas o pipeline atual deve permanecer neutro.

A escolha deverá ser baseada num vertical slice real, não em preferência abstrata.

## Vertical slice prioritário

Corredor:

```text
Cidade Alta
→ Elevador Lacerda
→ Praça Cairu
→ Mercado Modelo
→ Cidade Baixa / waterfront
```

Antes de expansão urbana grande, esse slice deve provar:

- caminhada;
- colisão;
- câmera;
- veículo controlável;
- veículos IA básicos;
- pedestres/NPCs básicos;
- navegação;
- tráfego/interseções mínimos;
- água;
- iluminação;
- streaming/carregamento;
- performance.

## Ordem macro de desenvolvimento

1. separar referência topográfica de terreno/colisão jogável;
2. classificar regionalmente erros reais versus adaptações de gameplay;
3. corrigir somente erros estruturais realmente relevantes;
4. construir/estabilizar superfícies de gameplay;
5. consolidar escarpa e interfaces críticas;
6. coastline/cais;
7. ruas/cruzamentos;
8. escadas/calçadas;
9. footprints/Hero assets;
10. colisão funcional;
11. rede de pedestres/NPCs;
12. rede de tráfego/veículos;
13. vertical slice em engine candidata;
14. otimização e arte final do recorte;
15. expansão da cidade.

A ordem pode ser ajustada quando gameplay revelar dependências reais.

## Bloqueios atuais

- fit vertical completo e terrestre seguem `insufficient`;
- a superfície amostrada mistura terreno funcional, colisão e patamares de MVP;
- escarpa contém transições abruptas que o DEM pode representar mal localmente;
- fit XY segue `candidate`, não `verified`;
- não há referência vertical terrestre independente suficiente para autorizar correção local apenas por métrica.

Esses bloqueios não impedem planejamento de gameplay layers, classificação semântica ou preparação do vertical slice.

## O que não fazer

- não tentar zerar RMS global por princípio;
- não reconstruir a cena do zero sem motivo;
- não deformar Hero assets para acomodar erro de base;
- não transformar `static_terrain_collision` em topografia “real” por força;
- não usar geometria visual pesada diretamente como colisão/navmesh por conveniência;
- não inventar largura de rua como se fosse medida;
- não aplicar escala/offset global sem análise;
- não confundir OSM com lógica completa de tráfego;
- não expandir a cidade rapidamente antes do vertical slice ser funcional;
- não escolher engine definitiva antes de um teste representativo;
- não deixar decisões importantes apenas em chats.

## Documentos de entrada para nova IA

Ler nesta ordem:

1. `AGENTS.md`;
2. `docs/PROJECT_STATUS.md`;
3. `docs/PROJECT_VISION.md`;
4. `docs/GAMEPLAY_FIDELITY_POLICY.md`;
5. `docs/CODEX_HANDOFF.md`;
6. `docs/CODEX_STRUCTURE_HANDOFF.md`;
7. handoff da revisão atual, se existir.

## Regra de manutenção documental

Toda mudança material em qualquer um destes itens deve atualizar este documento e os handoffs afetados:

- direção do jogo;
- cena Blender oficial;
- revisão ativa;
- captura geográfica;
- critérios de fidelidade;
- pipeline estrutural;
- gameplay layers;
- engine;
- vertical slice;
- principais blockers;
- próximos passos.

O repositório deve permitir que outro agente retome o projeto sem depender da memória de uma conversa.