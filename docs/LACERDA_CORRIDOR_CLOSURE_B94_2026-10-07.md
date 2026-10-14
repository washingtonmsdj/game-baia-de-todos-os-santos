# Lacerda — fechamentos da passarela e do túnel B94 — 07/10/2026

B94 aplicada ao vivo, salva e reaberta na mesma janela Blender, PID 16912, MCP 9876, cena `SALVADOR | ESBOCO OFICIAL`. B76–B93 preservadas. Esta rodada responde aos vãos indevidos dos corredores, sem retomar investigação do datum ou da instalação dos elevadores.

## Antes e depois

1. **Passarela → saguão superior.** Faltavam os dois retornos na extremidade oeste do contorno SUCOP17: lado norte entre a quina externa do saguão e o endpoint da ponte; lado sul entre o outro endpoint da ponte e a quina externa. Foram construídos peitoril, vidro e verga, usando os materiais existentes. O portal central continua aberto: largura documental local 6.163564m. Não foi criada uma parede atravessando a circulação. Os pisos e a cobertura agora incluem os mesmos endpoints da ponte, eliminando uma pequena divergência entre os contornos. Recorte do núcleo antigo mantido.
2. **Túnel → face existente da torre antiga.** Piso e teto terminavam antes da reentrância permanente da torre; havia um tampão transversal nessa extremidade prematura. A união das lajes incorpora o pequeno encontro de 1.947166m² entre o contorno inferior SUCOP12 e a face da torre já reconstruída de SUCOP17. As paredes laterais chegam aos mesmos endpoints; o tampão prematuro foi substituído pelos retornos laterais. A face da torre e o envelope do poço permanecem intactos. Este encontro é `ADAPT_LOCAL` derivado dos contornos documentais existentes; não é prova de alinhamento as-built entre plantas de pavimentos diferentes nem aprovação da entrada no poço.
3. **Malha das paredes.** A representação usa união planar antes da extrusão, incluindo os encontros de canto. Evita caixas soldadas apenas por arestas, faces internas duplicadas e quinas abertas. Espessura 0,18m permanece aproximação herdada, registrada como candidata. Não foram inventadas cotas de parede ou dimensões da cabine.

Seis meshes existentes alteradas e seis componentes de retorno adicionados. Objetos-fonte, transforms, frame arquitetônico, núcleo das torres, níveis dos pisos, terreno e SSOT preservados. Nenhuma mudança em Lapa, Dique, Fonte Nova ou decoração.

## Verificação real

- Reabertura da B94 com arquivo, hash, PID e cena conferidos.
- 603 componentes B88–B94 comparados às assinaturas persistidas; 397 visíveis sem faces degeneradas, arestas não manifold, winding inconsistente ou faces duplicadas no escopo auditado.
- 6303 objetos fora da edição protegidos durante a aplicação; 9 meshes do inventário local, fora da edição, conferidas novamente após a reabertura. Não confundir essas duas contagens.
- 100 sondagens reais de piso/cobertura nos retornos e no prolongamento do túnel; 60 sondagens das paredes em várias alturas; 15 verificações de abertura do portal; 12 encontros verticais, gap máximo 0.00000023m.
- Sondagens de superfície usam barycentros em double sobre os triângulos reais. A BVH float apresentou erro numérico Z de cerca de 0,00013m em um triângulo estreito; não houve alteração de skin, cápsula ou geometria para mascarar isso. Os hits BVH e os resultados double ficam registrados.
- SSOT, terreno e assinaturas do GAMEPLAY_PROXY B82 idênticos aos anteriores.
- 5 bindings históricos preservados, explicitamente desabilitados/invalidados após a alteração dos objetos-fonte. Nenhum collider novo duplicado e nenhuma declaração de controller aprovado.
- Vistas reais de ambas as junções e do mapa completo em `artifacts/lacerda-live-diagnostic/b94-*.png`. A janela terminou com `local_view=false`, terreno visível e `unsaved_changes=false`.

Esta validação comprova os fechamentos e encontros no escopo acima. Não comprova toda a circulação interna, implantação absoluta, cabine/poço, CCD da cabine ou controller. Não foi repetido o CCD histórico sem alteração da instalação. A relação entre piso inferior e terreno mantém a pendência documentada na B93; não foi escondida com aterro, rampa ou parede.

## Estados preservados

`LACERDA_VERTICAL = BLOCKED_EXTERNAL_EVIDENCE`

`movement_enabled = false`

`27 testemunhas B80 = UNRESOLVED / PRESERVED`

`GAMEPLAY_PROXY B82 = PRESERVED / replacement_required: true`

`ABSOLUTE_MAP_PLACEMENT = NEEDS_REVIEW`

`EXPANDED_MAP = GREYBOX`

`production_ready = false`

Fonte ativa: `blender/salvador_lacerda_r30b94_fechamentos_passarela_tunel.blend`. SHA-256 `f557e11231f3e628d1b8960f81973cd2686dfe3cb8706a82ac7029326adb9ca6`. Produção e fonte gameplay continuam anteriores; não exportar esta candidata para produção.

Controles e genealogia: `docs/reports/blender/lacerda-closure-b94/mutation-journal.json`; antes: `before.json`; alterações: `application.json`; QA: `validation.json`; apresentação: `presentation.json`. Fontes SUCOP12/17 dependem do registro relativo B88 já documentado e permanecem separadas do SSOT canônico.

Próxima verificação de modelagem: revisar os demais encontros exteriores contra a planta, preservando as entradas reais. A conexão arquitetônica ao poço e o percurso completo não podem ser declarados funcionais pela correção destas seams.
