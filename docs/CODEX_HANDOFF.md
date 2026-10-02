# Handoff Geral do Codex — Bay of All Saints

## Versionamento de 02/10/2026

Sincronização inclui scripts, contratos, relatórios, revisões oficiais Blender,
fonte do carro V14 e GLBs por Git LFS. As revisões R30C rejeitadas, imagens locais
de referência, backups e pacotes Base64 de transferência ficam fora do Git;
nenhum arquivo local foi removido. Os importadores V7C/V8B usam primeiro seus
GLBs versionados, validando os mesmos hashes de origem. Fontes geográficas e
acervo visual pesado continuam externos, com proveniência nos manifests.

Validações para commit: compileall de tools/tests, 62 testes Python aprovados,
cadastro de referências com zero erros e dois avisos (bounds pendentes e
cobertura do cais da Praça Cairu). Sem npm/build ou promoção de B38 ao runtime.

## 02/10/2026 — Continuar pela B38: Conceição e colisor local

Fonte candidata: `blender/salvador_lacerda_r30b38_binding_conceicao.blend`, pai B37.
Ponteiro explícito no catálogo; produção/runtime continuam B30. Não exportar
automaticamente esta revisão nem reiniciar a partir da B23/B30.

O aparente degrau de 36 m da Conceição era binding do nó `7520527645` na pista
superior da Montanha, por deslocamento do fit XY candidato. Corrigido o ponto
da curva derivada `R30A7 | ROAD | 421206045` para apoio inferior, com metadados;
fonte OSM e curva autoral permanecem intactas. Não deformar Z para apagar o
resíduo do eixo errado nem transformar solo em pista sem evidência.

Refino localizado do proxy: 20 vértices novos; 910 amostras, erro máximo 4,02 cm.
5.255 componentes protegidos, terreno visual e larguras preservados. Replay com
carro V14 existente em trecho contínuo de cerca de 136 m: 1.135 frames/4.540 apoios
interpolados sem ausência; execução visível concluída em 45,52 s (97 updates).
Esse método é cinemático, com bitola/limite de esterço nominais registrados,
não física dinâmica nem prova de desempenho/colisão urbana completa.

Contato inicial de até 5,5 mm do envelope com a contenção foi corrigido por
adaptação suave do percurso de teste, até 3,5 cm nos últimos 12 apoios, dentro do
asfalto existente. `ADAPT_LOCAL` documentado; largura e geografia inalteradas.
Curva salva conferida novamente por biblioteca. Checagem lateral final: 3.420
raios sem contato; limitações/critério de amostragem registrados no relatório.

No Blender: coleção `GAMEPLAY | VALIDACAO | Conceicao B38`, timeline 1–1135,
25 fps; espaço reproduz o trecho. Carro/percurso são somente validação,
fora da exportação. Relatório: `docs/reports/blender/conceicao_binding_r30b38.json`.
Próxima pendência: curvas/extremos sem envelope contínuo confirmado. Não unir
runs independentes, sobretudo o run 239–250 que atingia a Montanha; largura
real continua `null`. Não criar retorno fictício para fechar circuito.

## 02/10/2026 — Continuar pela B37: fachadas da Cidade Baixa

Fonte candidata: `blender/salvador_lacerda_r30b37_fachadas_baixa.blend`, pai B36;
consultar `blender-revisions.json#/authoring_source`. Produção permanece B30.
Relatório: `docs/reports/blender/cidade_baixa_r30b37.json`.
Refinadas as três fachadas já existentes ao sul do acesso inferior:
OSM 1263035780, 1220650507 e 1220650503. IDs/plantas/cotas preservados;
paredes com espessura, caixilhos e vidros recuados, cornijas/peitoris,
venezianas verdes, nervuras e painéis cinza, toldo rosado com espessura/bandô.
Sem novas fachadas posteriores ou detalhes extrapolados da foto ilegível.

Mutação R37 já aplicada: não repetir o script. 318 componentes protegidos
inalterados. Os 18 componentes modificados foram relidos do arquivo salvo
na mesma instância; isso não equivale a recarregar a cena inteira nem a validar
gameplay. Duas vistas locais registradas. Binding fotográfico, dimensões reais
e fidelidade global continuam candidatos. B36 segue visualmente não aceita;
o usuário pediu prosseguir em outras áreas. Não ocultar essa pendência.
Sem pesquisa nova, exportação, npm/build ou testes gerais.

