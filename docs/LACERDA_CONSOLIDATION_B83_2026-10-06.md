# B83 — encontro superior consolidado e vista completa — 06/10/2026

## Resultado

Nova revisão derivada da B82: `blender/salvador_lacerda_r30b83_encontro_superior_consolidado.blend`. Cena de abertura e revisão: `SALVADOR | ESBOCO OFICIAL`, na mesma janela Blender/MCP 9876, PID 11304. Não usar a cena proxy como substituta da revisão visual do mapa completo.

A abertura lateral apontada pelo usuário foi corrigida na malha existente. As duas paredes posteriores agora encontram as bordas da passarela. Lambris e rodapés acompanham os retornos; a verga foi reconciliada para não se sobrepor aos retornos prolongados. Sete malhas alteradas, sem deslocar objetos, mudar materiais, terreno, pisos ou a passarela.

Migração específica da geometria B78 já validada, após comprovar no mapa atual a mesma incompatibilidade de 9,40 × 6,00 e os mesmos componentes B77B. Não houve merge automático da revisão inteira. A biblioteca B78 foi lida pela API de dados dentro da única instância; nenhuma segunda janela ou edição headless. Um erro de lista na primeira leitura da biblioteca foi corrigido antes de aplicar alterações às malhas de destino.

Dois colisores candidatos derivados das paredes foram acrescentados à coleção física existente, com binding explícito `boas_derived_from_object`. A auditoria de bindings não encontrou collider desses retornos antes da criação. Não promover esses objetos ou o percurso histórico à produção.

## Fonte e limite de fidelidade

Controle: bordas permanentes dos componentes autorais atuais, genealogia/validação B78 e comparação ao vivo B82. A correção resolve uma incompatibilidade entre malhas atuais; **não comprova cotas construtivas reais do saguão, poço ou cabine**. Dimensões reais continuam parciais. Não alterar o datum, origem, escala geográfica ou distância entre níveis para acomodar a cabine.

As aproximações funcionais B82 continuam separadas na cena `BOAS | GAMEPLAY_PROXY B82`, com seus 70 objetos, `APPROXIMATE` e `replacement_required: true`. O terreno restaurado na apresentação proxy foi preservado no novo arquivo. A cena histórica foi deixada aberta para modelagem; controller não iniciado.

## Verificações após salvar e reabrir

- Reabertura real na mesma instância confirmada por `last-open.json`.
- 6.296 componentes históricos comparados: somente as sete alterações declaradas; zero mudanças inesperadas ou objetos anteriores ausentes.
- 48/48 sondagens de fechamento aprovadas.
- Fresta numérica máxima das paredes: 0,00000143 unidade.
- Paredes sem faces degeneradas ou arestas não-manifold; colisores coincidem com os vértices visuais, erro máximo 0,0.
- 1.947 amostras da cápsula no trajeto superior contra as sete malhas modificadas: nenhum bloqueio. Não é aprovação de todo o piso/poço ou controller histórico.
- SSOT preservado; B82 preservada por hash `9a8c89520df6b86eaebc9000792c4ad077c5c20a0e77e1aec7ec647a15b3a49a`. B76–B81 e B78 não foram sobrescritas.

B83 SHA-256: `7c4376037dcca58a9367f38d07d75ec8fd2f8f2106a0c68c109dbb5514c70423`.

## Gates preservados

`LACERDA_VERTICAL = BLOCKED_EXTERNAL_EVIDENCE`

27 testemunhas históricas B80 permanecem UNRESOLVED e seus relatórios não foram reescritos. `movement_enabled: false` histórico permanece. A conexão à entrada física do Mercado ainda não está aprovada. Não considerar a B83 uma solução do gate B80 ou um mapa integralmente perfeito.

Lapa/Campo da Pólvora/Dique/Fonte Nova continuam GREYBOX, sem alterações desta rodada. Após salvar/reabrir/validar, B83 foi registrada como candidata explícita de modelagem (`authoring_source`) e validação (`validation_source`), atendendo ao pedido de manter a revisão consolidada ativa. O arquivo B41 permanece preservado. Produção B30 e fonte proxy B82 não promovidas. Nenhuma exportação de produção.

CCD repetido em saída própria da B83: 38 componentes, 54 pares de contato, exatamente os mesmos pares da B80; zero novos ou removidos. Resultado permanece blocked. Esses contatos não foram automaticamente reclassificados como erro sólido ou resolução das 27 testemunhas. A correção do encontro não libera viagem vertical histórica.

Sweep de cápsula histórica repetido com skin 0,015, raio 0,30 e altura 1,80: superior com zero trechos penetrantes, inferior com nove. Apoios e limites do solver não equivalem a controller de engine aprovado. Saída própria `character_sweep_b83.json`, sem sobrescrever resultados B80. O percurso inferior original permanece bloqueado; o teste funcional B82 aplica-se somente ao proxy separado.

## Evidências

- `docs/reports/blender/lacerda-consolidation-b83/application.json`
- `docs/reports/blender/lacerda-consolidation-b83/validation.json`
- `docs/reports/blender/lacerda-consolidation-b83/ccd_comparison.json`
- `docs/reports/blender/lacerda-consolidation-b83/cabin_sweep_b83.json`
- `docs/reports/blender/lacerda-consolidation-b83/final_view_state.json`
- `artifacts/lacerda-live-diagnostic/b83-reopened.png` — DEV_REFERENCE_ONLY.
- `automation/blender/consolidate_upper_junction_b83.py`
- `automation/blender/validate_consolidated_b83.py`

Próximos gates independentes: conector Cairu–entrada física do Mercado e continuidade estrutural Tomé/Misericórdia/Pelourinho. A alta fidelidade interna do Lacerda permanece congelada, exceto pela correção específica do encontro solicitada nesta rodada.
