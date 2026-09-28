# R30A.4 — camadas semanticas de gameplay

Data: 2026-09-28.

## Objetivo

Separar responsabilidades funcionais da cena sem alterar vertices, arestas, faces ou transformacoes.

Cena de entrada:
`blender/salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a_structure_ref.blend`

Cena gerada:
`blender/salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a4_semantic_layers.blend`

Checkpoint anterior a alteracao:
`pre-r30a4-semantic-layers`.

## Resultado

Foram criadas colecoes semanticas R30A.4 apenas por links de objetos existentes e metadados customizados.

A geometria permaneceu invariavel:
- 4.677 objetos;
- 4.137 meshes;
- 839.684 vertices;
- 2.044.767 arestas;
- 1.238.783 poligonos.

## Camadas criadas

- `GAMEPLAY | TERRAIN`: 1 objeto;
- `GAMEPLAY | COLLISION SOURCE`: 1 objeto;
- `GAMEPLAY | ROAD DRIVEABLE`: 2 objetos;
- `GAMEPLAY | WALKABLE`: 8 objetos;
- `GAMEPLAY | PEDESTRIAN CROSSINGS`: 5 objetos;
- `GAMEPLAY | CURB BOUNDARIES`: 1 objeto;
- `GAMEPLAY | WATER`: 2 objetos;
- `REFERENCE | GEOREF`: 9 objetos;
- `REFERENCE | LEGACY TERRAIN PROXIES`: 3 objetos.

O objeto `MVP | terreno corrigido | colisao estatica` permanece composto e foi explicitamente marcado como `GAMEPLAY_TERRAIN + COLLISION_SOURCE`. Nenhum split destrutivo de geometria foi feito nesta revisao.

## Proximo passo

Usar essas camadas como contrato para gerar superficies funcionais de engine: colisao simplificada, road graph, pedestrian graph/navmesh source e limites de agua, sem usar automaticamente a malha visual pesada como runtime collision.

Relatorio estruturado: `semantic_layers.json`.
