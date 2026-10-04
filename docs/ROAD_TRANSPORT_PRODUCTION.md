# Vias, fluxos e transporte coletivo

## Prioridades de produção

1. Origem XY, escala e camadas verticais coerentes, com OSM IDs preservados.
2. Apoio contínuo, transições verticais, limites de pavimento e colisor fiel à superfície funcional.
3. Largura útil da pista e de cada faixa, calçadas, estacionamento, canteiros e bordos.
4. Sentidos, acessos, conversões legais e conexões direcionais de faixa.
5. Itinerários de ônibus, paradas, aproximação, embarque e circulação de pedestres.
6. Envelope completo dos veículos em curvas e cruzamentos, física, tráfego e performance.
7. Marcação, decoração e apresentação final.

Não alargar uma rua para esconder erro de binding, apoio ou trajetória.
Uma divergência precisa de classificação e evidência antes da alteração.
Uma rua com duas faixas pode ser mão única. Mão dupla não prova divisão igual
de faixas. Pistas separadas de uma avenida têm IDs e sentidos próprios.

## Fonte e largura

`width` do OSM é referência etiquetada, não medição de campo aprovada.
`lanes` é número total de faixas; `lanes:forward` e `lanes:backward` são relativos
à ordem dos nós da way. Preservar `oneway=-1`, condicionais, acesso por modal,
restrições e exceções de ônibus. Tag ausente permanece `null`/`pending`.

Não deduzir largura real de `highway`, nome de rua, número de faixas, capacidade
do ônibus ou largura provisória do runtime. Medir separadamente:

- largura de pavimento entre bordos;
- largura útil para circulação, descontando estacionamento e obstáculos;
- faixas por sentido, canteiro e separação entre pistas;
- calçadas e espaço para embarque;
- variação ao longo da via e gargalos, com estações georreferenciadas.

Cada medição real deve ter fonte, data, licença/uso, método, unidade,
incerteza, OSM way/nós e intervalo de aplicação. Imagem deve estar catalogada
quando for necessária. A transformação atual é candidata; coordenadas do
Blender não se tornam levantamento por estarem em unidades métricas.

`automation/blender/audit_road_widths.py` mede o pavimento autoral por material
e camada local, em três estações por segmento. A busca de 16 m por lado e
bisseção de passos de 0,25 m são parâmetros da auditoria, não precisão real.
Interseções podem ampliar a medição; mudanças de material, declividade e
limites do recorte podem interrompê-la. Revisar esses casos antes de concluir
que uma rua é estreita/larga. Não extrapolar largura constante de uma mediana.

## Sentidos, faixas e ônibus

`transport-network.json` é o contrato candidato de revisão da área. Não
substitui o grafo/runtime derivado registrado em `production.json`. Contém:

- tags originais e semântica por OSM way;
- segmentos com IDs, nós, sentido confirmado na fonte ou pendente;
- centros de faixa candidatos, separados da marcação e da geometria;
- restrições de conversão com relações e membros originais;
- membros ordenados dos itinerários e lacunas, sem ligações sintéticas;
- paradas OSM, localização de referência e candidatos de proximidade;
- falhas priorizadas, hashes das entradas e estado de aprovação.

As guias atuais dividem igualmente apenas pistas de mão única com `lanes`
explícito e largura autoral examinada. Não são faixas medidas nem tráfego
aprovado. O índice 1 é a faixa da direita **no sentido de deslocamento**;
isso inverte o sinal lateral quando o veículo segue contra a ordem da way.
Não dividir uma pista bidirecional automaticamente quando faltam faixas por
sentido. Uma exceção `oneway:bus`, faixa exclusiva ou tag condicional exige
regra própria antes de autorizar o ônibus.

Ônibus convencional prefere a direita no seu sentido, permitindo mudança de
faixa para conversões, desvio e trechos exclusivos/terminais documentados.
A preferência não impõe que nunca circule em outra faixa. Para embarque:

1. Confirmar itinerário atual, sentido e conversões legais.
2. Vincular parada à faixa e plataforma certas, por referência/inspeção; um
   vizinho próximo não é binding aprovado.
3. Conferir eixo dianteiro, lado físico das portas e transform do asset;
   alinhar portas do lado direito com calçada/plataforma acessível. Não
   espelhar o veículo para compensar orientação incorreta.
4. Conferir aproximação e saída, meio-fio, folga, obstáculos e pedestres.
5. Auditar os quatro apoios e o envelope varrido, incluindo traseira, espelhos
   e balanços. A câmera do motorista complementa a verificação geométrica.
6. Testar parada, embarque/desembarque e tráfego na engine escolhida.

A largura nominal de 2,55 m do Torino vem do contrato do projeto; não é
medida de fabricante verificada. A folga de 0,15 m por lado é um probe
candidato para apontar revisão. Uma faixa candidata menor que ônibus +
folgas não autoriza alargamento: revisar medição, estacionamento, distribuição
das faixas, trajeto e adaptação local justificada.

## Expansão sem reincidir

