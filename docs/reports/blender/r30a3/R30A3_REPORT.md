# R30A.3 — auditoria semântica direta da cena

## Estado

Auditoria concluída diretamente no Blender 5.2.2 via OrdaX Device Agent / Blender Live, sem Codex como intermediário.

Cena analisada:

`blender/salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a_structure_ref.blend`

Foi criado antes da auditoria o checkpoint OrdaX:

`pre-r30a3-direct-chatgpt`

A cena permaneceu `is_dirty=false` antes e depois da execução. Nenhuma geometria, material, coleção, propriedade ou transform foi alterado; o `.blend` não foi salvo.

## Inventário confirmado

- objetos: 4.677;
- meshes: 4.137;
- materiais: 135;
- objetos classificados para triagem semântica: 1.299;
- referências `SOURCE_GEOREF`: 9 objetos;
- `GAMEPLAY_TERRAIN`: 1 objeto;
- candidatos de colisão: 69;
- candidatos de via dirigível: 389;
- candidatos pedonais/calçadas: 74;
- candidatos de água: 24.
## Achado principal

O objeto ativo de terreno é:

`MVP | terreno corrigido | colisão estática`

Ele possui 547.464 vértices e 1.082.745 polígonos e está na coleção `19 MVP | terreno DEM e acessos corrigidos`.

A própria cena confirma que esse único objeto acumula responsabilidades diferentes:

- terreno jogável;
- colisão estática;
- pavimento/asfalto;
- percurso pedonal;
- Praça Cairu;
- passeios;
- contenção entre vias.

Materiais encontrados no mesmo objeto incluem `MVP | terreno contínuo`, `MVP | percurso pedonal`, `MVP | asfalto da ladeira`, `CAIRU | pedra portuguesa clara`, `VIAS | passeio mineral claro`, `VIAS | pavimento de pedra Rua Chile` e `RELEVO | contenção entre vias`.

Conclusão: a cena atual funciona como MVP histórico, mas a malha principal está semanticamente acoplada demais para uma transição robusta para engine, tráfego e NPCs.

## Proxies históricos

`TERRENO | Alto`, `TERRENO | Baixo` e `TERRENO | Encosta` são meshes ocultos de apenas 8 vértices cada, pertencentes à coleção `03 TERRENO | aproximacao volumetrica pendente de levantamento`.

Eles devem permanecer como referência/legado e não devem ser confundidos com a superfície jogável atual.
## Camadas funcionais já sugeridas pela cena

A cena já contém material útil para separação progressiva sem reconstrução do zero:

- coleção 21: ruas e calçadas OSM/Aleph;
- coleção 25: passeios, guias e travessias OSM;
- coleção 24: Baía/cais;
- coleção 19: terreno DEM e acessos corrigidos;
- coleções `SOURCE_GEOREF`: referência estrutural separada.

Na coleção 19 existem meshes separados para pista da Ladeira da Montanha, calçadas esquerda/direita, caminho do acesso alto e caminho da saída baixa. Isso permite evoluir a semântica gradualmente sem cortar imediatamente a malha principal.

Na coleção 25 há guias e travessias explícitas, úteis para futura camada pedonal e de tráfego, mas ainda são geometria visual/referencial e não navmesh/rede de trânsito final.

## Decisão R30A.3

Não separar fisicamente a malha de 547 mil vértices nesta rodada. Primeiro criar metadados/camadas funcionais não destrutivas e validar o corredor jogável.

Próxima ordem recomendada:

1. marcar semanticamente referência versus gameplay;
2. definir `GAMEPLAY_TERRAIN`, `ROAD_DRIVEABLE`, `SIDEWALK_WALKABLE` e `COLLISION` sem duplicação destrutiva;
3. auditar continuidade do corredor Cidade Alta → Elevador → Praça Cairu → Mercado → waterfront;
4. só depois gerar proxies funcionais/exportáveis para a engine.
