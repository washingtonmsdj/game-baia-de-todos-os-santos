# Handoff do Codex — Referências e Fidelidade Urbana

## Objetivo

Dar ao Codex um processo determinístico para melhorar a fidelidade de Salvador no Blender sem depender de imagens soltas, memória humana ou offsets locais não documentados.

## Entrada obrigatória

Antes de modelar um local do MVP:

```bash
python tools/references/validate_registry.py --root .
python tools/references/reference_gaps.py --area mvp-centro-lacerda
```

Ler:

- `world/areas/mvp-centro-lacerda/area.json`;
- `world/areas/mvp-centro-lacerda/locations.json`;
- `world/areas/mvp-centro-lacerda/media-manifest.json`;
- `docs/REFERENCE_PRODUCTION_PIPELINE.md`;
- `docs/DATA_PROVENANCE.md`.

## Seleção do trabalho

Escolher primeiro o maior `priority` ainda não aprovado e que possua referência suficiente para o tipo de alteração pretendida.

Se uma vista obrigatória estiver ausente:

- não inventar o detalhe;
- não promover o asset para `approved`;
- trabalhar apenas no que as referências suportam;
- registrar a lacuna no relatório da revisão.

## Ligação com Blender

O identificador canônico é `location_id`.

Quando o binding estiver presente, objetos/coleções relacionados devem carregar:

```text
boas_location_id = <location_id>
```

Não depender exclusivamente do nome do objeto Blender.

## Hero assets — classe A

Para Hero assets:

1. preservar o asset anterior;
2. conferir posição/orientação/escala;
3. comparar silhueta geral;
4. revisar fachadas e acessos somente com referência suficiente;
5. gerar imagens comparáveis antes/depois;
6. registrar o que foi alterado;
7. manter `manual_review_required=true` até uma revisão visual humana/validada.

## Ruas e calçadas

A ordem é:

1. eixo;
2. largura aproximada;
3. cruzamentos;
4. inclinação;
5. calçada/meio-fio;
6. travessias;
7. contenções/escadas;
8. mobiliário.

Não usar mobiliário para esconder desalinhamento estrutural.

## Coastline, cais e oceano

Separar três componentes:

- `coastline`: limite geográfico terra/água;
- `waterfront`: cais, muretas, píeres, contenções e infraestrutura;
- superfície visual da água: shader/mesh de render.

O shader pode ser artístico. Coastline e waterfront precisam de referência geográfica/visual apropriada.

## Mídia local

As imagens reais ficam fora do Git comum. Para cadastrar uma imagem:

```bash
python tools/references/register_media.py \
  --area mvp-centro-lacerda \
  --location mercado-modelo \
  --file CAMINHO_DA_IMAGEM \
  --media-root RAIZ_DO_ACERVO \
  --view front \
  --source-type own_photo \
  --usage-class PRODUCAO_APROVADA \
  --source-name "Levantamento próprio" \
  --license-status verified \
  --license "Direitos do projeto"
```

O script calcula SHA-256, impede duplicação por hash e grava somente o caminho lógico relativo ao acervo.

## Material temporário/restrito

Material catalogado como `TEMPORARIA` ou `PROIBIDO_PRODUCAO`:

- pode existir apenas para rastreabilidade/referência controlada conforme as regras de origem;
- não pode ser embutido como textura/material do jogo;
- não pode justificar promoção para `approved` quando for a única fonte relevante;
- deve poder ser removido do acervo sem quebrar a identificação do asset.

## Saída esperada de cada revisão visual

Registrar no relatório:

- `location_id` alterados;
- arquivos/referências usados por `media_id`;
- problemas de geografia encontrados;
- diferenças conhecidas ainda não corrigidas;
- variação de polígonos quando relevante;
- screenshots antes/depois para classe A;
- novo `model_status` e justificativa.

## Critério de fidelidade

"Fiel" não significa fingir precisão inexistente. Quando a fonte não mede algo exatamente, o resultado deve permanecer marcado como aproximado ou pendente.

A meta é reduzir progressivamente a incerteza mantendo cada decisão rastreável.
