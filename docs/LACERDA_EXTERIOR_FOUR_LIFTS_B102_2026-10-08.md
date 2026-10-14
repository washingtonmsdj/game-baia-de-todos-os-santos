# B102 — corpo exterior, encosta e quatro equipamentos provisórios

B101 preservada. Alterações efetuadas na mesma janela 9876/PID 8792, cena `SALVADOR | ESBOCO OFICIAL`; arquivo salvo e reaberto com conferência de hash e assinaturas.

## Diagnóstico e correções

- Quatro acabamentos R10 mantinham um alcance longitudinal de 54,57 m, ultrapassando a ponte documental de aproximadamente 24 m. Arquivados como `SUPERSEDED_REFERENCE`, sem apagar sua geometria.
- A envoltória estreita do núcleo 17 vinha sendo apresentada como todo o corpo da Cidade Alta. Núcleo preservado; corpo externo separado com largura principal 9,494 m derivada das faces principais 14/518/526 e alas das duas salas técnicas. Não reescalamos o núcleo nem movemos torres.
- Paredes e coberturas das salas laterais e contenções ligando a face posterior à encosta foram acrescentadas pelos controles 14 já registrados contra 17. Espessura 0,25 m e extrusões verticais são candidatas, explicitamente distintas de medição as-built. O contorno externo principal simplifica pequenos recuos; não é réplica certificada.
- O terreno atravessava os dois poços antigos. Recorte local pelo interior da casca arquitetônica17 existente, sem usar o tamanho da cabine como cortador. 28 faces substituídas; área XY retirada 14.974901m². 1030722 faces preservadas. Novos Z interpolados nas próprias faces fonte; nenhum offset, escala, datum ou DEM alterado. Datablock da malha anterior preservado.
- Os equipamentos antigos ficaram historicamente congelados após a revisão da arquitetura. A B82 continua intacta. Quatro equipamentos novos pertencem à coleção `GAMEPLAY_PROXY | Lacerda | quatro equipamentos B102`, com IDs estáveis e contrato único `world/areas/mvp-centro-lacerda/lacerda-four-lifts.json`.

## Equipamentos

| ID | Torre | Varredura da cabine | Controle |
|---|---|---|---|
|lacerda-01|CIDADE_ALTA|CABIN_VOLUME_CCD_CLEAR|STATE_MACHINE_AND_RIDER_TRANSPORT_PASSED|
|lacerda-02|CIDADE_ALTA|CABIN_VOLUME_CCD_CLEAR|STATE_MACHINE_AND_RIDER_TRANSPORT_PASSED|
|lacerda-03|CIDADE_BAIXA|CABIN_VOLUME_CCD_CLEAR|STATE_MACHINE_AND_RIDER_TRANSPORT_PASSED|
|lacerda-04|CIDADE_BAIXA|CABIN_VOLUME_CCD_CLEAR|STATE_MACHINE_AND_RIDER_TRANSPORT_PASSED|

Na emenda do terreno, dez índices novos coincidentes foram vinculados aos vértices fonte/novos equivalentes, com residual máximo de 0,000001349 m. Nenhuma coordenada foi alterada. UVs e materiais preservados; 31 polígonos derivados tiveram somente índices corrigidos. A auditoria final encontrou 58 arestas do recorte intencional e nenhuma fissura nova. Não foi feito merge global.
Os quatro possuem controle independente de chamada/abertura/fechamento/deslocamento e chegaram aos dois níveis na prova ao vivo. Portas somente abrem com cabine presente; partida exige portas fechadas e CCD aprovado; ocupação do portal impede fechamento; estado desconhecido bloqueia. O passageiro de prova conserva a posição relativa ao piso por deslocamento contínuo da cabine, sem teleporte.
A prova ao vivo registra 360 atualizações da viewport e os passos por equipamento. A varredura usa SAT triângulo × caixa varrida exata para translação vertical sem rotação. Inclui todo o volume externo da cabine, não apenas o centro. Folhas de cabine ficam contidas nesse envelope; a análise não certifica o portal arquitetônico/soleira.

## Como operar na janela atual

Abra a barra lateral com **N**, aba **BOAS**, painel **Lacerda · quatro elevadores**. “Chamar alto/baixo” chama ou abre no andar presente; “Viajar” fecha e viaja a partir da cabine aberta. O painel é registrado por `automation/blender/play_lacerda_four_lifts.py`; o texto `BOAS | quatro elevadores | iniciar.py` permite registrá-lo novamente após outra abertura. O bootstrap não executa código de arquivo automaticamente.

## Limites do resultado

- `LACERDA_VERTICAL = BLOCKED_EXTERNAL_EVIDENCE`; `movement_enabled:false` histórico,27 testemunhas B80 `UNRESOLVED` e relatórios preservados.
- `FOUR_LIFTS_PROXY = LIVE_ROUND_TRIP_PASSED`: quatro cabines provisórias passam pelo espaço ativo. Isso não prova a instalação real/Otis nem a folga regulamentar.
- `FOUR_LIFTS_PEDESTRIAN_ROUTE = NOT_INTEGRATED`: não declarar aprovado o trajeto completo de personagem entre praça, saguões, portas/soleiras e Cairu com esses quatro equipamentos. Esse ensaio não substitui sweep pedonal/engine.
- A remoção do solo dentro do núcleo é adaptação local documentada da cena derivada; nenhum arquivo geográfico bruto foi editado. Colisão de runtime não foi exportada nem promovida.
- Corpo externo, cobertura das salas e contato absoluto com a encosta continuam candidatos onde faltam elevações/as-built. Largura principal vem do desenho; altura dos volumes externos não deve ser apresentada como certificada.
- Cada novo asset/contrato usa `accuracy:APPROXIMATE` ou equivalente documental parcial, `replacement_required:true`, `production_ready:false`. Nenhum mecanismo interno/contrapeso foi inventado.
- Lapa, Dique, Fonte Nova, fachadas e decoração não alterados. B76–B101 e SSOT preservados. Produção continuaB30.

## Arquivos auditáveis

`controls.json`, `before.json`, `application.json`, `excavation.json`, `terrain-seam-repair.json`, `terrain-seam.json`, `validation.json`, `live-proof.json` em `docs/reports/blender/lacerda-exterior-b102/`. Imagens `artifacts/lacerda-live-diagnostic/b102-frente.png` e `b102-encosta.png` são capturas GPU da mesma cena, com o terreno visível.

## Próximo trabalho

Validar os quatro portais e a conexão pedonal na arquitetura atual antes de afirmar circulação completa. Manter a pesquisa histórica congelada e evitar nova alteração geográfica para acomodar equipamentos candidatos.
