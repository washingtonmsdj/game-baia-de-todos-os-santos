# Handoff Geral do Codex — Bay of All Saints

## 03/10/2026 — Rondesp V24: potência dos faróis e fronteira com runtime

Fonte ativa: `blender/assets/vehicles/rondesp-pickup/marrom_v24_farois.blend`, cena `VIATURA | Rondesp Hilux farois v24`, SHA-256 `362783bb439f3f26d337c477bccdc955790b448fc5e25cb72f2db6be043945db`. V23 preservada com hash conferido. Feixes dianteiros passam de parâmetro de potência 120 para 2400 por luz SPOT (20 vezes), mantendo direção e abertura. É potência de iluminação Blender, sem equivalência com consumo elétrico ou medição fotométrica de fábrica. Reforçados núcleo/guia/lente emissivos; `intensidade_farois` no root multiplica potência/emissão. `farois_ligados` continua 0/1. Conferência: desligado 0/0; ligado 2400/2400; reabertura confirmou intensidades. Capturas da viewport antes/depois mostram iluminação mais forte do piso à frente.

MCP 9876 na única janela PID 19576. Fonte salva/reaberta; hashes do corpo e quatro folhas preservados; demonstração V23 e demais luzes mantidas. Relatório: `docs/reports/blender/rondesp_farois_v24.json`; imagens `artifacts/vehicles/rondesp/v24-farois-*-viewport.png`. Janela atual Renderizado com reprodução ativa; fonte salva MATERIAL para preservar cores ao reabrir.

Esclarecimento ao usuário: o ciclo automático de apresentação é uma demonstração, não a lógica do veículo jogável. Malhas, pivôs, materiais compatíveis, posições/cores das luzes e movimentos de portas amostrados são candidatos a reaproveitamento. Drivers Python e compositor do Blender não executam na engine. Runtime precisará ligar as luzes aos estados/entradas do veículo, controlar pisca/freio, calibrar intensidades/sombras e implementar bloom. Exportação glTF pode levar luzes punctual quando habilitada e suportada no destino; transforms animados podem ser amostrados. Materiais procedurais que não forem compatíveis precisam de adaptação/bake. Nenhuma importação, exportação ou integração foi validada nesta etapa. Sem engine definitiva imposta, alteração de production.json, npm, testes, build ou commit.


## 03/10/2026 — Rondesp V23: demonstração visível de portas e luzes

Fonte ativa: `blender/assets/vehicles/rondesp-pickup/marrom_v23_demonstracao.blend`, cena `VIATURA | Rondesp Hilux demonstracao v23`, SHA-256 `d81c32eaa60ec275bd85372cfe225499e17ad955db90c0f3e71f46ab15e262f1`. V22 preservada com hash conferido. Usuário não via luzes: inspeção encontrou prévia de material com estúdio forte; reabertura da versão salva em Renderizado voltou a Sólido. Fonte final V23 salva em MATERIAL, confirmada na reabertura, e janela atual explicitamente colocada em RENDERED com compositor ALWAYS. Estúdio reduzido, emissão/iluminação do giroflex reforçada e alternância mais lenta. Três capturas da própria viewport comprovam azul, vermelho e quatro portas abertas.

Timeline 1–240, 24 fps nominais, FRAME_DROP para acompanhar o tempo disponível da viewport. Quatro portas abrem, aguardam e fecham, com vidros, espelhos e inscrições ligados aos pivôs existentes. Frame 1: fechadas; frame 90: todas abertas a 65 graus; frame 190: fechadas. Freio também alterna na demonstração. `RDP01_ROOT | viatura` → `demonstracao_ativa=0` devolve abertura/freio aos controles manuais originais; `abertura_graus` fica nos quatro pivôs. As folhas, eixos, parentagens e carroceria permanecem preservados. Não equivale a auditoria de colisão da montagem completa.

Única janela PID 19576, MCP 9876. Fonte salva/reaberta, hashes da malha protegida conferidos. Reprodução real amostrada por timer temporário de leitura: movimento das folhas e duas cores observados; callback encerra sozinho após 12 amostras. Relatório: `docs/reports/blender/rondesp_demonstracao_v23.json`; imagens `artifacts/vehicles/rondesp/v23-*-viewport.png`. Espaço pausa/reproduz; Z → R ativa iluminação completa depois de reabrir. Granulação inicial da prévia EEVEE durante acumulação não é defeito da malha. Sem npm, suíte de testes, build, commit ou exportação runtime. Acabamento fino segue candidato.


## 03/10/2026 — Rondesp montada: encaixes e luzes V22

Fonte ativa: `blender/assets/vehicles/rondesp-pickup/marrom_v22_luzes.blend`, cena `VIATURA | Rondesp Hilux marrom v22`, SHA-256 `13ec4cfb77c2597de25b487fd61deb17c04ecfc8cbf326c1a1cde4301bf527ea`. Revisões V20 e V21 preservadas e hashes conferidos. Montagem V21 (`blender/assets/vehicles/rondesp-pickup/marrom_v21_montada.blend`, SHA-256 `41c5833edb6350c83d1e23900d1d2347b628909f86804829bca7b1271d2cc581`) restaurou rodas, chassi, interior, capota, equipamentos, materiais marrons e inscrições; vidros/espelhos/textos das portas acompanham os pivôs. Materiais procedurais e letras em geometria, sem alegar textura fotográfica aprovada.

V22 ajustou 22 acessórios, incluindo lanternas traseiras, puxador, terceira luz, para-choque, suportes dianteiros e engate. Alojamentos e travessa/prolongamentos de suporte separados do corpo. Giroflex azul no lado esquerdo do veículo e vermelho no direito, com piscadas alternadas por drivers; faróis com feixes, posição traseira e freio independentes. Controles em `RDP01_ROOT | viatura`: `giroflex_ligado`, `farois_ligados`, `lanternas_ligadas`, `freio` (0/1), mais `giroflex_velocidade`. Na viewport, Z → M mostra emissão; Z → R mostra também os feixes e reflexos. Espaço inicia/pausa as piscadas pela timeline.

Aplicação pelo MCP 9876 na única janela Blender PID 19576. V22 salva/reaberta; fingerprints do corpo e quatro folhas preservados. Intensidades conferidas nas duas fases do sinalizador e com freio acionado; vistas finais inspecionadas. Relatórios: `docs/reports/blender/rondesp_marrom_v21.json` e `docs/reports/blender/rondesp_marrom_v22.json`; imagens `artifacts/vehicles/rondesp/v22-*.png`. Acabamento fino, capota, brasão e padrão policial permanecem candidatos; sem certificação industrial. Drivers/material Blender não equivalem à implementação no jogo. Sem npm, testes, build, commit ou exportação runtime.


## 03/10/2026 — Hilux: espessura interna e superfície externa V20

Fonte ativa: `blender/assets/vehicles/rondesp-pickup/hilux_chapa_v20.blend`, cena `HILUX | chapa e portas v20`, SHA-256 `7bd84c96d4392a73d2fd1c603f738274046022712c8abebea31d9756907494e1`. V19 e demais revisões preservadas. Comparação ao vivo separou superfície, espessura e normais: a faixa ondulada acima do vidro traseiro desaparece ao desligar a espessura ou mantê-la toda para dentro. Corrigido Solidify para offset −1, normais de alta qualidade, espessura candidata de 2,5 mm; adicionado Weighted Normal por área e ângulo conservando arestas marcadas. Não houve alteração dos vértices, faces, contornos ou portas.

MCP restabelecido na porta **9876**, conforme informado pelo usuário, na única janela PID 19576. A cena padrão dessa janela foi preservada em `artifacts/vehicles/rondesp/v20-recovered-default-scene.blend` antes de abrir a Hilux. V20 salva e reaberta; malha base comparada à geometria V19 e fingerprints das malhas preservados. Conferência de 0, 5 e 70 graus: zero penetração estrita detectada entre folhas/carroceria avaliada ou entre folhas; amostragem não certifica varredura contínua. Vistas neutras e linhas de reflexo publicadas. Relatório: `docs/reports/blender/hilux_chapa_v20.json`. Superfície candidata para avaliação do usuário; não declarar réplica perfeita ou aprovação industrial. Sem npm, suíte de testes, build, commit ou exportação.

## 03/10/2026 — Hilux V19: ondulações ainda pendentes

Usuário apontou ondulações no encontro do teto e painel posterior. V19 passa a `needs_review`; inspeção topológica anterior não constitui aprovação da superfície. Nenhuma nova mutação aplicada nesta tentativa: MCP OrdaX retorna `Transport closed`; fallback 9877 recusou conexão e não há listener no PID Blender 16304. Recuperação por computer-use também falhou em `list_apps`, inclusive após reset. Preservada a única janela e o arquivo V19.

Diagnóstico read-only: `docs/reports/blender/hilux_ondulacoes_v20_pending.json`. Comparação reversível preparada em `automation/blender/diagnose_hilux_ripples_v20.py`, ainda não executada. Próximo passo é reconectar o MCP na janela existente e conferir perto o encontro traseiro, incluindo forma da chapa e normais; não salvar V20 nem promover acabamento sem resultado visual convincente.

## 03/10/2026 — Hilux: cabeceira e capô V19

