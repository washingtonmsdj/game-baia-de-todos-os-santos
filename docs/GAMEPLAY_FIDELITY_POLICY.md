# Política de Fidelidade e Jogabilidade

## Objetivo

O **Bay of All Saints** deve ser reconhecivelmente Salvador, mas não deve tentar reproduzir a cidade real de forma milimétrica quando isso prejudicar a experiência de jogo.

A geografia real, OSM, DEM, referências arquitetônicas e medições são **fontes de referência e controle de qualidade**. A geometria final do jogo é uma interpretação autoral orientada por gameplay.

Princípio central:

> **Preservar a identidade espacial de Salvador; adaptar conscientemente o que for necessário para tornar o mundo legível, navegável, performático e divertido.**

Nenhuma diferença entre o mundo real e o Blender deve ser corrigida automaticamente apenas porque foi medida.

## Duas verdades separadas

O projeto deve manter semanticamente separadas:

### 1. Salvador de referência

Representa o que as fontes conhecidas indicam sobre a cidade real:

- georreferenciamento;
- OSM;
- DEM/relevo;
- coastline;
- footprints;
- eixos viários;
- escadas e áreas pedonais;
- cais/waterfront;
- posições relativas dos marcos reais.

Essa camada serve para comparação, auditoria e reconstrução controlada.

### 2. Salvador jogável

É o mundo efetivamente usado pelo jogo.

Pode conter adaptações documentadas de:

- largura de pista;
- largura útil de calçada;
- raio de curvas;
- declividade;
- transição vertical;
- altura funcional de meio-fio;
- escadas;
- corredores de pedestres;
- áreas de manobra;
- acessos;
- distância entre obstáculos;
- colisões;
- rotas de tráfego;
- navegação de NPCs.

Essas adaptações devem ser mínimas, locais e justificadas.

## O que deve permanecer altamente fiel

Priorizar fidelidade alta em elementos que definem a identidade de Salvador e a leitura do espaço:

- relação Cidade Alta ↔ Cidade Baixa;
- posição relativa do Elevador Lacerda;
- Praça Tomé de Sousa;
- Praça Cairu;
- Mercado Modelo;
- Palácio Rio Branco e outros marcos principais;
- eixo e conectividade das vias principais;
- escarpa e diferenças de altitude em escala urbana;
- coastline e relação terra/água;
- cais/waterfront;
- silhueta urbana;
- orientação geral das ruas;
- sequência espacial dos locais reconhecíveis.

Uma diferença pequena em metros não justifica uma correção se a relação espacial, a leitura visual e o gameplay já estiverem corretos.

## O que pode ser adaptado para gameplay

Adaptações são aceitáveis quando resolvem um problema concreto.

### Veículos

Pode ser necessário ajustar:

- raio de curva;
- largura útil de pista;
- encontro entre vias;
- inclinação excessiva;
- transições de inclinação;
- espaço de frenagem/manobra;
- entradas e saídas;
- áreas de spawn;
- corredores de tráfego.

O eixo e a identidade da rua devem ser preservados sempre que possível.

### Pedestres e jogador a pé

Pode ser necessário ajustar:

- largura navegável de calçadas;
- degraus e rampas;
- continuidade entre calçadas;
- travessias;
- passagens estreitas;
- acessos a praças e edifícios;
- superfícies caminháveis.

Detalhe visual e superfície funcional podem ser diferentes.

### NPCs

A geometria visual não deve ser usada diretamente como única fonte de navegação.

O projeto deve prever uma camada própria para:

- navmesh;
- pontos de travessia;
- links de escada/elevador;
- áreas de espera;
- entradas de edifícios;
- pontos de interesse;
- áreas proibidas;
- rotas preferenciais.

### Colisão

A colisão deve ser mais simples e estável que a malha visual.

Exemplos aceitáveis:

- escadaria visual com colisão em rampa suave;
- fachada ornamentada com collider simplificado;
- calçada visual irregular com superfície caminhável limpa;
- guarda-corpo visual detalhado com colisão simples.

A simplificação não deve criar passagem impossível, queda invisível ou barreira sem representação visual coerente.

## Camadas funcionais recomendadas no Blender

A nomenclatura exata pode evoluir, mas o projeto deve manter separação semântica equivalente a:

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

Regras:

- `SOURCE_*` e `REFERENCE_*` nunca são automaticamente arte final;
- `ENVIRONMENT_FINAL` representa a aparência do mundo;
- `GAMEPLAY_*` representa superfícies funcionais;
- `COLLISION` deve ser simplificada e previsível;
- navegação e tráfego devem ter dados próprios;
- diferenças entre referência real e geometria jogável devem ser documentadas quando relevantes.

## Rede de tráfego

OSM define estrutura real, mas não é uma rede completa de tráfego de videogame.

O jogo deverá possuir, em camada própria, dados equivalentes a:

```text
road
lanes
direction
intersection
turn_connections
speed_zone
traffic_light
crosswalk
spawn
parking
traffic_priority
```

A geometria das ruas e a lógica de tráfego não devem ser confundidas.

