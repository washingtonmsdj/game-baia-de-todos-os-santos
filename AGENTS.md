# AGENTS.md — Bay of All Saints

Estas instruções se aplicam a todo o repositório.

## Idioma

- Nome do jogo: **Bay of All Saints**.
- Documentação, relatórios, commits de projeto e handoffs: português.
- Identificadores de código existentes podem permanecer em inglês ou manter nomes históricos por compatibilidade.

## Antes de alterar o Blender

Leia, nesta ordem:

1. `docs/CODEX_HANDOFF.md`;
2. `docs/BLENDER_WORKFLOW.md`;
3. `docs/REFERENCE_PRODUCTION_PIPELINE.md`;
4. `docs/DATA_PROVENANCE.md`;
5. `world/areas/mvp-centro-lacerda/README.md` quando trabalhar no MVP atual.

## Fonte de verdade

- Scripts e documentação versionados no GitHub são a fonte de verdade do pipeline.
- `.blend` é binário de trabalho e deve ser preservado por revisão; não sobrescrever a origem por padrão.
- IDs de mundo real são os `location_id` em `world/areas/*/locations.json`, não nomes arbitrários de objetos Blender.
- Objetos vinculados a locais devem usar a custom property `boas_location_id` quando o binding for implementado/validado.

## Fidelidade da cidade

O projeto busca alta fidelidade de Salvador, especialmente em:

- ruas e cruzamentos;
- calçadas, ladeiras e escadarias;
- relevo Cidade Alta/Cidade Baixa;
- coastline, cais e limite terra/água;
- posição, escala e silhueta de hero assets;
- relação espacial entre os marcos reais.

Não deslocar geografia para acomodar um modelo sem registrar e justificar a correção.

## Referências visuais

Antes de modelar/revisar um local:

```bash
python tools/references/validate_registry.py --root .
python tools/references/reference_gaps.py --area mvp-centro-lacerda
```

Use apenas referências catalogadas em `media-manifest.json` e respeite `usage_class`/proveniência.

Regras obrigatórias:

- não inventar imagem ausente;
- não tratar imagem sem licença/origem como referência aprovada;
- não promover Hero asset para `approved` sem as vistas mínimas definidas;
- não usar Google Satellite/Street View obtidos pelo Aleph como asset de produção;
- não versionar o acervo visual/geográfico pesado no Git comum;
- registrar hash/proveniência das mídias reais com `tools/references/register_media.py`.

## Aleph e geografia

Aleph é ferramenta externa de aquisição/proveniência, atualmente pinada em:

`Belluxx/Aleph@d24c61507481a91a0dd6afac4f97626a4e5ea780`

A pista da captura histórica do MVP é:

`aleph-20260924T205631Z-aqqo7pkx`

Não implementar merge automático de novas áreas até a transformação mundo real → Blender estar verificada por múltiplos anchors e registrada com erro residual.

## Revisões Blender

- preservar arquivo anterior;
- salvar nova revisão;
- evitar operações destrutivas ocultas;
- validar reabertura;
- gerar relatórios;
- para alterações visuais de Hero assets, comparar antes/depois;
- manter `HERO`, `GAMEPLAY`, referência geográfica e geometria final semanticamente separadas.

## Validação antes de commit/PR

Executar no mínimo:

```bash
python -m compileall -q tools
python tools/references/validate_registry.py --root .
```

Se uma captura Aleph foi usada, gerar/atualizar seu `source_summary.json`.

Se uma revisão Blender foi aplicada, exportar os relatórios da cena antes de declarar a revisão concluída.

## Regra anti-gambiarra

Não resolver problema estrutural por:

- offset manual sem metadado;
- renomeação em massa;
- duplicação de geometria sem necessidade;
- path absoluto versionado;
- referência visual sem proveniência;
- números "aproximados" apresentados como medidos;
- substituição silenciosa de fonte de dados.

Quando uma informação ainda não foi verificada, mantê-la explicitamente como `null`, `candidate`, `partial` ou `pending` conforme o contrato correspondente.
