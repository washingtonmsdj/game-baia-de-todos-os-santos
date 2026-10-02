# Área `mvp-centro-lacerda`

## Objetivo

Concentrar o primeiro vertical slice de **Bay of All Saints** no corredor Cidade Alta → Elevador Lacerda → Cidade Baixa → Praça Cairu → Mercado Modelo com fidelidade espacial e visual alta.

Os arquivos canônicos desta área são:

- `production.json` — SSOT executável de revisão ativa, exportação, assets e runtime;
  fluxo em `docs/MVP_PRODUCTION_PIPELINE.md`;
- `blender-revisions.json` — ponteiro exclusivo da candidata de modelagem e sua
  cadeia de origem; não escolher arquivo por número, data ou janela aberta;

- `area.json` — geografia, estado e captura Aleph;
- `locations.json` — locais/assets que precisam existir e seu nível de fidelidade;
- `media-manifest.json` — referências visuais catalogadas e sua proveniência.

## Ordem de referência/modelagem

Prioridade atual:

1. **Elevador Lacerda** — Hero A / P5;
2. **Mercado Modelo** — Hero A / P5;
3. **Praça Cairu** — espaço urbano A / P5;
4. **corredor viário/pedonal da Cidade Baixa** — A / P5;
5. **cais e borda marítima da Praça Cairu** — A / P5;
6. **Palácio Rio Branco** — Hero A / P4;
7. **Praça Tomé de Sousa** — A / P4;
8. **superfície da Baía no recorte** — B / P4.

## Fila de captura visual

O comando abaixo mostra, por prioridade, as vistas ainda ausentes:

```bash
python tools/references/reference_gaps.py --area mvp-centro-lacerda
```

No estado inicial, o manifesto de mídia está vazio de propósito. Não foram criadas referências fictícias.

## Estrutura local recomendada

Exemplo fora do Git:

```text
world-reference/
  mvp-centro-lacerda/
    media/
      elevador-lacerda/
      mercado-modelo/
      palacio-rio-branco/
      praca-cairu/
      praca-tome-de-sousa/
      corredor-cidade-baixa/
      cais-praca-cairu/
      baia-agua-mvp/
```

Uma fotografia pode então ser registrada sem copiar o binário para o Git:

```bash
python tools/references/register_media.py \
  --area mvp-centro-lacerda \
  --location elevador-lacerda \
  --file world-reference/mvp-centro-lacerda/media/elevador-lacerda/front_01.jpg \
  --media-root world-reference \
  --view front \
  --source-type own_photo \
  --usage-class PRODUCAO_APROVADA \
  --source-name "Levantamento próprio" \
  --license-status verified \
  --license "Direitos do projeto"
```

No Windows o comando pode ser executado em uma única linha.

## Regras para o Codex

Antes de alterar um local:

1. ler sua entrada em `locations.json`;
2. executar `reference_gaps.py`;
3. usar somente mídia associada ao mesmo `location_id`;
4. respeitar `usage_class` e proveniência;
5. não marcar `approved` enquanto vistas obrigatórias estiverem ausentes;
6. para classe A, gerar capturas comparáveis do Blender antes/depois;
7. atualizar estado e notas somente depois da validação visual.

## Geografia

Os bounds WGS84 permanecem nulos até a recuperação da captura Aleph original ou uma nova fonte validada. Isso é intencional: **não preencher coordenadas por aproximação manual**.

A transformação mundo real → Blender permanece `candidate` até o fechamento por múltiplos anchors e erro residual registrado.

## Ruas e borda marítima

Ruas, calçadas, cais e coastline são estrutura, não decoração. Correções dessas camadas devem preceder props e embelezamento quando houver conflito.

A superfície visual da água pode evoluir artisticamente, mas a posição do limite terra/água deve vir de referência geográfica validada.
