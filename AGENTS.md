# AGENTS.md — Bay of All Saints

Estas instruções se aplicam a todo o repositório.

## Idioma

- Nome do jogo: **Bay of All Saints**.
- Documentação, relatórios, commits de projeto e handoffs: português.
- Identificadores de código existentes podem permanecer em inglês ou manter nomes históricos por compatibilidade.

## Prioridade atual

A prioridade de produção é **fidelidade estrutural de Salvador orientada à jogabilidade**, nesta ordem:

1. georreferenciamento XY;
2. coerência vertical DEM ↔ Blender;
3. terreno/relevo;
4. coastline, cais e waterfront;
5. ruas, cruzamentos e áreas pedonais;
6. escadarias, contenções e calçadas;
7. footprints e implantação dos edifícios;
8. superfícies funcionais para jogador, carros e NPCs;
9. Hero assets e detalhe visual;
10. referências fotográficas apenas quando realmente necessárias para detalhe arquitetônico.

Não atrasar correções estruturais para procurar imagens de fachada.

**Fidelidade não significa réplica milimétrica.** O mundo real é referência; a geometria final deve ser uma Salvador reconhecível, coerente e jogável. Nunca corrigir uma divergência apenas para reduzir RMS/offset se a mudança não melhorar identidade, continuidade espacial ou gameplay.

## Antes de alterar o Blender

Leia, nesta ordem:

1. `docs/PROJECT_STATUS.md`;
2. `docs/PROJECT_VISION.md`;
3. `docs/GAMEPLAY_FIDELITY_POLICY.md`;
4. `docs/BLENDER_WORKFLOW.md`;
5. `docs/BLENDMCP_FALLBACK.md`;
6. `docs/CODEX_HANDOFF.md`;
7. `docs/STRUCTURAL_FIDELITY_PIPELINE.md`;
8. `docs/CODEX_STRUCTURE_HANDOFF.md`;
9. `docs/GEOREFERENCE_FIT_PIPELINE.md`;
10. `docs/DEM_BLENDER_VERTICAL_FIT.md`;
11. `docs/OSM_TOPOLOGY_QA.md`;
12. `docs/TERRAIN_ROAD_QA.md`;
13. `docs/SCENE_REFERENCE_ALIGNMENT_QA.md`;
14. `docs/WORLD_DATA_ACQUISITION.md`;
15. `docs/DATA_PROVENANCE.md`;
16. `docs/REFERENCE_PRODUCTION_PIPELINE.md` quando o trabalho realmente depender de imagem;
17. `world/areas/mvp-centro-lacerda/README.md` quando trabalhar no MVP atual.

## Fonte de verdade

- Scripts e documentação versionados no GitHub são a fonte de verdade do pipeline e das decisões do projeto.
- Mudanças relevantes de direção, critérios de aceitação, arquitetura ou fluxo devem atualizar docs/handoffs no mesmo ciclo de trabalho.
- O projeto não deve depender de contexto de conversa para preservar decisões importantes.
- `.blend` de revisão oficial sob `blender/` pode ser versionado via Git LFS conforme a política atual; preservar revisões e não sobrescrever uma base validada sem motivo.
- OSM IDs e a transformação geográfica registrada são a referência estrutural do mundo real, não necessariamente a geometria final jogável.
- IDs de locais de produção são os `location_id` em `world/areas/*/locations.json`.
- Objetos vinculados a locais devem usar a custom property `boas_location_id` quando o binding for implementado/validado.
- Dados-fonte, referências/proxies, geometria visual final e camadas de gameplay devem permanecer semanticamente separados.

## Fidelidade da cidade

O projeto busca alta fidelidade de Salvador, especialmente em:

- ruas e cruzamentos;
- calçadas, ladeiras e escadarias;
- relevo Cidade Alta/Cidade Baixa;
- coastline, cais e limite terra/água;
- posição e footprint dos edifícios;
- relação espacial entre marcos reais.

Não deslocar geografia para acomodar um modelo sem registrar e justificar a correção.

Ao detectar uma divergência, classificar antes de agir:

- `KEEP_REAL_REFERENCE` — referência confirmada; manter como controle;
- `KEEP_GAMEPLAY` — diferença intencional/aceitável para gameplay;
- `ADAPT_LOCAL` — adaptação local justificada;
- `SOURCE_LIMITATION` — limitação da fonte;
- `NEEDS_REVIEW` — evidência insuficiente;
- `ERROR` — erro inequívoco.