## 02/10/2026 — Continuar pela B36: terraços e galerias preservadas

Fonte candidata: `blender/salvador_lacerda_r30b36_terracos_palacio.blend`, pai B35;
consultar o ponteiro explícito em `blender-revisions.json`. Produção B30.
Relatório: `docs/reports/blender/terracos_palacio_r30b36.json`.

**Não remover ou deslocar as galerias anteriores.** Três arcos do palácio
restaurados da B35, dez do trecho oposto inalterados. A ligação nova ao terraço
é separada; dois vãos candidatos, contagem real `null`. `final_layout` registra
o estado final e prevalece sobre as etapas intermediárias do relatório.
Colunata inferior, pisos, lajes, abóbadas, escadas e colisores separados.
Escada da colunata no interior da laje; escadas do jardim no lado oposto às
galerias, com patamares e aberturas nas contenções/guarda-corpos.
Solo/proxy recortados nos interiores e perfil local recomposto até a borda
existente da ladeira. Não alterar vias/DEM para acomodar decoração.

Scripts R36 de mutação já aplicados: não executá-los novamente. Conferências
locais e reabertura constam no relatório quando concluídas. Esta candidata
não foi exportada, nem aprovada para gameplay. Medidas reais, implantação
fina dos terraços, jardins e fachada posterior continuam pendentes; não
extrapolar detalhes ilegíveis nas fotos.
Feedback final do usuário: o passe consumiu tempo excessivo e continua sem
fidelidade suficiente. Não considerar a candidata aprovada. Primeiro resolver
a implantação relativa do terraço, três arcos originais e encosta; não expandir
o trecho candidato ou acrescentar decoração para disfarçar diferenças.
A B36 salva foi registrada e reaberta pelo hash: `load_post` confirmado.
Após a reabertura houve demora de resposta; PID 28348 foi adotado novamente.
Assinaturas pós-reabertura B36 conferidas antes do passe B37, com resultado
em `saved_source_reopened` no relatório. Não repetir a mutação B36.

## 02/10/2026 — Continuar pelo ponteiro B35

**Revisão histórica deste passe:** `blender/salvador_lacerda_r30b35_torre_galerias.blend`.
Pai B34 preservado; fonte explícita no catálogo, produção permanece B30.
Correção do apoio R30B08: alinhar a face à parede posterior superior e o
capitel à laje do saguão; não mover o saguão/torre principal ou inventar offset.
Galerias agora têm interiores com abóbada, piso e fundos a 4,2 m de profundidade
candidata; dimensão real `null`. Terreno/proxy escavados nos volumes dos vãos,
mantendo o piso superior apoiado em laje própria. Apoio com recuos posteriores
em níveis, três faixas verticais de vidro e capitel ligado à laje. Apoio antigo
sobreposto/blocos de terreno legados arquivados na coleção REFERENCE R35.
Talude localizado recomposto pelos controles existentes; não alterar ruas/DEM.
Palácio: refinados frontões, molduras, medalhões, relevos e portal; interrompida
a cornija diante do pavilhão central, colunas superiores sobre pedestais.
Praça: material de pedra em escala métrica, malha inalterada.
Relatório: `docs/reports/blender/torre_galerias_r30b35.json`.
Reabertura final do hash registrado confirmada; 39 amostras em cada malha
(visual/proxy) livres de solo nos interiores das galerias. Não exportar ao jogo antes de revisar a
circulação e o contrato das novas coleções/colliders. Próximos pontos reais:
terraços/jardins e colunata sob o palácio, continuidade do entorno e referências
legíveis das fachadas posteriores. Não preencher essas lacunas com decoração
inventada. O conjunto continua candidato, com esboços visíveis no panorama.
Não repetir os scripts de mutação R35: já foram aplicados; seus guards evitam
duplicação. Continuar por inspeção e alterações delimitadas na candidata.

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


## 02/10/2026 — fonte de trabalho e modelagem pela foto

