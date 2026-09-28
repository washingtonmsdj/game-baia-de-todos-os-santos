# R30A.2 — diagnóstico vertical por domínio

## Estado

**Diagnóstico concluído; nenhuma correção geométrica foi aplicada.** A rodada R30A.2 foi executada sobre a cena Blender versionada via Git LFS e aberta na sessão Blender conectada ao BlendMCP. A sessão foi usada somente para inspeção read-only das células críticas e dos objetos da cena; o arquivo `.blend` não foi salvo.

Cena analisada:

`blender/salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a_structure_ref.blend`

SHA-256 confirmado antes e depois do diagnóstico:

`ACF5F5BBA00DED0FC912116DB02DE7FCA26C43BB8DBF67A10AC5CB8A3C319A30`

Base de código: `cc2de0c3bc311ba861fa9819440cd7e533704844` (`main`).

Não foram aplicados escala Z, offset Z, movimento de terreno, alteração do DEM, suavização de escarpa, movimento de ruas/coastline/cais ou alteração do Mercado Modelo. Não foi criada nova cópia `.blend`.

## Validação inicial

- `python -m compileall -q tools tests`: passou.
- `python -m unittest discover -s tests -p "test_*.py" -v`: 46 testes passaram.
- `python tools/references/validate_registry.py --root .`: 0 erros; 2 avisos preexistentes sobre bounds WGS84 e referência insuficiente para `cais-praca-cairu`.
- O arquivo Blender está materializado pelo Git LFS, com 35.522.938 bytes.
- SHA-256 da cena: confere exatamente com o esperado.
- A sessão BlendMCP estava conectada e apontava para a cena dentro do repositório.

O `terrain.tif` usado é a captura histórica `aleph-20260924T205631Z-aqqo7pkx`, mantida fora do Git comum conforme a política de dados pesados. O relatório mantém o caminho lógico `data/aleph/aleph-20260924T205631Z-aqqo7pkx/terrain.tif`; não houve substituição por outra captura.

## Separação dos domínios DEM

Foram reutilizados `docs/reports/blender/r30a1/terrain_samples.json` e `artifacts/structural-pipeline/mvp-centro-lacerda/georef_fit.json`, com a transformação XY candidata já registrada. A amostragem encontrou 4.978 valores DEM válidos e nenhum nodata:

| Domínio | Amostras | Percentual das válidas | Faixa DEM | Mediana DEM |
|---|---:|---:|---:|---:|
| DEM < 0 m — abaixo do nível médio do mar/batimetria | 2 | 0,0402% | -877,8466 a -273,1960 m | -575,5213 m |
| DEM >= 0 m — candidato terrestre | 4.976 | 99,9598% | 0,6232 a 80,8239 m | 47,3847 m |
| Total válido | 4.978 | 100% | -877,8466 a 80,8239 m | — |

Os dois valores negativos não foram convertidos em nodata nem alterados. Eles estão em EPSG:3857 aproximadamente em `(-4287422,25, -1456413,48)` e `(-4287420,70, -1456421,39)`, com Z Blender `7,2557`. A documentação de domínio usada pelo handoff registra ETOPO1 como fonte de batimetria Mapzen/Tilezen; portanto esses valores permanecem como domínio separado. O raster está em EPSG:3857, 512 × 512 pixels, resolução aproximada de 4,7773 m e nodata declarado como `-3,4028235e38`.

## R30A.1 × R30A.2

R30A.1 não separava os domínios, mas seu fit completo é a referência numérica solicitada. Em R30A.2, o fit completo mantém todos os valores válidos no input; o fit terrestre usa somente DEM >= 0 m. O filtro robusto removeu os dois valores negativos no ajuste completo por serem outliers residuais, não por reclassificação como nodata. Por isso os parâmetros mantidos são idênticos:

| Métrica | R30A.1 completo | R30A.2 completo | R30A.2 terrestre DEM >= 0 |
|---|---:|---:|---:|
| Objetos de terreno | 1 | 1 | 1 |
| Amostras de entrada | 4.978 | 4.978 | 4.976 |
| Amostras abaixo de 0 m | não separado | 2 (0,0402%) | não aplicável |
| Amostras terrestres | não separado | 4.976 (99,9598%) | 4.976 (100% do domínio) |
| Amostras mantidas | 4.900 | 4.900 | 4.900 |
| Outliers removidos | 78 | 78 | 76 |
| Escala Z Blender/DEM | 1,0253290 | 1,0253290 | 1,0253290 |
| Offset Z Blender | -4,6316455 | -4,6316455 | -4,6316455 |
| RMS | 9,2106683 | 9,2106683 | 9,2106683 |
| Mediana absoluta | 5,2179134 | 5,2179134 | 5,2179134 |
| Máximo residual | 29,3265740 | 29,3265740 | 29,3265740 |
| Razão vertical/horizontal | 1,0568512 | 1,0568512 | 1,0568512 |
| Quality | `insufficient` | `insufficient` | `insufficient` |

