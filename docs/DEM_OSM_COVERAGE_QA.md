# QA de Cobertura DEM ↔ OSM

## Objetivo

Antes de usar `terrain.tif` para ajustar relevo, vias ou escarpa, confirmar que o raster realmente cobre a estrutura OSM do recorte.

Isso evita um erro silencioso perigoso: extrapolar altitude ou interpretar uma borda de tile como relevo real.

## Ferramenta

```bash
python tools/terrain/compare_dem_osm_coverage.py \
  --dem-audit artifacts/structural-pipeline/dem_audit.json \
  --structure artifacts/structural-pipeline/osm_structure.json \
  --output artifacts/structural-pipeline/dem_osm_coverage.json
```

Por padrão é exigida margem projetada de 20 m entre o bbox estrutural OSM e cada borda do DEM.

O valor é um gate de segurança/QA e pode ser ajustado conforme o recorte, mas nunca deve ser usado para fingir cobertura inexistente.

## Estados

### `covered_with_margin`

A estrutura OSM está integralmente dentro do DEM e possui a margem mínima solicitada em todas as bordas.

Ainda assim isso **não prova qualidade vertical**. Depois devem ser executados o fit vertical e o QA de perfis das vias.

### `covered_edge_sensitive`

Toda a estrutura OSM está dentro do DEM, mas ao menos uma borda está próxima do limite do raster.

Tratar com cuidado:

- vias junto às extremidades;
- coastline próxima à borda;
- mosaicos de tiles;
- nodata;
- descontinuidades locais.

### `insufficient`

Parte do bbox estrutural OSM está fora do DEM.

O comando termina com código 2. O pipeline estrutural para por padrão.

Não:

- esticar o raster;
- repetir pixel da borda;
- extrapolar Z;
- ajustar vias para caber no DEM;
- declarar o recorte coberto.

## Métricas registradas

O relatório contém:

- bounds EPSG:3857 do DEM;
- bounds EPSG:3857 da estrutura OSM;
- interseção;
- margem oeste/sul/leste/norte;
- margem aproximada em pixels;
- razão de cobertura do bbox OSM;
- warnings.

## Integração no pipeline

Quando `--dem` é fornecido a `tools/world/run_structural_pipeline.py`, a ordem passa a ser:

```text
audit_dem
→ extract_osm_structure
→ compare_dem_osm_coverage
→ audit_osm_topology
→ [audit_road_profiles opcional]
→ solve_osm_blender_fit
→ build_blender_structure_reference
```

Exemplo:

```bash
python tools/world/run_structural_pipeline.py \
  --osm CAMINHO/map.osm \
  --hints docs/reports/blender/georef_hints.json \
  --dem CAMINHO/terrain.tif \
  --dem-statistics \
  --audit-road-profiles \
  --output-dir artifacts/structural-pipeline/mvp-centro-lacerda
```

## Diagnóstico excepcional

Existe:

```text
--allow-insufficient-dem-coverage
```

Esse parâmetro serve somente para permitir que outros relatórios sejam produzidos durante diagnóstico. Ele não promove o DEM, não autoriza extrapolação e não transforma cobertura insuficiente em aceitável.

## Regra para o MVP

Para a R30A, qualquer `insufficient` deve permanecer bloqueador de correção baseada em DEM até que:

- a captura histórica correta seja recuperada; ou
- uma fonte estrutural substituta seja escolhida e registrada explicitamente.
