# Bay of All Saints — Salvador em Mundo Aberto

> **Nome do jogo:** Bay of All Saints  
> **Tagline:** *Todos têm um preço. Ninguém é santo.*

Jogo de ação em mundo aberto ambientado em Salvador, Bahia, Brasil.

O MVP atual está concentrado na região do **Elevador Lacerda / Cidade Alta / Cidade Baixa / Praça Cairu / Mercado Modelo**. O objetivo de longo prazo é expandir o mundo jogável para Salvador inteira, preservando a geografia vertical da cidade, sua identidade cultural, contrastes urbanos, marcos arquitetônicos, bairros, trânsito e vida cotidiana.

## Foco atual do desenvolvimento

O projeto está construindo o primeiro recorte urbano jogável ao redor do Elevador Lacerda.

A cena-fonte do Blender já contém terreno, geometria de referência derivada de OSM, vias, marcos arquitetônicos, sistema do Elevador Lacerda, Mercado Modelo, Praça Cairu, áreas de circulação jogáveis e várias revisões internas.

O trabalho no Blender é continuado por meio de **passes Python versionados e não destrutivos** armazenados neste repositório. Assim, ChatGPT/Codex pode preparar melhorias no GitHub e aplicá-las depois dentro do Blender sem interromper repetidamente o fluxo de construção do mapa.

## Fidelidade de Salvador

A meta é reproduzir a cidade com alta fidelidade, priorizando primeiro a estrutura que define Salvador:

- ruas, cruzamentos, calçadas, ladeiras e escadarias;
- relevo e relação Cidade Alta/Cidade Baixa;
- coastline, cais e limite terra/água;
- posição, escala e silhueta dos marcos reais;
- relação espacial entre edifícios, praças, vias e Baía de Todos-os-Santos.

O projeto possui um pipeline formal de referências. Cada prédio/local recebe um `location_id`, classe de fidelidade, estado de modelagem e conjunto mínimo de vistas. Imagens reais ficam fora do Git pesado, mas sua origem, licença, hash SHA-256 e caminho lógico são registrados em manifests versionados.

Consulte:

- [`docs/REFERENCE_PRODUCTION_PIPELINE.md`](docs/REFERENCE_PRODUCTION_PIPELINE.md);
- [`docs/CODEX_REFERENCE_HANDOFF.md`](docs/CODEX_REFERENCE_HANDOFF.md);
- [`world/areas/mvp-centro-lacerda/README.md`](world/areas/mvp-centro-lacerda/README.md).

## Estrutura do repositório

```text
AGENTS.md

docs/
  PROJECT_VISION.md
  BLENDER_WORKFLOW.md
  CODEX_HANDOFF.md
  CODEX_REFERENCE_HANDOFF.md
  DATA_PROVENANCE.md
  REFERENCE_PRODUCTION_PIPELINE.md
  WORLD_DATA_ACQUISITION.md
  references/
    ALEPH.md
    GEOREFERENCE_RECOVERY.md
    SOURCE_REGISTRY.json
  reports/
  revisions/
    R27.md
    R28.md
    R29.md
    R30_PLAN.md

schemas/
  area-reference.schema.json
  location-reference.schema.json
  media-manifest.schema.json

world/
  areas/
    mvp-centro-lacerda/
      README.md
      area.json
      locations.json
      media-manifest.json

tools/
  aleph/
    inspect_capture.py
    capture_area.py
  blender/
    r27_qa_review.py
    r28_gameplay_export.py
    r29_optimization.py
    export_revision_reports.py
    extract_georef_hints.py
  references/
    validate_registry.py
    register_media.py
    reference_gaps.py
```

## Dados geográficos e Aleph

O projeto utiliza **Aleph** como ferramenta externa de aquisição/proveniência geográfica, com a revisão atualmente analisada pinada em:

`Belluxx/Aleph@d24c61507481a91a0dd6afac4f97626a4e5ea780`

O software Aleph é MIT, mas os dados obtidos por ele mantêm as licenças/termos de suas fontes originais.

