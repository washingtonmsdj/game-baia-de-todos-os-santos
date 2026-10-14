# B84 — fechamento envidraçado do encontro superior

Base preservada: B83, além de B76–B82. SSOT e fonte de produção permanecem inalterados. Esta revisão trata somente os dois retornos posteriores junto à passarela; não reabre a investigação do poço/cabine.

## Evidência e limites

Fotografia enviada pelo usuário em 06/10/2026, catalogada como `elevador-lacerda-detail-a75dce21824f`. Hash SHA-256 `a75dce21824f50b16180ecf94aaecda2988494f3a2d13ca7cd97898ac257be2d`. Autoria, data de captura e licença desconhecidas; `DEV_REFERENCE_ONLY`, sem utilização como textura ou distribuição final.

Observação: faixa envidraçada com esquadrias claras continua ao redor dos volumes na altura da passarela. A imagem não comprova medidas, espessuras, número de módulos nem cada face oculta. A aplicação simétrica nos dois retornos é uma adaptação candidata à estrutura existente, explicitamente aproximada.

## Alteração

- `SUPERIOR | posterior lateral` e `.001`: substituição da faixa opaca por painéis de vidro com esquadrias, mantendo base, coroamento, bordas e abertura central.
- Os dois lambris associados são reconciliados com o peitoril. Rodapés, passagem, terreno e corpo elevado não são alterados.
- Vidro e materiais de caixilho reutilizados da passarela. Limites verticais e travessas vêm da geometria existente; subdivisão vertical aproximada, sem medição da fotografia.
- Colisores B83 preservados com o mesmo binding: o envelope fechado continua representando uma barreira física, agora composta também por vidro. Não se permite atravessar o vidro.

Os vidros fazem parte da própria malha do retorno; não existe pano opaco escondido atrás deles. Nenhuma imagem temporária é atribuída ao material.

Captura da cena histórica completa após reabertura: `artifacts/lacerda-live-diagnostic/b84-glazed-upper-return.png`. Conferida visualmente: o retorno visível está envidraçado e conectado à faixa da passarela; passagem central e peitoril mantidos. A vista com materiais fica aberta no Blender. Houve timeout de transporte durante a conferência, mas o script concluiu posteriormente, gerou a captura e registrou `reopened: true`; não foi iniciada outra instância.

## Validação

Resultados numéricos em `docs/reports/blender/lacerda-glazing-b84/validation.json`: 6.298 objetos conferidos, nenhuma alteração inesperada; quatro malhas autorizadas sem faces degeneradas ou arestas não manifold; 1.947 amostras locais da cápsula sem penetração. Colisores, SSOT e 70 objetos do proxy preservados. A reabertura da B84 foi confirmada em `artifacts/blender-sessions/last-open.json`, na mesma instância PID 11304. O teste local cobre somente as quatro malhas alteradas e o percurso superior candidato; não comprova a circulação histórica completa, folgas de cabine ou entrada do Mercado. Registro de referências: zero erros, dois avisos prévios (bounds e cobertura do cais).

`LACERDA_VERTICAL = BLOCKED_EXTERNAL_EVIDENCE`; 27 testemunhas históricas permanecem `UNRESOLVED`; movimento histórico desabilitado. `GAMEPLAY_PROXY B82` permanece separado, aproximado e com `replacement_required: true`. Não houve exportação ou promoção para produção. Expansão territorial preservada em `GREYBOX`.

Próxima frente estrutural continua Tomé / Misericórdia / Pelourinho. Esta correção visual específica não autoriza retomar detalhamento interno do Elevador.
