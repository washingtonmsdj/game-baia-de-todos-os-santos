# R30A — Alinhamento Estrutural do MVP

## Objetivo

Tornar o recorte **Cidade Alta → Elevador Lacerda → Praça Cairu → Mercado Modelo → cais** estruturalmente coerente com os dados geográficos antes do passe visual da R30B.

Esta revisão não existe para decorar a cena. Ela existe para corrigir:

- origem/escala/rotação do mundo;
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

## Etapa A — fit geográfico

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

`docs/reports/blender/georef_fit.json`

Nenhum offset global manual pode substituir esse passo.

## Etapa B — referência estrutural OSM

Gerar:

`artifacts/world/mvp-centro-lacerda/osm_structure.json`

Depois transformar para:

`docs/reports/blender/structural_reference.json`

Importar no Blender em:

`SOURCE_GEOREF | STRUCTURAL_REFERENCE`

A camada importada é somente referência e nunca é exportada como asset final.

## Etapa C — auditoria da cena existente

Executar:

```bash
blender cena.blend --background \
  --python tools/blender/audit_structural_scene.py \
  -- --output docs/reports/blender/structural_scene_audit.json
```

Revisar especialmente:

- bounds do terreno;
- Z mínimo/máximo;
- escalas não uniformes;
- vias/calçadas identificadas;
- água/waterfront;
- contenções/escadas;
- footprints/proxies de edifícios.

## Etapa D — terreno

Conferir em ordem:

1. bounds do DEM contra a área do Blender;
2. CRS e pixel size;
3. Cidade Alta e Cidade Baixa;
4. escarpa entre os dois níveis;
5. regiões em que o DEM bruto gerou cliff/spike;
6. interfaces com acessos do Elevador;
7. Praça Cairu e entorno do Mercado;
8. aproximação do cais.

Qualquer correção local deve existir como geometria/revisão derivada e documentada. Não modificar silenciosamente o raster-fonte.

## Etapa E — ruas e áreas pedonais

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

## Etapa F — coastline, cais e água

Comparar separadamente:

- `REF_COASTLINE`;
- `REF_WATERFRONT`;
- geometria autoral do cais;
- superfície visual da água.

Corrigir primeiro o limite terra/água e estruturas rígidas. O shader/mesh visual da Baía deve se adaptar ao contorno, não o contrário.

## Etapa G — footprints

Usar `REF_BUILDINGS` para revisar implantação horizontal.

Nesta revisão:

- corrigir posição/rotação/footprint quando a divergência estiver comprovada;
- não reconstruir fachada por falta de foto;
- preservar interiores e sistemas funcionais;
- Hero assets exigem revisão conservadora.

## Entregáveis

- `source_summary.json`;
- `dem_audit.json`;
- `georef_hints.json`;
- `georef_fit.json`;
- `osm_structure.json` local/artifact;
- `structural_reference.json`;
- `structural_scene_audit.json` antes e depois;
- `.blend` revisado salvo como nova revisão;
- relatório R30A com divergências corrigidas e pendentes.

## Critério de conclusão

R30A termina quando:

- fit geográfico foi revisado e tem qualidade suficiente;
- sobreposição estrutural foi inspecionada no Blender;
- corredor principal não apresenta desalinhamentos grandes de planta;
- coastline/cais do MVP são coerentes com a referência disponível;
- terreno não possui artefatos críticos escondidos por geometria decorativa;
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
