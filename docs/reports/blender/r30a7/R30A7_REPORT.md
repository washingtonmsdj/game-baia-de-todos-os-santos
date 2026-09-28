# R30A.7 — Grafo lógico de vias

## Objetivo

Criar uma camada lógica engine-agnostic para vias e cruzamentos do MVP, preparando trânsito futuro sem inventar lane graph, largura ou sentido ausentes da fonte.

A revisão foi aplicada ao vivo na única janela visível do Blender, com OrdaX e BlendMCP 1.4.4 no mesmo processo.

## Fonte

O grafo usa `artifacts/structural-pipeline/mvp-centro-lacerda/osm_structure.json` e o `robust_fit` atual de `georef_fit.json`.

O fit XY permanece `candidate`; por isso os helpers são candidatos de gameplay/topologia, não autoridade cadastral.

## Grafo gerado

- vias OSM: `187`;
- nós: `677`;
- segmentos: `743`;
- candidatos a cruzamento: `174`;
- segmentos com direção explícita/rotatória: `483`;
- segmentos com acesso restrito: `19`.
## Materialização no Blender

- helpers de via criados: `177`;
- splines de via: `177`;
- vias parciais por sair do recorte/collider: `31`;
- marcadores de cruzamento criados: `164`;
- nós resolvidos sobre o collider: `572`;
- nós não resolvidos: `105`.

Os nós não resolvidos não são interpolados nem conectados artificialmente. O script divide a via em sequências contíguas resolvidas para evitar pontes falsas sobre áreas sem superfície de gameplay.

A direção usa somente `oneway` e `junction=roundabout`; ausência de informação permanece bidirecional candidata. Restrições de acesso são preservadas como metadados.

## Apresentação de trabalho

Colliders, SOURCE_GEOREF, QA R27 e câmeras ficam ocultos por padrão na viewport de gameplay, mas permanecem preservados na cena e no Outliner.

Isso reduz ruído visual sem apagar dados de referência ou debug.
## Cena de saída

`blender/salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a7_road_graph.blend`

SHA-256:

`7BA803E66A548EFEFEBDE615B97808B9DB64CD710C8FBA08A89E6251E6F719BF`

A cena mantém `4.201` meshes; o aumento de objetos vem de curvas e empties lógicos, não de duplicação pesada da cidade.

## Próximo passo

Criar navigation hints para pedestres a partir das superfícies caminháveis, travessias e escadas já catalogadas. Isso ainda não será navmesh final de engine.
