# Lacerda — estrutura exterior B88–B90 — 07/10/2026

A candidata de modelagem ativa é **B90**, salva e reaberta na mesma janela Blender PID 16912, MCP 9876, cena `SALVADOR | ESBOCO OFICIAL`. Esta rodada substitui as proporções genéricas da B87 por uma estrutura arquitetônica relativa às pranchas SUCOP 12, 17 e 23. Não constitui certificação da instalação ou da implantação geográfica.

## Alterações reais

- B88: 514 componentes e quatro novos elementos estruturais. Piso/galeria da torre nova, ponte livre, envoltória da torre nova, corpo da torre antiga, alas sob o edifício superior, piso e limites inferiores/túnel derivados dos contornos vetoriais documentais. Referências históricas e acabamentos substituídos continuam preservados; não apagar para retomar layout.
- B89: 60 componentes. Abertura galeria/ponte identificada pelos mesmos endpoints CAD, independente da ordem dos vértices. Piso inferior e corpos estruturais usam agora a diferença **59,01 m** entre os pisos arquitetônicos. Não reinterpretar isso como parada de cabine, soleira instalada ou solução do offset B80.
- B90: cinco componentes. Cobertura do edifício superior em **+14,00 m** e platibandas em **+15,40 m**, cotas impressas na prancha 23. A cobertura da passarela permanece **+4,00 m**.

| Relação | B87 | Estrutura atual |
|---|---:|---:|
| Ponte livre | aproximadamente 41,2 m, alinhada artificialmente | borda norte 22.32 m; borda sul 24.15 m |
| Ângulo relativo torre nova / ponte | alinhamento genérico | 9.58° derivado dos segmentos CAD |
| Apoio antigo junto à encosta | volume genérico de aproximadamente 15,88 × 10,96 m em toda a altura | contorno do núcleo antigo separado das alas do edifício e das circulações |
| Piso inferior | retângulo genérico 8,80 × 10,20 m, sem ligação arquitetônica completa | envoltória inferior e corredor/túnel documentais |
| Saguão/circulações superiores | contorno B86, com apoios/distância ainda genéricos | contorno preservado e reconciliado com ponte/torres; abertura do núcleo antigo separada do chão |

## Origem e transformação

`world/geographic-reference.json` permanece canônico e byte a byte intacto: `1d9da0962d456cb38ed3df0da797208e499a8465f82e9836c14bb337df2385e7`.

A transformação documental deriva de três cotas impressas da prancha 17: 5,20 / 1,99 / 2,20 m. Escala nominal resultante: 37.790955 unidades PDF por metro. Maior residual dessas cotas: 0.0037 m. Este residual avalia a consistência do documento, não precisão de levantamento.

Ponto de origem documental PDF `[2932.68, 1085.08]` associado ao acesso superior local `[5.5, 0]` no frame histórico da cena. Os vértices originais, fontes, hashes e transformação estão em `docs/reports/blender/lacerda-massing-b88/architectural-controls.json`.

**Registro geográfico independente ainda não aceito.** A forma e a relação espacial do conjunto vêm do documento; sua implantação absoluta no terreno continua candidata. Não foram deslocados terreno, Cidade Alta/Baixa, Mercado, Prefeitura, Palácio, vias ou SSOT para esconder discrepâncias. A geometria inferior agora está no datum relativo do projeto: Z 11.113009; terreno e contexto mantêm seus valores anteriores. A interface com o terreno/rua precisa de reconciliação independente e não está aprovada para circulação.

## Espaço interno e limites

Os pisos são volumes fechados com recortes dos núcleos das torres. A circulação possui espaço geométrico separado dos corpos dos poços; nenhuma cabine foi redimensionada para encaixar.

Área total de envoltória não equivale às áreas de compartimentos impressas. O salão superior de 117,50 m² não representa todas as circulações. O saguão inferior de 265,56 m² e o túnel de 90,99 m² ainda precisam de subdivisão/controle do layout e do trecho técnico junto à rocha. Não declarar essas áreas internas verificadas pela simples área dos polígonos desta rodada.

Espessuras de chapa/parede e elementos de acabamento que não possuem controle próprio continuam aproximações herdadas/autorais. O layout das janelas, portas internas, equipamentos e divisões não foi certificado. Contorno esquemático da torre não comprova seção útil do poço ou cabine atual.

## Verificação efetiva

- 518 componentes conferidos contra assinaturas persistidas; zero faces de área zero. Pisos estruturais controlados têm arestas manifold.
- Bounds XY dos quatro pisos/galeria/ponte conferidos contra os contornos CAD; maior residual 0.00000425 m, somente numérico.
- Diferença real entre planos de piso: 59.01000023 m; cobertura superior +14.000000; platibanda +15.399994; cobertura da galeria +4.000000.
- Capturas de planta e exterior são da mesma cena/janela, com isolamento local apenas para comparação. A revisão final abre o **mapa completo**, com terreno visível e sem `local_view`.
- B76–B89, proxy B82, SSOT, terreno e 27 testemunhas históricas preservados. Nenhum export ou promoção para produção.
- Colisores derivados afetados mantêm seus bindings, mas a validação anterior foi explicitamente invalidada. Não representam controller aprovado na nova arquitetura. Não houve sweep/CCD novo nesta rodada de modelagem.

## Estados e sequência

`LACERDA_VERTICAL = BLOCKED_EXTERNAL_EVIDENCE`

`movement_enabled = false`

`GAMEPLAY_PROXY_B82 = PRESERVED / APPROXIMATE / replacement_required: true`

`ARCHITECTURAL_RELATIVE_STRUCTURE = DOCUMENT_DERIVED_LOCAL_QA`

`ABSOLUTE_MAP_PLACEMENT = NEEDS_REVIEW`

`INTERIOR_LAYOUT = NOT_VALIDATED`

`EXPANDED_MAP = GREYBOX`

Próxima etapa necessária antes de aprovar a estrutura dentro do mapa: reconciliar implantação absoluta e datum de pisos com controles físicos/geográficos independentes, incluindo interfaces Cidade Alta/escarpa e saguão inferior/rua. Depois ajustar divisões, janelas e distribuição dos quatro ascensores. Os gates SEMOB/Otis continuam como dívida conhecida; não foram reabertos nem declarados resolvidos.

Fonte ativa: `blender/salvador_lacerda_r30b90_cotas_exteriores_consolidadas.blend`. SHA-256: `519a5dd85c63edbea53251cf51c3162086d9cbb094654a5a0613e95f08669ea6`.