**Continuar na candidata B33:** `blender/salvador_lacerda_r30b33_fachadas_foto_cairu.blend`.
Fonte/hash/origem no `blender-revisions.json`; produção permanece B30 em
`production.json`. B33 não foi exportada ao navegador. Não usar B23 ou B31
como base de novos passes nem selecionar pelo maior número/mtime.

B32 recuperou modelagem autoral B23 que o passe B31 tinha piorado:
três corpos + 38 componentes (toldo incluído), iguais à B23 após reabertura;
23 substituições B31 conservadas ocultas. Terrain/proxy continuam iguais à B30.
Relatório `facade_regression_b23_b31.json`: a recuperação local da sessão suja
B23 não diferiu no escopo selecionado; não pressupor comparação da cena inteira.

B33: três parcelas OSM explícitas `1263035780`, `1220650507`, `1220650503`.
Mesma foto `elevador-lacerda-panorama-783a31279c0d`, sem novas pesquisas.
Fachadas com vãos e componentes separados, toldo rosado e cobertura; fonte
com água e acabamento de piso conformado. Revisão visual encontrou e corrigiu
face cinza voltada para o fundo e empena aberta; rascunho preservado em
`artifacts/cidade-baixa/r30b33_before_front_refinement.blend`.
Relatório `cidade_baixa_r30b33.json` guarda alterações, reabertura e conferência
local de preservação. Alturas, associação fotográfica e acabamento candidatos;
plantas e fundações preservadas. Ruína no morro sem binding/implantação confirmados,
portanto adiada. Não inventar edifícios/fundos/interiores em vista pouco legível.

**MCP 9876** na janela adotada; não editar outra instância/porta. Entrada:
`open_registered_source.py --source-operation` pelo `run_script.py`.
Em nova sessão, `inspect_authoring_session.py --read-only --adopt-session`.
Mutações conferem PID/porta, arquivo/hash; inspeções usam `--read-only`.
Para reabrir de verdade: `--source-operation --reopen`; ler `last-open.json`
e inspecionar após timeout, sem repetir alterações já feitas.
Política: `docs/BLENDER_REVISION_POLICY.md`. Próxima revisão real deve registrar
pai/evidência e atualizar ponteiro/status/handoff; exportar apenas após promover.

Antes de substituir qualquer fachada, conferir modelagem autoral por objeto/ID.
Não arquivar trabalho melhor só porque existe novo gerador. Conferir fora do
escopo terreno/colisor e componentes recuperados. Essa preservação não aprova
geografia inteira, altura real ou testes dinâmicos de tráfego.
Sem npm/build/CI/testes gerais/commit/exportação neste passe. Ao promover para
runtime, declarar também as novas coleções `ENVIRONMENT_FINAL`/`HERO` na seleção
de exportação: os IDs numéricos antigos não incluem automaticamente as novas.

## Histórico — conexões reais, sem ruas fictícias

**Fonte ativa R30B.30:** `blender/salvador_lacerda_r30b30_conexao_real_recorte.blend`,
hash no contrato `production.json`. Preserva B29/B23. Extensão de chão/colisor
integrada às bordas existentes, 4 m ao sul, na conexão OSM `619722483` dos ways
`1075624458`/`421206045`. Sem mover vértices antigos nem alterar larguras.
`ADAPT_LOCAL`: perfil extrapolado da borda autoral, não cota real medida.
Após reabrir: 205 sondas/41 poses, nenhum chão ausente; delta máximo 9,4 mm.
Detalhes em `terrain_real_boundary_extension.json` e `terrain_real_boundary_verify.json`.

Na sessão anterior, a janela MCP 9877 estava no **artefato de teste**, não na fonte:
`artifacts/terrain-vehicle/r30b30_boundary_vehicle_test.blend`.
Carro V14 real, 195 componentes, 41 poses avaliadas/201 quadros/8,04 s;
Espaço reproduz o trecho da Praça Castro Alves. É replay cinemático de apoio,
não teste dinâmico ou aprovação da faixa/ônibus. Relatório:
`terrain_real_boundary_vehicle.json`. Antes de nova mutação/exportação,
reabrir a fonte do contrato em chamada MCP separada da inspeção.

