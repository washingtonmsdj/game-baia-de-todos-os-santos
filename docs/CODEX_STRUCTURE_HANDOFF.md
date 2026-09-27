# Handoff do Codex — Fidelidade Estrutural

## Objetivo

Aplicar no Blender uma revisão estrutural reproduzível do MVP de **Bay of All Saints**, priorizando terreno, ruas, coastline/cais e footprints antes de qualquer passe visual.

## Pré-requisitos locais

Procurar a captura histórica:

```text
aleph-20260924T205631Z-aqqo7pkx/
```

Esperado quando disponível:

```text
manifest.json
map.osm
terrain.tif
```

Também é necessário um `.blend` validado após R29.

## 1. Preservar originais

Não editar nem mover os arquivos da captura-fonte.

Não sobrescrever o `.blend` validado.

Criar diretórios de saída separados para relatórios/artifacts.

## 2. Auditar a captura

```bash
python tools/aleph/inspect_capture.py CAMINHO_DA_CAPTURA \
  --output docs/reports/aleph/mvp-centro-lacerda/source_summary.json
```

Se existir `terrain.tif`:

```bash
python tools/terrain/audit_dem.py \
  --dem CAMINHO_DA_CAPTURA/terrain.tif \
  --output docs/reports/aleph/mvp-centro-lacerda/dem_audit.json
```

Não continuar tratando o DEM como EPSG:3857 se a auditoria indicar outro CRS sem investigar a origem.

## 3. Extrair pistas da cena

```bash
blender CENA_VALIDADA.blend --background \
  --python tools/blender/extract_georef_hints.py \
  -- --output docs/reports/blender/georef_hints.json
```

Depois auditar a estrutura existente:

```bash
blender CENA_VALIDADA.blend --background \
  --python tools/blender/audit_structural_scene.py \
  -- --output docs/reports/blender/structural_scene_audit_before.json
```

## 4. Executar pipeline estrutural

Com DEM:

```bash
python tools/world/run_structural_pipeline.py \
  --osm CAMINHO_DA_CAPTURA/map.osm \
  --dem CAMINHO_DA_CAPTURA/terrain.tif \
  --hints docs/reports/blender/georef_hints.json \
  --output-dir artifacts/structural-pipeline/mvp-centro-lacerda
```

Para incluir o QA do DEM sob as vias no mesmo comando, quando `rasterio` estiver disponível:

```bash
python tools/world/run_structural_pipeline.py \
  --osm CAMINHO_DA_CAPTURA/map.osm \
  --dem CAMINHO_DA_CAPTURA/terrain.tif \
  --hints docs/reports/blender/georef_hints.json \
  --audit-road-profiles \
  --output-dir artifacts/structural-pipeline/mvp-centro-lacerda
```

Sem DEM, omitir `--dem` e `--audit-road-profiles`.

O comando gera artefatos separados:

```text
osm_structure.json
osm_topology_audit.json
georef_fit.json
structural_reference.json
dem_audit.json           # se --dem foi fornecido
dem_road_profiles.json   # se --audit-road-profiles foi solicitado
```

Se o fit não atingir `candidate` ou `strong_candidate`, o pipeline deve parar. Não usar `--allow-weak-fit` para produção; ele existe apenas para diagnóstico explícito.

## 5. Revisar o QA topológico antes de usar a sobreposição

Ler:

```text
osm_topology_audit.json
```

Consultar `docs/OSM_TOPOLOGY_QA.md`.

Prioridade de revisão:

1. `missing_node_refs`;
2. `unclosed_buildings` relevantes;
3. endpoints internos da `coastline`;
4. `near_misses`;
5. endpoints internos de transporte;
6. componentes desconectados inesperados.

Não corrigir automaticamente:

- rua sem saída legítima;
- endpoint na borda do recorte;
- possível ponte/túnel/layer diferente;
- píer, muro, cliff ou earthwork que realmente termina.

Se a topologia-fonte estiver comprovadamente problemática em uma área crítica, registrar a limitação antes de corrigir o Blender. Não deformar a cena apenas para reproduzir um erro da referência.

## 6. Auditar o perfil do terreno sob as vias

Quando `terrain.tif` estiver disponível e `rasterio` estiver instalado, usar `--audit-road-profiles` no pipeline principal ou executar:

```bash
python tools/terrain/audit_road_profiles.py \
  --dem CAMINHO_DA_CAPTURA/terrain.tif \
  --structure artifacts/structural-pipeline/mvp-centro-lacerda/osm_structure.json \
  --output docs/reports/aleph/mvp-centro-lacerda/dem_road_profiles.json
```

