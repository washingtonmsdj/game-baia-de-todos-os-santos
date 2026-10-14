# B80 — piso e embarque superior candidatos; poço continua bloqueado

## Resultado e limites

A B80 deriva diretamente da B79, sem incorporar automaticamente a B78. Reconcilia o collider da passarela com o piso visual e corrige a trajetória candidata dos pés. **O embarque superior ainda não está certificado fisicamente e a viagem permanece bloqueada.** Não houve recorte de lajes, redimensionamento de cabine, deslocamento de Hero Assets ou alteração geográfica para acomodar a cápsula.

Fonte salva e reaberta na única janela Blender, MCP 9876:

- `blender/salvador_lacerda_r30b80_piso_e_embarque_superior.blend`.
- SHA-256: `2dc973c3efc4710cf268b348d4892fc17df0c2ac2ecef0e2e45d0493c249e4c4`.
- B76, B77B, B78 e B79 preservadas e conferidas por hash.
- 6.292 objetos originais da B79 preservados; dois objetos derivados adicionados, total 6.294.
- SSOT `world/geographic-reference.json` preservado, SHA-256 `1d9da0962d456cb38ed3df0da797208e499a8465f82e9836c14bb337df2385e7`.
- Produção B30 e autoria B41 não promovidas. **B79/B80 não exportadas para produção.** Os JSONs de triângulos são evidência de auditoria, não pacote do jogo.

## Investigação independente e proveniência

Aleph continua ferramenta de aquisição, pinado em `Belluxx/Aleph@d24c61507481a91a0dd6afac4f97626a4e5ea780`. Nenhuma origem, escala ou datum paralelo foi introduzido. OSM/DEM/satélite existentes foram reaproveitados; não se repetiu a fundação B76 nem se substituiu DEM.

Quatro novas consultas Street View foram adquiridas pelo pipeline Aleph e suas imagens efetivamente inspecionadas. Cada captura tem relatório, coordenada retornada pelo provedor, panorama, orientação, data quando disponível, hash, arquivo bruto e classificação `DEV_REFERENCE_ONLY` nos catálogos centrais. As três consultas superiores mostram estruturas temporárias de evento/obra em dezembro de 2024, sem revelar o interior necessário. A quarta retornou panorama a aproximadamente 24,39 m da coordenada solicitada, na Ladeira da Montanha: proximidade XY não prova acesso ao desembarque superior. Não foi usada como medida do saguão.

Foram conferidas também fotografias locais catalogadas de acesso, revestimentos, rocha exposta e placa da restauração. A placa registra fevereiro de 2025; por isso equipamentos/estruturas vistos na captura anterior não foram classificados automaticamente como arquitetura permanente.

