# R30A.1 — correções do diagnóstico estrutural

## Motivo

A execução R30A do commit `a19b4fd` foi correta ao **não mover geometria**, mas revelou três problemas no próprio diagnóstico que precisam ser resolvidos antes de qualquer correção estrutural do Blender.

## 1. Cobertura DEM artificialmente insuficiente

A captura Aleph tem bounds WGS84:

```text
south = -12.977
west  = -38.5155
north = -12.969
east  = -38.508
```

O `map.osm` exportado pelo Aleph/Geofabrik preserva ways completos. Alguns objetos atravessam a janela de captura e carregam geometria muito além do retângulo solicitado.

A R30A comparou o DEM contra o bbox de **todas as geometrias OSM completas**, produzindo cobertura de `0,1584%`. Esse número não deve ser interpretado como cobertura física real do DEM sobre o MVP.

### Correção

`compare_dem_osm_coverage.py` agora aceita `--capture-bounds-source` e usa os bounds WGS84 do:

- `manifest.json` Aleph;
- `source_summary.json`; ou
- `area.json`.

`run_structural_pipeline.py` procura automaticamente `manifest.json` ao lado de `map.osm`.

O bbox completo do OSM continua registrado para auditoria, mas não invalida o DEM quando a janela real da captura está coberta.

Nenhum way OSM é cortado ou modificado por essa correção.

## 2. Fit vertical contaminado por objetos que não são terreno

A R30A exportou 8.319 amostras de 121 objetos. Entre os objetos classificados como terreno apareceram exemplos como:

- montantes de passarela;
- vãos verticais da torre;
- fachadas;
- calçadas;
- coroamentos/fechamentos da encosta.

Isso aconteceu porque a heurística histórica considerava **nome do objeto + nomes das coleções** e keywords amplas como `relevo` e `encosta`.

O RMS vertical `12,5436` portanto não deve ser usado como calibração de Z.

### Correção

`export_terrain_samples.py` passa a usar `--selection-mode strict` por padrão.

No modo estrito:

- apenas o nome do próprio objeto é considerado automaticamente;
- keywords automáticas são `terreno`, `terrain` e `dem`;
- nomes de coleção não promovem um objeto a terreno;
- `boas_terrain_surface=true` inclui explicitamente;
- `boas_terrain_surface=false` exclui explicitamente;
- `--include-regex` e `--exclude-regex` permitem seleção consciente/reproduzível;
- `--selection-mode legacy` existe apenas para reproduzir auditorias anteriores.

O schema de amostras permanece v1 porque o formato geométrico não mudou; foram adicionados metadados de seleção compatíveis.

## 3. OSM ID agregado pode esconder binding errado

Na R30A, o Mercado Modelo `59392558` apareceu ligado tanto ao footprint esperado quanto ao objeto:

`MVP | terreno corrigido | colisão estática`

Ao agregar todos os bounds com o mesmo OSM ID, o comparador produziu um offset enorme que não representa necessariamente a posição do footprint correto.

### Correção

`compare_scene_reference_alignment.py` agora:

- preserva a comparação agregada antiga;
- compara também cada objeto individual associado ao OSM ID;
- compara categorias semânticas da cena contra a camada OSM esperada;
- escolhe um `best_object_candidate` apenas para triagem;
- gera `binding_conflict_review` quando o agregado é contaminado por objetos semanticamente incompatíveis ou espacialmente divergentes;
- nunca remove propriedade, move objeto ou escolhe automaticamente qual binding apagar.

O relatório passa para schema `scene-reference-alignment-v2`.

## Execução R30A.1 esperada

1. atualizar o repositório;
2. reexecutar testes;
3. reexecutar `run_structural_pipeline.py` sem `--allow-insufficient-dem-coverage` inicialmente;
4. confirmar que o runner detectou o `manifest.json` como `capture_bounds_source`;
5. exportar novamente `terrain_samples.json` com seleção `strict`;
6. inspecionar a lista de objetos selecionados antes do fit vertical;
7. executar novamente o fit vertical;
8. executar novamente a auditoria da cena e `compare_scene_reference_alignment.py`;
9. revisar especificamente o `binding_conflict_review` do Mercado Modelo;
10. não mover geometria nesta rodada salvo se um erro de binding puder ser corrigido de forma inequívoca, não destrutiva e documentada.

## Gate para correção geométrica

Só iniciar movimentos/correções estruturais quando:

- a cobertura DEM contra a **janela da captura** estiver explicada;
- a seleção vertical contiver somente superfícies de terreno conscientemente aceitas;
- o fit vertical for reavaliado;
- bindings OSM conflitantes forem identificados por objeto;
- o fit XY continuar estável após remoção/isolamento dos bindings incorretos;
- divergências remanescentes puderem ser atribuídas à geometria da cena e não ao diagnóstico.

A R30A.1 é uma revisão de confiabilidade do diagnóstico. Ela não deve ser usada para antecipar a R30B visual.
