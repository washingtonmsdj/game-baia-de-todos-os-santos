# Lacerda — estrutura dimensional B101 — 08/10/2026

B100 preservada, B101 aplicada/salva/reaberta na única janela Blender/MCP9876, PID8792. Fonte `blender/salvador_lacerda_r30b101_pavimentos_estruturais.blend`, SHA256 `87a66414190b4ced14d7a51fe27a23ce96b7a26f36e342ae73809b2a508aabcd`. A janela anterior estava encerrada; reaberta a fonte explícita do catálogo, sem segunda instância. Nenhuma nova busca externa, DEM ou registro das pranchas: reutilizados contornos14/15 e transformação documental derivada da B99.

## Estrutura efetivamente acrescentada

Três superfícies estruturais antes ausentes: piso da subestação/subsolo02 e pisos das duas antigas salas técnicas/subsolo03. Não são cabines, mecanismos ou novas plataformas sobre os poços. Não foram alterados torre, ponte, túnel, corpo superior, lajes anteriores ou terreno para acomodar essas peças.

| Componente | Cota relativa documental (m) | Z arquitetônico (m) | Área do contorno modelado (m²) |
|---|---:|---:|---:|
| B101 | cidade alta | laje subsolo 02 subestação | -9.74 | 60.383009 | 80.9073 |
| B101 | cidade alta | piso sala técnica norte subsolo 03 | -19.85 | 50.273009 | 14.1288 |
| B101 | cidade alta | piso sala técnica sul subsolo 03 | -19.85 | 50.273009 | 14.2373 |

A cota−9,74 vem da15;−19,85 vem da14. As posições dos contornos vêm das faces internas e quinas CAD registradas em `controls.json`, não de pixels de fotografia. A laje02 segue o contorno principal das superfícies da subestação, preservando a reentrância dos lances da escada. Cotas/níveis impressos e coordenadas derivadas de vetores são categorias diferentes no manifesto dimensional.

Espessura0,25m continua candidata, não cálculo estrutural/as-built. Pequenos rebaixos/jambas foram simplificados. As áreas da tabela são das placas modeladas; **não equivalem automaticamente à área útil anunciada de cada ambiente**. A descrição de subestação100,48m² não é usada para reescalar o contorno ou fabricar piso sobre escada/equipamento.

Os pisos03 registram os contornos principais e o nível documental. **Altura/teto das salas, fechamento das paredes entre níveis e conexão física completa dessas salas não estão comprovados nesta revisão**. Não interpretar o empilhamento de lajes como edifício completo, estrutura civil calculada ou circulação aprovada. Não extrudir paredes até a planta15 apenas por ela mostrar a projeção da cobertura.

## Controle dimensional consolidado

`docs/reports/blender/lacerda-floors-b101/dimensions.json` passa a concentrar as verificações desta estrutura, subordinado a `world/geographic-reference.json`, sem outro SSOT. Inclui13 controles de níveis existentes, três pavimentos novos e quatro contornos documentais: torre nova, ponte, galeria e saguão superior. Corpo/cobertura e subsolos anteriores apontam para os controles B100/B99 já executados; não há necessidade de repetir aquisição/registro antes de cada edição.

Cotas de saguão inferior−59,01, cobertura inferior−53,17, térreo0,00, cobertura da galeria+4,00, subsolo01−4,97, pavimentos+4,94/+9,42, cobertura+14,00 e platibanda+15,40 foram conferidas na mesh. A camada legada de acabamento da ponte−0,03 permanece explicitamente candidata. Nenhuma dimensão da cabine/poço é inferida dos contornos exteriores ou de nomes de objetos.

## Verificação do arquivo reaberto

623 componentes arquitetônicos conferidos, 324 visíveis. As malhas ativas verificadas não apresentam faces degeneradas, arestas não manifold, winding inconsistente ou duplicatas internas. 620 assinaturas anteriores intactas; três componentes novos, zero mesh anterior alterada e zero geometria deletada.

22 sondagens das lajes, 25 sondagens sem laje tampando o recorte da escada. Erro máximo de aplicação dos novos contornos 0.00000135m. Os encontros anteriores ponte/saguão e túnel foram rechecados; portal superior6.163564m, conector inferior1.947166m². Não houve npm/build/testes gerais ou novo CCD do equipamento congelado.

Capturas reais inspecionadas: `artifacts/lacerda-live-diagnostic/b101-estrutura.png`, `b101-pavimentos.png` e `b101-map.png`. A vista de pavimentos é uma inspeção temporária sem paredes, não outra cena. Final: mapa completo na cena `SALVADOR | ESBOCO OFICIAL`, terreno visível, sem alterações pendentes.

## Limites que não mudaram

B76–B100 preservadas. SSOT, terreno, duas torres, GAMEPLAY_PROXY B82 e27 testemunhas históricas intactos. `LACERDA_VERTICAL=BLOCKED_EXTERNAL_EVIDENCE`, testemunhas `UNRESOLVED`, `movement_enabled=false`, `replacement_required=true`. Instalação dos quatro ascensores não certificada. Datum/implantação absoluta e interface inferior de aproximadamente3,857m com o terreno seguem `NEEDS_REVIEW`; não foi deslocado o elevador ou deformada Salvador para esconder isso. Produção B30 inalterada; nenhuma exportação/promoção.

Estrutura dimensional **aprovada somente para os controles listados**. Acabamento/fachadas permanecem fora do escopo. As ligações verticais técnicas, escadas executadas e seções ausentes precisam de controle documental específico antes de serem consideradas definitivas; preservar essas distinções no próximo passe de modelagem.
