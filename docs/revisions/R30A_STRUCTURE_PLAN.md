# R30A — Alinhamento Estrutural do MVP

## Objetivo

Tornar o recorte **Cidade Alta → Elevador Lacerda → Praça Cairu → Mercado Modelo → cais** estruturalmente coerente com os dados geográficos antes do passe visual da R30B.

Esta revisão não existe para decorar a cena. Ela existe para corrigir:

- origem/escala/rotação do mundo;
- relação vertical DEM ↔ Blender;
- terreno e escarpa;
- eixos viários;
- cruzamentos e conexões pedonais;
- coastline e cais;
- footprints/implantação;
- interfaces entre terreno, rua, praça e edifícios.

## Gate de entrada

A R30A só começa depois de:

- R29 aplicada/validada;
- captura Aleph histórica procurada;
- `map.osm` e `terrain.tif` preservados quando encontrados;
- `source_summary.json` gerado;
- `dem_audit.json` gerado;
- `georef_hints.json` exportado da cena.

Se o `map.osm` histórico não for recuperado, registrar o bloqueio e não fingir que outro recorte OSM é idêntico ao usado na cena.

## Etapa A — fit geográfico XY

Executar o solver e revisar:

- quantidade de anchors;
- escala;
- rotação;
- origem WGS84/EPSG:3857;
- RMS;
- residual máximo;
- outliers removidos.

Mercado Modelo e Palácio Rio Branco devem ser conferidos quando disponíveis.

Resultado esperado:

`georef_fit.json`

Nenhum offset global manual pode substituir esse passo.

## Etapa B — estrutura e topologia OSM

Gerar `osm_structure.json` e `osm_topology_audit.json` pelo pipeline estrutural.

Antes de usar a referência no Blender, revisar em ordem:

1. node refs ausentes;
2. footprints `building=*` não fechados;
3. endpoints internos de coastline;
4. near-misses entre endpoints distintos;
5. endpoints internos da rede de transporte;
6. componentes desconectados inesperados;
7. possíveis separações de nível por `bridge`, `tunnel` ou `layer`.

Não transformar uma flag em correção automática. Rua sem saída, limite do recorte, píer, cliff, muro ou ponte podem terminar legitimamente.

Consultar `docs/OSM_TOPOLOGY_QA.md`.

## Etapa C — referência estrutural Blender

Transformar a estrutura validada para `structural_reference.json` e importar em:

`SOURCE_GEOREF | STRUCTURAL_REFERENCE`

A camada importada é somente referência e nunca é exportada como asset final.

Quando existirem no OSM, revisar também:

```text
REF_CLIFFS
REF_EARTHWORKS
REF_RETAINING_WALLS
```

Essas camadas ajudam a entender a escarpa e as transições de nível sem suavizar o relevo arbitrariamente.

## Etapa D — auditoria e alinhamento da cena existente

Executar:

```bash
blender cena.blend --background \
  --python tools/blender/audit_structural_scene.py \
  -- --output docs/reports/blender/structural_scene_audit_before.json
```

A auditoria atual registra OSM IDs explícitos e exclui `SOURCE_GEOREF`.

Depois comparar entidades com o mesmo OSM ID:

```bash
python tools/world/compare_scene_reference_alignment.py \
  --scene-audit docs/reports/blender/structural_scene_audit_before.json \
  --reference artifacts/structural-pipeline/mvp-centro-lacerda/structural_reference.json \
  --output docs/reports/blender/scene_reference_alignment.json
```

Revisar primeiro `center_offset_review`. `bounds_size_review` é triagem, pois AABB pode variar com rotação, extrusão ou asset dividido em partes.

Priorizar quando presentes:

- Mercado Modelo — way `59392558`;
- Palácio Rio Branco — way `402383814`;
- outros OSM IDs explícitos distribuídos pelo recorte.

Não criar correspondência por semelhança de nome. Não mover objeto apenas porque o AABB divergiu.

Consultar `docs/SCENE_REFERENCE_ALIGNMENT_QA.md`.

## Etapa E — terreno e relação vertical

Conferir em ordem:

1. bounds do DEM contra a área do Blender;
2. CRS e pixel size;
3. relação vertical DEM ↔ Z Blender;
4. Cidade Alta e Cidade Baixa;
5. escarpa entre os dois níveis;
6. regiões em que o DEM bruto gerou cliff/spike;
7. interfaces com acessos do Elevador;
8. Praça Cairu e entorno do Mercado;
9. aproximação do cais.

Qualquer correção local deve existir como geometria/revisão derivada e documentada. Não modificar silenciosamente o raster-fonte.

### E0 — fit vertical DEM ↔ Blender

Exportar amostras da mesh de terreno:

