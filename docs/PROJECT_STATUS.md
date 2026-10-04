# Estado Atual do Projeto — Bay of All Saints

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

## 02/10/2026 — Variante azul do ônibus

Torino azul criado da mesma base amarela v06; amarelo e verde preservados.
Fonte: `blender/assets/vehicles/torino-31065/azul_v01.blend`; catálogo/hashes em
`world/vehicles/catalog.json`. Somente materiais externos e cor dos letreiros.
Geometria, dimensões, textos, três portas e anúncio traseiro mantidos.
Referência do usuário registrada em `world/vehicles/media-manifest.json`.
Scripts de cor compartilham `automation/blender/bus_color_variant.py`.
Conferência: `docs/reports/blender/torino_azul_v01.json`; runtime inalterado.


## 02/10/2026 — Variante verde do ônibus

Torino verde criado a partir da fonte amarela v06 com anúncio traseiro;
amarelo preservado. Fontes e hashes em `world/vehicles/catalog.json`.
Nova fonte: `blender/assets/vehicles/torino-31065/verde_v01.blend`.
Somente pintura externa/marca e cor dos letreiros mudaram. Geometria,
dimensões, textos, pivôs, portas, rodas e anúncio preservados.
É variante do Torino, não modelagem do Comil Svelto da referência.
Relatório: `docs/reports/blender/torino_verde_v01.json`.
Produção/runtime e cidade inalterados; sem build/npm.

## 02/10/2026 — Conceição: binding de camada e colisor local — B38

**Autoria candidata B38**, `blender/salvador_lacerda_r30b38_binding_conceicao.blend`,
pai B37 preservado. Produção/runtime permanecem B30, sem exportação nesta etapa.
O salto histórico de cerca de 36 m no nó OSM `7520527645` não demonstrava um
degrau na Conceição: o eixo candidato atingia a Montanha. Corrigido somente o
binding de gameplay da way `421206045`, usando o eixo autoral da mesma ID/ordem
de nós e apoio visual inferior. Referência OSM, fit candidato e larguras mantidos.
Não repintar como asfalto os pontos do eixo que saem do pavimento existente.

Colisor refinado em cinco faces iniciais, com 20 vértices adicionais: diferença
máxima piso/proxy caiu de 7,17 para 4,02 cm em 910 amostras. Terreno visual e
5.255 componentes protegidos preservados. Quatro componentes conferidos por
leitura do arquivo salvo, sem abrir segunda instância Blender.

Percurso candidato separado de cerca de 136 m, 182 poses, carro V14 existente em escala
do asset. Conferidos 1.135 frames/4.540 apoios interpolados, sem apoio ausente;
desvio máximo de apoio de 6,22 cm (critério geométrico candidato, não suspensão).
Replay visível finalizado em 45,52 s, 97 atualizações observadas: não é benchmark
de performance nem validação dinâmica. Coleção de teste excluída da exportação.
**Não é circuito urbano concluído.** Curvas, extremos, colisão com todos os
edifícios e largura real permanecem em revisão; esta última é `null`.
Os runs que atingem a pista superior não são conectores entre ruas. Uma adaptação
suave de até 3,5 cm no fim do percurso retirou contato do envelope com a contenção,
sem alterar pista/parede. Rechecagem: 3.420 raios laterais sem contato, em três
alturas/estações longitudinais a cada seis frames; não cobre todo obstáculo urbano.
Evidência: `docs/reports/blender/conceicao_binding_r30b38.json`.

## 02/10/2026 — Fachadas da Cidade Baixa — B37

**Revisão histórica: B37**, `blender/salvador_lacerda_r30b37_fachadas_baixa.blend`,
pai B36 preservado; ponteiro explícito no catálogo. Produção permanece B30.
Passe localizado nas parcelas OSM 1263035780, 1220650507 e 1220650503:
paredes com espessura nos vãos, esquadrias recuadas, cornijas, peitoris,
venezianas verdes, nervuras/painéis do prédio cinza e toldo rosado com espessura.
Implantação XY, cotas, alturas e contagem de vãos existentes preservadas.
Correspondência fotográfica e medidas reais continuam candidatas, não levantadas.

Conferidos 318 componentes protegidos, incluindo terreno, vias, recuperação B23
e conjunto B36. Leitura de retorno de 18 componentes do `.blend` salvo e duas
vistas locais conferidas. Sem exportação, build ou validação de gameplay.
Relatório: `docs/reports/blender/cidade_baixa_r30b37.json`.
As limitações de fidelidade B36 permanecem; este passe não aprova a cidade inteira.

## 02/10/2026 — Terraços e continuidade das galerias — B36

**Revisão histórica: B36**, `blender/salvador_lacerda_r30b36_terracos_palacio.blend`;
pai B35 preservado. Produção permanece B30. A seleção de autoria deve seguir
`blender-revisions.json`, sem escolha por número ou data de arquivo.

Os três arcos do palácio e os dez do trecho oposto foram preservados. O trecho
do palácio, deslocado durante o passe, foi restaurado exatamente da B35;
a ligação ao terraço curvo foi acrescentada separadamente. Os dois novos
vãos são **candidatos**: contagem real e medidas levantadas continuam `null`.
Colunata inferior com sete vãos, interior aberto e escada dentro de uma
abertura real na laje; escadas do jardim com patamares e passagens nos
guarda-corpos. Dimensões/implantação fina ainda candidatas pelas fotografias.
Solo e proxy corrigidos localmente pelos limites das estruturas e borda da
ladeira existente, sem alterar vértices/largura das vias ou o DEM-fonte.

