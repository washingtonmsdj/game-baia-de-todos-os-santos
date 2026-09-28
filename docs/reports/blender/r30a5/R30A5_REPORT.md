# R30A.5 — proxies de runtime e primeira colisão otimizada

## Objetivo

Preparar a cena para uma futura engine sem escolher Godot, Unity ou Unreal prematuramente.
A revisão separa fontes de gameplay e cria o primeiro collider derivado do terreno, preservando integralmente a geometria-fonte R30A.4.

## Cena-fonte

`blender/salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a4_semantic_layers.blend`

SHA-256:

`BE65675CD2F0B00A4048103B373D0A497F00CD8C9603F92525D5529C2E4C6713`

## Nova cena

`blender/salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a5_runtime_proxies.blend`

SHA-256:

`C0E1566101E6A1F07F98188A3CB9B9021CB7D4F27A2ACF1CFA0D41E46544083F`

A R30A.4 permanece preservada e não foi sobrescrita.

## Collider derivado

Fonte:

`MVP | terreno corrigido | colisão estática`

- fonte: 547.464 vértices / 1.082.745 polígonos;
- proxy: 66.051 vértices / 131.097 polígonos;
- redução de polígonos: **87,8922%**;
- razão de decimação aprovada: `0,12`;
- amostras de QA: 5.023;
- erro mediano: `0,0000666 m`;
- erro P95: `0,0018215 m`;
- erro máximo observado: `0,180078 m`;
- gate: **aprovado como candidato de runtime**.

Limites do gate desta revisão:

- P95 <= `0,25 m`;
- máximo <= `1,00 m`.

O proxy não substitui a fonte e não é considerado collider final de produção. Ele existe como base otimizada para testes, chunking e futura integração de física.

## Fontes de runtime organizadas

A revisão criou/usa as seguintes responsabilidades:

- terreno de colisão derivado: 1 proxy;
- vias dirigíveis: 2 meshes, 28.528 polígonos;
- superfícies caminháveis: 8 meshes, 69.151 polígonos;
- travessias: 5 meshes, 688 polígonos;
- guias/meio-fio: 1 mesh, 18.042 polígonos;
- água: 2 meshes, 148 polígonos.

Os objetos-fonte são reutilizados por coleção/metadados quando não existe razão técnica para duplicá-los.
A única geometria nova desta rodada é o collider otimizado derivado.

## Validações

A nova cena foi reaberta com Blender 5.2.2 usando `--factory-startup` e validou:

- 4.678 objetos;
- 4.138 meshes;
- coleção raiz R30A.5 presente;
- collider presente com 131.097 polígonos;
- `boas_proxy_status=accepted_candidate`;
- `boas_revision=R30A.5`.

## Fallback BlendMCP

O fallback foi validado de forma independente da sessão OrdaX:

- BlendMCP `1.4.4`;
- Blender `5.2.2 LTS`;
- porta isolada `9877`;
- cena R30A.5 carregada;
- `get_addon_version` respondeu nativamente;
- `get_scene_info` respondeu;
- `get_object_info` inspecionou o collider R30A.5 com sucesso.

O launcher agora usa `--factory-startup --disable-autoexec`, registra somente o addon necessário e aguarda até 120 segundos pelo carregamento da cena pesada.

## Limitações e próximo passo

Ainda faltam:

1. dividir colisão em chunks apropriados para streaming/física;
2. gerar grafo de vias e conexões de cruzamentos para veículos;
3. criar hints/navmesh para pedestres e NPCs;
4. testar inclinação, largura útil e continuidade do corredor jogável;
5. só então realizar um vertical slice em engine candidata.

Arquivo de dados: `docs/reports/blender/r30a5/runtime_manifest.json`.
