"""Documentação/proveniência da correção real, sem promoção de produção."""
import json,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[2];out=root/'docs/reports/blender/lacerda-mesh-b91'
r=json.loads((out/'application.json').read_text());qa=json.loads((out/'validation.json').read_text())
assert r['reopened'] and qa['reopened'] and r['sha256']==qa['sha256']
assert hashlib.sha256((root/'world/geographic-reference.json').read_bytes()).hexdigest()==r['ssot_sha256']
with (root/r['file']).open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==r['sha256']
text=f'''# Lacerda — integridade de malha e encontros B91 — 07/10/2026

A B91 foi aplicada e reaberta na mesma janela Blender PID {r['pid']}, MCP 9876, cena `SALVADOR | ESBOCO OFICIAL`. Continuação da B90, preservando B76–B90. Esta é correção de arquitetura exterior candidata; não resolve implantação geográfica, datum da instalação, interiores ou controller.

## Erros comprovados e correções

| Causa | Antes, B90 | B91 |
|---|---|---|
| Seleção incompleta da montagem B88 | `CALIBRADO / passarela piso` permaneceu retangular, ~55,54 m, fora do novo contorno da ponte | Mesma peça e nome vinculados ao polígono `bridge` da prancha 17. Contato físico com intradorso e piso paginado, sem offset mundial |
| Casca da torre fragmentada e incompleta | Quatro grupos de prismas; corpo terminado em Z {r['contact_levels']['support_bottom_inherited']:.6f}, técnico iniciado em +4,00; intervalo sem fechamento arquitetônico | Uma casca contínua com o mesmo contorno externo/interno até a face inferior do capeamento. Três cascas e técnico originais preservados como referência substituída |
| Apoio da galeria indevidamente arquivado junto ao acabamento B88 | Consolo antigo ocultado, sem substituto estrutural adequado | Novo consolo alargado fechado, com vazio do núcleo, contorno superior documental e contato com fundo da galeria. Original permanece preservado |
| Prismas adjacentes construídos isoladamente | Faces internas opostas e vértices repetidos em apoios, alas, paredes inferiores e bandas da galeria | {qa['removed_internal_faces']} faces internas removidas; vértices coincidentes soldados em até 0,00001 m. Bounds e volumes de cada limpeza conferidos; sem fill-holes |
| Vértices colapsados nas três paredes superiores | Quatro arestas não manifold por parede; borda degenerada com extremos coincidentes | Soldagem localizada; as paredes permanecem fechadas e suas aberturas arquitetônicas não foram preenchidas |
| Duas coberturas para a mesma função | Volumes encaixados um dentro do outro, mesma face superior +14,00; sobreposição coplanar e material concorrente | Um volume ativo. `EDIFICIO / cobertura` preservado oculto como referência, sem apagamento |

{len(r['changes'])} objetos existentes tratados, um novo apoio. Não foram removidos objetos históricos. Materiais/aberturas não receberam detalhamento cosmético.

## Fontes, precisão e aproximações

- Contornos: controles vetoriais SUCOP 17 já registrados em `docs/reports/blender/lacerda-massing-b88/architectural-controls.json`.
- Continuidade vertical e presença do consolo: corte SUCOP 23 e fotografias já catalogadas. A forma da abertura interna não é certificação da seção útil do poço instalado.
- A espessura de parede 0,18 m permanece aproximação herdada, sem levantamento. Não foi apresentada como cota impressa.
- O consolo usa envoltória convexa do núcleo na base e contorno real da galeria no topo. Altura {r['contact_levels']['support_height_approximate']:.6f} m vem do intervalo herdado do modelo até o fundo atual da galeria, **não de cota documental**. Perfil, espessura e altura: `APPROXIMATE_SECTION_PROFILE_WITH_DOCUMENT_XY`, `replacement_required: true`, `CONSOLO_UNCOTED_PROFILE_AND_ABSOLUTE_PLACEMENT`.
- Espessura da laje da ponte resulta do encontro das superfícies existentes do intradorso e piso. Essa coerência de montagem não certifica espessura construtiva real.
- A transformação arquitetônica relativa B88 foi mantida. O SSOT geográfico não foi alterado para encaixar o asset.

## Verificação efetiva após reabertura

- {qa['objects_checked']} componentes comparados com assinaturas persistidas; {qa['visible_objects_checked']} visíveis auditados. Nos componentes visíveis auditados: zero faces degeneradas, zero arestas não manifold e zero grupos de faces coincidentes dentro de uma mesma malha.
- Nas limpezas, a maior variação relativa de volume foi {max(c['relative_volume_change'] for c in r['cleanup']):.10f}. Nenhuma abertura intencional foi tapada.
- Contornos de seis componentes estruturais conferidos contra CAD; maior residual numérico de bounds {max(c['cad_bounds_residual_m'] for c in qa['document_contours']):.8f} m.
- Quatro encontros estruturais explicitamente conferidos. Maior gap numérico: {max(c['gap_m'] for c in qa['structural_contacts']):.8f} m. Isso não prova automaticamente todos os encontros/auto-interseções do edifício.
- Diferença dos pisos arquitetônicos preservada: {qa['architectural_access_difference_m']:.8f} m. Não equivale à distância de parada da cabine B80.
- Assinaturas de terreno e proxy B82 comparadas independentemente com a B90. SSOT byte a byte intacto: `{r['ssot_sha256']}`.
- Fontes substituídas mantêm geometria original e permanecem separadas da camada ativa. Interfaces opostas entre materiais/componentes distintos podem ser contatos legítimos; não aplicar deduplicação automática da cidade.
- Colisores derivados continuam preservados e desabilitados quando dependem da arquitetura alterada. Não houve CCD/varredura do personagem ou export de runtime nesta rodada.

## Estados preservados

`LACERDA_VERTICAL = BLOCKED_EXTERNAL_EVIDENCE`

`movement_enabled = false`

`27 testemunhas B80 = UNRESOLVED / PRESERVED`

`GAMEPLAY_PROXY B82 = PRESERVED / replacement_required: true`

`ABSOLUTE_MAP_PLACEMENT = NEEDS_REVIEW`

`INTERIOR_LAYOUT = NOT_VALIDATED`

`EXPANDED_MAP = GREYBOX`

`production_ready = false`

Ainda faltam reconciliar implantação/datum inferior com o terreno e controlar o perfil sem cota do consolo, interfaces de saguões e layout interno. A inspeção desta rodada prova fechamento das malhas e encontros especificados; não autoriza chamar todo o mapa/instalação de perfeito.

Fonte ativa: `{r['file']}`. SHA-256: `{r['sha256']}`.
Relatórios: `before.json`, `contacts.json`, `application.json`, `validation.json`, em `docs/reports/blender/lacerda-mesh-b91/`.
'''
doc=root/'docs/LACERDA_MESH_STRUCTURE_B91_2026-10-07.md';doc.write_text(text,encoding='utf8')
provpath=root/'world/data-provenance.json';prov=json.loads(provpath.read_text());resource={'resource_id':'derived:lacerda-structure-mesh-b91','provider':'Bay of All Saints / modelagem autoral derivada SUCOP','dataset':'Correção de malhas e encontros da estrutura exterior Lacerda B91','capture_date':'2026-10-07','bounds':None,'raw_files':[],
 'derived_files':[r['file'],doc.relative_to(root).as_posix(),'docs/reports/blender/lacerda-mesh-b91/application.json','docs/reports/blender/lacerda-mesh-b91/validation.json'],'usage_class':'PENDENTE_VERIFICACAO','release_status':'REPLACE_BEFORE_RELEASE','purpose':'Arquitetura candidata exterior; espessuras/perfil sem cota e implantação/as-built pendentes',
 'dependencies':['derived:lacerda-massing-b90','source:lacerda-issue22-sucop-17','source:lacerda-issue22-sucop-23'],'kind':'geometry','generation_status':'APPLIED_LIVE_REOPENED_LOCAL_MESH_QA','accuracy':'DOCUMENT_CONTOURS_WITH_DECLARED_APPROXIMATE_STRUCTURE','replacement_required':True}