Fonte ativa: `blender/assets/vehicles/rondesp-pickup/hilux_superficies_v19.blend`, cena `HILUX | superficies e portas v19`, SHA-256 `af484a3fcda12649e07a3ed4bd53c64b3233845b6878a56d557e174498bde540`. V18 preservada. Correção do recuo da coluna B que deformava a faixa acima das portas; retorno interno com linhas de suporte entre Z 1,750 e 1,758 m. Capô com coroamento adicional candidato de até 24 mm e arredondamento local de 8 mm. Quatro portas, pivôs e peças reservadas preservados.

Edição pelo fallback MCP na única janela visível, PID 16304; revisão salva e reaberta. Malha final sem faces degeneradas/duplicadas, arestas com mais de duas faces, winding inconsistente, vértices coincidentes ou junções em T nos critérios da inspeção. Cinco poses (0, 2, 5, 10, 70 graus) sem penetração estrita detectada entre portas/carroceria antes do último microacabamento de menos de 0,02 mm. Não equivale a varredura contínua. Relatório: `docs/reports/blender/hilux_superficies_v19.json`. Sem npm, suíte de testes, build, commit ou exportação runtime. Acabamento permanece candidato.

## 03/10/2026 — Hilux: portas independentes e coluna B interna V18

Fonte explícita: `blender/assets/vehicles/rondesp-pickup/hilux_portas_v18.blend`, cena `HILUX | carroceria e portas v18`. SHA-256: `0facd4dd74797aec7f2051d8b445019fb9ea310ee762e71677390647b0e8e260`. V17 preservada com hash conferido; montagem V11 mantida. Oficina agora mostra carroceria fixa, quatro portas e suas ferragens; vidros, rodas, chassi, capota policial, inscrições e demais conjuntos permanecem reservados.

As quatro folhas foram refeitas com chapa externa curva, caixilho integrado, dobra periférica e estampagem interna com abertura de serviço. Maçanetas, canais das janelas e vedações acompanham cada porta. Geometria refletida entre os lados, com malhas e movimento independentes, mantendo nomes dos objetos e pivôs existentes. Dobradiças possuem folhas fixas/móveis e pinos; o controle `abertura_graus` no pivô aceita 0–70 graus, com sentido oposto nos lados. Portas salvas fechadas.

Correção solicitada a partir da lateral Hilux catalogada: as portas cobrem a coluna B estrutural e se encontram por fora numa junta candidata de 4 mm. Recuo localizado de 537 vértices da coluna/encontros, com identidade de painéis preservada; corpo continua em uma malha com Mirror X. O contorno das janelas foi compatibilizado com as folhas e a estrutura interna recuada 10 mm do bordo externo para liberar os batentes. Dimensões e posição dos eixos são parâmetros de modelagem candidatos, sem levantamento industrial.

Conferência de 13 poses, inclusive portas dianteiras/traseiras abrindo separadamente: zero penetração estrita detectada entre folhas ou contra a carroceria avaliada com Mirror e espessura. Zero auto-interseções detectadas nas folhas, faces degeneradas, arestas soltas, junções triplas ou orientação incoerente. Reflexão dos vértices esquerda/direita sem diferença na tolerância numérica observada. Arestas abertas das aberturas de serviço são intencionais. Corpo mantém 42.610 vértices/46.278 faces; portas dianteiras 4.372/7.534, traseiras 3.847/6.524. Não há certificação de varredura contínua ou da remontagem das peças reservadas.

Aplicação inicial por OrdaX MCP na janela PID 4160. Após perda de transporte e encerramento dessa janela, checkpoint V18 recuperado em uma única janela visível PID 16304, com BlendMCP 1.4.4 na porta 9877. A rejeição de auditoria simultânea foi respeitada; operações seguintes ocorreram sequencialmente após confirmação da recuperação. Wrapper `tools/blendmcp/run_vehicle_script.py` confere arquivo/hash/PID do asset sem alterar o contrato da cidade. Fonte final salva/reaberta, hash e quatro controles fechados conferidos.

Relatório: `docs/reports/blender/hilux_portas_v18.json`; inventário e geometria: `artifacts/vehicles/rondesp/v18-doors-before.json` e `v18-doors-audit.json`; cinco vistas `v18-*.png`. Scripts aplicados: `model_hilux_doors_v18.py`, `join_hilux_door_seams_v18.py`, `conceal_hilux_hinges_v18.py`, `finish_hilux_door_returns_v18.py`, `finish_hilux_front_hinge_v18.py`, `save_hilux_doors_v18.py`. Não repetir mutações sobre a fonte final. Inspeção: `audit_hilux_doors_v18.py`; vistas: `review_hilux_doors_v18.py`. Sem npm, testes, build, exportação runtime ou commit, conforme pedido. Direção e rodagem continuam adiadas.


## 03/10/2026 — Hilux: conexões da chapa e retopologia V17

Fonte explícita: `blender/assets/vehicles/rondesp-pickup/hilux_carroceria_v17.blend`, cena `HILUX | carroceria isolada v17`. Hash SHA-256: `58d0b48616c03f3b6c5cf50fcdf00bc2cfa02921667aee732285e57b189eb7d3`. V16 preservada com hash anterior conferido; montagem V11 mantida. Somente `HILUX | CARROCERIA PRINCIPAL` visível, metade +X e Mirror X com clipping; portas, rodas, chassi, vidros, capota e equipamentos continuam separados e ocultos.

Cabeceira externa da caçamba ligada ao retorno superior, eliminando a junção tripla com sua parede interna. Soleira refeita como percurso contínuo entre armação e assoalho; transição do piso ao painel posterior e cowl ligados às respectivas bordas. Tampa externa usa as mesmas estações das dobras. Retiradas 17 faces da flange da grade que duplicavam parte do encaixe do farol. Retopologia localizada conserva os contornos e pontos de controle do para-lama e da frente, retirando faces dobradas. Retorno frontal reconstruído entre os limites efetivos da frente, capô e para-lama; canto dos retornos do para-brisa recebe mitra comum. Estações finais da caçamba ajustadas para folga candidata de 6 mm da face interna da tampa; o parâmetro está registrado, sem alegar medida de fábrica.

Auditoria da malha base: arestas com mais de duas faces **53 → 0**, orientações incoerentes **221 → 0**, pontos intermediários desconectados em bordas **148 → 0**. Zero faces degeneradas/duplicadas, arestas soltas ou vértices coincidentes na tolerância auditada. Inspeção final não encontrou penetração não local entre chapas; dois contatos numéricos em arestas efetivamente compartilhadas foram classificados como contato com tolerância de 1 µm. As bordas dos vãos, centro do Mirror e juntas físicas não são defeitos a fechar automaticamente. Esta auditoria não certifica dimensões industriais nem o encaixe dos conjuntos reservados ou toda a malha avaliada por modificadores.

Aplicado via MCP na única janela Blender visível, PID 4160. Revisão salva/reaberta, 42.610 vértices e 46.278 faces de autoria, hash conferido e oito vistas revisadas. Relatório: `docs/reports/blender/hilux_carroceria_v17.json`; evidências: `artifacts/vehicles/rondesp/v17-mesh-before.json`, `v17-mesh-after.json`, `v17-intersections.json` e `v17-carroceria-*.png`. Fidelidade e parâmetros permanecem candidatos de modelagem. Rig, remontagem e exportação continuam adiados. Sem npm, testes, build ou commit, conforme pedido.

Scripts aplicados, não repetir: `polish_hilux_structure_v17.py`, `finish_hilux_intersections_v17.py`, `finish_hilux_joints_v17.py` e `save_hilux_body_v17.py`, em `automation/blender/`. Scripts de leitura: `inspect_hilux_mesh_v17.py` e `inspect_hilux_intersections_v17.py`; vistas: `review_hilux_body_v17.py`. Checkpoints não são fontes ativas. Durante a sessão, o worker `ordax_studio.workbench_bridge` monopolizou o lock global sem comandos na fila Blender; recuperação restrita a esse helper, com a janela Blender preservada. As mutações da cena ocorreram pelo MCP.



## 03/10/2026 — Hilux: caçamba contínua e encontro frontal V16

Fonte explícita: `blender/assets/vehicles/rondesp-pickup/hilux_carroceria_v16.blend`, cena `HILUX | carroceria isolada v16`. V15 e montagem V11 preservadas. Continua visível somente a carroceria com Mirror X; portas, rodas, chassi, vidros, capota e acessórios ficam separados e ocultos.

Caçamba reconstruída com as mesmas estações na lateral, borda enrolada, parede interna, piso e caixa de roda. Cabeceira ligada ao piso e às laterais, fechos das bordas dianteira/traseira e dobras que acompanham os arcos. Volume lateral regularizado, preservando a junta física com a cabine e o encaixe candidato da tampa. Chapa frontal ligada ao contorno existente do capô por 57 arestas compartilhadas; faixa abaixo dessa borda regularizada. Cabine e tampa mantidas. Identidade das faces em `boas_panel_id`.

Aplicado na única janela Blender visível; revisão salva/reaberta, hash conferido e oito vistas revisadas. Relatório: `docs/reports/blender/hilux_carroceria_v16.json`; imagens: `artifacts/vehicles/rondesp/v16-carroceria-*.png`. Contornos finos da cabine/frente e encaixes dos conjuntos reservados continuam candidatos. Dobradiças, direção e rodagem adiadas. Forma e raios são interpretação autoral das referências catalogadas, sem medidas de fábrica. Sem npm, testes, build, exportação runtime ou commit, conforme pedido.