Relatório: `docs/reports/blender/terracos_palacio_r30b36.json`. Conferência de
modelagem localizada; não aprova circulação no runtime ou fidelidade da cidade
inteira. Fachada posterior sem referência suficiente preservada; entorno,
jardins e escultura ornamental continuam parciais. Sem exportação ou build.
**Revisão visual não aceita pelo usuário:** ligação acrescentada e forma da
encosta/terraços ainda diferem da foto. Não ampliar detalhes dessa candidata
antes de corrigir a implantação do conjunto pela referência disponível.

## 02/10/2026 — Correção do apoio e galerias com profundidade — B35

**Revisão deste passe: B35**, `blender/salvador_lacerda_r30b35_torre_galerias.blend`.
Ponteiro explícito em `blender-revisions.json`; B34 preservada, produção B30.
O apoio R30B08 ficava inteiro antes da parede posterior do saguão superior.
Face e capitel reconstruídos pelos planos da parede e da laje existentes;
não deslocar o edifício superior nem a torre principal para acomodar o apoio.
Galerias com abóbadas, pisos, fundos e lajes superiores separados. Profundidade
de 4,2 m **candidata**, escolhida para leitura volumétrica, não medida real;
nenhum ramal interno extrapolado. Proxies simples de piso/laje separados.
Terreno/proxy recortados nos volumes das galerias; apoio com perfil posterior
escalonado, alinhado à laje, e faixa vertical envidraçada. Arquivados o apoio
legado sobreposto e blocos antigos de terreno, preservando suas geometrias.
Talude local recomposto entre a borda existente da ladeira e os controles
superiores; sem alterar XY/largura das vias ou o DEM-fonte.

Palácio: molduras e frontões, medalhões, relevos da arquivolta, cornijas,
consoles, pedestal e colunas do portal refinados pelas fotos. Implantação e
cota preservadas. Praça com material métrico de paralelepípedos, sem deslocar
vértices ou aplicar displacement. Esculturas figurativas, fundos não documentados,
jardins/terraços inferiores do palácio e parte do entorno continuam pendentes;
o panorama ainda contém esboços. Não declarar o conjunto fiel/concluído.
Relatório: `docs/reports/blender/torre_galerias_r30b35.json`.
Reabertura do hash registrado confirmada na mesma janela. Conferidos 256
componentes preservados e os componentes de fachada alterados. As 39 amostras
de cada malha (visual e proxy) não encontraram solo dentro das galerias.
Comparação visual localizada registrada; isso não aprova a cidade inteira.
Sem exportação, npm/build ou testes gerais nesta etapa de modelagem.

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


> Documento vivo. Atualizar quando houver mudança relevante de revisão, direção, pipeline, bloqueios, engine, vertical slice ou critério de produção.

**Atualizado em:** 2026-10-02

## Revisões e modelagem da Cidade Baixa — 02/10/2026

**Trabalho: B33**, declarada em `world/areas/mvp-centro-lacerda/blender-revisions.json`.
**Produção registrada: B30**, mantida no contrato. A candidata não atualizou o navegador.
A cadeia B23–B33 mantém fontes anteriores; B23 é histórica, R30C rejeitada.

B31 preservou terreno/colisão B30, porém seu gerador regrediu fachadas já modeladas.
B32 recuperou da B23 três corpos e 38 componentes, incluindo toldo, e ocultou
somente 23 substituições regressivas da B31. Conferência após reabrir: os 41
componentes recuperados têm geometria, transforms e materiais iguais à B23;
terreno/proxy iguais à B30. A recuperação da sessão suja B23 não diferiu da
fonte salva nesse escopo; a cena inteira não foi comparada.

B33 acrescenta três fachadas nas parcelas OSM `1263035780`, `1220650507` e
`1220650503`, usando apenas a mesma foto enviada e catalogada. Vãos, vidros,
caixilhos, cornijas, frisos, folhas verdes, toldo rosado e cobertura separados.
A revisão visual corrigiu a frente do prédio cinza (aresta frontal 2) e fechou
a empena sob o telhado. Acrescentado acabamento concêntrico da fonte apoiado
na mesh existente e material de água; escultura vinculada e implantação preservadas.
Plantas, fundações, terreno, pistas, colisor e recuperação B23 não alterados.
Alturas, larguras do acabamento/toldo e identificação fotográfica são candidatas;
não foram apresentadas como dimensões medidas ou assets aprovados.

Ruína do morro: falta confirmar vínculo/implantação; não colocada por aproximação.
Fundos, interiores, edifícios ilegíveis e ornamentos ausentes aguardam outras fotos.
Relatórios: `cidade_baixa_r30b32.json`, `cidade_baixa_r30b33.json`.
Conferência localizada/reabertura do passe final registrada no relatório B33.
Sem pesquisa nova, exportação runtime, npm/build, testes gerais ou commit neste passe.

Janela de edição: **9876**, mesma instância adotada. Guard confere PID/porta,
caminho/hash. Recuperações locais em `artifacts/blender-sessions/`.
Procedimento e prevenção de regressões: `docs/BLENDER_REVISION_POLICY.md`.
Não escolher pela janela aberta/sufixo/data nem recomeçar toda a cidade na B23.

## Histórico recente: terreno e malha

### Conexões reais e recorte do chão — R30B.30

Fonte ativa: `blender/salvador_lacerda_r30b30_conexao_real_recorte.blend`,
derivada da R30B.29/R30B.23; anteriores preservadas. Extensão integrada de 4 m
na borda sul junto ao nó OSM `619722483`, compartilhado por `1075624458`
(Praça Castro Alves) e `421206045` (Ladeira da Conceição da Praia). O recorte
anterior excluía esse nó por 1,30 m. Foram acrescentados 100 vértices/96 faces
no terreno e 64 vértices/60 faces no colisor separado, sem mover vértices
anteriores, alterar larguras ou acrescentar conexões ao grafo.