`terrain_vehicle_replay.py` agora interpreta `direction=both/reverse`:
uma aresta física origina arcos de tráfego, não novas ruas. A auditoria ampla
do carro permanece B29; a alteração do helper não foi reaplicada globalmente.
`plan_osm_return.py` confirmou o retorno real no OSM/Aleph (871,62 m), mas
`plan_real_road_circuit.py` só admite geometria anteriormente verificada e
continua sem retorno aprovado. Não confundir ausência de retorno **verificado**
com ausência de estrada real. Os relatórios discriminam a fonte da auditoria.

Não liberar ônibus nem criar atalhos: Conceição ainda tem o conflito de níveis
abaixo e cobertura parcial de pavimento. Seções existentes têm ~2,4–2,5 m de
asfalto autoral, não largura real certificada; dimensões reais permanecem `null`.
Revisar implantação/seções/perfil com IDs e proveniência antes de alterar esse
corredor. Não escavar passagem fictícia sob a Montanha ou alargar a rua para
forçar um circuito. Runtime não atualizado; sem npm/build/CI/commit nesta etapa.

## Histórico de 01/10/2026 — R30B.29

**Atualização: fonte ativa R30B.29**, derivada da R30B.23; R30C rejeitadas.
Arquivo do contrato: `blender/salvador_lacerda_r30b29_colisao_rede_viaria.blend`.
MCP continua na única janela utilizada, porta 9877. R30B.29 refinou seis faces
adicionais do proxy nas vias cobertas, acrescentando 26 vértices. Após reabrir:
59.720 apoios com fonte, zero ausência no proxy, delta máximo 4,55 cm. Três
sondas fora do recorte não foram preenchidas. Os relatórios atuais são
`terrain_proxy_network_refinement.json` e `terrain_proxy_network_verify.json`.
Não repetir o script de mutação `terrain_proxy_refine_network.py` em revisões
novas; ele exige a R30B.28. Verificação específica: `terrain_network_verify_saved.py`.

**Conflito restante confirmado:** Conceição da Praia, `way-421206045-seg-6/7`,
perto de (-148, -150), tem descontinuidade de ~36,6 m na própria fonte visual.
Colunas mostram apenas uma superfície, não pavimento inferior já pronto.
Não criar passagem sobreposta nem recortar a Montanha arbitrariamente: revisar
perfil e limites das duas vias com proveniência. Larguras reais seguem `null`;
o fit vertical histórico é insuficiente. `terrain_remaining_profiles.json`
registra os quatro apoios e os materiais/normais dos 89 pontos com alertas.
O replay agora bloqueia torção >20 cm ou apoio ausente, preservando inclinações
como alertas a revisar. Não confundir concordância proxy–fonte com fonte correta.

O replay atual está aberto em `artifacts/terrain-vehicle/r30b29_vehicle_test.blend`
na mesma janela. Carro V14: 587 segmentos/12.069 poses; Montanha inteira do
recorte em 19 segmentos, 143,72 s, sem interrupção geométrica. Arquivo de teste
não é a fonte oficial: antes de exportar, abrir a R30B.29 indicada no contrato.
Bloqueados na rede: Conceição `way-421206045-seg-7`, bordas
`way-397449211-seg-1` e `way-531109209-seg-1`. Demais 23 alertas de torção e 71
de inclinação não foram aprovados automaticamente. Relatórios atuais:
`terrain_vehicle_audit_r30b29.json` e `terrain_vehicle_replay_r30b29.json`.
Próximo foco continua terreno/perfil da Conceição, sem tráfego/decoração.

Consulta às fontes: `terrain_conceicao_source_check.json`, com GeoTIFF original
EPSG:3857/PixelIsPoint de 4,777 m projetados, hash e tags OSM. Nenhuma largura
tagged nas duas vias; resolução maior que sua separação nesse ponto após
converter pelo fit XY. Não deformar a cidade para copiar cegamente esse DEM.
Faltam controles locais confiáveis de bordas/cotas para fechar a Conceição sem
estreitar/alargar vias ou inventar uma passagem. A inspeção usa
`tools/terrain/inspect_conceicao_source.py --capture CAMINHO_DA_CAPTURA` e não
modifica Blender. Scripts Python por arquivo evitam espera de EOF do PowerShell
ao encaminhar heredoc para `python -`; tentativas por stdin foram encerradas.