Scripts aplicados, não repetir: `rebuild_hilux_bed_v16.py`, `align_hilux_front_v16.py`, `finish_hilux_front_band_v16.py` e `save_hilux_body_v16.py`, em `automation/blender/`. `review_hilux_body_v16.py` gera oito vistas, `review_hilux_front_v16.py` duas vistas frontais. `inspect_hilux_shell_v16.py` lê contornos. Checkpoints em `artifacts/vehicles/rondesp/` não são fontes ativas; o inventário `v16-contours-live.json` usado no acabamento frontal corresponde à etapa anterior a esse acabamento. Guia: `world/vehicles/hilux-body-editing.md`.


## 03/10/2026 — Hilux: armação contínua da cabine V15

Fonte explícita: `blender/assets/vehicles/rondesp-pickup/hilux_carroceria_v15.blend`, cena `HILUX | carroceria isolada v15`. V14 e montagem V11 preservadas. Uma carroceria visível, metade +X com Mirror X; portas, rodas, chassi, vidros, capota e acessórios seguem separados e ocultos.

Substituídos os painéis independentes da cabine por armação lateral A/B/C com vãos completos, teto e painel posterior que compartilham os contornos. Cantos C arredondados, vão do vidro traseiro aberto e retornos dos batentes ligados à armação. Perfil lateral regularizado, retorno contínuo do para-brisa e dobra localizada no encontro teto/lateral; corrigidos os dentes na borda A e a mistura de normais nas dobras internas. Mantidas as chapas de caçamba e frente da V14, a junta física cabine/caçamba e a identificação de faces `boas_panel_id`.

Aplicado na única janela Blender visível; fonte salva/reaberta, hash conferido e sete vistas revisadas. Relatório: `docs/reports/blender/hilux_carroceria_v15.json`; vistas: `artifacts/vehicles/rondesp/v15-carroceria-*.png`. Contorno e transições finas da chapa continuam candidatos; conferir o encaixe das peças reservadas ao remontar. Dobradiças, direção e rodagem permanecem adiadas. Parâmetros autorais, sem alegar medidas de fábrica. Sem npm, testes, build, exportação runtime ou commit, conforme pedido.

Scripts já aplicados, não repetir: `rebuild_hilux_cab_v15.py`, `finish_hilux_cab_v15.py`, `regularize_hilux_a_v15.py`, `finish_hilux_sheet_normals_v15.py`, `save_hilux_body_v15.py` em `automation/blender/`. `review_hilux_body_v15.py` gera vistas; `inspect_hilux_cab_v15.py` lê os contornos. Checkpoints em `artifacts/vehicles/rondesp/` não são fontes ativas. Guia: `world/vehicles/hilux-body-editing.md`.


## 03/10/2026 — Hilux: vãos, frente e cantos da caçamba V14

Fonte explícita: `blender/assets/vehicles/rondesp-pickup/hilux_carroceria_v14.blend`, cena `HILUX | carroceria isolada v14`. V13 preservada. Apenas a carroceria fica visível, com Mirror X; portas, rodas, chassi, vidros, capota e acessórios seguem separados e ocultos. Rig continua adiado.

Para-lama dianteiro reconstruído até a soleira, batente A ligado à chapa e soleira com retorno ao piso. Coluna A ganhou largura em Y/Z, seção B suavizada e coluna C com retorno interno. Flanges adicionadas nos encaixes de farol e grade. Tampa da caçamba acompanha a largura lateral por altura, com face interna e dobras alinhadas. Linha inferior da lateral traseira elevada suavemente e dobrada, removendo as pontas da deformação antiga. Faces identificadas por `boas_panel_id`, preservado após a solda.

Aplicado na única janela Blender visível; fonte salva/reaberta, hash conferido e cinco vistas revisadas. Relatório: `docs/reports/blender/hilux_carroceria_v14.json`; vistas: `artifacts/vehicles/rondesp/v14-carroceria-*.png`. Parâmetros autorais candidatos, sem alegar medidas de fábrica. Contorno fino, alguns encontros do teto e encaixe posterior das peças reservadas ainda precisam de ajuste. Sem npm, testes, build, exportação runtime ou commit, conforme pedido.

Scripts aplicados, não repetir: `automation/blender/refine_hilux_shell_v14.py` e `automation/blender/finish_hilux_shell_v14.py`. `review_hilux_body_v14.py` gera vistas da fonte na sessão visível. Checkpoints em `artifacts/vehicles/rondesp/` não são fontes ativas. O guia `world/vehicles/hilux-body-editing.md` acompanha esta revisão.

## 03/10/2026 — Hilux: correção das chapas e encontros V13

Fonte explícita de autoria no catálogo: `blender/assets/vehicles/rondesp-pickup/hilux_carroceria_v13.blend`, cena `HILUX | carroceria isolada v13`. V12 e montagem V11 preservadas. Mantido o pedido de trabalhar somente na carroceria: uma malha visível, Mirror X, portas, rodas, chassi, vidros, capota e equipamentos ocultos em peças reservadas.

Painel posterior da cabine reconstruído com vão de vidro arredondado, contorno curvo da coluna C e encontro com teto. Cabeceira da caçamba independente da chapa da cabine, preservando a junta física. Piso com estampagem longitudinal, paredes internas, caixas de roda e bordas superiores refeitos; superfícies duplicadas e 99 faces residuais nas bordas compartilhadas removidas. Retorno dianteiro substituído, lábios dos arcos refeitos e ponta A/teto alinhada. Corrigida a amplificação da espessura nas quinas. Identidade das faces registrada em `boas_panel_id`, pois grupos de vértices soldados não bastam para identificar os painéis.

Aplicado via MCP na única janela Blender visível, fonte salva e reaberta, hash conferido e vistas frontal, traseira e aproximada revisadas. Relatório: `docs/reports/blender/hilux_carroceria_v13.json`; imagens: `artifacts/vehicles/rondesp/v13-carroceria-*.png`. Referências internas já catalogadas: `hilux-srx-user-rear` e `hilux-2024-std-dealer-side`; dimensões novas são parâmetros autorais candidatos. Fidelidade fina do contorno e encaixe das peças reservadas seguem pendentes. Sem npm, testes, build, exportação runtime ou commit, conforme pedido.

Scripts aplicados, não repetir: `refine_hilux_shell_v13.py`, `finish_hilux_shell_v13.py`, `clean_hilux_v13_shared_edges.py`, `align_hilux_v13_roof_tip.py`. `review_hilux_body_v13.py` gera as vistas da fonte V13 na sessão visível. Scripts em `automation/blender/`; checkpoints em `artifacts/vehicles/rondesp/` não são fontes ativas.

## 03/10/2026 — Hilux: oficina da carroceria isolada V12

Pedido atual: trabalhar apenas na carroceria original da Hilux, sem portas,
rodas, chassi ou cobertura policial sobre a caçamba; recolocar os conjuntos
depois. Fonte de autoria explícita no catálogo:
`blender/assets/vehicles/rondesp-pickup/hilux_carroceria_v12.blend`, cena
`HILUX | carroceria isolada v12`. A montagem V11 e as fontes anteriores
permanecem preservadas.

Somente `HILUX | CARROCERIA PRINCIPAL` fica visível: uma malha de chapa fixa
com Mirror X, origem métrica preservada e metade +X editável. Caixilhos
separados das colunas; caçamba aberta com piso, paredes e caixas de roda
candidatas. Tiras antigas de batente que cruzavam os vãos removidas. Não há
união boolean nem collider gerado. Forma e interior ainda precisam de ajuste
fino; dimensões das novas chapas são autorais, não levantamento de fábrica.

Demais conjuntos estão separados e ocultos em `RDP01 | PECAS RESERVADAS`.
Portas/dobradiças, direção e rodagem ficaram adiadas conforme o novo escopo.
A tentativa inicial de rig falhou no Blender, foi descartada e a sessão foi
recuperada da V11 salva; nenhuma animação funcional foi promovida.

V11 corrigiu encaixes do teto, fechamento posterior da cabine, painéis da
capota e suportes do giroflex; preservada como snapshot de montagem no
catálogo. V12 salva/reaberta na única janela visível, com apenas uma malha
visível. Relatório: `docs/reports/blender/hilux_carroceria_v12.json`; vistas:
`artifacts/vehicles/rondesp/v12-carroceria-frente.png` e
`artifacts/vehicles/rondesp/v12-carroceria-cacamba.png`. Guia de edição:
`world/vehicles/hilux-body-editing.md`. Sem npm, testes, build, exportação
runtime ou commit, a pedido do usuário.


## 03/10/2026 — Rondesp: traseira e inscrições V10

Fonte candidata `blender/assets/vehicles/rondesp-pickup/marrom_v10.blend`; V09
preservada. Capota afunilada, painel traseiro inclinado, cantos curvos e
para-choque com asas arredondadas/rebaixo da placa. Letreiro mais pesado,
prefixo traseiro maior, 190 com telefone, RONDESP/LESTE nas laterais e POLÍCIA
no capô. Giroflex com lentes vermelhas e emissão estática, sem animação.
Brasões são simplificações vetoriais candidatas, não réplicas aprovadas.

