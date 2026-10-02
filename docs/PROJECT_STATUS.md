# Estado Atual do Projeto — Bay of All Saints

## 02/10/2026 — Conceição: binding de camada e colisor local — B38

**Autoria candidata B38**, `blender/salvador_lacerda_r30b38_binding_conceicao.blend`,
pai B37 preservado. Produção/runtime permanecem B30, sem exportação nesta etapa.
O salto histórico de cerca de 36 m no nó OSM `7520527645` não demonstrava um
degrau na Conceição: o eixo candidato atingia a Montanha. Corrigido somente o
binding de gameplay da way `421206045`, usando o eixo autoral da mesma ID/ordem
de nós e apoio visual inferior. Referência OSM, fit candidato e larguras mantidos.
Não repintar como asfalto os pontos do eixo que saem do pavimento existente.

Colisor refinado em cinco faces iniciais, com 20 vértices adicionais: diferença
máxima piso/proxy caiu de 7,17 para 4,02 cm em 910 amostras. Terreno visual e
5.255 componentes protegidos preservados. Quatro componentes conferidos por
leitura do arquivo salvo, sem abrir segunda instância Blender.

Percurso candidato separado de cerca de 136 m, 182 poses, carro V14 existente em escala
do asset. Conferidos 1.135 frames/4.540 apoios interpolados, sem apoio ausente;
desvio máximo de apoio de 6,22 cm (critério geométrico candidato, não suspensão).
Replay visível finalizado em 45,52 s, 97 atualizações observadas: não é benchmark
de performance nem validação dinâmica. Coleção de teste excluída da exportação.
**Não é circuito urbano concluído.** Curvas, extremos, colisão com todos os
edifícios e largura real permanecem em revisão; esta última é `null`.
Os runs que atingem a pista superior não são conectores entre ruas. Uma adaptação
suave de até 3,5 cm no fim do percurso retirou contato do envelope com a contenção,
sem alterar pista/parede. Rechecagem: 3.420 raios laterais sem contato, em três
alturas/estações longitudinais a cada seis frames; não cobre todo obstáculo urbano.
Evidência: `docs/reports/blender/conceicao_binding_r30b38.json`.

## 02/10/2026 — Fachadas da Cidade Baixa — B37

**Revisão histórica: B37**, `blender/salvador_lacerda_r30b37_fachadas_baixa.blend`,
pai B36 preservado; ponteiro explícito no catálogo. Produção permanece B30.
Passe localizado nas parcelas OSM 1263035780, 1220650507 e 1220650503:
paredes com espessura nos vãos, esquadrias recuadas, cornijas, peitoris,
venezianas verdes, nervuras/painéis do prédio cinza e toldo rosado com espessura.
Implantação XY, cotas, alturas e contagem de vãos existentes preservadas.
Correspondência fotográfica e medidas reais continuam candidatas, não levantadas.

Conferidos 318 componentes protegidos, incluindo terreno, vias, recuperação B23
e conjunto B36. Leitura de retorno de 18 componentes do `.blend` salvo e duas
vistas locais conferidas. Sem exportação, build ou validação de gameplay.
Relatório: `docs/reports/blender/cidade_baixa_r30b37.json`.
As limitações de fidelidade B36 permanecem; este passe não aprova a cidade inteira.

## 02/10/2026 — Terraços e continuidade das galerias — B36

**Revisão histórica: B36**, `blender/salvador_lacerda_r30b36_terracos_palacio.blend`;
pai B35 preservado. Produção permanece B30. A seleção de autoria deve seguir
`blender-revisions.json`, sem escolha por número ou data de arquivo.

Os três arcos do palácio e os dez do trecho oposto foram preservados. O trecho
do palácio, deslocado durante o passe, foi restaurado exatamente da B35;
a ligação ao terraço curvo foi acrescentada separadamente. Os dois novos
vãos são **candidatos**: contagem real e medidas levantadas continuam `null`.
Colunata inferior com sete vãos, interior aberto e escada dentro de uma
abertura real na laje; escadas do jardim com patamares e passagens nos
guarda-corpos. Dimensões/implantação fina ainda candidatas pelas fotografias.
Solo e proxy corrigidos localmente pelos limites das estruturas e borda da
ladeira existente, sem alterar vértices/largura das vias ou o DEM-fonte.

Relatório: `docs/reports/blender/terracos_palacio_r30b36.json`. Conferência de
modelagem localizada; não aprova circulação no runtime ou fidelidade da cidade
inteira. Fachada posterior sem referência suficiente preservada; entorno,
jardins e escultura ornamental continuam parciais. Sem exportação ou build.
**Revisão visual não aceita pelo usuário:** ligação acrescentada e forma da
encosta/terraços ainda diferem da foto. Não ampliar detalhes dessa candidata
antes de corrigir a implantação do conjunto pela referência disponível.

## 02/10/2026 — Correção do apoio e galerias com profundidade — B35

**Revisão deste passe: B35**, `blender/salvador_lacerda_r30b35_torre_galerias.blend`.
Ponteiro explícito em `blender-revisions.json`; B34 preservada, produção B30.
O apoio R30B08 ficava inteiro antes da parede posterior do saguão superior.
Face e capitel reconstruídos pelos planos da parede e da laje existentes;
não deslocar o edifício superior nem a torre principal para acomodar o apoio.
Galerias com abóbadas, pisos, fundos e lajes superiores separados. Profundidade
de 4,2 m **candidata**, escolhida para leitura volumétrica, não medida real;
nenhum ramal interno extrapolado. Proxies simples de piso/laje separados.
Terreno/proxy recortados nos volumes das galerias; apoio com perfil posterior
escalonado, alinhado à laje, e faixa vertical envidraçada. Arquivados o apoio
legado sobreposto e blocos antigos de terreno, preservando suas geometrias.
Talude local recomposto entre a borda existente da ladeira e os controles
superiores; sem alterar XY/largura das vias ou o DEM-fonte.

