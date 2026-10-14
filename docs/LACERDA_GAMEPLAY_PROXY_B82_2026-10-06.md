# B82 — Lacerda funcional por proxy de gameplay — 06/10/2026

## Resultado e separação histórica

Revisão `blender/salvador_lacerda_r30b82_gameplay_proxy.blend`, cena `BOAS | GAMEPLAY_PROXY B82`, preservando a cena histórica `SALVADOR | ESBOCO OFICIAL`. Foram acrescentados 70 objetos: 17 pisos, 40 obstáculos/guardas, 12 peças dinâmicas e personagem. Comparação antes e após reabrir: zero mudanças de geometria, transforms ou materiais nos 6.296 componentes históricos. B76–B81 e 24 arquivos protegidos mantêm seus hashes. SSOT permanece canônico e inalterado.

`LACERDA_VERTICAL = BLOCKED_EXTERNAL_EVIDENCE`, 27 testemunhas `UNRESOLVED`, movimento histórico desabilitado. A nova camada tem autorização distinta: `GAMEPLAY_PROXY`, `APPROXIMATE`, `replacement_required: true`. Dimensões, saguões, soleiras e seção da cabine são temporários; o deslocamento candidato de 62,709 m não foi certificado ou corrigido.

## Percurso funcional

Tomé → saguão superior → passarela → cabine → descida → circulação lateral no saguão inferior → cadeia OSM → Cairu, e retorno. A guia original permanece na referência histórica; gradis separados aproximam o fluxo lateral observado nas referências 2025. A visibilidade dos objetos históricos conflitantes é mascarada apenas na view layer do protótipo. Nenhuma malha histórica foi apagada, deslocada ou recortada; nenhum derivado de contexto recortado foi criado.

A travessia do protótipo usa `EXCLUSIVE_PEDESTRIAN_PROTOTYPE_NO_MOVING_TRAFFIC`. Não representa semáforo verde real; o contrato histórico mantém `traffic_permission: null`. O percurso termina em Cairu, sem certificar entrada do Mercado.

## Controller e verificação

Implementação neutra de engine hospedada no Blender: cápsula raio 0,30, altura 1,80, step 0,25, skin 0,015; gravidade, apoio, subdivisão do deslocamento e colisão cápsula/OBB. Portas fechadas bloqueiam; estação sem cabine bloqueia; abertura ocupada impede fechamento; partida exige portas fechadas; passageiro acompanha o deslocamento contínuo da cabine. Nenhum waypoint aplica teleporte.

Ida/volta: 10.608 amostras do mesmo controller; nove casos funcionais/negativos aprovados. Deslocamento máximo por amostra: XY 0,04167 m, Z 0,06667 m. Na sessão reaberta, conferidos 40 obstáculos e 17 pisos contra a representação visual e três poses reais, inclusive transporte. Isso valida o protótipo finito, não uma certificação exaustiva de engine/arquitetura. A métrica legada `falls` não é instrumentada; não serve como prova independente.

Uma falha de timer do operador modal foi corrigida (`Event` sem acesso confiável a `timer`); o operador permaneceu ativo após a correção. Captura nativa retornou preta; captura GPU da mesma câmera/sessão confirmou o viewport. Não foi iniciada segunda instância ou exportação de produção.

## Como jogar

Na cena B82, personagem está ativo na janela atual. WASD ou ↑/↓ movem, ←/→ giram, botão direito + mouse olha. E chama/abre o elevador; após entrar no centro da cabine, E solicita a viagem. Esc encerra. Para reiniciar: F3 → `BOAS Jogar Lacerda (proxy)` ou painel BOAS. Depois de reiniciar Blender, executar o texto `BOAS_JOGAR_PROXY.py` para registrar o painel. Seguir o saguão/passarela até a cabine; no piso inferior contornar os gradis pela lateral até o caminho para Cairu.

O runtime ainda é o Blender, não o jogo browser/Unity/Godot. Fontes de authoring, validação histórica e produção não foram promovidas para B82. Proveniência central classifica o recurso como `REPLACE_BEFORE_RELEASE`.

## Retomada territorial

Auditoria de dados existentes em `docs/reports/world/territorial-resumption/priority_audit.json`: Centro Histórico 714 alertas pendentes, Lapa/Campo 69, Dique 16, Fonte Nova 21. São alertas para triagem, não bugs confirmados. Foram ordenadas as prioridades nos registros existentes, sem reconstruir fundação ou criar geografia nova. Próximo trabalho: confirmar os desvios XY/topologia e continuidade estrutural do Centro Histórico antes das demais regiões. Toda expansão permanece `GREYBOX`.

## Evidências

- `docs/reports/blender/lacerda-gameplay-proxy/application_b82.json`
- `docs/reports/blender/lacerda-gameplay-proxy/validation_b82.json`
- `docs/reports/blender/lacerda-gameplay-proxy/interlocks.json`
- `docs/reports/blender/lacerda-gameplay-proxy/round_trip_numeric.json`
- `docs/reports/blender/lacerda-gameplay-proxy/preservation.json`
- `artifacts/lacerda-gameplay-proxy/controller-gpu.png` (captura de desenvolvimento)
- `world/areas/mvp-centro-lacerda/lacerda-known-debt.json`

Alta fidelidade encerrada temporariamente por decisão do usuário. Substituição futura mediante as-built, levantamento ou documentação SEMOB/Otis; nenhuma dívida foi reclassificada como resolvida.