Correções aplicadas via MCP porta 9877 na janela já aberta: `terrain_junction_correct.py`
(R30B.24), `terrain_junction_finish.py` (R30B.25) e `terrain_proxy_bind_source.py`
(R30B.26), `terrain_proxy_apply_transform.py` (R30B.27) e
`terrain_proxy_refine_driveable.py` (R30B.28). Não repetir esses scripts sobre
revisões novas. Nenhuma largura ou
XY da cidade visual foi alterada; apenas Z local do encontro, depois binding
e alturas do proxy simplificado. As instruções históricas de bloqueio abaixo
não descrevem a situação atual.

R30B.25 foi reaberta e mostrou desnível transversal <3 mm nas seções auditadas
do encontro Montanha/Pau da Bandeira. O replay do carro existente completou
19 segmentos da Montanha; é cinemático, não suspensão/tráfego de runtime.
Auditoria geral: 587 segmentos, 12.069 poses. As duas falhas de apoio em
Travessa Professor Antônio Borja/Rua do Carro foram localizadas nos limites
do recorte: rodas atravessam a borda da malha existente. SOURCE_LIMITATION;
não ampliar terreno/ruas sem fonte. Definir limite de navegação antes desses
finais de percurso; não são buracos internos a preencher. Demais alertas de
inclinação/não coplanaridade seguem para revisão, sem nivelamento automático.
Não promover a cidade inteira como pronta. Resultado em relatórios
`terrain_vehicle_*r30b25.json`. Artefato de teste `artifacts/terrain-vehicle/r30b25_vehicle_test.blend`.

O proxy antigo estava em coordenadas locais, enquanto o terreno tinha world
transform; seus limites locais foram conferidos, não foi inventado offset.
Depois do binding, 37.861 alturas do proxy foram atualizadas sobre a fonte;
zero suporte ausente com tolerância de borda de 2 mm (overshoot original <1,77 mm).
O máximo delta de resampling (~51,52 m) mostra que o proxy era obsoleto também
na encosta; não equivale a terreno visual movido. R30B.26 mostrou world matrix
stale no objeto oculto após reabrir; R30B.27 aplicou a matrix basis registrada
aos vértices e deixou transforms em identidade. R30B.28 refinou localmente
32 faces inicialmente divergentes, adicionando apenas 122 vértices ao proxy.
Após reabrir: 1.428 amostras, zero apoio ausente, diferença visual–colisão
máxima 3,87 cm na Montanha/Pau da Bandeira. `terrain_proxy_verify.json` aprovado
somente para suporte geométrico desse percurso, não para dinâmica/gameplay.

Sem nova exportação de runtime, npm/build, commit ou teste jogável de cinco minutos.
Evitar `bpy.ops.render.opengl`: travou sessões anteriores. Posicionar viewport
na janela e usar medições/inspeção segura enquanto captura não estiver disponível.

Continuação do encontro Montanha/Pau da Bandeira: os perfis em
`artifacts/terrain-vehicle/junction-profiles.json` confirmam até ~0,93 m entre
as duas superfícies no encontro. A faixa de `RELEVO | contenção entre vias`
atravessa o eixo em uma seção. Não confundir falha do filtro de material de
asfalto com ausência real de suporte: o replay foi preparado para verificar
quatro apoios no terreno completo, mantendo as vias como seleção do percurso.

`automation/blender/terrain_junction_correct.py` está preparado, **não aplicado**:
altera apenas Z do pavimento existente num encontro de três eixos e sincroniza
localmente o proxy; preserva XY, materiais e topologia. Revisão R30B.24 ainda
não existe nem foi promovida. Não declarar a correção concluída pelo script.

A sessão porta 9876/PID 28348 travou na captura OpenGL. Uma sessão já aberta
porta 9877/PID 32900, com R30B.23, respondeu ao healthcheck e às medições, mas
também travou na captura; ambas as chamadas terminaram por timeout. Não abrir
terceira janela nem usar background para contornar. Foi pedido ao usuário
cancelar/recuperar e manter uma única janela. Não houve mutação de terreno.
Próximo passo: recuperar MCP, aplicar correção, repetir auditoria/replay sobre
a revisão salva, conferir visualmente por captura que não use o operador
OpenGL que travou. Não repetir `terrain_junction_inspect.py` com render OpenGL.

