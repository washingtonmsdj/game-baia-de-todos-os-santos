# Issue #22 — evidência independente do Lacerda reconciliada com B80

## Decisão

**`NO_SCENE_CHANGE`.** Pesquisa executada na branch `research/lacerda-evidence-2026-10-06`, seguindo o roteiro desta branch e a [issue #22](https://github.com/washingtonmsdj/game-baia-de-todos-os-santos/issues/22). Nenhuma correção geométrica específica está autorizada nesta rodada. B81 não criada; movimento continua bloqueado; nenhuma exportação para produção.

A pesquisa avançou de textos históricos e vistas externas para **12 pranchas oficiais R00 do projeto executivo de 2023**, além do memorial justificativo e caderno de especificações. Isso permite uma comparação arquitetônica independente. Ainda não permite determinar qual contorno de laje deve ser corrigido na B80: falta registro dos desenhos no SSOT e confirmação da cabine/poço/soleiras no estado executado. A cabine candidata não foi usada como gabarito de recorte.

## Reconciliação local e preservação

O relatório local canônico `docs/LACERDA_CORRIDOR_B80.md` e suas auditorias foram usados diretamente, sem reconstrução a partir da conversa ou substituição pela pesquisa remota. A branch remota continha o roteiro e a pesquisa preliminar; a B80 já existente no workspace permanece a base geométrica.

`docs/reports/research/lacerda-issue22/reconciliation.json` registra SHA-256 verificado das revisões B76, B77B, B78, B79 e B80, do SSOT e dos relatórios canônicos. B80 mantém hash `2dc973c3efc4710cf268b348d4892fc17df0c2ac2ecef0e2e45d0493c249e4c4`. O total de 6.294 objetos vem da validação salva/reaberta B80; não foi anunciado como nova contagem exportada nesta pesquisa. Produção B30 e autoria B41 permanecem sem promoção.

Alterações anteriores e arquivos não rastreados do workspace foram preservados. Não houve commit/push nesta rodada: a reconciliação identifica os artefatos locais necessários antes de publicar um pacote que dependa da B80.

## Fontes recuperadas e tentativas

| Fonte | Recuperação e classe | Limite |
|---|---|---|
| Concorrência SUCOP 24/2023, processo 182358/2023 | Edital integral, 44 páginas; `OFFICIAL_TEXT`. Link do próprio edital levou ao anexo técnico público | Edital administrativo não mede cabine |
| Projeto executivo A+P, arquitetura 2301 R00 | Pranchas 03, 04, 08, 12, 13, 17, 21, 22, 23, 24, 31 e 34; `OFFICIAL_DRAWING`. Todas renderizadas e inspecionadas | Conjunto selecionado, não projeto completo nem as-built |
| Memorial justificativo e caderno de especificações | 36 e 11 páginas; `OFFICIAL_TEXT`. Memorial datado setembro/2023, Fase A, Produto 4; autoria identificada | Não contém plano de montagem cotado da cabine atual |
| Artigo técnico SBQP 2025, Nivaldo Vieira de Andrade Junior | 17 páginas; `ACADEMIC_SECONDARY`; fotos pós-restauro e discussão da intervenção | Autor participou do projeto; imagens não são levantamento métrico independente |
| IPHAN 01502.000406/2001-93 / 1497-T-02 | Tentativa do volume do parecer redirecionou para página inicial; índice e busca recuperados. Registros 9697/9698 apontam para imagens F105611/F105612 e versos no visualizador; HTML preservado | Não demonstrada ligação desses registros ao processo solicitado. Anexos gráficos e plantas da reforma de 2002 **não recuperados** |
| UFBA, item ri/24863, figuras 122–124 | Endpoint original falhou na verificação TLS Python; tentativas com TLS normal do Windows em ambos os namespaces retornaram 404 | Figuras **não inspecionadas**; não tratar como pranchas recuperadas |
| Otis, modernização anunciada em 2023 | Comunicado oficial consultado no navegador; tentativa de cópia local retornou 403 | Confirma modernização, mas não fornece W/D/H, montagem, soleiras ou folgas |
| Levantamento cadastral atual e as-built 2023–2025 | Memorial menciona levantamentos anteriores; pacote público inventariado parcialmente | Levantamento cotado específico da cabine/poço atual **não localizado** |

Origem primária do pacote: [edital SUCOP](https://sucop.salvador.ba.gov.br/wp-content/uploads/2023/10/EDITAL-CONCORRENCIA-No-24-2023.pdf), com [anexos públicos](https://drive.google.com/drive/folders/1gayuTpUYkNcUjoGd5CxWlj58MuWDI1Ju). Autoria das pranchas: Alexandre Prisco Paraíso Barreto, CAU A33292-5, A+P Arquitetos Associados; colaboradores Gabriela Otremba / Lucas Paes. Não confundir a autoria com escritórios homônimos encontrados em buscas.

O [artigo SBQP](https://eventos.antac.org.br/index.php/sbqp/article/download/8233/6115) e o memorial ajudam a distinguir reformas históricas, remoção de forros e instalações suspensas. O [comunicado Otis](https://otisinvestors.com/news/news-details/2023/Otis-selected-to-modernize-Elevador-Lacerda/default.aspx) não é desenho de montagem nem comprovação dimensional do equipamento instalado.

URLs, arquivos brutos, hashes, autoria, datas e pranchas estão em `source_summary.json` e no catálogo central `world/data-provenance.json`. Binários permanecem em `world-reference/mvp-centro-lacerda/research-20261006-issue22/`, fora do Git e do release. Disponibilização pública não equivale a licença de redistribuição; todos os novos recursos são `DEV_REFERENCE_ONLY`, sem objetos derivados. Falhas e respostas HTML estão separadas dos PDFs válidos nos relatórios de aquisição.

## O que a nova evidência comprova

As cotas **impressas** do projeto situam acesso superior em 0,00, cobertura da passarela em +4,00, cobertura inferior em −53,17 e acesso inferior em −58,93 m. São valores do datum local do projeto, não altitude absoluta do SSOT nem medição as-built. Não foram obtidos medindo pixels.

As plantas superiores distinguem circulação de entrada, saída e acesso à torre. A representação hachurada da torre é esquemática: não deve virar uma suposta planta interna das cabines. Os cortes mostram a relação vertical torre/acessos e a distinção entre lajes, instalações suspensas e grelhas. A cota de 3,07 m do corte DD se refere ao ambiente do acesso superior até a grelha, não à altura da cabine. Pranchas 22 e 24 têm conflito entre escala 1:50 do carimbo e 1:100 das legendas; nenhuma dimensão foi extrapolada dessas escalas.

O memorial, pp. 5 e 10–16, separa intervenção de 2001–2002 da proposta de 2023: forros antigos e cobertura de vidro inferior não devem ser confundidos com laje permanente ou estado atual. As fotos de 2025 apoiam essa separação, sem provar dimensões ocultas. Não foram inventados contrapesos ou instalações internas.

### Diagnóstico vertical

| Controle | Valor | Classe |
|---|---:|---|
| Deslocamento candidato B80 | 62,70900011062622 unidades de cena | `SCENE_CANDIDATE` |
| Percurso histórico citado no baseline | 59 m | Histórico, somente diagnóstico |
| Diferença de cotas de acesso no projeto 2023 | 58,93 m | `OFFICIAL_DRAWING`, datum local |
| B80 menos histórico, se unidade for metro | +3,70900011062622 | `NEEDS_REVIEW` |
| B80 menos projeto, se unidade for metro | +3,77900011062622 | `NEEDS_REVIEW` |

Essas diferenças não demonstram sozinhas se o erro está no desembarque candidato, transform do asset, datum, correspondência do acesso ou trajetória. Não autorizam reescala Z, offset global, mudança do terreno ou deslocamento de Hero. O SSOT permanece único e intacto.

## Triagem das 27 testemunhas

`witness_triage.json` contém **uma entrada rastreável para cada uma das 27 testemunhas**: componente, obstáculo, parâmetro da viagem, Z candidato, intervalo de contato superficial do par, bounds da mesh, fonte/hash B80, documentos relevantes, classificação e correção autorizada.

As ocorrências pertencem a **três grupos de obstáculos**, não a 27 defeitos arquitetônicos independentes: plataforma superior (13), cobertura inferior (13) e plataforma inferior (1). A classificação geométrica original `ERROR` continua válida para o vértice estritamente dentro do sólido convexo exportado. A atribuição de uma **correção arquitetônica independente** fica `NEEDS_REVIEW`: a prancha não foi registrada por controles no SSOT, e o nome de uma mesh não prova correspondência com o elemento desenhado. Não se sabe ainda se uma ocorrência exige corrigir arquitetura, posição/envelope candidato da cabine ou ambos.

O intervalo `t_first`–`t_last` é o intervalo agregado de contato superficial do par; **não se afirma que todo esse intervalo tenha penetração sólida**. Outros 27 pares com contato superficial sem testemunha sólida continuam separados de erros comprovados. Nenhuma tangência virou erro por conveniência, e nenhuma testemunha foi apagada para liberar o gate.

**Correções geométricas autorizadas: nenhuma.** Continuidade esquemática do poço é uma evidência útil de topologia, mas não fornece o contorno registrado que autorizaria um boolean em uma plataforma B80. Próximo passo é registrar plantas/cortes com controles físicos independentes e obter desenho de instalação ou levantamento cabine–poço–soleiras.

## B78, apoio e Aleph

As sete alterações B78 continuam comparadas pelo relatório canônico: dois retornos posteriores, dois lambris, dois rodapés e uma verga. As plantas novas sustentam a organização geral do acesso; não comprovam as sete edições ou suas posições. Todas as migrações permanecem `NEEDS_REVIEW`, sem merge. Elas também não corrigiriam os três obstáculos do CCD.

Piso/collider/ground-following B80 preservados: zero trechos superiores com penetração, 18 apoios ainda dependentes de solver e nove trechos inferiores com penetração. A pesquisa não equivale a gravidade, step, slide ou controller real. Como nenhuma geometria/trajetória mudou, **não se repetiu o CCD para simular uma nova validação**: os relatórios existentes foram reconciliados por hash e continuam bloqueados.

Aleph/OSM/DEM e consultas Street View já catalogadas na B80 foram reaproveitados como contexto geográfico, sem novo SSOT nem nova captura redundante. As vistas disponíveis não revelam as dimensões internas necessárias. Dados geográficos externos não substituem o levantamento do poço e não foram promovidos a assets finais. Nenhum GeoTIFF foi modificado; auditorias das capturas permanecem válidas como baseline.

## Desconhecidos e continuação

`unknown_matrix.json` separa fatos do projeto de valores atuais desconhecidos (`null`): abertura livre da porta, posição porta/soleira, gap, cabine W/D/H, perfil interno e folgas do poço, equipamentos/contrapesos, contornos/espessuras das lajes registrados no SSOT, alinhamento atual dos desembarques, datum absoluto e as-built. O registro humano de leitura é `docs/research/LACERDA_DRAWING_OBSERVATIONS_2026-10-06.json`.

Mantidos: porta fechada bloqueia passagem; cabine ausente bloqueia poço; partida depende de portas fechadas e sweeps aprovados; portal ocupado impede fechamento; informação desconhecida bloqueia. `movement_enabled: false` refere-se ao contrato do controller; timeline demonstrativa não virou viagem segura.

A continuação lógica é **registro documental do acesso superior e identificação inequívoca das lajes/aberturas**, seguida da obtenção das medidas da cabine atual. Só depois cabe uma revisão geométrica estreita e repetição dos sweeps. Lapa, Dique e Fonte Nova permanecem fora desta rodada. Não houve npm, build, suíte geral, alteração da cena, exportação ou falso teste físico.

## Verificação dirigida

`validation.json`: cinco revisões preservadas por hash, relatórios B80 canônicos inalterados, 27 testemunhas rastreáveis sem perda de classificação geométrica, referências de cada testemunha presentes no catálogo, 16 recursos com hash e arquivos brutos excluídos do Git, seis scripts com sintaxe válida e contrato B80 ainda não liberado. Essas verificações comprovam integridade documental, não física da engine.

`tools/references/validate_registry.py --root .`: zero erros, dois avisos herdados (bounds WGS84 da área ainda pendentes e referência insuficiente do cais Praça Cairu). Nenhum desses avisos foi ocultado ou corrigido por aproximação.