A análise do `.blend` recuperou uma pista da captura Aleph original do MVP:

```text
data/aleph/aleph-20260924T205631Z-aqqo7pkx/map.osm
```

Essa pista está registrada para recuperação futura; ela não substitui a validação do `manifest.json` original.

Política atual:

- OpenStreetMap/Geofabrik: uso no pipeline com atribuição e obrigações ODbL;
- terreno do Aleph: referência/MVP até confirmar a origem/licença efetiva do DEM usado;
- Google Satellite obtido pelo Aleph: não usar como asset de produção;
- Google Street View obtido pelo Aleph: não usar como asset/fonte derivativa automática de produção.

Para uma captura já existente:

```bash
python tools/aleph/inspect_capture.py CAMINHO_DA_CAPTURA \
  --output docs/reports/aleph/AREA_ID/source_summary.json
```

Para criar uma nova captura territorial padronizada, limitada intencionalmente a `osm` + terreno:

```bash
python tools/aleph/capture_area.py \
  --area-id centro-historico \
  --bbox SOUTH WEST NORTH EAST
```

Para extrair pistas geográficas diretamente de uma cena Blender:

```bash
blender cena.blend --background \
  --python tools/blender/extract_georef_hints.py \
  -- --output docs/reports/blender/georef_hints.json
```

Consulte [`docs/references/ALEPH.md`](docs/references/ALEPH.md), [`docs/references/GEOREFERENCE_RECOVERY.md`](docs/references/GEOREFERENCE_RECOVERY.md), [`docs/DATA_PROVENANCE.md`](docs/DATA_PROVENANCE.md) e [`docs/WORLD_DATA_ACQUISITION.md`](docs/WORLD_DATA_ACQUISITION.md).

## Referências visuais

Validar o catálogo:

```bash
python tools/references/validate_registry.py --root .
```

Ver o que ainda falta para cada local:

```bash
python tools/references/reference_gaps.py --area mvp-centro-lacerda
```

Registrar uma foto real sem colocá-la no Git:

```bash
python tools/references/register_media.py --help
```

O acervo binário local deve ficar em `world-reference/` (ignorado pelo Git), enquanto o catálogo leve permanece em `world/areas/`.

## Política de revisões do Blender

Cada automação do Blender deve:

- ser não destrutiva por padrão;
- preservar o `.blend` anterior;
- salvar em um novo arquivo de revisão;
- poder ser executada novamente com segurança quando possível;
- evitar renomeações em massa ou junções destrutivas sem aprovação explícita;
- registrar o que foi alterado;
- manter geometria de referência/proxy separada da geometria destinada ao jogo;
- fornecer metadados suficientes para o Codex validar o resultado posteriormente.

## Marco atual

**Vertical slice do MVP:** Elevador Lacerda e entorno jogável imediato.

Estado atual do pipeline:

- **R27** — marcadores de QA, câmera de revisão e iluminação opcional de preview;
- **R28** — guias de rota jogável, zonas de gameplay, classificação de exportação e auditoria de performance;
- **R29** — auditoria e deduplicação conservadora de meshes comprovadamente idênticas, além de candidatos de LOD, colisão e chunks;
- **R30** — próximo passe: evolução visual perceptível do recorte jogável, guiada pelas métricas reais da R29 e pelo catálogo de referências.

A R29 possui dois modos: auditoria por padrão e aplicação exata somente com `--apply-exact`. Objetos `HERO` e `GAMEPLAY` ficam fora da deduplicação automática.

Consulte [`docs/BLENDER_WORKFLOW.md`](docs/BLENDER_WORKFLOW.md), [`docs/CODEX_HANDOFF.md`](docs/CODEX_HANDOFF.md), [`docs/revisions/R29.md`](docs/revisions/R29.md) e [`docs/revisions/R30_PLAN.md`](docs/revisions/R30_PLAN.md).

## Idioma

O nome do jogo permanece em inglês: **Bay of All Saints**.

Documentação, relatórios, handoffs e notas de desenvolvimento são mantidos em **português**.
