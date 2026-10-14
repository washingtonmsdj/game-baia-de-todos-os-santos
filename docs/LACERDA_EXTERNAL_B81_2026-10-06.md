# B81 — frente externa parcial, percurso bloqueado

Base: `LACERDA_EXTERNAL_PEDESTRIAN_2026-10-06.md` e B80 preservada. Esta revisão não resolve o gate vertical.

- `LACERDA_VERTICAL = BLOCKED_EXTERNAL_EVIDENCE`
- `CAIRU_MARKET_PEDESTRIAN = PARTIAL_ROUTE_APPLIED_BLOCKED`
- `EXPANDED_MAP = GREYBOX`
- `movement_enabled: false`; 27 testemunhas B80 `UNRESOLVED`.

## Sessão e mudança efetiva

BlendMCP 1.4.4 recuperado na porta 9876, PID 10684, mesma janela: B80 confirmada com 6.294 objetos e sem alterações pendentes. OrdaX não adotou a sessão, mas o fallback existente respondeu; nenhuma segunda instância ou edição headless foi usada.

Salva `blender/salvador_lacerda_r30b81_cairu_colisao_e_rota_parcial.blend`, SHA-256 `45583e49dde0a4a03d6b8d4a654135bb11644e786acb681dab7da3d68984e4af`. Dois derivados adicionados, total 6.296 objetos:

1. patch físico de meios-fios, 1.848 triângulos existentes copiados sem deslocar vértices, limitado à frente externa;
2. guia de trajetória candidata OSM, desabilitada para navegação e produção.

Os pisos reaproveitam seus bindings B77 existentes, sem duplicação. Pintura verde comprovadamente plana recebeu `RENDER_ONLY`/colisão desabilitada no contrato externo. Meio-fio mantém papel físico de degrau; não foi apagado ou achatado. Metadados foram aplicados em cinco objetos-fonte. Comparação antes/depois dos 6.294 objetos originais registrou **zero alterações em geometria, transforms e materiais**. Terreno, edifícios, portas, cabine e poço não foram modificados.

O cliente atingiu timeout durante a aplicação, mas o script concluiu posteriormente e a revisão foi confirmada na mesma sessão, sem alterações pendentes. A persistência pós-reabertura é registrada separadamente em `docs/reports/blender/cairu-market-b81/validation.json`; não usar o timeout como prova de falha nem repetir a mutação.

Reabertura concluída no PID 10684. Validação pós-reabertura: todos os 1.848 triângulos derivados pertencem à fonte; cinco fontes modificadas apenas em metadados preservam assinatura geométrica. Os três bindings de chão foram comparados em 46 sondagens sobre vértices/centroides: nenhum apoio ausente e residual Z máximo 0,0. Isso valida essas superfícies amostradas, não o trajeto inteiro. B76–B80, SSOT e 17 relatórios/contratos canônicos foram novamente conferidos por hash em `protected_baseline.json`. Nenhum CCD do poço/cabine foi repetido.

## Nova trajetória e limites de evidência

A rota antiga fica somente no baseline histórico. Nova candidata usa a cadeia compartilhada:

`736745764 → 3178050253 → 3986605269 → 3986605270 → 5917201014 → 592378620 → 13078289038 → 12229090827`.

São controles das ways 312006925, 395865976 e 1423065746, reconciliados exclusivamente pelo SSOT. Z vem das faces da B80 e dos apoios R21 inspecionados ao vivo; nenhuma altitude foi extraída do OSM. **Os conectores saguão–caminho e caminho–entrada do Mercado não estão aprovados.** Não foi inventada conexão ou entrada: o término é o último nó do caminho catalogado, não a porta do Mercado.

## Seis testemunhas e controller

Cada testemunha anterior foi inspecionada na malha viva: fonte `B63 | VISUAL | meios-fios das vias existentes`, triângulo, vértices, distância da cápsula e profundidade preservados em `live_inspection_b80.json`. Os seis contatos variam de aproximadamente 0,0021 a 0,0035 unidades, no ensaio anterior com skin 0,002. O conjunto registra altura de desenho candidata 0,12, inferior ao step de projeto 0,25, mas isso não prova que a subida funcione. Superfície continua física; ação candidata é subir com solver, contornar se houver piso livre comprovado ou bloquear.

O novo ensaio usa raio 0,30, altura 1,80, step 0,25 e **skin contratual 0,015**. Não se reutilizou silenciosamente o skin 0,002 da sondagem anterior. Foram gerados 889 pontos e 25 amostras exigindo solver de degrau/apoio.

A pré-validação encontrou **47 segmentos penetrantes**, todos em `INFERIOR | guia de fila.001`. O controller numérico executou gravidade 9,81, CCD de cápsula, tentativa de step up/forward/drop e slide por normal; aceitou 50 movimentos e bloqueou o movimento 51. Não removeu a guia de fila. Isso é prova candidata de bloqueio, **não aprovação da física de uma engine**. O sweep pós-aplicação e o replay da fonte B81 ficam em relatórios próprios.

Após aplicar/reabrir B81, o sweep externo foi repetido com o patch derivado substituindo a fonte de meio-fio na camada física, evitando colisão duplicada. Resultado: **47 segmentos penetrantes**, zero intervalos numéricos inconclusivos e zero apoios ausentes nas sondagens. Replay B81 mantém parada no movimento 51; permissão de tráfego desconhecida continua bloqueando. O resultado não autoriza produção nem fluxo até o Mercado. Arquivos: `character_sweep_post_application_b81.json` e `controller_replay_b81.json`.

Topologia da travessia confirmada, mas semáforos, clearance geométrico e permissão de veículos permanecem gates distintos. `traffic_permission: null` bloqueia o planner; sinal verde não é presumido. A execução não chegou à travessia nem à entrada do Mercado. Não houve tentativa de contornar o elevador por teleporte ou animação.

## Próximo gate

Identificar e validar o conector pedonal real entre o saguão e o início do caminho OSM, respeitando a guia de fila e paredes existentes. Depois conferir degraus, calçadas, semáforos e acesso físico do Mercado usando referências catalogadas e superfícies reais. Só habilitar após sweep sem penetrações e apoio/controller/tráfego aprovados. Se o acesso não puder ser comprovado, manter o trecho parcial bloqueado. Lapa, Campo da Pólvora, Dique, Fonte Nova, fachadas e decoração permanecem inalterados; produção não foi promovida ou exportada.
