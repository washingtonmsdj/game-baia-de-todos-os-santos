# Proveniência de Dados Geográficos

## Objetivo

Bay of All Saints deve conseguir responder, para qualquer dado geográfico usado na construção do mundo:

- de onde veio;
- quando foi obtido;
- com qual ferramenta/versão;
- em qual sistema de coordenadas;
- para que finalidade pode ser usado;
- quais obrigações de atribuição/licença existem;
- se o dado é apenas referência, proxy de MVP ou asset aprovado para produção.

A ausência dessas respostas deve ser tratada como bloqueio para distribuição, não como autorização implícita.

## Classes de uso

### `PRODUCAO_APROVADA`

A fonte possui licença/termos compatíveis com o uso pretendido e as obrigações estão registradas.

### `PRODUCAO_COM_ATRIBUICAO`

Uso permitido desde que atribuição e demais condições sejam cumpridas. Exemplo atual: dados OpenStreetMap sob ODbL, sujeitos à análise do uso concreto.

### `REFERENCIA_INTERNA`

Pode orientar validação técnica/interna, mas não deve ser empacotada como asset final nem considerada automaticamente apta para derivação de conteúdo distribuído.

### `PENDENTE_VERIFICACAO`

Fonte ou licença ainda não foi confirmada o suficiente para distribuição. Pode existir no MVP como legado/proxy, mas precisa ser substituída, confirmada ou isolada antes do release.

### `PROIBIDO_PRODUCAO`

Não deve ser incorporada ao conteúdo distribuído nem usada como fonte derivativa de produção dentro do pipeline definido neste projeto.

## Registro mínimo por captura

Cada captura/fonte territorial deve registrar:

```text
area_id
nome_area
bounds_wgs84
ferramenta
ferramenta_commit
capturado_em
sistema_coordenadas
fontes
licencas
classe_uso
manifest_sha256
observacoes
```

Quando uma captura for feita pelo Aleph, preservar o `manifest.json` original e gerar um resumo com `tools/aleph/inspect_capture.py`.

## Fontes conhecidas

### OpenStreetMap / Geofabrik

- **Uso inicial:** `PRODUCAO_COM_ATRIBUICAO`
- **Licença:** ODbL
- **Aplicações:** vias, footprints, POIs, implantação urbana, proxies e apoio à construção do mapa.
- **Obrigação mínima:** atribuir OpenStreetMap e deixar clara a disponibilidade dos dados sob ODbL; avaliar obrigações adicionais para bancos derivados/distribuição concreta.
- **Regra:** OSM não substitui levantamento/arte manual de hero assets.

### Aleph — software

- **Uso:** `PRODUCAO_APROVADA` como ferramenta de pipeline, respeitando a licença MIT.
- **Importante:** a licença MIT do software Aleph não concede automaticamente direitos sobre dados obtidos de serviços externos.
- **Registro detalhado:** `docs/references/ALEPH.md`.

### Elevação obtida pelo Aleph

- **Uso inicial:** `PENDENTE_VERIFICACAO`
- **Formato observado:** GeoTIFF Float32, metros, EPSG:3857.
- **Aplicações atuais:** referência de relevo, blockout e validação de diferenças de altitude.
- **Regra:** antes de distribuição comercial, registrar a origem/licença efetiva do dataset de elevação usado na captura.

### Google Satellite obtido pelo Aleph

- **Uso:** `PROIBIDO_PRODUCAO`
- **Motivo operacional:** a implementação analisada usa endpoint Google e o próprio Aleph informa uso de APIs não documentadas; os termos atuais do Google Maps restringem scraping/download em massa e criação de conteúdo derivado.
- **Regra:** não versionar como textura do jogo, não redistribuir e não usar como base automática para modelagem de produção.

### Google Street View obtido pelo Aleph

- **Uso:** `PROIBIDO_PRODUCAO`
- **Regra:** não incorporar imagens ao jogo/repositório de assets e não usar como base derivativa automática de conteúdo de produção. Preferir fotografia própria ou fontes explicitamente licenciadas.

## Estado legado do MVP

A cena Blender analisada registra uso histórico de **Aleph DEM EPSG:3857 + OSM**.

Até que a origem/licença do DEM específico seja confirmada:

- manter o terreno como aproximação de MVP;
- não declará-lo levantamento certificado;
- não assumir que pode ser redistribuído comercialmente apenas porque foi obtido via Aleph;
- manter o OSM identificado separadamente dos hero assets e da geometria autoral.

## Regras para Codex/Blender

Ao importar dados geográficos:

1. preservar a origem em custom properties ou relatório da revisão;
2. nunca converter silenciosamente `REFERENCIA_INTERNA`, `PENDENTE_VERIFICACAO` ou `PROIBIDO_PRODUCAO` em asset de produção;
3. manter proxies OSM em coleção separada (`PROXY_OSM` ou equivalente);
4. manter terreno de referência separado do terreno artístico/final quando houver dúvida de licença ou precisão;
5. registrar transformação de coordenadas e origem local usada no Blender;
6. gerar relatório antes/depois de qualquer substituição de fonte geográfica.

## Créditos e release

Antes de qualquer build público/comercial, criar uma revisão específica de créditos/licenças contendo pelo menos:

- atribuição OpenStreetMap;
- licença ODbL e escopo do dado utilizado;
- licenças de datasets de elevação/ortofoto adotados;
- fontes de fotografias/referências que precisem atribuição;
- avisos de software de terceiros incorporado/distribuído.

Este documento é uma política técnica de proveniência, não substitui revisão jurídica para o release comercial.