## Navegação de pedestres/NPCs

O mundo deverá possuir conectividade funcional própria entre:

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

Uma calçada visualmente fiel que cause NPCs presos é considerada incorreta do ponto de vista do jogo.

## Política para terreno e relevo

DEM é referência, não superfície final obrigatória.

Antes de alterar o terreno, perguntar:

1. a divergência é real ou é limitação da fonte?
2. ela altera a leitura de Salvador?
3. quebra acesso, rua, praça, escada ou edifício?
4. prejudica carro, jogador ou NPC?
5. pode ser corrigida localmente sem deformar o restante do mundo?

Só então decidir por correção.

Não aplicar escala ou offset global apenas para reduzir RMS.

O erro estatístico é ferramenta de diagnóstico, não meta artística.

## Política para vias

A ordem de prioridade é:

1. conectividade;
2. eixo e orientação reconhecíveis;
3. relação com terreno e cruzamentos;
4. dirigibilidade;
5. largura funcional;
6. calçadas/travessias;
7. detalhe visual.

Quando a largura real não for conhecida, usar aproximação de gameplay documentada, não apresentar como medida real.

## Política para Hero assets

Hero assets devem permanecer visual e espacialmente reconhecíveis.

Pequenos ajustes no entorno podem ser preferíveis a deformar o Hero asset.

Não mover um marco real apenas para fazer uma rua, collider ou navmesh caber sem antes avaliar alternativas funcionais.

## Regra de decisão para divergências

Uma divergência detectada pelo pipeline deve ser classificada em uma destas categorias:

- `KEEP_REAL_REFERENCE` — referência confirmada; manter como controle;
- `KEEP_GAMEPLAY` — geometria atual difere da referência, mas é melhor para gameplay e continua coerente;
- `ADAPT_LOCAL` — correção local necessária para identidade ou gameplay;
- `SOURCE_LIMITATION` — diferença explicada por limitação de OSM/DEM/referência;
- `NEEDS_REVIEW` — dados insuficientes;
- `ERROR` — erro inequívoco de implementação/binding/geometria.

Nenhum agente deve transformar automaticamente toda divergência em `ERROR`.

## Critérios para uma adaptação de gameplay

Uma adaptação deve:

- resolver um problema observável;
- ser a menor mudança razoável;
- preservar a identidade do lugar;
- não quebrar conexões vizinhas;
- registrar o motivo;
- permanecer reversível sempre que possível;
- ser validada com jogador, veículo e/ou NPC conforme aplicável.

## Engine: decisão adiada e pipeline neutro

O projeto não deve ser amarrado prematuramente a Godot, Unity ou Unreal.

O Blender e os dados do mundo devem permanecer exportáveis e neutros:

- unidade métrica consistente;
- origem documentada;
- transforms controlados;
- nomes e IDs estáveis;
- materiais organizados;
- LODs quando necessários;
- colisores separados;
- metadados estruturados;
- setores/streaming preparados;
- exportação preferencialmente por formatos interoperáveis como glTF quando adequado.

A escolha da engine deverá acontecer por teste de um vertical slice funcional, não por preferência abstrata.

## Vertical slice para escolha da engine

O primeiro teste funcional deve priorizar o corredor:

```text
Cidade Alta
→ Elevador Lacerda
→ Praça Cairu
→ Mercado Modelo
→ trecho da Cidade Baixa/waterfront
```

O slice deve demonstrar, no mínimo:

- personagem a pé;
- colisão estável;
- câmera;
- um veículo controlável;
- veículos de IA básicos;
- pedestres/NPCs básicos;
- navmesh/conectividade;
- tráfego/interseções mínimos;
- mar;
- iluminação;
- carregamento/streaming do recorte;
- performance mensurável.

A engine deve ser escolhida depois de comparar esse cenário real de produção.

## Relação entre fidelidade e performance

Fidelidade visual não justifica custo técnico sem benefício perceptível.

Sempre preferir:

- instâncias para elementos repetidos;
- LODs;
- colisões simplificadas;
- occlusion/culling adequados à engine futura;
- divisão espacial do mundo;
- proxies para longa distância;
- densidade alta apenas onde o jogador percebe.

## Critério de pronto de uma área

Uma área não está pronta apenas porque se parece com Salvador.

Ela precisa passar por:

1. referência estrutural;
2. blockout;
3. travessia a pé;
4. teste de veículo quando aplicável;
5. colisão;
6. conectividade de NPCs;
7. tráfego básico quando aplicável;
8. Hero assets;
9. otimização;
10. passe visual;
11. gameplay;
12. QA.

## Regra para agentes futuros

Ao receber uma métrica de erro entre Salvador real e a cena, não pergunte apenas:

> "Como zerar esse erro?"

Pergunte:

> "Essa diferença prejudica a identidade de Salvador, a continuidade espacial ou a jogabilidade?"

Se a resposta for não, a correção pode ser desnecessária.

O objetivo final é **uma Salvador convincente, reconhecível, sistêmica e divertida de jogar**, não uma réplica cadastral.