Conclusão deste quadro: a hipótese “a batimetria misturada é a causa dominante do fit vertical ruim” não foi confirmada. O fit terrestre não melhora porque os dois pontos negativos já eram rejeitados pelo robust fit e não controlavam a regressão. O ajuste continua insuficiente e não autoriza escala/offset global.

## Inspeção espacial no Blender

As dez células abaixo são as primeiras de `land_spatial_grid.review_cells`, ordenadas por mediana absoluta do resíduo, com o fit XY R30A.2. Os bounds permanecem em EPSG:3857; o centro convertido para Blender foi usado somente para localizar objetos e coleções na cena aberta pelo MCP.

| grid index | bounds EPSG:3857 | amostras | faixa DEM (m) | Z Blender mediano (m) | resíduo mediano abs. (m) | região da cena | provável causa comprovável | confiança |
|---|---|---:|---:|---:|---:|---|---|---|
| `[-85748,-29139]` | -4287400,-1456950 a -4287350,-1456900 | 16 | 26,164–66,458 | 11,664 | 26,456 | Cidade Baixa junto à base da escarpa; waterfront/cais, não Praça Cairu | Escarpa abrupta e mistura espacial de cotas no DEM; a cena tem `Encosta \| fechamento lateral`/`coroamento` e a malha local varia de 7,256 a 64,102 m | média-alta |
| `[-85751,-29142]` | -4287550,-1457100 a -4287500,-1457050 | 11 | 21,286–32,376 | 46,702 | 23,182 | Cidade Baixa/waterfront, Av. Lafayete Coutinho e Rua da Conceição da Praia, junto ao cais | Plataforma/colisão histórica do MVP: vértices locais do objeto de colisão variam de 6,566 a 52,515 m, mediana 47,142 m, enquanto as vias baixas da cena estão em torno de 11 m | alta |
| `[-85741,-29140]` | -4287050,-1457000 a -4287000,-1456950 | 10 | 43,748–51,666 | 66,117 | 23,161 | Cidade Alta, quadras do Corpo de Bombeiros/Sindacs | Platô de Cidade Alta adaptado ao MVP: malha local quase plana em 65,231–66,216 m e edifícios OSM próximos com bases em torno de 66 m; não é indício isolado de erro XY | alta |
| `[-85740,-29140]` | -4287000,-1457000 a -4286950,-1456950 | 20 | 43,501–45,295 | 62,674 | 21,932 | Cidade Alta, mesma faixa do Corpo de Bombeiros/Sindacs | Plataforma/colisão do platô: malha local 61,425–66,121 m, com baixa variação intra-célula e cota muito acima do DEM local | alta |
| `[-85744,-29126]` | -4287200,-1456300 a -4287150,-1456250 | 10 | 28,022–33,838 | 7,256 | 21,119 | Cidade Baixa waterfront, Terminal de Cruzeiros/Avenidas da França e Estados Unidos | Piso/plataforma baixa do MVP: todos os vértices locais estão em 7,256 m e as bases dos edifícios próximos estão em torno de 7,1 m; a divergência restante é vertical do DEM na planície construída ou do piso histórico | média-alta |
| `[-85739,-29140]` | -4286950,-1457000 a -4286900,-1456950 | 32 | 44,000–45,240 | 61,460 | 20,742 | Cidade Alta, quadras altas próximas ao limite da escarpa | Cota alta fixada na superfície de colisão do MVP: malha local 57,223–64,079 m, mediana 61,441 m, em sequência com as células do platô | alta |
| `[-85739,-29139]` | -4286950,-1456950 a -4286900,-1456900 | 9 | 44,611–47,249 | 62,539 | 20,315 | Cidade Alta, continuidade do platô | Alteração histórica/plataforma do MVP, evidenciada pela malha local 59,529–65,223 m e pela continuidade espacial do resíduo positivo | alta |
| `[-85740,-29139]` | -4287000,-1456950 a -4286950,-1456900 | 12 | 46,693–53,220 | 65,660 | 20,013 | Cidade Alta, entorno de Solar Jonathas Abbot | Platô de colisão adaptado: malha local 64,029–66,216 m, alinhada às bases de edifícios da Cidade Alta, mas acima do DEM amostrado | alta |
| `[-85741,-29139]` | -4287050,-1456950 a -4287000,-1456900 | 11 | 45,394–53,602 | 66,209 | 18,975 | Cidade Alta, borda do platô próxima à escarpa | Platô superior histórico do MVP; malha local quase constante em 66,153–66,216 m, enquanto o DEM varia 45,394–53,602 m | alta |
| `[-85743,-29142]` | -4287150,-1457100 a -4287100,-1457050 | 13 | 48,968–56,252 | 65,767 | 18,898 | Cidade Alta, quadras altas junto à ladeira/encosta | Platô de colisão adaptado; malha local 64,247–66,216 m e edifícios próximos em aproximadamente 64–75 m. A proximidade de referências de ladeira impede atribuir o resíduo apenas ao DEM | média-alta |

