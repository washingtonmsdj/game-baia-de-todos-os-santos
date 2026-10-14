# Orla Cairu–Lacerda — revisão de fidelidade

## 05/10/2026 — B72/B73: continuidade das vias e tangente local da encosta

Candidata ativa de validação: `blender/salvador_lacerda_r30b73_tangente_encosta_costura.blend`, SHA-256 `d49f9b35e00b292acdbd33028b58f8eaa52d71e9ba9fd232ba679190227e1f0b`. B71 e B72 preservadas. Ambas as revisões foram salvas/reabertas na mesma janela MCP. Autoria B41 e produção B30 permanecem separadas.

Os oito eixos conferidos coincidem exatamente com a referência OSM armazenada, pelos mesmos IDs. Isso não certifica o georreferenciamento da cidade: o fit permanece candidato. B72 continuou o pavimento nas superfícies existentes e recompôs a junção OSM 4527284526 entre Manoel Vitórino/Conceição: 1.286 vértices, delta Z máximo 0,5672 m. Inclinação transversal máxima: Manoel 12,97% → 3,77%; Conceição 6,92% → 3,77%. Longitudinal: Manoel 22,98% → 16,15%; Conceição 14,43% → 16,20% (tradeoff explícito). Os oito eixos e apoios laterais a ±0,825 m têm chão nas amostras a cada até 0,5 m; isso é leitura geométrica, não teste físico do veículo. Materiais contínuos nos eixos; o nó compartilhado da Manoel usa o pavimento de pedra da Conceição.

B73 modifica 2.359 vértices de terreno não viário numa faixa de transição de 8 m; escolha local de modelagem, não dimensão levantada. Preserva XY, topologia, extremos, vias/calçadas bloqueadas, núcleo, piso/cais, píeres e água; delta Z máximo 3,9890 m. Diferença de inclinação entre os lados, medida em segmentos de 1 m: P95 3,7581 → 0,3600. Diferença de cotas em pontos a ±0,01 m da borda: máxima 0,07884 → 0,00980 m. Valores de vários metros medidos em pontos separados por 2 m incluíam a própria descida da encosta; não eram um degrau medido no mesmo XY.

**Não concluído:** bordas serrilhadas do pavimento, acabamento da expansão, georreferenciamento/altimetria absolutos, larguras reais, 94 triângulos degenerados preexistentes no núcleo e travessia física na engine. A captura original Aleph ainda está ausente; não inventar sua altitude nem promover o fit por reduzir uma métrica. A cena continua parcial e não aprovada para produção/AAA.

Evidências: `docs/reports/blender/city_seam_r30b72{,_validation}.json`, `terrain_tangent_r30b73{,_validation}.json` e `terrain_tangent_b73_candidate.json`. Ledger preserva as 716 detecções existentes e registra os dois ciclos. Limpeza recuperável de caches/autosaves registrada em `storage_cleanup_b72_*.json` e `storage_cleanup_b73_browser_cache.json`; instalações e revisões oficiais preservadas.

Nova solicitação de 05/10: expandir até Dique do Tororó, Arena Fonte Nova e Center Lapa, adquirindo fontes reais, verificando anchors/overlap e só depois integrar terreno/vias e revisão cinemática com a Rondesp/câmera do motorista. Sem npm/build/suíte de testes.

## 04/10/2026 — B71: encontro norte corrigido; acesso privado nas vias revisadas

Fonte candidata salva/reaberta pelo MCP na mesma janela: `blender/salvador_lacerda_r30b71_encontro_norte_cais.blend`, SHA-256 `b851703b3e47571469f30bd5c32c1e0fe01fa7e476f2776976e7b222dd4ed989`. B70 preservada; autoria B41/produção B30 mantidas. O canto do piso coincidia em XY com o núcleo, mas estava 1,8006 m acima; corrigido o vínculo ao vértice real da cena. Topo do cais e piso recompostos localmente até esse apoio: 12 vértices do cais alterados, 380 do piso acima de 0,00001 m; transição de 12 m é escolha candidata de modelagem, não dimensão real levantada. Núcleo, HQ, vias, píeres, água, XY e topologia preservados; visual/colisão iguais após reabrir.

Piso: dois → zero triângulos acima de 200%; inclinação máxima 259,49% → 63,85%, P95 23,35% → 21,82%; nenhum vértice abaixo do mar nominal. Máximo desencontro Z nos 23 vínculos norte: 0,0000003813 m (precisão numérica), canto a 0,0000305 m do controle. Zero triângulos degenerados/arestas com mais de duas faces. As superfícies abertas de piso e contenção não são volumes estanques; estes números não certificam caminhabilidade ou altimetria real.

