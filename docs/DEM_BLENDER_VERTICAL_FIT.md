# Fit Vertical DEM ↔ Blender — Bay of All Saints

## Objetivo

Medir a relação entre as elevações do `terrain.tif` e o eixo Z da geometria de terreno existente no Blender.

O fit XY já resolve:

- escala horizontal;
- rotação;
- translação/origem.

Ele não prova que o Z da cena segue a mesma escala nem qual offset vertical foi usado historicamente.

Este pipeline estima:

```text
Z_blender = escala_vertical * Z_dem_m + offset_vertical
```

sem alterar o terreno.

## Por que isso importa em Salvador

O MVP depende fortemente de:

- Cidade Alta;
- Cidade Baixa;
- escarpa;
- acessos superior/inferior do Elevador Lacerda;
- ladeiras, escadas e contenções;
- Praça Cairu e aproximação do cais.

Antes de corrigir esses elementos, precisamos distinguir:

- diferença global de escala/offset vertical;
- correção local legítima;
- artefato do DEM;
- mesh histórica classificada indevidamente como terreno.

## 1. Exportar amostras do Blender

```bash
blender CENA.blend --background \
  --python tools/blender/export_terrain_samples.py \
  -- \
  --output docs/reports/blender/terrain_samples.json
```

Por padrão são selecionadas meshes cujo nome/coleção contém termos de terreno/relevo/DEM/encosta.

Se a nomenclatura histórica produzir falsos positivos, restringir explicitamente:

```bash
blender CENA.blend --background \
  --python tools/blender/export_terrain_samples.py \
  -- \
  --output docs/reports/blender/terrain_samples.json \
  --include-regex "GR03 TERRENO|GR19 MVP.*TERRENO|RELEVO"
```

O exportador:

- não modifica a cena;
- não inclui `SOURCE_GEOREF`;
- usa vértices da mesh original em world space;
- limita a amostragem por objeto de forma determinística;
- registra os objetos de origem.

## 2. Pré-requisitos

É necessário:

- `terrain_samples.json`;
- `georef_fit.json` com qualidade `candidate` ou `strong_candidate`;
- `terrain.tif` em EPSG:3857;
- Python com `rasterio`.

## 3. Executar o fit vertical

```bash
python tools/terrain/fit_dem_blender_vertical.py \
  --samples docs/reports/blender/terrain_samples.json \
  --fit artifacts/structural-pipeline/mvp-centro-lacerda/georef_fit.json \
  --dem CAMINHO_DA_CAPTURA/terrain.tif \
  --output docs/reports/blender/terrain_vertical_fit.json
```

## Como funciona

Para cada amostra Blender:

1. pega `(X_blender, Y_blender, Z_blender)`;
2. inverte a transformação XY para recuperar EPSG:3857;
3. amostra o DEM nessa coordenada;
4. cria um par `(Z_dem, Z_blender)`;
5. estima escala e offset por regressão linear;
6. rejeita outliers de forma robusta;
7. calcula resíduos globais e por objeto.

## Saída principal

`terrain_vertical_fit.json` contém:

- `scale_z_blender_units_per_dem_meter`;
- `dem_meters_per_blender_z_unit`;
- `z_offset_blender_units`;
- RMS do resíduo;
- mediana/máximo do resíduo;
- relação entre escala vertical e escala horizontal;
- número de amostras válidas;
- `nodata`;
- outliers removidos;
- resíduos por objeto;
- maiores resíduos espaciais.

## Interpretação

### Escala vertical próxima da horizontal

É um bom sinal de unidades coerentes, mas não prova precisão topográfica.

EPSG:3857 é uma projeção horizontal e o DEM pode usar um datum vertical distinto. Portanto a comparação é tratada como consistência, não como igualdade obrigatória exata.

### Offset vertical

Um offset global pode ser parte do pipeline histórico da cena. Não zerar automaticamente.

Primeiro verificar:

- como o DEM foi importado;
- níveis conhecidos do MVP;
- acessos superior/inferior;
- relação com a superfície da água;
- correções locais históricas.

### Outliers

Outlier não significa erro automaticamente. Pode ser:

```text
local_manual_correction
DEM_artifact
wrong_terrain_object
retaining_or_cliff_geometry
source_nodata_edge
historical_blockout_adjustment
```

Revisar espacialmente os maiores resíduos antes de editar a cena.

## Gate de qualidade

A ferramenta retorna apenas:

```text
strong_candidate
candidate
insufficient
```

Mesmo `strong_candidate` continua `candidate_only`: não modifica `area.json`, não altera Z da cena e não declara levantamento certificado.

## Uso na R30A

A ordem recomendada é:

1. fechar QA topológico OSM;
2. fechar fit XY;
3. auditar DEM;
4. exportar amostras do terreno;
5. calcular fit vertical;
6. revisar maiores resíduos;
7. comparar com `dem_road_profiles.json`;
8. somente então corrigir artefatos locais de terreno/interface.

## Regra anti-gambiarra

Não:

- aplicar `Z -= offset` em toda a cena automaticamente;
- reescalar todo o terreno sem revisar o fit;
- remover outliers da geometria só porque o algoritmo os removeu da regressão;
- suavizar a escarpa para melhorar RMS;
- usar o fit vertical para substituir dados de campo/levantamento.

O objetivo é entender a transformação histórica e localizar divergências reais.
