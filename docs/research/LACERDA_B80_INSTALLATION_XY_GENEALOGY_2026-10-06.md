# B80 — instalação SEMOB, registro XY e genealogia, 06/10/2026

Baseline: `LACERDA_B80_CONTROLLED_REGISTRATION_2026-10-06.md`. **`NO_SCENE_CHANGE` preservado. Nenhuma B81, exportação, alteração de SSOT ou repetição de CCD.** Não houve intervenção em Lapa, Dique, Fonte Nova, fachada ou decoração.

## Resultado explícito

| Gate solicitado | Resultado |
|---|---|
| `ORIGIN_OF_3_709_FOUND` | **Não**: contexto semântico parcial recuperado; operação e revisão introdutora não comprovadas |
| `SEMOB_INSTALLATION_DATA_FOUND` | **Não**: nenhum Projeto Básico, proposta comercial ou desenho dimensional da modernização recuperado |
| `XY_REGISTRATION_ACCEPTED` | **Não**: pontos documentais identificados, sem correspondências físicas inequívocas na cena |
| Estado da rodada | **`STILL_UNRESOLVED`** |

As 27 testemunhas permanecem `UNRESOLVED`; o ERROR geométrico original não é apagado. Nenhum contato sólido foi reclassificado como tangência. Movimento e produção continuam bloqueados.

## A — documentos da instalação atual

