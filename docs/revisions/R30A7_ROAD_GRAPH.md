# R30A.7 — Road Graph

## Direção

A R30A.7 adiciona uma camada lógica de vias e cruzamentos acima da geometria visual, sem transformar OSM automaticamente em IA de trânsito.

O objetivo é permitir futura criação de lanes, semáforos, regras de conversão, tráfego e perseguições com uma topologia rastreável.

## Regras

- preservar IDs OSM;
- usar `oneway` somente quando explícito ou implícito por rotatória;
- preservar `lanes`, `width` e `maxspeed` apenas quando tagueados;
- não inventar lane centerlines;
- não criar conexão através de nós fora do collider;
- manter fit XY como `candidate` até validação superior;
- manter engine binding `unbound`.

Coleção principal:

`35 GAMEPLAY | ROAD GRAPH R30A7`
## Runtime e viewport

As linhas de via são `CURVE` helpers e os cruzamentos são `EMPTY` helpers; ambos ficam fora do render final e carregam metadados de gameplay.

O Z é projetado sobre `R30A5 | COLLISION | terrain proxy`, isto é, a superfície de gameplay, e não diretamente sobre o DEM.

Camadas pesadas de colisão/referência ficam ocultas por padrão na viewport para permitir leitura da cidade e do grafo.

## Operação

Toda mutação da revisão deve ocorrer na única janela visível do Blender. OrdaX e BlendMCP podem operar sobre a mesma instância.

Artefatos principais:

- `docs/reports/blender/r30a7/road_graph.json`;
- `docs/reports/blender/r30a7/road_graph_scene.json`;
- `docs/reports/blender/r30a7/R30A7_REPORT.md`;
- `blender/salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a7_road_graph.blend`.
