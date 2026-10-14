# Encontro saguão superior–passarela — B78

Fonte: `blender/salvador_lacerda_r30b78_encontro_saguao_passarela.blend`.
Registro canônico: `world/areas/mvp-centro-lacerda/blender-revisions.json#/validation_source`.
Baseline preservada: B77B; a B76 também permanece intacta. Autoria B41 e produção B30 não são promovidas.

## Causa comprovada na cena

As paredes `SUPERIOR | posterior lateral` terminavam em Y local −4,70/+4,70, deixando um vão de 9,40 unidades. A passarela existente termina no mesmo plano X e tem bordas Y −3,00/+3,00: largura 6,00. Restavam aberturas laterais de aproximadamente 1,70 em cada lado, imediatamente atrás do saguão.

Classificação `ERROR` para essa incompatibilidade entre componentes existentes. Não é comprovação de que o saguão real ou a passarela real tenham essas dimensões. O referencial de medição é derivado do transform persistente do piso do saguão e registrado em `scene_b78.json`; nenhum alinhamento geográfico independente foi criado.

## Alteração limitada

- Prolongados os dois retornos existentes até as bordas medidas da passarela, mantendo suas bordas externas, alturas, espessuras, materiais e transforms.
- Lambris e rodapés existentes acompanham a correção, com redistribuição da malha de acabamento; paginação/dimensões reais continuam pendentes.
- A verga posterior passou a terminar no mesmo vão de 6,00, eliminando a sobreposição coplanar com os retornos prolongados. A altura do vão foi preservada.
- Dois colisores sólidos simples derivam dessas paredes e ficam na coleção existente `COLLISION | Galerias Cidade Alta R34`, separados da geometria visual e ocultos no render.

São sete malhas existentes alteradas e dois objetos derivados adicionados; nenhum objeto anterior é removido. Entrada frontal, comprimento/largura da passarela, pisos, terreno, cotas, portas, cabine, animações, SSOT e geografia não são reposicionados ou reescalados.

A primeira auditoria também detectou transforms incorretos nos colisores intermediários. Os proxies finais foram refeitos em coordenadas mundo a partir dos transforms persistentes e da hierarquia das paredes, com transform identity. O pipeline foi corrigido para evitar leitura de `matrix_world` ainda em cache, sem offset manual.

## Referências e limite da decisão

Reutilizadas referências catalogadas: fotografia `elevador-lacerda-front-1e24e0731977` (Wikimedia Commons/Thaismay, 21/07/2025) e panorama Aleph `praca-tome-de-sousa-panorama-6ab5f847ddb9` (Street View, imagem de dezembro/2024).

Elas conferem a relação entre volumes e o contexto do acesso, mas não oferecem planta cotada do encontro interno. Não foi inventada uma nova planta nem extraída medida física dessas fotos. A correção reconcilia componentes já presentes; detalhes construtivos exatos seguem `partial`. Nenhuma imagem foi importada como textura ou asset final.

Proveniência central: `derived:lacerda-junction-b78` em `world/data-provenance.json`, dependente do legado do corredor. Mantida a classe herdada pendente de verificação; a correção não aprova licença/release de todo o núcleo.

## Evidências e aceite

`docs/reports/blender/lacerda-corridor/junction_before_b78.json` registra a incompatibilidade anterior. `scene_b78.json` registra as malhas, hashes, controles e revisão salva. `validation_b78.json` decide o aceite geométrico após reabertura real.

O verificador compara todos os objetos anteriores, testa fechamento lateral por raios, continuidade das bordas, ausência de degeneração/não-manifold nas paredes, correspondência dos colisores, cápsula amostrada ao longo do percurso existente e portas animadas reais. Pisos e apoio do percurso mantêm a evidência B77B porque suas malhas e transforms permanecem iguais.

Isso não certifica física em uma engine, dimensões mecânicas do elevador, datum absoluto ou fidelidade construtiva milimétrica. O próximo trecho prioritário continua sendo soleira/cabine/poço e, depois, travessias Cairu–Mercado; expansão Lapa/Dique/Fonte Nova permanece greybox.

## Resultado da revisão reaberta

SHA-256: `b79ccf20e4bd1e30895348a742f528754a21ac7212f75b9792cf6794c5437ab0`. Aceite geométrico: `passed=true`.

6.088 objetos anteriores preservados; somente as sete malhas declaradas mudaram. Cena final: 6.090 objetos. Zero diferenças fora do escopo, zero faces degeneradas/arestas não-manifold nas paredes, 48/48 sondagens laterais fechadas e zero diferença entre vértices dos colisores e paredes. Fresta numérica máxima: 0.000000477 unidade. Erro de borda da verga: 0.000000000 unidade.

5.508 amostras de cápsula ao longo do percurso superior, incluindo interpolação a cada até 0,20 unidade: nenhum bloqueio pelas paredes corrigidas. As portas reais também permaneceram sem bloqueios nas rotas superior/inferior. B77B e SSOT mantiveram seus hashes. Não houve npm, build, exportação runtime ou suíte geral de testes.

Revisão visual frontal e interna conferida no viewport real: `visual_b78.json`. A janela foi deixada enquadrada no encontro interno.