Classificação `ADAPT_LOCAL`: continuação das seções/materiais autorais na borda;
alturas extrapoladas de tangentes locais, **não altimetria real medida**.
Depois de reabrir: 41 poses/205 sondas de apoio, nenhuma ausência de chão,
delta máximo visual–colisor de 9,4 mm e nenhum alerta de torção acima de 8 cm.
Carro V14 existente, 195 componentes, percorre esse segmento em um replay
cinemático separado de 201 quadros/8,04 s. Isso não aprova largura, suspensão,
obstáculos, tráfego ou circulação do ônibus. Relatórios: `terrain_real_boundary_extension.json`,
`terrain_real_boundary_verify.json` e `terrain_real_boundary_vehicle.json`.

O grafo guarda uma aresta física com `direction=forward/reverse/both`; o replay
anterior só derivava arcos `from→to`. O helper foi corrigido para interpretar
ambos os sentidos e virar a orientação do carro ao percorrer o sentido inverso.
Nenhuma rua foi criada para essa correção. A busca de topologia real confirmou
um retorno de 871,62 m: Praça Castro Alves → Ladeira/Rua da Conceição da Praia →
Santos Dumont → Pinto Martins. `osm_real_return.json` conserva cada ID/sentido.
Esse é um circuito candidato de verificação, **não uma linha pública de ônibus**.

**Continua bloqueada a aprovação do circuito:** conflito de níveis da Conceição
descrito abaixo; trechos sem cobertura de pavimento; larguras reais ausentes.
Duas seções autorais da Conceição têm aproximadamente 2,4–2,5 m de asfalto,
com resolução de sondagem de 10 cm; não são medidas da rua real nem justificam
alargá-la para o ônibus nominal de 2,55 m. A auditoria ampla referenciada no
planejamento ainda é a R30B.29, identificada explicitamente nos relatórios;
a verificação nova da R30B.30 é localizada. Não houve exportação de runtime,
`npm`, build, CI ou commit nesta etapa.

### Histórico da rede viária — R30B.29


Fonte ativa: `blender/salvador_lacerda_r30b29_colisao_rede_viaria.blend`.
Mantém a geometria visual e as larguras da R30B.28, derivada da R30B.23.
Refino local adicional da colisão em seis faces, com 26 vértices novos:
66.199 vértices no proxy, sem copiar a malha visual detalhada.
Após salvar e reabrir, foram conferidas 59.723 sondas em 587 segmentos cobertos;
59.720 têm terreno-fonte. Nenhuma dessas sondas perdeu apoio no proxy; diferença
máxima visual–colisão de 4,55 cm, todas abaixo de 5 cm. As três sondas restantes
ultrapassam a borda do mapa em duas poses já catalogadas como SOURCE_LIMITATION.
Isso certifica concordância geométrica, não circulação dinâmica nem ausência
de defeitos na própria fonte. Relatórios: `terrain_proxy_network_refinement.json`
e `terrain_proxy_network_verify.json` em `docs/reports/blender/`.

A revisão localizada dos 28 segmentos com alertas confirmou uma descontinuidade
de aproximadamente 36,6 m no eixo da Ladeira da Conceição da Praia, junto da
Montanha (`way-421206045-seg-6/7`). A sondagem de colunas não encontrou uma via
inferior sob o pavimento elevado: não se trata apenas de escolher outro hit do
raycast. O eixo da Conceição passa a ~2,97 m do eixo da Montanha nesse ponto,
onde os pavimentos estão em níveis distintos. A causa exata da composição
dessas superfícies e seus limites laterais exige revisão estrutural; não criar
um túnel/ponte fictícios nem deformar a Montanha para eliminar a métrica.
O fit DEM–Blender histórico é `insufficient`; a medida real de largura é `null`.
Esse conflito não foi reparado e impede aprovação da rede inteira. Perfis:
`terrain_remaining_profiles.json`. O replay passa a rejeitar apoio ausente ou
torção de quatro rodas acima de 20 cm, critério explícito do teste geométrico,
sem tratar toda ladeira como erro.

Os arquivos OSM/DEM originais foram localizados na captura Aleph histórica.
Leitura read-only do GeoTIFF confirmou EPSG:3857, PixelIsPoint e espaçamento
projetado de ~4,78 m. As duas vias não têm tag de largura. A separação de seus
eixos no ponto crítico (~2,97 unidades Blender) é menor que a resolução projetada
convertida pelo fit XY (~4,63 unidades); esse DEM não resolve ali os limites e
cotas de cada pista. Não foi aplicado diretamente como perfil viário ou fit Z.
`terrain_conceicao_source_check.json` preserva hash, IDs e amostras. Para resolver
o conflito sem alterar larguras, faltam controles locais confiáveis das bordas
e cotas das duas vias; as fontes disponíveis não autorizam escolher uma das
superfícies por aproximação e declarar a outra correta.

Reteste R30B.29 com o carro V14 existente: 587 segmentos, 12.069 poses;
19 segmentos da Montanha percorridos continuamente em 143,72 s de replay.
Bloqueios explícitos: `way-421206045-seg-7` (Conceição) e os dois segmentos
de borda `way-397449211-seg-1` / `way-531109209-seg-1`. Mantêm-se 23 alertas
de torção e 71 de inclinação para revisão. Arquivo visível de teste:
`artifacts/terrain-vehicle/r30b29_vehicle_test.blend`. A fonte de produção
R30B.29 foi preservada; antes de exportar, reabri-la via MCP pelo contrato.
`terrain_vehicle_audit_r30b29.json` e `terrain_vehicle_replay_r30b29.json`
registram os resultados. Sem física de suspensão, validação de obstáculos,
exportação de runtime, npm, build ou commit. O mapa inteiro permanece parcial.