Palácio: molduras e frontões, medalhões, relevos da arquivolta, cornijas,
consoles, pedestal e colunas do portal refinados pelas fotos. Implantação e
cota preservadas. Praça com material métrico de paralelepípedos, sem deslocar
vértices ou aplicar displacement. Esculturas figurativas, fundos não documentados,
jardins/terraços inferiores do palácio e parte do entorno continuam pendentes;
o panorama ainda contém esboços. Não declarar o conjunto fiel/concluído.
Relatório: `docs/reports/blender/torre_galerias_r30b35.json`.
Reabertura do hash registrado confirmada na mesma janela. Conferidos 256
componentes preservados e os componentes de fachada alterados. As 39 amostras
de cada malha (visual e proxy) não encontraram solo dentro das galerias.
Comparação visual localizada registrada; isso não aprova a cidade inteira.
Sem exportação, npm/build ou testes gerais nesta etapa de modelagem.

## 02/10/2026 — Palácio Rio Branco, galerias e borda da praça — B34

**Trabalho: B34**, `blender/salvador_lacerda_r30b34_palacio_galerias.blend`.
Continuar pelo ponteiro de `blender-revisions.json`; pai B33 preservado.
Produção/navegador continuam B30. Edição na mesma janela MCP 9876.

Nove capturas enviadas pelo usuário catalogadas como `REFERENCIA_INTERNA`,
licença desconhecida; nenhuma pesquisa nova nem imagem usada como textura.
O edifício das fotos é o **Palácio Rio Branco**. A Prefeitura/Palácio Tomé de
Souza é outro edifício e não foi substituída.

Palácio: planta e cota de implantação herdadas; alas com paredes vazadas,
janelas/caixilhos, três entradas, escadaria, cornijas, pilastras, sacadas,
pórtico lateral, cobertura e cúpula apoiada com nervuras/lucarnas/lanternim.
Esboço anterior arquivado, sem apagar nomes ou dependências. Revisão visual
corrigiu a conversão local→mundo do corpo das alas e fechou as empenas.
Alturas/profundidades são candidatas pela fotografia; não medidas reais.

Galerias: três arcos gradeados no trecho do palácio e dez vãos no trecho
oposto, alinhados aos capeamentos existentes. Extensão parcial; associação
fotográfica/controle ainda candidata. A transição suave do terreno encobria
os arcos. Corrigidas duas bandas locais de contenção no terreno e proxy,
sem escala Z global, alteração do DEM-fonte ou deslocamento XY de vias.
Lajes sobre as galerias conservam a cota superior amostrada da praça;
colisores simples separados em `COLLISION | Galerias Cidade Alta R34`.
Pedra/argamassa das galerias em escala métrica procedural. Material do
barranco localizado por atributo e reamostrado após a retopologia, sem
aplicar ruído à pista nem usar fotos como textura.

Relatório: `docs/reports/blender/palacio_rio_branco_r30b34.json`.
Conferência visual localizada e reabertura registradas no relatório; não é
aprovação de jogabilidade. Preservados 212 componentes protegidos e 192.597
posições de vértices das superfícies de circulação. A consulta local do
proxy não encontrou vértices de pista nessa banda; não equivale a teste de
veículo. Nenhuma exportação runtime, build/npm, testes gerais ou commit.
Esculturas figurativas, interiores e fundos sem vista suficiente permanecem
pendentes. Colunata branca/escadaria da encosta não instanciadas por palpite:
falta controle de implantação próprio. Promover/exportar exige declarar as
novas coleções HERO/ENVIRONMENT_FINAL/COLLISION e validar circulação.


> Documento vivo. Atualizar quando houver mudança relevante de revisão, direção, pipeline, bloqueios, engine, vertical slice ou critério de produção.

**Atualizado em:** 2026-10-02

## Revisões e modelagem da Cidade Baixa — 02/10/2026

**Trabalho: B33**, declarada em `world/areas/mvp-centro-lacerda/blender-revisions.json`.
**Produção registrada: B30**, mantida no contrato. A candidata não atualizou o navegador.
A cadeia B23–B33 mantém fontes anteriores; B23 é histórica, R30C rejeitada.

B31 preservou terreno/colisão B30, porém seu gerador regrediu fachadas já modeladas.
B32 recuperou da B23 três corpos e 38 componentes, incluindo toldo, e ocultou
somente 23 substituições regressivas da B31. Conferência após reabrir: os 41
componentes recuperados têm geometria, transforms e materiais iguais à B23;
terreno/proxy iguais à B30. A recuperação da sessão suja B23 não diferiu da
fonte salva nesse escopo; a cena inteira não foi comparada.

B33 acrescenta três fachadas nas parcelas OSM `1263035780`, `1220650507` e
`1220650503`, usando apenas a mesma foto enviada e catalogada. Vãos, vidros,
caixilhos, cornijas, frisos, folhas verdes, toldo rosado e cobertura separados.
A revisão visual corrigiu a frente do prédio cinza (aresta frontal 2) e fechou
a empena sob o telhado. Acrescentado acabamento concêntrico da fonte apoiado
na mesh existente e material de água; escultura vinculada e implantação preservadas.
Plantas, fundações, terreno, pistas, colisor e recuperação B23 não alterados.
Alturas, larguras do acabamento/toldo e identificação fotográfica são candidatas;
não foram apresentadas como dimensões medidas ou assets aprovados.