A consulta foi direcionada ao processo **151228/2023**, contrato SEMOB **008/2023** e inexigibilidade **013/2023**. A pista do resumo publicado em 24/10/2023 permanece secundária: [espelho do DOM](https://www.escavador.com/diarios/5804834/DOMSSA/P/2023-10-24?page=34). Não foi recuperada a publicação primária com seus anexos. Otis é a contratada indicada nessa pista, mas modelo e configuração física da cabine executada não foram demonstrados.

Além das buscas exatas, foram consultadas por GET público:

- [SEMOB: licitações](https://mobilidade.salvador.ba.gov.br/licitacao/) e [transparência](https://mobilidade.salvador.ba.gov.br/transparencia/);
- busca pública WordPress por `151228`, `Otis`, `inexigibilidade`, `Lacerda` e `008/2023`;
- página [Aquisições](https://mobilidade.salvador.ba.gov.br/aquisicoes/) e sua representação pública JSON;
- portais municipal atual/antigo e o link de compras encontrado na página oficial antiga.

A busca `151228` retornou lista vazia. Os resultados `Otis` incluem notícia de manutenção, linha de metrô e Plano Inclinado Gonçalves, sem anexo da instalação solicitada. O índice de licitações contém a manutenção do Lacerda de 2023 e ar condicionado de 2019: **não são a modernização 008/2023**. `008/2023` retornou HTTP 500; não interpretar isso como ausência de documentos. A página Aquisições apenas encaminha à consulta municipal de aquisições pela unidade gestora, sem anexos técnicos próprios.

O portal de compras retornou **HTTP 503**. As duas páginas SEFAZ sondadas apresentaram erro de cadeia de certificado no cliente usado; o endereço DOM candidato teve timeout. O frontend público do portal atual foi identificado, sem autenticação, uso de credenciais ou acesso reservado. **Não foi esgotado o acervo interno do processo nem comprovada a inexistência dos anexos.** Não houve email, formulário ou requerimento enviado.

Não confundir o contrato de manutenção **004/2023 / 20952/2023** com a instalação investigada. Permanecem `null`: modelo executado, W/D/H, abertura livre/posição das portas, soleira, gap estação/cabine, seção útil do poço, folgas, montagem, níveis de parada e offsets próprios da modernização.

Origem, URL inicial/final, momento, processo-alvo, código HTTP e SHA-256 dos arquivos efetivamente recuperados estão nos quatro relatórios de aquisição e em `source_summary.json`. HTML/JSON de busca, código público e páginas de erro não foram tratados como anexos técnicos. Brutos sob `world-reference/`, fora do Git comum, classificados `DEV_REFERENCE_ONLY` no catálogo central.

## Genealogia do −3,709

Foram lidos, sem salvar, três snapshots: primeira referência estrutural R30A preservada, B01 e B80. Foi consultado também o histórico Git de scripts/relatórios com buscas específicas pelos valores, pelo nome histórico da passarela e pelo metadado inferior.

**Contexto semântico comprovado pelo metadado histórico:** `docs/reports/blender/r30a/georef_hints.json`, exportado de uma cena identificada como **R27**, registra `lower_terminal_r21` como cota de passeio **7,406**, terreno local **7,256**, **aproximação do MVP, não levantamento oficial**. Outro metadado conserva saída baixa **11 m**, com compatibilização local. São registros da intenção aproximada do MVP, não dados de instalação atual.

**Não comprovado:** o nome `lower_terminal_r21` não prova que o transform tenha sido criado na R21. Não foi encontrado script de criação, relatório antes/depois ou commit executando −3,709. O primeiro commit que contém auditoria com esse número, `b2a9e7c` de 28/09/2026, documenta um estado já existente; não cria o deslocamento. A primeira revisão que o introduziu permanece `null`. Import, calibração, edição manual e script anterior não puderam ser distinguidos.

| Snapshot lido | Objetos com translação Z mundial exata −3,709 | Dependências diretas identificadas |
|---|---:|---:|
| R30A referência estrutural | 54 | 0 |
| B01 | 54 | 0 |
| B80 | 56 | 10 |

Na B80: **9** elementos `FUNCIONAL | 3`, **44** `FUNCIONAL | 4`, **1** soleira inferior geral e **2** colisores B79. A enumeração completa, matrizes, propriedades, coleções e vínculos está em `genealogy_snapshots_readonly.json`. Coincidência de offset não prova uma origem comum; contagens descrevem o estado salvo, não todos os estados da animação.

Os dois itens adicionados ao conjunto desde o primeiro snapshot são os colisores das portas inferiores do equipamento 3, parentados às portas-fonte. Outras oito dependências diretas são vedações B02 de portas inferiores/cabine 4. Não houve alteração desses vínculos. Consumidores externos adicionais usam os níveis inferiores no traçado B77, animação de portas, proxy de poço B79 e investigação de acesso; referências de código estão no JSON de síntese.

**Plataforma, cobertura e piso inferior não compartilham o transform exato:** têm posições próprias — centros Z aproximadamente **7,211**, **11,791** e **7,281**, respectivamente — já presentes no primeiro snapshot. Seus níveis relacionam-se ao desembarque, mas não foi comprovada a operação que os colocou ali. Não subtrair ou somar automaticamente 3,709 a esses objetos. A diferença de pisos continua candidata; nenhum offset uniforme de datum explica sozinho a diferença entre acessos.

## Genealogia da passarela

R30A preservada, B01 e B80 têm a mesma extensão longitudinal local **55,538544**, mínimo X **−14,355003**, máximo X **41,183540**, escala unitária e nenhum parent. Logo, o alongamento/asimetria já existia antes das rodadas B77–B80; não foi causado pela investigação atual. O relatório da cena R27 conserva os mesmos bounds mundiais, dentro do arredondamento de exportação.

O script versionado `refine_lacerda_r30b08_support.py` usa **55,539** para intradorso/vigas novos. É um consumidor da extensão existente, não evidência da operação que alterou a passarela original. O metadado `dimensoes_status = medida publicada` e o nome 28,71 são inconsistentes com a extensão medida e não autorizam sua redução. Não foi localizada a revisão/operação original de alongamento; nenhuma escala física foi reconstruída pelo nome.

## B — registro XY controlado

As pranchas **17, 12, 13 e 23** foram revistas visualmente. Foram preservados/examinados três pontos vetoriais não colineares por planta 17/12/13, incluindo agora três pontos concretos da 13, que antes eram buscas sem coordenadas. `xy_controls_round2.json` registra desenho, coordenada PDF, curva/vértice, hash, fonte, justificativa, confiança e residual. A não colinearidade foi calculada em pontos PDF; **não é uma dimensão física em metros**.

As quinas são candidatos do contorno estrutural documentado da região da torre. A equivalência de face/fase com a cena ainda não foi demonstrada. Os três obstáculos da triagem são malhas de plataforma/cobertura retangulares; seus vértices não identificam por si só encontros de paredes ou torre das plantas. Não atribuir a uma quina documental um vértice de caixa por proximidade, nome ou conveniência.

Consequentemente, `scene_object`, `scene_point` e `residual` de correspondências não comprovadas permanecem **`null`**. São nove pontos no desenho e **zero correspondências aceitas**, sem fit artificial. A prancha 23 continua controlando níveis documentais do baseline; não foi convertida em controle XY da planta nem usada para confirmar dimensões das cabines.

Não se usou cabine, mobiliário, instalação temporária ou porta inferida como controle. Escala por pixels/carimbo não foi aplicada. `world/geographic-reference.json` continua único e canônico; transformação derivada XY permanece `null`.

## Pendências precisas

Recuperar a íntegra/anexos do processo 151228/2023, incluindo Projeto Básico, proposta comercial, desenhos de instalação/montagem e medições/as-built. Separadamente, demonstrar três encontros físicos permanentes em desenho **e** cena, com calibração por cotas e identificação do mesmo plano/fase. Para a genealogia, ainda faltam snapshots/registro operacional anteriores à R27/R30A. Não promover o contexto semântico parcial a `ORIGIN_OF_3_709_FOUND` completo.

Resultados auditáveis em `docs/reports/research/lacerda-b80-installation-xy/`; proveniência central atualizada. Nenhuma geometria mudou, portanto o CCD dos 38 componentes e o sweep do personagem não foram repetidos como se essa pesquisa aprovasse o movimento.

Verificação focada: cinco snapshots protegidos e SSOT/relatórios canônicos conferidos por hash; três snapshots históricos lidos sem salvar; nove pontos documentais conferidos; 27 testemunhas preservadas; 16 arquivos de aquisição com hashes conferidos e exclusão do Git confirmada; sintaxe dos cinco scripts desta rodada válida. Validador de referências: zero erros e dois avisos preexistentes. Isso comprova integridade e rastreabilidade, não dimensões de instalação, correspondência física ou jogabilidade. Nenhum npm, build, suíte geral de testes, commit ou push executado.
