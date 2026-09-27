# QA Topológico OSM — Bay of All Saints

## Objetivo

Auditar a continuidade da base estrutural antes de comparar ou corrigir o Blender.

Uma linha OSM terminar não significa automaticamente erro. Pode ser:

- rua sem saída;
- acesso privado;
- limite do recorte;
- píer/muro que realmente termina;
- ponte/túnel em nível diferente;
- dado incompleto;
- gap topológico que merece correção/revisão.

A ferramenta existe para separar esses casos para inspeção, não para conectar geometrias automaticamente.

## Ferramenta

`tools/world/audit_osm_topology.py`

Entrada:

`osm_structure.json` gerado por `extract_osm_structure.py`.

Uso:

```bash
python tools/world/audit_osm_topology.py \
  --structure artifacts/world/mvp-centro-lacerda/osm_structure.json \
  --output docs/reports/aleph/mvp-centro-lacerda/osm_topology_audit.json
```

Ou usar `run_structural_pipeline.py`, que executa esse QA automaticamente.

## O que é auditado

### Nodes ausentes

`missing_node_refs`

Um way referencia nodes que não estavam disponíveis no arquivo OSM carregado. Isso tem prioridade alta, pois a geometria pode estar truncada.

### Buildings não fechados

`unclosed_buildings`

Footprints `building=*` esperados como polígonos são sinalizados quando o primeiro e o último node não coincidem.

A flag não altera o OSM; apenas impede tratar o footprint como confiável sem revisão.

### Endpoints internos

Para camadas lineares, endpoints com grau 1 são classificados em:

- `boundary_or_extract_edge` — próximos ao limite espacial do conjunto;
- `internal_dangling_review` — internos e merecem inspeção.

Camadas avaliadas:

```text
roads
pedestrian
steps
coastline
waterfront
retaining_walls
earthworks
cliffs
railways
```

Ruas/áreas pedonais/escadas compartilham o grupo `transport`, porque podem se conectar entre si.

### Near-miss

Dois endpoints de ways distintos, com nodes OSM diferentes, mas fisicamente muito próximos, entram como:

`distinct_nodes_within_tolerance`

Threshold padrão:

`1.5 m projetados`

Isso é revisão, não correção automática.

### Possível separação de nível

Quando endpoints próximos possuem diferenças em tags como:

- `layer=*`;
- `bridge=*`;
- `tunnel=*`;

eles entram separadamente como:

`possible_grade_separation`

Esses casos não entram na fila normal de near-miss, pois podem representar geometria correta em níveis diferentes.

### Componentes de rede

O relatório calcula componentes conectados por node compartilhado para:

- `transport`;
- `coastline`.

Múltiplos componentes não significam necessariamente erro, mas ajudam a identificar ilhas estruturais inesperadas.

## Coastline

Endpoints da coastline próximos à borda do recorte podem ser normais.

Endpoints internos são tratados como revisão de prioridade alta porque uma cadeia quebrada pode afetar:

- limite terra/água;
- fechamento de áreas costeiras;
- posicionamento do cais;
- continuidade futura do mapa.

## Novas camadas estruturais reconhecidas

O extrator também reconhece:

```text
waterfront: man_made=pier|breakwater|groyne|quay
cliffs: natural=cliff
earthworks: man_made=embankment | embankment=yes | cutting=yes
retaining_walls: barrier=retaining_wall|wall|city_wall ou man_made=retaining_wall
```

Essas camadas são importantes para a escarpa e waterfront de Salvador.

## Saída

O JSON contém:

- resumo;
- componentes de rede;
- nodes ausentes;
- buildings abertos;
- endpoints internos;
- endpoints de borda;
- near-misses;
- possíveis separações de nível;
- `review_queue`.

## Uso na R30A

A ordem recomendada é:

1. resolver/entender `missing_node_refs`;
2. revisar coastline interna interrompida;
3. revisar near-misses;
4. revisar endpoints internos de transporte;
5. confirmar componentes desconectados esperados;
6. só então usar a sobreposição como base de correção no Blender.

## Regra

Não editar a cena para acomodar um erro comprovado da base OSM.

Também não editar OSM ou conectar endpoints apenas porque a auditoria os marcou. A classificação existe para localizar incerteza e exigir uma decisão consciente.
