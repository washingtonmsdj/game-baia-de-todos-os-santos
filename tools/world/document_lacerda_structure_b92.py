"""Consolida relatório e proveniência das correções B91/B92."""
import json,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[2];out=root/'docs/reports/blender/lacerda-bridge-b92'
r=json.loads((out/'application.json').read_text());q=json.loads((out/'validation.json').read_text());q91=json.loads((root/'docs/reports/blender/lacerda-mesh-b91/validation.json').read_text())
assert r['reopened'] and q['reopened'] and q['sha256']==r['sha256']
assert hashlib.sha256((root/'world/geographic-reference.json').read_bytes()).hexdigest()==r['ssot_sha256']
with (root/r['file']).open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==r['sha256']
doc=root/'docs/LACERDA_STRUCTURE_B92_2026-10-07.md'
text=f'''# Lacerda — estrutura e malhas B91/B92 — 07/10/2026

A **B92** é a candidata de modelagem ativa, salva e reaberta na mesma janela Blender PID {r['pid']}, MCP 9876, cena `SALVADOR | ESBOCO OFICIAL`. B76–B91 preservadas. SSOT, terreno, proxy B82 e gates históricos mantidos. Nenhum export de produção ou alteração na expansão.

## Correção da causa raiz

A seleção da B88 ignorou componentes da coleção `08 ELEVADOR E TERRENO / dimensoes calibradas`. O nome da passarela dizia 28,71 m, mas sua malha ainda media cerca de **55,54 m**. Esses nomes históricos não são cotas confiáveis.

**B91:** laje da ponte reconstruída pelo mesmo contorno CAD do piso paginado; contato com intradorso e acabamento. Casca da torre contínua, apoio alargado da galeria e limpeza de malha. Removidas 226 faces internas opostas; soldadas as bordas degeneradas de três paredes, sem preencher abertura arquitetônica. Cobertura redundante preservada como referência. Relatório completo: `docs/LACERDA_MESH_STRUCTURE_B91_2026-10-07.md`.

**B92:** cobertura da passarela usa exatamente o mesmo contorno CAD da ponte, topo **+4,00 m**, conforme prancha 23. Os 18 montantes e duas vigas laterais do esboço antigo foram identificados como representação substituída: a nova ponte já tem caixilhos/estrutura longitudinal. Seus meshes/transforms permanecem intactos, com `SUPERSEDED_REFERENCE`, fora da apresentação ativa. A plataforma superior da implantação antiga também foi preservada como referência substituída; ela estava flutuando ao lado da galeria atual. Não foram movidos para encaixar nem apagados.

O binding `B82 / upper_walkway` cita a laje histórica, mas o proxy continua independente. Seus metadados foram comparados com a B90: **{len(r['proxy_metadata_restored']['changed_keys'])} diferenças**. Não foi promovido nem ajustado para a arquitetura candidata.

## Validação real

- {q['objects_checked']} componentes comparados com assinaturas após reabertura; {q['visible_objects_checked']} visíveis auditados com zero faces degeneradas, arestas não manifold, winding inconsistente ou faces duplicadas internas.
- Cobertura e laje da ponte possuem o mesmo contorno XY. Topo da cobertura acima do piso: {q['bridge_roof_above_walkable_m']:.8f} m.
- Quatro encontros estruturais explicitamente conferidos, gap numérico máximo {max(c['gap_m'] for c in q['structural_contacts']):.8f} m: intradorso/laje, laje/piso, núcleo/capeamento e consolo/galeria.
- Vinte componentes da ponte e a plataforma superior substituída conferidos geometricamente intactos e preservados como referência. B91 permanece preservada como revisão própria, com QA de {q91['objects_checked']} componentes. O checkpoint anterior de apresentação B92 foi preservado em `{r.get('presentation_checkpoint_backup','pending')}`, hash `{r.get('presentation_checkpoint_before_sha256','pending')}`.
- QA local de malha/contatos. **Não é auditoria integral de todas as auto-interseções do edifício**, aprovação de controller, CCD, layout interno ou fidelidade milimétrica.

## Aproximações e pendências explícitas

Apresentação final conferida em `docs/reports/blender/lacerda-bridge-b92/presentation-map.json`: B92 na mesma cena/janela, mapa completo, `local_view: false`, terreno visível e `unsaved_changes: false`. Capturas reais: `artifacts/lacerda-live-diagnostic/b92-exterior.png` (isolamento local de inspeção) e `b92-map.png` (mapa completo). Não são testes em engine nem outra cena.

Contornos documentais derivados das pranchas 17/23 não constituem registro geográfico absoluto aceito. O consolo possui forma alargada comprovada nas referências, mas sua altura/perfil sem cota e espessuras de montagem continuam candidatos declarados, `replacement_required: true`. Não apresentá-los como medidas as-built.

O inventário adicional encontrou 85 componentes legados/controles visíveis. Só os 20 componentes da ponte e a plataforma superior com substituição inequívoca foram retirados da camada ativa nesta etapa; a cobertura foi corrigida. Outros componentes — em especial fachada inferior, marquises e peças no antigo datum inferior — continuam como pendência de reconciliação do conjunto com o mapa. Não ocultar essas discrepâncias ajustando terreno ou declarando o gate resolvido.

`LACERDA_VERTICAL = BLOCKED_EXTERNAL_EVIDENCE`

`movement_enabled = false`

`27 testemunhas B80 = UNRESOLVED / PRESERVED`

`GAMEPLAY_PROXY B82 = PRESERVED / replacement_required: true`

`ABSOLUTE_MAP_PLACEMENT = NEEDS_REVIEW`

`INTERIOR_LAYOUT = NOT_VALIDATED`

`EXPANDED_MAP = GREYBOX`

`production_ready = false`

Próxima causa estrutural identificada: conciliar, com controles independentes, a fachada inferior/implantação do conjunto com os pisos relativos do projeto e terreno SSOT. Não investigar novamente cabine/poço por causa desta limpeza de malha. Não começar janelas novas ou decoração antes dessa reconciliação.

Fonte ativa: `{r['file']}`. SHA-256: `{r['sha256']}`.
Fonte canônica: `blender-revisions.json#/authoring_source`, também `validation_source`. Produção B30 e proxy B82 permanecem separados.
'''
doc.write_text(text,encoding='utf8')
provpath=root/'world/data-provenance.json';prov=json.loads(provpath.read_text());resource={'resource_id':'derived:lacerda-bridge-b92','provider':'Bay of All Saints / modelagem autoral derivada SUCOP','dataset':'Consolidação dos componentes estruturais da passarela Lacerda','capture_date':'2026-10-07','bounds':None,'raw_files':[],
 'derived_files':[r['file'],doc.relative_to(root).as_posix(),'docs/reports/blender/lacerda-bridge-b92/application.json','docs/reports/blender/lacerda-bridge-b92/validation.json'],'usage_class':'PENDENTE_VERIFICACAO','release_status':'REPLACE_BEFORE_RELEASE','purpose':'Completar seleção estrutural da ponte; não certifica implantação, interiores ou instalação atual','dependencies':['derived:lacerda-structure-mesh-b91','source:lacerda-issue22-sucop-17','source:lacerda-issue22-sucop-23'],'kind':'geometry','accuracy':'DOCUMENT_CONTOURS_WITH_DECLARED_APPROXIMATE_THICKNESS','replacement_required':True}
