# Handoff Geral do Codex — Bay of All Saints

> Produção do MVP: consultar primeiro `world/areas/mvp-centro-lacerda/production.json`
> e `docs/MVP_PRODUCTION_PIPELINE.md`. A revisão ativa é explícita; textos históricos
> e scripts antigos não autorizam escolher outro `.blend`. Exportação canônica:
> `automation/blender/export_active_world.py` via MCP na janela única; empacotamento:
> `python tools/runtime/package_world.py`. Não editar arquivos derivados manualmente.


## Objetivo

Continuar o desenvolvimento do **Bay of All Saints** sem depender de contexto de conversa e sem exigir coordenação manual repetida.

Antes de qualquer trabalho relevante, leia:

1. `AGENTS.md`;
2. `docs/PROJECT_STATUS.md`;
3. `docs/PROJECT_VISION.md`;
4. `docs/GAMEPLAY_FIDELITY_POLICY.md`;
5. este documento;
6. `docs/CODEX_STRUCTURE_HANDOFF.md` quando a tarefa envolver terreno, OSM, DEM, ruas, coastline ou footprints;
7. o handoff da revisão atual, quando existir.

## Fonte de verdade

- GitHub: scripts, documentação, relatórios e decisões de direção;
- `.blend` oficial sob `blender/`: cena de trabalho rastreável via Git LFS;
- dados Aleph/OSM/DEM: referência estrutural, não geometria final obrigatória;
- `docs/PROJECT_STATUS.md`: estado vivo e ponto de entrada para nova IA.

Decisões importantes não devem existir apenas em chat.

## Cena Blender oficial atual

Consultar sempre `docs/PROJECT_STATUS.md` para caminho, SHA-256 e revisão ativa.

Não sobrescrever silenciosamente uma revisão validada. Criar nova revisão apenas quando houver mudança real de cena que justifique nova versão.

## Princípio de fidelidade

O objetivo não é fazer uma cópia milimétrica de Salvador.

A cidade real serve como referência para identidade, estrutura e coerência espacial. A geometria final deve ser adaptada quando necessário para:

- personagem a pé;
- carros;
- NPCs/pedestres;
- câmera;
- colisão;
- navegação;
- tráfego;
- missões/perseguições;
- performance.

Ao detectar diferença entre referência e cena, não corrigir automaticamente. Classificar primeiro conforme `docs/GAMEPLAY_FIDELITY_POLICY.md`.

## Separação obrigatória de responsabilidades

Evitar usar a mesma malha como solução improvisada para tudo.

Manter separações equivalentes a:

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

A nomenclatura pode evoluir; a separação semântica não.

## Captura geográfica do MVP

Captura histórica recuperada:

```text
data/aleph/aleph-20260924T205631Z-aqqo7pkx/
  manifest.json
  map.osm
  terrain.tif
```

Aleph pinado atualmente:

`Belluxx/Aleph@d24c61507481a91a0dd6afac4f97626a4e5ea780`

Antes de trocar ou ampliar a fonte, consultar:

- `docs/DATA_PROVENANCE.md`;
- `docs/WORLD_DATA_ACQUISITION.md`;
- `docs/references/SOURCE_REGISTRY.json`;
- `docs/references/ALEPH.md`.

Não substituir silenciosamente a captura histórica.

## Georreferenciamento

O pipeline estrutural deve continuar reproduzível.

Ferramentas principais:

```text
tools/blender/extract_georef_hints.py
tools/world/run_structural_pipeline.py
tools/georef/solve_osm_blender_fit.py
tools/world/extract_osm_structure.py
tools/world/audit_osm_topology.py
tools/world/build_blender_structure_reference.py
tools/world/compare_scene_reference_alignment.py
tools/terrain/audit_dem.py
tools/terrain/compare_dem_osm_coverage.py
tools/terrain/audit_road_profiles.py
tools/terrain/fit_dem_blender_vertical.py
tools/terrain/analyze_vertical_domains.py
```

A coleção:

`SOURCE_GEOREF | STRUCTURAL_REFERENCE`

é referência somente. Não promover automaticamente para arte final.

## Anchors conhecidos

- Palácio Rio Branco — OSM way `402383814`;
- Mercado Modelo — OSM way `59392558`.

Usar múltiplos anchors. Não determinar transformação global por um único prédio.

## Estado estrutural atual

Não duplicar números aqui: consultar `docs/PROJECT_STATUS.md` e os relatórios da revisão ativa.

Em termos de direção, o trabalho atual deve:

1. terminar diagnósticos que realmente influenciam decisões;
2. identificar erros locais comprováveis;
3. corrigir somente o que melhora identidade, continuidade ou gameplay;
4. iniciar superfícies funcionais de jogo antes de expandir a cidade em grande escala.

## Terreno

DEM é referência. Não é superfície final obrigatória.

Não:

- aplicar escala Z global apenas para reduzir RMS;
- suavizar a escarpa por conveniência;
- transformar batimetria em nodata automaticamente;
- editar silenciosamente `terrain.tif`;
- deslocar ruas/prédios para encaixar um artefato de DEM.

Correção local deve ser rastreável e validada também do ponto de vista de gameplay.

## Ruas e carros

OSM fornece estrutura, não rede de tráfego completa.

Além da geometria das ruas, o jogo precisará de dados próprios para:

```text
lanes
direction
intersections
turn_connections
speed_zones
traffic_lights
crosswalks
spawns
parking
traffic_priority
```

