# Lacerda: gameplay temporário e dívida histórica

Decisão do usuário em 06/10/2026: congelar a investigação de alta fidelidade do Elevador Lacerda. Preservar B76–B81, SSOT, relatórios, documentos e as 27 testemunhas B80. Nenhuma dessas pendências é reclassificada como resolvida.

O fluxo funcional passa a usar um perfil explícito `GAMEPLAY_PROXY`, `accuracy = APPROXIMATE`, `replacement_required = true`. Dimensões de cabine, portas, soleiras, circulação interna e posição das guias podem ser aproximadas para o protótipo. Isso não autoriza mudar Hero Assets históricos nem deslocar a geografia.

## Autoridades

- `world/geographic-reference.json`: SSOT geográfico, preservado.
- `blender-revisions.json#/validation_source`: B81 histórica bloqueada, preservada.
- `blender-revisions.json#/gameplay_proxy_source`: revisão separada de protótipo, sem promoção de produção.
- `lacerda-gameplay-proxy.json`: geometria simplificada e parâmetros do controller do protótipo.
- `lacerda-known-debt.json`: pendências congeladas e condições futuras de substituição.
- `production.json`: continua sendo a única autoridade para exportar produção; o protótipo não a substitui.

Um frame local derivado do centro/orientação B81 serve somente à geometria do asset e ao controller. Sua transformação para o SSOT é explícita; não é um segundo georreferenciamento.

## Separação na revisão

A cena histórica conserva objetos, malhas, materiais, transforms e visibilidade. A cena `BOAS | GAMEPLAY_PROXY B82` tem sua própria view layer e coleção de proxies. Candidatos históricos que conflitam com a circulação não são usados como colisão funcional nessa cena. Sua apresentação pode ser mascarada nessa view layer; a cena histórica permanece disponível. Contexto de terreno recortado para apresentação, quando necessário, é derivado substituível e não uma correção topográfica.

Não usar o controller antigo da timeline como física. O controller novo controla abertura, fechamento, presença, transporte e apoio. Portas de uma estação ausente continuam físicas e fechadas; ocupação do portal impede fechamento; deslocamento exige portas fechadas. O personagem atravessa a abertura por movimento contínuo e acompanha o deslocamento da cabine.

A guia `.001` continua `STILL_UNRESOLVED` para fidelidade. O par de gradis do protótipo mantém circulação lateral e saída junto à bilheteria, sem afirmar que sua posição seja real. Os originais não são deletados.

## Tráfego provisório

A conexão com Cairu acompanha os controles XY da cadeia OSM já catalogada. Larguras, pads de junção e pequenas transições do chão são de gameplay. A regra do protótipo é `EXCLUSIVE_PEDESTRIAN_PROTOTYPE_NO_MOVING_TRAFFIC`: não há veículos em movimento na travessia deste perfil. Isso não representa semáforo verde nem simulação do tráfego real. `traffic_permission: null` permanece no contrato histórico.

## Retomada territorial

Após aprovar o fluxo funcional, encerrar temporariamente o trabalho no elevador. Prioridade: Centro Histórico; Lapa/Campo da Pólvora; Dique; Fonte Nova. Terreno, vias, quadras, footprints, massing e marcos primeiro. Sem fachadas prédio por prédio. Reutilizar Aleph/OSM e SSOT, sem reconstruir B76 ou abrir outro fit regional.

As pendências do Dique e das vias continuam reais; o congelamento do elevador não as resolve. Adaptações locais devem registrar sua finalidade e revisão. Proxies não podem ser promovidos silenciosamente para produção.

## Substituição futura

Retomar alta fidelidade quando houver as-built, levantamento físico, desenhos de instalação ou documentação SEMOB/Otis útil. Processo SEMOB 151228/2023, contrato 008/2023, continua referência de evidência externa necessária. Substituir os proxies gradualmente, repetindo as validações funcionais e preservando esta trilha. Resolver um proxy não resolve automaticamente as 27 testemunhas históricas.