### Correções anteriores sobre a R30B.23 — R30B.28

Fonte anterior: `blender/salvador_lacerda_r30b28_colisao_viaria_refinada.blend`,
derivada exclusivamente da R30B.23 escolhida pelo usuário. A R30B.23 foi preservada.
R30B.24 corrigiu o perfil do encontro Montanha/Pau da Bandeira; R30B.25 unificou
a superfície local do encontro, preservando XY, larguras, materiais e topologia
do terreno visual. Nas seções auditadas, o desnível lateral caiu de ~0,93 m para
menos de 3 mm. Não houve nivelamento global das ladeiras.

O proxy histórico não acompanhava o transform da malha-fonte. Seus limites XY
locais coincidem com os da fonte, com erro numérico máximo de ~1,77 mm. R30B.26
restaurou o proxy preservado, vinculou-o ao transform existente do terreno e
atualizou alturas por amostras individuais. Zero vértices sem suporte após
sondas numéricas de borda de 2 mm. R30B.27 aplicou o transform aos vértices do
proxy para evitar world matrix stale no objeto oculto após reabrir. R30B.28
refinou localmente as faces de colisão divergentes: apenas 122 vértices novos,
66.173 no total. Não substituiu o collider pela malha visual detalhada.
Conferência após reabrir: 1.428 amostras na Montanha/Pau da Bandeira, zero apoio
ausente, diferença máxima visual–colisão 3,87 cm. Aprovação somente geométrica
desse percurso; não certifica suspensão, obstáculos ou toda a cidade.

Reteste da geometria visual R30B.25: 587 segmentos e 12.069 poses; replay
cinemático completou os 19 segmentos da Ladeira da Montanha sem interrupção.
As duas ocorrências de apoio ausente nas demais vias (Travessa Professor Antônio
Borja e Rua do Carro) foram localizadas nas bordas do recorte: rodas ultrapassam
os limites da malha disponível. Classificação SOURCE_LIMITATION, não buraco
interior; não criar terreno fictício nem ampliar ruas para acomodar o carro.
Esses finais de percurso precisam de limites de navegação. Há também alertas de inclinação/não coplanaridade
que exigem revisão. A cidade inteira NÃO está aprovada. Teste dinâmico de
suspensão, validação no navegador e cinco minutos de gameplay continuam pendentes.
Não houve exportação/runtime, npm, build ou commit nesta continuação.

Relatórios atuais: `terrain_junction_finish.json`, `terrain_proxy_binding.json`,
`terrain_proxy_applied_transform.json`, `terrain_proxy_refinement.json`, `terrain_proxy_verify.json`,
`terrain_vehicle_audit_r30b25.json`, `terrain_vehicle_replay_r30b25.json` em
`docs/reports/blender/`. As notas de bloqueio abaixo são histórico anterior.

### Análise veicular da R30B.23 — 01/10/2026

Continuação: seção transversal confirmou ~0,93 m de desnível no encontro
Montanha/Pau da Bandeira e uma faixa de contenção cruzando o eixo. Correção
local preparada, mas ainda não aplicada: captura OpenGL travou o Blender/MCP
nas portas 9876 e 9877. Necessário recuperar uma única janela para modificar
a malha. Fonte ativa segue R30B.23; R30B.24 não foi criada/promovida.

Auditoria via MCP na janela única: 547.464 vértices, 1.092.489 triângulos de
terreno; 732 segmentos viários únicos do grafo OSM, com 15.838 amostras.
Ausência fora da área modelada não foi convertida automaticamente em buraco.
O sweep de quatro apoios com o asset existente V14 avaliou 578 segmentos e
11.255 poses válidas: 485 ocorrências de apoio ausente no pavimento classificado,
9 de não coplanaridade dos apoios e 58 de inclinação para revisão. Esses são
alertas geométricos, não prova de que cada ocorrência seja defeito de terreno.

Replay contínuo de 17 segmentos da Ladeira da Montanha criado na cópia de teste
`artifacts/terrain-vehicle/r30b23_vehicle_test.blend`; bloqueia antes de
`way-48846625-seg-9`. Ali há diferenças transversais de até aproximadamente
0,92 m e classificação de pavimento descontínua. Investigar o encontro de vias
antes de ajustar a malha; não ampliar a pista para acomodar o veículo.

A fonte R30B.23, XY e larguras não foram alterados. Nenhuma fonte R30C foi usada.
O replay é cinemático, não teste de suspensão/física nem tráfego de runtime.
Não declarar que o carro percorreu todas as ruas em fluxo contínuo ou que o
mapa está aprovado. Relatórios: `terrain_vehicle_audit_r30b23.json` e
`terrain_vehicle_replay.json` em `docs/reports/blender/`.

Correção de fonte solicitada pelo usuário em 01/10/2026: a composição a usar é
`blender/salvador_lacerda_r30b23_fachada_praca.blend`. As tentativas R30C abaixo
partiram de uma base anterior e não devem ser transferidas para a R30B.23 nem
tratadas como trabalho aprovado. A exportação/runtime anterior também não é
evidência de que a R30B.23 esteja integrada. Consultar o contrato executável e
`docs/reports/blender/terrain_source_selection.json` para a seleção conferida.

Nesta etapa, preservar os limites XY e larguras autorais da R30B.23, com
ladeiras e patamares. Regularizar o pavimento sem criar envelopes por classe de
rua. Largura sem fonte confirmada permanece não verificada; não apresentar a
geometria existente como levantamento. Calçadas e tráfego ficam para depois.

