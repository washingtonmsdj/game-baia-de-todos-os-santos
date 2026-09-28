# Handoff Codex — R30A.2

## Objetivo

Executar diagnóstico vertical por domínio no `.blend` versionado via Git LFS, sem alterar geometria.

Cena base:

`blender/salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a_structure_ref.blend`

SHA-256 esperado:

`ACF5F5BBA00DED0FC912116DB02DE7FCA26C43BB8DBF67A10AC5CB8A3C319A30`

Captura Aleph:

`data/aleph/aleph-20260924T205631Z-aqqo7pkx/`

Arquivos principais:

- `manifest.json`
- `map.osm`
- `terrain.tif`

## Pre-flight

1. Atualizar `main` e confirmar LFS materializado (`git lfs pull` quando necessário).
2. Confirmar SHA-256 da cena.
3. Executar:

```bash
python -m compileall -q tools tests
python -m unittest discover -s tests -p "test_*.py" -v
python tools/references/validate_registry.py --root .
```

Não modificar geometria se os testes falharem.

## Reutilizar os artefatos R30A.1

Use como base:

- `docs/reports/blender/r30a1/terrain_samples.json`
- `artifacts/structural-pipeline/mvp-centro-lacerda/georef_fit.json`
- `data/aleph/aleph-20260924T205631Z-aqqo7pkx/terrain.tif`

Se os artefatos em `artifacts/` não existirem na estação atual, regenere o pipeline estrutural usando os mesmos inputs históricos. Não invente substitutos.

## Executar domínio vertical

Execute:

```bash
python tools/terrain/analyze_vertical_domains.py \
  --samples docs/reports/blender/r30a1/terrain_samples.json \
  --fit artifacts/structural-pipeline/mvp-centro-lacerda/georef_fit.json \
  --dem data/aleph/aleph-20260924T205631Z-aqqo7pkx/terrain.tif \
  --output docs/reports/blender/r30a2/vertical_domains.json
```

Mantenha inicialmente os defaults:

- nível do mar: `0 m`;
- grid: `50 m`;
- fila de revisão: mediana absoluta >= `5 m` com pelo menos 8 amostras.

Esses valores servem para diagnóstico/triagem. Não ajuste thresholds apenas para obter `candidate`.

## O que comparar

Compare explicitamente com R30A.1:

- total de amostras válidas;
- amostras DEM < 0 m;
- amostras DEM >= 0 m;
- RMS do fit completo;
- RMS do fit terrestre;
- mediana absoluta do fit completo/terrestre;
- escala Z completa/terrestre;
- offset Z completo/terrestre;
- razão escala vertical/horizontal;
- qualidade completa/terrestre.

## Grade de resíduos

Analise `land_spatial_grid.review_cells`.

Para as células com maior mediana absoluta:

1. converter bounds EPSG:3857 para a região correspondente da cena usando o fit XY;
2. identificar quais partes físicas estão ali: escarpa, Cidade Alta, Cidade Baixa, ladeira, Praça Cairu, cais ou área marítima;
3. conferir se o objeto de terreno representa superfície física, plataforma artificial, colisão ou preenchimento histórico;
4. registrar conclusão sem mover vértices.

Produza uma tabela das 10 células terrestres mais críticas com:

- grid index;
- bounds;
- amostras;
- faixa DEM;
- mediana Z Blender;
- mediana absoluta residual;
- região interpretada da cena;
- provável causa;
- confiança da interpretação.

## Batimetria

Não trate DEM negativo como nodata automaticamente.

A documentação Mapzen/Tilezen registra ETOPO1 para batimetria oceânica em todos os zooms. Portanto valores negativos na Baía devem permanecer no relatório como domínio separado e não participar do fit terrestre padrão.

Não elevar fundo da Baía para 0 m e não modificar `terrain.tif`.

## Reexportação de terrain_samples

A R30A.1 já tem uma seleção explícita correta por `--include-regex`. Reutilize-a salvo se a cena tiver mudado.

Se for necessário reexportar, use o mesmo objeto:

`MVP | terreno corrigido | colisão estática`

O modo `strict` atualizado não deve mais aceitar `dem` como substring em palavras como `Ordem`.

Não amplie a seleção para proxies, fachada, passarela, calçadas ou volumes estimados.

## Proibições nesta rodada

Não:

- aplicar escala Z;
- aplicar offset Z;
- suavizar terreno;
- mover coastline/cais;
- deslocar ruas;
- corrigir escarpa;
- alterar Hero assets;
- remodelar Mercado Modelo;
- apagar batimetria;
- salvar uma revisão geométrica apenas para registrar diagnóstico.

Se apenas relatórios forem gerados, o `.blend` pode permanecer byte a byte igual.

## Entregáveis

Criar:

- `docs/reports/blender/r30a2/vertical_domains.json`
- `docs/reports/blender/r30a2/R30A2_REPORT.md`
- `docs/reports/blender/r30a2/r30a2_status.json`

No relatório registrar:

1. R30A.1 × R30A.2;
2. quantidade/percentual de amostras batimétricas;
3. resultado do fit terrestre;
4. top 10 células residuais;
5. regiões físicas correspondentes;
6. quais divergências parecem ser limitação do DEM;
7. quais parecem ser geometria histórica do MVP;
8. blockers restantes;
9. recomendação objetiva para a próxima revisão estrutural.

## Critério para avançar

Somente autorizar a primeira correção geométrica se existir uma região com:

- discrepância espacialmente localizada;
- causa razoavelmente identificada;
- dados de referência suficientes;
- correção local que não dependa de reescala global ou offset mágico.

Se isso não estiver demonstrado, manter o diagnóstico e aprofundar a causa.