Não converter automaticamente toda divergência em `ERROR`.

## Jogabilidade é requisito estrutural

O chão, ruas e circulação precisam funcionar para um jogo, não apenas coincidir com o mundo real.

Antes de uma correção estrutural, avaliar impacto em:

- personagem a pé;
- veículos;
- NPCs/pedestres;
- câmera;
- colisão;
- navegação;
- tráfego;
- missões/perseguições;
- performance.

Adaptações locais de largura, inclinação, raio de curva, degraus, transições, calçadas e acessos são permitidas quando resolvem problema comprovável e preservam a identidade do lugar.

A geometria visual não deve acumular todas as responsabilidades. Manter, quando implementadas, separações equivalentes a:

```text
SOURCE_GEOREF
REFERENCE_OSM
REFERENCE_TERRAIN
ENVIRONMENT_FINAL
GAMEPLAY_TERRAIN
ROAD_DRIVEABLE
SIDEWALK_WALKABLE
NAVIGATION_HINTS
COLLISION
HERO
WATER
STREAMING
```

Detalhes e critérios estão em `docs/GAMEPLAY_FIDELITY_POLICY.md`.

## Engine e interoperabilidade

A engine definitiva ainda não está escolhida. Não introduzir dependência estrutural desnecessária de Godot, Unity ou Unreal nesta fase.

Manter:

- unidade métrica consistente;
- origem documentada;
- transforms controlados;
- IDs/nomenclatura estáveis;
- colisores separados;
- metadados estruturados;
- mundo divisível em setores;
- exportação interoperável quando apropriada.

A escolha da engine será feita por vertical slice funcional com personagem, carro, NPCs, navegação, tráfego, streaming e performance, não por preferência abstrata.

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

O pipeline gera estrutura OSM, QA topológico, auditoria do DEM, QA opcional das vias, fit XY e referência estrutural Blender.

Antes de corrigir a cena, revisar `osm_topology_audit.json` e `georef_fit.json`.

### Fit vertical do terreno

Depois de fechar o fit XY, exportar amostras reais da mesh de terreno:

```bash
blender CENA.blend --background \
  --python tools/blender/export_terrain_samples.py \
  -- --output docs/reports/blender/terrain_samples.json
```

Se a seleção automática incluir objetos indevidos, repetir com `--include-regex` explícito.

Então estimar a relação vertical:

```bash
python tools/terrain/fit_dem_blender_vertical.py \
  --samples docs/reports/blender/terrain_samples.json \
  --fit artifacts/structural-pipeline/mvp-centro-lacerda/georef_fit.json \
  --dem CAMINHO/terrain.tif \
  --output docs/reports/blender/terrain_vertical_fit.json
```

Revisar escala, offset e maiores resíduos. Nunca aplicar escala/offset Z global automaticamente apenas porque o fit foi calculado.

### Comparação da cena com a referência

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

A captura histórica do MVP recuperada é:

`aleph-20260924T205631Z-aqqo7pkx`

Não implementar merge automático de novas áreas até a transformação mundo real → Blender estar verificada por múltiplos anchors e registrada com erro residual.

## Revisões Blender

- preservar arquivo anterior;
- salvar nova revisão quando houver mudança real que justifique nova revisão;
- evitar operações destrutivas ocultas;
- validar reabertura;
- gerar relatórios;
- manter `HERO`, `GAMEPLAY`, `SOURCE_GEOREF`, referência geográfica, colisão/navegação e geometria final semanticamente separadas;
- corrigir estrutura antes de decoração;
- não criar nova cópia `.blend` apenas para alterar número de revisão quando nenhuma mudança de cena ocorreu.

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
- reescala Z global sem fit/revisão;
- renomeação em massa;
- duplicação de geometria sem necessidade;
- path absoluto versionado;
- número aproximado apresentado como medido;
- largura de rua inventada quando a fonte não fornece;
- edição silenciosa do DEM-fonte;
- substituição silenciosa de fonte de dados;
- uso de decoração para esconder desalinhamento estrutural;
- correspondência automática entre asset e feature real sem ID/proveniência confiável;
- deformação do mundo apenas para reduzir uma métrica sem ganho de identidade ou gameplay;
- usar a malha visual detalhada como collider/navmesh por conveniência quando isso prejudicar estabilidade ou performance.

Quando uma informação ainda não foi verificada, mantê-la explicitamente como `null`, `candidate`, `partial` ou `pending` conforme o contrato correspondente.
