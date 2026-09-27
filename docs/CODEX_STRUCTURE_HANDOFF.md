# Handoff do Codex — Fidelidade Estrutural

## Objetivo

Executar a **R30A** do **Bay of All Saints** de forma reproduzível, priorizando georreferenciamento, terreno, coastline/cais, vias e footprints antes de acabamento visual.

## 1. Entradas locais

Procurar e preservar a captura histórica:

```text
aleph-20260924T205631Z-aqqo7pkx/
  manifest.json
  map.osm
  terrain.tif
```

Usar também um `.blend` validado após R29. Nunca sobrescrever a captura-fonte nem o `.blend` validado.

## 2. Auditar captura e DEM

```bash
python tools/aleph/inspect_capture.py CAMINHO_DA_CAPTURA \
  --output docs/reports/aleph/mvp-centro-lacerda/source_summary.json

python tools/terrain/audit_dem.py \
  --dem CAMINHO_DA_CAPTURA/terrain.tif \
  --output docs/reports/aleph/mvp-centro-lacerda/dem_audit.json
```

Se CRS/bounds/resolução divergirem do esperado, parar e investigar antes de continuar.

## 3. Exportar pistas e auditoria da cena

```bash
blender CENA_VALIDADA.blend --background \
  --python tools/blender/extract_georef_hints.py \
  -- --output docs/reports/blender/georef_hints.json

blender CENA_VALIDADA.blend --background \
  --python tools/blender/audit_structural_scene.py \
  -- --output docs/reports/blender/structural_scene_audit_before.json
```

A auditoria estrutural atual registra OSM IDs explícitos e exclui objetos `SOURCE_GEOREF`.

## 4. Executar pipeline estrutural

Quando `rasterio` estiver disponível:

```bash
python tools/world/run_structural_pipeline.py \
  --osm CAMINHO_DA_CAPTURA/map.osm \
  --dem CAMINHO_DA_CAPTURA/terrain.tif \
  --hints docs/reports/blender/georef_hints.json \
  --audit-road-profiles \
  --output-dir artifacts/structural-pipeline/mvp-centro-lacerda
```

Sem `rasterio`, omitir `--audit-road-profiles`. Sem DEM, omitir também `--dem`.

Artefatos esperados:

```text
osm_structure.json
osm_topology_audit.json
georef_fit.json
structural_reference.json
dem_audit.json           # quando houver DEM
dem_road_profiles.json   # quando solicitado
```

Fit XY `insufficient` deve parar o fluxo. `--allow-weak-fit` é apenas diagnóstico.

## 5. Revisar topologia da fonte

Antes de usar a sobreposição, revisar `osm_topology_audit.json` nesta ordem:

1. node refs ausentes;
2. buildings não fechados;
3. coastline interrompida internamente;
4. near-misses;
5. endpoints internos de transporte;
6. componentes inesperadamente desconectados;
7. possíveis separações por bridge/tunnel/layer.

Consultar `docs/OSM_TOPOLOGY_QA.md`.

Não deformar o Blender para reproduzir um erro comprovado da fonte OSM.

## 6. Revisar fit XY

Conferir:

- anchors usados;
- `meters_per_blender_unit`;
- rotação;
- origem;
- RMS e residual máximo;
- outliers;
- Mercado Modelo way `59392558`;
- Palácio Rio Branco way `402383814` quando presentes.

Nunca promover automaticamente o anchor para `verified`.

## 7. Fechar relação vertical DEM ↔ Blender

Exportar amostras da geometria real de terreno:

```bash
blender CENA_VALIDADA.blend --background \
  --python tools/blender/export_terrain_samples.py \
  -- --output docs/reports/blender/terrain_samples.json
```

Se a seleção automática incluir objetos que não representam a superfície principal, repetir com `--include-regex` restritivo.

Calcular o fit vertical:

