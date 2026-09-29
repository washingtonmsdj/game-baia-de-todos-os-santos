# R30A.11 — Pedestrian Navigation Foundation

## Objetivo

Criar uma base engine-agnostic para circulação de pedestres, escadas, travessias e pontos de conexão do vertical slice, sem antecipar navmesh ou pathfinding específico de engine.

## Fontes

- `artifacts/structural-pipeline/mvp-centro-lacerda/osm_structure.json`;
- fit geográfico robusto atual (`candidate`);
- collider jogável `R30A5 | COLLISION | terrain proxy`;
- superfícies `32.4 GAMEPLAY | WALKABLE`;
- travessias `32.5 GAMEPLAY | PEDESTRIAN CROSSINGS`.

## Resultado

- 126 caminhos pedonais OSM;
- 6 escadarias OSM;
- 487 nós e 488 segmentos;
- 125 helpers de caminho;
- 5 helpers de escada;
- 106 junctions;
- 5 crossing anchors;
- 471 nós resolvidos sobre a superfície jogável.

Cena:

`blender/salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a11_pedestrian_nav.blend`

SHA-256:

`DE552B045D190C8FEADCB763539E2F0F0B1CE68B6A231884BBE7D70FCD8FD396`

## Regras

- helpers não são navmesh final;
- nenhuma conexão é criada atravessando gaps sem superfície;
- escadas ficam em categoria própria;
- travessias não são conectadas automaticamente, mesmo quando existe match de OSM node ID;
- objetos walkable legados marcados como substituídos continuam `reference_only`;
- helpers de debug ficam fora do render final.

## Gate para próxima revisão

A próxima etapa pode criar links revisados de travessia/escada e um controlador funcional de personagem/NPC, desde que mantenha separadas evidência OSM, geometria visual e navegação runtime.
