# Lacerda — reconciliação estrutural superior B98 — 07/10/2026

## Cena utilizada e preservação das modificações

Inspeção da janela existente PID16912/MCP9876: B97 salva, hash igual ao catálogo, sem edição pendente; 605 componentes comparados, nenhuma divergência de geometria/transform/material. Não houve recarga nem substituição de trabalho do usuário antes da alteração. Depois da modelagem, B98 salva e reaberta na mesma janela, hash `64bc2ddfacbfe166f10d4cdffcb6b7e41a70b2ec878dd1b92074246f81b5b2ee`; arquivo `blender/salvador_lacerda_r30b98_frente_superior_reconciliada.blend`. B76–B97 preservadas, SSOT inalterado.

## Correções efetivas

- A frente térrea anterior conservava seis pilares, cinco vãos e esquadrias/persianas na linha X quase constante, extrapolando os limites das circulações documentais. Foi substituída na apresentação ativa por quatro apoios derivados dos contornos estruturais da prancha17: curvas1751/1758/1738/1743. Agora acompanha a linha oblíqua da frente e os intervalos reais do desenho, em vez de escalar a frente antiga inteira.
- Três vãos entre os apoios reconstruídos: dois volumes simples de porta de rolo nas posições indicadas na17 e um vão central aberto. Cabeceiras segmentadas encostam nos apoios, sem uma barra atravessando as passagens. Não cria salão/interior novo por dedução de área.
- Apoios/cabeceiras reconciliados com piso70,123008728 e face inferior da cobertura73,873008728. Topo documental da cobertura +4,00m continua preservado. Contato entre peças é esperado, não interseção defeituosa automaticamente.
- A marquise antiga estava acima da cobertura em0,957m e mantinha uma extensão herdada incompatível com o conjunto atual. Preservada integralmente como referência substituída; não foi inventada projeção nova sem controle documental.
- Nove meshes novas; 68 peças antigas preservadas com geometria/transform/material intactos e fora da apresentação ativa. Sem deslocar torre, geografia, terreno, Hero asset inteiro, poço, cabine ou B82. Bindings atingidos ficam invalidados/desabilitados, sem duplicação de collider.

## Precisão e limite da conclusão

XY usa vetores/cotas já catalogados da17 e o referencial arquitetônico relativo B88. Não constitui registro absoluto aceito no SSOT. Pequenos rebaixos das extremidades dos pilares foram simplificados para estrutura jogável e estão documentados nos controles. Não são seção de concreto/armadura ou as-built certificados.

Abertura vertical2,69m é candidata herdada das folhas antigas, não cota documental. Espessura de cobertura0,25m também herdada/candidata. As portas de rolo são massas simples: montagem e subdivisão fina não aprovadas. Todos os componentes têm `replacement_required=true`, `production_ready=false`, fonte/controle/proveniência registrados. Nenhuma medida desconhecida foi apresentada como real comprovada.

## Verificação

- 614 componentes de arquitetura conferidos; 335 visíveis sem face degenerada/aresta não manifold/winding inconsistente/duplicata interna no escopo auditado. 605 assinaturas anteriores intactas.
- Nove contornos/cotas conferidos contra os controles, máximo residual numérico 0.00000067m. Esse residual prova aplicação relativa do controle, não erro real de implantação/as-built.
- 163 sondagens de superfícies, 60 de fechamentos e 15 de portal; interfaces B94–B97 preservadas.
- Cápsula raio0,30/altura1,80/skin0,015: CCD conservativo local do interior do novo vão, 1 intervalos aprovados contra as nove peças. Apoio medido no piso real. Não é simulação de gravidade/controller, validação da praça inteira, acesso à cabine ou trajeto Tomé–Mercado.
- Capturas reais da mesma cena: `artifacts/lacerda-live-diagnostic/b98-frente.png`, `b98-conjunto.png`, `b98-map.png`. Janela final no mapa completo, terreno visível, sem edição pendente.

## Pendências que não podem ser declaradas finalizadas

`LACERDA_VERTICAL=BLOCKED_EXTERNAL_EVIDENCE`; 27 testemunhas B80 `UNRESOLVED`; `movement_enabled=false`; GAMEPLAY_PROXY B82 preservado e separado. Interface inferior/datum com terreno continua NEEDS_REVIEW, com divergência3,857m documentada naB93. Instalação atual depende de as-built/processoSEMOB151228/2023/Contrato008/2023 ou levantamento equivalente. Esta rodada não reabre essa investigação, não deforma terreno e não promove produção.

A frente superior foi reconciliada nesta rodada. O elevador completo **não está arquitetonicamente certificado nem liberado para controller**; chamá-lo de finalizado apagaria pendências reais. Lapa, Dique, Fonte Nova e demais regiões não alteradas. Auditoria aplicada em `docs/reports/blender/lacerda-completion-b98/`.