Análise veicular executada sobre a R30B.23 via MCP: ler os relatórios
`docs/reports/blender/terrain_vehicle_audit_r30b23.json` e
`docs/reports/blender/terrain_vehicle_replay.json`. Scripts:
`terrain_vehicle_audit_r30b23.py`, `terrain_vehicle_replay.py` e
`terrain_vehicle_visual.py`. Não executar o append do carro repetidamente.
O teste foi salvo separadamente em `artifacts/terrain-vehicle/r30b23_vehicle_test.blend`;
a composição autoral e o contrato continuam R30B.23. A janela pode mostrar a
cópia de teste, portanto reabrir a fonte do contrato antes de mutar geometria.

Sweep de quatro rodas: 578 segmentos/11.255 poses; não é dinâmica física.
Replay conectado: 17 segmentos da Montanha; encontro do segmento
`way-48846625-seg-9` bloqueia o percurso completo, com diferença transversal
até ~0,92 m. Também há alertas na Chile/Ajuda. Registrar e investigar os
encontros de via e o perfil antes de qualquer alteração Z; preservar XY/largura.
Os segmentos OSM sem chão fora do recorte não autorizam criar nova cidade.

O usuário corrigiu explicitamente a fonte: usar
`blender/salvador_lacerda_r30b23_fachada_praca.blend` (**R30B.23**), preservando
o refinamento do Elevador e entorno. A seleção anterior R30C.5 partiu de base
antiga e foi rejeitada. Não importar terrenos/partições da R30C na R30B.23.
O relatório `terrain_source_selection.json` registra a abertura e o hash; a
troca da fonte não implica exportação do runtime nem correção de geometria.

Diretriz mais recente: não aumentar/diminuir larguras, conservar os limites XY
autorais e regularizar apenas a superfície viária. Larguras reais não confirmadas
continuam incertas. Percursos devem derivar das vias existentes; adiar calçadas.
As notas R30C abaixo são histórico rejeitado, não instrução para continuar.

O usuário restringiu esta etapa à malha/chão e solicitou pesquisa de padrões
de terrenos em jogos. Ler `docs/TERRAIN_GAMEPLAY_RESEARCH.md`. Terreno não deve
ser globalmente plano: conservar ladeiras e patamares, corrigir continuidade.

Fonte ativa declarada no contrato: R30C.5. Foram corrigidas sobreposições do
corredor de teste e o uso de transform ainda não atualizado após carregar um
objeto de biblioteca. R30C.4 é intermediária incorreta; não usar como base.
Scripts de modelagem via MCP: `urban_terrain_partition.py` (sobre R30C.2) e
`urban_terrain_grade.py`; não executar novamente indiscriminadamente. As
revisões preservadas são checkpoints, não fontes concorrentes do runtime.

O corredor possui pista/passeio separados, suporte próprio e adaptação local
documentada. O entorno exterior ainda requer inspeção. Tráfego fica pausado
enquanto `urban_slice.json` tiver `status=terrain_review`. A integração anterior
de carros/NPCs é candidata, não um teste jogável aprovado. Não declarar cinco
minutos de estabilidade: esse fluxo ainda não foi verificado. Browser MCP
retornou timeouts de CDP; usar novamente quando disponível, sem fabricar prova.

Sem npm/build/CI nesta sessão. Validações obrigatórias Python passaram
(62 testes; registro sem erros, dois avisos). Não houve commit/push nesta etapa.

> Elevador Lacerda: revisão visual **parcial R30B.22** em
> `blender/salvador_lacerda_r30b22_exterior_vidros.blend`. O apoio permanece na
> posição original; R30B.14 foi rejeitada por deslocá-lo. Ver
> `docs/revisions/R30B22_LACERDA_EXTERIOR.md` para alterações e pendências.
> Incluir entorno imediato: calçada, comércio confirmado e guarda-corpos da praça, reaproveitando referências catalogadas.
> Prioridade atual: exterior, fachadas e ligação dos acessos à praça/calçada; adiar microdetalhes internos.
> A fonte ativa em `production.json` permanece R30A.11; não houve exportação.

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
