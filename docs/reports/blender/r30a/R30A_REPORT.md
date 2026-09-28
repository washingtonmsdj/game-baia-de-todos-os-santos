# R30A — alinhamento estrutural do MVP

## Estado

**Diagnóstico executado; R30A não concluída.** A captura histórica `aleph-20260924T205631Z-aqqo7pkx` foi recuperada localmente e preservada. O pipeline foi executado, mas a cobertura DEM ↔ OSM e o fit XY não atingiram os critérios para uma correção estrutural rastreável. Nenhuma geometria, escala Z, coastline ou asset foi movido.

## Captura e proveniência

- Manifest Aleph: `data/aleph/aleph-20260924T205631Z-aqqo7pkx/manifest.json`, estado `complete`.
- OSM: `map.osm`, 11.590.732 bytes; origem observada `download.geofabrik.de`; uso de produção com atribuição ODbL.
- DEM: `terrain.tif`, 498.804 bytes; origem observada `elevation-tiles-prod.s3.amazonaws.com`; licença/origem dos dados de elevação ainda pendente de confirmação.
- Bounds WGS84 registrados pelo capture: `[-12.977, -38.5155, -12.969, -38.508]`.
- Relatórios: `docs/reports/aleph/mvp-centro-lacerda/source_summary.json` e `dem_audit.json`.

O DEM é GeoTIFF Float32, 512×512, EPSG:3857, pixel de 4,777314 m. A auditoria encontrou 262.144 pixels válidos, mínimo `-1092,837 m`, máximo `81,924 m` e um aviso de faixa de elevação incomum. O arquivo-fonte não foi alterado, suavizado ou reamostrado.

## Pipeline estrutural executado

Saída local não versionada: `artifacts/structural-pipeline/mvp-centro-lacerda/`.

- Estrutura OSM v2: 81.523 nós, 2.592 ways, 2.446 ways classificados, 13 relações multipolygon carregadas, 9 features de relação emitidas e 2.455 features totais.
- Camadas: buildings 1.050; cliffs 3; coastline 1.069; pedestrian 126; railways 8; retaining_walls 2; roads 187; steps 6; waterfront 4.
- Integridade de referências: nenhum missing node ref, nenhum membro de way ausente, nenhuma cadeia outer multipolygon incompleta e nenhum edifício aberto.
- QA topológico: 160 endpoints internos pendentes, 9 pares near-miss, 302 componentes de coastline e 149 itens na fila de revisão. Os endpoints de coastline não foram automaticamente unidos.

### Cobertura DEM ↔ OSM

O status foi `insufficient`: razão de cobertura `0,0015837449` (0,1584%). O bbox OSM extraído mede aproximadamente 3.777.655.175 m², enquanto o DEM mede 5.982.842 m²; há margens negativas em todas as bordas. O pipeline foi autorizado a continuar somente para produzir diagnóstico (`--allow-insufficient-dem-coverage`).

Isso não autoriza extrapolar altitude, esticar o raster ou recortar silenciosamente a estrutura OSM. É necessário confirmar se os ways completos que atravessam a área ampliam o bbox além do capture e, se for útil, gerar uma execução separada explicitamente restrita aos bounds da captura.

### Perfis DEM sob vias

Foram analisadas 313 features, com 6.896 amostras; 85 features foram marcadas para revisão e 1 apresentou nodata. Os saltos e declividades extremos não foram corrigidos: com a cobertura insuficiente e o aviso de faixa do DEM, esses valores permanecem evidência para QA, não autorização para ajustar vias ou terreno.

## Fit XY e referência Blender

O fit produziu `quality: candidate` e `status: candidate_only`:

- 1.032 anchors brutos; 1.012 anchors robustos;
- escala horizontal `0,9701734818` unidades Blender por metro;
- rotação EPSG:3857 → Blender `-0,050990°`;
- RMS `4,168632` unidades Blender; mediana `2,296868`; máximo `13,825936`.

A referência v2 foi gerada e importada somente como coleção `SOURCE_GEOREF | STRUCTURAL_REFERENCE` na revisão local `salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a_structure_ref.blend`. Ela permanece referência, não arte final.

A comparação de entidades com OSM ID explícito encontrou 1.359 IDs comparados e 51 itens de revisão; mediana de offset `0,919 m` e máximo `249,446 m`. O Mercado Modelo (`59392558`) foi removido como outlier do fit, com resíduo de `123,517` unidades Blender. Na comparação de cena, o mesmo ID está ligado ao footprint do Mercado e também ao objeto `MVP | terreno corrigido | colisão estática`, produzindo bounds agregados muito maiores e o offset de `249,446 m`. Esse binding precisa de revisão manual; nenhum objeto foi movido.

O Palácio Rio Branco (`402383814`) não foi sinalizado pela comparação de bounds: offset de centro de `1,092 m`, com dimensões relativas compatíveis. Isso é evidência favorável, mas não promove sozinho o fit para `verified`.

## Fit vertical DEM ↔ Blender

O relatório permanece `quality: insufficient` e `status: candidate_only`:

- 8.319 amostras de terreno; 8.077 mantidas; 242 outliers removidos;
- RMS `12,543587` unidades Blender; mediana absoluta `7,835173`; máximo `44,159227`;
- escala vertical candidata `1,0017919167` unidades Blender por metro DEM;
- razão vertical/horizontal `1,0325904959`.

Nenhuma escala ou offset Z foi aplicado. O resíduo e a cobertura insuficiente impedem tratar o resultado como calibração final.

## Revisão da cena

Foi preservada a origem R27 e criado o pre-flight R30A sem alteração geométrica. A revisão com referência importada foi reaberta no Blender 5.2.2 com `--factory-startup` e auditada. As auditorias antes/depois, excluindo deliberadamente a coleção de referência, permanecem iguais:

- 4.407 objetos estruturais;
- 2.264 objetos com OSM ID explícito;
- 1.399 IDs OSM únicos;
- 207 objetos de terreno, 234 vias, 73 calçadas, 210 escadarias, 59 contenções, 6 waterfront, 262 água e 2.795 edifícios.

`geometry_changed: false`. Não houve correção de coastline, cais, escarpa, ruas, footprints ou relevo.

## Alterações de pipeline

- O runner estrutural passou a usar mensagens ASCII nas etapas para funcionar também em console Windows com code page não UTF-8.
- A auditoria de perfis de vias passou a aceitar `osm-structure-v2`, schema emitido pelo extrator atual.
- O comparador de alinhamento passou a aceitar `blender-structure-reference-v2`.
- Foi adicionada regressão unitária para o suporte ao schema v2.

## Pendências e próximo passo seguro

1. Resolver a discrepância de cobertura DEM ↔ OSM sem alterar `terrain.tif` e sem esconder o bbox real.
2. Confirmar a unidade, nodata e origem/licença do DEM diante do mínimo negativo anômalo.
3. Revisar a fila topológica de coastline e os 9 near-misses antes de qualquer união.
4. Revisar manualmente o binding do Mercado Modelo e os demais outliers; não usar o outlier para deslocar a cidade.
5. Reexecutar fit XY/vertical após a cobertura ser explicada e somente então decidir se alguma correção estrutural é justificável.

Até essas etapas, a R30A deve permanecer como diagnóstico candidato e não como revisão estrutural concluída.
