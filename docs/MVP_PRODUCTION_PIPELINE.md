# Produção do MVP: Blender → pacote interoperável → Three.js

## Fonte de verdade por responsabilidade

O contrato executável é `world/areas/mvp-centro-lacerda/production.json`.
Não escolher a revisão pelo maior número no nome, arquivo mais recente, contexto
de chat ou preferência de um exportador. A R30A.11 está ativa por escolha explícita
do usuário. A R30A.12 permanece preservada como revisão histórica/candidata.

| Responsabilidade | Fonte canônica |
| --- | --- |
| Revisão ativa, hashes, exportação, coordenadas e perfil de runtime | `production.json` |
| Implantação, terreno e geometria artística da área | `.blend` em `world_source.file` |
| Veículo editável | `.blend` em `vehicle.source.file` |
| Identidade dos locais e estado de aprovação | `locations.json` |
| OSM/DEM, referências e proveniência | catálogos já existentes em `world/` e `docs/references/` |
| Lógica de gameplay | código versionado; não fica embutida em materiais/nomes de objetos |
| Pacote de entrega | manifesto gerado, nunca uma segunda fonte editável |

SSOT não significa guardar tudo em um arquivo. Significa não ter duas autoridades
para a mesma decisão. Os relatórios documentam o contrato; não o substituem.

## Organização do Blender

Uma cena de composição por área mantém origem, implantação, terreno, vias e
referências. É correto o MVP atual continuar em uma composição única. Cada
prédio **não precisa** virar um `.blend` apenas por existir.

Assets reutilizáveis, com edição independente ou maior complexidade ficam em
`blender/assets/<asset_id>/` (os veículos existentes em `blender/assets/` são
preservados). A composição deve usar bibliotecas vinculadas/instâncias de coleção
quando esses assets forem integrados, com caminhos relativos. Overrides são
locais e explícitos; `Append` repetido não é atualização de biblioteca.

Dentro do asset, separar geometria visual, colisão, LODs, rig, pontos de montagem e
apresentação. Chão de estúdio, luzes e câmeras nunca pertencem ao veículo exportado.
Usar `boas_asset_id` para assets novos e `boas_location_id` somente após binding
validado. Não criar correspondência geográfica pela semelhança de nomes.

As coleções autorais existentes são mantidas. A exportação usa seleção declarada
no contrato e respeita visibilidade/renderização. Um objeto compartilhado com uma
coleção GAMEPLAY não deixa de ser arte: exportá-lo uma única vez.

Separar HERO, ENVIRONMENT_FINAL, GAMEPLAY_TERRAIN, ROAD_DRIVEABLE,
SIDEWALK_WALKABLE, COLLISION, NAVIGATION_HINTS, WATER e SOURCE_GEOREF.
Essa separação é de responsabilidade; não exige cortar destrutivamente o terreno.
No terreno composto atual, as pistas são extraídas pelos materiais registrados,
não pelos índices variáveis dos slots. A mesh visual não vira collider geral.

Não foram divididos/movidos prédios nem criadas cópias novas de `.blend` nesta
correção. Migrar um Hero para biblioteca exige preservar pivô, transforms,
constraints, referências e funcionamento de interiores, com revisão específica.

## Coordenadas

- Blender: metros, Z para cima, origem local existente.
- Runtime/glTF: `(X,Y,Z) Blender → (X,Z,-Y)`; rotação com determinante positivo.
- GLB já está convertido pelo exportador. O carregador não aplica outra reflexão.
- Grafo OSM em `blender_xy` é convertido na fronteira de leitura.
- O pacote de colisão já usa coordenadas de runtime; não converter duas vezes.
- Fit geográfico permanece `candidate`. Nenhum offset/reescala geográfica novo.

## Fluxo de trabalho obrigatório

1. Ler o contrato e abrir a fonte registrada na única janela visível do Blender.
2. Editar na coleção/asset responsável. Preservar IDs, origem e referências.
3. Se houve alteração real, salvar uma revisão e promover caminho/hash no contrato.
   Não sobrescrever a base validada nem criar revisão vazia.