Ruína do morro: falta confirmar vínculo/implantação; não colocada por aproximação.
Fundos, interiores, edifícios ilegíveis e ornamentos ausentes aguardam outras fotos.
Relatórios: `cidade_baixa_r30b32.json`, `cidade_baixa_r30b33.json`.
Conferência localizada/reabertura do passe final registrada no relatório B33.
Sem pesquisa nova, exportação runtime, npm/build, testes gerais ou commit neste passe.

Janela de edição: **9876**, mesma instância adotada. Guard confere PID/porta,
caminho/hash. Recuperações locais em `artifacts/blender-sessions/`.
Procedimento e prevenção de regressões: `docs/BLENDER_REVISION_POLICY.md`.
Não escolher pela janela aberta/sufixo/data nem recomeçar toda a cidade na B23.

## Histórico recente: terreno e malha

### Conexões reais e recorte do chão — R30B.30

Fonte ativa: `blender/salvador_lacerda_r30b30_conexao_real_recorte.blend`,
derivada da R30B.29/R30B.23; anteriores preservadas. Extensão integrada de 4 m
na borda sul junto ao nó OSM `619722483`, compartilhado por `1075624458`
(Praça Castro Alves) e `421206045` (Ladeira da Conceição da Praia). O recorte
anterior excluía esse nó por 1,30 m. Foram acrescentados 100 vértices/96 faces
no terreno e 64 vértices/60 faces no colisor separado, sem mover vértices
anteriores, alterar larguras ou acrescentar conexões ao grafo.

Classificação `ADAPT_LOCAL`: continuação das seções/materiais autorais na borda;
alturas extrapoladas de tangentes locais, **não altimetria real medida**.
Depois de reabrir: 41 poses/205 sondas de apoio, nenhuma ausência de chão,
delta máximo visual–colisor de 9,4 mm e nenhum alerta de torção acima de 8 cm.
Carro V14 existente, 195 componentes, percorre esse segmento em um replay
cinemático separado de 201 quadros/8,04 s. Isso não aprova largura, suspensão,
obstáculos, tráfego ou circulação do ônibus. Relatórios: `terrain_real_boundary_extension.json`,
`terrain_real_boundary_verify.json` e `terrain_real_boundary_vehicle.json`.

O grafo guarda uma aresta física com `direction=forward/reverse/both`; o replay
anterior só derivava arcos `from→to`. O helper foi corrigido para interpretar
ambos os sentidos e virar a orientação do carro ao percorrer o sentido inverso.
Nenhuma rua foi criada para essa correção. A busca de topologia real confirmou
um retorno de 871,62 m: Praça Castro Alves → Ladeira/Rua da Conceição da Praia →
Santos Dumont → Pinto Martins. `osm_real_return.json` conserva cada ID/sentido.
Esse é um circuito candidato de verificação, **não uma linha pública de ônibus**.

**Continua bloqueada a aprovação do circuito:** conflito de níveis da Conceição
descrito abaixo; trechos sem cobertura de pavimento; larguras reais ausentes.
Duas seções autorais da Conceição têm aproximadamente 2,4–2,5 m de asfalto,
com resolução de sondagem de 10 cm; não são medidas da rua real nem justificam
alargá-la para o ônibus nominal de 2,55 m. A auditoria ampla referenciada no
planejamento ainda é a R30B.29, identificada explicitamente nos relatórios;
a verificação nova da R30B.30 é localizada. Não houve exportação de runtime,
`npm`, build, CI ou commit nesta etapa.

### Histórico da rede viária — R30B.29


Fonte ativa: `blender/salvador_lacerda_r30b29_colisao_rede_viaria.blend`.
Mantém a geometria visual e as larguras da R30B.28, derivada da R30B.23.
Refino local adicional da colisão em seis faces, com 26 vértices novos:
66.199 vértices no proxy, sem copiar a malha visual detalhada.
Após salvar e reabrir, foram conferidas 59.723 sondas em 587 segmentos cobertos;
59.720 têm terreno-fonte. Nenhuma dessas sondas perdeu apoio no proxy; diferença
máxima visual–colisão de 4,55 cm, todas abaixo de 5 cm. As três sondas restantes
ultrapassam a borda do mapa em duas poses já catalogadas como SOURCE_LIMITATION.
Isso certifica concordância geométrica, não circulação dinâmica nem ausência
de defeitos na própria fonte. Relatórios: `terrain_proxy_network_refinement.json`
e `terrain_proxy_network_verify.json` em `docs/reports/blender/`.

A revisão localizada dos 28 segmentos com alertas confirmou uma descontinuidade
de aproximadamente 36,6 m no eixo da Ladeira da Conceição da Praia, junto da
Montanha (`way-421206045-seg-6/7`). A sondagem de colunas não encontrou uma via
inferior sob o pavimento elevado: não se trata apenas de escolher outro hit do
raycast. O eixo da Conceição passa a ~2,97 m do eixo da Montanha nesse ponto,
onde os pavimentos estão em níveis distintos. A causa exata da composição
dessas superfícies e seus limites laterais exige revisão estrutural; não criar
um túnel/ponte fictícios nem deformar a Montanha para eliminar a métrica.
O fit DEM–Blender histórico é `insufficient`; a medida real de largura é `null`.
Esse conflito não foi reparado e impede aprovação da rede inteira. Perfis:
`terrain_remaining_profiles.json`. O replay passa a rejeitar apoio ausente ou
torção de quatro rodas acima de 20 cm, critério explícito do teste geométrico,
sem tratar toda ladeira como erro.