Dirigibilidade pode justificar adaptações locais de largura, raio de curva e inclinação, desde que a identidade da rua seja preservada.

## Pedestres e NPCs

Calçada visual não equivale a navmesh.

O jogo deverá ter conectividade própria para:

```text
sidewalk
crosswalk
steps
ramp
plaza
building_entrance
elevator
poi
restricted_area
```

Uma área visualmente fiel que prenda NPCs é funcionalmente incorreta.

## Colisão

Preferir colisores simples e previsíveis.

Exemplos:

- escada visual + rampa de colisão;
- fachada detalhada + collider simplificado;
- calçada irregular + superfície caminhável limpa.

Não usar detalhe visual pesado como colisão apenas por conveniência.

## Engine

Nenhuma engine está escolhida definitivamente.

Não amarrar prematuramente o pipeline a Godot, Unity ou Unreal.

Manter unidade métrica, origem, IDs, transforms, colisão e metadados de forma interoperável.

A escolha deverá ser feita após vertical slice funcional do corredor:

**Cidade Alta → Elevador Lacerda → Praça Cairu → Mercado Modelo → Cidade Baixa/waterfront**.

O slice deverá testar personagem, veículo, NPCs, navegação, tráfego, streaming e performance.

## Revisões do Blender

Para qualquer revisão que altere a cena:

- preservar a anterior;
- aplicar mudança rastreável;
- salvar nova revisão quando justificado;
- reabrir e validar;
- gerar relatórios antes/depois;
- registrar motivo das adaptações de gameplay;
- manter referência, arte final, gameplay e colisão separados.

Não criar nova revisão apenas para alterar número quando a cena não mudou.

## Validação mínima

Antes de concluir um ciclo:

```bash
python -m compileall -q tools tests
python -m unittest discover -s tests -p "test_*.py" -v
python tools/references/validate_registry.py --root .
```

Quando Blender for alterado, validar reabertura e exportar relatórios correspondentes.

## Manutenção documental obrigatória

Sempre atualizar `docs/PROJECT_STATUS.md` quando mudar:

- cena oficial;
- revisão ativa;
- etapa atual;
- blockers;
- política de fidelidade/gameplay;
- engine;
- vertical slice;
- pipeline estrutural;
- próximos passos.

Se uma decisão material contradizer algum documento existente, corrigir o documento no mesmo ciclo de trabalho.

## Regra de autonomia

Trabalhar de forma autônoma em decisões técnicas normais, preservando estado anterior e registrando incertezas.

Não usar offsets mágicos, valores inventados, edições destrutivas ocultas ou decoração para mascarar problema estrutural.

## Three.js — fonte única R30A.11 (2026-09-29)

A visualização usa exclusivamente a arte renderizável do arquivo
`blender/salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a11_pedestrian_nav.blend`.
SHA-256 confirmado: `de552b045d190c8feadcb763539e2f0f0b1ce68b6a231884bbe7d70fcd8fd396`.
O exportador anterior omitia objetos compartilhados com coleções GAMEPLAY,
incluindo terreno e vias. Corrigido para selecionar objetos das coleções de arte
06–31 e 36, respeitando visibilidade e renderização. Não altera/salva o Blender.
O manifesto ao lado do GLB registra origem, hashes e nomes dos objetos.
Removidos geradores alternativos de cidade e fallback de marcos. Falha na carga
oficial agora interrompe a visualização, sem substituir o cenário.
`official_surfaces.json` contém apenas suporte de gameplay proveniente da mesma
cena, incluindo proxy de terreno R30A.5; não é renderizado. Exclui superfícies
legadas ocultas. Não há terreno procedural apresentado como cenário oficial.
Ônibus: chão de estúdio excluído do cálculo de escala; carroceria configurada
em 12 × 2,55 × 3,25 m, com retrovisores fora da largura nominal. Essas medidas
são alvo de projeto, não especificação de fábrica confirmada.


### Apoio dos ônibus — correção da fonte de altura
Na R30A.11 as pistas antigas estão ocultas. O asfalto visível pertence ao objeto
`MVP | terreno corrigido | colisão estática`, nos materiais `MVP | asfalto da ladeira`
e `VIAS | pavimento de pedra Rua Chile`. O exportador de superfícies extrai
somente esses triângulos como ROAD, mantendo o proxy separado para terreno.
O posicionamento dos ônibus usa pontos inferiores dos pneus medidos do GLB e
recalcula altura, pitch e roll na posição atual. Não usa a média de alturas dos
extremos do segmento nem offsets verticais de apresentação. Apoios fora do
asfalto consultam o suporte oficial próximo; locais sem suporte não recebem
instância visível. O rig de suspensão individual permanece pendente.


### Correção de orientação — contrato único de coordenadas
A reflexão `group.scale.z = -1` espelhava a cidade mesmo preservando distâncias.
Foi removida. Convenção de runtime: Blender (X,Y,Z) → Three.js (X,Z,-Y),
a mesma rotação própria do glTF, com determinante positivo. Grafo viário,
superfícies de apoio, coastline, limites e spawn convertidos para essa convenção.
O JSON de suporte histórico permanece (X,Z,Y), convertido explicitamente no
carregamento. A auditoria anterior de origens do GLB não abrangia a reflexão
adicionada em JavaScript e não confirmava orientação correta no navegador.
Removidos também os geradores procedurais de terreno que não devem substituir
superfícies oficiais ausentes.
