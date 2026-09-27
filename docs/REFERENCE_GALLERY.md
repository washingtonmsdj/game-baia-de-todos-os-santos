# Galeria local de referências

## Objetivo

Transformar o acervo técnico de referências em uma interface visual navegável por `location_id`, sem mover os binários para o Git e sem depender de um serviço externo.

A galeria é gerada a partir de:

- `locations.json`;
- `media-manifest.json`;
- `reference-candidates.json`;
- arquivos reais existentes em `world-reference/`.

Ela não altera nenhum desses arquivos.

## Gerar

```bash
python tools/references/build_gallery.py \
  --area mvp-centro-lacerda \
  --media-root world-reference
```

Saída padrão:

```text
artifacts/reference-gallery/mvp-centro-lacerda/index.html
```

`artifacts/` já fica fora do versionamento normal.

## O que a página mostra

Para cada local:

- prioridade e classe de fidelidade;
- estado do modelo e das referências;
- vistas obrigatórias;
- vistas ainda faltantes;
- imagens já importadas no acervo;
- hash/licença/origem de cada mídia;
- indicação de cobertura principal ou adicional;
- candidatos ainda não importados, com link para o Wikimedia Commons.

Uma mídia panorâmica com `coverage` aparece nos diversos locais que ela realmente ajuda a documentar, mas continua existindo como um único arquivo/hash no acervo.

## Uso pelo Codex

Antes de um passe visual grande:

1. validar o catálogo;
2. gerar `reference_gaps.py`;
3. importar candidatos necessários;
4. gerar a galeria;
5. usar a galeria como índice visual do trabalho;
6. modelar somente o que as referências sustentam;
7. regenerar a galeria quando o manifesto mudar.

## Limites

A galeria é uma ferramenta de navegação, não uma fonte de verdade independente.

- licença e proveniência continuam vindo do manifesto;
- coordenadas continuam vindo das fontes geográficas registradas;
- candidatos não contam como mídia importada;
- arquivo local ausente é mostrado explicitamente como ausente;
- a galeria nunca promove `model_status` ou `reference_status` automaticamente.

## Acervo externo

Se `world-reference/` estiver em outro disco, passe o caminho real:

```bash
python tools/references/build_gallery.py \
  --area mvp-centro-lacerda \
  --media-root D:/BayOfAllSaints/world-reference \
  --output artifacts/reference-gallery/mvp-centro-lacerda/index.html
```

Os links das imagens são calculados relativamente à saída HTML; nenhum caminho absoluto é persistido no catálogo versionado.
