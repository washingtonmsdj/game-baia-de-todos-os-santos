# QA de Terreno sob Vias — Bay of All Saints

## Objetivo

Detectar pontos em que o `terrain.tif` pode estar produzindo comportamento suspeito sob ruas e áreas pedonais antes de corrigir a cena Blender.

Isso é especialmente importante em Salvador por causa de:

- escarpa Cidade Alta/Cidade Baixa;
- ladeiras;
- contenções;
- escadarias;
- transições abruptas próximas ao Elevador Lacerda;
- artefatos de DEM em bordas muito íngremes.

## Ferramenta

`tools/terrain/audit_road_profiles.py`

Ela cruza:

- `terrain.tif` em EPSG:3857;
- `osm_structure.json` produzido por `extract_osm_structure.py`.

Por padrão analisa:

- `roads`;
- `pedestrian`.

`steps` só entra com `--include-steps`, porque inclinação alta em escadaria pode ser legítima e geraria muito ruído na fila de revisão.

## Dependência

A amostragem exige `rasterio` no ambiente local:

```bash
python -m pip install rasterio
```

Não instalar isso dentro do Blender sem necessidade. O QA pode rodar no Python do ambiente de projeto antes da etapa Blender.

## Uso

```bash
python tools/terrain/audit_road_profiles.py \
  --dem CAMINHO/terrain.tif \
  --structure artifacts/world/mvp-centro-lacerda/osm_structure.json \
  --output docs/reports/aleph/mvp-centro-lacerda/dem_road_profiles.json
```

Parâmetros padrão de QA:

```text
spacing = 5 m projetados
grade_review = 0.35 (35%)
jump_review = 4 m entre amostras adjacentes
```

Esses valores são **heurísticas de triagem**, não limites de engenharia e não significam automaticamente que o terreno está errado.

## Saída

O relatório contém para cada via:

- OSM ID;
- nome e classe `highway` quando presentes;
- quantidade de amostras;
- amostras `nodata`;
- Z mínimo/máximo;
- amplitude vertical;
- maior grade absoluta;
- percentil 95 da grade absoluta;
- maior salto vertical;
- segmentos marcados para revisão.

Também cria `review_queue`, ordenada pelos casos mais extremos.

## Interpretação

### `nodata`

O DEM não forneceu elevação válida em uma ou mais amostras. Não preencher automaticamente por interpolação silenciosa.

### `grade_review`

A inclinação local superou o threshold de triagem. Em Salvador isso pode ser real; conferir contexto antes de mexer.

### `jump_review`

A diferença de elevação entre duas amostras próximas superou o limite de triagem. Pode indicar:

- borda de escarpa legítima;
- muro/contenção;
- via passando por viaduto/estrutura;
- artefato do DEM;
- alinhamento OSM incorreto para o raster;
- recorte/nodata.

Nunca assumir que `jump_review` significa "suavizar terreno".

## Procedimento na R30A

Para cada item da `review_queue`:

1. localizar o OSM ID na referência estrutural;
2. verificar a via correspondente no Blender;
3. verificar se o salto é coerente com escada, muro, viaduto ou escarpa;
4. conferir outros anchors/terreno ao redor;
5. classificar como:
   - `real_feature`;
   - `dem_artifact`;
   - `alignment_issue`;
   - `source_uncertain`;
6. corrigir somente quando a causa estiver clara;
7. registrar a decisão no relatório R30A.

## Correção de artefato DEM

Quando um artefato for comprovado:

- preservar `terrain.tif` original;
- criar uma superfície derivada/corrigida;
- limitar a alteração à região necessária;
- registrar OSM IDs/área afetados;
- registrar motivo e método;
- comparar antes/depois.

Não aplicar smoothing global à escarpa para resolver poucos pontos locais.

## Precisão

As distâncias horizontais usadas pelo QA vêm de EPSG:3857. Elas são adequadas para triagem relativa do recorte, mas o relatório não deve ser tratado como levantamento topográfico certificado.

A finalidade é encontrar **onde investigar**, não substituir medição de campo.

## Auditoria veicular B39 — 04/10/2026

A fonte autora é B39 no catálogo; produção B30. A rede foi examinada com quatro contatos da Rondesp V25, mantendo bindings por OSM way e ordem dos nós. Relatórios `rondesp_network_audit_b38.json`, `rondesp_turn_audit.json` e `rondesp_driver_review_b39.json` registram coverage e pendências. Critérios de raio, grade, torção e tolerância do proxy são probes candidatos, não normas de engenharia ou aprovação AAA. Posição de câmera é candidata; material local de vidro permite inspeção. O percurso contínuo Montanha tem 3.192 apoios interpolados e não constitui validação de suspensão/tráfego/colisão volumétrica. Não reduzir resíduos por deformação global ou conectar endpoints sem apoio.

## B40 — largura e circulação

Priorizar apoio/camada/colisor, largura útil e faixa, fluxo legal e ônibus, nessa ordem. Regras e ferramentas em `ROAD_TRANSPORT_PRODUCTION.md`. Nenhuma largura real foi inventada ou aplicada na B40. Guias candidatas são referência; cenário visual preservado. Registrar ocorrências por OSM way/par de nós e preservar histórico, inclusive falhas não observadas que ainda precisam de confirmação.
