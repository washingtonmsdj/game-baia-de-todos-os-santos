# Lacerda — estrutura inferior B93 — 07/10/2026

A B93 continua a arquitetura relativa da B92 na mesma janela Blender, PID 16912, MCP 9876, cena `SALVADOR | ESBOCO OFICIAL`. B76–B92 preservadas. Não houve alteração do terreno/SSOT, expansão, GAMEPLAY_PROXY B82 ou instalação histórica. Não exportada para produção.

## Causa e correções

1. **Cota da cobertura inferior.** A B88 usou 5,76m entre piso arquitetônico e cobertura. Isso misturava o nível de acesso -58,93 com o piso do saguão -59,01. Prancha12 identifica o piso -59,01; o corte23 identifica a cobertura Cidade Baixa -53,17. A diferença arquitetônica correta é **5,84m**. A cobertura subiu 0.08000000m; o topo das duas paredes acompanha sua face inferior, e a base da casca da torre acompanha seu topo. Piso, níveis superiores e datum histórico -3,709 não foram movidos. Espessura de cobertura 0,25m permanece herdada/candidata.
2. **Quatro apoios frontais.** A planta12 mostra quatro massas estruturais na linha da entrada. Foram recuperados os contornos pela união exata dos hatchs pretos do PDF, com IDs dos segmentos registrados em controls.json. Não houve convex hull, escala visual por foto, seis pilares genéricos ou criação de portas sem evidência. Quatro sólidos novos ligam a base da laje à face inferior da cobertura; sua posição é relativa ao mesmo registro arquitetônico B88, ainda sem implantação geográfica absoluta aprovada.
3. **Frente legada.** 51 peças da fachada/marquise/acabamento no antigo esquema foram identificadas pelo inventário e genealogia R30B02/03/07. Geometria, transform e materiais permanecem idênticos à B92, preservados como SUPERSEDED_REFERENCE. Não foram esticados ou deslocados para caber. Caixilhos, marquise e acabamento novos não foram inventados nesta etapa. Plataforma histórica inferior e elementos internos congelados permanecem intactos.

## Validação

- B93 salva e reaberta na mesma janela, com hash e identidade de cena conferidos.
- 597 componentes comparados com as assinaturas B88–B93; 391 visíveis sem faces degeneradas, arestas não manifold, winding inconsistente ou faces duplicadas internas no escopo auditado.
- 1155 componentes do inventário anterior, fora da alteração, geometricamente idênticos e com visibilidade preservada.
- 13 contatos de nível conferidos; gap máximo 0.00000000m. Isso comprova os encontros Z especificados, não fundações, carga estrutural ou todos os contatos/interseções XY do edifício.
- Terrain e proxies B82 comparados independentemente com o arquivo B92 preservado e idênticos. Metadados B82 mantidos na reabertura. Não foram vinculados à cena de arquitetura para contornar gates.
- Buffers com degeneração provenientes de hatch/triangulação foram rejeitados antes da aplicação. A triangulação em double preserva o contorno, com área conferida; os novos sólidos passam o QA.
- Não foram repetidos CCD/controller históricos: nenhuma alteração na cabine/poço. Esta revisão de arquitetura não certifica gameplay.

Apresentação conferida na própria cena B93: `local_view=false`, terreno visível e nenhuma alteração pendente na memória da janela. Captura real do viewport: `artifacts/lacerda-live-diagnostic/b93-map.png`; identidade registrada em `docs/reports/blender/lacerda-lower-structure-b93/presentation-map.json`.

## Encontro com terreno: pendência explicitamente preservada

No contorno frontal relativo da planta, o terreno B92 permanece em aproximadamente **7,25567m**. O piso documental relativo atual está em **11.11300873m**, diferença de cerca de **3,85734m**. Essa discrepância já existia entre o datum arquitetônico reconstruído e a implantação da cena; não foi ocultada com parede, fundação fictícia, aterro, rampa ou deslocamento global.

É necessária a conciliação independente de implantação/níveis do conjunto com a praça e as superfícies SSOT. O registro arquitetônico B88 continua derivado e relativo, com ssot_registration_accepted=false. Não apresentar a frente como acesso externo final validado. O túnel permanece candidato com área/limites ainda não conciliados integralmente com a prancha. O acabamento de fachada inferior, a marquise documental e a transição ao terreno não estão concluídos.

`LACERDA_VERTICAL = BLOCKED_EXTERNAL_EVIDENCE`

`movement_enabled = false`

`27 testemunhas B80 = UNRESOLVED / PRESERVED`

`GAMEPLAY_PROXY B82 = PRESERVED / replacement_required: true`

`ABSOLUTE_MAP_PLACEMENT = NEEDS_REVIEW`

`EXPANDED_MAP = GREYBOX`

`production_ready = false`

Fontes: SUCOP2023 pranchas12/23 catalogadas. controles/IDs/hashes: docs/reports/blender/lacerda-lower-structure-b93/controls.json. Antes/depois: application.json; QA: validation.json. Registros derivados continuam REPLACE_BEFORE_RELEASE. Não são desenhos de instalação/as-built dos ascensores.

Fonte ativa: `blender/salvador_lacerda_r30b93_estrutura_inferior_documental.blend`. SHA-256 `a1a8034893803a440a67c0a4b3b33d880684d309cc909776afe0f2966fc95c7f`.

Próximo passo estrutural: registro de implantação/nível do exterior com controles físicos da praça/terraço, preservando os níveis relativos documentais. Não deslocar o terreno ou o conjunto para apenas eliminar a diferença numérica. Marquise/fechamentos externos só após recuperar seus contornos documentais.
