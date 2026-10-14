# B86 — contorno e proporções do conjunto superior

**Revisão posterior ativa:** B87, documentada em `docs/LACERDA_UPPER_FINISH_B87_2026-10-07.md`. A B86 permanece preservada como snapshot intermediário.

## Resultado

Revisão real salva e reaberta na única janela Blender, PID **16912**, MCP **9876**, cena **SALVADOR | ESBOCO OFICIAL**.

- Arquivo: `blender/salvador_lacerda_r30b86_saguao_superior_planta.blend`.
- SHA-256: `5add1823f0d2cebb9c2c3bd33f59b6aead145a7929787dc88137be3ef173fb48`.
- Base preservada: B85, SHA-256 `c1d5e4b8aad618e0ebcdca77accf700febf49c0b8d4861809d9034c20453a7c8`.
- `authoring_source` e `validation_source` apontam explicitamente para B86. Produção e fonte independente do proxy B82 não mudaram.

O saguão não permanece com o contorno genérico anterior. Piso e cobertura foram reconstruídos com contorno escalonado derivado da prancha 17. Paredes, retornos envidraçados e bloco elevado foram reconciliados com essa proporção. A implantação no mapa e a instalação dos quatro elevadores continuam candidatas: esta revisão não representa certificação arquitetônica/as-built ou aprovação de gameplay.

## Fonte, escala e implantação

Fonte oficial: SUCOP, prancha 17, projeto 2023, `source:lacerda-issue22-sucop-17`. PDF: `world-reference/mvp-centro-lacerda/research-20261006-issue22/sucop-architectural-17.pdf`, SHA-256 `02d02b37b61b9a44ca931a00811e196e104322a6f0f89fc4bfb04f70d7783dd1`.

Foram usados vetores e três cotas impressas de 5,20 / 1,99 / 2,20 m, sem assumir o carimbo de escala. Resíduos de escala: aproximadamente −1,93 / +0,95 / +3,70 mm. Esses números são coerência dos controles documentais selecionados, não precisão de levantamento físico.

**Zero controles físicos de implantação XY aceitos.** A ancoragem ao acesso superior existente é candidata e está descrita em `layout_source.json`; não modifica o SSOT. A altura atual foi preservada, sem correção global Z.

| Medida | B85 | B86 |
|---|---:|---:|
| Profundidade principal do conjunto superior | 11,00 | cerca de 25,31 m |
| Largura principal do conjunto superior | 18,60 | cerca de 15,99 m |
| Bloco elevado junto à praça | 11,00 × 11,40 | cerca de 15,70 × 10,96 m |

O contorno inclui acessos escalonados: o bounding box completo do piso chega a aproximadamente **26,27 × 19,68 m**, não é um retângulo de 25,31 × 15,99 m. Não confundir o salão de 117,50 m², cotado na prancha, com toda a área de circulação superior.

## Alterações efetivas

1. Piso e cobertura escalonados, mantendo os níveis Z anteriores.
2. Paredes laterais, retornos/lambris, esquadrias e dependências existentes reconciliados com o conjunto superior maior.
3. Bloco elevado ampliado longitudinalmente; envelope do apoio da encosta reposicionado relativamente ao conjunto segundo a região candidata da planta. Esse apoio é **APPROXIMATE**, não seção certificada de poço.
4. Passarela recortada no novo encontro. Módulos de vidro existentes mantiveram seu ritmo, em vez de comprimir todas as janelas longitudinalmente. 28 componentes que pertenciam ao trecho substituído ficaram explicitamente `SUPERSEDED_REFERENCE`, preservados fora da apresentação/navegação ativa.
5. **46 bindings explícitos** reconciliados com os respectivos objetos-fonte. O collider superficial do piso superior foi colocado na superfície visual, mantendo sua representação plana quando essa era sua função, sem extrusão de espessura zero.
6. **Cinco faces de área zero herdadas** removidas em cópias temporárias. Não foram eliminadas superfícies físicas válidas para liberar passagem.