```bash
python tools/terrain/fit_dem_blender_vertical.py \
  --samples docs/reports/blender/terrain_samples.json \
  --fit artifacts/structural-pipeline/mvp-centro-lacerda/georef_fit.json \
  --dem CAMINHO_DA_CAPTURA/terrain.tif \
  --output docs/reports/blender/terrain_vertical_fit.json
```

Revisar:

- escala Z;
- offset Z;
- relação escala vertical/horizontal;
- RMS;
- resíduos por objeto;
- maiores outliers.

Não aplicar reescala/offset global automaticamente. Consultar `docs/DEM_BLENDER_VERTICAL_FIT.md`.

## 8. Importar referência estrutural

```bash
blender CENA_VALIDADA.blend --background \
  --python tools/blender/import_structural_reference.py \
  -- \
  --reference artifacts/structural-pipeline/mvp-centro-lacerda/structural_reference.json \
  --save-as CENA_r30a_structure_ref.blend
```

A coleção `SOURCE_GEOREF | STRUCTURAL_REFERENCE` é somente referência, oculta no render e nunca deve ser convertida automaticamente em arte final.

Camadas possíveis:

```text
REF_ROADS
REF_PEDESTRIAN
REF_STEPS
REF_BUILDINGS
REF_COASTLINE
REF_WATERFRONT
REF_RETAINING_WALLS
REF_EARTHWORKS
REF_CLIFFS
REF_WATER
REF_RAILWAYS
```

## 9. Comparar entidades da cena por OSM ID

```bash
python tools/world/compare_scene_reference_alignment.py \
  --scene-audit docs/reports/blender/structural_scene_audit_before.json \
  --reference artifacts/structural-pipeline/mvp-centro-lacerda/structural_reference.json \
  --output docs/reports/blender/scene_reference_alignment.json
```

Somente IDs explícitos são comparados. Não criar binding por semelhança de nomes. `bounds_size_review` é triagem; `center_offset_review` também precisa de validação antes de mover qualquer asset.

Consultar `docs/SCENE_REFERENCE_ALIGNMENT_QA.md`.

## 10. Corrigir a cena na ordem correta

1. problemas críticos da fonte já classificados;
2. coastline;
3. waterfront/cais;
4. eixos viários;
5. cruzamentos;
6. terreno e interfaces críticas;
7. itens do `dem_road_profiles.json`;
8. áreas pedonais e escadas;
9. cliffs, earthworks e contenções;
10. footprints;
11. integração conservadora com Hero assets.

Para cada mudança registrar OSM ID/layer, objeto Blender, problema, fonte, alteração e incerteza remanescente.

### Terreno

Nunca editar silenciosamente `terrain.tif`. Artefato comprovado deve virar correção derivada/local documentada. Não suavizar globalmente a escarpa para reduzir resíduos.

### Vias

Priorizar eixo e continuidade. Largura só é medida quando houver dado confiável; `extract_osm_structure.py` não inventa `width`.

### Coastline

Manter separados:

```text
coastline geográfica
waterfront construído
water surface visual
```

O shader da Baía se adapta à estrutura, não o contrário.

## 11. Auditoria depois

```bash
blender CENA_r30a.blend --background \
  --python tools/blender/audit_structural_scene.py \
  -- --output docs/reports/blender/structural_scene_audit_after.json
```

Registrar diferenças antes/depois e salvar uma nova revisão do `.blend`, preservando R29 e a versão intermediária com `SOURCE_GEOREF`.

## 12. Gate final da R30A

Só concluir quando:

- topologia crítica estiver classificada;
- fit XY estiver revisado;
- fit vertical estiver revisado ou sua insuficiência explicitamente registrada;
- OSM IDs prioritários estiverem comparados;
- ruas principais estiverem coerentes em planta;
- coastline/cais estiverem coerentes;
- Praça Cairu conectar corretamente Elevador, Mercado, vias e waterfront;
- problemas de DEM estiverem classificados;
- footprints principais estiverem auditados;
- nenhum Hero asset tiver sido movido para mascarar erro de base.

Somente depois avançar para R30B/R30 visual.
