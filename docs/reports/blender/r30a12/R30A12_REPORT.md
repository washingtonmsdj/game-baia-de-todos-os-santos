# R30A.12 — Links Funcionais de Navegação

## Objetivo

Promover apenas conexões pedonais sustentadas por evidência explícita, sem gerar navmesh ou criar atalhos por proximidade.

A revisão parte da R30A.11 e foi aplicada ao vivo na única janela visível do Blender.

Cena final:

`blender/salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a12_nav_links.blend`

SHA-256:

`D5A1BA39250E9AB291D45C9BE8B9058FE84FD82F7D6B01CC5FD309E690CB8835`

## Travessias

Foram avaliadas as 5 travessias existentes. Todas possuem:

- match exato entre `osm_node_id` da travessia e o nó do grafo pedonal;
- deslocamento visual ≤ `2,5 m`;
- status de contrato `reviewed_candidate`.

Resultado no Blender: `5/5` links curtos de travessia materializados.

## Escadas

O contrato preserva os endpoints reais dos 6 ways `highway=steps`, totalizando 12 anchors candidatos.

Resultado no Blender:

- `11/12` endpoints materializados sobre o collider jogável;
- `1/12` permaneceu unresolved.

Endpoint unresolved:

- way OSM `530127473` — `Escadaria do Passo`;
- node OSM `5148629906`;
- endpoint `start`.

Esse ponto não recebeu posição inventada porque não houve contato com a superfície jogável atual.

## Coleções

- `38 GAMEPLAY | NAV LINKS R30A12`;
- `38.1 NAV | REVIEWED CROSSING LINKS`;
- `38.2 NAV | STEP ENDPOINTS`.

Os objetos também são vinculados à coleção runtime `33.7 RUNTIME | NAV HINTS` quando ela existe.

## Regras de segurança

- travessias não são ligadas apenas por distância;
- o ID OSM precisa coincidir exatamente;
- o deslocamento visual precisa respeitar o limite do contrato;
- endpoints de escada sem superfície permanecem unresolved;
- `start/end` de escada não é reinterpretado como `top/bottom` sem evidência vertical;
- nenhum helper desta revisão é navmesh final.

## Próximo passo

Usar esses links revisados no vertical slice de locomoção: jogador/NPC a pé, transição em travessias, escadas e entradas/saídas, mantendo a navegação independente da engine até a decisão final de runtime.