Três fotos do usuário catalogadas em `world/vehicles/media-manifest.json`;
prefixos 2.1212/BTS e de outras viaturas não substituem a identidade 3.1110.
Dimensões da adaptação são autorais pela fotografia, não levantamento.
Fonte salva/reaberta via MCP na única janela. Relatório/hash em
`docs/reports/blender/rondesp_marrom_v10.json`; vistas em
`artifacts/vehicles/rondesp/v10-frente.png` e `v10-traseira.png`.
Scripts `refine_rondesp_v10.py` e `finish_rondesp_v10.py` já aplicados.
Sem npm, testes, build, exportação runtime ou commit, conforme solicitação.
Fidelidade final, brasão detalhado e camuflagem exata continuam pendentes.


## 03/10/2026 — Rondesp: carroceria candidata V09

Fonte `blender/assets/vehicles/rondesp-pickup/marrom_v09.blend`; V08 preservada.
Capô abaulado transversalmente, transição curva dos ombros, portas com coroa
longitudinal e inscrições conformadas, retorno lateral dos faróis e fechamento
interno das caixas de roda. Entre-eixos conferido: 3,085 m. Teto preservado após
reverter uma tentativa que produzia ressalto. Seções são interpretação das fotos,
não medidas de levantamento. Pesquisa da Hilux 2025 e RONDESP registrada no relatório;
catálogo Toyota 2024/2025 retornou HTTP 403 e não foi usado como medição nova.

Aplicação via MCP na única instância visível. Fonte salva/reaberta; revisão de
frente, lateral e traseira em `artifacts/vehicles/rondesp/v09-*.png`. Relatório:
`docs/reports/blender/rondesp_marrom_v09.json`. Scripts `refine_hilux_body_v09.py`,
`finish_hilux_body_v09.py`, `close_hilux_body_v09.py` já aplicados; não repetir.
`review_hilux_body_v09.py` somente gera vistas na instância visível. Checkpoints
intermediários em `artifacts/vehicles/rondesp/`; não são fontes de autoria.

Status candidate: fidelidade final ainda precisa de aprovação; brasão, camuflagem
exata, animação e runtime pendentes. Compileall passou; 62 testes aprovados;
registro de referências com zero erros e dois avisos existentes da cidade.
Sem commit/push, build ou exportação runtime.


## 03/10/2026 — Rondesp: fonte candidata V08

Fonte `blender/assets/vehicles/rondesp-pickup/marrom_v08.blend`, V07 preservada. Protetor frontal reconstruído com tubos curvos e suportes, sinalizador baixo sem módulos repetidos e acabamento dos refletores. Acessórios interpretados das fotos, dimensões não verificadas. Relatório/hash: `docs/reports/blender/rondesp_marrom_v08.json`. Script `automation/blender/refine_rondesp_front_v08.py`, aplicado via MCP na única janela, fonte reaberta. Sem render offline/npm/build/testes gerais; sem exportação runtime. Fidelidade final da carroceria, brasão e camuflagem exata continuam pendentes.


## 03/10/2026 — Hilux Rondesp: fonte candidata V07

Fonte: `blender/assets/vehicles/rondesp-pickup/marrom_v07.blend`; V06 preservada.
Correção local dos ombros dos para-lamas e continuidade com capô, encaixe teto/para-brisa, acabamento de peças moldadas e pintura menos brilhante. Script: `automation/blender/correct_hilux_v07.py`. Relatório/hash: `docs/reports/blender/rondesp_marrom_v07.json`. Fonte salva e reaberta na única janela; viewport conferido via MCP. Sem render offline, pesquisa, npm/build ou testes gerais. Status candidate: fidelidade final, brasão e camuflagem exata pendentes; sem integração runtime.


## 03/10/2026 — Hilux Rondesp: autoria candidata V06

Fonte explícita: `blender/assets/vehicles/rondesp-pickup/marrom_v06.blend`, cena
`VIATURA | Rondesp Hilux marrom v06`. Hash no catálogo e em
`docs/reports/blender/rondesp_marrom_v06.json`. V01–V05 preservadas; V04/V05
não atendiam à fidelidade solicitada. Não retomar essas bases pelo histórico.

V06 reconstrói a carroceria pelas referências existentes: caimento do capô,
ombros dos para-lamas, estreitamento da cabine no teto, vãos curvos das janelas,
chapas das portas, batentes/soleiras, grade STD, câmaras ópticas e lentes,
capota e lanternas. Inscrições da 3.1110 conformadas à superfície. Entre-eixos
mantido em 3,085 m; especificações nominais em `world/vehicles/hilux-dimensions.json`.
As seções da carroceria continuam interpretações de imagens com perspectiva,
não medidas de escaneamento; acessórios policiais não têm dimensões verificadas.

Revisão visual: frente, lateral, traseira e forma neutra em
`artifacts/vehicles/rondesp/v06-*.png`. Trabalho via MCP na única instância visível.
Scripts: `rebuild_hilux_reference_v06.py`, `finish_hilux_reference_v06.py`,
`present_hilux_v06.py`, em `automation/blender/`. Executam passes de modelagem;
não repetir um passe de acabamento na mesma revisão sem conferir seu escopo.

Status **candidate**, não approved e não declarado equivalente ao ônibus.
Pendentes: aprovação de fidelidade, brasão PMBA detalhado, camuflagem exata,
animação das portas e integração runtime. Sem pesquisa adicional, npm/build ou
testes gerais neste ciclo, conforme escopo solicitado; sem commit/push.


## 02/10/2026 — Hilux Rondesp: fonte V04

Fonte explícita: `blender/assets/vehicles/rondesp-pickup/marrom_v04.blend`, cena `VIATURA | Rondesp Hilux marrom v04`. V01–V03 preservadas como históricas; não retomar por maior sufixo ou mtime.

Carroceria reconstruída com seções curvas; revisão da frente, encaixes dos faróis, máscara STD, capô, portas, teto, caçamba, capota e rodas. Medidas nominais Toyota em `world/vehicles/hilux-dimensions.json`: comprimento 5,325 m, largura base 1,855 m, altura stock 1,815 m, entre-eixos 3,085 m e pneus 265/65 R17. Esses valores são especificações do veículo base; não levantamento dos acessórios policiais. Vistas SRX enviadas servem ao contorno, sem aplicar rodas/alargadores da SRX à viatura.

Status `candidate`: aprovação visual final, brasão e mapa exato da camuflagem pendentes; não exportado/integrado no runtime. Relatório `docs/reports/blender/rondesp_marrom_v04.json`; comparação visual em quatro vistas, sem npm/build/testes gerais nesta etapa, conforme pedido do usuário.

## 02/10/2026 — Rondesp: continuar pela V03

Fonte candidata `blender/assets/vehicles/rondesp-pickup/marrom_v03.blend`,
ID `vehicle-rondesp-pickup`. Não voltar à V01/V02 pelo arquivo aberto/mtime;
catálogo e hash em `world/vehicles/catalog.json` indicam a fonte.
As novas fotos enviadas documentam frente e traseira da Hilux 3.1110.
Corrigidos bind dos pivôs, aros de aço, capô/para-lamas, recortes dos faróis,
janelas arredondadas e camuflagem. Relatório da V03 em `docs/reports/blender/`.
Pendentes: brasão detalhado, dimensões verificadas, desenho exato da pintura,
animação completa com inscrição dividida por folha. Referências internas
creditadas a Sotero Filho/viaturas_ba_ no manifesto, licença pendente.
Fontes dos ônibus e produção do MVP preservadas; sem integração no runtime.

## 02/10/2026 — Variante azul do ônibus

Torino azul criado da mesma base amarela v06; amarelo e verde preservados.
Fonte: `blender/assets/vehicles/torino-31065/azul_v01.blend`; catálogo/hashes em
`world/vehicles/catalog.json`. Somente materiais externos e cor dos letreiros.
Geometria, dimensões, textos, três portas e anúncio traseiro mantidos.
Referência do usuário registrada em `world/vehicles/media-manifest.json`.
Scripts de cor compartilham `automation/blender/bus_color_variant.py`.
Conferência: `docs/reports/blender/torino_azul_v01.json`; runtime inalterado.


## 02/10/2026 — Ônibus por cor

Catálogo de autoria: `world/vehicles/catalog.json`, uma fonte por cor.
Amarelo v06 preservado; verde v01 em `blender/assets/vehicles/torino-31065/`.
Material externo alterado; malha, textos, portas, rodas e anúncio mantidos.
Não confundir a variante Torino com o Comil Svelto da referência de cor.
Registro de proveniência em `world/vehicles/media-manifest.json` e conferência
em `docs/reports/blender/torino_verde_v01.json`. Runtime não alterado.

## Versionamento de 02/10/2026

Sincronização inclui scripts, contratos, relatórios, revisões oficiais Blender,
fonte do carro V14 e GLBs por Git LFS. As revisões R30C rejeitadas, imagens locais
de referência, backups e pacotes Base64 de transferência ficam fora do Git;
nenhum arquivo local foi removido. Os importadores V7C/V8B usam primeiro seus
GLBs versionados, validando os mesmos hashes de origem. Fontes geográficas e
acervo visual pesado continuam externos, com proveniência nos manifests.

Validações para commit: compileall de tools/tests, 62 testes Python aprovados,
cadastro de referências com zero erros e dois avisos (bounds pendentes e
cobertura do cais da Praça Cairu). Sem npm/build ou promoção de B38 ao runtime.

## 02/10/2026 — Continuar pela B38: Conceição e colisor local