Revisão das quatro vias: OSM 1004133492/3493 são acessos privados e 1004133494 é corredor privado de estacionamento; 778284292 é via de serviço com acesso pendente. 757 amostras dos eixos dentro da região, a cada até 1 m, com chão presente; isso não prova largura, conexão completa, material correto ou passagem das quatro rodas. Não usar esses acessos privados automaticamente como trajetos de ônibus. Larguras reais null.

Evidências: `docs/reports/blender/north_junction_r30b71.json`, `north_junction_r30b71_validation.json`, `coastal_service_roads_b71_review.json` no mesmo diretório; vista `artifacts/waterfront/b71-encontro-norte.png`. Próximo: perfis/encontros viários e encosta, com controles existentes e classificação explícita; acabamento regional/níveis absolutos/fonte Aleph original seguem pendentes. Sem aprovação integral ou exportação runtime.


## 04/10/2026 — B70: junção terreno–piso–cais recomposta localmente

Candidata salva/reaberta pelo MCP na única janela PID 22916/porta 9876: `blender/salvador_lacerda_r30b70_juncao_terreno_cais.blend`, SHA-256 `2838e38a4347cd307d6e25eddf152fd38d7bde40747b4adb7c672a5e75093c64`. B69 preservada; autoria B41/produção B30 mantidas. Corrigido o vínculo de alturas por arestas físicas entre B62/B63; adaptação local aos controles do cais existente, sem levantamento altimétrico. Piso: 126 → 2 triângulos acima de 200% de inclinação; 19 → 0 vértices abaixo do mar nominal. Conferência reaberta: 206 contatos com diferença Z zero, visual/colisão iguais, zero triângulos degenerados, XY/topologia preservados e 16.240 vértices de vias/passeios fixos. As superfícies de terreno permanecem abertas intencionalmente.

A faixa de contato de 2 m e transição até 30 m são escolhas de modelagem candidatas, não larguras reais medidas; maior alteração local Z: 7,5900 m. Altimetria absoluta continua não verificada. Restam dois triângulos no extremo norte (controles 7,2557 versus ~9,0563 m), transição diagonal, acabamento urbano/encosta e conexões viárias. Não aprovado para circulação integral nem promovido ao runtime. Originais Aleph ainda ausentes no caminho registrado.

Evidências: `docs/reports/blender/coastal_junction_r30b70.json`, `docs/reports/blender/coastal_junction_r30b70_validation.json` e `artifacts/waterfront/b70-juncao-cais.png`. Próximo passe: revisar o conflito local norte com controles verticais confiáveis e inspecionar conexões viárias OSM 778284292/1004133492/3493/3494, sem inventar larguras.


O erro de contato foi classificado ERROR: estimar altura por raios tangentes à borda não reproduzia a aresta física. O nivelamento local foi classificado ADAPT_LOCAL: utiliza cotas da cena atual, não altera o DEM-fonte e não certifica fidelidade altimétrica. Foram recompostas somente B62 visual/colisão e B63 piso visual/colisão, mantendo nomes e IDs. Cais, água, núcleo histórico, píeres, canteiros, meios-fios e navegação protegidos mantiveram suas assinaturas.

No piso, P95 de inclinação: 142,87% → 23,35%; máximo: 2541,82% → 259,49% nos dois triângulos de borda ainda pendentes. Na faixa HQ examinada, máximo: 83,22% → 78,89%, mas P95: 26,23% → 36,29%; portanto não interpretar a melhoria do piso como aprovação da caminhabilidade de toda a faixa adjacente. A inspeção visual continua parcial e mostra transição diagonal/acabamento e vias incompletos. Gameplay, personagem, quatro rodas, tráfego e câmera não foram aprovados por estas verificações.


## 04/10/2026 — B69: encontros dos píeres corrigidos; região ainda incompleta

Candidata explícita: `blender/salvador_lacerda_r30b69_encontros_sem_frestas.blend`, SHA-256 `30d079046f029b559ffce28d1254bc65a6a3f57f0625245b809deb9c7ad7bfa2`. B67/B68 preservadas; autoria B41 e produção B30 inalteradas. MCP na única janela PID 22916/porta 9876; fonte salva, reaberta e conferida.

