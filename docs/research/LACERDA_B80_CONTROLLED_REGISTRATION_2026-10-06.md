# Registro arquitetônico controlado — B80, 06/10/2026

**Decisão: `NO_SCENE_CHANGE`. Não foi criada B81, não houve exportação nem alteração do SSOT.** O registro é parcial e diagnóstico; não existe transformação arquitetônica aprovada. As revisões B76, B77B, B78, B79 e B80 permanecem preservadas.

## Pranchas selecionadas

| Prancha SUCOP 2023 | Utilidade nesta rodada |
|---|---|
| 17 | Planta superior: acesso, passarela e contorno da torre |
| 12 | Planta inferior: desembarque, saguão, túnel e torre |
| 13 | Planta da cobertura inferior e relação com a torre |
| 23 | Cortes AA/BB: níveis dos acessos e coberturas |
| 21 | Comparação construtiva dos cortes AA/BB, existente/proposto |
| 24 | Cortes CC/DD, apoio à investigação superior; escala conflitante |

03/04/08 documentam construção/demolição e ajudam a distinguir fases, mas não acrescentam automaticamente controles independentes às plantas correspondentes. 22 é contextual, com conflito de escala; 31/34 documentam instalações/tetos, sem provar a seção estrutural do poço ou a cabine.

Foram usadas as cotas impressas 0,00, +4,00, −53,17 e −58,93. Não foi convertida distância em pixels para dimensão física. O carimbo não resolve o conflito 1:50 × 1:100. Projeto arquitetônico de 2023 não equivale a as-built da instalação modernizada.

## Controles e limite do registro

`vertical_registration.json` contém oito comparações de nível: quatro elementos em duas pranchas do mesmo projeto. Não são oito controles independentes. Cada registro contém desenho, ponto, objeto, ponto da cena, fonte, confiança, resíduo e motivo. XY desconhecido permanece `null`; a correspondência entre o nível documental e o plano físico da mesh é candidata.

`xy_control_attempts.json` contém seis pontos vetoriais documentais nas plantas 12/17 e três buscas de encontros estruturais na 13. Pontos vetoriais não são medidas métricas nem controles aceitos: não foi identificado com segurança o mesmo encontro físico na malha. Nenhuma correspondência foi escolhida por proximidade ou nome. Não há três controles físicos não colineares aceitos por planta. Transformações XY e completa permanecem `null`.

`world/geographic-reference.json` continua canônico. A comparação Z fixa escala 1 e calcula somente um offset/resíduos diagnósticos, sem aplicar ajustes. Não certifica escala física, datum absoluto, desenho executado ou associação arquitetônica.

## Onde aparecem os aproximadamente 3,78

Medições read-only da B80 salva, em unidades métricas nominais da cena:

| Elemento/plano candidato | Z local | Z mundo |
|---|---:|---:|
| Fundo da soleira superior | 70,115005 | 70,115005 |
| Fundo da soleira inferior | 11,115000 | 7,406000 |
| Topo da plataforma superior | — | 70,059998 |
| Topo da plataforma inferior | — | 7,351000 |
| Topo da cobertura inferior | — | 11,916000 |

A soleira inferior possui transform Z **−3,70900011062622**, escala unitária e nenhum parent. A superior tem matriz identidade. Antes desse transform, a diferença entre os fundos das meshes é aproximadamente **59,000006**. O CCD usa **62,70900011062622**; a geração histórica do percurso usa os níveis candidatos dessas soleiras.

Decomposição nominal auditável:

`62,70900011062622 − 58,93 = 3,70900011062622 + (59,00 − 58,93)`

Portanto, **3,709** aparecem no transform local inferior e **0,070** na diferença entre a referência histórica aproximada e a cota documental. A precisão numérica dos vértices acrescenta cerca de 0,000006 à comparação das meshes. Um offset uniforme de datum cancela na diferença entre acessos e não explica esse excesso.

O transform inferior já consta no inventário anterior à B77; sua primeira revisão e intenção original continuam desconhecidas. **Localizar a contribuição não prova que removê-la esteja correto.** O plano da soleira, o piso arquitetônico e o envelope da cabine ainda precisam de correspondência independente.