O texto indexado da [dissertação disponibilizada pela UFBA](https://repositorio.ufba.br/handle/ri/24863), p. 183, menciona passadiço histórico de 6,00 × 28,70 m e figuras de levantamento cadastral de 2000. A abertura do PDF integral falhou: as plantas não foram inspecionadas ou escaladas. É uma dimensão documental histórica secundária, **não comprovação do vão livre atual, soleira ou interior da cabine**.

| Classe | Evidência disponível | Uso permitido nesta revisão |
|---|---|---|
| Fato observado | Conteúdo das imagens inspecionadas; placa de restauração; presença de estruturas temporárias | Contexto e separação entre permanente/temporário, sem derivar dimensões ocultas |
| Documento histórico | Passadiço 6,00 × 28,70 m, texto indexado UFBA | Controle histórico; não certifica acesso ou cabine atual |
| Estimativa independente | Nenhuma suficiente para corrigir lajes/poço | Nenhuma dimensão numérica promovida por inferência |
| Candidato | Implantação SSOT e dimensões/cotas da cena | Auditoria interna e preparo de contrato |
| Desconhecido | Largura livre do acesso/portas; posição real de portas; gap e relação soleira/cabine; espessura/posição de lajes; cobertura interna; cabine W/D/H; abertura/folga do poço; alinhamento físico dos desembarques | Valores reais `null`; gate bloqueado |

Registro auditável: `world/areas/mvp-centro-lacerda/upper-boarding-evidence-b80.json`. Não foram inferidos contrapesos ou estruturas internas a partir de imagens externas. As medições das malhas no relatório de investigação são candidatas da cena; extents locais não são comprimentos físicos medidos.

## Comparação B78 × B79

A B78 alterou sete malhas: dois retornos posteriores, seus dois lambris, seus dois rodapés e a verga sobre a passarela. Tentou fechar aberturas laterais de 1,70 unidade entre um saguão de 9,40 e uma passarela de 6,00 unidades. Não corrigiu cabine, abertura do poço, plataformas ou cobertura que aparecem no CCD B79.

Comparação explícita de fingerprints das sete malhas confirma diferenças geométricas, mantendo transforms e materiais correspondentes. A largura histórica de 6 m sustenta somente uma referência geral da passarela; não comprova posição atual dos retornos nem fechamento arquitetônico exato. A migração permanece `NEEDS_REVIEW`, sem merge. Mesmo que posteriormente comprovado, esse fechamento lateral não resolve as interferências da viagem da cabine.

Evidência: `docs/reports/blender/lacerda-controller-b80/upper_investigation_b80.json` e baseline `docs/LACERDA_JUNCTION_B78.md`.

## Correção aplicada

O collider anterior `B77 | COLLISION | NAV | passarela superior` vinha de um plano NAV em Z aproximadamente 70,115, enquanto o piso paginado visual está em aproximadamente 70,123. O binding antigo foi preservado, mas marcado `enabled: false`, `superseded_floor_plane` no perfil central. O adaptador deve respeitar bindings habilitados; não selecionar todo objeto de uma coleção cegamente.

O novo `B80 | COLLISION | passarela piso visual` contém 660 triângulos da superfície superior real avaliada do piso paginado. Fonte explícita, sem copiar toda a malha visual. A validação após reabertura mediu distância máxima zero entre vértices do collider e a superfície-fonte.

A trajetória superior manteve o mesmo traçado XY. Foram derivados 901 pontos com pés acompanhando superfícies existentes e a pele de contato candidata de 0,015 já presente no contrato do personagem. A maior mudança em Z foi 0,138008 unidade de cena; não é correção de relevo nem medida de obra. Nenhum vão recebeu piso artificial. A trajetória candidata trata contato com faces/arestas reais; **18 pontos ainda exigem verificar apoio da parte arredondada do pé e comportamento de gravidade/step na engine**.

O objeto `B80 | NAV | superior ground-following candidato` é evidência cinemática, não controller físico. As duas adições ficam semanticamente separadas e fora do render. O recurso derivado `derived:upper-ground-b80` permanece pendente de verificação, equivalente a `REPLACE_BEFORE_RELEASE` pela política central.

## Validação e gates

Os relatórios finais da cena salva ficam em `docs/reports/blender/lacerda-controller-b80/`:

- `validation_b80.json`: reabertura, preservação de objetos/fontes/SSOT e coincidência do collider com piso visual.
- `ground_following_b80.json`: alterações dos pés e 18 apoios pendentes.
- `cabin_sweep_b80.json`: CCD contínuo dos componentes completos, não somente centro da cabine.
- `character_sweep_b80.json`: cápsula completa, cabeça/corpo/pés, trajetória superior e regressão inferior.
- `triage_b80.json`: testemunhas sólidas separadas de contatos/tangência; fontes OSM da travessia.
- `contract_proof_b80.json`: verificações dirigidas do protocolo e planner; não substituem física de engine.
- `actual_states_b80.json`: dez combinações desembarque/estado exportado; gate certificado permanece bloqueado mesmo quando o predicado geométrico superior é candidato.
- `provenance_gate_b80.json`: seis recursos candidatos/temporários rejeitados como esperado pela política; nenhum pacote criado.

| Verificação | B79 | B80 salva/reaberta |
|---|---:|---:|
| Pares componente/obstáculo em contato no CCD da cabine | 54 | 54 |
| Testemunhas de penetração sólida | 27 | 27 |
| Trechos superiores com penetração da cápsula | 8 | 0 |
| Trechos inferiores com penetração da cápsula | 9 | 9 |
| Apoios superiores ainda pendentes do solver físico | Não certificados | 18 |
| Movimento aprovado pelo contrato | Não | Não |

Na B80, o sweep superior registra zero intervalos indeterminados e zero ausências de apoio nas três amostras de cada segmento. Essas amostras não certificam apoio contínuo: os 18 pontos da derivação do ground-following continuam pendentes. O CCD da cabine cobre 904.535 pares de triângulos candidatos; não houve alteração das fontes de interferência. Os números contam pares/testemunhas ou trechos, não 27 defeitos arquitetônicos independentes.

O CCD cobre os 38 componentes visíveis da cabine no percurso exportado. Geometria interna oculta/desconhecida e contenção sólida não convexa não recebem aprovação por ausência de contato superficial. Contatos sem testemunha sólida permanecem `NEEDS_REVIEW`; não são tratados automaticamente como erro. Interseções sólidas comprovadas bloqueiam partida, mas ainda não autorizam uma correção arquitetônica sem evidência independente.

O sweep superior sem penetrações contra triângulos exportados melhora a trajetória B79, que tinha oito trechos penetrando piso/soleira. Isso não prova apoio contínuo, gravidade, atrito, slide, step, carry da plataforma móvel, tolerâncias da engine ou dimensões construtivas reais. O trecho inferior permanece uma regressão, sem fechamento do percurso anunciado.

Contrato temporal preservado: porta fechada bloqueia acesso; cabine ausente bloqueia o poço; partida exige portas fechadas, portal vazio, ocupação suportada e sweep aprovado; portal ocupado impede fechamento; estados desconhecidos bloqueiam. A aresta de embarque exige adicionalmente `upper_reference_verified`, ainda desconhecido. Planner com esse gate `false` ou `null` não encontra rota. Serviço vertical permanece separado de caminhada pelo poço.

**A animação herdada na timeline continua uma demonstração e não foi convertida em controller intertravado.** `movement_enabled: false` no relatório da cena refere-se ao contrato, não à remoção de keyframes. Dar Play não constitui autorização física de viagem.

## Cairu/Mercado e próximo passo

A travessia OSM `way/395865976` é mantida como referência com seu ID explícito; proximidade da rota não comprova binding. Três encontros com vias (`46348179`, `978525930`, `1004133497`) precisam de vínculo da travessia e permissão de tráfego. Nenhuma faixa nova foi criada ou alinhada por proximidade. Desembarque inferior, meios-fios e entrada do Mercado continuam pendentes, sem deslocar o foco antes do gate superior.

O próximo passo continua sendo obter planta/corte ou levantamento independente do embarque e poço para determinar quais lajes/cobertura são realmente incorretas. Depois, corrigir somente o erro comprovado e repetir CCD/cápsula com gravidade e apoio real. O adaptador `slice-engine-contract-b80.json` especifica os testes de engine necessários. Lapa, Campo da Pólvora, Dique e Fonte Nova permanecem em greybox; nenhum detalhe cosmético ou exportação para produção foi realizado.
