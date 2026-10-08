# Mercado Modelo — aberturas arquitetônicas candidatas (B97)

## Inspeção real e verificável

Na única janela Blender aberta (PID 16912, cena SALVADOR | ESBOCO OFICIAL,
fonte B97), foram encontradas duas aberturas arquitetônicas **visíveis**,
com ombreiras e verga. A cena não tinha alterações não salvas.
As medidas abaixo são **da geometria autoral**, não medidas certificadas
do edifício real nem uma rota de gameplay aprovada.

| Abertura candidata | Centro XY Blender | Vão geométrico projetado | Altura até base da verga |
| --- | --- | ---: | ---: |
| Fachada Praça Cairu | (-126,491974; 154,290283) | 2,75891 m | 4,50 m |
| Fachada posterior | (-96,603867; 184,757965) | 2,131885 m | 4,00 m |

Os dois centros tiveram sondagens verticais positivas contra a malha
TÉRREO | laje e o terreno MVP | terreno corrigido | colisão estática,
com Z aproximadamente 7,25566 m. Os cinco controles por abertura
(-3, -1, 0, +1 e +3 m no normal local) mostraram o piso de mercado
em um lado e o terreno no outro, com cotas próximas onde houve contato.
Isso **não** demonstra o caminho completo, a ausência de obstáculos,
a largura livre após colisores, a existência das portas na edificação
real nem conexão ao último nó de rota do B82.

As peças têm status de fidelidade:
"esboço tipológico; footprint e escala exterior derivados do OSM;
interior sem planta cadastral publicada". Portanto, nenhuma das
aberturas é aprovada como entrada pública real. O objeto
MERCADO MODELO | entrada principal continua oculto na coleção LEGACY,
e **não** foi reativado nem usado como vínculo de navegação.

## Autoridade e execução

A autoridade de locais continua sendo
world/areas/mvp-centro-lacerda/locations.json.
O item mercado-modelo ainda possui blender_binding=null e OSM
way 59392558 com verified=false. Não adicionar segunda tabela
de entradas nem preencher coordenadas geográficas estimadas.

A auditoria somente-leitura automation/blender/audit_market_access.py
descobre as aberturas pelas três partes reais na coleção do Mercado,
compara geometria e níveis nos mesmos XY e submete o resultado a
tools/world/market_access.py. A classificação é sempre candidata,
nunca aprovação de rota; a futura liberação requer evidência arquitetônica
independente, binding geográfico verificado, varredura completa de colisão,
e teste de percurso ponta a ponta com personagem.

A auditoria deve executar apenas com a fonte autoral explícita já
registrada e seu SHA-256 correspondente; caso contrário falha fechada.
O código fica no GitHub para uso após a consolidação da B97 no Git LFS.
Nenhuma alteração do arquivo .blend é necessária para esta auditoria.

## Pendências de jogabilidade

- FULL_TOME_MARKET_ROUTE = NOT_APPROVED.
- MARKET_ENTRANCE_CONNECTOR = NOT_IMPLEMENTED_NOT_TESTABLE.
- LACERDA_VERTICAL = BLOCKED_EXTERNAL_EVIDENCE.
- ABSOLUTE_MAP_PLACEMENT = NEEDS_REVIEW.
- Produção continua B30; não promover B97 e não habilitar movement_enabled.
- A tentativa de varredura abrangente de obstáculos do Mercado excedeu
  o tempo de execução; **não** registrar passagem livre como comprovada.

Próximo trabalho: comparar a posição das ombreiras com fontes de
acesso físico verificadas, resolver o binding do Mercado e conferir
uma faixa caminhável contínua desde Cairu por malhas e colisores reais.


## Ligação ao último ponto do percurso experimental B82

A fonte existente `world/areas/mvp-centro-lacerda/lacerda-gameplay-proxy.json`
usa um frame local explícito e termina o percurso inferior em aproximadamente
**XY mundial (-89,289593; 106,561385)**. O centro da abertura candidata
voltada à Praça Cairu está em **(-126,491974; 154,290283)**, distante
**60,515 m em linha reta**. Não existe ligação no controller B82.

Uma nova inspeção somente-leitura no Blender B97 mediu terreno sob 16
pontos igualmente espaçados do segmento, todos com Z≈7,2557 m. Isso
comprova apenas **cobertura do terreno na linha amostrada**, não caminhabilidade
da praça. Verificação por `ray_cast` nas malhas visuais detectou pelo menos:

- **5,145 m** desde o início: encosto de banco da Praça Cairu no raio horizontal
  Z≈8,0 m;
- **58,896 m** desde o início: ombreira direita da abertura candidata do Mercado,
  com interseção em raios Z≈7,6 / 8,0 / 8,55 m.

Portanto a ligação reta **não está livre**. Esses são acertos geométricos
reais da linha, não apenas sobreposição de AABB; mesmo assim, **não**
representam um teste completo de cápsula ou da árvore de colisores. A
malha `B81 | NAV | Cairu OSM parcial bloqueada` tem envelope XY
aproximado x=[-89,29; -47,07], y=[54,16;116,06], deixando o alvo
**fora da cobertura**. Estar dentro de uma bounding box de nav
tampouco certifica conexão.

A extensão de `tools/world/market_access.py` calcula a diferença entre
o último waypoint B82 (transformado por seu frame local) e a geometria
atual do Mercado. A própria
`automation/blender/audit_market_access.py` usa broadphase para selecionar
malhas visíveis próximas e raycasts pontuais de alturas de personagem.
O resultado `direct_cairu_approach` é um **diagnóstico reproduzível**:
`route_approved=false` e `navigation_approved=false` independentemente
de o número de interseções ser zero.

### Próxima intervenção física

Propor e avaliar segmentos alternativos por malhas caminháveis e
colisores reais, considerando os bancos e ombreiras, travessias e
posição verdadeira de acesso ao Mercado. Não ligar ponto B82 a porta
candidata por reta, não mover bancos, não ampliar calçadas e não criar
navmesh por posição aproximada. A rota continua bloqueada até existir
evidência independente do acesso real e teste de deslocamento físico
ponta a ponta.


## Análise do grafo pedonal existente — 08/10/2026

O pipeline já constrói `docs/reports/blender/r30a11/pedestrian_graph.json`
com nós OSM em XY Blender, arestas, permissões e sentidos por `oneway:foot`.
Não se deve criar um segundo grafo somente para o Mercado.

Buscando o percurso de `B82.lower_route[-1]` até a **abertura modelada**
voltada à Praça Cairu, o grafo candidato contém:

- **487 nós e 488 arestas** no inventário completo;
- início em `(-89,289593; 106,561385)`, coincidente com um nó existente;
- **6 nós** encadeados por aproximadamente **72,027 m** de arestas pedonais;
- último nó em `(-126,502035; 147,578777)`;
- a abertura modelada em `(-126,491974; 154,290283)` ainda fica
  **6,712 m além desse último nó**.

Esse afastamento é superior ao limite explícito de associação de 2,5 m,
portanto **não existe ligação aprovada entre a rede OSM e a entrada**.
O caminho de 72,027 m é um *candidato sobre o grafo*, não movimento
contínuo certificado no cenário ou uma rota até dentro do Mercado.

`tools/world/build_pedestrian_graph.py` agora contém
`inspect_candidate_route`, que respeita `access=restricted`,
`oneway:foot`, separa escadas por padrão, usa distância planar acumulada
de arestas reais e rejeita snaps implícitos. A auditoria do Mercado apenas
reutiliza essa operação e reporta lacunas em
`osm_pedestrian_candidate` — não gera navmesh, novos waypoints,
colisores nem aprova `movement_enabled`.

**Próxima validação geométrica:** sondar os segmentos desse caminho
candidato na B97 com as malhas caminháveis e os colisores reais
(incluindo banco, gola de árvores, mobiliário e fachadas), testar a
largura da cápsula do personagem e buscar evidência independente da
entrada física. O trajeto atual tem `fit_status=candidate_only` e
`FULL_TOME_MARKET_ROUTE=NOT_APPROVED`.


### Sondagem visual na B97 aberta

A inspeção direta dos **cinco segmentos OSM encontrados**, no
Blender B97 já aberto, realizou raycasts à altura **Z=8,0 m** com
filtro de geometria visual relevante da Praça Cairu e Mercado Modelo.
Resultado: **zero interseções no eixo central observado**. O teste
manteve `bpy.data.is_dirty=false`, não modificou malha ou cena e não
criou um caminho no runtime.

**Limites materiais:** um único raio central não é um ensaio de cápsula
com largura/altura, não cobre colisores ocultos nem classifica
superfícies como caminháveis. Também permanece a lacuna de **6,711514 m**
do último nó OSM até a abertura tipológica não autenticada.
Assim, o resultado é somente `VISUAL_CENTERLINE_NO_HIT`;
`route_approved=false` continua obrigatório.