Fonte candidata: `blender/salvador_lacerda_r30b38_binding_conceicao.blend`, pai B37.
Ponteiro explícito no catálogo; produção/runtime continuam B30. Não exportar
automaticamente esta revisão nem reiniciar a partir da B23/B30.

O aparente degrau de 36 m da Conceição era binding do nó `7520527645` na pista
superior da Montanha, por deslocamento do fit XY candidato. Corrigido o ponto
da curva derivada `R30A7 | ROAD | 421206045` para apoio inferior, com metadados;
fonte OSM e curva autoral permanecem intactas. Não deformar Z para apagar o
resíduo do eixo errado nem transformar solo em pista sem evidência.

Refino localizado do proxy: 20 vértices novos; 910 amostras, erro máximo 4,02 cm.
5.255 componentes protegidos, terreno visual e larguras preservados. Replay com
carro V14 existente em trecho contínuo de cerca de 136 m: 1.135 frames/4.540 apoios
interpolados sem ausência; execução visível concluída em 45,52 s (97 updates).
Esse método é cinemático, com bitola/limite de esterço nominais registrados,
não física dinâmica nem prova de desempenho/colisão urbana completa.

Contato inicial de até 5,5 mm do envelope com a contenção foi corrigido por
adaptação suave do percurso de teste, até 3,5 cm nos últimos 12 apoios, dentro do
asfalto existente. `ADAPT_LOCAL` documentado; largura e geografia inalteradas.
Curva salva conferida novamente por biblioteca. Checagem lateral final: 3.420
raios sem contato; limitações/critério de amostragem registrados no relatório.

No Blender: coleção `GAMEPLAY | VALIDACAO | Conceicao B38`, timeline 1–1135,
25 fps; espaço reproduz o trecho. Carro/percurso são somente validação,
fora da exportação. Relatório: `docs/reports/blender/conceicao_binding_r30b38.json`.
Próxima pendência: curvas/extremos sem envelope contínuo confirmado. Não unir
runs independentes, sobretudo o run 239–250 que atingia a Montanha; largura
real continua `null`. Não criar retorno fictício para fechar circuito.

## 02/10/2026 — Continuar pela B37: fachadas da Cidade Baixa

Fonte candidata: `blender/salvador_lacerda_r30b37_fachadas_baixa.blend`, pai B36;
consultar `blender-revisions.json#/authoring_source`. Produção permanece B30.
Relatório: `docs/reports/blender/cidade_baixa_r30b37.json`.
Refinadas as três fachadas já existentes ao sul do acesso inferior:
OSM 1263035780, 1220650507 e 1220650503. IDs/plantas/cotas preservados;
paredes com espessura, caixilhos e vidros recuados, cornijas/peitoris,
venezianas verdes, nervuras e painéis cinza, toldo rosado com espessura/bandô.
Sem novas fachadas posteriores ou detalhes extrapolados da foto ilegível.

Mutação R37 já aplicada: não repetir o script. 318 componentes protegidos
inalterados. Os 18 componentes modificados foram relidos do arquivo salvo
na mesma instância; isso não equivale a recarregar a cena inteira nem a validar
gameplay. Duas vistas locais registradas. Binding fotográfico, dimensões reais
e fidelidade global continuam candidatos. B36 segue visualmente não aceita;
o usuário pediu prosseguir em outras áreas. Não ocultar essa pendência.
Sem pesquisa nova, exportação, npm/build ou testes gerais.

## 02/10/2026 — Continuar pela B36: terraços e galerias preservadas

Fonte candidata: `blender/salvador_lacerda_r30b36_terracos_palacio.blend`, pai B35;
consultar o ponteiro explícito em `blender-revisions.json`. Produção B30.
Relatório: `docs/reports/blender/terracos_palacio_r30b36.json`.

**Não remover ou deslocar as galerias anteriores.** Três arcos do palácio
restaurados da B35, dez do trecho oposto inalterados. A ligação nova ao terraço
é separada; dois vãos candidatos, contagem real `null`. `final_layout` registra
o estado final e prevalece sobre as etapas intermediárias do relatório.
Colunata inferior, pisos, lajes, abóbadas, escadas e colisores separados.
Escada da colunata no interior da laje; escadas do jardim no lado oposto às
galerias, com patamares e aberturas nas contenções/guarda-corpos.
Solo/proxy recortados nos interiores e perfil local recomposto até a borda
existente da ladeira. Não alterar vias/DEM para acomodar decoração.

Scripts R36 de mutação já aplicados: não executá-los novamente. Conferências
locais e reabertura constam no relatório quando concluídas. Esta candidata
não foi exportada, nem aprovada para gameplay. Medidas reais, implantação
fina dos terraços, jardins e fachada posterior continuam pendentes; não
extrapolar detalhes ilegíveis nas fotos.
Feedback final do usuário: o passe consumiu tempo excessivo e continua sem
fidelidade suficiente. Não considerar a candidata aprovada. Primeiro resolver
a implantação relativa do terraço, três arcos originais e encosta; não expandir
o trecho candidato ou acrescentar decoração para disfarçar diferenças.
A B36 salva foi registrada e reaberta pelo hash: `load_post` confirmado.
Após a reabertura houve demora de resposta; PID 28348 foi adotado novamente.
Assinaturas pós-reabertura B36 conferidas antes do passe B37, com resultado
em `saved_source_reopened` no relatório. Não repetir a mutação B36.

## 02/10/2026 — Continuar pelo ponteiro B35

**Revisão histórica deste passe:** `blender/salvador_lacerda_r30b35_torre_galerias.blend`.
Pai B34 preservado; fonte explícita no catálogo, produção permanece B30.
Correção do apoio R30B08: alinhar a face à parede posterior superior e o
capitel à laje do saguão; não mover o saguão/torre principal ou inventar offset.
Galerias agora têm interiores com abóbada, piso e fundos a 4,2 m de profundidade
candidata; dimensão real `null`. Terreno/proxy escavados nos volumes dos vãos,
mantendo o piso superior apoiado em laje própria. Apoio com recuos posteriores
em níveis, três faixas verticais de vidro e capitel ligado à laje. Apoio antigo
sobreposto/blocos de terreno legados arquivados na coleção REFERENCE R35.
Talude localizado recomposto pelos controles existentes; não alterar ruas/DEM.
Palácio: refinados frontões, molduras, medalhões, relevos e portal; interrompida
a cornija diante do pavilhão central, colunas superiores sobre pedestais.
Praça: material de pedra em escala métrica, malha inalterada.
Relatório: `docs/reports/blender/torre_galerias_r30b35.json`.
Reabertura final do hash registrado confirmada; 39 amostras em cada malha
(visual/proxy) livres de solo nos interiores das galerias. Não exportar ao jogo antes de revisar a
circulação e o contrato das novas coleções/colliders. Próximos pontos reais:
terraços/jardins e colunata sob o palácio, continuidade do entorno e referências
legíveis das fachadas posteriores. Não preencher essas lacunas com decoração
inventada. O conjunto continua candidato, com esboços visíveis no panorama.
Não repetir os scripts de mutação R35: já foram aplicados; seus guards evitam
duplicação. Continuar por inspeção e alterações delimitadas na candidata.

## 02/10/2026 — Palácio Rio Branco, galerias e borda da praça — B34

**Trabalho: B34**, `blender/salvador_lacerda_r30b34_palacio_galerias.blend`.
Continuar pelo ponteiro de `blender-revisions.json`; pai B33 preservado.
Produção/navegador continuam B30. Edição na mesma janela MCP 9876.

Nove capturas enviadas pelo usuário catalogadas como `REFERENCIA_INTERNA`,
licença desconhecida; nenhuma pesquisa nova nem imagem usada como textura.
O edifício das fotos é o **Palácio Rio Branco**. A Prefeitura/Palácio Tomé de
Souza é outro edifício e não foi substituída.

Palácio: planta e cota de implantação herdadas; alas com paredes vazadas,
janelas/caixilhos, três entradas, escadaria, cornijas, pilastras, sacadas,
pórtico lateral, cobertura e cúpula apoiada com nervuras/lucarnas/lanternim.
Esboço anterior arquivado, sem apagar nomes ou dependências. Revisão visual
corrigiu a conversão local→mundo do corpo das alas e fechou as empenas.
Alturas/profundidades são candidatas pela fotografia; não medidas reais.

Galerias: três arcos gradeados no trecho do palácio e dez vãos no trecho
oposto, alinhados aos capeamentos existentes. Extensão parcial; associação
fotográfica/controle ainda candidata. A transição suave do terreno encobria
os arcos. Corrigidas duas bandas locais de contenção no terreno e proxy,
sem escala Z global, alteração do DEM-fonte ou deslocamento XY de vias.
Lajes sobre as galerias conservam a cota superior amostrada da praça;
colisores simples separados em `COLLISION | Galerias Cidade Alta R34`.
Pedra/argamassa das galerias em escala métrica procedural. Material do
barranco localizado por atributo e reamostrado após a retopologia, sem
aplicar ruído à pista nem usar fotos como textura.

Relatório: `docs/reports/blender/palacio_rio_branco_r30b34.json`.
Conferência visual localizada e reabertura registradas no relatório; não é
aprovação de jogabilidade. Preservados 212 componentes protegidos e 192.597
posições de vértices das superfícies de circulação. A consulta local do
proxy não encontrou vértices de pista nessa banda; não equivale a teste de
veículo. Nenhuma exportação runtime, build/npm, testes gerais ou commit.
Esculturas figurativas, interiores e fundos sem vista suficiente permanecem
pendentes. Colunata branca/escadaria da encosta não instanciadas por palpite:
falta controle de implantação próprio. Promover/exportar exige declarar as
novas coleções HERO/ENVIRONMENT_FINAL/COLLISION e validar circulação.


