# QA de Alinhamento Cena ↔ Referência — Bay of All Saints

## Objetivo

Medir divergências entre entidades OSM já presentes na cena Blender e a referência estrutural transformada para o mesmo sistema XY.

Esse QA responde a uma pergunta diferente dos outros gates:

- `osm_topology_audit.json`: a fonte OSM está estruturalmente coerente?
- `georef_fit.json`: OSM e Blender compartilham uma transformação plausível?
- `scene_reference_alignment.json`: objetos da cena com o **mesmo OSM ID** estão no mesmo lugar da referência?

Nenhum desses relatórios move geometria automaticamente.

## Pré-requisito

Gerar novamente a auditoria da cena com a versão atual:

```bash
blender CENA.blend --background \
  --python tools/blender/audit_structural_scene.py \
  -- --output docs/reports/blender/structural_scene_audit_before.json
```

A auditoria v2 extrai OSM IDs apenas quando há identificação explícita em nome/custom property. Sufixos Blender como `.001` não são tratados como OSM ID.

Objetos `SOURCE_GEOREF` são excluídos para evitar comparar a referência com ela mesma.

## Uso

```bash
python tools/world/compare_scene_reference_alignment.py \
  --scene-audit docs/reports/blender/structural_scene_audit_before.json \
  --reference artifacts/structural-pipeline/mvp-centro-lacerda/structural_reference.json \
  --output docs/reports/blender/scene_reference_alignment.json
```

Thresholds padrão:

```text
center offset review = 3 m
bounds size delta review = 25%
```

São valores de triagem, não tolerâncias cadastrais.

## Como funciona

Para cada OSM ID presente nos dois lados:

1. agrega os bounds XY dos objetos Blender associados ao ID;
2. calcula bounds XY da feature estrutural OSM já transformada;
3. compara os centros;
4. converte o offset para metros usando `meters_per_blender_unit` do fit;
5. calcula diferença relativa dos tamanhos dos bounds;
6. gera flags de revisão.

## Flags

### `center_offset_review`

O centro da entidade Blender está além do threshold de deslocamento.

É a flag mais útil quando a entidade representa o mesmo objeto completo, por exemplo um building way claramente identificado.

### `bounds_size_review`

O tamanho do AABB XY diverge acima do threshold.

É apenas uma triagem. Bounds podem mudar por:

- rotação;
- extrusão;
- objetos divididos em várias partes;
- detalhes além do footprint;
- organização histórica do asset.

Nunca redimensionar automaticamente por essa flag.

## Entidades prioritárias

Quando os IDs existirem dos dois lados, começar por anchors conhecidos:

- Mercado Modelo — way `59392558`;
- Palácio Rio Branco — way `402383814`.

Depois revisar outros buildings/ways com identificação explícita distribuídos pelo recorte.

## O que fazer com um offset

Antes de mover o objeto:

1. confirmar que o OSM ID identifica a mesma entidade;
2. confirmar que o fit não está sendo distorcido por anchors ruins;
3. conferir `osm_topology_audit.json`;
4. verificar se a cena possui múltiplos objetos compondo a entidade;
5. avaliar se o erro pertence à geometria histórica, à referência, ao fit ou à interpretação dos bounds;
6. registrar a decisão.

Classificação recomendada:

```text
scene_alignment_issue
reference_interpretation_issue
fit_issue
asset_split_or_bounds_issue
source_uncertain
no_action
```

## Limitação

Este comparador não faz Hausdorff/ICP nem equivalência topológica de malhas. Ele é deliberadamente conservador: usa OSM ID, centro e bounds para descobrir **onde investigar**.

Uma análise geométrica mais fina só deve ser implementada quando existirem bindings confiáveis entre feature real e geometria final, para evitar corrigir o mapa com correspondências falsas.
