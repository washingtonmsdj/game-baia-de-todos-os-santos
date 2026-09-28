# R30A.6 — Collision Chunks

## Objetivo

Preparar a colisão do terreno para runtime/streaming sem alterar a geometria-fonte nem escolher engine.

A revisão foi executada ao vivo na única janela visível do Blender, usando OrdaX/Blender Live. O BlendMCP 1.4.4 ficou acoplado à mesma instância na porta 9877 como fallback.

## Fonte

Cena de entrada:

`blender/salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a5_runtime_proxies.blend`

Collider-fonte:

`R30A5 | COLLISION | terrain proxy`

Polígonos do collider-fonte: `131.097`.
## Candidatos avaliados

| Tamanho | Chunks | P95 polígonos | Máximo | Resultado |
| --- | ---: | ---: | ---: | --- |
| 64 m | 175 | 2.234,4 | 5.304 | chunks demais |
| 128 m | 63 | 6.875,5 | 12.000 | aprovado |
| 256 m | 25 | 20.595,4 | 21.922 | chunks pesados demais |

A política atual limita a 80 chunks, 15.000 polígonos no pior chunk e 10.000 no P95. Por isso, `128 m` foi selecionado sem valor mágico manual.

## Resultado

- chunks: `63`;
- partição de polígonos: exata;
- soma dos polígonos: `131.097`;
- razão de duplicação de vértices nas bordas: `1,0468577`;
- maior chunk: `12.000` polígonos;
- engine binding: `unbound_engine_agnostic`.
## Validação ao vivo

O chunk `R30A6 | COLLISION | x-002_y-002` foi consultado pelo BlendMCP na mesma instância visível do Blender e retornou `6.121` vértices e `12.000` polígonos.

Cena de saída:

`blender/salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a6_collision_chunks.blend`

SHA-256:

`482A9F4F8E1FCDBA0A912922AC130EC0810D604F67B8FEC0FB7B5603B445CC3E`

## Próximo passo

Construir o grafo lógico de vias/cruzamentos e navigation hints do vertical slice. Não transformar automaticamente OSM em IA de trânsito nem escolher engine nesta fase.