existing=next((v for v in prov['resources'] if v['resource_id']==resource['resource_id']),None)
if existing:existing.update(resource)
else:prov['resources'].append(resource)
ids={v['resource_id'] for v in prov['resources']};assert all(dep in ids for dep in resource['dependencies'])
provpath.write_text(json.dumps(prov,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
summary=f'''## 07/10/2026 — B91: integridade das malhas e encontros do Lacerda

B91 é authoring_source/validation_source, aplicada e reaberta na mesma janela MCP 9876. Corrigida a laje legada de ~55,54 m, casca da torre contínua e apoio alargado da galeria; 226 faces internas removidas, três paredes degeneradas corrigidas, uma cobertura redundante preservada fora da camada ativa. QA de {qa['objects_checked']} componentes, contatos estruturais explícitos sem gaps numéricos relevantes. Consolo/espessuras permanecem aproximados declarados; implantação absoluta, interiores, as-built e controller NÃO aprovados. B76–B90, terreno, SSOT, proxy B82, 27 testemunhas e BLOCKED_EXTERNAL_EVIDENCE preservados; movement_enabled false, produção B30 inalterada. Relatório: docs/LACERDA_MESH_STRUCTURE_B91_2026-10-07.md. Não reabrir investigação da instalação ou detalhar expansão por causa desta correção exterior.

'''
for name in ('PROJECT_STATUS.md','CODEX_HANDOFF.md','CODEX_STRUCTURE_HANDOFF.md'):
 path=root/'docs'/name;old=path.read_text(encoding='utf8')
 if not old.startswith('## 07/10/2026 — B91:'):path.write_text(summary+old,encoding='utf8')
print(json.dumps({'revision':'B91','objects_checked':qa['objects_checked'],'report':doc.relative_to(root).as_posix(),'provenance':resource['resource_id'],'production_ready':False},ensure_ascii=False))