O relatório cria uma `review_queue` com trechos que merecem inspeção por:

- `nodata`;
- inclinação local acima do threshold de triagem;
- salto vertical entre amostras próximas.

Essas flags **não autorizam suavização automática**. Salvador possui escarpa, ladeiras, muros e escadas reais. Classificar cada caso antes de corrigir.

Consultar `docs/TERRAIN_ROAD_QA.md`.

## 7. Revisar o fit antes do Blender

Conferir:

- `anchor_count`;
- `meters_per_blender_unit`;
- `rotation_epsg3857_to_blender_deg`;
- RMS;
- residual máximo;
- outliers;
- Mercado Modelo;
- Palácio Rio Branco;
- outros anchors distribuídos no recorte.

Não promover `world_anchor_status=verified` apenas porque o script terminou sem erro.

## 8. Importar referência estrutural

```bash
blender CENA_VALIDADA.blend --background \
  --python tools/blender/import_structural_reference.py \
  -- \
  --reference artifacts/structural-pipeline/mvp-centro-lacerda/structural_reference.json \
  --save-as CENA_r30a_structure_ref.blend
```

A cena resultante deve conter:

```text
SOURCE_GEOREF | STRUCTURAL_REFERENCE
```

com objetos `REF_*` ocultos no render, incluindo quando presentes:

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

Nunca converter automaticamente `REF_*` em geometria final.

## 9. Correção estrutural manual/assistida

Trabalhar nesta ordem:

1. topologia-fonte crítica já classificada;
2. coastline;
3. waterfront/cais;
4. eixos viários;
5. cruzamentos;
6. terreno nas interfaces críticas e itens da `review_queue` do DEM;
7. áreas pedonais/escadas;
8. cliffs, earthworks e contenções;
9. footprints;
10. integração com Hero assets.

Para cada correção relevante registrar:

```text
feature/layer
OSM ID quando aplicável
objeto Blender alterado
problema detectado
fonte usada
mudança aplicada
incerteza remanescente
```

## 10. Terreno

Não editar o `terrain.tif` original.

Quando o DEM tiver artefato real (spike/cliff/nodata/interpolação ruim):

- preservar o DEM;
- criar camada/mesh derivada corrigida;
- marcar a correção como local;
- documentar a justificativa;
- relacionar a correção aos OSM IDs/segmentos afetados quando aplicável.

A escarpa de Salvador deve continuar fisicamente legível; não suavizar globalmente apenas para facilitar o blockout.

## 11. Ruas

Priorizar eixo/continuidade. Largura só pode ser tratada como medida quando houver fonte explícita.

`extract_osm_structure.py` não inventa largura para ruas sem `width=*`.

Se a largura tiver de permanecer artística/aproximada para gameplay, documentar essa diferença separadamente da posição geográfica do eixo.

## 12. Coastline / waterfront / água

Não misturar:

```text
coastline
waterfront construído
water surface visual
```

O contorno da água e o cais devem ser resolvidos antes do shader da Baía.

## 13. Auditoria depois das correções

Executar novamente:

```bash
blender CENA_r30a.blend --background \
  --python tools/blender/audit_structural_scene.py \
  -- --output docs/reports/blender/structural_scene_audit_after.json
```

Registrar diferenças antes/depois.

Se o terreno foi corrigido de forma derivada, repetir `audit_road_profiles.py` sobre o DEM/representação derivada apropriada apenas quando houver um raster georreferenciado comparável; caso contrário, registrar a validação diretamente no Blender.

## 14. Saída esperada

Salvar nova revisão, por exemplo:

```text
CENA_r30a.blend
```

Preservar:

- R29 validada;
- versão com referência carregada;
- R30A corrigida;
- `osm_topology_audit.json`;
- relatórios antes/depois;
- `dem_road_profiles.json` quando aplicável.

## Gate final

Só declarar R30A concluída quando:

- itens topológicos críticos do recorte estiverem classificados;
- a referência estrutural puder ser desligada e a cena continuar coerente;
- ruas principais não estiverem deslocadas de forma evidente;
- coastline/cais estiverem coerentes;
- Praça Cairu conectar corretamente Elevador, Mercado, vias e waterfront;
- problemas de DEM restantes estiverem registrados/classificados;
- nenhum Hero asset tiver sido deslocado apenas para mascarar um erro da base.

Depois disso, avançar para o passe visual R30B/R30.