O usuário pediu suspender a ampliação do teste urbano e focar primeiro no chão.
Revisão de terreno R30C.5 salva pela mesma janela Blender/MCP, com R30A.11 e
revisões anteriores preservadas. Remove sobreposição da pista no corredor
Chile–Ajuda–Vassouras e regulariza seu perfil local em coordenadas mundiais.
São adaptações de gameplay, não medidas topográficas verificadas. A pista
mantém relevo: declividade máxima amostrada no eixo de aproximadamente 7,03%.
2.241 amostras tiveram suporte; conferência visual do corredor no Blender e
reabertura realizadas. O entorno exterior do corredor ainda precisa de revisão.

Pesquisa e decisões: `docs/TERRAIN_GAMEPLAY_RESEARCH.md`.
Relatório: `docs/reports/blender/urban_terrain_partition.json`.
Tráfego pausado no perfil `terrain_review`. A vertical slice e o teste jogável
de cinco minutos NÃO estão concluídos. Controle do navegador nesta sessão
falhou por timeout CDP; não tratar screenshots Blender como validação do jogo.
Validações Python obrigatórias: 62 testes aprovados, compileall aprovado,
registro de referências sem erros e com dois avisos já identificados.

## Resumo executivo

Bay of All Saints é um jogo de ação em mundo aberto ambientado em Salvador. O objetivo é construir uma cidade reconhecível e estruturalmente coerente com Salvador, mas **adaptada conscientemente para gameplay**.

O projeto não busca réplica cadastral/milimétrica. O mundo real fornece referência; a versão final deve funcionar para personagem, carros, NPCs, câmera, colisão, navegação, trânsito, missões e performance.

Diretriz obrigatória: `docs/GAMEPLAY_FIDELITY_POLICY.md`.

## Repositório

`washingtonmsdj/game-baia-de-todos-os-santos`

Branch de produção: `main`.

## Fonte ativa do MVP e contrato de produção

**SSOT executável:** `world/areas/mvp-centro-lacerda/production.json`.
Fluxo obrigatório: `docs/MVP_PRODUCTION_PIPELINE.md`.

A composição ativa para o MVP Three.js é a **R30A.11**, escolhida explicitamente
pelo usuário: `blender/salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a11_pedestrian_nav.blend`.
O contrato registra o SHA-256; exportadores e runtime derivado usam essa mesma fonte.
A R30A.12 permanece preservada, mas não pode substituir a fonte ativa apenas por
ter um número de revisão maior. Não há promoção automática.

Revisão visual candidata do Elevador: **R30B.22**, em
`blender/salvador_lacerda_r30b22_exterior_vidros.blend`. Inclui a remodelagem
da encosta junto à Ladeira da Montanha, o apoio oposto em sua posição original
e o acabamento escuro das venezianas nas duas faces principais da torre.
R30B.21–22 corrigem o recorte da face oposta, os materiais do acesso inferior,
a transparência dos vidros e o encaixe do letreiro, com microrelevo no reboco.
O asfalto medido permanece em cerca de 6,5–7,0 m. A base do apoio ainda é
parcialmente encoberta na vista da Cidade Baixa, e o terreno requer revisão
conjunta com a via antes de qualquer promoção. A R30B.14, que deslocou o apoio,
foi rejeitada. A R30A.11 continua sendo a fonte ativa do runtime. Ver
`docs/revisions/R30B22_LACERDA_EXTERIOR.md`.

O ônibus tem fonte editável própria em `blender/assets/onibus_torino_31065_v03.blend`.
Os Hero assets existentes continuam em coleções da composição: não foram cortados,
reposicionados ou migrados destrutivamente para novas bibliotecas.

O pipeline agora separa fonte Blender, staging de exportação e releases de runtime.
O carregador usa manifesto com hashes, setores espaciais, fila limitada e descarte
de recursos. Terreno visual amplo/core e colisão integral ainda não têm streaming
geométrico completo. LOD, rig e medição de performance permanecem pendentes.

## Histórico das revisões (não determina a fonte ativa)

### R30A.12 — links revisados de navegação

A camada pedonal agora possui conexões promovidas somente quando existe evidência suficiente: `5/5` travessias têm match exato de OSM node ID e deslocamento visual ≤ `2,5 m`, portanto receberam links curtos de navegação revisados.

Os 6 ways de escada produziram `12` endpoints candidatos; `11` foram materializados sobre o collider. O endpoint inicial da `Escadaria do Passo` (`way 530127473`, node `5148629906`) permanece unresolved porque não há superfície jogável no ponto atual.

Cena oficial: `blender/salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a12_nav_links.blend`. Relatório: `docs/reports/blender/r30a12/R30A12_REPORT.md`. Contrato: `docs/reports/blender/r30a12/nav_links.json`.

Próximo foco: vertical slice funcional de locomoção de jogador/NPC usando caminhos, travessias e escadas já revisados.
### R30A.11 — navigation hints de pedestres

A base pedonal do vertical slice foi materializada de forma engine-agnostic: `126` caminhos OSM, `6` escadarias, `487` nós e `488` segmentos. A cena cria `125` helpers de caminho, `5` de escada, `106` junctions e `5` crossing anchors sem gerar navmesh final.

`471` nós foram resolvidos sobre o collider jogável; `16` ficaram fora/sem contato. As cinco travessias existentes têm match exato de `osm_node_id` com o grafo pedonal, mas continuam `review_only_not_connected` até validação da camada de navegação da engine.

Cena oficial: `blender/salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a11_pedestrian_nav.blend`. Relatório: `docs/reports/blender/r30a11/R30A11_REPORT.md`. Revisão: `docs/revisions/R30A11_PEDESTRIAN_NAV.md`.

