# Diagnóstico da apresentação do Lacerda — B82 — 06/10/2026

## Resultado

NO_SCENE_CHANGE. Mesma janela Blender PID 10684, arquivo B82, cena ativa `BOAS | GAMEPLAY_PROXY B82`. Não houve salvamento, reabertura, reset do controller ou alteração de visibilidade durante esta inspeção. Lacerda histórico continua congelado.

Comparação de geometria, transforms e materiais com `protected_original_components.json`: 6.296 componentes históricos, zero alterados e zero ausentes. Os 40 obstáculos estáticos do contrato proxy não apresentaram erro de posição ou dimensão. A coleção mantém seus 70 objetos. Isso não constitui auditoria exaustiva de modificadores, animação, colisões ou fidelidade arquitetônica.

Controller registrado e ativo: CLOSED, estação superior, cabine Z=70,114998, abertura=0, sem teclas pressionadas. As posições observadas da cabine/portas são compatíveis com esse estado. Nenhum novo teste de movimento foi executado.

## Aparência atual

A captura GPU do viewport atual mostra blocos claros de saguão/parede proxy diante da arquitetura histórica. Os objetos `SUPERIOR | piso saguão`, `INFERIOR | piso do saguão` e `CALIBRADO | passarela piso 28.71 x 6.00m` estão ocultos na view layer proxy. Essa separação foi introduzida pela B82, conforme `finalize_lacerda_gameplay_proxy_b82.py` e `application_b82.json`: geometria histórica conflitante é mascarada para apresentar o protótipo aproximado. Não é evidência de exclusão dos objetos ou nova deformação da arquitetura.

A apresentação é grosseira e pode parecer descaracterizada: os proxies são visuais simples, não somente colisores invisíveis. Não declarar essa aparência como acabamento arquitetônico aprovado. Não revelar toda geometria histórica sobre o proxy para esconder o problema: isso pode restabelecer conflitos visuais. Qualquer revisão futura de apresentação deve preservar a separação entre aproximação e referência histórica.

O arquivo está dirty e a timeline estava no frame 65024. Isso sozinho não prova alteração de malha; não foi presumida a causa completa das mudanças não salvas. A inspeção foi somente leitura. O cliente MCP expirou após 100 s, mas o script concluiu e gravou o diagnóstico e a captura; não houve repetição da inspeção pesada nem abertura de segunda instância.

## Evidências

- `docs/reports/blender/lacerda-live-diagnostic/current.json`
- `artifacts/lacerda-live-diagnostic/current-viewport.png` — DEV_REFERENCE_ONLY, captura da mesma sessão.
- `docs/reports/blender/lacerda-gameplay-proxy/application_b82.json`

B76–B82, SSOT, 27 testemunhas e `LACERDA_VERTICAL = BLOCKED_EXTERNAL_EVIDENCE` preservados. Nenhuma B83, mudança arquitetônica ou promoção para produção.

## Recuperação de apresentação após captura do usuário

Na janela reaberta pelo usuário, único PID Blender 11304, confirmado o mesmo arquivo B82 via porta 9876. A máscara proxy ocultava o objeto inteiro `MVP | terreno corrigido | colisão estática` e pisos históricos, não apenas faces dentro do percurso. Portanto a apresentação proxy podia eliminar chão de grande parte do núcleo. O terreno B74 também consta mascarado; a impressão de expansão visível não comprova que toda sua superfície estivesse ativa. A inspeção anterior de componentes intactos não detectava esse defeito de apresentação.

Recuperação limitada à UI: encerrado controller se ativo, interrompida timeline se em reprodução e selecionada a cena existente `SALVADOR | ESBOCO OFICIAL`. Onze objetos de piso/terreno/marquise conferidos visíveis nessa cena. A coleção dos 70 proxies continua intacta na cena B82 separada. Não houve edição de malha, correção arquitetônica, novo arquivo, salvamento ou promoção de fonte. O defeito de máscara da apresentação proxy permanece dívida técnica; esta recuperação restaura a visualização completa para modelagem, não redefine o protótipo como aprovado visualmente.

