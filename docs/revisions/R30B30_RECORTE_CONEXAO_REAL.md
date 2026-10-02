# R30B.30 — conexão real no limite do terreno

Base preservada: R30B.29, derivada da composição oficial R30B.23.
Aplicação via MCP 9877 na única janela utilizada, sem Blender background.

O nó OSM `619722483` existe na captura Aleph
`aleph-20260924T205631Z-aqqo7pkx`, conectando Praça Castro Alves (`1075624458`)
à Ladeira da Conceição da Praia (`421206045`). O recorte do terreno excluía
esse nó por 1,30 m. A revisão prolonga 4 m das bordas já existentes, integrada
à mesh visual e ao colisor simplificado separado. Sem deslocar vértices
anteriores, alterar larguras ou acrescentar arestas fictícias ao grafo.

`ADAPT_LOCAL`: a margem atende ao apoio do veículo de teste; altura continua
as tangentes da seção autoral e não constitui levantamento real. Materiais e
larguras autorais são preservados. Larguras reais seguem `null`.

Após reabertura, 41 poses/205 sondas têm apoio; diferença máxima terreno–colisor
de 0,009384 m. Replay separado do carro V14: 201 quadros, 8,04 segundos,
195 componentes. Sem simulação de suspensão, carroceria/obstáculos ou tráfego.

O retorno real existe topologicamente: Praça Castro Alves → Ladeira/Rua da
Conceição da Praia → Santos Dumont → Pinto Martins. Não é linha de ônibus
verificada. Não está aprovado para circulação: a Conceição tem conflito de
níveis e seções autorais estreitas/parcialmente cobertas. Não foi inventada
passagem inferior, conexão por proximidade ou alargamento para fechar o circuito.

Relatórios em `docs/reports/blender/`: `terrain_real_boundary_extension.json`,
`terrain_real_boundary_verify.json`, `terrain_real_boundary_vehicle.json`,
`osm_real_return.json`, `real_road_circuit.json` e `real_return_boundary_probe.json`.
Sem runtime exportado, npm, build, CI ou commit.
