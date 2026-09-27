# R30 — Plano do Passe Visual do MVP

## Objetivo

A R30 é o primeiro passe pós-otimização cujo resultado precisa ser **claramente perceptível ao abrir a cena**.

Ela não deve transformar o MVP em uma cidade finalizada nem tentar detalhar Salvador inteira. O objetivo é fazer o corredor jogável atual parecer um recorte urbano coerente, legível e intencional de **Bay of All Saints**.

A R30 só deve ser iniciada depois que a R29 estiver aplicada e validada, com os relatórios reais exportados para `docs/reports/`.

## Área de foco

O trabalho deve permanecer concentrado no corredor:

**Cidade Alta → acesso superior → Elevador Lacerda → saída inferior → Praça Cairu → Mercado Modelo**

As áreas fora desse corredor podem continuar como referência/proxy quando não forem necessárias para composição ou horizonte próximo.

## Princípios

### 1. Salvador antes de mapa genérico

A cena deve comunicar Salvador por geografia, verticalidade, materiais, mobiliário, vegetação, implantação e relação com a Baía — não apenas por placas ou marcos isolados.

### 2. Jogabilidade antes de excesso de detalhe

Todo detalhe novo deve respeitar circulação de pedestres, veículos, câmera e futuras missões.

Não preencher espaços vazios apenas para “parecer mais detalhado”. Espaço vazio pode ser necessário para travessia, combate, perseguição, spawn ou leitura visual.

### 3. Hero assets permanecem protegidos

Elevador Lacerda, Mercado Modelo e outros `HERO` não devem ser reconstruídos destrutivamente nesta revisão.

A R30 pode melhorar integração, entorno, materiais auxiliares, iluminação de leitura e composição, mas qualquer reconstrução estrutural de hero asset deve ser uma revisão própria.

### 4. Modularidade

Novos elementos repetidos devem preferir módulos e instâncias:

- bancos;
- postes;
- lixeiras;
- balizadores;
- defensas;
- floreiras;
- árvores;
- sinalização;
- pequenos elementos de fachada;
- elementos de calçada.

## Zona A — Cidade Alta / acesso superior

Objetivos:

- tornar clara a aproximação ao Elevador Lacerda;
- reforçar a leitura do acesso para o jogador a pé;
- melhorar transição entre praça, calçada e entrada;
- evitar bloqueios visuais desnecessários próximos à entrada;
- reservar espaço para NPCs, filas, policiamento, vendedores ou eventos futuros.

Entregáveis:

- revisão de calçadas e bordas imediatas;
- zonas de mobiliário sem bloquear rota principal;
- pontos de iluminação e sinalização coerentes;
- pelo menos uma rota secundária curta ou espaço lateral explorável, quando a geometria existente permitir.

## Zona B — Elevador Lacerda

Objetivos:

- preservar funcionamento e alinhamentos já construídos;
- melhorar leitura das entradas superior/inferior;
- diferenciar áreas técnicas, públicas e de circulação;
- garantir visibilidade clara das portas e soleiras;
- preparar lógica futura de interação.

Entregáveis:

- revisão visual das zonas de entrada/saída;
- materiais auxiliares e elementos de orientação quando necessário;
- pontos claros para interação futura;
- checagem de colisão e espaço de câmera, sem criar colisões finais nesta revisão.

## Zona C — saída inferior / transição Cidade Baixa

Esta é uma das áreas de maior prioridade visual.

Objetivos:

- evitar sensação de que o jogador “sai do elevador para um vazio”;
- construir uma transição urbana convincente;
- estabelecer direção natural para Praça Cairu e Mercado Modelo;
- manter alternativas de movimento lateral.

Entregáveis:

- reforço de calçadas, guias, contenções e bordas;
- composição de mobiliário e vegetação em baixa densidade;
- leitura de travessias e acesso à malha viária;
- pontos potenciais de cobertura e abrigo sem transformar a área em arena artificial.

## Zona D — Praça Cairu

A Praça Cairu deve funcionar como primeiro **hub externo** do MVP.

Objetivos:

- criar hierarquia clara entre área de circulação, permanência, travessia e acesso aos POIs;
- preservar linhas visuais para Elevador Lacerda e Mercado Modelo quando possível;
- permitir pedestres em grupos, eventos, vendedores e missões futuras;
- evitar uma praça excessivamente preenchida.

Entregáveis:

- pavimentação/zonas de piso mais legíveis;
- mobiliário modular;
- vegetação controlada;
- pontos de sombra/permanência;
- corredores livres de travessia;
- pontos potenciais para NPC/eventos;
- revisão das bordas de rua e calçada.

## Zona E — Mercado Modelo

Objetivos:

- reforçar o edifício como POI principal;
- melhorar transição entre exterior e acessos;
- organizar entorno imediato para leitura de gameplay;
- preparar espaço para fluxo de pedestres, veículos e possíveis missões.

Entregáveis:

- tratamento coerente da praça/área frontal;
- mobiliário e vegetação sem ocultar fachada principal;
- zonas de acesso bem definidas;
- espaço reservado para carga/serviço quando fizer sentido na cena existente;
- iluminação de leitura de fachada apenas se não exigir reconstrução do asset.

## Ruas e calçadas

A R30 deve revisar o corredor principal procurando:

- mudanças abruptas de largura;
- buracos entre terreno e via;
- calçadas sem conexão;
- guias flutuantes;
- degraus incompatíveis com travessia;
- superfícies sobrepostas;
- vias que terminam sem justificativa visual;
- áreas de pedestres invadidas por mobiliário;
- espaço insuficiente para veículos.

Correções simples e seguras podem ser feitas. Problemas estruturais derivados do DEM devem ser documentados em vez de mascarados com geometria arbitrária.

## Iluminação e atmosfera

Nesta revisão, iluminação serve para **leitura de arte**, não para fechar o sistema final de dia/noite.

Criar uma configuração de preview consistente que permita avaliar:

- silhueta do Elevador Lacerda;
- diferença de nível Cidade Alta/Cidade Baixa;
- Praça Cairu;
- fachada e volume do Mercado Modelo;
- leitura das ruas.

O sistema final de iluminação dinâmica deve permanecer separado.

## Vegetação

Usar vegetação para composição e identidade, não para esconder problemas de geometria.

Regras:

- não bloquear corredores principais;
- não ocultar hero assets;
- preferir instâncias;
- separar vegetação decorativa da lógica futura de colisão;
- evitar distribuição uniforme ou procedural sem direção artística.

## Gameplay espacial

A R30 deve reservar explicitamente:

- rota principal de pedestres;
- pelo menos alguns desvios laterais;
- espaços para encontros de NPCs;
- áreas potenciais de cobertura;
- zonas de entrada/saída de veículos;
- pontos de câmera com boa leitura;
- áreas que possam receber missões sem reconstrução pesada.

## Performance

Antes de adicionar detalhe a qualquer objeto/área, consultar:

- `R29_OPTIMIZATION_REPORT`;
- `R29_LOD_COLLISION_CANDIDATES`;
- `scene_summary.json` exportado da cena validada.

Regras:

- evitar detalhar objetos que já aparecem como gargalos graves sem estratégia de LOD;
- usar instâncias para props repetidos;
- manter `PROXY_OSM` fora da exportação padrão;
- registrar qualquer crescimento relevante de polígonos;
- não executar otimizações destrutivas escondidas dentro da R30.

## Validação visual obrigatória

Antes de considerar a R30 concluída, gerar capturas comparáveis de pelo menos:

1. visão geral Cidade Alta → Cidade Baixa;
2. entrada superior do Elevador Lacerda;
3. saída inferior;
4. Praça Cairu;
5. Mercado Modelo;
6. corredor de rua principal da Cidade Baixa;
7. vista ampla mostrando relação com a Baía quando disponível.

As câmeras de QA/revisão existentes devem ser reutilizadas quando forem úteis.

## Critério de conclusão

A R30 está concluída quando:

- o corredor jogável está visualmente mais legível;
- Praça Cairu funciona como hub espacial;
- saída inferior do Elevador possui transição urbana convincente;
- Mercado Modelo tem entorno coerente;
- ruas/calçadas principais não apresentam falhas visuais óbvias dentro do slice;
- novos props repetidos usam estratégia modular/instanciada;
- não ocorreu regressão funcional no Elevador;
- nenhuma geometria hero foi reconstruída destrutivamente sem revisão própria;
- métricas e capturas foram exportadas e registradas.

## Depois da R30

A sequência recomendada é:

- **R31:** colisões simplificadas, exportação e chunks reais;
- **R32:** corredores de tráfego e pedestres;
- **R33:** base de gameplay sistêmico do vertical slice;
- **R34+:** expansão territorial controlada para áreas adjacentes.