## 02/10/2026 — fonte de trabalho e modelagem pela foto

**Continuar na candidata B33:** `blender/salvador_lacerda_r30b33_fachadas_foto_cairu.blend`.
Fonte/hash/origem no `blender-revisions.json`; produção permanece B30 em
`production.json`. B33 não foi exportada ao navegador. Não usar B23 ou B31
como base de novos passes nem selecionar pelo maior número/mtime.

B32 recuperou modelagem autoral B23 que o passe B31 tinha piorado:
três corpos + 38 componentes (toldo incluído), iguais à B23 após reabertura;
23 substituições B31 conservadas ocultas. Terrain/proxy continuam iguais à B30.
Relatório `facade_regression_b23_b31.json`: a recuperação local da sessão suja
B23 não diferiu no escopo selecionado; não pressupor comparação da cena inteira.

B33: três parcelas OSM explícitas `1263035780`, `1220650507`, `1220650503`.
Mesma foto `elevador-lacerda-panorama-783a31279c0d`, sem novas pesquisas.
Fachadas com vãos e componentes separados, toldo rosado e cobertura; fonte
com água e acabamento de piso conformado. Revisão visual encontrou e corrigiu
face cinza voltada para o fundo e empena aberta; rascunho preservado em
`artifacts/cidade-baixa/r30b33_before_front_refinement.blend`.
Relatório `cidade_baixa_r30b33.json` guarda alterações, reabertura e conferência
local de preservação. Alturas, associação fotográfica e acabamento candidatos;
plantas e fundações preservadas. Ruína no morro sem binding/implantação confirmados,
portanto adiada. Não inventar edifícios/fundos/interiores em vista pouco legível.

**MCP 9876** na janela adotada; não editar outra instância/porta. Entrada:
`open_registered_source.py --source-operation` pelo `run_script.py`.
Em nova sessão, `inspect_authoring_session.py --read-only --adopt-session`.
Mutações conferem PID/porta, arquivo/hash; inspeções usam `--read-only`.
Para reabrir de verdade: `--source-operation --reopen`; ler `last-open.json`
e inspecionar após timeout, sem repetir alterações já feitas.
Política: `docs/BLENDER_REVISION_POLICY.md`. Próxima revisão real deve registrar
pai/evidência e atualizar ponteiro/status/handoff; exportar apenas após promover.

Antes de substituir qualquer fachada, conferir modelagem autoral por objeto/ID.
Não arquivar trabalho melhor só porque existe novo gerador. Conferir fora do
escopo terreno/colisor e componentes recuperados. Essa preservação não aprova
geografia inteira, altura real ou testes dinâmicos de tráfego.
Sem npm/build/CI/testes gerais/commit/exportação neste passe. Ao promover para
runtime, declarar também as novas coleções `ENVIRONMENT_FINAL`/`HERO` na seleção
de exportação: os IDs numéricos antigos não incluem automaticamente as novas.

## Histórico — conexões reais, sem ruas fictícias

**Fonte ativa R30B.30:** `blender/salvador_lacerda_r30b30_conexao_real_recorte.blend`,
hash no contrato `production.json`. Preserva B29/B23. Extensão de chão/colisor
integrada às bordas existentes, 4 m ao sul, na conexão OSM `619722483` dos ways
`1075624458`/`421206045`. Sem mover vértices antigos nem alterar larguras.
`ADAPT_LOCAL`: perfil extrapolado da borda autoral, não cota real medida.
Após reabrir: 205 sondas/41 poses, nenhum chão ausente; delta máximo 9,4 mm.
Detalhes em `terrain_real_boundary_extension.json` e `terrain_real_boundary_verify.json`.

Na sessão anterior, a janela MCP 9877 estava no **artefato de teste**, não na fonte:
`artifacts/terrain-vehicle/r30b30_boundary_vehicle_test.blend`.
Carro V14 real, 195 componentes, 41 poses avaliadas/201 quadros/8,04 s;
Espaço reproduz o trecho da Praça Castro Alves. É replay cinemático de apoio,
não teste dinâmico ou aprovação da faixa/ônibus. Relatório:
`terrain_real_boundary_vehicle.json`. Antes de nova mutação/exportação,
reabrir a fonte do contrato em chamada MCP separada da inspeção.

`terrain_vehicle_replay.py` agora interpreta `direction=both/reverse`:
uma aresta física origina arcos de tráfego, não novas ruas. A auditoria ampla
do carro permanece B29; a alteração do helper não foi reaplicada globalmente.
`plan_osm_return.py` confirmou o retorno real no OSM/Aleph (871,62 m), mas
`plan_real_road_circuit.py` só admite geometria anteriormente verificada e
continua sem retorno aprovado. Não confundir ausência de retorno **verificado**
com ausência de estrada real. Os relatórios discriminam a fonte da auditoria.

Não liberar ônibus nem criar atalhos: Conceição ainda tem o conflito de níveis
abaixo e cobertura parcial de pavimento. Seções existentes têm ~2,4–2,5 m de
asfalto autoral, não largura real certificada; dimensões reais permanecem `null`.
Revisar implantação/seções/perfil com IDs e proveniência antes de alterar esse
corredor. Não escavar passagem fictícia sob a Montanha ou alargar a rua para
forçar um circuito. Runtime não atualizado; sem npm/build/CI/commit nesta etapa.

## Histórico de 01/10/2026 — R30B.29

**Atualização: fonte ativa R30B.29**, derivada da R30B.23; R30C rejeitadas.
Arquivo do contrato: `blender/salvador_lacerda_r30b29_colisao_rede_viaria.blend`.
MCP continua na única janela utilizada, porta 9877. R30B.29 refinou seis faces
adicionais do proxy nas vias cobertas, acrescentando 26 vértices. Após reabrir:
59.720 apoios com fonte, zero ausência no proxy, delta máximo 4,55 cm. Três
sondas fora do recorte não foram preenchidas. Os relatórios atuais são
`terrain_proxy_network_refinement.json` e `terrain_proxy_network_verify.json`.
Não repetir o script de mutação `terrain_proxy_refine_network.py` em revisões
novas; ele exige a R30B.28. Verificação específica: `terrain_network_verify_saved.py`.

**Conflito restante confirmado:** Conceição da Praia, `way-421206045-seg-6/7`,
perto de (-148, -150), tem descontinuidade de ~36,6 m na própria fonte visual.
Colunas mostram apenas uma superfície, não pavimento inferior já pronto.
Não criar passagem sobreposta nem recortar a Montanha arbitrariamente: revisar
perfil e limites das duas vias com proveniência. Larguras reais seguem `null`;
o fit vertical histórico é insuficiente. `terrain_remaining_profiles.json`
registra os quatro apoios e os materiais/normais dos 89 pontos com alertas.
O replay agora bloqueia torção >20 cm ou apoio ausente, preservando inclinações
como alertas a revisar. Não confundir concordância proxy–fonte com fonte correta.

O replay atual está aberto em `artifacts/terrain-vehicle/r30b29_vehicle_test.blend`
na mesma janela. Carro V14: 587 segmentos/12.069 poses; Montanha inteira do
recorte em 19 segmentos, 143,72 s, sem interrupção geométrica. Arquivo de teste
não é a fonte oficial: antes de exportar, abrir a R30B.29 indicada no contrato.
Bloqueados na rede: Conceição `way-421206045-seg-7`, bordas
`way-397449211-seg-1` e `way-531109209-seg-1`. Demais 23 alertas de torção e 71
de inclinação não foram aprovados automaticamente. Relatórios atuais:
`terrain_vehicle_audit_r30b29.json` e `terrain_vehicle_replay_r30b29.json`.
Próximo foco continua terreno/perfil da Conceição, sem tráfego/decoração.

Consulta às fontes: `terrain_conceicao_source_check.json`, com GeoTIFF original
EPSG:3857/PixelIsPoint de 4,777 m projetados, hash e tags OSM. Nenhuma largura
tagged nas duas vias; resolução maior que sua separação nesse ponto após
converter pelo fit XY. Não deformar a cidade para copiar cegamente esse DEM.
Faltam controles locais confiáveis de bordas/cotas para fechar a Conceição sem
estreitar/alargar vias ou inventar uma passagem. A inspeção usa
`tools/terrain/inspect_conceicao_source.py --capture CAMINHO_DA_CAPTURA` e não
modifica Blender. Scripts Python por arquivo evitam espera de EOF do PowerShell
ao encaminhar heredoc para `python -`; tentativas por stdin foram encerradas.

Correções aplicadas via MCP porta 9877 na janela já aberta: `terrain_junction_correct.py`
(R30B.24), `terrain_junction_finish.py` (R30B.25) e `terrain_proxy_bind_source.py`
(R30B.26), `terrain_proxy_apply_transform.py` (R30B.27) e
`terrain_proxy_refine_driveable.py` (R30B.28). Não repetir esses scripts sobre
revisões novas. Nenhuma largura ou
XY da cidade visual foi alterada; apenas Z local do encontro, depois binding
e alturas do proxy simplificado. As instruções históricas de bloqueio abaixo
não descrevem a situação atual.

