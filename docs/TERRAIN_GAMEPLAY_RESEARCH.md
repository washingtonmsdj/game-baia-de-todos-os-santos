# Terreno jogável — pesquisa e decisão de produção

Pesquisa de 01/10/2026, solicitada durante a revisão da malha.

Terreno de jogo não precisa ser plano. Salvador exige preservar patamares,
ladeiras, escarpa e sua relação espacial. Cada superfície deve ser contínua no
trecho navegável, com declividade intencional e encontros sem buracos ou saltos
artificiais. Uma superfície contínua pode ser inclinada e curva.

## Referências técnicas primárias

- [Rockstar — GTA Online Race Creator](https://media.rockstargames.com/rockstargames/img/global/news/upload/GTAO_Race_Creator_Guide.pdf): contempla percursos de montanha e teste com diferentes veículos. Demonstra que relevo e circulação coexistem; não descreve o pipeline interno de malhas da Rockstar. Não atribuir à RAGE uma técnica específica sem evidência.
- [Epic — Landscape Splines](https://dev.epicgames.com/documentation/en-us/unreal-engine/landscape-splines-in-unreal-engine): perfil da via controla a integração com o terreno por largura e transição lateral suave. Isso é referência de método, não uma decisão de migrar para Unreal.
- [Unity — Terrain colliders](https://docs.unity.com/en-us/engine/6000.3/manual/physics-section/physics-overview/collision-section/collider-shapes/terrain-colliders/introduction): colisão acompanha forma, posição e escala do terreno; simplificação é possível quando sua precisão atende ao uso.
- [Blender — Clean Up](https://docs.blender.org/manual/en/latest/modeling/meshes/editing/mesh/cleanup.html): remoção de geometria degenerada, vértices duplicados e limpeza de malhas. Não substituir por preenchimento indiscriminado de todas as bordas abertas.

## Aplicação no MVP

1. Fonte atual escolhida pelo usuário: R30B.23. Preservar limites XY, larguras
   autorais e relevo. Não aumentar/diminuir a largura para facilitar o teste;
   largura real sem levantamento permanece incerta, sem valor inventado.
2. Geometria final de terreno, pista, passeio e contenção com encontros explícitos.
3. Perfil viário em coordenadas mundiais, mantendo anchors e adaptação local documentada.
4. Calçadas ficam para etapa posterior. Pontes, túneis, contenções e estruturas de múltiplos níveis precisam de meshes; um heightmap sozinho não representa tudo.
5. Colisão e navegação separadas da decoração, acompanhando o chão visível.
6. Simplificação/setores depois de conferir estrutura; nunca um plano invisível para esconder terreno defeituoso.

## Erros encontrados nesta sessão

As faixas da primeira slice estavam sobrepostas ao terreno e interpolavam alturas
que discordavam da superfície inferior. O recorte eliminou essa duplicação, mas
expôs saltos locais e bordas inadequadas. Uma revisão intermediária também leu
o transform ainda não atualizado de um objeto carregado de biblioteca, produzindo
um perfil vertical incorreto. Essa revisão não deve ser tomada como referência
geográfica validada. A leitura correta exige vincular a fonte temporária à cena e
atualizar o dependency graph antes de consultar `matrix_world`.

O foco solicitado passou a ser somente terreno/malha. Tráfego fica pausado na
revisão; a vertical slice e seu teste jogável de cinco minutos continuam pendentes.
Uma auditoria de amostras ou testes Python aprovados não equivalem à validação
visual e jogável da cidade inteira.
