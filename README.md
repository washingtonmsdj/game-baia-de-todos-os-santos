# Bay of All Saints — Salvador em Mundo Aberto

> **Nome do jogo:** Bay of All Saints  
> **Tagline:** *Todos têm um preço. Ninguém é santo.*

Jogo de ação em mundo aberto ambientado em Salvador, Bahia, Brasil.

O MVP atual está concentrado na região do **Elevador Lacerda / Cidade Alta / Cidade Baixa / Praça Cairu / Mercado Modelo**. O objetivo de longo prazo é expandir o mundo jogável para Salvador inteira, preservando a geografia vertical da cidade, sua identidade cultural, contrastes urbanos, marcos arquitetônicos, bairros, trânsito e vida cotidiana.

## Foco atual do desenvolvimento

A prioridade atual é **fidelidade estrutural**, antes de acabamento visual:

1. georreferenciamento;
2. terreno/relevo;
3. coastline, cais e waterfront;
4. ruas, cruzamentos e áreas pedonais;
5. escadarias, contenções e calçadas;
6. footprints e implantação dos edifícios;
7. somente depois, detalhe visual fino.

A cena-fonte do Blender já contém terreno, geometria de referência derivada de OSM, vias, marcos arquitetônicos, sistema do Elevador Lacerda, Mercado Modelo, Praça Cairu, áreas de circulação jogáveis e várias revisões internas.

O trabalho no Blender é continuado por meio de **passes Python versionados e não destrutivos** armazenados neste repositório. ChatGPT/Codex prepara melhorias no GitHub e o Codex local aplica/valida no `.blend`.

## Fidelidade de Salvador

A meta é reproduzir a cidade com alta fidelidade, priorizando a estrutura que define Salvador:

- ruas, cruzamentos, calçadas, ladeiras e escadarias;
- relevo e relação Cidade Alta/Cidade Baixa;
- coastline, cais e limite terra/água;
- posição e footprint dos marcos reais;
- relação espacial entre edifícios, praças, vias e Baía de Todos-os-Santos.

A referência visual existe como apoio, mas **não substitui a base geográfica**.

Consulte primeiro:

- [`docs/STRUCTURAL_FIDELITY_PIPELINE.md`](docs/STRUCTURAL_FIDELITY_PIPELINE.md);
- [`docs/GEOREFERENCE_FIT_PIPELINE.md`](docs/GEOREFERENCE_FIT_PIPELINE.md);
- [`docs/WORLD_DATA_ACQUISITION.md`](docs/WORLD_DATA_ACQUISITION.md);
- [`docs/revisions/R30A_STRUCTURE_PLAN.md`](docs/revisions/R30A_STRUCTURE_PLAN.md).

## Estrutura do repositório

```text
AGENTS.md

docs/
  PROJECT_VISION.md
  BLENDER_WORKFLOW.md
  CODEX_HANDOFF.md
  DATA_PROVENANCE.md
  STRUCTURAL_FIDELITY_PIPELINE.md
  GEOREFERENCE_FIT_PIPELINE.md
  WORLD_DATA_ACQUISITION.md
  REFERENCE_PRODUCTION_PIPELINE.md
  references/
  reports/
  revisions/
    R27.md
    R28.md
    R29.md
    R30A_STRUCTURE_PLAN.md
    R30_PLAN.md

world/
  areas/
    mvp-centro-lacerda/

tools/
  aleph/
    inspect_capture.py
    capture_area.py
  georef/
    solve_osm_blender_fit.py
  terrain/
    audit_dem.py
  world/
    extract_osm_structure.py
    build_blender_structure_reference.py
  blender/
    extract_georef_hints.py
    import_structural_reference.py
    audit_structural_scene.py
    r27_qa_review.py
    r28_gameplay_export.py
    r29_optimization.py
  references/
    validate_registry.py
    register_media.py
    reference_gaps.py
    import_commons.py
    build_gallery.py
```

## Dados geográficos e Aleph

O projeto utiliza **Aleph** como ferramenta externa de aquisição/proveniência geográfica, com a revisão atualmente analisada pinada em:

