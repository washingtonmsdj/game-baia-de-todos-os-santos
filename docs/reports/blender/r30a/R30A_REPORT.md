# R30A — alinhamento estrutural do MVP

## Estado

**Bloqueada, não concluída.** A captura histórica `aleph-20260924T205631Z-aqqo7pkx` registrada na cena não foi recuperada na estação. A própria cena aponta para `data/aleph/aleph-20260924T205631Z-aqqo7pkx/map.osm`; não foi usada outra captura como substituta.

## Trabalho realizado

- Validação do repositório: `compileall`, 37 testes unitários e validação do registro de referências concluídos.
- Cena usada: revisão R27 mais recente e válida encontrada localmente, preservada sem sobrescrita.
- Blender 5.2.2 abriu a cena com `--factory-startup` sem erro de carregamento.
- Exportados `georef_hints.json`, `structural_scene_audit_before.json`, `terrain_samples.json` e o resumo da cena R27.
- A cena contém os anchors explícitos Mercado Modelo `59392558` e Palácio Rio Branco `402383814`.
- Criado apenas um pre-flight Blender sem alteração geométrica: `R30A_PREFLIGHT` e propriedades de status. O binário local é `salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a_preflight.blend` e não foi versionado.
- O SHA-256 da origem R27 preservada é `90FC6F91C01A6515786A0A94E6219C3D05E11480F03FA8EE64A82332FBF5F7CA`.

## Métricas observadas

| Item | R27 auditada |
|---|---:|
| Objetos totais | 4.668 |
| Mesh datablocks | 4.137 |
| Materiais | 135 |
| Coleções | 34 |
| Curvas | 412 |
| Câmeras | 55 |
| Luzes | 4 |
| Objetos classificados na auditoria estrutural | 4.407 |
| Objetos com OSM ID explícito | 2.264 |
| IDs OSM únicos detectados | 1.399 |
| Objetos de terreno selecionados para amostra | 140 |
| Vértices de terreno exportados | 8.319 |

Não há métricas antes/depois de alinhamento porque nenhuma geometria foi corrigida.

## Bloqueios reais

Sem `manifest.json`, `map.osm` e `terrain.tif` correspondentes não é possível, de forma rastreável:

- executar o inspector de captura e confirmar bounds/proveniência;
- extrair estrutura OSM e suporte a multipolygons;
- auditar topologia e cobertura DEM ↔ OSM;
- fechar fit XY por múltiplos anchors;
- gerar/importar `SOURCE_GEOREF | STRUCTURAL_REFERENCE`;
- calcular fit vertical DEM ↔ Blender ou perfis DEM sob vias;
- comparar entidades da cena com a referência estrutural;
- classificar correções de coastline, cais, escarpa, ruas e footprints.

## O que permanece aproximado

- O terreno histórico registra Aleph DEM EPSG:3857 + OSM, mas sua fonte efetiva e licença não foram reconfirmadas.
- Cotas conciliadas localmente da cena continuam aproximações do MVP.
- A entrada superior, a saída inferior, a ladeira e trechos da escarpa permanecem pendentes de validação contra a captura original.
- Os anchors existentes são pistas da cena, não uma transformação geográfica verificada.

## Próximo passo seguro

Recuperar a captura histórica, preservar seus arquivos originais, executar `inspect_capture.py` e `audit_dem.py`, e então repetir o pipeline estrutural completo. Até lá, não mover assets, não alterar o DEM, não criar offsets e não avançar para decoração.
