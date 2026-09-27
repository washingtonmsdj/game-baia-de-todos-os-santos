# Suporte a Multipolygons OSM — Fidelidade Estrutural

## Por que isso existe

No OpenStreetMap, edifícios, áreas d'água, cais e outras geometrias podem ser representados por uma única `way` fechada **ou** por uma relação `type=multipolygon` composta por várias ways.

Ignorar relações multipolygon pode fazer o pipeline estrutural perder footprints inteiros ou interpretar um conjunto de segmentos como geometria incompleta.

## Comportamento do extrator v2

`tools/world/extract_osm_structure.py` agora:

- carrega todas as ways necessárias para resolver relações;
- identifica relações `type=multipolygon`;
- classifica a relação pelos próprios tags estruturais;
- monta anéis somente quando os endpoints compartilham o mesmo node OSM;
- nunca fecha gaps por proximidade espacial;
- emite cada anel externo válido como uma feature com:
  - `osm_type=relation`;
  - `osm_id` da relação;
  - `relation_part_index`;
  - `member_way_ids`;
  - `relation_hole_count`;
- registra relações incompletas em `relation_diagnostics`.

O schema de estrutura passa a ser:

```text
bay-of-all-saints/osm-structure-v2
```

## Anéis internos / holes

Anéis internos são detectados e contados, mas não são transformados automaticamente em preenchimento Blender.

Isso é intencional: uma área com pátio, ilha ou vazio interno não pode ser convertida cegamente em uma superfície cheia.

`relation_hole_count > 0` deve ser tratado como sinal de revisão quando a geometria final depender de preenchimento.

## QA topológico

`tools/world/audit_osm_topology.py` aceita v1 e v2 e passa a registrar:

- relações com member ways ausentes;
- outer chains incompletas;
- inner chains incompletas;
- identidade tipada `osm_type + osm_id + relation_part_index`.

Esses casos entram na `review_queue` como `incomplete_multipolygon_relation` quando aplicável.

## Blender

`build_blender_structure_reference.py` preserva metadados da relação e gera `blender-structure-reference-v2`.

`import_structural_reference.py` aceita v1/v2 e registra no datablock `STRUCTURAL_REFERENCE_INDEX`:

- `osm_type`;
- `osm_id`;
- `relation_part_index`;
- `member_way_ids`;
- `relation_hole_count`.

Assim duas partes da mesma relação não se tornam indistinguíveis durante a auditoria.

## Regra anti-gambiarra

Não:

- juntar ways pela distância quando não compartilham node OSM;
- fechar relação incompleta manualmente no extrator;
- preencher holes automaticamente;
- transformar a relação OSM diretamente em asset final.

A relação continua sendo **referência estrutural**. A geometria autoral do jogo é corrigida em revisão separada.
