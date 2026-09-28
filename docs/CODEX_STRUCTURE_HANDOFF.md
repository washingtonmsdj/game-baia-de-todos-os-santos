# Handoff do Codex — Fidelidade Estrutural

## Objetivo

Executar a evolução estrutural do **Bay of All Saints** de forma reproduzível, priorizando georreferenciamento, terreno, coastline/cais, vias e footprints antes de acabamento visual — **sem confundir fidelidade com réplica milimétrica**.

Antes deste documento, ler obrigatoriamente:

- `AGENTS.md`;
- `docs/PROJECT_STATUS.md`;
- `docs/GAMEPLAY_FIDELITY_POLICY.md`.

A referência real orienta o mundo. A geometria final precisa funcionar como jogo.

## Regra de decisão estrutural

Uma divergência OSM/DEM ↔ Blender não autoriza correção automática.

Antes de mover ou deformar qualquer coisa, classificar a situação como:

- `KEEP_REAL_REFERENCE`;
- `KEEP_GAMEPLAY`;
- `ADAPT_LOCAL`;
- `SOURCE_LIMITATION`;
- `NEEDS_REVIEW`;
- `ERROR`.

Corrigir quando houver ganho real em pelo menos um destes eixos:

- identidade/reconhecimento de Salvador;
- continuidade espacial;
- acesso a local importante;
- dirigibilidade;
- circulação do jogador;
- navegação de NPCs;
- colisão;
- câmera;
- missão/perseguição;
- performance.

Não perseguir RMS mínimo como objetivo artístico.

## 1. Entradas locais

Usar a captura histórica:

```text
aleph-20260924T205631Z-aqqo7pkx/
  manifest.json
  map.osm
  terrain.tif
```

Consultar `docs/PROJECT_STATUS.md` para a cena `.blend` oficial atual e seu SHA-256.

Nunca sobrescrever a captura-fonte nem uma cena validada sem motivo documentado.

## 2. Auditar captura e DEM

```bash
python tools/aleph/inspect_capture.py CAMINHO_DA_CAPTURA \
  --output docs/reports/aleph/mvp-centro-lacerda/source_summary.json

python tools/terrain/audit_dem.py \
  --dem CAMINHO_DA_CAPTURA/terrain.tif \
  --output docs/reports/aleph/mvp-centro-lacerda/dem_audit.json
```

Se CRS/bounds/resolução divergirem do esperado, investigar antes de continuar.

Valores negativos no recorte costeiro não devem ser automaticamente classificados como erro/nodata; o dataset pode conter batimetria. Consultar `SOURCE_REGISTRY.json` e a revisão R30A.2.

## 3. Exportar pistas e auditoria da cena

```bash
blender CENA_VALIDADA.blend --background \
  --python tools/blender/extract_georef_hints.py \
  -- --output docs/reports/blender/georef_hints.json

blender CENA_VALIDADA.blend --background \
  --python tools/blender/audit_structural_scene.py \
  -- --output docs/reports/blender/structural_scene_audit_before.json
```

A auditoria estrutural registra OSM IDs explícitos e exclui objetos `SOURCE_GEOREF`.

## 4. Executar pipeline estrutural

Quando `rasterio` estiver disponível:

```bash
python tools/world/run_structural_pipeline.py \
  --osm CAMINHO_DA_CAPTURA/map.osm \
  --dem CAMINHO_DA_CAPTURA/terrain.tif \
  --hints docs/reports/blender/georef_hints.json \
  --audit-road-profiles \
  --output-dir artifacts/structural-pipeline/mvp-centro-lacerda
```

Sem `rasterio`, omitir `--audit-road-profiles`. Sem DEM, omitir também `--dem`.

Artefatos esperados:

```text
osm_structure.json
osm_topology_audit.json
georef_fit.json
structural_reference.json
dem_audit.json
dem_osm_coverage.json
dem_road_profiles.json
```

Fit XY `insufficient` deve parar o fluxo. Opções de override são diagnóstico, não promoção automática.

## 5. Revisar topologia da fonte

Antes de usar a sobreposição, revisar `osm_topology_audit.json` nesta ordem:

1. node refs ausentes;
2. buildings não fechados;
3. coastline interrompida internamente;
4. near-misses;
5. endpoints internos de transporte;
6. componentes inesperadamente desconectados;
7. possíveis separações por bridge/tunnel/layer.

Consultar `docs/OSM_TOPOLOGY_QA.md`.

Não deformar o Blender para reproduzir erro comprovado da fonte OSM.

## 6. Revisar fit XY

Conferir:

- anchors usados;
- `meters_per_blender_unit`;
- rotação;
- origem;
- RMS e residual máximo;
- outliers;
- Mercado Modelo way `59392558`;
- Palácio Rio Branco way `402383814` quando presentes.

Nunca promover automaticamente o fit para `verified` apenas por quantidade de anchors.

Um offset pequeno em asset coerente não obriga movimento se a experiência e a relação espacial já estiverem boas.

## 7. Fechar relação vertical DEM ↔ Blender

Exportar amostras da geometria real de terreno:

```bash
blender CENA_VALIDADA.blend --background \
  --python tools/blender/export_terrain_samples.py \
  -- --output docs/reports/blender/terrain_samples.json
```

Se a seleção automática incluir objetos que não representam superfície principal, repetir com `--include-regex` restritivo ou propriedades explícitas.

Calcular o fit vertical:

```bash
python tools/terrain/fit_dem_blender_vertical.py \
  --samples docs/reports/blender/terrain_samples.json \
  --fit artifacts/structural-pipeline/mvp-centro-lacerda/georef_fit.json \
  --dem CAMINHO_DA_CAPTURA/terrain.tif \
  --output docs/reports/blender/terrain_vertical_fit.json
```