B68 criou dois preenchimentos terrestres, mas a sondagem posterior encontrou 24/21 lacunas nos encontros. B69 substituiu apenas suas malhas por recortes obtidos pela subtração XY do chão e da água existentes, com triangulação em coordenadas locais. Áreas planas: 4,0730 e 3,2009 m². Na conferência reaberta: 16.000 sondagens, zero apoio terrestre ausente no recorte examinado; sólidos com zero arestas/vértices não manifold, zero triângulos degenerados e colisão igual. As 24 assinaturas protegidas permaneceram iguais. Isso não aprova toda a costa nem acessibilidade.

Diferenças máximas deck/piso: 1,4774 m (609043799) e 0,0477 m (609043801). Alturas reais, fundações e maré continuam null/pending. Nível nominal 0,35 preservado; base dos volumes é domínio candidato, não fundação levantada. Área de sobreposição usa projeção XY/centroides, não a área inclinada 3D nem uma prova integral de interseção.

A imagem regional foi obtida novamente: `artifacts/waterfront/b69-regiao-pendente.png`. **O relevo, acabamento urbano, junções das vias e relação vertical terra/água continuam insatisfatórios.** O piso B63 tem 126 triângulos acima de 200% de inclinação e 19 vértices de fronteira abaixo do mar nominal. Um ensaio de alisamento interno com borda fixa piorou a malha e foi rejeitado sem aplicação. Não mascarar a causa com suavização/global Z.

Triagem regional OSM: 620 amostras de eixo a cada ≤10 m; 614 com material de via e seis com chão sem material viário. Isso NÃO demonstra conexão correta, largura, perfil, quatro rodas ou veículos. Os alertas de material abrangem IDs 778284292, 1004133492/3493/3494 e requerem inspeção; não alargar nem mover eixos automaticamente.

Originais Aleph `map.osm`/`terrain.tif` não estão disponíveis no caminho registrado do projeto auxiliar; busca limitada ao diretório Tom Oliver também não os encontrou. Referência estrutural derivada e demais derivados permanecem disponíveis. Não substituir fonte silenciosamente nem apresentar alturas candidatas como reais. Próximo passe: recuperar/provar fontes e corrigir a junção B62–B63–cais, depois perfis/conexões das vias e relevo local.

Evidências: `docs/reports/blender/pier_land_contacts_r30b69.json`, `pier_land_contacts_r30b69_validation.json`, `coastal_region_source_coverage_b69.json`, `coastal_region_b68_inventory.json` e `coastal_floor_fairing_b69_probe.json` (últimos quatro no mesmo diretório). Pendências preservadas no ledger; sem npm, build, instalação, suíte geral ou exportação runtime.

## 04/10/2026 — B67: píeres reais e domínio da água

Candidata de validação: `blender/salvador_lacerda_r30b67_pieres_e_dominio_oceanico.blend`, SHA-256 `e0fcda84e28adaf3161da7458195471511b00c2ef9e70fd42f6edc555188b412`. B66 preservada; autoria B41 e produção B30 continuam separadas. Aplicação MCP na única janela PID 22916/porta 9876, seguida de reabertura e conferência local.

Uma consulta oficial nova ao OSM foi preservada em `artifacts/waterfront/osm_coastal_check_20261004.osm.gz`, sem substituir silenciosamente a captura anterior. Seis controles de mesmas features confirmaram reutilização local da transformação XY. Dois contornos fechados ausentes, OSM 609043799 e 609043801, receberam decks visuais, referência e superfícies candidatas separadas de colisão. Contornos XY mantidos dentro de 0,0001 m de tolerância numérica da mesh; isso não certifica a precisão absoluta da fonte.

Alturas dos novos decks: 2,9742 e 4,5861 unidades Blender, derivadas do piso da cena, classificadas ADAPT_LOCAL/candidate. Não são levantamento real. Ligação à margem, fundações, guarda-corpos e maré permanecem pendentes; o primeiro ponto de margem tem variação de 2,4814 unidades e exige revisão antes de criar acesso. Eixos adicionais 1321555661/1321717133, quebra-mar 217677378 e passarela 1426173324 permanecem somente referências ocultas, com largura/altura reais null.

O volume de água foi reconstruído a partir do contorno da superfície atual, fechado e com normais coerentes. Espuma costeira derivada do mesmo limite, excluindo três bordas artificiais do recorte. Nível 0,35 preservado; fundo -16 é domínio de gameplay legado, não batimetria. Nos decks antigos há bordo livre candidato de 6,9057 unidades, portanto o encaixe vertical absoluto água–cais–píeres ainda não está aprovado. Não elevar o mar nem aplicar escala/offset Z global para ocultar isso.