Os arquivos OSM/DEM originais foram localizados na captura Aleph histórica.
Leitura read-only do GeoTIFF confirmou EPSG:3857, PixelIsPoint e espaçamento
projetado de ~4,78 m. As duas vias não têm tag de largura. A separação de seus
eixos no ponto crítico (~2,97 unidades Blender) é menor que a resolução projetada
convertida pelo fit XY (~4,63 unidades); esse DEM não resolve ali os limites e
cotas de cada pista. Não foi aplicado diretamente como perfil viário ou fit Z.
`terrain_conceicao_source_check.json` preserva hash, IDs e amostras. Para resolver
o conflito sem alterar larguras, faltam controles locais confiáveis das bordas
e cotas das duas vias; as fontes disponíveis não autorizam escolher uma das
superfícies por aproximação e declarar a outra correta.

Reteste R30B.29 com o carro V14 existente: 587 segmentos, 12.069 poses;
19 segmentos da Montanha percorridos continuamente em 143,72 s de replay.
Bloqueios explícitos: `way-421206045-seg-7` (Conceição) e os dois segmentos
de borda `way-397449211-seg-1` / `way-531109209-seg-1`. Mantêm-se 23 alertas
de torção e 71 de inclinação para revisão. Arquivo visível de teste:
`artifacts/terrain-vehicle/r30b29_vehicle_test.blend`. A fonte de produção
R30B.29 foi preservada; antes de exportar, reabri-la via MCP pelo contrato.
`terrain_vehicle_audit_r30b29.json` e `terrain_vehicle_replay_r30b29.json`
registram os resultados. Sem física de suspensão, validação de obstáculos,
exportação de runtime, npm, build ou commit. O mapa inteiro permanece parcial.

### Correções anteriores sobre a R30B.23 — R30B.28

Fonte anterior: `blender/salvador_lacerda_r30b28_colisao_viaria_refinada.blend`,
derivada exclusivamente da R30B.23 escolhida pelo usuário. A R30B.23 foi preservada.
R30B.24 corrigiu o perfil do encontro Montanha/Pau da Bandeira; R30B.25 unificou
a superfície local do encontro, preservando XY, larguras, materiais e topologia
do terreno visual. Nas seções auditadas, o desnível lateral caiu de ~0,93 m para
menos de 3 mm. Não houve nivelamento global das ladeiras.

O proxy histórico não acompanhava o transform da malha-fonte. Seus limites XY
locais coincidem com os da fonte, com erro numérico máximo de ~1,77 mm. R30B.26
restaurou o proxy preservado, vinculou-o ao transform existente do terreno e
atualizou alturas por amostras individuais. Zero vértices sem suporte após
sondas numéricas de borda de 2 mm. R30B.27 aplicou o transform aos vértices do
proxy para evitar world matrix stale no objeto oculto após reabrir. R30B.28
refinou localmente as faces de colisão divergentes: apenas 122 vértices novos,
66.173 no total. Não substituiu o collider pela malha visual detalhada.
Conferência após reabrir: 1.428 amostras na Montanha/Pau da Bandeira, zero apoio
ausente, diferença máxima visual–colisão 3,87 cm. Aprovação somente geométrica
desse percurso; não certifica suspensão, obstáculos ou toda a cidade.

Reteste da geometria visual R30B.25: 587 segmentos e 12.069 poses; replay
cinemático completou os 19 segmentos da Ladeira da Montanha sem interrupção.
As duas ocorrências de apoio ausente nas demais vias (Travessa Professor Antônio
Borja e Rua do Carro) foram localizadas nas bordas do recorte: rodas ultrapassam
os limites da malha disponível. Classificação SOURCE_LIMITATION, não buraco
interior; não criar terreno fictício nem ampliar ruas para acomodar o carro.
Esses finais de percurso precisam de limites de navegação. Há também alertas de inclinação/não coplanaridade
que exigem revisão. A cidade inteira NÃO está aprovada. Teste dinâmico de
suspensão, validação no navegador e cinco minutos de gameplay continuam pendentes.
Não houve exportação/runtime, npm, build ou commit nesta continuação.

Relatórios atuais: `terrain_junction_finish.json`, `terrain_proxy_binding.json`,
`terrain_proxy_applied_transform.json`, `terrain_proxy_refinement.json`, `terrain_proxy_verify.json`,
`terrain_vehicle_audit_r30b25.json`, `terrain_vehicle_replay_r30b25.json` em
`docs/reports/blender/`. As notas de bloqueio abaixo são histórico anterior.

### Análise veicular da R30B.23 — 01/10/2026

Continuação: seção transversal confirmou ~0,93 m de desnível no encontro
Montanha/Pau da Bandeira e uma faixa de contenção cruzando o eixo. Correção
local preparada, mas ainda não aplicada: captura OpenGL travou o Blender/MCP
nas portas 9876 e 9877. Necessário recuperar uma única janela para modificar
a malha. Fonte ativa segue R30B.23; R30B.24 não foi criada/promovida.

Auditoria via MCP na janela única: 547.464 vértices, 1.092.489 triângulos de
terreno; 732 segmentos viários únicos do grafo OSM, com 15.838 amostras.
Ausência fora da área modelada não foi convertida automaticamente em buraco.
O sweep de quatro apoios com o asset existente V14 avaliou 578 segmentos e
11.255 poses válidas: 485 ocorrências de apoio ausente no pavimento classificado,
9 de não coplanaridade dos apoios e 58 de inclinação para revisão. Esses são
alertas geométricos, não prova de que cada ocorrência seja defeito de terreno.

Replay contínuo de 17 segmentos da Ladeira da Montanha criado na cópia de teste
`artifacts/terrain-vehicle/r30b23_vehicle_test.blend`; bloqueia antes de
`way-48846625-seg-9`. Ali há diferenças transversais de até aproximadamente
0,92 m e classificação de pavimento descontínua. Investigar o encontro de vias
antes de ajustar a malha; não ampliar a pista para acomodar o veículo.

