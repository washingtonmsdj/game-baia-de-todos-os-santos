# R30A.9 — ônibus Integra Salvador

## Objetivo

Introduzir o primeiro ônibus urbano de Salvador no vertical slice de **Bay of All Saints** sem contaminar as camadas estruturais já validadas.

A revisão parte da cena oficial R30A.8 e deve salvar um novo `.blend`:

`blender/salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a9_integra_bus.blend`

A R30A.8 não deve ser sobrescrita.

## Asset de origem

Arquivo recebido:

`yellow city bus 3d model.glb`

SHA-256 aprovado:

`F3D5DEE69DCAB15379817A9AE13E562DF8023FD7AF38E8B6A0CDB4742AB650A2`

Auditoria inicial:

- 67 geometrias;
- 69 nós;
- 992.121 vértices;
- 1.954.141 triângulos;
- escala bruta arbitrária;
- material detectado como um único slot lógico na inspeção externa.

O GLB é tratado como **fonte de autoria**, não como asset runtime final.

## Automação

Script:

`automation/blender/r30a9_integrate_integra_bus.py`

A automação:

1. exige a cena oficial R30A.8 aberta e sem alterações não salvas;
2. exige o GLB correto pelo SHA-256;
3. importa o asset sem alterar terreno, água, georreferenciamento ou grafo de vias;
4. organiza o veículo em coleção própria;
5. normaliza dimensões para uma referência inicial de 12,0 m × 2,55 m × 3,25 m;
6. posiciona o ônibus em staging sobre um segmento do grafo R30A.7 próximo ao centro da cena;
7. registra metadados deixando explícito que o posicionamento é `candidate_only`;
8. salva uma nova revisão R30A.9;
9. gera `docs/reports/blender/r30a9/integra_bus_scene.json` com bounds, estatísticas e SHA-256 da nova cena.

O binário pode ser fornecido por:

- variável `BOAS_INTEGRA_BUS_GLB`; ou
- `artifacts/incoming/integra-salvador/yellow city bus 3d model.glb`; ou
- `artifacts/incoming/yellow city bus 3d model.glb`.

`artifacts/` continua fora do Git.

## Coleções e metadados

Coleção principal:

`37 VEHICLES | INTEGRA SALVADOR R30A9`

Fonte importada:

`37.1 SOURCE | INTEGRA SALVADOR`

Root do veículo:

`R30A9 | BUS | INTEGRA SALVADOR 01`

Metadados principais:

- `boas_asset_id=vehicle-integra-salvador-01`;
- `boas_asset_type=vehicle`;
- `boas_vehicle_class=urban_bus`;
- `boas_traffic_binding=candidate_only`;
- `boas_placement=road_graph_centerline_staging`;
- `boas_runtime_status=authoring_only_needs_lod_and_vehicle_rig`.

## Limites desta revisão

O grafo R30A.7 representa topologia/eixo viário e **não é lane graph final**. Portanto, o ônibus colocado sobre esse helper serve para revisão visual e de escala, não para ser tratado como tráfego pronto.

Esta revisão não cria automaticamente:

- IA de trânsito;
- lane binding definitivo;
- wheel rig;
- suspensão;
- collider final;
- LODs;
- material runtime otimizado.

Esses itens exigem validação própria para não esconder problemas do asset de origem.

## Gate de validação

Antes de promover o ônibus para runtime:

1. capturar vistas frontal, traseira e laterais no Blender;
2. verificar escala em relação às ruas e ao jogador;
3. identificar rodas e pivôs corretos;
4. criar LODs preservando silhueta, janelas e rodas;
5. criar collider simplificado separado da malha visual;
6. revisar materiais/texturas e draw calls;
7. definir binding real a lanes quando a camada de tráfego existir;
8. validar reabertura da R30A.9 e registrar SHA-256.

## Estado

Automação e contrato do asset estão versionados na `main`. A revisão só deve ser marcada como aplicada depois que a automação for executada na única janela visível do Blender e a nova cena for validada visualmente.
