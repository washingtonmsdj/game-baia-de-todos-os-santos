# Handoff Codex — R30A.1

## Objetivo

Reexecutar o diagnóstico estrutural corrigindo três falsos sinais da R30A original:

1. gate DEM calculado contra bbox OSM inflado por ways completos;
2. fit vertical contaminado por objetos que não são terreno;
3. binding OSM agregado contaminado por objeto incompatível, especialmente Mercado Modelo `59392558`.

Não iniciar passe visual e não mover a cidade por causa dos números antigos.

## Entrada

Usar a mesma captura histórica recuperada:

`data/aleph/aleph-20260924T205631Z-aqqo7pkx/`

com `manifest.json`, `map.osm` e `terrain.tif` preservados.

Usar como cena de diagnóstico a revisão R30A com referência estrutural já importada ou a origem preservada, conforme fizer mais sentido para cada exportador. Nunca sobrescrever a origem.

## Passos

### 1. Validar repositório

```bash
python -m compileall -q tools tests
python -m unittest discover -s tests -p "test_*.py" -v
python tools/references/validate_registry.py --root .
```

### 2. Reexecutar pipeline estrutural

O runner agora detecta automaticamente `manifest.json` ao lado de `map.osm` e usa os bounds da captura no gate DEM.

Não usar `--allow-insufficient-dem-coverage` na primeira tentativa.

Confirmar no resultado:

```text
dem_coverage_target_kind = capture_bounds
capture_bounds_source = .../manifest.json
```

Se a cobertura continuar insuficiente contra `capture_bounds`, registrar os números e parar qualquer uso vertical do DEM até revisar a causa.

### 3. Reexportar amostras de terreno

Executar `export_terrain_samples.py` no modo padrão `strict`.

Antes do fit vertical, revisar a lista de objetos selecionados.

Não aceitar como terreno objetos de:

- passarela;
- fachada;
- torre;
- mobiliário;
- calçada/pista apenas por estarem em coleção chamada TERRENO;
- estruturas de contenção que não representem superfície do solo.

Quando necessário, usar `boas_terrain_surface=true/false` ou `--include-regex/--exclude-regex` e registrar a decisão.

### 4. Reexecutar fit vertical

Usar o novo `terrain_samples.json` estrito com o mesmo `georef_fit.json` candidato, desde que o fit XY continue válido.

Comparar:

- quantidade de objetos/amostras;
- escala vertical;
- offset Z;
- RMS;
- mediana absoluta;
- resíduos por objeto.

Não aplicar escala/offset Z automaticamente.

### 5. Reexecutar comparação cena ↔ referência

Gerar novamente `structural_scene_audit` e `scene_reference_alignment.json`.

O comparador agora gera:

- `best_object_candidate`;
- `object_candidates`;
- `binding_conflict_review`;
- `binding_conflicts`.

Revisar primeiro Mercado Modelo `59392558`.

Se `MVP | terreno corrigido | colisão estática` realmente carrega o OSM ID do Mercado sem representar o Mercado, corrigir **somente o metadado/binding indevido**, preservando a geometria. Documentar antes/depois.

Não mover o footprint correto para compensar um binding errado.

### 6. Fit XY

Depois de corrigir bindings inequivocamente errados, exportar novamente hints/auditoria se necessário e reexecutar o fit XY.

Comparar com a R30A:

```text
escala: 0,9701734818
rotação: -0,050990°
RMS: 4,168632
anchors robustos: 1.012
```

Mudança grande nesses valores exige investigação; não promover automaticamente.

## Entregáveis

Criar em `docs/reports/blender/r30a1/`:

- `R30A1_REPORT.md`;
- `r30a1_status.json`;
- novo `terrain_samples.json`;
- novo `terrain_vertical_fit.json`;
- novo `scene_reference_alignment.json`;
- qualquer audit antes/depois de binding corrigido;
- tabela comparativa R30A → R30A.1.

Atualizar os artefatos estruturais locais em `artifacts/structural-pipeline/mvp-centro-lacerda/`.

Salvar nova revisão `.blend` somente se algum binding/metadado for efetivamente corrigido; não versionar o binário pesado no Git comum.

## Critério de sucesso

R30A.1 é bem-sucedida quando sabemos, com dados limpos:

- se o DEM cobre ou não o recorte real;
- qual conjunto de meshes realmente representa terreno;
- qual é o fit vertical sem estruturas contaminantes;
- quais OSM IDs possuem bindings conflitantes;
- se o footprint do Mercado Modelo está realmente desalinhado ou se o outlier era apenas metadado incorreto.

Ainda não é autorização para decoração ou correção estrutural em massa.