R30B.25 foi reaberta e mostrou desnível transversal <3 mm nas seções auditadas
do encontro Montanha/Pau da Bandeira. O replay do carro existente completou
19 segmentos da Montanha; é cinemático, não suspensão/tráfego de runtime.
Auditoria geral: 587 segmentos, 12.069 poses. As duas falhas de apoio em
Travessa Professor Antônio Borja/Rua do Carro foram localizadas nos limites
do recorte: rodas atravessam a borda da malha existente. SOURCE_LIMITATION;
não ampliar terreno/ruas sem fonte. Definir limite de navegação antes desses
finais de percurso; não são buracos internos a preencher. Demais alertas de
inclinação/não coplanaridade seguem para revisão, sem nivelamento automático.
Não promover a cidade inteira como pronta. Resultado em relatórios
`terrain_vehicle_*r30b25.json`. Artefato de teste `artifacts/terrain-vehicle/r30b25_vehicle_test.blend`.

O proxy antigo estava em coordenadas locais, enquanto o terreno tinha world
transform; seus limites locais foram conferidos, não foi inventado offset.
Depois do binding, 37.861 alturas do proxy foram atualizadas sobre a fonte;
zero suporte ausente com tolerância de borda de 2 mm (overshoot original <1,77 mm).
O máximo delta de resampling (~51,52 m) mostra que o proxy era obsoleto também
na encosta; não equivale a terreno visual movido. R30B.26 mostrou world matrix
stale no objeto oculto após reabrir; R30B.27 aplicou a matrix basis registrada
aos vértices e deixou transforms em identidade. R30B.28 refinou localmente
32 faces inicialmente divergentes, adicionando apenas 122 vértices ao proxy.
Após reabrir: 1.428 amostras, zero apoio ausente, diferença visual–colisão
máxima 3,87 cm na Montanha/Pau da Bandeira. `terrain_proxy_verify.json` aprovado
somente para suporte geométrico desse percurso, não para dinâmica/gameplay.

Sem nova exportação de runtime, npm/build, commit ou teste jogável de cinco minutos.
Evitar `bpy.ops.render.opengl`: travou sessões anteriores. Posicionar viewport
na janela e usar medições/inspeção segura enquanto captura não estiver disponível.

Continuação do encontro Montanha/Pau da Bandeira: os perfis em
`artifacts/terrain-vehicle/junction-profiles.json` confirmam até ~0,93 m entre
as duas superfícies no encontro. A faixa de `RELEVO | contenção entre vias`
atravessa o eixo em uma seção. Não confundir falha do filtro de material de
asfalto com ausência real de suporte: o replay foi preparado para verificar
quatro apoios no terreno completo, mantendo as vias como seleção do percurso.

`automation/blender/terrain_junction_correct.py` está preparado, **não aplicado**:
altera apenas Z do pavimento existente num encontro de três eixos e sincroniza
localmente o proxy; preserva XY, materiais e topologia. Revisão R30B.24 ainda
não existe nem foi promovida. Não declarar a correção concluída pelo script.

A sessão porta 9876/PID 28348 travou na captura OpenGL. Uma sessão já aberta
porta 9877/PID 32900, com R30B.23, respondeu ao healthcheck e às medições, mas
também travou na captura; ambas as chamadas terminaram por timeout. Não abrir
terceira janela nem usar background para contornar. Foi pedido ao usuário
cancelar/recuperar e manter uma única janela. Não houve mutação de terreno.
Próximo passo: recuperar MCP, aplicar correção, repetir auditoria/replay sobre
a revisão salva, conferir visualmente por captura que não use o operador
OpenGL que travou. Não repetir `terrain_junction_inspect.py` com render OpenGL.

Análise veicular executada sobre a R30B.23 via MCP: ler os relatórios
`docs/reports/blender/terrain_vehicle_audit_r30b23.json` e
`docs/reports/blender/terrain_vehicle_replay.json`. Scripts:
`terrain_vehicle_audit_r30b23.py`, `terrain_vehicle_replay.py` e
`terrain_vehicle_visual.py`. Não executar o append do carro repetidamente.
O teste foi salvo separadamente em `artifacts/terrain-vehicle/r30b23_vehicle_test.blend`;
a composição autoral e o contrato continuam R30B.23. A janela pode mostrar a
cópia de teste, portanto reabrir a fonte do contrato antes de mutar geometria.

Sweep de quatro rodas: 578 segmentos/11.255 poses; não é dinâmica física.
Replay conectado: 17 segmentos da Montanha; encontro do segmento
`way-48846625-seg-9` bloqueia o percurso completo, com diferença transversal
até ~0,92 m. Também há alertas na Chile/Ajuda. Registrar e investigar os
encontros de via e o perfil antes de qualquer alteração Z; preservar XY/largura.
Os segmentos OSM sem chão fora do recorte não autorizam criar nova cidade.

O usuário corrigiu explicitamente a fonte: usar
`blender/salvador_lacerda_r30b23_fachada_praca.blend` (**R30B.23**), preservando
o refinamento do Elevador e entorno. A seleção anterior R30C.5 partiu de base
antiga e foi rejeitada. Não importar terrenos/partições da R30C na R30B.23.
O relatório `terrain_source_selection.json` registra a abertura e o hash; a
troca da fonte não implica exportação do runtime nem correção de geometria.

Diretriz mais recente: não aumentar/diminuir larguras, conservar os limites XY
autorais e regularizar apenas a superfície viária. Larguras reais não confirmadas
continuam incertas. Percursos devem derivar das vias existentes; adiar calçadas.
As notas R30C abaixo são histórico rejeitado, não instrução para continuar.

O usuário restringiu esta etapa à malha/chão e solicitou pesquisa de padrões
de terrenos em jogos. Ler `docs/TERRAIN_GAMEPLAY_RESEARCH.md`. Terreno não deve
ser globalmente plano: conservar ladeiras e patamares, corrigir continuidade.

Fonte ativa declarada no contrato: R30C.5. Foram corrigidas sobreposições do
corredor de teste e o uso de transform ainda não atualizado após carregar um
objeto de biblioteca. R30C.4 é intermediária incorreta; não usar como base.
Scripts de modelagem via MCP: `urban_terrain_partition.py` (sobre R30C.2) e
`urban_terrain_grade.py`; não executar novamente indiscriminadamente. As
revisões preservadas são checkpoints, não fontes concorrentes do runtime.

O corredor possui pista/passeio separados, suporte próprio e adaptação local
documentada. O entorno exterior ainda requer inspeção. Tráfego fica pausado
enquanto `urban_slice.json` tiver `status=terrain_review`. A integração anterior
de carros/NPCs é candidata, não um teste jogável aprovado. Não declarar cinco
minutos de estabilidade: esse fluxo ainda não foi verificado. Browser MCP
retornou timeouts de CDP; usar novamente quando disponível, sem fabricar prova.

Sem npm/build/CI nesta sessão. Validações obrigatórias Python passaram
(62 testes; registro sem erros, dois avisos). Não houve commit/push nesta etapa.

> Elevador Lacerda: revisão visual **parcial R30B.22** em
> `blender/salvador_lacerda_r30b22_exterior_vidros.blend`. O apoio permanece na
> posição original; R30B.14 foi rejeitada por deslocá-lo. Ver
> `docs/revisions/R30B22_LACERDA_EXTERIOR.md` para alterações e pendências.
> Incluir entorno imediato: calçada, comércio confirmado e guarda-corpos da praça, reaproveitando referências catalogadas.
> Prioridade atual: exterior, fachadas e ligação dos acessos à praça/calçada; adiar microdetalhes internos.
> A fonte ativa em `production.json` permanece R30A.11; não houve exportação.

> Produção do MVP: consultar primeiro `world/areas/mvp-centro-lacerda/production.json`
> e `docs/MVP_PRODUCTION_PIPELINE.md`. A revisão ativa é explícita; textos históricos
> e scripts antigos não autorizam escolher outro `.blend`. Exportação canônica:
> `automation/blender/export_active_world.py` via MCP na janela única; empacotamento:
> `python tools/runtime/package_world.py`. Não editar arquivos derivados manualmente.


## Objetivo

Continuar o desenvolvimento do **Bay of All Saints** sem depender de contexto de conversa e sem exigir coordenação manual repetida.

Antes de qualquer trabalho relevante, leia:

1. `AGENTS.md`;
2. `docs/PROJECT_STATUS.md`;
3. `docs/PROJECT_VISION.md`;
4. `docs/GAMEPLAY_FIDELITY_POLICY.md`;
5. este documento;
6. `docs/CODEX_STRUCTURE_HANDOFF.md` quando a tarefa envolver terreno, OSM, DEM, ruas, coastline ou footprints;
7. o handoff da revisão atual, quando existir.

## Fonte de verdade

- GitHub: scripts, documentação, relatórios e decisões de direção;
- `.blend` oficial sob `blender/`: cena de trabalho rastreável via Git LFS;
- dados Aleph/OSM/DEM: referência estrutural, não geometria final obrigatória;
- `docs/PROJECT_STATUS.md`: estado vivo e ponto de entrada para nova IA.

Decisões importantes não devem existir apenas em chat.

## Cena Blender oficial atual

Consultar sempre `docs/PROJECT_STATUS.md` para caminho, SHA-256 e revisão ativa.

