# B79 — colisão e contrato de controller; percurso ainda bloqueado

## Resultado

Nova revisão derivada **diretamente da B77B**, salva e reaberta na única sessão Blender/MCP 9876: `blender/salvador_lacerda_r30b79_contrato_colisao_slice.blend`. Fonte/hash atuais: `world/areas/mvp-centro-lacerda/blender-revisions.json#/validation_source`. B76, B77B e B78 permanecem intactas; **as correções da B78 não foram incorporadas**, respeitando a base solicitada.

A preparação técnica avançou, mas **Tomé de Souza → cabine → Cairu → Mercado não está aprovado como percurso funcional**. A auditoria integral dos componentes visíveis encontrou interferências que a sondagem central B77 não detectava. Não foram redimensionadas arquitetura/cabine, ocultados obstáculos nem preenchidos vãos para aprovar o teste.

## Comparação com a B77B

| Item | B77B | B79 |
|---|---|---|
| Objetos | 6.088 | 6.292 |
| Componentes anteriores | baseline | 6.088 preservados; zero mudança de malha, material, transform, hierarquia, visibilidade ou action |
| Colisão | 15 proxies de pisos e terreno legado candidato | pisos reaproveitados, 203 patches locais de obstáculos/componentes móveis e um trigger do poço |
| Sweep cabine | sondagem central de personagem | CCD contínuo de 38 componentes da cabine, inclusive piso, teto, laterais, batentes, portas e vedações |
| Sweep personagem | amostragem de esferas/rota candidata | cápsula completa e certificado contínuo por distância segmento–triângulo/Lipschitz |
| Navegação | animação de demonstração | contrato executável, interlocks e estados temporais; permissões desconhecidas bloqueadas |
| Engine | não comprovada | continua não comprovada; adaptador/export delineado, sem promoção para produção |

O SSOT `world/geographic-reference.json` mantém o hash `1d9da0962d456cb38ed3df0da797208e499a8465f82e9836c14bb337df2385e7`. Escala/datum físicos seguem candidatos. Nenhum terreno, Hero, footprint, via ou geografia da expansão foi deslocado. Lapa/Campo da Pólvora/Dique/Fonte Nova permanecem greybox. Não houve triagem em massa dos 118/234 alertas.

## Poço e cabine

Exportados 882 objetos próximos das rotas/poço, 251.655 triângulos avaliados: 836 estáticos e 46 dinâmicos. A captura acompanha também filhos das folhas de estação; evita tratar vedações móveis como obstáculos estáticos quando a porta abre.

O sweep usa SAT contínuo triângulo–triângulo com eixos para coplanaridade e tolerância `1e-7` unidade. Percorre toda a translação vertical existente de `62,7090001106` unidades, incluindo todos os 38 componentes móveis visíveis; não se limita ao centro. Portas de estação fechadas entram como obstáculos durante o movimento.

- 904.535 pares candidatos examinados; **54 pares componente/obstáculo com contato**.
- **27 testemunhas de interseção sólida confirmada**, com vértice estritamente dentro de sólido convexo fechado, distância interior mínima `0,0001` unidade. São testemunhas entre componentes, não 27 edifícios/erros independentes.
- Contatos agrupados: plataforma superior, cobertura inferior, plataforma inferior, consolo inclinado e terreno. As testemunhas sólidas estão nas plataformas/cobertura; outros contatos permanecem `NEEDS_REVIEW`, incluindo tangências ou malhas não convexas.
- O corte B77 no consolo liberava a cápsula central; não demonstrava a passagem do envelope inteiro da cabine.

**Movimento bloqueado no contrato.** Corrigir a geometria de estação/poço exige conciliar abertura real, cabine e lajes; não recortar pelas dimensões da animação sem referência independente. Não foram inventados contrapesos/estruturas.

