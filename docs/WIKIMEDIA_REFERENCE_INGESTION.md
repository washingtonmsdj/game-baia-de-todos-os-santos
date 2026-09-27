# Ingestão de referências do Wikimedia Commons

## Objetivo

Fornecer ao Codex um caminho reproduzível e auditável para obter fotografias reais de Salvador com licença explícita, sem depender de downloads manuais, nomes de arquivos soltos ou material sem proveniência.

O Wikimedia Commons é tratado como **fonte externa de mídia licenciada**. O projeto não assume que toda imagem encontrada está automaticamente aprovada: a licença é consultada no momento da importação e o binário continua fora do Git comum.

## Fluxo

1. candidatos são registrados em `world/areas/<area_id>/reference-candidates.json`;
2. o Codex escolhe um candidato adequado para uma vista que ainda falta;
3. roda `import_commons.py` primeiro em `--dry-run`;
4. confere título, autor, licença, dimensões, data e coordenadas quando existirem;
5. importa a imagem para `world-reference/`;
6. `register_media.py` calcula SHA-256 e registra a mídia em `media-manifest.json`;
7. `validate_registry.py` confirma integridade e cross-references;
8. `reference_gaps.py` mostra quais vistas ainda faltam.

## Inspeção sem download

```bash
python tools/references/import_commons.py \
  --area mvp-centro-lacerda \
  --candidate-id mercado-modelo-frente-2025 \
  --dry-run
```

Esse modo consulta apenas os metadados do Commons e não altera o catálogo.

## Importação

```bash
python tools/references/import_commons.py \
  --area mvp-centro-lacerda \
  --candidate-id mercado-modelo-frente-2025 \
  --media-root world-reference \
  --usage-class REFERENCIA_INTERNA
```

O arquivo é salvo em:

```text
world-reference/<area_id>/<location_id>/...
```

`world-reference/` fica ignorado pelo Git. O repositório recebe somente o registro leve com hash e proveniência.

## Promoção para PRODUCAO_APROVADA

O importador somente aceita `--usage-class PRODUCAO_APROVADA` automaticamente quando a licença reportada pelo Commons pertence à allowlist conservadora do pipeline:

- CC BY;
- CC BY-SA;
- CC0;
- Public Domain/Public Domain Mark.

Licenças com restrições NC/ND não são aprovadas automaticamente. Licenças fora da allowlist continuam podendo ser catalogadas como `REFERENCIA_INTERNA` com status de licença pendente, desde que o uso em questão seja permitido.

A licença do arquivo continua sendo a licença da fonte; o script não concede direitos adicionais.

## Candidatos não são mídia final

`reference-candidates.json` não substitui `media-manifest.json`.

Um candidato registra apenas:

- local associado;
- página do Commons;
- título do arquivo;
- vista sugerida;
- expectativa preliminar de licença;
- notas de uso.

Somente depois do download + hash + verificação a mídia entra em `media-manifest.json`.

Isso evita registrar como disponível uma imagem que nunca foi realmente preservada no acervo local.

## Seleção visual

Priorizar fotografias que ajudem a reconstruir geometria, não apenas imagens bonitas.

Para edifícios Hero, buscar combinação de:

- frontal;
- traseira;
- laterais;
- oblíquas;
- acessos;
- telhado quando possível;
- contexto de rua/praça;
- detalhes arquitetônicos.

Para Praça Cairu/cais/ruas, priorizar imagens georreferenciadas e com heading quando disponíveis, porque ajudam a cruzar a leitura visual com a base geográfica.

## Limites

Uma fotografia não deve ser tratada como levantamento métrico isoladamente.

Usar imagens para:

- silhueta;
- proporção relativa;
- ritmo de fachada;
- aberturas;
- materiais;
- mobiliário;
- contexto visual.

Usar geodados/anchors validados para:

- posição absoluta;
- eixo de rua;
- coastline;
- escala global;
- transformação mundo real → Blender.

## Auditoria

Após uma rodada de importações:

```bash
python tools/references/validate_registry.py --root .
python tools/references/reference_gaps.py --area mvp-centro-lacerda
```

Nenhum Hero asset deve ser promovido para `approved` apenas porque existe uma fotografia frontal.
