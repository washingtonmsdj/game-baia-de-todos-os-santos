# Conjunto superior do Lacerda — preparação e sessão indisponível

**Estado posterior:** sessão recuperada com autorização do usuário; B86 efetivamente aplicada, salva e reaberta. Fonte atual e limites estão em `docs/LACERDA_UPPER_LAYOUT_B86_2026-10-07.md`. O texto abaixo preserva o estado histórico da preparação/interrupção, não deve ser usado como ponteiro atual de autoria.

## Resultado desta rodada

**Não há B86 salva ou validada.** A fonte de modelagem registrada continua sendo a B85, `blender/salvador_lacerda_r30b85_apoio_encosta_proporcoes.blend`, SHA-256 `c1d5e4b8aad618e0ebcdca77accf700febf49c0b8d4861809d9034c20453a7c8`. Nenhuma promoção para produção.

A B85 foi reaberta na janela existente, PID 11304, conforme `artifacts/blender-sessions/last-open.json`. A tentativa subsequente de aplicação não retornou em 180 segundos. Depois, o Windows continuou indicando `Responding: false`; o healthcheck read-only da porta 9876 expirou, o companion nativo retornou `Transport closed`, e a leitura da janela por Computer Use expirou duas vezes. Não foi aberta outra instância, nem usada edição headless.

Um timeout do socket não prova cancelamento da execução. Não reenviar a mutação nem tratar ausência do arquivo como prova de que a sessão em memória está limpa. `application-control.json` está desabilitado; o script relê esse controle antes de preparar e antes de trocar malhas. Antes da retomada, conferir a mesma janela, sua cena, arquivo, alterações pendentes e eventuais objetos `B86_STAGING | ...`. Preservar alterações úteis antes de qualquer reabertura. A falha de triangulação anterior ocorreu em cópias temporárias não vinculadas e foi corrigida, sem representar uma B86 aplicada.

O usuário confirmou que a janela estava travada e autorizou explicitamente **reiniciar e reabrir B85**. Apenas o PID 11304 foi encerrado. Depois de confirmar ausência de outra instância e conferir novamente o SHA-256 da fonte registrada, foi iniciado um único Blender visível, PID 16912, com a B85 e bootstrap na porta 9876. A apresentação inicial foi solicitada em SOLID para recuperação; nenhuma geometria foi alterada por esse bootstrap. Logs: `artifacts/blendmcp-fallback/recovery-20261007T030118.stdout.log` e `.stderr.log`. Enquanto o carregamento/conexão não for confirmado, a aplicação continua desabilitada. A autorização de recuperação não representa aprovação da B86 ou de fidelidade arquitetônica.

## Dados preparados, sem aprovação arquitetônica

Fonte: prancha oficial SUCOP 17, projeto 2023, já catalogada como `source:lacerda-issue22-sucop-17`. Hash do PDF: `02d02b37b61b9a44ca931a00811e196e104322a6f0f89fc4bfb04f70d7783dd1`.

O arquivo `docs/reports/blender/lacerda-layout-b86/layout_source.json` registra três controles de escala impressos: **5,20 m, 1,99 m e 2,20 m**. Ajuste de escala vetorial com resíduos de aproximadamente −1,93 mm, +0,95 mm e +3,70 mm. Esses resíduos medem coerência entre controles documentais e vetores selecionados; não são precisão de levantamento físico nem residual de registro da cena.

| Elemento | Geometria B85 | Derivação preparada da prancha | Limitação |
|---|---|---|---|
| Profundidade principal do conjunto superior | 11,00 unidades | cerca de 25,31 m | Inclui salão e circulações; não equivale ao salão de 117,50 m² isoladamente |
| Largura principal do conjunto superior | 18,60 unidades | cerca de 15,99 m | Contorno é escalonado, com acessos que excedem essa largura principal |
| Bloco elevado junto à praça | 11,00 × 11,40 unidades | cerca de 15,70 × 10,96 m | Correspondência/implantação precisa de conferência |
| Passarela atual | cerca de 55,54 unidades | recorte no encontro com o conjunto maior | Não comprova vão livre final nem resolve distância entre torres |

O nome `CALIBRADO | passarela piso 28.71 x 6.00m` não é medida da malha atual. Também não autoriza forçar comprimento de 28,71 m sem confirmar quais limites físicos a referência mede.

**Registro físico XY aceito: zero controles.** A ancoragem do desenho ao acesso superior existente é explicitamente candidata. `world/geographic-reference.json` permanece canônico e não foi alterado. Escala documental, posição geográfica, altura e instalação são problemas distintos.

## Aplicação preparada e QA pendente

`automation/blender/model_lacerda_upper_layout_b86.py` prepara em cópias temporárias o piso/cobertura escalonados, seus encontros laterais, o bloco elevado e dependências explicitamente vinculadas. Mantém módulos existentes de vidros da ponte, recortando apenas o encontro; registra peças substituídas como referência. O apoio da encosta é envelope aproximado, não seção certificada de um poço. A aplicação está suspensa.

`automation/blender/validate_upper_layout_b86.py` prepara conferência após reabertura: persistência, faces degeneradas, fechamento do piso/cobertura, assinaturas dos 70 proxies B82 e do terreno, hashes, apoio no encontro e amostras da cápsula de raio 0,30 m, altura 1,80 m, step 0,25 m e skin 0,015 m. **Esse QA ainda não foi executado.** Não é CCD completo nem validação do controller/poço ou do percurso até o Mercado.

Antes de aprovar uma revisão, conferir visualmente o contorno contra a prancha, continuidade dos vidros e paredes, correspondência dos colisores e terreno. Não compensar bloqueios reduzindo cápsula ou movendo Hero Assets por encaixe visual.

## O que continua pendente

- Implantação e orientação relativa das duas torres, distância total e vão livre da ponte.
- Relação entre o apoio da encosta, os dois elevadores antigos e o conjunto superior.
- Quatro elevadores como dois pares em torres distintas e conexão inferior por túnel: as pranchas indicam a organização geral, mas não autorizam duplicar cabines candidatas ou afirmar dimensões atuais de instalação.
- Alturas/soleiras, cabine e seção útil dos poços instalados: não comprovadas por esta análise de planta.

`LACERDA_VERTICAL = BLOCKED_EXTERNAL_EVIDENCE`; 27 testemunhas B80 `UNRESOLVED`; `movement_enabled: false`. Proxy B82 continua separado, aproximado e `replacement_required: true`. B76–B85 preservadas, Lapa/Dique/Fonte Nova em GREYBOX. Não exportar para produção.

## Armazenamento

Foram encontrados aproximadamente 0,88 GB livres no C:. Limpeza restrita a corpos antigos de cache Chrome liberou cerca de 1,12 MB; perfis, índices, cookies, cenas e referências foram preservados. A compactação conservadora de históricos antigos não encontrou novos arquivos elegíveis: zero bytes liberados e nenhum conteúdo apagado. Relatórios em `docs/reports/storage/stale-browser-cache-20261007.json` e `history-compaction-20261007.json`. Não atribuir o travamento ao espaço em disco como causa comprovada.

## Próximo passo obrigatório

Recuperar a sessão visível existente e inspecionar seu estado antes de liberar `application-control.json`. Só então aplicar, conferir, salvar e reabrir uma B86 real. A preparação desta rodada não deve ser apresentada como correção concluída do saguão ou do elevador inteiro.
