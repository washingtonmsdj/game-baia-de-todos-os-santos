# R30B.01 — refinamento visual do Elevador Lacerda

Revisão de trabalho: `blender/salvador_lacerda_r30b01_refinamento.blend`.
Base preservada: R30A.11, escolhida em `production.json`. **Não promovida ao runtime.**

## Alterações

- Materiais de 502 componentes do elevador: reboco marfim, esquadrias claras, vidro transparente, mármore dos peitoris e inox das cabines.
- Venezianas modeladas nas aberturas técnicas existentes, friso de cruzetas sob a galeria e chanfros superiores nas aberturas da passarela.
- Piso visual paginado sobre a superfície existente da passarela. Paginação é `ADAPT_LOCAL`, sem alegar medidas reais das placas.
- Detalhes estáticos consolidados em 28 objetos na coleção `HERO | Lacerda | detalhes R30B`, com `boas_location_id=elevador-lacerda`.
- Nenhuma mudança de implantação, escala geográfica, navegação, colisão ou animação existente. Nenhuma separação/reparentamento do Hero original.

## Evidência e limites

Fotos Commons de julho de 2025 registradas em `media-manifest.json`, CC BY-SA 4.0, uso `REFERENCIA_INTERNA`:

- `elevador-lacerda-detail-ded7c75d401c`: interior da passarela, autor Sintegrity.
- `elevador-lacerda-oblique_left-ca2c56d9b78b`: conjunto exterior, autora Thaismay.

Fotos não usadas como textura do jogo. Materiais procedurais próprios.
Revisão visual da galeria e da passarela realizada via MCP na única janela. Arquivo salvo e reaberto com sucesso.
Capturas e relatório local em `artifacts/lacerda/`.

**Estado parcial, não aprovado:** faltam cobertura visual das demais fachadas, revisão completa dos saguões/cabines e comprovação visual do movimento do sistema existente. Dimensões da cena preservadas não equivalem a levantamento real. O preview apresenta ruído de transparência; não é um render final.

Scripts desta etapa: `automation/blender/refine_lacerda_r30b.py` e `automation/blender/finish_lacerda_r30b.py`, executados sequencialmente via MCP. O piso paginado e ajuste métrico dos nós de textura foram aplicados adicionalmente via MCP e estão preservados no `.blend`.
Não executar esses scripts sobre a revisão já refinada. Não substituir a fonte ativa automaticamente.