Quando aplicável, executar também a análise por domínio da R30A.2:

```bash
python tools/terrain/analyze_vertical_domains.py \
  --samples docs/reports/blender/terrain_samples.json \
  --fit artifacts/structural-pipeline/mvp-centro-lacerda/georef_fit.json \
  --dem CAMINHO_DA_CAPTURA/terrain.tif \
  --output docs/reports/blender/vertical_domains.json
```

Revisar escala, offset, relação vertical/horizontal, RMS, distribuição espacial e maiores resíduos.

**Não aplicar reescala/offset global automaticamente.** Um terreno jogável pode divergir localmente do DEM por razões legítimas.

## 8. Importar referência estrutural

```bash
blender CENA_VALIDADA.blend --background \
  --python tools/blender/import_structural_reference.py \
  -- \
  --reference artifacts/structural-pipeline/mvp-centro-lacerda/structural_reference.json \
  --save-as CENA_structure_ref.blend
```

A coleção `SOURCE_GEOREF | STRUCTURAL_REFERENCE` é somente referência, oculta no render e nunca deve ser convertida automaticamente em arte final.

Camadas possíveis:

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

## 9. Comparar entidades da cena por OSM ID

```bash
python tools/world/compare_scene_reference_alignment.py \
  --scene-audit docs/reports/blender/structural_scene_audit_before.json \
  --reference artifacts/structural-pipeline/mvp-centro-lacerda/structural_reference.json \
  --output docs/reports/blender/scene_reference_alignment.json
```

Somente IDs explícitos são comparados. Não criar binding por semelhança de nomes.

Flags são triagem, não prova automática de erro.

Consultar `docs/SCENE_REFERENCE_ALIGNMENT_QA.md`.

## 10. Decidir se a correção vale a pena

Para cada divergência relevante, registrar:

```text
fonte real
objeto Blender
métrica/erro observado
impacto visual
impacto a pé
impacto veicular
impacto NPC/navmesh
impacto colisão/câmera
classificação
mudança proposta
risco
```

Exemplos:

- encosta com erro grande mas inacessível: pode ser `KEEP_GAMEPLAY` ou `SOURCE_LIMITATION`;
- rua com pequeno erro que quebra entrada importante: pode ser `ADAPT_LOCAL`;
- prédio com binding falso: `ERROR`;
- curva real estreita que impede carro/câmera: adaptação jogável local pode ser correta.

## 11. Corrigir a cena na ordem correta

A ordem não é “zerar referência”. É estabilizar o jogo:

1. erros inequívocos de binding/fonte/implantação;
2. interfaces críticas do terreno;
3. coastline e waterfront/cais onde afetam leitura/acesso;
4. eixos viários e cruzamentos;
5. dirigibilidade das vias prioritárias;
6. áreas pedonais, escadas e calçadas;
7. colisão funcional;
8. conectividade de NPCs;
9. footprints relevantes;
10. integração conservadora com Hero assets;
11. detalhe visual somente depois.

### Terreno

Nunca editar silenciosamente `terrain.tif`. Artefato comprovado deve virar correção derivada/local documentada.

Não suavizar globalmente a escarpa para reduzir resíduos.

A superfície visual pode ser detalhada; a superfície de gameplay/colisão pode ser mais limpa.

### Vias

Priorizar:

1. conectividade;
2. eixo reconhecível;
3. cruzamentos;
4. dirigibilidade;
5. largura funcional;
6. calçadas/travessias;
7. detalhe.

Largura real desconhecida pode receber aproximação de gameplay documentada; não chamar de medida real.

### Coastline

Manter separados:

```text
coastline geográfica
waterfront construído
water surface visual
```

A água visual se adapta à estrutura; a estrutura não deve ser movida apenas para servir ao shader.

### Colisão e navegação

Não usar a malha visual detalhada como única colisão/navmesh.

Preferir colliders simplificados e superfícies funcionais dedicadas.

## 12. Auditoria depois

```bash
blender CENA_NOVA.blend --background \
  --python tools/blender/audit_structural_scene.py \
  -- --output docs/reports/blender/structural_scene_audit_after.json
```

Registrar diferenças antes/depois e motivo de cada adaptação relevante.

## 13. Gate de conclusão estrutural do MVP

O recorte só deve avançar para arte pesada quando:

- topologia crítica estiver classificada;
- fit XY estiver entendido o suficiente para controle estrutural;
- problemas verticais relevantes estiverem classificados por região;
- coastline/cais prioritários estiverem coerentes;
- Praça Cairu conectar corretamente Elevador, Mercado, vias e waterfront;
- vias prioritárias forem caminháveis/dirigíveis conforme intenção;
- áreas críticas tiverem colisão planejada;
- navegação de pedestres/NPCs tiver caminho claro para implementação;
- Hero assets não tiverem sido movidos para mascarar erro de base;
- adaptações de gameplay relevantes estiverem registradas.

## 14. Próxima fronteira: vertical slice em engine

Quando o recorte estrutural e funcional estiver estável, preparar o corredor:

**Cidade Alta → Elevador Lacerda → Praça Cairu → Mercado Modelo → Cidade Baixa/waterfront**

para teste com:

- personagem;
- veículo;
- pedestres/NPCs;
- navmesh;
- rede de tráfego mínima;
- colisão;
- água;
- streaming;
- performance.

A escolha de Godot/Unity/Unreal deve ser decidida depois desse teste, conforme `docs/GAMEPLAY_FIDELITY_POLICY.md`.

## 15. Manutenção documental

Após qualquer mudança material, atualizar `docs/PROJECT_STATUS.md` e os documentos afetados.

Não deixar decisões de direção apenas em mensagens de chat.