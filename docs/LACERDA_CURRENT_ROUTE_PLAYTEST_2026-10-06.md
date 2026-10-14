# Teste atual Cidade Alta → Lacerda → Cairu / Mercado — 06/10/2026

## Resposta

O protótipo B82 executa Tomé de Souza → embarque superior → descida → desembarque inferior → Cairu e retorno. **Não existe aprovação do trajeto completo até a entrada do Mercado Modelo**. O conector final não está implementado no contrato funcional; não foi criada uma rota até uma porta por proximidade.

O teste foi na cena `BOAS | GAMEPLAY_PROXY B82`, não em `SALVADOR | ESBOCO OFICIAL`, embora ambas estejam no mesmo arquivo/janela. A posterior inspeção confirmou que a cena histórica mantém aberturas laterais no encontro superior saguão–passarela, aproximadamente 1,70 unidade por lado. O teste não aprovou essas paredes; ver `docs/LACERDA_LIVE_DIAGNOSTIC_2026-10-06.md`.

## Teste numérico do controller existente

Executado novamente com o contrato atual: 10.608 amostras, duas viagens e nove verificações aprovadas: porta fechada bloqueia, cabine ausente bloqueia poço, portal ocupado impede fechamento, não parte com porta aberta, não abre sem cabine atracada, parede de cabine bloqueia, transporte contínuo do passageiro, interlocks de partida e ausência de salto na sequência. Raio 0,30, altura 1,80, step 0,25 e skin 0,015 preservados. Deslocamentos subdivididos do solver B82, não prova de CCD contínuo de todas as malhas da cidade.

Endpoint funcional XY Blender [−89,289593; 106,561385], correspondente ao controle OSM 13078289038 em Cairu. Não é binding a entrada física do Mercado. A política da travessia é provisória `EXCLUSIVE_PEDESTRIAN_PROTOTYPE_NO_MOVING_TRAFFIC`; semáforo/tráfego real não aprovado.

## Execução na janela visível

Mesma janela PID 11304 / MCP 9876, B82 existente. Inputs gerados progressivamente para o mesmo ProxyController; não reprodução de uma lista gravada de poses nem atribuição de waypoints ao personagem. Spawn explicitamente inicializado antes do teste. 10.675 passos/yields na rotina ao vivo, diferença de contagem inclui espera de abertura e marcadores; mesmos eventos temporais de partida/chegada da rotina numérica. Timesteps físicos 1/60 s, lotes de 30 atualizações por callback de 0,05 s: apresentação acelerada nominalmente 10×, duração observada 66,53 s. Isso não é benchmark de performance de uma engine.

Viagem inferior e superior concluídas, chegada a Cairu e retorno ao spawn confirmados. Erro de sincronização mundial da pose do personagem 0,0; erro máximo passageiro–cabine em Z 5,69e−16. Seis marcos capturados: spawn, embarque, descida, desembarque inferior, Cairu e retorno superior. Nenhuma penetração detectada pelo contrato de caixas do proxy durante caminhada. Poses dinâmicas, vista e cena prévias restauradas após concluir; patch de visibilidade de terreno mantido. Nenhuma revisão salva, B82 não sobrescrita.

## Limitações que impedem aprovação integral

- Colisão exercitada: pisos/OBBs do GAMEPLAY_PROXY. Não equivale a colisão contra toda malha histórica, terreno restaurado, mobiliário ou edifícios visíveis.
- Capturas mostram saguão simplificado e volume cinza durante a descida. A execução numérica não prova apresentação arquitetônica livre de interpenetrações; não declarar esse aspecto visual aprovado.
- Conexão final Cairu → entrada física do Mercado ausente do contrato; não testável como percurso implementado.
- Sem engine-alvo integrada, NPCs, tráfego real ou revisão das 27 testemunhas históricas.

## Gates e preservação

`B82_PROXY_TOME_CAIRU = PASS_IMPLEMENTED_PROXY_ONLY`

`FULL_TOME_MARKET_ROUTE = NOT_APPROVED`

`MARKET_ENTRANCE_CONNECTOR = NOT_IMPLEMENTED_NOT_TESTABLE`

`LACERDA_VERTICAL = BLOCKED_EXTERNAL_EVIDENCE` (histórico)

27 testemunhas históricas, movement_enabled false histórico, SSOT, B76–B82 e replacement_required true preservados. Não promover para produção. Nenhuma malha alterada, nenhuma B83. Este ensaio não transforma gates históricos em resolvidos.

## Evidências

- `docs/reports/blender/lacerda-current-playtest/numeric.json`
- `docs/reports/blender/lacerda-current-playtest/live.json`
- `artifacts/lacerda-live-diagnostic/playtest-*.png` — capturas DEV_REFERENCE_ONLY.
- `tools/world/test_lacerda_proxy_current_route.py`
- `automation/blender/playtest_lacerda_current_route.py`

Próximo trabalho para obter a rota completa: selecionar e vincular o acesso físico do Mercado, reconciliar seu conector e auditar obstáculos/superfícies visíveis com o contrato funcional. Isso é pendência externa, não autorização para reabrir a investigação interna de alta fidelidade do Lacerda.
