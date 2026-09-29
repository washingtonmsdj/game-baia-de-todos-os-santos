# R30A.12 — Reviewed Navigation Links

## Objetivo

Transformar evidências R30A.11 em links de navegação revisados, sem antecipar navmesh ou pathfinding específico de engine.

## Contrato

Arquivo:

`docs/reports/blender/r30a12/nav_links.json`

Regras:

- crossing link exige `osm_node_id` exato;
- deslocamento visual máximo: `2,5 m`;
- escadas usam somente endpoints reais do way OSM;
- falta de superfície bloqueia a materialização;
- nenhum link é criado por heurística de proximidade genérica.

## Resultado

- `5/5` crossing links materializados;
- `11/12` step endpoint anchors materializados;
- `1` endpoint unresolved, preservado como evidência pendente.

Cena:

`blender/salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a12_nav_links.blend`

SHA-256:

`D5A1BA39250E9AB291D45C9BE8B9058FE84FD82F7D6B01CC5FD309E690CB8835`

## Limites

A revisão não define:

- navmesh final;
- crowd avoidance;
- custo de pathfinding;
- comportamento de travessia de NPC;
- regra top/bottom para escadas sem evidência vertical;
- integração específica com Unreal/Godot/Unity.