4. Pelo MCP executar `automation/blender/export_active_world.py`. O wrapper
   recusa cena não salva ou arquivo diferente. Exportadores leem o mesmo contrato.
   Se a mesma fonte já tiver exportação, uma diferença no conjunto de objetos
   interrompe a operação: visibilidade temporária não pode publicar meia cidade.
5. Fora do Blender executar `python tools/runtime/package_world.py`.
   É empacotamento de assets, não build do aplicativo.
6. Conferir relatório `docs/reports/runtime/package_world.json` e visualização.
   Promover a revisão só após verificar orientação, pontos de acesso e gameplay.

Para editar/exportar o ônibus, abrir a fonte de `vehicle.source` na mesma janela
e usar `automation/blender/export_onibus_torino_glb.py`. Voltar à composição para
integração. Não criar outra janela nem substituir a cena de cidade pelo estúdio.

Os caminhos de staging antigos permanecem como compatibilidade dos exportadores.
O jogo passa a consumir exclusivamente `/world/runtime.json` e os arquivos de sua
release, nunca esses caminhos legados diretamente. Para novo clone, gerar o
pacote antes de iniciar Vite. Não instalar/rodar uma build para exportar a cidade.

## Carregamento e setorização

O empacotador preserva vértices, índices, materiais, transforms e ancestrais glTF.
Cada nó com mesh pertence a exatamente um setor. Ancestrais sem mesh podem ser
repetidos como estrutura, sem duplicar a geometria. Não recorta prédios pelo meio.

Objetos menores são atribuídos a células de 256 m. Objetos maiores que uma célula
(terreno contínuo/oceano) ficam no core. O tamanho é uma configuração de entrega,
não uma alteração da geografia. Mudar o tamanho gera nova release.

O carregador verifica tamanho e SHA-256, mantém no máximo duas requisições de
setores simultâneas, prioriza proximidade, usa distâncias diferentes para carregar
e descarregar e libera geometria/material/textura quando remove um setor.
Erros ficam explícitos; não há cidade, ônibus ou terreno sintético substituto.

Na visão geral todos os setores são solicitados progressivamente. No modo a pé,
somente a vizinhança permanece carregada. Entrada em setor não pronto é bloqueada;
a colisão do MVP permanece residente para não desaparecer sob o jogador.
O manifesto atual só é substituído após os arquivos completos estarem publicados.
URLs contêm a identidade da release: arquivos antigos não são misturados com novos.

## Perfil de execução e limites ainda abertos

O perfil inicial é provisório: 12 ônibus, teto de 30 FPS, pixel ratio máximo 1,25,
sombras 1024. Esses valores são configuráveis no contrato, não medições de capacidade
da máquina nem substitutos para LOD/otimização geométrica.

Ainda pendentes: LODs do ônibus e de Hero assets, rig/suspensão individual, colisão
predial completa, navegação/trânsito robustos, subdivisão do terreno visual amplo,
streaming da colisão e medição CPU/GPU em hardware-alvo. Não declarar o MVP completo
ou otimizado só porque agora existe streaming. A grade viária mantém larguras
aproximadas para gameplay; não são dimensões levantadas.

## Versionamento

Fontes `.blend`, inclusive subpastas, são Git LFS. Scripts, contrato e relatórios
textuais ficam no Git normal. Releases derivadas em `public/world/releases/` e
o ponteiro gerado `runtime.json` são ignorados e reproduzíveis. O empacotador não
apaga releases antigas automaticamente nem executa Git. Os binários de staging
historicamente versionados permanecem rastreáveis até migração dedicada.

Os scripts históricos em `automation/blender/r*` são histórico de revisões,
não entradas de produção concorrentes. Novos trabalhos devem partir do wrapper
canônico e do contrato, sem procurar "o arquivo mais recente".
