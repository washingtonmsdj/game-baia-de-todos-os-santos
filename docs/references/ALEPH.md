# Aleph — referência e integração

## Registro da fonte

- **Projeto:** Aleph
- **Repositório:** `Belluxx/Aleph`
- **URL:** https://github.com/Belluxx/Aleph
- **Revisão analisada:** `d24c61507481a91a0dd6afac4f97626a4e5ea780`
- **Data da revisão analisada:** 25/09/2026
- **Licença do software:** MIT
- **Função no Bay of All Saints:** aquisição, organização e proveniência de dados geográficos de referência.

Este registro existe para que a origem técnica usada no MVP não se perca quando o projeto mudar de máquina, agente ou ferramenta.

## O que o Aleph oferece de útil

O Aleph consegue capturar uma área retangular e organizar, em uma mesma execução:

- dados OpenStreetMap;
- terreno/elevação em GeoTIFF Float32;
- imagens de satélite;
- fotos Street View;
- GeoJSONs auxiliares;
- `manifest.json` com limites, opções, fontes, datas e estado da captura.

Para o Bay of All Saints, a parte mais importante é a capacidade de transformar uma seleção geográfica em um **pacote reproduzível**, em vez de depender de downloads manuais sem histórico.

## Integração recomendada

Não copiar o Aleph inteiro para este repositório.

Preferir utilizá-lo como ferramenta externa versionada/pinada. O fluxo recomendado é:

1. instalar/clonar Aleph em ambiente de aquisição;
2. registrar o commit utilizado;
3. executar a captura da área necessária;
4. manter o `manifest.json` original junto aos dados de referência locais;
5. executar `tools/aleph/inspect_capture.py` deste repositório;
6. gerar um relatório de proveniência para o Codex/Blender;
7. importar para o Blender apenas as fontes aprovadas para aquele uso.

Isso evita acoplar o pipeline do jogo à implementação interna do Aleph e facilita atualizar ou substituir o coletor no futuro.

## Componentes que podemos aproveitar imediatamente

### 1. OpenStreetMap / Geofabrik

**Uso recomendado:** SIM.

Aplicações no projeto:

- footprint inicial de edifícios;
- eixos e classificação de ruas;
- POIs;
- implantação urbana de referência;
- apoio à expansão de Salvador por bairros;
- geração de proxy/blockout, nunca substituindo revisão artística/manual dos hero assets.

O Aleph baixa regiões OSM da Geofabrik e exporta `map.osm` preservando tags e topologia relevantes.

**Licença dos dados:** ODbL. Manter atribuição ao OpenStreetMap e cumprir as condições aplicáveis ao uso/distribuição de dados derivados.

### 2. Terreno GeoTIFF

**Uso recomendado:** SIM, mas com gate de proveniência/licença antes de distribuição.

O Aleph produz `terrain.tif` com alturas Float32 em metros, EPSG:3857, sem reamostragem no merge. Isso é tecnicamente muito útil para:

- blockout de relevo;
- conferência das diferenças Cidade Alta/Cidade Baixa;
- expansão territorial;
- comparação com o terreno já existente;
- criação de proxies de terreno/chunks.

A própria documentação do Aleph alerta que resolução, data, precisão e referência vertical variam por fonte; zoom maior não garante maior detalhe.

**Regra do projeto:** terreno capturado via Aleph é referência técnica/MVP até que a licença e a fonte exata do dataset de elevação usado naquela captura tenham sido verificadas e registradas.

### 3. `manifest.json`

**Uso recomendado:** SIM, prioritário.

Esse é um dos ativos mais valiosos do Aleph para nosso pipeline porque registra:

- `bounds`;
- opções da captura;
- zoom de satélite/terreno;
- fontes selecionadas;
- estágios;
- arquivos e URLs de origem;
- datas de captura;
- estado da execução.

O manifesto deve ser preservado como evidência de proveniência mesmo quando os arquivos pesados não forem versionados no GitHub.

### 4. GeoJSON e grades Web Mercator

**Uso recomendado:** SIM.

A lógica de grade/tiles e os GeoJSONs podem ajudar a:

- manter correspondência entre mundo real e Blender;
- criar chunks espaciais;
- planejar streaming futuro;
- localizar imagens/referências por área;
- reconstruir uma captura posteriormente.

### 5. Imagens de satélite do Google

**Uso de produção:** NÃO, por padrão.

A implementação analisada do Aleph baixa tiles de satélite de endpoint do Google. O próprio Aleph declara uso de APIs não documentadas. Os termos atuais do Google Maps restringem scraping/download em massa e criação de conteúdo derivado do conteúdo do Google Maps.

Portanto, no Bay of All Saints:

- não versionar essas imagens como assets do jogo;
- não convertê-las em texturas distribuídas;
- não modelar/digitalizar geometria de produção com base nelas como fonte principal;
- não tratar o fato de o Aleph conseguir baixá-las como autorização de uso.

Se uma fonte de imagem aérea com licença apropriada for adotada depois, ela deve entrar no registro de proveniência separadamente.

### 6. Street View do Google

**Uso de produção:** NÃO, por padrão.

Pelo mesmo motivo acima, capturas Street View feitas via Aleph não devem entrar no repositório como assets distribuíveis nem servir como fonte derivativa automática do conteúdo final sem revisão jurídica/licença adequada.

Para referência de arquitetura/fachadas, preferir:

- fotografias próprias;
- acervos públicos com licença compatível;
- dados de órgãos públicos;
- imagens explicitamente licenciadas para o uso pretendido.

## Relação com a cena atual

A auditoria histórica do `.blend` do MVP já registrava terreno baseado em **Aleph DEM / EPSG:3857 + OSM**.

Esse fato deve continuar preservado como proveniência histórica. Ele **não transforma o terreno atual em levantamento certificado** e não elimina a necessidade de confirmar a licença/fonte exata do DEM antes de uma distribuição comercial.

## Próximas integrações previstas

### A. Inspector de captura

`tools/aleph/inspect_capture.py` valida a estrutura básica de uma pasta de captura e produz um resumo de proveniência sem copiar os arquivos pesados para o repositório.

### B. Registro por área

Cada futura expansão territorial deve possuir um registro com:

- nome da área;
- bounds WGS84;
- commit do Aleph;
- opções usadas;
- data;
- fontes efetivamente utilizadas;
- licença/status de uso de cada fonte;
- hash do manifesto;
- responsável/automação que importou a referência.

### C. Bridge para Blender

Depois de termos uma captura real validada, criar um bridge específico para:

- origem local do mundo;
- conversão WGS84/EPSG:3857 → coordenadas do Blender;
- chunks;
- importação de OSM como `PROXY_OSM`;
- terreno como `REFERENCE_TERRAIN`;
- metadados de fonte em custom properties.

Esse bridge não deve importar automaticamente fontes marcadas como `PROIBIDO_PRODUCAO`.

## Política de atualização

O Aleph é um projeto externo e pode mudar. Antes de atualizar o commit pinado:

1. revisar changelog/commits;
2. verificar alterações no formato do `manifest.json`;
3. verificar fontes/endpoints de dados;
4. revisar termos/licenças quando a origem dos dados mudar;
5. atualizar este documento e os testes do inspector.