A diferença entre os topos das plataformas também é aproximadamente 62,709, portanto o problema não se limita à posição candidata da cabine. Entre topo da plataforma inferior e topo da cobertura há **4,565**, contra **5,76** entre os níveis documentais −58,93/−53,17: resíduo candidato **−1,195**. Usar a soleira como piso muda a comparação; é necessário distinguir laje, acabamento, cobertura e soleira antes de atribuir erro à arquitetura.

A passarela chamada `CALIBRADO | passarela piso 28.71 x 6.00m` mede **55,538544** no eixo longitudinal local da malha, com escala unitária e sem parent. O nome conserva uma dimensão antiga e não é controle confiável. Não foi autorizada redução da passarela. A torre de referência em torno da origem também não foi adotada como controle apenas pelo nome/propriedades.

## As 27 testemunhas

O arquivo `witness_reclassification.json` conserva componente, obstáculo, instante sólido e classificação geométrica original de cada testemunha. Resultado: **27 `UNRESOLVED`**, distribuídas em plataforma superior (13), cobertura inferior (13) e plataforma inferior (1). Nenhuma correção autorizada.

`UNRESOLVED` significa atribuição causal não comprovada; não apaga penetrações geométricas. `CONTACT_ONLY` não foi aplicado às 27 testemunhas sólidas. Os demais pares superficiais do baseline não foram promovidos automaticamente a erros. As cotas e transforms levantam hipóteses, mas não distinguem inequivocamente arquitetura incorreta, cabine incorreta ou ambas.

## Instalação atual: busca específica

Continuam desconhecidos W/D/H da cabine executada, abertura livre, posição da porta, soleira, gap estação/cabine, seção interna e folgas do poço. Não foram recuperados desenhos de montagem/as-built que comprovem essas dimensões.

Foi localizado um **indicador secundário, ainda sem documento primário validado**: publicação sobre contrato SEMOB 008/2023, processo 151228/2023, inexigibilidade 013/2023, referente à reforma/revitalização dos quatro equipamentos. Projeto básico e proposta comercial são os próximos anexos específicos a recuperar. Não confundir com contrato de manutenção 004/2023/processo 20952/2023. A [publicação espelhada de 24/10/2023](https://www.escavador.com/diarios/5804834/DOMSSA/P/2023-10-24?page=34) é pista de localização, não prova dimensional ou fonte promovida para release.

As buscas focaram montagem, instalação, fiscalização/medição e modernização Otis/SUCOP/SEMOB/FMLF; não produziram as-built público utilizável. O comunicado público da Otis identifica a modernização, mas não informa as medidas necessárias. Não foram enviados pedidos, emails ou formulários. Referências documentais existentes continuam `DEV_REFERENCE_ONLY` na política central.

## Próximo gate

Identificar três encontros físicos permanentes por planta útil, confirmar por cotas o perfil/plano correspondente e recuperar os anexos específicos da instalação. Só depois existe base para autorizar uma correção localizada e repetir CCD dos 38 componentes/sweep do personagem. Nesta rodada não houve mudança geométrica: repetir CCD idêntico não comprovaria a arquitetura real. Movimento e produção continuam bloqueados; Lapa, Dique, Fonte Nova e decoração não foram alterados.

Dados desta rodada: `docs/reports/research/lacerda-registration-b80/`. Baseline: `docs/research/LACERDA_B80_ISSUE22_RESULT_2026-10-06.md` e relatórios canônicos B80. A inspeção da cena foi headless estritamente read-only, sem salvar, trocar a cena visível ou abrir outra janela de edição.

Verificação focada concluída: hashes das cinco revisões/SSOT e relatórios canônicos preservados; 17 registros de controles/tentativas conferidos; 27 testemunhas rastreáveis; 16 recursos documentais com brutos/hashes preservados. Validador de referências: zero erros e dois avisos anteriores (bounds WGS84 da área e cobertura visual do cais). Essas verificações comprovam integridade/rastreabilidade, não aprovação física ou arquitetônica. Não foram executados npm, build ou suíte geral de testes. Nenhum commit/push nesta rodada.
