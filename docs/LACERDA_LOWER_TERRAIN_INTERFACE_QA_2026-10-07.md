# Interface terreno–saguão inferior — diagnóstico B97 corrigido

## Correção da metodologia anterior (07/10/2026)

A primeira versão deste documento e o QA da PR #28 **comparavam a cota máxima
global do piso (Z≈11,113008 m) com o terreno em quatro pontos**, sem sondar
se havia, de fato, geometria de piso em cada XY. Isso tornou incorreta a
interpretação dos três deltas de aproximadamente +3,857 m como diferenças
entre superfícies coexistentes. Esses deltas ficam expressamente
**revogados como evidência de contato físico**.

A nova inspeção, somente leitura, na cena B97 do Blender PID 16912,
utilizou os quatro controles `lower_floor` documentados na B93 e a
transformação da B78. Dois `ray_cast` verticais independentes, sobre a
malha exata `INFERIOR | piso do saguão` e a malha
`MVP | terreno corrigido | colisão estática`, foram executados em
**cada mesmo XY**. Nenhuma malha ou visibilidade foi alterada.
A sessão estava salva, `bpy.data.is_dirty=false`.

| Controle | XY mundo | Z terreno | Z piso interceptado | Piso menos terreno |
|---|---|---:|---:|---:|
| 1 | (-31,61979; 39,01907) | 12,051285 | 11,113031 | **−0,938254 m** |
| 2 | (-33,47567; 57,21959) | 7,255676 | **Sem interseção** | **Não aplicável** |
| 3 | (-46,45688; 49,55744) | 7,255661 | **Sem interseção** | **Não aplicável** |
| 4 | (-39,96627; 53,38852) | 7,255661 | **Sem interseção** | **Não aplicável** |

As quatro sondagens atingiram o terreno e reproduziram a amostragem B93
dentro do erro de arredondamento; **somente uma sondagem atingiu o piso
da arquitetura inferior**. No controle 1 há um possível conflito vertical
(terreno sobre a primeira interseção com o piso), mas **não** foi provada
interpenetração jogável: ainda faltam a análise de faces da superfície
caminhável, datum arquitetônico absoluto e ensaio do personagem.

Também foi verificado que a antiga mesh `MERCADO MODELO | entrada principal`
permanece oculta na coleção legada e sem `boas_location_id` válido.
Os registros `elevador-lacerda`, `praca-cairu` e `mercado-modelo` em
`world/areas/mvp-centro-lacerda/locations.json` continuam sem
`blender_binding` aprovado. Não converter o objeto legado em conector
funcional do Mercado por nome ou proximidade.

## QA corrigido no mesmo componente

`tools/terrain/surface_registration.py` agora recebe **Z medido do piso
em cada XY** (campo `floor_world_z`) e `terrain_world_z`. O máximo da
bounding box é guardado apenas como `floor_reference_top_z`, nunca usado
como substituto de uma interseção ausente. A classe `NO_FLOOR_HIT` é um
resultado explícito sem `height_delta_m`; `NO_TERRAIN_HIT` e
`NO_BOTH_SURFACES_HIT` também impedem comparações inválidas.

`automation/blender/audit_lower_terrain_interface.py` passa a executar
os dois `ray_cast` no mesmo XY, registrar índices das faces e manter
o gate de identidade da cena e hash SHA-256 do catálogo de autoria.

Depois de consolidar a candidata B97 no repositório como fonte autoral,
a execução pela janela única deve usar o runner canônico do projeto.
Se a B97 aberta não corresponder ao ponteiro explícito do checkout, o
auditor deverá **falhar fechado**, não forçar o apontamento.

## Status físico e gates

- `VALID_SURFACE_PAIRS = 1/4` nas amostras documentadas.
- `ABSOLUTE_MAP_PLACEMENT = NEEDS_REVIEW`.
- `FULL_TOME_MARKET_ROUTE = NOT_APPROVED`.
- `LACERDA_VERTICAL = BLOCKED_EXTERNAL_EVIDENCE`.
- `movement_enabled = false` para o histórico; produção B30 preservada.
- Não adicionar rampa/escada, ajustar Z global, mover o terreno, reabilitar
  piso legado ou inventar um acesso ao Mercado para suprimir os alertas.

**Próxima ação estrutural:** localizar o contorno físico real da porta
inferior e seus controles de implantação, verificar quais faces de solo e
piso a conectam e só depois fazer uma nova revisão de geometria, colisão
e navegação, acompanhada do teste de rota.