Conferência após reabertura: volume fechado com zero arestas não manifold e zero triângulos degenerados; dois decks sólidos fechados, referências/superfícies sem degeneração, colisão igual e espuma coerente com a costa atual. Terrenos, água visual, cais, píeres anteriores e larguras de ruas preservados no passe. Sem exportação runtime ou aprovação global de cidade, tráfego, personagem/veículo.

Evidências: `docs/reports/blender/coastal_osm_source_check.json`, `pier_land_contacts_b67_probe.json`, `waterfront_piers_r30b67.json` e `waterfront_piers_r30b67_validation.json` (estes três em `docs/reports/blender/`). No Blender ficam domínio/nível e prévia da água; renderização dinâmica, ondas, consultas de altura e flutuação exigem implementação na engine. A engine definitiva segue em aberto; o protótipo Three.js usa nível nominal 0,35.

Limpeza autorizada adicional: perfis temporários inativos, três pacotes runtime antigos fora do ponteiro ativo, cache de downloads pip antigo e três autosaves temporários B56/B57/B62 substituídos. Fontes oficiais, bibliotecas instaladas, pacote ativo e recoveries manuais preservados. Relatórios de limpeza guardam escopo e hashes. A falta recorrente de espaço ainda limita novas revisões. Sem npm, build, instalação ou suíte geral.


Limpeza adicional por disco cheio: cinco experimentos R30C rejeitados foram removidos (274.731.641 bytes), com hashes e estado local registrados. Um perfil temporário R30A10 sem processo ativo também foi removido. Fontes B30/B41/B66, revisões oficiais e recoveries preservados.

## Referências reais e limites

Foram catalogadas e inspecionadas três fotografias, com hash, autoria e licença CC BY-SA 4.0. O acervo binário permanece fora do Git; os registros estão em `world/areas/mvp-centro-lacerda/media-manifest.json`, como `REFERENCIA_INTERNA`.

| Registro | Data/autor | Uso verificado |
|---|---|---|
| `mercado-modelo-roof-c81220c814b5` | 06/08/2022, Túllio F | Mercado, contorno do cais, píeres estreitos da marina e Forte São Marcelo separado da costa pela água |
| `cais-praca-cairu-waterfront-context-e8ff600587df` | 21/09/2024, Sturm | Terminal, muro do cais, estacionamento, passeio e guarda-corpo |
| `cais-praca-cairu-street-context-6f026986b483` | 21/09/2024, Sturm | Terminal e Arena da Capoeira vistos da praça; não mostra o contorno dos píeres |

