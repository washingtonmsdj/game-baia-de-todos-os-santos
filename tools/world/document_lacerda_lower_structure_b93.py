"""Relatório e proveniência da estrutura inferior B93, após validação real."""
import json,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[2];out=root/'docs/reports/blender/lacerda-lower-structure-b93'
r=json.loads((out/'application.json').read_text());q=json.loads((out/'validation.json').read_text());c=json.loads((out/'controls.json').read_text())
assert r['reopened'] and q['reopened'] and q['sha256']==r['sha256']
with (root/r['file']).open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==r['sha256']
assert hashlib.sha256((root/'world/geographic-reference.json').read_bytes()).hexdigest()==r['ssot_sha256']
doc=root/'docs/LACERDA_LOWER_STRUCTURE_B93_2026-10-07.md'
text=f'''# Lacerda — estrutura inferior B93 — 07/10/2026

A B93 continua a arquitetura relativa da B92 na mesma janela Blender, PID {r['pid']}, MCP 9876, cena `SALVADOR | ESBOCO OFICIAL`. B76–B92 preservadas. Não houve alteração do terreno/SSOT, expansão, GAMEPLAY_PROXY B82 ou instalação histórica. Não exportada para produção.

## Causa e correções

1. **Cota da cobertura inferior.** A B88 usou 5,76m entre piso arquitetônico e cobertura. Isso misturava o nível de acesso -58,93 com o piso do saguão -59,01. Prancha12 identifica o piso -59,01; o corte23 identifica a cobertura Cidade Baixa -53,17. A diferença arquitetônica correta é **5,84m**. A cobertura subiu {r['roof_delta_applied']:.8f}m; o topo das duas paredes acompanha sua face inferior, e a base da casca da torre acompanha seu topo. Piso, níveis superiores e datum histórico -3,709 não foram movidos. Espessura de cobertura 0,25m permanece herdada/candidata.
2. **Quatro apoios frontais.** A planta12 mostra quatro massas estruturais na linha da entrada. Foram recuperados os contornos pela união exata dos hatchs pretos do PDF, com IDs dos segmentos registrados em controls.json. Não houve convex hull, escala visual por foto, seis pilares genéricos ou criação de portas sem evidência. Quatro sólidos novos ligam a base da laje à face inferior da cobertura; sua posição é relativa ao mesmo registro arquitetônico B88, ainda sem implantação geográfica absoluta aprovada.
3. **Frente legada.** {r['legacy_front_preserved']} peças da fachada/marquise/acabamento no antigo esquema foram identificadas pelo inventário e genealogia R30B02/03/07. Geometria, transform e materiais permanecem idênticos à B92, preservados como SUPERSEDED_REFERENCE. Não foram esticados ou deslocados para caber. Caixilhos, marquise e acabamento novos não foram inventados nesta etapa. Plataforma histórica inferior e elementos internos congelados permanecem intactos.

## Validação

- B93 salva e reaberta na mesma janela, com hash e identidade de cena conferidos.
- {q['objects_checked']} componentes comparados com as assinaturas B88–B93; {q['visible_objects_checked']} visíveis sem faces degeneradas, arestas não manifold, winding inconsistente ou faces duplicadas internas no escopo auditado.
- {q['protected_scoped_objects']} componentes do inventário anterior, fora da alteração, geometricamente idênticos e com visibilidade preservada.
- {len(q['structural_contacts'])} contatos de nível conferidos; gap máximo {max(x['gap_m'] for x in q['structural_contacts']):.8f}m. Isso comprova os encontros Z especificados, não fundações, carga estrutural ou todos os contatos/interseções XY do edifício.
- Terrain e proxies B82 comparados independentemente com o arquivo B92 preservado e idênticos. Metadados B82 mantidos na reabertura. Não foram vinculados à cena de arquitetura para contornar gates.
- Buffers com degeneração provenientes de hatch/triangulação foram rejeitados antes da aplicação. A triangulação em double preserva o contorno, com área conferida; os novos sólidos passam o QA.
- Não foram repetidos CCD/controller históricos: nenhuma alteração na cabine/poço. Esta revisão de arquitetura não certifica gameplay.

Apresentação conferida na própria cena B93: `local_view=false`, terreno visível e nenhuma alteração pendente na memória da janela. Captura real do viewport: `artifacts/lacerda-live-diagnostic/b93-map.png`; identidade registrada em `docs/reports/blender/lacerda-lower-structure-b93/presentation-map.json`.

## Encontro com terreno: pendência explicitamente preservada

No contorno frontal relativo da planta, o terreno B92 permanece em aproximadamente **7,25567m**. O piso documental relativo atual está em **{c['levels']['hall_floor_world']:.8f}m**, diferença de cerca de **3,85734m**. Essa discrepância já existia entre o datum arquitetônico reconstruído e a implantação da cena; não foi ocultada com parede, fundação fictícia, aterro, rampa ou deslocamento global.

É necessária a conciliação independente de implantação/níveis do conjunto com a praça e as superfícies SSOT. O registro arquitetônico B88 continua derivado e relativo, com ssot_registration_accepted=false. Não apresentar a frente como acesso externo final validado. O túnel permanece candidato com área/limites ainda não conciliados integralmente com a prancha. O acabamento de fachada inferior, a marquise documental e a transição ao terreno não estão concluídos.

`LACERDA_VERTICAL = BLOCKED_EXTERNAL_EVIDENCE`

`movement_enabled = false`

`27 testemunhas B80 = UNRESOLVED / PRESERVED`

`GAMEPLAY_PROXY B82 = PRESERVED / replacement_required: true`

`ABSOLUTE_MAP_PLACEMENT = NEEDS_REVIEW`

`EXPANDED_MAP = GREYBOX`

`production_ready = false`

Fontes: SUCOP2023 pranchas12/23 catalogadas. controles/IDs/hashes: docs/reports/blender/lacerda-lower-structure-b93/controls.json. Antes/depois: application.json; QA: validation.json. Registros derivados continuam REPLACE_BEFORE_RELEASE. Não são desenhos de instalação/as-built dos ascensores.

Fonte ativa: `{r['file']}`. SHA-256 `{r['sha256']}`.

Próximo passo estrutural: registro de implantação/nível do exterior com controles físicos da praça/terraço, preservando os níveis relativos documentais. Não deslocar o terreno ou o conjunto para apenas eliminar a diferença numérica. Marquise/fechamentos externos só após recuperar seus contornos documentais.
'''
doc.write_text(text,encoding='utf8')
provpath=root/'world/data-provenance.json';prov=json.loads(provpath.read_text())
resource={'resource_id':'derived:lacerda-lower-structure-b93','provider':'Bay of All Saints / modelagem autoral derivada SUCOP','dataset':'Cotas e quatro apoios frontais da estrutura inferior Lacerda','capture_date':'2026-10-07','bounds':None,'raw_files':[], 'derived_files':[r['file'],doc.relative_to(root).as_posix(),'docs/reports/blender/lacerda-lower-structure-b93/controls.json','docs/reports/blender/lacerda-lower-structure-b93/application.json','docs/reports/blender/lacerda-lower-structure-b93/validation.json'], 'usage_class':'PENDENTE_VERIFICACAO','release_status':'REPLACE_BEFORE_RELEASE','purpose':'Arquitetura relativa documental; sem certificação de implantação, as-built, interiores ou controller','dependencies':['derived:lacerda-bridge-b92','source:lacerda-issue22-sucop-12','source:lacerda-issue22-sucop-23'],'kind':'geometry','accuracy':'DOCUMENT_RELATIVE_LEVELS_VECTOR_CONTOURS_INHERITED_THICKNESS','replacement_required':True}
old=next((v for v in prov['resources'] if v['resource_id']==resource['resource_id']),None)
if old:old.update(resource)
else:prov['resources'].append(resource)
ids={v['resource_id'] for v in prov['resources']};assert all(v in ids for v in resource['dependencies'])
provpath.write_text(json.dumps(prov,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
summary=f'''## 07/10/2026 — B93 ativa: estrutura inferior documental

B93 continua B92: cobertura inferior corrigida em +0,08m (-59,01 piso → -53,17 cobertura = 5,84m), encontros de paredes/casca reconciliados e quatro apoios frontais recuperados dos vetores CAD12. {r['legacy_front_preserved']} peças da frente legada preservadas integralmente como referência substituída, sem migrar acabamentos por escala visual. Salva/reaberta na mesma janela MCP9876; QA de {q['objects_checked']} componentes, {q['visible_objects_checked']} visíveis, e {len(q['structural_contacts'])} contatos Z. Comparação independente com B92 confirma terrain/proxyB82 intactos. Implantação absoluta e interface com terreno permanecem NEEDS_REVIEW (piso relativo ~3,857m acima do terreno na linha frontal). B76–B92, SSOT, gates, 27 testemunhas, movement_enabled=false e produção preservados. Relatório: docs/LACERDA_LOWER_STRUCTURE_B93_2026-10-07.md. Fonte authoring_source/validation_source B93; não exportar. Próximo passo: implantação exterior por controles físicos, sem reabrir cabine/poço nem detalhar expansão.

'''
for name in ('PROJECT_STATUS.md','CODEX_HANDOFF.md','CODEX_STRUCTURE_HANDOFF.md'):
    path=root/'docs'/name;t=path.read_text(encoding='utf8')
    if t.startswith('## 07/10/2026 — B93 ativa:'):
        i=t.find('\n## ',1);t=t[i+1:] if i>=0 else ''
    path.write_text(summary+t,encoding='utf8')
print(json.dumps({'report':doc.relative_to(root).as_posix(),'revision':'B93','production_ready':False},ensure_ascii=False))
