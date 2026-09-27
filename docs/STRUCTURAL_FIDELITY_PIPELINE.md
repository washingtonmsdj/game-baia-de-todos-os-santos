# Pipeline de Fidelidade Estrutural — Bay of All Saints

## Objetivo

Priorizar a fidelidade física de Salvador antes de detalhe visual fino. O foco desta etapa é:

- relevo;
- ruas e cruzamentos;
- calçadas, áreas pedonais e escadarias;
- footprints de edifícios;
- contenções;
- coastline;
- cais, píeres e waterfront;
- alinhamento entre Cidade Alta e Cidade Baixa.

Imagens não são requisito para esta etapa. O pipeline usa principalmente `map.osm`, `terrain.tif`, o fit geográfico validado e a cena Blender existente.

## Regra principal

**Dados-fonte e geometria final nunca são a mesma camada.**

O pipeline cria uma sobreposição de referência. O Codex compara a cena contra essa sobreposição e corrige a geometria autoral em revisão separada.

Não mover ruas, hero assets ou terreno automaticamente apenas porque uma referência foi importada.

## Etapa 1 — recuperar e auditar a captura Aleph

Na estação que contém a captura histórica, localizar preferencialmente:

```text
aleph-20260924T205631Z-aqqo7pkx/
  manifest.json
  map.osm
  terrain.tif
```

Executar:

```bash
python tools/aleph/inspect_capture.py CAMINHO_DA_CAPTURA \
  --output docs/reports/aleph/mvp-centro-lacerda/source_summary.json
```

Auditar o DEM:

```bash
python tools/terrain/audit_dem.py \
  --dem CAMINHO_DA_CAPTURA/terrain.tif \
  --output docs/reports/aleph/mvp-centro-lacerda/dem_audit.json
```

`audit_dem.py` usa `rasterio` quando disponível e, como alternativa, `gdalinfo -json`. Se nenhuma implementação geoespacial confiável estiver disponível, ele falha em vez de interpretar o TIFF parcialmente.

## Etapa 2 — extrair estrutura do OSM

Executar:

```bash
python tools/world/extract_osm_structure.py \
  --osm CAMINHO_DA_CAPTURA/map.osm \
  --output artifacts/world/mvp-centro-lacerda/osm_structure.json
```

São classificadas as seguintes camadas quando presentes:

```text
roads
pedestrian
steps
buildings
coastline
waterfront
retaining_walls
water
railways
```

Para vias, `width_m_tagged` e `lanes_tagged` só aparecem quando o OSM fornece esses dados explicitamente. O pipeline **não inventa largura** com base na classe da rua.

## Etapa 3 — fechar o fit OSM → Blender

Primeiro exportar pistas do `.blend`:

```bash
blender cena.blend --background \
  --python tools/blender/extract_georef_hints.py \
  -- --output docs/reports/blender/georef_hints.json
```

Depois executar:

```bash
python tools/georef/solve_osm_blender_fit.py \
  --hints docs/reports/blender/georef_hints.json \
  --osm CAMINHO_DA_CAPTURA/map.osm \
  --output docs/reports/blender/georef_fit.json
```

Consultar `docs/GEOREFERENCE_FIT_PIPELINE.md` para os critérios de promoção.

## Etapa 4 — gerar referência em coordenadas Blender

Somente quando o fit tiver qualidade `candidate` ou `strong_candidate`:

```bash
python tools/world/build_blender_structure_reference.py \
  --structure artifacts/world/mvp-centro-lacerda/osm_structure.json \
  --fit docs/reports/blender/georef_fit.json \
  --output docs/reports/blender/structural_reference.json
```

O arquivo preserva:

- OSM ID;
- layer;
- tags;
- métricas explicitamente disponíveis;
- pontos transformados para XY do Blender;
- resumo do fit usado.

Fit `insufficient` é recusado por padrão.

## Etapa 5 — importar a sobreposição no Blender

```bash
blender cena_r29.blend --background \
  --python tools/blender/import_structural_reference.py \
  -- \
  --reference docs/reports/blender/structural_reference.json \
  --save-as cena_structure_ref.blend
```

O Blender cria a coleção:

```text
SOURCE_GEOREF | STRUCTURAL_REFERENCE
```

com subcamadas por tipo. Objetos `REF_*`:

- são referência somente;
- ficam ocultos no render;
- não substituem geometria existente;
- preservam índice de spline → OSM ID em `STRUCTURAL_REFERENCE_INDEX`.

Se a coleção já existir, o script falha. Para reconstruí-la conscientemente, usar `--replace-existing`.

## Ordem de correção estrutural

Após validar visualmente a sobreposição:

1. **coastline / waterfront** — conferir limite terra/água, cais, píeres e contenções;
2. **eixos viários** — posição e continuidade;
3. **cruzamentos** — conexão entre vias e áreas pedonais;
4. **relevo** — verificar se rua/escada/terreno se encontram corretamente;
5. **calçadas e escadas** — largura e conexão onde houver dado suficiente;
6. **footprints de edifícios** — posição/escala horizontal;
7. **Hero assets** — somente depois da base espacial estar coerente.

## Terreno

`terrain.tif` não deve ser tratado como verdade absoluta apenas por existir. Antes de usar:

- confirmar CRS;
- confirmar pixel size;
- confirmar bounds;
- conferir `nodata`;
- comparar visualmente transições críticas da escarpa;
- documentar qualquer correção local necessária.

Correções locais devem ser feitas em uma camada derivada ou revisão do terreno, nunca sobrescrevendo silenciosamente o DEM-fonte.

## Coastline e água

Separar sempre:

```text
coastline        = limite geográfico terra/água
waterfront       = cais, muretas, píeres, contenções
water_surface    = mesh/shader visual da água
```

A superfície visual da água pode ser artística. Coastline e waterfront devem permanecer estruturalmente rastreáveis.

## Critério para iniciar a R30 visual

A R30 visual só deve avançar fortemente quando:

- fit geográfico estiver revisado;
- referência estrutural estiver carregada;
- corredor Elevador → Praça Cairu → Mercado estiver coerente em planta;
- coastline/cais do recorte estiverem revisados;
- principais artefatos do terreno estiverem identificados;
- qualquer trecho ainda aproximado estiver explicitamente registrado.

## Anti-gambiarra

Não:

- usar offset manual para alinhar todo o mapa sem registrar transformação;
- engrossar rua para esconder erro de posição;
- mover prédio para encaixar em rua incorreta;
- editar o DEM-fonte para esconder degrau/artefato;
- assumir largura de via que o dado não fornece;
- transformar OSM em mesh final automaticamente.

A referência serve para revelar divergências, não para escondê-las.
