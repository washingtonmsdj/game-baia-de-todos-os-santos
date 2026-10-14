# Lacerda — integridade de malha e encontros B91 — 07/10/2026

A B91 foi aplicada e reaberta na mesma janela Blender PID 16912, MCP 9876, cena `SALVADOR | ESBOCO OFICIAL`. Continuação da B90, preservando B76–B90. Esta é correção de arquitetura exterior candidata; não resolve implantação geográfica, datum da instalação, interiores ou controller.

## Erros comprovados e correções

| Causa | Antes, B90 | B91 |
|---|---|---|
| Seleção incompleta da montagem B88 | `CALIBRADO / passarela piso` permaneceu retangular, ~55,54 m, fora do novo contorno da ponte | Mesma peça e nome vinculados ao polígono `bridge` da prancha 17. Contato físico com intradorso e piso paginado, sem offset mundial |
| Casca da torre fragmentada e incompleta | Quatro grupos de prismas; corpo terminado em Z 67.323006, técnico iniciado em +4,00; intervalo sem fechamento arquitetônico | Uma casca contínua com o mesmo contorno externo/interno até a face inferior do capeamento. Três cascas e técnico originais preservados como referência substituída |
| Apoio da galeria indevidamente arquivado junto ao acabamento B88 | Consolo antigo ocultado, sem substituto estrutural adequado | Novo consolo alargado fechado, com vazio do núcleo, contorno superior documental e contato com fundo da galeria. Original permanece preservado |
| Prismas adjacentes construídos isoladamente | Faces internas opostas e vértices repetidos em apoios, alas, paredes inferiores e bandas da galeria | 226 faces internas removidas; vértices coincidentes soldados em até 0,00001 m. Bounds e volumes de cada limpeza conferidos; sem fill-holes |
| Vértices colapsados nas três paredes superiores | Quatro arestas não manifold por parede; borda degenerada com extremos coincidentes | Soldagem localizada; as paredes permanecem fechadas e suas aberturas arquitetônicas não foram preenchidas |
| Duas coberturas para a mesma função | Volumes encaixados um dentro do outro, mesma face superior +14,00; sobreposição coplanar e material concorrente | Um volume ativo. `EDIFICIO / cobertura` preservado oculto como referência, sem apagamento |

19 objetos existentes tratados, um novo apoio. Não foram removidos objetos históricos. Materiais/aberturas não receberam detalhamento cosmético.

## Fontes, precisão e aproximações

- Contornos: controles vetoriais SUCOP 17 já registrados em `docs/reports/blender/lacerda-massing-b88/architectural-controls.json`.
- Continuidade vertical e presença do consolo: corte SUCOP 23 e fotografias já catalogadas. A forma da abertura interna não é certificação da seção útil do poço instalado.
- A espessura de parede 0,18 m permanece aproximação herdada, sem levantamento. Não foi apresentada como cota impressa.
- O consolo usa envoltória convexa do núcleo na base e contorno real da galeria no topo. Altura 2.550003 m vem do intervalo herdado do modelo até o fundo atual da galeria, **não de cota documental**. Perfil, espessura e altura: `APPROXIMATE_SECTION_PROFILE_WITH_DOCUMENT_XY`, `replacement_required: true`, `CONSOLO_UNCOTED_PROFILE_AND_ABSOLUTE_PLACEMENT`.
- Espessura da laje da ponte resulta do encontro das superfícies existentes do intradorso e piso. Essa coerência de montagem não certifica espessura construtiva real.
- A transformação arquitetônica relativa B88 foi mantida. O SSOT geográfico não foi alterado para encaixar o asset.

## Verificação efetiva após reabertura

- 520 componentes comparados com assinaturas persistidas; 386 visíveis auditados. Nos componentes visíveis auditados: zero faces degeneradas, zero arestas não manifold e zero grupos de faces coincidentes dentro de uma mesma malha.
- Nas limpezas, a maior variação relativa de volume foi 0.0000000000. Nenhuma abertura intencional foi tapada.
- Contornos de seis componentes estruturais conferidos contra CAD; maior residual numérico de bounds 0.00000534 m.
- Quatro encontros estruturais explicitamente conferidos. Maior gap numérico: 0.00000000 m. Isso não prova automaticamente todos os encontros/auto-interseções do edifício.
- Diferença dos pisos arquitetônicos preservada: 59.01000023 m. Não equivale à distância de parada da cabine B80.
- Assinaturas de terreno e proxy B82 comparadas independentemente com a B90. SSOT byte a byte intacto: `1d9da0962d456cb38ed3df0da797208e499a8465f82e9836c14bb337df2385e7`.
- Fontes substituídas mantêm geometria original e permanecem separadas da camada ativa. Interfaces opostas entre materiais/componentes distintos podem ser contatos legítimos; não aplicar deduplicação automática da cidade.
- Colisores derivados continuam preservados e desabilitados quando dependem da arquitetura alterada. Não houve CCD/varredura do personagem ou export de runtime nesta rodada.

## Estados preservados

`LACERDA_VERTICAL = BLOCKED_EXTERNAL_EVIDENCE`

`movement_enabled = false`

`27 testemunhas B80 = UNRESOLVED / PRESERVED`

`GAMEPLAY_PROXY B82 = PRESERVED / replacement_required: true`

`ABSOLUTE_MAP_PLACEMENT = NEEDS_REVIEW`

`INTERIOR_LAYOUT = NOT_VALIDATED`

`EXPANDED_MAP = GREYBOX`

`production_ready = false`

Ainda faltam reconciliar implantação/datum inferior com o terreno e controlar o perfil sem cota do consolo, interfaces de saguões e layout interno. A inspeção desta rodada prova fechamento das malhas e encontros especificados; não autoriza chamar todo o mapa/instalação de perfeito.

Fonte ativa: `blender/salvador_lacerda_r30b91_integridade_malha_e_apoios.blend`. SHA-256: `b1d8bd448b71c2c65481a507f73fbb696468688cf72b7496b0eb191f4b849c57`.
Relatórios: `before.json`, `contacts.json`, `application.json`, `validation.json`, em `docs/reports/blender/lacerda-mesh-b91/`.