```bash
blender cena.blend --background \
  --python tools/blender/export_terrain_samples.py \
  -- --output docs/reports/blender/terrain_samples.json
```

Quando a seleção automática capturar objetos indevidos, repetir com `--include-regex` restritivo.

Calcular:

```bash
python tools/terrain/fit_dem_blender_vertical.py \
  --samples docs/reports/blender/terrain_samples.json \
  --fit artifacts/structural-pipeline/mvp-centro-lacerda/georef_fit.json \
  --dem CAMINHO/terrain.tif \
  --output docs/reports/blender/terrain_vertical_fit.json
```

Revisar escala vertical, offset, relação com escala XY, RMS, resíduos por objeto e maiores outliers.

Não aplicar reescala Z ou offset global automaticamente. Outliers podem ser correções locais legítimas ou objetos históricos que não representam a superfície principal.

Consultar `docs/DEM_BLENDER_VERTICAL_FIT.md`.

### E1 — QA do DEM sob ruas

Quando `rasterio` estiver disponível, executar o QA dos perfis viários.

A `review_queue` serve para localizar:

- `nodata`;
- saltos verticais entre amostras próximas;
- grades muito altas para revisão.

Os thresholds são heurísticas. Um trecho marcado pode ser uma ladeira, escarpa, muro ou estrutura real. Cada caso deve ser classificado antes de correção.

Classes de decisão recomendadas:

```text
real_feature
dem_artifact
alignment_issue
source_uncertain
```

Não aplicar smoothing global por causa de flags locais.

## Etapa F — ruas e áreas pedonais

Comparar a geometria atual contra `REF_ROADS`, `REF_PEDESTRIAN` e `REF_STEPS`.

Prioridade:

1. posição do eixo;
2. continuidade;
3. cruzamentos;
4. relação com relevo;
5. largura **somente quando houver dado confiável**;
6. calçadas;
7. travessias;
8. escadarias.

Não inventar largura pela classe OSM. Se `width=*`/medida confiável não existir, preservar a incerteza e usar a referência apenas para eixo/implantação.

## Etapa G — coastline, cais e água

Comparar separadamente:

- `REF_COASTLINE`;
- `REF_WATERFRONT`;
- geometria autoral do cais;
- superfície visual da água.

Corrigir primeiro o limite terra/água e estruturas rígidas. O shader/mesh visual da Baía deve se adaptar ao contorno, não o contrário.

Uma coastline interrompida internamente no `osm_topology_audit.json` precisa ser entendida antes de ser usada como referência de correção.

## Etapa H — footprints

Usar `REF_BUILDINGS` para revisar implantação horizontal.

Nesta revisão:

- corrigir posição/rotação/footprint quando a divergência estiver comprovada;
- usar `scene_reference_alignment.json` como triagem para OSM IDs explícitos;
- não usar building way aberto como footprint confiável sem revisão;
- não reconstruir fachada por falta de foto;
- preservar interiores e sistemas funcionais;
- Hero assets exigem revisão conservadora.

## Entregáveis

- `source_summary.json`;
- `dem_audit.json`;
- `terrain_samples.json`;
- `terrain_vertical_fit.json`;
- `dem_road_profiles.json` quando aplicável;
- `georef_hints.json`;
- `georef_fit.json`;
- `osm_structure.json`;
- `osm_topology_audit.json`;
- `structural_reference.json`;
- `structural_scene_audit_before.json`;
- `scene_reference_alignment.json`;
- `structural_scene_audit_after.json`;
- `.blend` revisado salvo como nova revisão;
- relatório R30A com divergências corrigidas e pendentes.

## Critério de conclusão

R30A termina quando:

- fit XY foi revisado e tem qualidade suficiente;
- fit vertical foi revisado ou sua insuficiência foi explicitamente registrada;
- problemas topológicos críticos do recorte foram classificados;
- OSM IDs explícitos prioritários foram comparados contra a referência;
- offsets significativos foram classificados antes de qualquer movimento;
- sobreposição estrutural foi inspecionada no Blender;
- corredor principal não apresenta desalinhamentos grandes de planta;
- coastline/cais do MVP são coerentes com a referência disponível;
- terreno não possui artefatos críticos escondidos por geometria decorativa;
- flags críticas do perfil DEM-vias foram classificadas;
- Praça Cairu se conecta corretamente a vias, Elevador, Mercado e waterfront;
- footprints dos marcos principais foram auditados;
- toda aproximação remanescente está registrada.

## Gate para R30B

Somente depois da R30A concluída avançar para:

- mobiliário;
- vegetação;
- materiais finos;
- iluminação de apresentação;
- composição visual;
- densidade urbana decorativa.

A R30B não deve reabrir ou mascarar problemas que pertencem à R30A.