old=next((x for x in prov['resources'] if x['resource_id']==resource['resource_id']),None)
if old:old.update(resource)
else:prov['resources'].append(resource)
ids={x['resource_id'] for x in prov['resources']};assert all(x in ids for x in resource['dependencies'])
provpath.write_text(json.dumps(prov,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
summary=f'''## 07/10/2026 — B92 ativa: ponte e malhas estruturais consolidadas

B91/B92 corrigem omissão da coleção calibrada na seleção B88: laje/cobertura da ponte no contorno CAD, casca contínua da torre e consolo alargado; 226 faces internas removidas e três paredes com borda degenerada corrigidas. Vinte peças da ponte e a plataforma superior antiga preservadas como SUPERSEDED_REFERENCE; plataforma flutuante substituída fora da apresentação ativa. B92 salva/reaberta na mesma janela MCP 9876; QA de {q['objects_checked']} componentes, {q['visible_objects_checked']} visíveis sem faces degeneradas/arestas não manifold/winding inconsistente/duplicatas internas. Quatro contatos estruturais verificados. Consolo/espessuras sem cota e implantação geográfica permanecem candidatos; fachada inferior no antigo datum ainda requer reconciliação independente. B76–B91, SSOT, terreno, GAMEPLAY_PROXY B82, 27 testemunhas e BLOCKED_EXTERNAL_EVIDENCE preservados; movement_enabled false, produção B30 inalterada. Relatório: docs/LACERDA_STRUCTURE_B92_2026-10-07.md. Fonte authoring_source/validation_source B92; não exportar. Próxima prioridade: implantação/interface inferior, sem reabrir cabine/poço ou fazer decoração.

'''
for name in ('PROJECT_STATUS.md','CODEX_HANDOFF.md','CODEX_STRUCTURE_HANDOFF.md'):
 path=root/'docs'/name;text=path.read_text(encoding='utf8')
 if text.startswith('## 07/10/2026 — B92 ativa:'):
  next_heading=text.find('\n## ',1)
  text=text[next_heading+1:] if next_heading>=0 else ''
 path.write_text(summary+text,encoding='utf8')
profilepath=root/'world/areas/mvp-centro-lacerda/corridor-slice.json';profile=json.loads(profilepath.read_text())
history=profile.setdefault('revision_history',[])
entry={'revision':'R30B.92','scope':'Ponte documental e integridade exterior; sem aprovação de controller ou instalação','movement_enabled':False,'evidence':doc.relative_to(root).as_posix()}
existing=next((row for row in history if row.get('revision')=='R30B.92'),None)
if existing:existing.update(entry)
else:history.append(entry)
profilepath.write_text(json.dumps(profile,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'revision':'B92','report':doc.relative_to(root).as_posix(),'objects_checked':q['objects_checked'],'provenance':resource['resource_id'],'production_ready':False},ensure_ascii=False))
