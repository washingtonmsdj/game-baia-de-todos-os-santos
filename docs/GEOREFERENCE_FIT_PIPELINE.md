# Fit geográfico OSM → Blender

## Objetivo

Recuperar de forma reproduzível a transformação entre o mundo real e a cena Blender do **Bay of All Saints**, evitando offsets manuais e correções "no olho".

A transformação é estimada entre:

- coordenadas de referência em **EPSG:3857** derivadas do `map.osm` original;
- coordenadas XY reais dos objetos OSM já presentes no `.blend`.

## Princípio de segurança

O solver é **somente de auditoria**.

Ele não:

- move objetos;
- altera o `.blend`;
- modifica `area.json`;
- marca `world_anchor_status=verified`;
- corrige ruas/coastline automaticamente.

Ele produz um relatório candidato que precisa ser revisado antes de virar fonte de verdade.

## Pré-requisitos

1. recuperar a captura Aleph original ou outro `map.osm` exatamente correspondente à cena;
2. preservar o arquivo original;
3. exportar as pistas da cena Blender:

```bash
blender cena.blend --background \
  --python tools/blender/extract_georef_hints.py \
  -- --output docs/reports/blender/georef_hints.json
```

O relatório contém OSM IDs, bounds e objetos associados.

## Executar o solver

```bash
python tools/georef/solve_osm_blender_fit.py \
  --hints docs/reports/blender/georef_hints.json \
  --osm CAMINHO/map.osm \
  --output docs/reports/blender/georef_fit.json
```

Por padrão, o solver tenta usar `way`s com tag `building`, pois footprints de edifícios tendem a fornecer anchors mais estáveis que vias longas/curvas.

Se houver poucos buildings detectados, ele amplia automaticamente para outros `way`s correspondentes. `--all-ways` permite começar diretamente nesse modo.

## Como o ponto de cada anchor é obtido

### OSM

Para cada `way`:

1. nós WGS84 são convertidos para EPSG:3857;
2. para polígonos válidos é calculado o centróide do footprint;
3. geometrias degeneradas usam média dos pontos.

### Blender

Para cada objeto que contém o mesmo OSM ID:

1. usa-se o centro do `bounds_world`;
2. se houver mais de um objeto para o mesmo OSM ID, usa-se a mediana dos centros;
3. cada OSM ID pesa apenas uma vez no fit.

Esse método é adequado para **recuperar/alcançar uma transformação candidata**, mas não substitui anchors explicitamente medidos para certificação final.

## Modelo matemático

O solver estima uma similaridade 2D:

```text
BlenderXY = escala × rotação(EPSG3857XY) + translação
```

Isso fornece:

- `scale_blender_units_per_meter`;
- `meters_per_blender_unit`;
- `rotation_epsg3857_to_blender_deg`;
- vetor do norte verdadeiro no Blender;
- origem `(0,0)` do Blender em EPSG:3857;
- origem correspondente em WGS84;
- residual de cada anchor;
- RMS, mediana e residual máximo.

## Outliers

Além do fit bruto, é calculado um `robust_fit`.

O robust fit remove iterativamente o pior anchor somente quando seu residual excede o limite configurado e enquanto a quantidade mínima de anchors puder ser preservada.

Padrões iniciais:

```text
min_anchors = 4
max_residual = 8 unidades Blender
target_rms = 3 unidades Blender
```

Esses números são gates de análise, **não tolerâncias definitivas de arte final**. Depois que `meters_per_blender_unit` for confirmado, os limites devem ser interpretados fisicamente em metros.

## Qualidade retornada

O relatório usa três estados de qualidade:

- `strong_candidate` — conjunto maior de anchors e RMS baixo;
- `candidate` — resultado suficiente para revisão manual detalhada;
- `insufficient` — não promover nem usar como base automática.

Mesmo `strong_candidate` continua com `status=candidate_only` até revisão.

## Validação obrigatória

Antes de alterar `world_anchor_status` para `verified`:

1. conferir visualmente pelo menos vários anchors distribuídos pela área;
2. verificar se Mercado Modelo e Palácio Rio Branco estão coerentes quando presentes;
3. verificar que outliers removidos têm explicação concreta (objeto derivado, ID ambíguo, geometria não correspondente etc.);
4. conferir escala em uma distância física conhecida;
5. conferir norte/rotação em pelo menos um eixo viário ou par de anchors distante;
6. registrar RMS e quantidade de anchors usados;
7. não esconder residual ruim com offset manual posterior.

## Promoção para `area.json`

Somente após validação, registrar de forma explícita:

```text
world_origin_wgs84
world_origin_epsg3857
world_origin_blender
rotation_true_north_deg
meters_per_blender_unit
fit_rms_error_m
anchors_used
```

Se o relatório ainda trabalha em unidades Blender e a escala não foi validada, não escrever `fit_rms_error_m` como se fosse metros.

## Relação com ruas, cais e coastline

Depois do anchor ser verificado:

1. importar/gerar referência geográfica usando a transformação registrada;
2. comparar eixos de ruas existentes contra OSM;
3. comparar coastline/borda d'água;
4. separar coastline real de waterfront construído e do shader da água;
5. corrigir a geometria autoral com revisão dedicada;
6. nunca deslocar a base geográfica para encaixar um asset modelado incorretamente.

## Teste matemático

`tests/test_georef_fit.py` valida a matemática com uma transformação sintética conhecida e também testa rejeição de outlier.

O CI executa esses testes em todo PR que altera `tools/` ou `tests/`.