Fontes: [vista elevada de 2022](https://commons.wikimedia.org/wiki/File:Mercado_Modelo_-_Salvador_-_20220806152921.JPG), [terminal e cais em 2024](https://commons.wikimedia.org/wiki/File:Salvador_-_BA_(Sep_2024)_0371.jpg), [vista da praça em 2024](https://commons.wikimedia.org/wiki/File:Salvador_-_BA_(Sep_2024)_0575.jpg).

As fotografias confirmam relações espaciais e tipos de estrutura. Não fornecem alturas, fundações, largura de ruas ou largura da passarela em metros. A época final da representação permanece pendente; imagens de 2022/2024 não comprovam operação turística atual. Não usar estruturas antigas da cena como referência real apenas porque já foram modeladas.

## Correções aplicadas via MCP

B63 acrescentou bordas nos limites existentes entre pista e passeio, oito canteiros mantidos após revisão e piso na lacuna junto ao cais. O fragmento OSM `565958078`, com cobertura insuficiente, foi ocultado/excluído como colisão de runtime. Meios-fios e canteiros têm dimensões de desenho candidatas; não foram medidos em campo.

B64 recortou o terreno pelo limite da água preservada: 59.453 faces marítimas removidas do núcleo e 59 do piso novo. As 266.281 faces de pavimento e seus vértices permaneceram preservados. A água, o DEM, a expansão HQ e os píeres mantiveram suas assinaturas. A contenção conserva o objeto legado e acompanha o limite da costa e o apoio atual do piso.

B65 corrigiu resíduos da triangulação e soldou vértices repetidos do piso novo e da face visível do cais. Não altera a largura das ruas. Piso e face do cais são superfícies abertas intencionais; não há espessura/fundação real certificada. A colisão derivada acompanha a geometria visual e permanece candidata, sem exportação de runtime.

A conferência da B65 reaberta encontrou 678 faces do cais voltadas para o lado terrestre e quatro resíduos numéricos do piso (área total 0,000058 unidades Blender²). B66 orientou essas faces para a água e removeu os resíduos; sem deslocar a costa, os terrenos principais, o pavimento ou os píeres.

Fontes anteriores B62/B63/B64/B65 preservadas; autoria B41 e produção B30 permanecem separadas. Revisão de validação atual B66: `blender/salvador_lacerda_r30b66_cais_normais_corrigidas.blend`. A auditoria completa da cidade e a física de veículos não estão concluídas.

Conferência B66 após reabertura: 11 malhas visíveis novas/alteradas com zero triângulos degenerados e colisão igual; piso novo com zero centroides sobre água; cais com zero faces voltadas para o lado errado. Meios-fios e oito canteiros mantidos com zero arestas não manifold. Piso/cais são superfícies abertas intencionais, ainda sem volume/fundação real certificados. Isso não aprova a passarela nem todo o mapa.

## Acesso náutico e pendências estruturais

Os píeres fechados OSM `1426173139` e `1426173140` conservam seus footprints. Na B64, os caminhos `1426173138`, `1426173325` e `1426173326` têm apoio ao longo das amostras de eixo. Isso não certifica toda a largura, guarda-corpos, maré ou embarque.

A passarela `1426173327` é explicitamente `bridge=yes`, `highway=footway`, `layer=1`. Sua ligação de aproximadamente 12 unidades Blender tem 11 amostras sem piso. A largura real não está na fonte. Manter o eixo como controle e obter contorno/documentação suficiente antes de apresentar uma reconstrução como fiel. Não preencher o mar como terreno para encobrir essa lacuna.

O Forte São Marcelo deve conservar sua separação marítima. O acesso de gameplay será náutico, com embarque no cais e desembarque no forte. Não criar conexão rodoviária fictícia. O ponto exato de embarque, o desembarque no forte, os níveis de plataforma/maré e a operação representada ainda precisam de evidência.

A altimetria absoluta do cais, a arquitetura do terminal, a configuração temporal da fonte/monumentos e o conjunto Cairu–Mercado–acesso inferior do Lacerda permanecem em revisão. Não declarar região perfeita, AAA, nem todos os percursos aprovados.

## Regra para expansão e novas correções

1. Usar fonte/transformação registradas e OSM IDs explícitos; fonte ausente permanece `SOURCE_LIMITATION`.
2. Conferir o lado terrestre da coastline antes de gerar piso; detectar faces sobre água e sobreposição entre terrenos.
3. Usar fotografias catalogadas para classificar praça pavimentada, jardim, cais e píer. `leisure=park` sozinho não significa gramado.
4. Preservar eixos e pavimento até haver causa comprovada para alteração; largura sem evidência real permanece `null`.
5. Separar fonte, geometria final, colisão e navegação. Caminho com nós apoiados não prova continuidade entre nós.
6. Registrar mudanças no ledger e nas revisões, salvar e conferir reabertura na mesma janela. Verificar interfaces, triangulação e parceiros de colisão.
7. Promoção de autoria/runtime exige seus gates próprios. Os checks deste passe são locais; não substituem percursos completos, personagem, quatro rodas, ônibus e tráfego.

Relatórios: `urban_edges_r30b63.json`, `coastal_volumes_r30b64.json`, `coast_reference_b64_inspection.json`, `coastal_floor_r30b65.json`, `coastal_floor_r30b65_validation.json` `coastal_orientation_r30b66.json`, `coastal_floor_r30b66_validation.json` e `waterfront_real_reference_review.json`, em `docs/reports/blender/`.

## Espaço e recuperação

A falta de espaço interrompeu uma gravação de metadados. O manifesto foi recuperado: 35 registros anteriores preservados e três novos registros com hashes conferidos. Foram removidos exports NPZ regeneráveis de B62, quatro cenas derivadas antigas de testes de veículo e perfis temporários de inspeção de navegador sem processo ativo. Revisões oficiais e cópias de recuperação foram preservadas.

Antes de nova revisão, conferir espaço e preservar os metadados anteriores. Usar arquivo temporário completo e conferir o conteúdo antes de substituir catálogos; em sistemas que bloqueiem rename, manter a cópia anterior e conferir a gravação alternativa. Nunca sobrescrever um manifesto sem recuperação quando o disco estiver cheio.