A fonte R30B.23, XY e larguras não foram alterados. Nenhuma fonte R30C foi usada.
O replay é cinemático, não teste de suspensão/física nem tráfego de runtime.
Não declarar que o carro percorreu todas as ruas em fluxo contínuo ou que o
mapa está aprovado. Relatórios: `terrain_vehicle_audit_r30b23.json` e
`terrain_vehicle_replay.json` em `docs/reports/blender/`.

Correção de fonte solicitada pelo usuário em 01/10/2026: a composição a usar é
`blender/salvador_lacerda_r30b23_fachada_praca.blend`. As tentativas R30C abaixo
partiram de uma base anterior e não devem ser transferidas para a R30B.23 nem
tratadas como trabalho aprovado. A exportação/runtime anterior também não é
evidência de que a R30B.23 esteja integrada. Consultar o contrato executável e
`docs/reports/blender/terrain_source_selection.json` para a seleção conferida.

Nesta etapa, preservar os limites XY e larguras autorais da R30B.23, com
ladeiras e patamares. Regularizar o pavimento sem criar envelopes por classe de
rua. Largura sem fonte confirmada permanece não verificada; não apresentar a
geometria existente como levantamento. Calçadas e tráfego ficam para depois.

O usuário pediu suspender a ampliação do teste urbano e focar primeiro no chão.
Revisão de terreno R30C.5 salva pela mesma janela Blender/MCP, com R30A.11 e
revisões anteriores preservadas. Remove sobreposição da pista no corredor
Chile–Ajuda–Vassouras e regulariza seu perfil local em coordenadas mundiais.
São adaptações de gameplay, não medidas topográficas verificadas. A pista
mantém relevo: declividade máxima amostrada no eixo de aproximadamente 7,03%.
2.241 amostras tiveram suporte; conferência visual do corredor no Blender e
reabertura realizadas. O entorno exterior do corredor ainda precisa de revisão.

Pesquisa e decisões: `docs/TERRAIN_GAMEPLAY_RESEARCH.md`.
Relatório: `docs/reports/blender/urban_terrain_partition.json`.
Tráfego pausado no perfil `terrain_review`. A vertical slice e o teste jogável
de cinco minutos NÃO estão concluídos. Controle do navegador nesta sessão
falhou por timeout CDP; não tratar screenshots Blender como validação do jogo.
Validações Python obrigatórias: 62 testes aprovados, compileall aprovado,
registro de referências sem erros e com dois avisos já identificados.

## Resumo executivo

Bay of All Saints é um jogo de ação em mundo aberto ambientado em Salvador. O objetivo é construir uma cidade reconhecível e estruturalmente coerente com Salvador, mas **adaptada conscientemente para gameplay**.

O projeto não busca réplica cadastral/milimétrica. O mundo real fornece referência; a versão final deve funcionar para personagem, carros, NPCs, câmera, colisão, navegação, trânsito, missões e performance.

Diretriz obrigatória: `docs/GAMEPLAY_FIDELITY_POLICY.md`.

## Repositório

`washingtonmsdj/game-baia-de-todos-os-santos`

Branch de produção: `main`.

## Fonte ativa do MVP e contrato de produção

**SSOT executável:** `world/areas/mvp-centro-lacerda/production.json`.
Fluxo obrigatório: `docs/MVP_PRODUCTION_PIPELINE.md`.

A composição ativa para o MVP Three.js é a **R30A.11**, escolhida explicitamente
pelo usuário: `blender/salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a11_pedestrian_nav.blend`.
O contrato registra o SHA-256; exportadores e runtime derivado usam essa mesma fonte.
A R30A.12 permanece preservada, mas não pode substituir a fonte ativa apenas por
ter um número de revisão maior. Não há promoção automática.

Revisão visual candidata do Elevador: **R30B.22**, em
`blender/salvador_lacerda_r30b22_exterior_vidros.blend`. Inclui a remodelagem
da encosta junto à Ladeira da Montanha, o apoio oposto em sua posição original
e o acabamento escuro das venezianas nas duas faces principais da torre.
R30B.21–22 corrigem o recorte da face oposta, os materiais do acesso inferior,
a transparência dos vidros e o encaixe do letreiro, com microrelevo no reboco.
O asfalto medido permanece em cerca de 6,5–7,0 m. A base do apoio ainda é
parcialmente encoberta na vista da Cidade Baixa, e o terreno requer revisão
conjunta com a via antes de qualquer promoção. A R30B.14, que deslocou o apoio,
foi rejeitada. A R30A.11 continua sendo a fonte ativa do runtime. Ver
`docs/revisions/R30B22_LACERDA_EXTERIOR.md`.

O ônibus tem fonte editável própria em `blender/assets/onibus_torino_31065_v03.blend`.
Os Hero assets existentes continuam em coleções da composição: não foram cortados,
reposicionados ou migrados destrutivamente para novas bibliotecas.

O pipeline agora separa fonte Blender, staging de exportação e releases de runtime.
O carregador usa manifesto com hashes, setores espaciais, fila limitada e descarte
de recursos. Terreno visual amplo/core e colisão integral ainda não têm streaming
geométrico completo. LOD, rig e medição de performance permanecem pendentes.

## Histórico das revisões (não determina a fonte ativa)

### R30A.12 — links revisados de navegação

A camada pedonal agora possui conexões promovidas somente quando existe evidência suficiente: `5/5` travessias têm match exato de OSM node ID e deslocamento visual ≤ `2,5 m`, portanto receberam links curtos de navegação revisados.

Os 6 ways de escada produziram `12` endpoints candidatos; `11` foram materializados sobre o collider. O endpoint inicial da `Escadaria do Passo` (`way 530127473`, node `5148629906`) permanece unresolved porque não há superfície jogável no ponto atual.

Cena oficial: `blender/salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a12_nav_links.blend`. Relatório: `docs/reports/blender/r30a12/R30A12_REPORT.md`. Contrato: `docs/reports/blender/r30a12/nav_links.json`.

