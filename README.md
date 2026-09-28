# Bay of All Saints — Salvador em Mundo Aberto

> **Nome do jogo:** Bay of All Saints  
> **Tagline:** *Todos têm um preço. Ninguém é santo.*

Jogo de ação em mundo aberto ambientado em Salvador, Bahia, Brasil.

O MVP atual está concentrado no corredor **Cidade Alta / Elevador Lacerda / Praça Cairu / Mercado Modelo / Cidade Baixa / waterfront**.

O objetivo de longo prazo é construir uma Salvador ampla, reconhecível e sistêmica, com carros, pedestres, NPCs, trânsito, missões, atividades e expansão por bairros — sem transformar a cidade real em uma restrição que prejudique a jogabilidade.

## Comece por aqui

Para entender o estado atual sem depender de conversas anteriores:

1. [`AGENTS.md`](AGENTS.md)
2. [`docs/PROJECT_STATUS.md`](docs/PROJECT_STATUS.md)
3. [`docs/PROJECT_VISION.md`](docs/PROJECT_VISION.md)
4. [`docs/GAMEPLAY_FIDELITY_POLICY.md`](docs/GAMEPLAY_FIDELITY_POLICY.md)
5. [`docs/CODEX_HANDOFF.md`](docs/CODEX_HANDOFF.md)

`docs/PROJECT_STATUS.md` é o documento vivo que registra cena oficial, revisão ativa, blockers e próximos passos.

## Princípio central

A meta não é reproduzir Salvador de forma cadastral ou milimétrica.

O projeto busca:

> **uma Salvador reconhecível, estruturalmente coerente e divertida de jogar.**

OSM, DEM, Aleph e referências reais são usados para controle estrutural. A geometria final pode receber adaptações locais justificadas para:

- dirigibilidade;
- circulação do jogador;
- NPCs/pedestres;
- colisão;
- câmera;
- navegação;
- tráfego;
- missões;
- performance.

Uma diferença entre a referência real e o Blender não é automaticamente um erro.

Leia a política completa em [`docs/GAMEPLAY_FIDELITY_POLICY.md`](docs/GAMEPLAY_FIDELITY_POLICY.md).

## Foco atual do desenvolvimento

A fase atual ainda é estrutural e funcional, antes de arte pesada:

1. entender georreferenciamento e terreno;
2. localizar erros reais por região;
3. corrigir apenas o que afeta identidade, continuidade ou gameplay;
4. estabilizar escarpa/coastline/cais;
5. estabilizar ruas e cruzamentos prioritários;
6. preparar superfícies para caminhada e veículos;
7. preparar colisão e navegação;
8. consolidar Hero assets;
9. montar um vertical slice jogável;
10. só depois expandir Salvador em grande escala.

## Cena Blender

A cena oficial atual está versionada em Git LFS sob `blender/`.

Caminho, SHA-256 e revisão ativa estão em [`docs/PROJECT_STATUS.md`](docs/PROJECT_STATUS.md).

O projeto preserva separação entre:

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

A nomenclatura pode evoluir; a separação de responsabilidades deve permanecer.

## Mundo real × mundo jogável

### Deve permanecer altamente reconhecível

- relação Cidade Alta/Cidade Baixa;
- Elevador Lacerda;
- Praça Tomé de Sousa;
- Praça Cairu;
- Mercado Modelo;
- marcos principais;
- eixos das vias;
- escarpa;
- coastline/cais;
- relação da cidade com a Baía.

### Pode ser adaptado quando necessário

- largura útil de pista;
- raio de curva;
- inclinação/transições;
- largura navegável de calçada;
- degraus/rampas;
- colisores;
- corredores de NPCs;
- áreas de manobra;
- acessos e rotas de gameplay.

Adaptações devem ser locais, mínimas, registradas e testadas.

## Carros e tráfego

OSM informa a estrutura real das ruas, mas não é uma rede completa de tráfego de videogame.

O projeto deverá ter dados próprios para:

```text
lanes
direction
intersections
turn_connections
speed_zones
traffic_lights
crosswalks
spawns
parking
traffic_priority
```

## Pedestres e NPCs

Calçada visual não deve ser confundida com navmesh.

A navegação deverá representar conexões funcionais entre:

```text
sidewalk
crosswalk
steps
ramp
plaza
building_entrance
elevator
poi
restricted_area
```

## Colisão

Colisão deve ser previsível e mais simples que a geometria visual.

Exemplos esperados:

- escada visual com rampa de colisão;
- fachada detalhada com collider simplificado;
- calçada irregular com superfície caminhável limpa.

## Engine

A engine definitiva ainda **não foi escolhida**.

Godot, Unity e Unreal podem ser avaliados futuramente, mas o pipeline atual deve permanecer neutro.

A escolha será baseada num vertical slice funcional real, comparando:

- personagem;
- veículos;
- IA de pedestres/trânsito;
- navegação;
- streaming;
- iluminação;
- performance;
- manutenção do pipeline.

## Vertical slice prioritário

```text
Cidade Alta
→ Elevador Lacerda
→ Praça Cairu
→ Mercado Modelo
→ Cidade Baixa / waterfront
```

Esse trecho deverá provar, antes da expansão grande:

- caminhada;
- colisão;
- câmera;
- veículo controlável;
- veículos IA básicos;
- NPCs/pedestres;
- navmesh/conectividade;
- tráfego/interseções mínimos;
- água;
- iluminação;
- streaming;
- performance.

## Dados geográficos e Aleph

O projeto utiliza Aleph como ferramenta externa de aquisição/proveniência geográfica.

Revisão pinada:

`Belluxx/Aleph@d24c61507481a91a0dd6afac4f97626a4e5ea780`

Captura histórica recuperada do MVP:

```text
data/aleph/aleph-20260924T205631Z-aqqo7pkx/
  manifest.json
  map.osm
  terrain.tif
```

Ferramentas principais:

```text
tools/aleph/inspect_capture.py
tools/georef/solve_osm_blender_fit.py
tools/world/run_structural_pipeline.py
tools/world/extract_osm_structure.py
tools/world/audit_osm_topology.py
tools/world/build_blender_structure_reference.py
tools/world/compare_scene_reference_alignment.py
tools/terrain/audit_dem.py
tools/terrain/compare_dem_osm_coverage.py
tools/terrain/audit_road_profiles.py
tools/terrain/fit_dem_blender_vertical.py
tools/terrain/analyze_vertical_domains.py
```

A coleção `SOURCE_GEOREF | STRUCTURAL_REFERENCE` é somente referência e não deve ser automaticamente transformada em arte final.

## Referências visuais

Referências fotográficas são apoio secundário nesta fase. A prioridade é estrutura e gameplay.

O catálogo permanece disponível quando detalhe arquitetônico for necessário, mas não deve bloquear terreno, vias, colisão, navegação ou gameplay.

## Política de desenvolvimento

Todo trabalho importante deve permanecer reproduzível:

- scripts versionados;
- relatórios versionados;
- revisões Blender rastreáveis;
- mudanças de direção registradas;
- handoffs atualizados;
- incertezas explícitas;
- operações destrutivas evitadas.

Mudanças materiais de direção devem atualizar [`docs/PROJECT_STATUS.md`](docs/PROJECT_STATUS.md) e os documentos afetados no mesmo ciclo.

## Idioma

O nome do jogo permanece em inglês: **Bay of All Saints**.

Documentação, relatórios, handoffs e notas de desenvolvimento são mantidos em **português**.