Limite explícito: o CCD cobre as superfícies avaliadas visíveis e os estados exportados. Malhas grandes foram recortadas por ROI; objetos ocultos/referências foram separados. Contenção integral em sólidos não convexos, elementos não visíveis e **folga positiva mínima do poço** não estão certificados. Ausência de contato não significaria aprovação. Testemunhas positivas já bastam para reprovar o movimento atual.

Evidências: `docs/reports/blender/lacerda-controller/{cabin_sweep_b77b,triage_b79}.json`.

## Personagem: saguão → cabine e Cairu → Mercado

Cápsula nominal de raio `0,30`, altura `1,80`, skin de auditoria `0,002` unidade. Distâncias exatas entre o segmento central e triângulos cobrem cabeça, ombros, corpo e pés. A subdivisão usa certificado Lipschitz e exclusão vertical segura de faces completamente abaixo/acima da cápsula; não substitui o corpo por raios. Suporte é investigado separadamente em início/meio/fim dos segmentos, **não é prova contínua de apoio/gravidade**.

| Rota candidata herdada | Resultado volumétrico |
|---|---|
| Superior | 8 achados de penetração; piso do saguão, pavimento visual da passarela e soleira/cornija |
| Inferior | 9 achados; piso/soleiras e meios-fios nas aproximações/travessias |

Na rota superior, os pés herdados podem ficar até `0,0615` unidade abaixo do pavimento visual. Na inferior, há penetração de até `0,12` unidade em meios-fios e `0,0515` na soleira. São valores da cena, **não medidas reais da obra**. Corrigir o ground-following/controller e conciliar proxy/piso real antes de aceitar esses trechos. Uma rota A* em plano candidato não comprova passagem no chão real.

Não apareceram intervalos numericamente inconclusivos nem falta de suporte nos três pontos amostrados; isso não anula as penetrações nem aprova step, queda, slide ou soleira. O replay cinemático para no primeiro segmento inválido, sem teleporte. Não foi apresentado como controller físico.

A rota inferior intercepta eixos OSM de Rua da Conceição da Praia (`1004133497`), Praça Visconde de Cayru (`978525930`) e Avenida Lafayete Coutinho (`46348179`). Existe a travessia fonte `395865976`; sua vinculação à rota ainda é `NEEDS_REVIEW`. A menor distância entre vértices fonte/rota, `2,8018` unidades, não comprova alinhamento de faixas. Não foi criada travessia. Sinalização/fluxo e permissão de tráfego devem ser confirmados.

Evidências: `character_sweep_b77b.json`, `triage_b79.json` e `actual_states_b79.json`, no mesmo diretório de relatórios.

## Colisão, estados e export

`corridor-slice.json` continua o contrato central; `tools/world/elevator_controller.py` é a implementação neutra de engine. A cabine é uma **aresta de serviço temporal**, nunca um segmento pedonal atravessando o poço. Embarque, fechamento/partida, chegada e desembarque têm pré-condições separadas; não se exige presença simultânea nos dois pisos.

- Embarque: cabine presente/parada, ambas as aberturas suficientes para a cápsula, soleira compatível, suporte e cápsula livres.
- Fechamento: portal vazio; partida: portas fechadas, ocupante apoiado e sweep aprovado.
- Cabine ausente ou informação desconhecida: bloqueio. Planner e follower devem invalidar/rever arestas na mudança de estado.
- Travessia: fonte confirmada, clearance e permissão de tráfego; desconhecido bloqueia.

81 combinações de estado e uma sequência temporal sintética verificaram a lógica; quatro casos analíticos conferiram primitivas geométricas. Dez casos com folhas/poses reais exportadas da B77B ficaram bloqueados. **A sequência sintética verifica apenas o protocolo; não é descida física do personagem.**

As camadas são `WALKABLE_FLOOR`, `STATIC_OBSTACLE`, `DYNAMIC_DOOR`, `DYNAMIC_CABIN`, `FORBIDDEN_SHAFT` e `TERRAIN`. Novos patches retêm triângulos locais e dissolução coplanar, sem convexificar aberturas ou copiar o edifício inteiro. 10.069 triângulos de entrada resultam em 9.624 faces; patches estáticos recortados exigem colisão bilateral. Proxies dinâmicos seguem os pais-fonte, sem duplicar tracks; 225 verificações em cinco poses tiveram erro de matriz zero.