Próximo foco: vertical slice funcional de locomoção de jogador/NPC usando caminhos, travessias e escadas já revisados.
### R30A.11 — navigation hints de pedestres

A base pedonal do vertical slice foi materializada de forma engine-agnostic: `126` caminhos OSM, `6` escadarias, `487` nós e `488` segmentos. A cena cria `125` helpers de caminho, `5` de escada, `106` junctions e `5` crossing anchors sem gerar navmesh final.

`471` nós foram resolvidos sobre o collider jogável; `16` ficaram fora/sem contato. As cinco travessias existentes têm match exato de `osm_node_id` com o grafo pedonal, mas continuam `review_only_not_connected` até validação da camada de navegação da engine.

Cena oficial: `blender/salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a11_pedestrian_nav.blend`. Relatório: `docs/reports/blender/r30a11/R30A11_REPORT.md`. Revisão: `docs/revisions/R30A11_PEDESTRIAN_NAV.md`.

Próximo foco: vertical slice funcional de locomoção, links revisados de travessias/escadas e entrada/saída de áreas jogáveis.
### R30A.8 ? oceano visual e ?gua de gameplay

A ?gua da Ba?a de Todos-os-Santos foi separada em autoria visual, superf?cie de refer?ncia e volume de gameplay. O n?vel f?sico permanece determin?stico em `0,35 m`; o volume atual permite nado/mergulho at? `-16 m` no recorte existente.

A camada visual usa material PBR animado e espuma derivada da borda real da malha de ?gua. Uma tentativa baseada em `REF_WATERFRONT` foi rejeitada visualmente por desalinhamento e n?o foi mantida como fonte final.

O runtime permanece engine-agnostic: ondas, consulta de superf?cie, nata??o, mergulho, buoyancy, correntes, c?mera submersa, c?usticas e p?s-processamento devem ser implementados no motor, n?o como f?sica Blender.

Cena oficial: `blender/salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a11_pedestrian_nav.blend`. Relat?rio: `docs/reports/blender/r30a8/R30A8_REPORT.md`. Contrato: `docs/reports/blender/r30a8/water_runtime_contract.json`.

Pr?ximo foco: refer?ncia de ondas de larga escala, zonas de corrente/profundidade e vertical slice runtime de nata??o/mergulho quando a engine for selecionada.

### R30A.7 — grafo lógico de vias e cruzamentos

O OSM estrutural foi convertido em uma camada lógica engine-agnostic: `187` vias, `677` nós, `743` segmentos e `174` candidatos a cruzamento. A cena materializa `177` helpers de via e `164` marcadores de cruzamento sobre o collider jogável.

Foram resolvidos `572` nós sobre a superfície de gameplay; `105` ficaram fora/sem contato com o collider. Vias parciais são divididas em sequências contíguas, sem criar pontes artificiais através de gaps.

A revisão preserva `oneway`, rotatórias, restrições e tags existentes, mas não inventa faixas, larguras ou IA de trânsito. O fit XY ainda é `candidate`.

Cena oficial: `blender/salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a7_road_graph.blend`. Relatório: `docs/reports/blender/r30a7/R30A7_REPORT.md`.

Próximo foco: navigation hints de pedestres, travessias e escadas do vertical slice.

### R30A.6 — collision chunks para runtime

O collider otimizado da R30A.5 foi dividido ao vivo, na única janela visível do Blender, em `63` chunks de `128 m`. A partição preserva exatamente os `131.097` polígonos do proxy, com razão de duplicação de vértices `1,0468577`.

Foram comparadas grades de 64/128/256 m. A grade de 128 m foi a primeira a cumprir simultaneamente os limites de quantidade de chunks, máximo de polígonos e P95 por chunk.

Cena: `blender/salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a6_collision_chunks.blend`. Relatório: `docs/reports/blender/r30a6/R30A6_REPORT.md`.

A sessão de produção usa uma única instância visível do Blender com OrdaX e BlendMCP 1.4.4 na mesma janela.

### R30A.5 — proxies de runtime e primeira colisão otimizada

A R30A.5 criou a primeira geometria derivada especificamente para runtime sem alterar a malha-fonte R30A.4. O collider do terreno reduziu de 1.082.745 para 131.097 polígonos (`-87,8922%`) e passou o gate geométrico com 5.023 amostras: erro P95 `0,0018215 m` e máximo `0,180078 m`.

A cena agora também expõe fontes engine-agnostic para vias dirigíveis, superfícies caminháveis, travessias, guias/meio-fio e água. Nenhuma engine foi escolhida e nenhum navmesh/grafo de tráfego foi inventado nesta etapa.

Cena oficial: `blender/salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a5_runtime_proxies.blend`. Relatórios: `docs/reports/blender/r30a5/R30A5_REPORT.md` e `docs/reports/blender/r30a5/runtime_manifest.json`.

O BlendMCP fallback foi revalidado na R30A.5 com addon `1.4.4`, porta `9877`, `get_addon_version`, `get_scene_info` e `get_object_info`. O launcher usa `--factory-startup --disable-autoexec` e timeout de 120 s.

Próximo foco: chunking da colisão, grafo de vias/cruzamentos e hints de navegação do vertical slice.

### R30A.4 — camadas semânticas de gameplay aplicadas

A primeira separação funcional foi aplicada diretamente no Blender por coleções e metadados não destrutivos. A geometria permaneceu invariável: 4.677 objetos, 4.137 meshes, 839.684 vértices, 2.044.767 arestas e 1.238.783 polígonos.