O pipeline `tools/world/run_structural_pipeline.py` agora gera também
`road_graph.json` e `osm_transport_reference.json`, após o gate do fit.
Passar `--capture-id` quando o ID é conhecido. A extração preserva sentidos,
faixas, restrições e ônibus. Ligações `*_link` são classificadas como vias;
ciclovias permanecem distinguíveis e não entram automaticamente no tráfego
de carros/ônibus.

Para cada nova área:

1. Registrar área/captura, fonte, licença, limites e transformação.
2. Auditar topologia, cobertura DEM e fit; não conectar limites de recortes
   por proximidade ou igual nome. Conferir nós/camadas entre setores.
3. Gerar referências de tráfego. Exigir largura/sentido/distribuição ou marcar
   lacuna explicitamente. Importar apenas como referência candidata.
4. Criar superfícies funcionais e colisor separado. Testar apoio em todo
   trecho coberto, incluindo bordos, encontros, duas direções permitidas,
   curvas e ambos os veículos. Não atravessar amostras sem apoio.
5. Medir largura autoral e comparar com evidência real por intervalo.
6. Gerar contrato e fila de falhas; bloquear aprovação sem os gates.
7. Corrigir causas com revisão preservada; salvar, reabrir, repetir os
   contatos afetados e conferir invariantes do restante da cena.
8. Atualizar histórico, relatório e handoff no mesmo ciclo. Runtime só muda
   após promoção e exportação pelo contrato canônico.

Ferramentas genéricas da etapa, com caminhos da área como parâmetros:

```text
extract_osm_transport.py --osm FONTE --graph GRAFO --capture-id ID --output REFERENCIA
audit_transport_network.py --area-id AREA --graph GRAFO --source REFERENCIA
  --widths QA_LARGURA --supports QA_APOIOS --turns QA_CURVAS
  --production-contract CONTRATO --fit FIT --output REDE
  [--preservation-report PROVA_DE_PAVIMENTO_PRESERVADO]
validate_transport_network.py --network REDE --output QA
merge_road_issues.py --network REDE --ledger HISTORICO --cycle CICLO
```

`validate_transport_network.py --require-production-ready` retorna 2 enquanto
existir pendência de produção. Relatórios de largura e apoio de revisões diferentes exigem prova de pavimento
visual preservado, com hashes, diferenças e reabertura conferidos.
Consistência do contrato não significa aprovação
de geometria, medidas, itinerários ou física. Ausência de uma falha numa nova
varredura não fecha automaticamente o histórico; confirmar coverage/reabertura.

## Histórico de correções

`road-corrections.json` preserva primeira/última detecção, estado e eventos por
ID da área, OSM way/nós e tipo de falha. Não apagar itens resolvidos ao gerar
novo relatório. Uma fonte que muda a ordem dos nós não pode transformar a
falha antiga em outro problema sem revisão: IDs de ocorrência usam o par de
nós, além do ID da way, quando disponíveis.

Correção aceita registra classificação (`ERROR`, `ADAPT_LOCAL` etc.), causa,
antes/depois, fonte/hash, método e tolerância, pontos afetados, invariantes,
salvamento/reabertura e pendências restantes. Medida não verificada continua
nula. Nunca marcar a cidade inteira como AAA ou 100% por um replay curto.

## Evidência inicial — 04/10/2026

Captura original: `aleph-20260924T205631Z-aqqo7pkx`. Grafo atual: 187 ways e
743 segmentos. A fonte contém 119 ways com mão única explícita, 8 com mão
dupla explícita, 60 sem `oneway` e nenhuma largura numérica. Há 11 nós de
ônibus na captura (excluídos 4 registros de bonde), uma relação de ônibus
0429 Barra–Iapi parcialmente presente e uma restrição de conversão. Estes
dados são a fotografia da fonte; operação atual não foi confirmada.

Auditoria de largura B39: 1.732 estações medidas, 91 sem limite resolvido,
55 sem pavimento central adequado, 28 segmentos sem curva e 89 sem binding
de endpoint. As larguras reais continuam `null`; nenhuma via foi alargada.
Resultados e limitações estão nos relatórios de `docs/reports/blender/`.

## Evidência B41 — 04/10/2026

A R30B.41 corrige somente o perfil derivado de `way 803899198` (Rua da Misericórdia). A causa foi interpolação Z linear entre nós OSM esparsos; o helper passou de 3 para 224 pontos, com amostragem ≤ 0,5 m sobre o pavimento funcional, sem alterar OSM, XY, largura, pavimento visual, colisor ou runtime.

A auditoria integral após reabertura eliminou as 20 ocorrências de `center_support_missing` do segmento `way-803899198-seg-1`; `unresolved_endpoint_binding` permaneceu 89. Permanecem no segmento `crossfall_review=7`, `grade_review=6`, `vertical_discontinuity=1` e `wheel_outside_pavement=1`. Não suavizar nem aplicar offset global para ocultar esses valores.

A prova B39→B41 reexecutou a auditoria de largura e comparou 743 segmentos: delta máximo de largura 0 m e superfície viária com assinatura idêntica. Usar `docs/reports/blender/road_width_preservation_b39_b41.json` quando largura B39 e apoio B41 forem combinados no contrato. O gate continua `needs_review`; produção permanece B30.