O trigger do poço é envelope conservador candidato, **query-only**, não parede/chão físico. O adaptador deve bloquear aproximação/embarque indevido e manter o ocupante suportado pela cabine. Dois conjuntos de venezianas (5.148 triângulos cada) ficaram pendentes de representação física dedicada. O terreno legado e os pisos candidatos ainda precisam de prova de conformidade; não foram silenciosamente promovidos para físicos finais.

`slice-engine-contract-b79.json` registra fonte/hash, bindings, sensores e conversão `(X,Z,-Y)` aplicada uma vez. Produção continua B30. O wrapper `automation/blender/export_active_world.py` mantém sua proteção: **não exportar B79 burlando o contrato de produção**. A promoção/exportação só deve ocorrer após os gates; nenhum GLB/build foi gerado nesta rodada. O text block Blender é snapshot informativo, não outro SSOT.

## Aleph e proveniência

Mantido o pin Aleph `d24c61507481a91a0dd6afac4f97626a4e5ea780`. Reutilizados OSM, satélite e DEM já auditados, sem trocar fonte/datum. Duas vistas Street View adicionais, ambas com imagery date `2024-12`, foram conferidas e catalogadas:

- `aleph-dev-20261006T035717Z-b79-acesso-superior`: panorama superior identificado na Tomé de Souza; obras/elementos temporários limitam a vista, não confirma interior/soleira/poço.
- `aleph-dev-20261006T035910Z-b79-cairu-mercado`: entorno Cairu, via, meio-fio e travessia marcada; não comprova toda a entrada do Mercado ou regras atuais de circulação.

As capturas têm coordenadas reais, heading, pano ID, fonte, hashes e data nos relatórios `docs/reports/aleph/mvp-centro-lacerda/development/`. Registro visual: `media-manifest.json`; índice central: `world/data-provenance.json`. Permanecem `DEV_REFERENCE_ONLY`, sem material/textura final. Derivados B79 dependem de autoria legada pendente; classificação central continua bloqueando release. Catálogo validado: zero erros, dois avisos herdados (bounds MVP e referência insuficiente do cais).

A auditoria dirigida `provenance_gate_b79.json` confirmou o bloqueio de B79 e três dependências por `REPLACE_BEFORE_RELEASE`. Também marca `INCOMPLETE_INVENTORY`: o manifesto de diagnóstico contém apenas esta candidata, não o pacote integral do jogo. Não é aprovação do inventário final.

## Gates restantes e próximo trabalho

Não comprovados: datum/escala físicos, largura/profundidade/altura real da cabine, abertura e contorno do poço, folgas mínimas, construção das soleiras, dimensões dos desembarques e envelope dos mecanismos. Valores reais ausentes permanecem `null/candidate` no contrato.

Antes da engine: obter controle independente dos desembarques/poço; corrigir as lajes/cobertura que invadem o envelope; reconciliar pisos/proxies e rotas com superfícies reais; vincular as travessias existentes. A abertura posterior herdada da B77B também permanece conhecida; B78 preservada pode ser comparada em migração explícita futura.

Na engine: cápsula com gravidade/slide/step, CCD das portas, antiesmagamento, carry da plataforma móvel, ausência de cabine, colisão bilateral, navegação temporal e circulação/semáforos. Engine não escolhida; esses testes estão pendentes, não substituídos por Play na timeline.

Próximo trecho lógico: **saguão superior → soleira → cabine**, conciliando chão e abertura do poço com dados reais; depois desembarque inferior e travessia Cairu–Mercado. Não avançar decoração/fachadas ou expansão enquanto esses gates estiverem abertos.

Conferência reaberta: `docs/reports/blender/lacerda-controller/validation_b79.json`. Snapshots B77B/B76 preservados; nenhum npm, build ou suíte geral executado.