Próximo foco: vertical slice funcional de locomoção, links revisados de travessias/escadas e entrada/saída de áreas jogáveis.
### R30A.8 ? oceano visual e ?gua de gameplay

A ?gua da Ba?a de Todos-os-Santos foi separada em autoria visual, superf?cie de refer?ncia e volume de gameplay. O n?vel f?sico permanece determin?stico em `0,35 m`; o volume atual permite nado/mergulho at? `-16 m` no recorte existente.

A camada visual usa material PBR animado e espuma derivada da borda real da malha de ?gua. Uma tentativa baseada em `REF_WATERFRONT` foi rejeitada visualmente por desalinhamento e n?o foi mantida como fonte final.

O runtime permanece engine-agnostic: ondas, consulta de superf?cie, nata??o, mergulho, buoyancy, correntes, c?mera submersa, c?usticas e p?s-processamento devem ser implementados no motor, n?o como f?sica Blender.

Cena oficial: `blender/salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a11_pedestrian_nav.blend`. Relat?rio: `docs/reports/blender/r30a8/R30A8_REPORT.md`. Contrato: `docs/reports/blender/r30a8/water_runtime_contract.json`.

Pr?ximo foco: refer?ncia de ondas de larga escala, zonas de corrente/profundidade e vertical slice runtime de nata??o/mergulho quando a engine for selecionada.

### R30A.7 — grafo lógico de vias e cruzamentos

O OSM estrutural foi convertido em uma camada lógica engine-agnostic: `187` vias, `677` nós, `743` segmentos e `174` candidatos a cruzamento. A cena materializa `177` helpers de via e `164` marcadores de cruzamento sobre o collider jogável.

Foram resolvidos `572` nós sobre a superfície de gameplay; `105` ficaram fora/sem contato com o collider. Vias parciais são divididas em sequências contíguas, sem criar pontes artificiais através de gaps.

A revisão preserva `oneway`, rotatórias, restrições e tags existentes, mas não inventa faixas, larguras ou IA de trânsito. O fit XY ainda é `candidate`.

Cena oficial: `blender/salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a7_road_graph.blend`. Relatório: `docs/reports/blender/r30a7/R30A7_REPORT.md`.

Próximo foco: navigation hints de pedestres, travessias e escadas do vertical slice.

### R30A.6 — collision chunks para runtime

O collider otimizado da R30A.5 foi dividido ao vivo, na única janela visível do Blender, em `63` chunks de `128 m`. A partição preserva exatamente os `131.097` polígonos do proxy, com razão de duplicação de vértices `1,0468577`.

Foram comparadas grades de 64/128/256 m. A grade de 128 m foi a primeira a cumprir simultaneamente os limites de quantidade de chunks, máximo de polígonos e P95 por chunk.

Cena: `blender/salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a6_collision_chunks.blend`. Relatório: `docs/reports/blender/r30a6/R30A6_REPORT.md`.

A sessão de produção usa uma única instância visível do Blender com OrdaX e BlendMCP 1.4.4 na mesma janela.

### R30A.5 — proxies de runtime e primeira colisão otimizada

A R30A.5 criou a primeira geometria derivada especificamente para runtime sem alterar a malha-fonte R30A.4. O collider do terreno reduziu de 1.082.745 para 131.097 polígonos (`-87,8922%`) e passou o gate geométrico com 5.023 amostras: erro P95 `0,0018215 m` e máximo `0,180078 m`.

A cena agora também expõe fontes engine-agnostic para vias dirigíveis, superfícies caminháveis, travessias, guias/meio-fio e água. Nenhuma engine foi escolhida e nenhum navmesh/grafo de tráfego foi inventado nesta etapa.

Cena oficial: `blender/salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a5_runtime_proxies.blend`. Relatórios: `docs/reports/blender/r30a5/R30A5_REPORT.md` e `docs/reports/blender/r30a5/runtime_manifest.json`.

O BlendMCP fallback foi revalidado na R30A.5 com addon `1.4.4`, porta `9877`, `get_addon_version`, `get_scene_info` e `get_object_info`. O launcher usa `--factory-startup --disable-autoexec` e timeout de 120 s.

Próximo foco: chunking da colisão, grafo de vias/cruzamentos e hints de navegação do vertical slice.

### R30A.4 — camadas semânticas de gameplay aplicadas

A primeira separação funcional foi aplicada diretamente no Blender por coleções e metadados não destrutivos. A geometria permaneceu invariável: 4.677 objetos, 4.137 meshes, 839.684 vértices, 2.044.767 arestas e 1.238.783 polígonos.

Camadas criadas: terreno, fonte de colisão, pistas dirigíveis, superfícies caminháveis, travessias, guias/meio-fio, água, referência geográfica e proxies legados. O terreno principal continua marcado como composto `GAMEPLAY_TERRAIN + COLLISION_SOURCE`; nenhum split destrutivo foi feito.

Cena oficial: `blender/salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a4_semantic_layers.blend`. Relatório: `docs/reports/blender/r30a4/R30A4_REPORT.md`.

Fallback Blender MCP validado em `docs/BLENDMCP_FALLBACK.md`: BlendMCP 1.4.4 na porta 9877, isolado da sessão histórica da porta 9876.

### R30A.3 — auditoria semântica direta via OrdaX concluída

A cena oficial foi inspecionada diretamente pelo ChatGPT através de OrdaX Device Agent / Blender Live, sem Codex como intermediário. Foi criado o checkpoint `pre-r30a3-direct-chatgpt`; a cena permaneceu `is_dirty=false` e nenhuma geometria foi salva.

A auditoria confirmou 4.677 objetos, 4.137 meshes e 135 materiais. O objeto `MVP | terreno corrigido | colisão estática` concentra 547.464 vértices / 1.082.745 polígonos e hoje acumula terreno jogável, colisão, asfalto, percurso pedonal, Praça Cairu, passeios e contenções.

