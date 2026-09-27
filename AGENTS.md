# AGENTS.md — Bay of All Saints

Estas instruções se aplicam a todo o repositório.

## Idioma

- Nome do jogo: **Bay of All Saints**.
- Documentação, relatórios, commits de projeto e handoffs: português.
- Identificadores de código existentes podem permanecer em inglês ou manter nomes históricos por compatibilidade.

## Prioridade atual

A prioridade de produção é **fidelidade estrutural de Salvador**, nesta ordem:

1. georreferenciamento;
2. terreno/relevo;
3. coastline, cais e waterfront;
4. ruas, cruzamentos e áreas pedonais;
5. escadarias, contenções e calçadas;
6. footprints e implantação dos edifícios;
7. Hero assets e detalhe visual;
8. referências fotográficas apenas quando realmente necessárias para detalhe arquitetônico.

Não atrasar correções estruturais para procurar imagens de fachada.

## Antes de alterar o Blender

Leia, nesta ordem:

1. `docs/CODEX_HANDOFF.md`;
2. `docs/BLENDER_WORKFLOW.md`;
3. `docs/STRUCTURAL_FIDELITY_PIPELINE.md`;
4. `docs/CODEX_STRUCTURE_HANDOFF.md`;
5. `docs/GEOREFERENCE_FIT_PIPELINE.md`;
6. `docs/OSM_TOPOLOGY_QA.md`;
7. `docs/TERRAIN_ROAD_QA.md`;
8. `docs/SCENE_REFERENCE_ALIGNMENT_QA.md`;
9. `docs/WORLD_DATA_ACQUISITION.md`;
10. `docs/DATA_PROVENANCE.md`;
11. `docs/REFERENCE_PRODUCTION_PIPELINE.md` quando o trabalho realmente depender de imagem;
12. `world/areas/mvp-centro-lacerda/README.md` quando trabalhar no MVP atual.

## Fonte de verdade

- Scripts e documentação versionados no GitHub são a fonte de verdade do pipeline.
- `.blend` é binário de trabalho e deve ser preservado por revisão; não sobrescrever a origem por padrão.
- OSM IDs e a transformação geográfica registrada são a referência estrutural do mundo real.
- IDs de locais de produção são os `location_id` em `world/areas/*/locations.json`.
- Objetos vinculados a locais devem usar a custom property `boas_location_id` quando o binding for implementado/validado.
- Dados-fonte, referências/proxies e geometria final devem permanecer semanticamente separados.

## Fidelidade da cidade

O projeto busca alta fidelidade de Salvador, especialmente em:

- ruas e cruzamentos;
- calçadas, ladeiras e escadarias;
- relevo Cidade Alta/Cidade Baixa;
- coastline, cais e limite terra/água;
- posição e footprint dos edifícios;
- relação espacial entre marcos reais.

Não deslocar geografia para acomodar um modelo sem registrar e justificar a correção.

## Pipeline estrutural obrigatório

Quando `map.osm`, `terrain.tif` e o `.blend` estiverem disponíveis localmente, preferir:

```bash
python tools/world/run_structural_pipeline.py \
  --osm CAMINHO/map.osm \
  --dem CAMINHO/terrain.tif \
  --hints docs/reports/blender/georef_hints.json \
  --audit-road-profiles \
  --output-dir artifacts/structural-pipeline/mvp-centro-lacerda
```

O pipeline gera estrutura OSM, QA topológico, auditoria do DEM, QA opcional das vias, fit e referência estrutural Blender.

Antes de corrigir a cena, revisar `osm_topology_audit.json` e `georef_fit.json`.

Depois de importar `SOURCE_GEOREF | STRUCTURAL_REFERENCE`, gerar novamente `structural_scene_audit_before.json` com a versão atual de `audit_structural_scene.py` e executar:

```bash
python tools/world/compare_scene_reference_alignment.py \
  --scene-audit docs/reports/blender/structural_scene_audit_before.json \
  --reference artifacts/structural-pipeline/mvp-centro-lacerda/structural_reference.json \
  --output docs/reports/blender/scene_reference_alignment.json
```

Só investigar automaticamente entidades com OSM ID explícito nos dois lados. Nunca criar correspondência de entidade por semelhança de nome.

A coleção `SOURCE_GEOREF | STRUCTURAL_REFERENCE` é somente referência. Nunca convertê-la silenciosamente em arte final.

## Referências visuais

Referências visuais são secundárias nesta fase. Quando forem necessárias:

```bash
python tools/references/validate_registry.py --root .
python tools/references/reference_gaps.py --area mvp-centro-lacerda
python tools/references/build_gallery.py --area mvp-centro-lacerda --media-root world-reference
```

Use apenas referências catalogadas em `media-manifest.json` e respeite `usage_class`/proveniência.

Regras obrigatórias:

- não inventar imagem ausente;
- não tratar imagem sem licença/origem como referência aprovada;
- não promover Hero asset para `approved` sem as vistas mínimas definidas;
- não versionar o acervo visual/geográfico pesado no Git comum;
- usar `coverage` para uma mesma mídia que documenta vários locais, sem duplicar o binário.

## Aleph e geografia

Aleph é ferramenta externa de aquisição/proveniência, atualmente pinada em:

`Belluxx/Aleph@d24c61507481a91a0dd6afac4f97626a4e5ea780`

A pista da captura histórica do MVP é:

`aleph-20260924T205631Z-aqqo7pkx`

Não implementar merge automático de novas áreas até a transformação mundo real → Blender estar verificada por múltiplos anchors e registrada com erro residual.

## Revisões Blender

- preservar arquivo anterior;
- salvar nova revisão;
- evitar operações destrutivas ocultas;
- validar reabertura;
- gerar relatórios;
- manter `HERO`, `GAMEPLAY`, `SOURCE_GEOREF`, referência geográfica e geometria final semanticamente separadas;
- corrigir estrutura antes de decoração.

## Validação antes de commit/PR

Executar no mínimo:

```bash
python -m compileall -q tools tests
python -m unittest discover -s tests -p "test_*.py" -v
python tools/references/validate_registry.py --root .
```

Se uma captura Aleph foi usada, gerar/atualizar seu `source_summary.json` e, quando existir `terrain.tif`, o `dem_audit.json`.

Se uma revisão Blender foi aplicada, exportar os relatórios da cena antes de declarar a revisão concluída.

## Regra anti-gambiarra

Não resolver problema estrutural por:

- offset manual sem metadado;
- renomeação em massa;
- duplicação de geometria sem necessidade;
- path absoluto versionado;
- número aproximado apresentado como medido;
- largura de rua inventada quando a fonte não fornece;
- edição silenciosa do DEM-fonte;
- substituição silenciosa de fonte de dados;
- uso de decoração para esconder desalinhamento estrutural;
- correspondência automática entre asset e feature real sem ID/proveniência confiável.

Quando uma informação ainda não foi verificada, mantê-la explicitamente como `null`, `candidate`, `partial` ou `pending` conforme o contrato correspondente.
