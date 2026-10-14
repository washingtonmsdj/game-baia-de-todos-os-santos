# Lacerda–Cairu–Mercado: bloqueio vertical encerrado e frente externa

## Estado

- `LACERDA_VERTICAL = BLOCKED_EXTERNAL_EVIDENCE`
- Conclusão da investigação B80: `STILL_UNRESOLVED`; pesquisa ativa encerrada.
- `CAIRU_MARKET_PEDESTRIAN = CANDIDATE_VALIDATION_NOT_APPLIED`
- `EXPANDED_MAP = GREYBOX`
- `NO_SCENE_CHANGE`, `movement_enabled: false`, nenhuma B81 ou exportação.

O desbloqueio vertical depende do **Processo SEMOB 151228/2023 / Contrato 008/2023 / inexigibilidade 013/2023**, especialmente Projeto Básico, proposta comercial, desenhos de instalação/montagem da modernização ou levantamento físico equivalente do conjunto executado. É necessário resolver dimensões, portas/soleiras/gap, seção e folgas do poço, níveis e datum/offsets. A manutenção 004/2023 / 20952/2023 não substitui essa evidência. Nenhuma nova busca genérica foi executada nesta rodada.

B76, B77B, B78, B79, B80, SSOT e os 17 relatórios/contratos canônicos B80 permanecem intactos por SHA-256: `docs/reports/world/cairu-market-pedestrian/closure_and_controller_gate.json`. As 27 testemunhas mantêm a classificação `UNRESOLVED` e a detecção geométrica original. O CCD da cabine não foi repetido. Não foi usado teleporte, passagem invisível, recorte ou animação como substituto da física.

## Travessia comprovada por topologia

O XML OSM já catalogado (`source:osm-centro-20261005`) confirma **way/395865976** pelos seguintes nós compartilhados, em ordem:

| Nó | Via | Controle registrado no OSM |
|---|---|---|
| 3178050253 | 1004133497, Rua da Conceição da Praia | uncontrolled |
| 5917201014 | 978525930, Praça Visconde de Cayru | traffic_signals |
| 592378620 | 46348179, Av. Lafayete Coutinho | traffic_signals |

Os caminhos `312006925` e `1423065746` conectam os extremos por IDs de nós. Isso comprova conexão geográfica; não prova rampa existente, largura livre, altitude, sinal verde ou entrada atual do Mercado. Não foi criada nova faixa ou conexão por proximidade.

A transformação canônica reproduz os seis traçados na referência estrutural existente com residual XY **0,0**. Esse resultado compara dados de referência, não certifica o pavimento final da cena. O inventário B76 contém objetos com IDs explícitos, mas a exportação volumétrica B80 não inclui as curvas de referência. A reconciliação final desses objetos exige inspeção na sessão visível.

**A rota inferior antiga não segue a travessia:** seus afastamentos dos cinco nós são 3,313; 2,801; 10,681; 11,048; 6,810 unidades Blender. Portanto, corrigir apenas Z dessa rota não autoriza vinculá-la à passagem real. Os conectores até o saguão e a entrada do Mercado continuam pendentes; não foram ligados artificialmente.

## Nove penetrações e ground-following

O baseline possui **duas ocorrências na interface cabine/soleira inferior e sete externas nos meios-fios**. Todas foram preservadas em `baseline_penetrations.json`; nenhuma foi declarada corrigida na cena.

Foi preparado ground-following candidato sobre triângulos existentes, com cápsula de raio 0,30 e altura 1,80, passo máximo de projeto 0,25 e skin numérico 0,002. OSM fornece XY; Z vem de faces da B80, com busca local limitada. Não foram acrescentados pisos ou rampas.

O diagnóstico da rota antiga usa 1.491 pontos e continua **bloqueado**: oito segmentos com penetração e 20 amostras exigindo solver de degrau/contato. A travessia OSM isolada usa 337 pontos; nove amostras exigem o mesmo solver. As contagens não são equivalentes às nove ocorrências originais, pois houve adensamento e nova trajetória de pés. Não há prova de controller físico nem de percurso completo.

A primeira sondagem da travessia detectou 44 segmentos com contato sólido, incluindo a pintura verde. O script R30B06 e as propriedades da malha comprovam que `fundo verde travessia 3178050253` é pintura visual plana, com separação de render de 0,003; não é laje. Sua exclusão foi ensaiada somente no candidato de colisão, preservando toda a geometria visual, chão e meios-fios. Restam **seis segmentos com penetração**, sem intervalos numéricos inconclusivos ou perda de apoio nas sondagens: **a travessia continua bloqueada**. Resultado separado em `character_sweep_crossing_collision_roles.json` e `collision_role_evidence.json`; nenhum binding foi aplicado ao Blender.

## Contrato e próximo trabalho

`world/areas/mvp-centro-lacerda/cairu-market-pedestrian.json` estende o contrato da slice existente e reutiliza `elevator_controller.py`; não cria SSOT, planner ou sistema de colisão paralelo. O vínculo OSM é verdadeiro, mas clearance pedonal permanece falso e permissão de tráfego desconhecida. O planner bloqueia tanto a viagem vertical quanto o percurso inferior completo; nenhum sinal é presumido verde.

O MCP/companion não respondeu na janela atual: porta 9876 em escuta, sondagem com timeout, OrdaX sem sessão fresca e adoção sem sucesso. Foi solicitada reativação na mesma janela. A regra de sessão visível impediu aplicação geométrica; não foi criada segunda janela nem usada edição headless.

Próximo passo: recuperar a sessão, inspecionar B80 e reconciliar as superfícies externas/colliders com seus objetos-fonte; validar os acessos reais dos dois caminhos OSM, degraus/rampas e entrada do Mercado. Executar então sweep externo e controller com gravidade/slide/step e tráfego. O gate vertical permanece independente e bloqueado. Lapa, Campo da Pólvora, Dique e Fonte Nova não foram alterados.