Nenhuma das dez células corresponde ao marcador Blender `R27 | PRACA CAIRU` (aprox. `[-126,49,154,29]`) ou `R27 | MERCADO MODELO` (aprox. `[-148,95,172,78]`). As duas primeiras são waterfront/Cidade Baixa, mas não o footprint do Mercado Modelo nem a Praça Cairu. O controle do Mercado Modelo permanece intocado; seu footprint real continua com offset aproximado de `1,878 m` e o falso binding já eliminado não foi reintroduzido.

## Evidência da natureza da malha

No Blender MCP, o objeto amostrado foi confirmado como único objeto `MVP | terreno corrigido | colisão estática`, na coleção `19 MVP | terreno DEM e acessos corrigidos`, com 547.464 vértices e 1.082.745 polígonos. As propriedades existentes, apenas lidas, registram:

- `game_role: static_terrain_collision`;
- `source: Aleph DEM + OSM; patamares adaptados aos pisos do esboço`;
- `surface_method: ... DEM filtrado na Cidade Alta + planície baixa ... patamares fixos ...`;
- `accuracy: Traçado OSM; altimetria filtrada e corrigida para MVP ... não levantamento`;
- `cairu_grade: Patamar z10.82m ... cota inferida, não levantamento`.

Isso comprova que parte dos resíduos altos está sobre uma superfície de colisão/plataforma ajustada para o MVP e não sobre uma malha topográfica independente de levantamento. Também comprova por que não é seguro aplicar um offset local só com este fit: as células reúnem escarpa, platô alto e plataformas baixas de naturezas semânticas diferentes.

## Investigação das causas

- **Batimetria misturada anteriormente:** não explica o RMS nesta rodada. Os dois negativos foram preservados e separados; já eram outliers do robust fit. Não houve alteração do DEM.
- **Limitação/resolução do DEM:** é plausível nas transições de waterfront e escarpa, especialmente na célula `[-85748,-29139]`, onde 50 m contêm DEM de 26 a 66 m. A resolução do raster é 4,777 m, mas o produto não representa necessariamente a quebra abrupta da escarpa nem o piso construído com fidelidade vertical local.
- **Escarpa abrupta não representada bem:** evidenciada pela célula junto aos objetos `Encosta` e pela coexistência de amostras baixas e altas na mesma célula. A causa está localizada, mas a referência DEM isolada não distingue erro de representação da escarpa de alteração histórica do MVP.
- **Alteração histórica/plataforma/colisão do MVP:** fortemente evidenciada nas sequências de células da Cidade Alta e waterfront baixo. A malha tem platôs quase constantes em aproximadamente 7,256 m e 61–66 m, além de propriedades que declaram patamares fixos, filtragem e adaptação aos pisos do esboço.
- **Erro do fit XY:** permanece possível em nível residual, pois o fit XY é `candidate`, não `verified` (escala `0,9701735`, rotação `-0,050990°`, RMS `4,168632`). Entretanto, a repetição de platôs sem deslocamento progressivo e a correspondência com coleções/objetos nomeados tornam um erro XY global insuficiente para explicar sozinho as células críticas.
- **Mercado Modelo:** não foi investigado como alvo de correção. O footprint real e o offset de controle permanecem preservados.

## Decisão

Os dados ainda não são suficientes para autorizar a primeira correção geométrica local. Existe sinal espacial localizado, mas as regiões críticas misturam superfície de colisão deliberadamente adaptada, Cidade Alta, base de escarpa e waterfront; o DEM sozinho não fornece referência suficiente para separar, em cada local, limitação de resolução de alteração histórica do MVP. A próxima investigação deve aprofundar a validação vertical regional com uma referência de elevação terrestre independente e controlar separadamente as plataformas fixas, antes de qualquer alteração de vértices.

**Conclusão objetiva: os dados ainda não são suficientes e é necessário aprofundar o problema vertical do terreno/plataformas do MVP e da escarpa.**
