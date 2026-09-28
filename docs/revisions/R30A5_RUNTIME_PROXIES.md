# R30A.5 — Runtime Proxies

## Propósito

Transformar a classificação semântica da R30A.4 em uma primeira camada funcional para runtime, ainda independente de engine.

A revisão deve:

- preservar integralmente a cena R30A.4;
- gerar colisão derivada em objeto separado;
- reutilizar fontes existentes de via/pedestre sem duplicação desnecessária;
- registrar métricas objetivas de redução/erro;
- manter Godot, Unity e Unreal igualmente possíveis.

## Resultado

Collider derivado aprovado como candidato:

- 1.082.745 → 131.097 polígonos;
- redução: 87,8922%;
- P95: 0,0018215 m;
- máximo amostrado: 0,180078 m;
- 5.023 amostras.

## Contrato de segurança

O collider R30A.5 é **derivado** e não substitui `MVP | terreno corrigido | colisão estática`.
Ele é candidato para testes de física e chunking, não collider final de produção.

As fontes de runtime ficam separadas em responsabilidades equivalentes a:

- terrain collision;
- road driveable;
- walkable;
- pedestrian crossings;
- curb boundaries;
- water.

## Próxima revisão

A R30A.6 deve priorizar:

1. chunking espacial do collider;
2. continuidade e inclinação das superfícies dirigíveis;
3. grafo de vias/cruzamentos;
4. navigation hints do corredor Elevador → Praça Cairu → Mercado Modelo;
5. critérios para o primeiro teste em engine.

Não criar navmesh ou rede de trânsito “no olho” sem validar as fontes existentes.
