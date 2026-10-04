# Aquisição Territorial para Expansão de Salvador

## Objetivo

Criar um processo repetível para expandir **Bay of All Saints** do vertical slice do Elevador Lacerda para Salvador inteira sem perder:

- localização;
- escala;
- origem dos dados;
- histórico de captura;
- licença/status de uso;
- relação entre áreas adjacentes.

## Princípio

Cada expansão territorial deve começar como **dados de referência registrados**, e não como importação solta no Blender.

A unidade mínima é uma `area_id`.

Exemplos de IDs:

```text
mvp-centro-lacerda
centro-historico
comercio
barra
rio-vermelho
liberdade
suburbio-ferroviario
pituba
itapua
cajazeiras
```

Os IDs não definem a ordem final de produção e podem representar subáreas menores quando necessário.

## Captura padrão com Aleph

Para aquisição inicial, preferir **somente OSM + terreno**:

```bash
alephgeo capture create \
  --bbox SOUTH WEST NORTH EAST \
  --sources osm \
  -o captures
```

O modo `osm` do Aleph inclui:

- `map.osm`;
- tiles de terreno;
- `terrain.tif` após exportação completa;
- `manifest.json` com a captura.

Por padrão, **não ativar `satellite` nem `streetview`** no pipeline do projeto.

## Registro após a captura

Executar:

```bash
python tools/aleph/inspect_capture.py captures/PASTA_DA_CAPTURA \
  --output docs/reports/aleph/AREA_ID/source_summary.json
```

O relatório deve ser commitado no GitHub.

Os arquivos geográficos pesados podem permanecer fora do Git, desde que o manifesto e o caminho/armazenamento local estejam preservados no ambiente de produção.

## Estrutura recomendada de referência local

Fora do Git, uma estação de trabalho pode manter:

```text
world-source/
  mvp-centro-lacerda/
    aleph-RUN/
      manifest.json
      map.osm
      terrain.tif
      terrain/
  centro-historico/
  comercio/
  barra/
  ...
```

No Git:

```text
docs/reports/aleph/
  mvp-centro-lacerda/
    source_summary.json
  centro-historico/
    source_summary.json
  ...
```

## Overlap entre áreas

Áreas vizinhas devem possuir uma pequena faixa de sobreposição suficiente para validar continuidade de:

- vias;
- relevo;
- footprints;
- limites de quarteirão;
- marcos compartilhados.

O tamanho do overlap deve ser definido conforme densidade/escala da área, não fixado globalmente sem necessidade.

Objetos duplicados existentes na faixa de overlap não devem ser importados duas vezes para a cena final. O bridge territorial futuro deve escolher uma área dona do objeto/chunk.

## Sistema de coordenadas

O pipeline precisa separar três conceitos:

1. **WGS84** — bounds e coordenadas geográficas de captura;
2. **EPSG:3857** — terreno/grade Web Mercator usada pelo pipeline Aleph analisado;
3. **coordenadas locais do Blender/engine** — origem local do mundo jogável.

Nunca assumir que `(0,0,0)` do Blender corresponde a uma coordenada real sem um registro explícito.

Antes da expansão territorial automatizada, o Codex deve extrair/confirmar a âncora geográfica da cena atual e registrar:

```text
world_origin_wgs84
world_origin_epsg3857
world_origin_blender
rotation_true_north
meters_per_blender_unit
```

Até esse registro existir, novas áreas Aleph podem ser capturadas e catalogadas, mas não devem ser mescladas automaticamente à cena principal.

## Camadas no Blender

Quando o bridge estiver implementado, usar separação semelhante a:

```text
SOURCE_OSM
REFERENCE_TERRAIN
PROXY_OSM
ROADS_BLOCKOUT
BUILDINGS_BLOCKOUT
HERO
GAMEPLAY
FINAL_ENVIRONMENT
```

Dados-fonte não devem ser confundidos com geometria final.

## Pipeline por área

Para cada `area_id`:

1. definir bounds;
2. capturar OSM/terrain com Aleph;
3. gerar `source_summary.json`;
4. validar licença/proveniência;
5. importar como camada de referência;
6. validar alinhamento com áreas vizinhas;
7. gerar blockout;
8. definir corredores de gameplay;
9. identificar hero assets;
10. otimizar/chunkar;
11. avançar para arte final somente após o layout estar estável.

## Prioridade territorial

O mapa não deve crescer radialmente apenas porque há dados disponíveis.

A expansão deve seguir necessidades de gameplay e continuidade urbana. Depois do slice Elevador Lacerda / Praça Cairu / Mercado Modelo, corredores naturais a avaliar incluem:

- Centro Histórico / Pelourinho;
- Comércio;
- conexões costeiras próximas;
- depois corredores que liguem regiões maiores da cidade.

Barra, Rio Vermelho, Liberdade, Subúrbio, Pituba, Itapuã, Cajazeiras e outras regiões entram quando houver justificativa de produção/gameplay.

## Fontes visuais futuras

Para ortofoto, fachada e referência visual de produção, preferir fontes com licença explicitamente compatível, como:

- dados públicos municipais/estaduais/federais quando disponíveis com licença adequada;
- ortofotos abertas/licenciadas;
- levantamento fotográfico próprio;
- acervos históricos/culturais com permissão clara;
- fornecedores comerciais contratados com direitos compatíveis.

Toda nova fonte entra em `docs/references/SOURCE_REGISTRY.json` antes de ser promovida para produção.

## Resultado esperado

Com esse processo, o projeto poderá crescer para Salvador inteira sem transformar o `.blend` em uma coleção irreproduzível de imports manuais. Cada bairro manterá uma cadeia clara entre mundo real, fonte, captura, referência, blockout e geometria final.

## Vias na expansão territorial

Preservar sentidos, faixas, restrições de conversão e transporte coletivo desde a captura; pipeline estrutural agora emite grafo e referência de transporte. Ler `ROAD_TRANSPORT_PRODUCTION.md`. Não deduzir mão dupla, largura ou rota por classe/nome. Auditar costuras entre setores com IDs/camadas e manter histórico de correções da área.
