# Estado Atual do Projeto — Bay of All Saints

> Documento vivo. Atualizar quando houver mudança relevante de revisão, direção, pipeline, bloqueios, engine, vertical slice ou critério de produção.

**Atualizado em:** 2026-09-28

## Resumo executivo

Bay of All Saints é um jogo de ação em mundo aberto ambientado em Salvador. O objetivo é construir uma cidade reconhecível e estruturalmente coerente com Salvador, mas **adaptada conscientemente para gameplay**.

O projeto não busca réplica cadastral/milimétrica. O mundo real fornece referência; a versão final deve funcionar para personagem, carros, NPCs, câmera, colisão, navegação, trânsito, missões e performance.

Diretriz obrigatória: `docs/GAMEPLAY_FIDELITY_POLICY.md`.

## Repositório

`washingtonmsdj/game-baia-de-todos-os-santos`

Branch de produção: `main`.

## Cena Blender oficial atual

Arquivo versionado via Git LFS:

`blender/salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a_structure_ref.blend`

SHA-256 conhecido:

`ACF5F5BBA00DED0FC912116DB02DE7FCA26C43BB8DBF67A10AC5CB8A3C319A30`

Commit que introduziu a cena no Git LFS e concluiu a R30A.1 diagnóstica:

`d631b431b04db5b67d817988c99e655a4808d658`

A cena não deve ser substituída/destruída silenciosamente. Novas revisões devem preservar a origem e ser justificadas por mudança real de cena.

## Fase atual

### R30A.2 — diagnóstico vertical por domínio

Implementação do pipeline integrada na `main` pelo merge:

`cc2de0c3bc311ba861fa9819440cd7e533704844`

Objetivo:

- separar terreno terrestre de batimetria;
- analisar resíduos verticais espacialmente;
- identificar regiões concretas que merecem correção;
- não aplicar correção geométrica global apenas para reduzir RMS.

Handoff:

`docs/CODEX_R30A2_HANDOFF.md`

Plano:

`docs/revisions/R30A2_VERTICAL_DOMAIN_PLAN.md`

## Estado conhecido da R30A.1

### Cobertura DEM

O falso diagnóstico anterior de `0,1584%` foi corrigido.

A janela real da captura Aleph está:

- `covered_with_margin`;
- cobertura: `100%`.

A captura histórica é:

`data/aleph/aleph-20260924T205631Z-aqqo7pkx/`

Arquivos principais:

- `manifest.json`;
- `map.osm`;
- `terrain.tif`.

### Fit XY

Estado atual:

- quality: `candidate`;
- status: `candidate_only`;
- escala horizontal: `0,9701734818` unidades Blender por metro;
- rotação EPSG:3857 → Blender: aproximadamente `-0,050990°`;
- RMS: aproximadamente `4,168632` unidades Blender;
- anchors robustos: `1.012`.

Não tratar como transformação final/verificada sem revisão adicional.

### Mercado Modelo

OSM way:

`59392558`

O falso binding de terreno detectado na R30A era causado por leitura indevida de ID dentro de texto descritivo. O auditor foi corrigido.

Footprint real observado com offset aproximado de:

`1,878 m`

Não mover o Mercado automaticamente apenas por esse valor.

### Fit vertical R30A.1

Seleção consciente de terreno:

- 1 objeto;
- 4.978 amostras;
- 4.900 mantidas;
- RMS: aproximadamente `9,2106683`;
- mediana absoluta: aproximadamente `5,2179134`;
- escala Z candidata: `1,0253290`;
- offset Z candidato: `-4,6316455`;
- quality: `insufficient`.

Nenhuma escala/offset Z foi aplicado.

A R30A.2 existe para decompor esse erro por domínio/região antes de qualquer alteração física.

## DEM e batimetria

O `terrain.tif` histórico é derivado do conjunto Mapzen/Tilezen Terrain Tiles usado pelo Aleph.

O recorte inclui a Baía de Todos-os-Santos. Valores DEM profundamente negativos podem representar batimetria do dataset e **não devem ser classificados automaticamente como nodata/erro**.

O fit de terreno terrestre deve separar explicitamente o domínio apropriado antes de interpretar resíduos.

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

1. fechar diagnóstico estrutural útil;
2. corrigir somente erros estruturais realmente relevantes;
3. construir superfícies de gameplay;
4. consolidar terreno/escarpa;
5. coastline/cais;
6. ruas/cruzamentos;
7. escadas/calçadas;
8. footprints/Hero assets;
9. colisão funcional;
10. rede de pedestres/NPCs;
11. rede de tráfego/veículos;
12. vertical slice em engine candidata;
13. otimização e arte final do recorte;
14. expansão da cidade.

A ordem pode ser ajustada quando gameplay revelar dependências reais.

## O que não fazer

- não tentar zerar RMS global por princípio;
- não reconstruir a cena do zero sem motivo;
- não deformar Hero assets para acomodar erro de base;
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