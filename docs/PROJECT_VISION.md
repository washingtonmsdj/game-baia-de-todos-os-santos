# Visão do Projeto

## Identidade atual

**Nome do jogo:** Bay of All Saints  
**Tagline:** *Todos têm um preço. Ninguém é santo.*

O nome ainda deve ser tratado como marca em desenvolvimento até serem concluídas verificações de disponibilidade, marca registrada, busca em lojas e domínio.

## Conceito do jogo

Bay of All Saints é um jogo de ação em mundo aberto ambientado em Salvador, Bahia, Brasil.

A ambição não é criar apenas uma pequena demonstração de um ponto turístico. A região do Elevador Lacerda é o primeiro recorte do MVP de um jogo pensado para crescer até uma escala urbana muito maior.

No longo prazo, o mundo deve representar Salvador como uma cidade densa, vertical, costeira e socialmente diversa, com bairros reconhecíveis, marcos arquitetônicos, padrões de trânsito, ladeiras, áreas formais e informais, zonas comerciais, regiões históricas, orla, vida noturna, áreas residenciais e expansão periférica.

## Pilares centrais

### 1. Salvador é a protagonista

A cidade não deve parecer um mapa genérico de mundo aberto com elementos brasileiros adicionados por cima. Geografia, arquitetura, altitude, som, mobilidade, vida de rua, clima, vegetação, referências culturais e diferenças entre bairros devem influenciar o gameplay.

### 2. Cidade vertical

Cidade Alta e Cidade Baixa não são apenas características visuais. Mudanças de altitude, ladeiras, escadarias, elevadores, viadutos, encostas, mirantes, túneis e circulação em camadas devem fazer parte da navegação, perseguições, missões, fugas e exploração.

### 3. Mundo aberto sistêmico

A experiência pretendida é um sandbox urbano sistêmico na tradição ampla de jogos como GTA e 171, mas com identidade própria construída em torno de Salvador.

O projeto poderá incluir veículos, pedestres, resposta policial, facções, negócios, trabalhos, propriedades, economia, missões de história, eventos emergentes e atividades. Esses sistemas devem ser introduzidos de forma incremental depois que o recorte urbano estiver estável.

### 4. Convincente antes de enorme

O projeto deve preferir um distrito convincente e jogável a um mapa gigantesco e vazio.

Cada nova área deve passar por um pipeline consistente:

1. referência e escala;
2. blockout;
3. travessia;
4. rotas de gameplay;
5. passe de marcos arquitetônicos;
6. lógica de tráfego e pedestres;
7. otimização;
8. passe de arte e detalhamento;
9. integração de gameplay;
10. validação.

### 5. Fidelidade orientada à jogabilidade

O objetivo não é reproduzir Salvador de forma cadastral ou milimétrica. O mundo real serve como referência estrutural; a versão final deve ser uma **Salvador jogável**.

Preservar com alta fidelidade os elementos que definem a identidade e a leitura da cidade, especialmente:

- relação Cidade Alta/Cidade Baixa;
- posição relativa dos principais marcos;
- eixos e conectividade das vias;
- escarpa e diferenças de altitude em escala urbana;
- coastline, cais e relação com a Baía;
- sequência espacial dos locais reconhecíveis.

Adaptar conscientemente quando necessário para:

- dirigibilidade;
- circulação do jogador;
- navegação de NPCs;
- colisão estável;
- leitura visual;
- câmera;
- performance;
- missões e perseguições.

Diferença entre DEM/OSM e Blender é evidência para análise, não ordem automática de correção. Uma divergência pequena pode permanecer quando não prejudica identidade, continuidade ou gameplay.

A política detalhada está em `docs/GAMEPLAY_FIDELITY_POLICY.md`.

## Área atual do MVP

O primeiro vertical slice está centrado em:

- Elevador Lacerda;
- Praça Tomé de Sousa / acesso pela Cidade Alta;
- aproximação superior de pedestres;
- sistema do elevador e cabines;
- saída inferior;
- Praça Cairu;
- Mercado Modelo;
- malha viária imediata da Cidade Baixa.

A cena atual já contém diversas revisões e deve ser evoluída, não reconstruída do zero.

O mesmo corredor será usado como primeiro teste funcional de gameplay, com personagem, colisão, veículo, tráfego básico, NPCs/pedestres e navegação antes de expandir o mapa em grande escala.

## Arquitetura funcional do mundo

A geometria visual não deve carregar sozinha todas as responsabilidades de gameplay. O projeto deve manter separadas, quando implementadas, camadas equivalentes a:

- referência geográfica;
- ambiente visual final;
- terreno jogável;
- áreas dirigíveis;
- áreas caminháveis;
- navegação de NPCs;
- colisão simplificada;
- Hero assets;
- água;
- setores/streaming.

A lógica de trânsito também deve ser separada da geometria das ruas: lanes, direções, interseções, conexões de conversão, zonas de velocidade, travessias, semáforos, spawns e estacionamento devem evoluir como dados de gameplay próprios.

## Engine

A engine definitiva ainda não deve ser escolhida apenas por preferência ou popularidade.

Blender, metadados e pipeline do mundo devem permanecer suficientemente neutros para futura integração com Godot, Unity ou Unreal. A decisão deve ser tomada depois de um vertical slice funcional real, medindo:

- qualidade de navegação;
- veículos;
- IA de pedestres e trânsito;
- streaming;
- iluminação;
- ferramentas de mundo aberto;
- performance;
- manutenção do pipeline.

## Direção de expansão do mundo

Depois que o MVP atual estiver estável e pronto para jogo, possíveis corredores de expansão incluem Centro Histórico/Pelourinho, Comércio, conexões com a orla, Barra, Rio Vermelho, Liberdade, Itapuã, Pituba, Cajazeiras, Subúrbio Ferroviário e outros bairros.

A ordem de expansão deve ser definida por gameplay, custo de produção, viabilidade técnica e necessidades narrativas, e não por uma tentativa prematura de cobrir toda a cidade de uma vez.

## Princípio de produção

Todo trabalho importante de construção do mundo deve permanecer reproduzível. Transformações do Blender que possam ser automatizadas devem ser versionadas neste repositório para que outro agente ou desenvolvedor consiga reproduzir, inspecionar ou reverter a alteração.

Documentação e handoffs devem ser atualizados junto com mudanças relevantes de direção, pipeline ou critérios de aceitação. O projeto não deve depender de uma conversa específica para preservar decisões importantes.