`Belluxx/Aleph@d24c61507481a91a0dd6afac4f97626a4e5ea780`

A análise do `.blend` recuperou uma pista da captura Aleph original do MVP:

```text
data/aleph/aleph-20260924T205631Z-aqqo7pkx/map.osm
```

Na estação de origem, procurar prioritariamente por:

```text
aleph-20260924T205631Z-aqqo7pkx/
  manifest.json
  map.osm
  terrain.tif
```

Para auditar uma captura:

```bash
python tools/aleph/inspect_capture.py CAMINHO_DA_CAPTURA \
  --output docs/reports/aleph/AREA_ID/source_summary.json
```

Para auditar o terreno:

```bash
python tools/terrain/audit_dem.py \
  --dem CAMINHO_DA_CAPTURA/terrain.tif \
  --output docs/reports/aleph/AREA_ID/dem_audit.json
```

Para extrair a estrutura do OSM:

```bash
python tools/world/extract_osm_structure.py \
  --osm CAMINHO_DA_CAPTURA/map.osm \
  --output artifacts/world/AREA_ID/osm_structure.json
```

Para extrair pistas geográficas do Blender:

```bash
blender cena.blend --background \
  --python tools/blender/extract_georef_hints.py \
  -- --output docs/reports/blender/georef_hints.json
```

Depois o fit OSM → Blender é calculado por `tools/georef/solve_osm_blender_fit.py` e a sobreposição estrutural é gerada/importada conforme `docs/STRUCTURAL_FIDELITY_PIPELINE.md`.

## Referência estrutural no Blender

A sobreposição importada fica em:

```text
SOURCE_GEOREF | STRUCTURAL_REFERENCE
```

Ela pode conter:

```text
REF_ROADS
REF_PEDESTRIAN
REF_STEPS
REF_BUILDINGS
REF_COASTLINE
REF_WATERFRONT
REF_RETAINING_WALLS
REF_WATER
REF_RAILWAYS
```

Esses objetos são **somente referência**, ocultos no render e rastreáveis por OSM ID em `STRUCTURAL_REFERENCE_INDEX`.

A cena existente pode ser auditada com:

```bash
blender cena.blend --background \
  --python tools/blender/audit_structural_scene.py \
  -- --output docs/reports/blender/structural_scene_audit.json
```

## Referências visuais

Referências visuais permanecem disponíveis para detalhe arquitetônico quando necessário, mas não são a prioridade desta etapa.

```bash
python tools/references/validate_registry.py --root .
python tools/references/reference_gaps.py --area mvp-centro-lacerda
```

O acervo binário local fica fora do Git; o catálogo leve permanece em `world/areas/`.

## Política de revisões do Blender

Cada automação do Blender deve:

- ser não destrutiva por padrão;
- preservar o `.blend` anterior;
- salvar em um novo arquivo de revisão;
- evitar renomeações/junções destrutivas sem justificativa;
- registrar o que foi alterado;
- manter dados-fonte, referência/proxy e geometria final separados;
- fornecer metadados suficientes para validação posterior.

## Marco atual

**Vertical slice do MVP:** Elevador Lacerda e entorno jogável imediato.

Estado atual do pipeline:

- **R27** — marcadores de QA, câmera de revisão e iluminação opcional de preview;
- **R28** — rota jogável, zonas, classificação de exportação e auditoria de performance;
- **R29** — auditoria/deduplicação conservadora de meshes e candidatos de LOD/colisão/chunks;
- **R30A** — próximo passe obrigatório: alinhamento estrutural de terreno, ruas, coastline/cais e footprints;
- **R30B/R30 visual** — somente depois da R30A: composição, mobiliário, vegetação, materiais e iluminação de apresentação.

A R29 possui dois modos: auditoria por padrão e aplicação exata somente com `--apply-exact`. Objetos `HERO` e `GAMEPLAY` ficam fora da deduplicação automática.

## Idioma

O nome do jogo permanece em inglês: **Bay of All Saints**.

Documentação, relatórios, handoffs e notas de desenvolvimento são mantidos em **português**.