Camadas criadas: terreno, fonte de colisão, pistas dirigíveis, superfícies caminháveis, travessias, guias/meio-fio, água, referência geográfica e proxies legados. O terreno principal continua marcado como composto `GAMEPLAY_TERRAIN + COLLISION_SOURCE`; nenhum split destrutivo foi feito.

Cena oficial: `blender/salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a4_semantic_layers.blend`. Relatório: `docs/reports/blender/r30a4/R30A4_REPORT.md`.

Fallback Blender MCP validado em `docs/BLENDMCP_FALLBACK.md`: BlendMCP 1.4.4 na porta 9877, isolado da sessão histórica da porta 9876.

### R30A.3 — auditoria semântica direta via OrdaX concluída

A cena oficial foi inspecionada diretamente pelo ChatGPT através de OrdaX Device Agent / Blender Live, sem Codex como intermediário. Foi criado o checkpoint `pre-r30a3-direct-chatgpt`; a cena permaneceu `is_dirty=false` e nenhuma geometria foi salva.

A auditoria confirmou 4.677 objetos, 4.137 meshes e 135 materiais. O objeto `MVP | terreno corrigido | colisão estática` concentra 547.464 vértices / 1.082.745 polígonos e hoje acumula terreno jogável, colisão, asfalto, percurso pedonal, Praça Cairu, passeios e contenções.

Isso confirma que o próximo trabalho não é forçar novo fit global nem cortar a malha imediatamente. A prioridade passa a ser separar responsabilidades semanticamente e criar camadas funcionais não destrutivas para `GAMEPLAY_TERRAIN`, `ROAD_DRIVEABLE`, `SIDEWALK_WALKABLE` e `COLLISION`.

Relatórios: `docs/reports/blender/r30a3/R30A3_REPORT.md` e `docs/reports/blender/r30a3/semantic_scene_audit.json`.


### R30A.2 — diagnóstico vertical por domínio concluído

Pipeline integrado em:

`cc2de0c3bc311ba861fa9819440cd7e533704844`

Execução/relatório concluído em:

`450c377ee0fdbb385e64464959091b72bfdb195b`

Relatórios:

- `docs/reports/blender/r30a2/R30A2_REPORT.md`;
- `docs/reports/blender/r30a2/r30a2_status.json`;
- `docs/reports/blender/r30a2/vertical_domains.json`.

Estado final da rodada:

`diagnostic_complete_vertical_domain_split_insufficient`

Nenhuma correção geométrica local foi autorizada pela R30A.2.

## Principais conclusões da R30A.2

### Batimetria não explica o erro vertical

Foram 4.978 amostras DEM válidas:

- 2 abaixo de 0 m (`0,0402%`);
- 4.976 no domínio terrestre não negativo (`99,9598%`).

O robust fit já rejeitava os dois valores negativos. Separar batimetria não alterou os parâmetros do fit.

Portanto, a hipótese “a batimetria é a principal causa do RMS vertical ruim” foi descartada.

### Fit vertical continua insuficiente

R30A.2 terrestre:

- entrada: 4.976 amostras;
- mantidas: 4.900;
- outliers: 76;
- escala Z candidata: `1,0253290`;
- offset Z candidato: `-4,6316455`;
- RMS: `9,2106683`;
- mediana absoluta: `5,2179134`;
- máximo residual: `29,3265740`;
- razão vertical/horizontal: `1,0568512`;
- quality: `insufficient`.

Nenhuma escala/offset Z foi aplicado.

### A malha amostrada não é topografia pura

O objeto usado no fit foi:

`MVP | terreno corrigido | colisão estática`

Evidências da própria cena indicam que ele é uma superfície funcional/histórica de MVP:

- `game_role: static_terrain_collision`;
- derivado de `Aleph DEM + OSM`;
- contém patamares adaptados aos pisos do esboço;
- altimetria foi filtrada/corrigida para MVP;
- inclui plataformas fixas e aproximações.

Isso é decisivo para a direção do projeto: **não devemos tentar deformar essa superfície de gameplay para coincidir globalmente com o DEM**.

A partir de agora, referência topográfica e terreno jogável devem ser tratados como responsabilidades diferentes.

### Regiões críticas detectadas

A grade espacial encontrou 157 células terrestres para revisão, com destaque para:

- base da escarpa/Cidade Baixa;
- waterfront/cais;
- plataformas baixas do MVP;
- platôs da Cidade Alta;
- transições junto à escarpa/ladeiras.

Os maiores resíduos aparecem frequentemente onde a malha atual contém patamares funcionais deliberados ou onde o DEM tem dificuldade para representar transições urbanas abruptas.

Nenhuma das dez células mais críticas apontou diretamente Praça Cairu ou o footprint do Mercado Modelo como alvo de correção.

### Mercado Modelo permanece controle, não alvo

OSM way:

`59392558`

Footprint real observado com offset aproximado de:

`1,878 m`

Não mover automaticamente.

## Cobertura DEM

O falso diagnóstico histórico de `0,1584%` foi corrigido na R30A.1.

A janela real da captura Aleph está:

- `covered_with_margin`;
- cobertura: `100%`.

Captura histórica:

`data/aleph/aleph-20260924T205631Z-aqqo7pkx/`

Arquivos principais:

- `manifest.json`;
- `map.osm`;
- `terrain.tif`.

## Fit XY

Estado conhecido:

- quality: `candidate`;
- status: `candidate_only`;
- escala horizontal: `0,9701734818` unidades Blender por metro;
- rotação EPSG:3857 → Blender: aproximadamente `-0,050990°`;
- RMS: aproximadamente `4,168632` unidades Blender;
- anchors robustos: `1.012`.

Não tratar como transformação final/verificada sem revisão adicional.

## Decisão estrutural após R30A.2

Ainda **não existe evidência suficiente para autorizar uma primeira correção geométrica local baseada apenas no DEM**.

