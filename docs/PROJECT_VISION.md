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

## Direção de expansão do mundo

Depois que o MVP atual estiver estável e pronto para jogo, possíveis corredores de expansão incluem Centro Histórico/Pelourinho, Comércio, conexões com a orla, Barra, Rio Vermelho, Liberdade, Itapuã, Pituba, Cajazeiras, Subúrbio Ferroviário e outros bairros.

A ordem de expansão deve ser definida por gameplay, custo de produção, viabilidade técnica e necessidades narrativas, e não por uma tentativa prematura de cobrir toda a cidade de uma vez.

## Princípio de produção

Todo trabalho importante de construção do mundo deve permanecer reproduzível. Transformações do Blender que possam ser automatizadas devem ser versionadas neste repositório para que outro agente ou desenvolvedor consiga reproduzir, inspecionar ou reverter a alteração.
