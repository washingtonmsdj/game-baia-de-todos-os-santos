# R30A.11 — Navigation Hints de Pedestres

## Objetivo

Preparar uma camada lógica de circulação a pé para jogador e NPCs sem gerar navmesh específico de engine e sem inventar conexões ausentes.

A revisão foi aplicada ao vivo na única janela visível do Blender, sobre a cena R30A.8 Ocean, preservando oceano, terreno, road graph e demais sistemas existentes.

Cena final:

`blender/salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a11_pedestrian_nav.blend`

SHA-256:

`DE552B045D190C8FEADCB763539E2F0F0B1CE68B6A231884BBE7D70FCD8FD396`

## Grafo pedonal

- caminhos OSM: `126`;
- escadarias OSM: `6`;
- nós: `487`;
- segmentos: `488`;
- junction candidates: `107`;
- segmentos restritos: `6`;
- segmentos direcionais: `0`.

## Materialização no Blender

- path helpers: `125`;
- step helpers: `5`;
- navigation junctions: `106`;
- crossing anchors: `5`;
- nós resolvidos na superfície jogável: `471`;
- nós não resolvidos: `16`.

Um caminho pedonal e uma escadaria não receberam helper completo porque não possuem sequência suficiente sobre o collider jogável. Nenhum gap foi preenchido artificialmente.

Coleção principal:

`37 GAMEPLAY | NAV HINTS R30A11`

Subcamadas:

- `37.1 NAV | PEDESTRIAN PATHS`;
- `37.2 NAV | STEPS`;
- `37.3 NAV | CROSSINGS`;
- `37.4 NAV | JUNCTIONS`;
- `37.5 NAV | WALKABLE SOURCES`.

Os helpers também alimentam `33.7 RUNTIME | NAV HINTS` sem duplicar meshes pesados.

## Travessias

| Travessia OSM | Nó pedonal correspondente | Distância visual |
| --- | --- | ---: |
| `3178050253` | `3178050253` | `1,305 m` |
| `5917201014` | `5917201014` | `1,332 m` |
| `592378620` | `592378620` | `1,632 m` |
| `9264983513` | `9264983513` | `2,108 m` |
| `9264983514` | `9264983514` | `1,645 m` |

As cinco travessias possuem match exato de `osm_node_id` com o grafo pedonal. A diferença métrica acima é entre o centro do mesh zebrado aproximado e a posição do nó OSM.

Mesmo com essa evidência, a revisão mantém `connection_status = review_only_not_connected`. A conexão final deve ser criada apenas quando a camada de navegação da engine for definida e validada.

## Walkable sources

Quatro superfícies permanecem candidatas de gameplay e quatro objetos antigos já marcados como substituídos permanecem `reference_only`. A revisão não promove geometria legada apenas porque ela está na coleção WALKABLE.

## Visualização de desenvolvimento

Os helpers são deliberadamente mais espessos que uma linha física real para revisão ao vivo: pedestres em verde, escadas em roxo, travessias em amarelo e junctions em ciano. Todos ficam `hide_render=true`.

## Limites

- não existe navmesh final nesta revisão;
- não existe crowd avoidance;
- não existe pathfinding de engine;
- não existe conexão automática de travessias;
- não existe regra final de escada para personagem/NPC;
- o fit XY continua `candidate`.

## Próximo passo

Usar estes contratos no vertical slice funcional: personagem a pé, links de travessia revisados, escadas e pontos de entrada/saída, mantendo a integração neutra até a escolha da engine.