Evidência: `docs/reports/blender/lacerda-live-diagnostic/restored_view.json`; operação reproduzível em `automation/blender/restore_historical_map_view.py`. Captura da vista restaurada: `artifacts/lacerda-live-diagnostic/restored-viewport.png`, DEV_REFERENCE_ONLY.

## Continuação — reparo de visibilidade do terreno no proxy

Aplicado ao vivo no mesmo PID 11304: os dois terrenos comprovados tiveram `hide_set(False)` somente na view layer proxy. Visibilidade histórica preservada; nenhum vértice, transform, collider ou estado físico alterado. Captura `proxy-ground-restored.png` confirma o chão do núcleo novamente presente. A janela terminou na cena histórica para modelagem, sem controller em execução.

Regra central em `lacerda-gameplay-proxy.json` → `presentation.keep_context_visible`; os scripts de apresentação e lançamento reutilizam a regra. O finalizador não deve mascarar essas malhas inteiras por overlap AABB local. O launcher reaplica o patch após registrar o controller, antes de iniciar o jogo. Não confundir essa exceção visual com liberação da arquitetura histórica para colisão ou novo sweep aprovado.

Patch da sessão **não salvo dentro do .blend B82**, para preservar o snapshot. É reproduzível pelos scripts; nenhuma B83 criada porque não há correção estrutural de malha. As paredes simplificadas do proxy continuam apenas na cena de protótipo: não foram apagadas nem declaradas fachadas reais. A vista de modelagem usa a cena histórica completa. Evidência: `ground_visibility_patch.json`.

## Abertura lateral no encontro superior — confirmada na cena histórica atual

Após nova captura do usuário, medidos 147 componentes do entorno na mesma janela PID 11304/porta 9876, cena ativa `SALVADOR | ESBOCO OFICIAL`. Zero diferenças de assinatura contra os componentes históricos preservados na B82. As paredes `SUPERIOR | posterior lateral` e `.001` estão visíveis e terminam em Y local −4,70/+4,70. O piso e cobertura da passarela terminam em Y −3,00/+3,00 no mesmo referencial de medição. Portanto o vão arquitetônico candidato é 9,40 contra largura geométrica 6,00, deixando cerca de 1,70 de abertura lateral em cada lado. É incompatibilidade entre componentes atuais, não sumiço por visibilidade. Não apresentar essas dimensões como cotas reais levantadas.

A geometria coincide com o baseline B77B em `junction_before_b78.json` para essas paredes/passarela. A B78 havia aplicado fechamento dos retornos, lambris/rodapés e verga, mas B79 foi derivada diretamente de B77B; a migração B78 não foi autorizada automaticamente nas rodadas B79/B80. Assim, a B82 conserva o encontro anterior. Não é uma deformação introduzida pela última auditoria ou teste.

O teste ao vivo foi em outra **cena dentro do mesmo arquivo** (`BOAS | GAMEPLAY_PROXY B82`), que substitui partes da apresentação por volumes aproximados. Sua aprovação limitada não se aplica ao fechamento da parede histórica, ao percurso arquitetônico original ou ao acesso Mercado. A captura atual confirma a distinção. Não mover Hero Assets, cabine ou poço para esconder esse vão. Nesta inspeção nenhuma geometria foi alterada e a migração B78 não foi executada; o congelamento histórico permanece vigente.

Evidências: `docs/reports/blender/lacerda-live-diagnostic/upper_wall_gap.json`, `artifacts/lacerda-live-diagnostic/historical-upper-gap.png` (DEV_REFERENCE_ONLY), `docs/LACERDA_JUNCTION_B78.md` e `docs/LACERDA_CORRIDOR_B79.md`.