431 objetos passaram pela derivação/atualização de metadados: 141 BRIDGE, 180 BUILDING, 6 OLD_TOWER_ENVELOPE e 104 STATION. O hash dos dados de 404 meshes mudou; isso não significa 404 erros arquitetônicos corrigidos. O relatório lista cada antes/depois e quais componentes ficaram como referência substituída.

A torre da Cidade Baixa, cabines instaladas candidatas e desembarque inferior não foram deslocados nesta revisão. O recorte da ponte melhora o encontro com o salão, mas **não resolve a distância total entre torres nem comprova o vão livre final**. Não forçar 28,71 m a partir do nome legado da mesh.

## Validação e limites

Aplicação feita em cópias temporárias não vinculadas. Somente depois de conferir as malhas foram trocados os dados dos objetos visíveis. Antes de salvar:

- nenhuma face degenerada nova aceita;
- piso e cobertura conferidos como fechados e manifold;
- objetos fora do domínio, terreno, 70 componentes do proxy B82 e hash do SSOT conferidos como preservados;
- cada collider alterado conserva binding explícito com a fonte;
- arquivo B85 conferido por hash.

Reabertura B86 confirmada pelo `load_post`. A conferência pós-reabertura foi concluída por `automation/blender/validate_upper_layout_b86.py`, apesar de um timeout inicial do socket. 431 signatures persistidas e proteção do terreno/proxy conferidas. A checagem local registrou `BLOCKED_OR_REVIEW` nas três linhas: primeiro pela projeção central inadequada ao degrau e depois pelo `NAV | passarela superior` legado, cuja representação física já estava substituída na B80. Evidência conservada em `initial_static_projection.json`, `validation.json` e `navigation_roles.json`. A B87 corrigiu o encontro/fechamento e a apresentação desse helper, sem reclassificar os gates históricos como resolvidos.

Os parâmetros locais são raio 0,30 m, altura 1,80 m, step 0,25 m e skin 0,015 m. A checagem usa superfícies de piso reais, inclusive acabamento da ponte, e reporta apoios/primeiro bloqueio. Não é prova do controller completo, gravidade/slide/CCD ao longo do elevador ou da ligação até o Mercado. Não usar essa checagem como aprovação geral.

## Preservação e proveniência

- B76–B85 e toda a evidência B80 preservadas.
- `world/geographic-reference.json` continua canônico e inalterado.
- `LACERDA_VERTICAL = BLOCKED_EXTERNAL_EVIDENCE`.
- 27 testemunhas históricas continuam `UNRESOLVED`; `movement_enabled: false`.
- Proxy B82 separado, `APPROXIMATE`, `replacement_required: true`.
- Lapa, Campo da Pólvora, Dique e Fonte Nova não foram alterados; permanecem GREYBOX.
- Derivação centralizada: `derived:lacerda-upper-layout-b86`, `REPLACE_BEFORE_RELEASE` / pendente de verificação. Não é asset final.
- Nenhum npm, build, teste amplo, exportação de produção, commit ou push nesta rodada.

## Recuperação da sessão

O usuário confirmou travamento e autorizou reinício. Somente o PID 11304 foi encerrado; a B85 registrada teve hash conferido e foi aberta em único PID 16912. MCP/cena/arquivo foram inspecionados com sucesso, sem alterações pendentes, antes de liberar a aplicação. O modo inicial SOLID foi usado para recuperação/apresentação estrutural; materiais da fonte foram preservados. Histórico em `LACERDA_UPPER_LAYOUT_PREPARATION_2026-10-07.md` e `session-recovery.json`.

## Próximo passo estrutural

Conferir visualmente esta revisão e fechar a implantação/orientação relativa das duas torres e os limites documentais do vão livre. Depois reconciliar o esquema dos dois pares de elevadores e sua ligação inferior por túnel, sem duplicar cabines candidatas nem inventar folgas. Isso continua independente da certificação de instalação SEMOB/Otis, que permanece dívida explícita.
