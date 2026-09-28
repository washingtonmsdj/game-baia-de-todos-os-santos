# R30A.1 — diagnóstico estrutural corrigido

## Estado

**Diagnóstico concluído; nenhuma correção geométrica foi aplicada.** A rodada R30A.1 foi executada sobre a revisão `.blend` dentro deste repositório, aberta no Blender 5.2.2 com o addon BlendMCP conectado na porta local 9876. A origem R30A não foi sobrescrita.

Arquivo de trabalho versionável:

`blender/salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a_structure_ref.blend`

O arquivo está configurado para Git LFS. SHA-256 da cópia no projeto: `ACF5F5BBA00DED0FC912116DB02DE7FCA26C43BB8DBF67A10AC5CB8A3C319A30`. A sessão BlendMCP apenas leu a cena e exportou relatórios; não foi salva uma alteração de geometria ou binding no `.blend`.

## Validação inicial

- `python -m compileall -q tools tests`: passou.
- `python -m unittest discover -s tests -p "test_*.py" -v`: 43 testes passaram.
- `python tools/references/validate_registry.py --root .`: 0 erros; 2 avisos preexistentes sobre bounds WGS84 e referência do cais de Praça Cairu.

## Cobertura DEM — R30A × R30A.1

Na R30A, o gate usava o bbox de todos os ways OSM completos e produzia cobertura de `0,1584%`. A R30A.1 detectou automaticamente o `manifest.json` ao lado do `map.osm` e passou a usar a janela real da captura Aleph:

- `dem_coverage_target_kind`: `capture_bounds`;
- `capture_bounds_source`: `data/aleph/aleph-20260924T205631Z-aqqo7pkx/manifest.json`;
- status: `covered_with_margin`;
- cobertura da janela: `100%`;
- margens DEM projetadas: oeste `285,691 m`, sul `702,306 m`, leste `1.325,398 m`, norte `829,797 m`.

O bbox completo do OSM continua preservado no relatório para auditoria: ele é muito maior porque alguns ways atravessam a janela e mantêm sua geometria completa. Nenhum way foi cortado e `terrain.tif` não foi alterado, recortado ou reamostrado.

O DEM ainda registra faixa vertical incomum, com mínimo `-1092,837 m`; a cobertura horizontal corrigida não transforma esse aviso em calibração vertical válida.

## Seleção de terreno — R30A × R30A.1

Seleção anterior: 121 objetos e 8.319 amostras, incluindo estruturas, fachadas, passarela, calçadas, proxies volumétricos e perfis estimados.

A seleção `strict` automática reduziu a lista, mas revelou falsos positivos nos dois objetos `Igreja da Ordem Terceira de São Domingos`: a substring `dem` de “Ordem” coincidia com a heurística. Também não foram aceitos como superfície real os proxies de 8 vértices das coleções de aproximação/calibração e o perfil estimado da ladeira.

A seleção final foi consciente e reproduzível com `--include-regex`, aceitando somente:

- objeto: `MVP | terreno corrigido | colisão estática`;
- coleção: `19 MVP | terreno DEM e acessos corrigidos`;
- 1 objeto;
- 4.978 amostras de 547.464 vértices.

Essa seleção representa a superfície de terreno/colisão do MVP. Nenhum objeto foi movido, editado ou marcado com propriedade nova no Blender.

## Fit vertical — R30A × R30A.1

| Métrica | R30A | R30A.1 |
|---|---:|---:|
| Objetos | 121 | 1 |
| Amostras de entrada | 8.319 | 4.978 |
| Amostras mantidas | 8.077 | 4.900 |
| Outliers removidos | 242 | 78 |
| Escala Z Blender/DEM | 1,0017919 | 1,0253290 |
| Offset Z Blender | -0,0754322 | -4,6316455 |
| RMS | 12,5435866 | 9,2106683 |
| Mediana absoluta | 7,8351733 | 5,2179134 |
| Máximo residual | 44,1592265 | 29,3265740 |
| Razão escala vertical/horizontal | 1,0325905 | 1,0568512 |

O resultado novo permanece `quality: insufficient` e `status: candidate_only`. A seleção limpa melhorou os resíduos, mas ainda há discrepâncias relevantes e o mínimo anômalo do DEM exige revisão. Nenhuma escala ou offset Z foi aplicado.

## Mercado Modelo e bindings

Na auditoria antiga, o ID `59392558` aparecia em:

- `MERCADO MODELO | footprint OSM` — edifício correto;
- `MVP | terreno corrigido | colisão estática` — terreno, incompatível com a camada `buildings`.

A origem da segunda ocorrência não era uma propriedade OSM explícita. Era apenas o texto descritivo da propriedade:

`mercado_support = "OSM 59392558: apoio z10.82, entorno integrado sem laje retangular sobre vias"`

O auditor foi corrigido para aceitar IDs somente do nome do objeto ou de propriedades OSM explícitas (`osm_id`, `way_id`, `relation_id` e equivalentes). A propriedade `mercado_support` foi preservada; não houve alteração de metadado no `.blend`.

Após a correção do diagnóstico:

- `MVP | terreno corrigido | colisão estática`: nenhum OSM ID detectado;
- `MERCADO MODELO | footprint OSM`: permanece com `59392558`;
- offset agregado antigo: `249,446 m`;
- offset do footprint isolado: `1,878 m`;
- conflito de binding do Mercado: não sinalizado;
- máximo de offset agregado na nova comparação: `3,462 m`.

O comparador completo encontrou 1.359 IDs compartilhados, 891 itens de revisão e 843 `binding_conflict_review` em outros IDs. Esses conflitos permanecem para triagem; não justificam remoção em massa nem movimento automático.

## Fit XY

O fit XY permaneceu estável após o diagnóstico corrigido:

- escala: `0,9701734818` unidades Blender por metro;
- rotação: `-0,050990°`;
- RMS: `4,168632` unidades Blender;
- anchors robustos: `1.012`;
- status: `candidate_only`.

Não houve deslocamento do Mercado, reescala global, alteração de coastline, cais, ruas, escadarias ou footprints.

## Bloqueios eliminados

- O falso bloqueio de cobertura causado pelo bbox OSM inflado foi eliminado: a janela real da captura está coberta.
- O falso binding do Mercado causado pela interpretação de texto descritivo foi eliminado no auditor.
- A seleção vertical deixou de aceitar automaticamente as estruturas e proxies contaminantes; o conjunto final é explicitamente um único objeto de superfície do MVP.

## Bloqueios reais restantes

1. Fit vertical ainda insuficiente, com residual máximo de `29,327` unidades Blender.
2. Faixa vertical anômala do DEM, incluindo mínimo negativo, precisa de revisão de unidade, nodata ou artefato.
3. Existem 843 conflitos de binding para revisão individual; o Mercado não está entre eles após a correção.
4. A auditoria topológica ainda registra 149 itens de revisão, 160 endpoints internos e 9 near-misses.
5. O fit XY segue candidato, não verificado; a origem/licença dos dados de elevação permanece pendente.

R30A.1 não autoriza R30B, decoração ou correção estrutural em massa. A próxima decisão deve continuar na ordem estrutural: terreno/vertical, escarpa, coastline/cais, ruas, cruzamentos, escadas/calçadas e footprints.