Não sobrescrever silenciosamente uma revisão validada. Criar nova revisão apenas quando houver mudança real de cena que justifique nova versão.

## Princípio de fidelidade

O objetivo não é fazer uma cópia milimétrica de Salvador.

A cidade real serve como referência para identidade, estrutura e coerência espacial. A geometria final deve ser adaptada quando necessário para:

- personagem a pé;
- carros;
- NPCs/pedestres;
- câmera;
- colisão;
- navegação;
- tráfego;
- missões/perseguições;
- performance.

Ao detectar diferença entre referência e cena, não corrigir automaticamente. Classificar primeiro conforme `docs/GAMEPLAY_FIDELITY_POLICY.md`.

## Separação obrigatória de responsabilidades

Evitar usar a mesma malha como solução improvisada para tudo.

Manter separações equivalentes a:

```text
SOURCE_GEOREF
REFERENCE_OSM
REFERENCE_TERRAIN
ENVIRONMENT_FINAL
GAMEPLAY_TERRAIN
ROAD_DRIVEABLE
SIDEWALK_WALKABLE
NAVIGATION_HINTS
COLLISION
HERO
WATER
STREAMING
```

A nomenclatura pode evoluir; a separação semântica não.

## Captura geográfica do MVP

Captura histórica recuperada:

```text
data/aleph/aleph-20260924T205631Z-aqqo7pkx/
  manifest.json
  map.osm
  terrain.tif
```

Aleph pinado atualmente:

`Belluxx/Aleph@d24c61507481a91a0dd6afac4f97626a4e5ea780`

Antes de trocar ou ampliar a fonte, consultar:

- `docs/DATA_PROVENANCE.md`;
- `docs/WORLD_DATA_ACQUISITION.md`;
- `docs/references/SOURCE_REGISTRY.json`;
- `docs/references/ALEPH.md`.

Não substituir silenciosamente a captura histórica.

## Georreferenciamento

O pipeline estrutural deve continuar reproduzível.

Ferramentas principais:

```text
tools/blender/extract_georef_hints.py
tools/world/run_structural_pipeline.py
tools/georef/solve_osm_blender_fit.py
tools/world/extract_osm_structure.py
tools/world/audit_osm_topology.py
tools/world/build_blender_structure_reference.py
tools/world/compare_scene_reference_alignment.py
tools/terrain/audit_dem.py
tools/terrain/compare_dem_osm_coverage.py
tools/terrain/audit_road_profiles.py
tools/terrain/fit_dem_blender_vertical.py
tools/terrain/analyze_vertical_domains.py
```

A coleção:

`SOURCE_GEOREF | STRUCTURAL_REFERENCE`

é referência somente. Não promover automaticamente para arte final.

## Anchors conhecidos

- Palácio Rio Branco — OSM way `402383814`;
- Mercado Modelo — OSM way `59392558`.

Usar múltiplos anchors. Não determinar transformação global por um único prédio.

## Estado estrutural atual

Não duplicar números aqui: consultar `docs/PROJECT_STATUS.md` e os relatórios da revisão ativa.

Em termos de direção, o trabalho atual deve:

1. terminar diagnósticos que realmente influenciam decisões;
2. identificar erros locais comprováveis;
3. corrigir somente o que melhora identidade, continuidade ou gameplay;
4. iniciar superfícies funcionais de jogo antes de expandir a cidade em grande escala.

## Terreno

DEM é referência. Não é superfície final obrigatória.

Não:

- aplicar escala Z global apenas para reduzir RMS;
- suavizar a escarpa por conveniência;
- transformar batimetria em nodata automaticamente;
- editar silenciosamente `terrain.tif`;
- deslocar ruas/prédios para encaixar um artefato de DEM.

Correção local deve ser rastreável e validada também do ponto de vista de gameplay.

## Ruas e carros

OSM fornece estrutura, não rede de tráfego completa.

Além da geometria das ruas, o jogo precisará de dados próprios para:

```text
lanes
direction
intersections
turn_connections
speed_zones
traffic_lights
crosswalks
spawns
parking
traffic_priority
```

Dirigibilidade pode justificar adaptações locais de largura, raio de curva e inclinação, desde que a identidade da rua seja preservada.

## Pedestres e NPCs

Calçada visual não equivale a navmesh.

O jogo deverá ter conectividade própria para:

```text
sidewalk
crosswalk
steps
ramp
plaza
building_entrance
elevator
poi
restricted_area
```

Uma área visualmente fiel que prenda NPCs é funcionalmente incorreta.

## Colisão

Preferir colisores simples e previsíveis.

Exemplos:

- escada visual + rampa de colisão;
- fachada detalhada + collider simplificado;
- calçada irregular + superfície caminhável limpa.

Não usar detalhe visual pesado como colisão apenas por conveniência.

## Engine

Nenhuma engine está escolhida definitivamente.

Não amarrar prematuramente o pipeline a Godot, Unity ou Unreal.

Manter unidade métrica, origem, IDs, transforms, colisão e metadados de forma interoperável.

A escolha deverá ser feita após vertical slice funcional do corredor:

**Cidade Alta → Elevador Lacerda → Praça Cairu → Mercado Modelo → Cidade Baixa/waterfront**.

O slice deverá testar personagem, veículo, NPCs, navegação, tráfego, streaming e performance.

## Revisões do Blender

Para qualquer revisão que altere a cena:

- preservar a anterior;
- aplicar mudança rastreável;
- salvar nova revisão quando justificado;
- reabrir e validar;
- gerar relatórios antes/depois;
- registrar motivo das adaptações de gameplay;
- manter referência, arte final, gameplay e colisão separados.

Não criar nova revisão apenas para alterar número quando a cena não mudou.

## Validação mínima

Antes de concluir um ciclo:

```bash
python -m compileall -q tools tests
python -m unittest discover -s tests -p "test_*.py" -v
python tools/references/validate_registry.py --root .
```

Quando Blender for alterado, validar reabertura e exportar relatórios correspondentes.

## Manutenção documental obrigatória

Sempre atualizar `docs/PROJECT_STATUS.md` quando mudar:

- cena oficial;
- revisão ativa;
- etapa atual;
- blockers;
- política de fidelidade/gameplay;
- engine;
- vertical slice;
- pipeline estrutural;
- próximos passos.

Se uma decisão material contradizer algum documento existente, corrigir o documento no mesmo ciclo de trabalho.

## Regra de autonomia

Trabalhar de forma autônoma em decisões técnicas normais, preservando estado anterior e registrando incertezas.

Não usar offsets mágicos, valores inventados, edições destrutivas ocultas ou decoração para mascarar problema estrutural.

## Three.js — fonte única R30A.11 (2026-09-29)

A visualização usa exclusivamente a arte renderizável do arquivo
`blender/salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a11_pedestrian_nav.blend`.
SHA-256 confirmado: `de552b045d190c8feadcb763539e2f0f0b1ce68b6a231884bbe7d70fcd8fd396`.
O exportador anterior omitia objetos compartilhados com coleções GAMEPLAY,
incluindo terreno e vias. Corrigido para selecionar objetos das coleções de arte
06–31 e 36, respeitando visibilidade e renderização. Não altera/salva o Blender.
O manifesto ao lado do GLB registra origem, hashes e nomes dos objetos.
Removidos geradores alternativos de cidade e fallback de marcos. Falha na carga
oficial agora interrompe a visualização, sem substituir o cenário.
`official_surfaces.json` contém apenas suporte de gameplay proveniente da mesma
cena, incluindo proxy de terreno R30A.5; não é renderizado. Exclui superfícies
legadas ocultas. Não há terreno procedural apresentado como cenário oficial.
Ônibus: chão de estúdio excluído do cálculo de escala; carroceria configurada
em 12 × 2,55 × 3,25 m, com retrovisores fora da largura nominal. Essas medidas
são alvo de projeto, não especificação de fábrica confirmada.


### Apoio dos ônibus — correção da fonte de altura
Na R30A.11 as pistas antigas estão ocultas. O asfalto visível pertence ao objeto
`MVP | terreno corrigido | colisão estática`, nos materiais `MVP | asfalto da ladeira`
e `VIAS | pavimento de pedra Rua Chile`. O exportador de superfícies extrai
somente esses triângulos como ROAD, mantendo o proxy separado para terreno.
O posicionamento dos ônibus usa pontos inferiores dos pneus medidos do GLB e
recalcula altura, pitch e roll na posição atual. Não usa a média de alturas dos
extremos do segmento nem offsets verticais de apresentação. Apoios fora do
asfalto consultam o suporte oficial próximo; locais sem suporte não recebem
instância visível. O rig de suspensão individual permanece pendente.


### Correção de orientação — contrato único de coordenadas
A reflexão `group.scale.z = -1` espelhava a cidade mesmo preservando distâncias.
Foi removida. Convenção de runtime: Blender (X,Y,Z) → Three.js (X,Z,-Y),
a mesma rotação própria do glTF, com determinante positivo. Grafo viário,
superfícies de apoio, coastline, limites e spawn convertidos para essa convenção.
O JSON de suporte histórico permanece (X,Z,Y), convertido explicitamente no
carregamento. A auditoria anterior de origens do GLB não abrangia a reflexão
adicionada em JavaScript e não confirmava orientação correta no navegador.
Removidos também os geradores procedurais de terreno que não devem substituir
superfícies oficiais ausentes.
