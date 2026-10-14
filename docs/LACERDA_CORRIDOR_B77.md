# Corredor Lacerda–Cairu — B77

Revisão salva e reaberta: `blender/salvador_lacerda_r30b77b_portas_e_percurso.blend`.
SHA-256: `2318f33cb65d72dc77efc13bc00d46db48188847d5dd405ff042495fda3927f8`. B76 preservada byte a byte.
Esta revisão é candidata geométrica e demonstração Blender, não aprovação de física/release.

## Comparação com B76

A revisão final desta rodada é B77B. B77 intermediária permanece preservada: a checagem com portas reais detectou abertura nula por origens compartilhadas e saída inferior pelo lado fechado. B77B calcula o movimento pelos centros geométricos/projeção dos vértices das folhas, usa o desembarque inferior correto e reconhece o topo da plataforma existente como chão. Nenhum vão foi preenchido.

| Item | Antes | Depois |
|---|---|---|
| Objetos existentes | 6069 | Todos preservados, mesmas malhas base, materiais, transforms e hierarquia no frame original |
| SSOT/terreno/Hero Assets | B76 | Mesma origem, escala, orientação, Z local; nenhum deslocamento ou reescala |
| Consolo sob galeria | Intersectava seção da cabine | Um Boolean reversível recorta somente a seção XY existente da cabine, extrudida verticalmente |
| Massing OSM 1263035777 | Volume sólido sobre o saguão; altura não fornecida no OSM | Referência preservada e ocultada de render/colisão; não usada para identificar/mover um Hero |
| Colisão | Pisos arquitetônicos e proxies dispersos | 15 derivados superiores separados nas coleções existentes, mais terreno de colisão reaproveitado |
| Serviço/câmera | Sem animação funcional ativa na cabine 3 | Cabine/portas existentes animadas; câmera acompanha as rotas amostradas |

Foram adicionados 19 objetos derivados de QA/colisão/referência; nenhum dos 6069 objetos anteriores foi removido. O recorte altera a geometria **avaliada** de um consolo, não sua malha base. Dimensões herdadas da cabine são candidatas; isso não comprova a construção real do poço.

## Alturas e circulação

Os novos colisores são de pisos. A auditoria de passagem considera obstáculos da geometria real, mas ainda não constitui pacote completo de colisores simplificados de paredes/obstáculos para uma engine. Essa integração permanece explícita no contrato da slice.

Piso superior da cabine: 70.114998 unidades; inferior: 7.405998; deslocamento relativo: 62.709000. São cotas locais existentes, não altitude geodésica certificada.
Pavimento Cairu/entrada Mercado: 7,255661; passeio/saguão inferior: 7,406 aproximadamente. Não foi necessário modificar relevo para obter as rotas.

Rota superior: 84.505 unidades; inferior até a entrada do Mercado: 138.406. A* em malhas reais com grid 0,4, personagem de raio 0,3/altura 1,8 e degrau máximo 0,25; dimensões são parâmetros de gameplay, não levantamento.
Verificação inclui apoio lateral e meio de segmento. No pequeno vão da soleira superior, a semiesfera inferior encontra bordas reais com queda máxima de 0,03; nenhum plano foi criado para preencher o vão. Essa hipótese exige controller compatível na engine.
Sondagem vertical do personagem no centro da cabine: 0 bloqueios após correção. Não equivale a sweep volumétrico integral da cabine ou simulação física.
As portas animadas reais também foram verificadas em todas as poses das duas rotas, sem bloqueios nas amostras; evidência `doors_b77.json`. Verificações do embarque superior e inferior estão em `portal_probe_b77.json`.
Os bloqueios das linhas retas iniciais não são contagem comparável às rotas A*: a busca contorna obstáculos existentes. Pisos estruturais sob paginação foram distinguidos do piso visual; proxy simplificado da passarela difere cerca de 8 mm do visual.

## Aleph e fontes

Mantido Aleph pinado em `d24c61507481a91a0dd6afac4f97626a4e5ea780`. Reutilizados OSM e candidatos DEM existentes; aquisição adicional inclui um recorte satélite de 240 m e quatro consultas Street View, com metadados/hashes e código pinado.
O satélite permite conferir relações Lacerda/Cairu/Mercado/escarpa; uma vista baixa mostra a entrada coberta e o acesso. As consultas superiores retornaram vistas obstruídas ou no nível baixo: não comprovam acesso superior ou dimensões.
Nenhuma imagem temporária virou textura final. GeoTIFF de melhor residual permanece candidato; não aplicado globalmente. Terreno expandido continua atribuído ao Terrarium efetivo, sem troca silenciosa de fonte.

## Proveniência e gate

Política central: `world/provenance-policy.json`; índice de dados: `world/data-provenance.json`; catálogos `media-manifest.json` continuam canônicos para mídia.
Classes: FINAL_ALLOWED, FINAL_ALLOWED_WITH_ATTRIBUTION, DEV_REFERENCE_ONLY e REPLACE_BEFORE_RELEASE. Dados herdados sem confirmação continuam pendentes, não recebem aprovação implícita.
`tools/references/audit_release_provenance.py` audita manifesto completo declarado, dependências transitivas, atribuição, hashes, origem desconhecida e inclusão de brutos mesmo renomeados. Dez verificações dirigidas tiveram os resultados esperados.
Fundação pronta para integração futura do exportador; não existe gate integrado ao build final nesta rodada. O inventário de materiais/imagens da cena aponta bindings ausentes. O mapa não está aprovado para release.

## Revisão visual no Blender

Câmera `B77 | QA | personagem`: frame 65024 inicia caminhada; 66497 inicia descida; 67025 inicia Cairu–Mercado; 69398 encerra.
Reprodução pode ser lenta: estes são keyframes de revisão, não controller interativo. Cabine para cima ao retornar ao frame inicial; os objetos originais mantêm posições no frame baseline 31978.

## Pendências e próximo trecho

Continuam pendentes o datum absoluto, a escala física certificada, dados do acesso superior e dimensões/folgas reais da cabine, sweep integral, controller/colisão dinâmica e bloqueio de navegação conforme portas.
Lapa, Campo da Pólvora, Dique e Fonte Nova seguem greybox. Margem aberta do Dique e vias finais não foram escondidas ou niveladas. Os 118 casos edifício/terreno e 234 transforms permanecem triagem da B76, não bugs automaticamente corrigidos.
Próximo fechamento lógico: passagem saguão superior–soleira–cabine e volume completo do poço, seguido de travessias pedonais Cairu–entrada Mercado em controller real. Não avançar para fachadas ou Fonte Nova enquanto esses gates estiverem pendentes.

Evidências: `docs/reports/blender/lacerda-corridor/` e contrato `world/areas/mvp-centro-lacerda/corridor-slice.json`.