Isso confirma que o próximo trabalho não é forçar novo fit global nem cortar a malha imediatamente. A prioridade passa a ser separar responsabilidades semanticamente e criar camadas funcionais não destrutivas para `GAMEPLAY_TERRAIN`, `ROAD_DRIVEABLE`, `SIDEWALK_WALKABLE` e `COLLISION`.

Relatórios: `docs/reports/blender/r30a3/R30A3_REPORT.md` e `docs/reports/blender/r30a3/semantic_scene_audit.json`.


### R30A.2 — diagnóstico vertical por domínio concluído

Pipeline integrado em:

`cc2de0c3bc311ba861fa9819440cd7e533704844`

Execução/relatório concluído em:

`450c377ee0fdbb385e64464959091b72bfdb195b`

Relatórios:

- `docs/reports/blender/r30a2/R30A2_REPORT.md`;
- `docs/reports/blender/r30a2/r30a2_status.json`;
- `docs/reports/blender/r30a2/vertical_domains.json`.

Estado final da rodada:

`diagnostic_complete_vertical_domain_split_insufficient`

Nenhuma correção geométrica local foi autorizada pela R30A.2.

## Principais conclusões da R30A.2

### Batimetria não explica o erro vertical

Foram 4.978 amostras DEM válidas:

- 2 abaixo de 0 m (`0,0402%`);
- 4.976 no domínio terrestre não negativo (`99,9598%`).

O robust fit já rejeitava os dois valores negativos. Separar batimetria não alterou os parâmetros do fit.

Portanto, a hipótese “a batimetria é a principal causa do RMS vertical ruim” foi descartada.

### Fit vertical continua insuficiente

R30A.2 terrestre:

- entrada: 4.976 amostras;
- mantidas: 4.900;
- outliers: 76;
- escala Z candidata: `1,0253290`;
- offset Z candidato: `-4,6316455`;
- RMS: `9,2106683`;
- mediana absoluta: `5,2179134`;
- máximo residual: `29,3265740`;
- razão vertical/horizontal: `1,0568512`;
- quality: `insufficient`.

Nenhuma escala/offset Z foi aplicado.

### A malha amostrada não é topografia pura

O objeto usado no fit foi:

`MVP | terreno corrigido | colisão estática`

Evidências da própria cena indicam que ele é uma superfície funcional/histórica de MVP:

- `game_role: static_terrain_collision`;
- derivado de `Aleph DEM + OSM`;
- contém patamares adaptados aos pisos do esboço;
- altimetria foi filtrada/corrigida para MVP;
- inclui plataformas fixas e aproximações.

Isso é decisivo para a direção do projeto: **não devemos tentar deformar essa superfície de gameplay para coincidir globalmente com o DEM**.

A partir de agora, referência topográfica e terreno jogável devem ser tratados como responsabilidades diferentes.

### Regiões críticas detectadas

A grade espacial encontrou 157 células terrestres para revisão, com destaque para:

- base da escarpa/Cidade Baixa;
- waterfront/cais;
- plataformas baixas do MVP;
- platôs da Cidade Alta;
- transições junto à escarpa/ladeiras.

Os maiores resíduos aparecem frequentemente onde a malha atual contém patamares funcionais deliberados ou onde o DEM tem dificuldade para representar transições urbanas abruptas.

Nenhuma das dez células mais críticas apontou diretamente Praça Cairu ou o footprint do Mercado Modelo como alvo de correção.

### Mercado Modelo permanece controle, não alvo

OSM way:

`59392558`

Footprint real observado com offset aproximado de:

`1,878 m`

Não mover automaticamente.

## Cobertura DEM

O falso diagnóstico histórico de `0,1584%` foi corrigido na R30A.1.

A janela real da captura Aleph está:

- `covered_with_margin`;
- cobertura: `100%`.

Captura histórica:

`data/aleph/aleph-20260924T205631Z-aqqo7pkx/`

Arquivos principais:

- `manifest.json`;
- `map.osm`;
- `terrain.tif`.

## Fit XY

Estado conhecido:

- quality: `candidate`;
- status: `candidate_only`;
- escala horizontal: `0,9701734818` unidades Blender por metro;
- rotação EPSG:3857 → Blender: aproximadamente `-0,050990°`;
- RMS: aproximadamente `4,168632` unidades Blender;
- anchors robustos: `1.012`.

Não tratar como transformação final/verificada sem revisão adicional.

## Decisão estrutural após R30A.2

Ainda **não existe evidência suficiente para autorizar uma primeira correção geométrica local baseada apenas no DEM**.

Próximo foco recomendado:

1. separar semanticamente referência física/topográfica de `GAMEPLAY_TERRAIN`/colisão;
2. obter ou validar referência vertical terrestre independente para regiões prioritárias;
3. revisar regionalmente escarpa e waterfront;
4. testar quais patamares são adaptações deliberadas de gameplay e quais são erros reais;
5. só então propor correções locais.

Importante: um patamar funcional pode permanecer diferente do DEM se ele melhora circulação/veículos/NPCs sem destruir a identidade de Salvador.

## DEM e batimetria

O `terrain.tif` histórico é derivado do conjunto Mapzen/Tilezen Terrain Tiles usado pelo Aleph.

O recorte inclui a Baía de Todos-os-Santos. Valores DEM profundamente negativos podem representar batimetria e **não devem ser classificados automaticamente como nodata/erro**.

A R30A.2 confirmou que esses pontos negativos não dominam o fit vertical.

Não editar o `terrain.tif` original.

## Filosofia de fidelidade