Próximo foco recomendado:

1. separar semanticamente referência física/topográfica de `GAMEPLAY_TERRAIN`/colisão;
2. obter ou validar referência vertical terrestre independente para regiões prioritárias;
3. revisar regionalmente escarpa e waterfront;
4. testar quais patamares são adaptações deliberadas de gameplay e quais são erros reais;
5. só então propor correções locais.

Importante: um patamar funcional pode permanecer diferente do DEM se ele melhora circulação/veículos/NPCs sem destruir a identidade de Salvador.

## DEM e batimetria

O `terrain.tif` histórico é derivado do conjunto Mapzen/Tilezen Terrain Tiles usado pelo Aleph.

O recorte inclui a Baía de Todos-os-Santos. Valores DEM profundamente negativos podem representar batimetria e **não devem ser classificados automaticamente como nodata/erro**.

A R30A.2 confirmou que esses pontos negativos não dominam o fit vertical.

Não editar o `terrain.tif` original.

## Filosofia de fidelidade

A pergunta de produção não é:

> “Como fazer o Blender coincidir 100% com OSM/DEM?”

A pergunta é:

> “A divergência prejudica a identidade de Salvador, a continuidade do mundo ou a jogabilidade?”

Classificações recomendadas:

- `KEEP_REAL_REFERENCE`;
- `KEEP_GAMEPLAY`;
- `ADAPT_LOCAL`;
- `SOURCE_LIMITATION`;
- `NEEDS_REVIEW`;
- `ERROR`.

Detalhes em `docs/GAMEPLAY_FIDELITY_POLICY.md`.

## Gameplay e arquitetura futura

O jogo é planejado para suportar, progressivamente:

- personagem a pé;
- veículos;
- tráfego;
- pedestres/NPCs;
- resposta policial/facções;
- missões;
- economia/atividades;
- mundo urbano sistêmico.

A geometria visual deve ser separada das camadas funcionais. Planejar equivalentes a:

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

A R30A.2 reforçou especialmente a necessidade de separar `REFERENCE_TERRAIN` de `GAMEPLAY_TERRAIN`/`COLLISION`.

Ruas visuais não são, por si só, rede de tráfego. Calçadas visuais não são, por si só, navmesh.

## Engine

Nenhuma engine foi escolhida definitivamente.

Candidatas futuras podem incluir Godot, Unity ou Unreal, mas o pipeline atual deve permanecer neutro.

A escolha deverá ser baseada num vertical slice real, não em preferência abstrata.

## Vertical slice prioritário

Corredor:

```text
Cidade Alta
→ Elevador Lacerda
→ Praça Cairu
→ Mercado Modelo
→ Cidade Baixa / waterfront
```

Antes de expansão urbana grande, esse slice deve provar:

- caminhada;
- colisão;
- câmera;
- veículo controlável;
- veículos IA básicos;
- pedestres/NPCs básicos;
- navegação;
- tráfego/interseções mínimos;
- água;
- iluminação;
- streaming/carregamento;
- performance.

## Ordem macro de desenvolvimento

1. separar referência topográfica de terreno/colisão jogável;
2. classificar regionalmente erros reais versus adaptações de gameplay;
3. corrigir somente erros estruturais realmente relevantes;
4. construir/estabilizar superfícies de gameplay;
5. consolidar escarpa e interfaces críticas;
6. coastline/cais;
7. ruas/cruzamentos;
8. escadas/calçadas;
9. footprints/Hero assets;
10. colisão funcional;
11. rede de pedestres/NPCs;
12. rede de tráfego/veículos;
13. vertical slice em engine candidata;
14. otimização e arte final do recorte;
15. expansão da cidade.

A ordem pode ser ajustada quando gameplay revelar dependências reais.

## Bloqueios atuais

- fit vertical completo e terrestre seguem `insufficient`;
- a superfície amostrada mistura terreno funcional, colisão e patamares de MVP;
- escarpa contém transições abruptas que o DEM pode representar mal localmente;
- fit XY segue `candidate`, não `verified`;
- não há referência vertical terrestre independente suficiente para autorizar correção local apenas por métrica.

Esses bloqueios não impedem planejamento de gameplay layers, classificação semântica ou preparação do vertical slice.

## O que não fazer

- não tentar zerar RMS global por princípio;
- não reconstruir a cena do zero sem motivo;
- não deformar Hero assets para acomodar erro de base;
- não transformar `static_terrain_collision` em topografia “real” por força;
- não usar geometria visual pesada diretamente como colisão/navmesh por conveniência;
- não inventar largura de rua como se fosse medida;
- não aplicar escala/offset global sem análise;
- não confundir OSM com lógica completa de tráfego;
- não expandir a cidade rapidamente antes do vertical slice ser funcional;
- não escolher engine definitiva antes de um teste representativo;
- não deixar decisões importantes apenas em chats.

## Documentos de entrada para nova IA

Ler nesta ordem:

1. `AGENTS.md`;
2. `docs/PROJECT_STATUS.md`;
3. `docs/PROJECT_VISION.md`;
4. `docs/GAMEPLAY_FIDELITY_POLICY.md`;
5. `docs/CODEX_HANDOFF.md`;
6. `docs/CODEX_STRUCTURE_HANDOFF.md`;
7. handoff da revisão atual, se existir.

## Regra de manutenção documental

Toda mudança material em qualquer um destes itens deve atualizar este documento e os handoffs afetados:

- direção do jogo;
- cena Blender oficial;
- revisão ativa;
- captura geográfica;
- critérios de fidelidade;
- pipeline estrutural;
- gameplay layers;
- engine;
- vertical slice;
- principais blockers;
- próximos passos.

O repositório deve permitir que outro agente retome o projeto sem depender da memória de uma conversa.
