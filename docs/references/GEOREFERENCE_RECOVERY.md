# Recuperação de Georreferenciamento do MVP

## Status

Este documento registra pistas recuperadas diretamente do `.blend` analisado. Elas ajudam a reconstruir a relação entre a cena local e os dados geográficos originais, mas **ainda não constituem uma origem geográfica certificada**.

## Captura Aleph original — pista recuperada

O `.blend` contém uma referência explícita a:

```text
data/aleph/aleph-20260924T205631Z-aqqo7pkx/map.osm
```

Portanto, o identificador provável da captura original é:

```text
aleph-20260924T205631Z-aqqo7pkx
```

A prioridade é procurar essa pasta na estação de trabalho onde o MVP foi construído. Se existir, preservar especialmente:

- `manifest.json`;
- `map.osm`;
- `terrain.tif`;
- `terrain/tiles/`;
- quaisquer GeoJSONs/metadados associados.

Não considerar a captura recuperada apenas pelo nome da pasta; o `manifest.json` deve ser validado com `tools/aleph/inspect_capture.py`.

## Metadados de terreno recuperados

A cena registra, em propriedades internas, a origem histórica do terreno como:

```text
Aleph DEM EPSG:3857 + OSM (praça, escarpa, ladeira, caminhos do Elevador)
```

Também registra que o DEM trabalha em metros e que houve compatibilização local de cotas para o MVP, incluindo aproximadamente:

- praça superior: 70 m;
- saída baixa: 11 m;
- Mercado Modelo: 10,9 m.

Isso confirma que o terreno atual não deve ser tratado como levantamento final: parte das cotas foi conciliada manualmente para o recorte jogável.

## Anchors OSM já presentes na cena

A cena contém vários IDs OSM embutidos em nomes/propriedades. Dois exemplos importantes:

### Palácio Rio Branco

```text
OSM way: 402383814
objeto: RIO BRANCO | corpo footprint 402383814
bounds Blender aproximados:
  min = (-30.819, -79.257, 70.0)
  max = (16.131, -24.761, 80.8)
centro do bounding box XY ≈ (-7.344, -52.009)
```

### Mercado Modelo

```text
OSM way: 59392558
objeto: MERCADO MODELO | footprint OSM
bounds Blender aproximados:
  min = (-150.43, 138.57, 11.0)
  max = (-80.38, 209.65, 28.0)
centro do bounding box XY ≈ (-115.405, 174.11)
```

Esses IDs devem ser cruzados com a geometria exata do `map.osm` original, não apenas com coordenadas aproximadas de serviços externos.

## Hipótese técnica inicial

Uma comparação preliminar entre os dois anchors acima e posições públicas aproximadas dos mesmos objetos indica:

- orientação XY da cena muito próxima dos eixos Web Mercator;
- rotação aparente próxima de zero;
- escala próxima de 1 metro por unidade Blender;
- offset local consistente com coordenadas EPSG:3857 transladadas.

Entretanto, bounding-box centers não são centroides OSM exatos. Pequenas diferenças de footprint produzem erro de vários metros. Portanto:

**não registrar ainda `world_origin_*` nem `rotation_true_north` como valores definitivos.**

## Método correto para fechar a transformação

Quando o `map.osm` original estiver disponível:

1. extrair pelo menos 3–5 ways/anchors presentes tanto no OSM quanto na cena;
2. calcular um ponto representativo idêntico em ambos os lados (preferencialmente os mesmos vértices/centro geométrico, não bounding-box de uma fonte e centroid de outra);
3. converter WGS84 → EPSG:3857;
4. ajustar uma transformação 2D por mínimos quadrados contendo:
   - translação;
   - rotação;
   - escala;
5. verificar os resíduos por anchor;
6. rejeitar a transformação se houver erro incompatível com a precisão esperada;
7. somente então registrar:

```text
world_origin_wgs84
world_origin_epsg3857
world_origin_blender
rotation_true_north
meters_per_blender_unit
fit_rms_error_m
anchors_used
```

## Automação preparada

Executar no Blender:

```bash
blender cena.blend --background \
  --python tools/blender/extract_georef_hints.py \
  -- --output docs/reports/blender/georef_hints.json
```

O script coleta:

- propriedades com referências a Aleph/OSM/EPSG/DEM/terrain;
- caminhos de origem encontrados;
- IDs OSM detectados;
- bounds em coordenadas world do Blender;
- configurações de unidade da cena.

Ele é somente leitura e não altera a geometria.

## Regra para o bridge futuro

O bridge Aleph/OSM → Blender só deve ser ativado automaticamente depois que a transformação estiver validada por múltiplos anchors. Até lá, capturas novas podem ser catalogadas, mas não devem ser mescladas na cena principal por um offset inferido.