A pergunta de produção não é:

> “Como fazer o Blender coincidir 100% com OSM/DEM?”

A pergunta é:

> “A divergência prejudica a identidade de Salvador, a continuidade do mundo ou a jogabilidade?”

Classificações recomendadas:

- `KEEP_REAL_REFERENCE`;
- `KEEP_GAMEPLAY`;
- `ADAPT_LOCAL`;
- `SOURCE_LIMITATION`;
- `NEEDS_REVIEW`;
- `ERROR`.

Detalhes em `docs/GAMEPLAY_FIDELITY_POLICY.md`.

## Gameplay e arquitetura futura

O jogo é planejado para suportar, progressivamente:

- personagem a pé;
- veículos;
- tráfego;
- pedestres/NPCs;
- resposta policial/facções;
- missões;
- economia/atividades;
- mundo urbano sistêmico.

A geometria visual deve ser separada das camadas funcionais. Planejar equivalentes a:

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

A R30A.2 reforçou especialmente a necessidade de separar `REFERENCE_TERRAIN` de `GAMEPLAY_TERRAIN`/`COLLISION`.

Ruas visuais não são, por si só, rede de tráfego. Calçadas visuais não são, por si só, navmesh.

## Engine

Nenhuma engine foi escolhida definitivamente.

Candidatas futuras podem incluir Godot, Unity ou Unreal, mas o pipeline atual deve permanecer neutro.

A escolha deverá ser baseada num vertical slice real, não em preferência abstrata.

## Vertical slice prioritário

Corredor:

```text
Cidade Alta
→ Elevador Lacerda
→ Praça Cairu
→ Mercado Modelo
→ Cidade Baixa / waterfront
```

Antes de expansão urbana grande, esse slice deve provar:

- caminhada;
- colisão;
- câmera;
- veículo controlável;
- veículos IA básicos;
- pedestres/NPCs básicos;
- navegação;
- tráfego/interseções mínimos;
- água;
- iluminação;
- streaming/carregamento;
- performance.

## Ordem macro de desenvolvimento

1. separar referência topográfica de terreno/colisão jogável;
2. classificar regionalmente erros reais versus adaptações de gameplay;
3. corrigir somente erros estruturais realmente relevantes;
4. construir/estabilizar superfícies de gameplay;
5. consolidar escarpa e interfaces críticas;
6. coastline/cais;
7. ruas/cruzamentos;
8. escadas/calçadas;
9. footprints/Hero assets;
10. colisão funcional;
11. rede de pedestres/NPCs;
12. rede de tráfego/veículos;
13. vertical slice em engine candidata;
14. otimização e arte final do recorte;
15. expansão da cidade.

A ordem pode ser ajustada quando gameplay revelar dependências reais.

## Bloqueios atuais

- fit vertical completo e terrestre seguem `insufficient`;
- a superfície amostrada mistura terreno funcional, colisão e patamares de MVP;
- escarpa contém transições abruptas que o DEM pode representar mal localmente;
- fit XY segue `candidate`, não `verified`;
- não há referência vertical terrestre independente suficiente para autorizar correção local apenas por métrica.

Esses bloqueios não impedem planejamento de gameplay layers, classificação semântica ou preparação do vertical slice.

## O que não fazer

- não tentar zerar RMS global por princípio;
- não reconstruir a cena do zero sem motivo;
- não deformar Hero assets para acomodar erro de base;
- não transformar `static_terrain_collision` em topografia “real” por força;
- não usar geometria visual pesada diretamente como colisão/navmesh por conveniência;
- não inventar largura de rua como se fosse medida;
- não aplicar escala/offset global sem análise;
- não confundir OSM com lógica completa de tráfego;
- não expandir a cidade rapidamente antes do vertical slice ser funcional;
- não escolher engine definitiva antes de um teste representativo;
- não deixar decisões importantes apenas em chats.

## Documentos de entrada para nova IA

Ler nesta ordem:

1. `AGENTS.md`;
2. `docs/PROJECT_STATUS.md`;
3. `docs/PROJECT_VISION.md`;
4. `docs/GAMEPLAY_FIDELITY_POLICY.md`;
5. `docs/CODEX_HANDOFF.md`;
6. `docs/CODEX_STRUCTURE_HANDOFF.md`;
7. handoff da revisão atual, se existir.

## Regra de manutenção documental

Toda mudança material em qualquer um destes itens deve atualizar este documento e os handoffs afetados:

- direção do jogo;
- cena Blender oficial;
- revisão ativa;
- captura geográfica;
- critérios de fidelidade;
- pipeline estrutural;
- gameplay layers;
- engine;
- vertical slice;
- principais blockers;
- próximos passos.

O repositório deve permitir que outro agente retome o projeto sem depender da memória de uma conversa.
## 02/10/2026 — Viatura Rondesp: autoria candidata V03

Fonte explícita: `blender/assets/vehicles/rondesp-pickup/marrom_v03.blend`,
ID `vehicle-rondesp-pickup`. Catálogo em `world/vehicles/catalog.json`.
Referências enviadas mostram Hilux CD 2.8 2024/2025, Rondesp Leste 3.1110.
Cabine dupla, capota fechada/acessos, rodas de aço pretas, estribos, quebra-mato,
sinalizador, vidros e inscrições separados. V02 corrige bind das rodas/portas;
V03 refina capô/para-lamas, rodas vazadas, janelas, lentes e camuflagem.
Relatório: `docs/reports/blender/rondesp_marrom_v03.json`.
Dimensões, mapa exato da pintura, brasão detalhado e animação final pendentes;
asset não aprovado nem integrado no runtime. V01/V02 históricas preservadas.
Sem mudanças na cidade, exportação de produção, npm ou build.
