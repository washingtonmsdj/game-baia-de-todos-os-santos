"""Registra os fechamentos B94 somente após salvar, reabrir e validar a cena."""
import json,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[2];out=root/'docs/reports/blender/lacerda-closure-b94'
r=json.loads((out/'application.json').read_text());q=json.loads((out/'validation.json').read_text());p=json.loads((out/'presentation.json').read_text())
assert r['reopened'] and q['reopened'] and q['sha256']==r['sha256']
assert p['file']==r['file'] and not p['local_view'] and p['terrain_visible'] and not p['unsaved_changes']
with (root/r['file']).open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==r['sha256']
assert hashlib.sha256((root/'world/geographic-reference.json').read_bytes()).hexdigest()==r['ssot_sha256']
doc=root/'docs/LACERDA_CORRIDOR_CLOSURE_B94_2026-10-07.md'
text=f'''# Lacerda — fechamentos da passarela e do túnel B94 — 07/10/2026

B94 aplicada ao vivo, salva e reaberta na mesma janela Blender, PID {r['pid']}, MCP 9876, cena `SALVADOR | ESBOCO OFICIAL`. B76–B93 preservadas. Esta rodada responde aos vãos indevidos dos corredores, sem retomar investigação do datum ou da instalação dos elevadores.

## Antes e depois

1. **Passarela → saguão superior.** Faltavam os dois retornos na extremidade oeste do contorno SUCOP17: lado norte entre a quina externa do saguão e o endpoint da ponte; lado sul entre o outro endpoint da ponte e a quina externa. Foram construídos peitoril, vidro e verga, usando os materiais existentes. O portal central continua aberto: largura documental local {q['portal_width_m']:.6f}m. Não foi criada uma parede atravessando a circulação. Os pisos e a cobertura agora incluem os mesmos endpoints da ponte, eliminando uma pequena divergência entre os contornos. Recorte do núcleo antigo mantido.
2. **Túnel → face existente da torre antiga.** Piso e teto terminavam antes da reentrância permanente da torre; havia um tampão transversal nessa extremidade prematura. A união das lajes incorpora o pequeno encontro de {q['connector_area_m2']:.6f}m² entre o contorno inferior SUCOP12 e a face da torre já reconstruída de SUCOP17. As paredes laterais chegam aos mesmos endpoints; o tampão prematuro foi substituído pelos retornos laterais. A face da torre e o envelope do poço permanecem intactos. Este encontro é `ADAPT_LOCAL` derivado dos contornos documentais existentes; não é prova de alinhamento as-built entre plantas de pavimentos diferentes nem aprovação da entrada no poço.
3. **Malha das paredes.** A representação usa união planar antes da extrusão, incluindo os encontros de canto. Evita caixas soldadas apenas por arestas, faces internas duplicadas e quinas abertas. Espessura 0,18m permanece aproximação herdada, registrada como candidata. Não foram inventadas cotas de parede ou dimensões da cabine.

Seis meshes existentes alteradas e seis componentes de retorno adicionados. Objetos-fonte, transforms, frame arquitetônico, núcleo das torres, níveis dos pisos, terreno e SSOT preservados. Nenhuma mudança em Lapa, Dique, Fonte Nova ou decoração.

## Verificação real

- Reabertura da B94 com arquivo, hash, PID e cena conferidos.
- {q['objects_checked']} componentes B88–B94 comparados às assinaturas persistidas; {q['visible_objects_checked']} visíveis sem faces degeneradas, arestas não manifold, winding inconsistente ou faces duplicadas no escopo auditado.
- {q['protected_before_application']} objetos fora da edição protegidos durante a aplicação; {len(q['protected_scoped_after_reopen'])} meshes do inventário local, fora da edição, conferidas novamente após a reabertura. Não confundir essas duas contagens.
- {len(q['surface_checks'])} sondagens reais de piso/cobertura nos retornos e no prolongamento do túnel; {len(q['wall_checks'])} sondagens das paredes em várias alturas; {len(q['portal_checks'])} verificações de abertura do portal; {len(q['structural_contacts'])} encontros verticais, gap máximo {max(c['gap_m'] for c in q['structural_contacts']):.8f}m.
- Sondagens de superfície usam barycentros em double sobre os triângulos reais. A BVH float apresentou erro numérico Z de cerca de 0,00013m em um triângulo estreito; não houve alteração de skin, cápsula ou geometria para mascarar isso. Os hits BVH e os resultados double ficam registrados.
- SSOT, terreno e assinaturas do GAMEPLAY_PROXY B82 idênticos aos anteriores.
- {len(r['invalidated_bindings'])} bindings históricos preservados, explicitamente desabilitados/invalidados após a alteração dos objetos-fonte. Nenhum collider novo duplicado e nenhuma declaração de controller aprovado.
- Vistas reais de ambas as junções e do mapa completo em `artifacts/lacerda-live-diagnostic/b94-*.png`. A janela terminou com `local_view=false`, terreno visível e `unsaved_changes=false`.

Esta validação comprova os fechamentos e encontros no escopo acima. Não comprova toda a circulação interna, implantação absoluta, cabine/poço, CCD da cabine ou controller. Não foi repetido o CCD histórico sem alteração da instalação. A relação entre piso inferior e terreno mantém a pendência documentada na B93; não foi escondida com aterro, rampa ou parede.

## Estados preservados

`LACERDA_VERTICAL = BLOCKED_EXTERNAL_EVIDENCE`

`movement_enabled = false`

`27 testemunhas B80 = UNRESOLVED / PRESERVED`

`GAMEPLAY_PROXY B82 = PRESERVED / replacement_required: true`

`ABSOLUTE_MAP_PLACEMENT = NEEDS_REVIEW`

`EXPANDED_MAP = GREYBOX`

`production_ready = false`

Fonte ativa: `{r['file']}`. SHA-256 `{r['sha256']}`. Produção e fonte gameplay continuam anteriores; não exportar esta candidata para produção.

Controles e genealogia: `docs/reports/blender/lacerda-closure-b94/mutation-journal.json`; antes: `before.json`; alterações: `application.json`; QA: `validation.json`; apresentação: `presentation.json`. Fontes SUCOP12/17 dependem do registro relativo B88 já documentado e permanecem separadas do SSOT canônico.

Próxima verificação de modelagem: revisar os demais encontros exteriores contra a planta, preservando as entradas reais. A conexão arquitetônica ao poço e o percurso completo não podem ser declarados funcionais pela correção destas seams.
'''
doc.write_text(text,encoding='utf8')
provpath=root/'world/data-provenance.json';prov=json.loads(provpath.read_text())
resource={'resource_id':'derived:lacerda-corridor-closure-b94','provider':'Bay of All Saints / modelagem autoral derivada SUCOP','dataset':'Fechamentos laterais superiores e encontro do túnel com a torre existente','capture_date':'2026-10-07','bounds':None,'raw_files':[],'derived_files':[r['file'],doc.relative_to(root).as_posix(),'docs/reports/blender/lacerda-closure-b94/mutation-journal.json','docs/reports/blender/lacerda-closure-b94/application.json','docs/reports/blender/lacerda-closure-b94/validation.json'],'usage_class':'PENDENTE_VERIFICACAO','release_status':'REPLACE_BEFORE_RELEASE','purpose':'Fechamentos arquitetônicos relativos, sem certificação de implantação, as-built, poço ou controller','dependencies':['derived:lacerda-lower-structure-b93','source:lacerda-issue22-sucop-12','source:lacerda-issue22-sucop-17'],'kind':'geometry','accuracy':'DOCUMENT_CONTOURS_LOCAL_JUNCTION_INHERITED_THICKNESS','replacement_required':True}
old=next((v for v in prov['resources'] if v['resource_id']==resource['resource_id']),None)
if old:old.update(resource)
else:prov['resources'].append(resource)
ids={v['resource_id'] for v in prov['resources']};assert all(v in ids for v in resource['dependencies'])
provpath.write_text(json.dumps(prov,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
summary=f'''## 07/10/2026 — B94 ativa: fechamentos da passarela e do túnel

B94 continua B93 na mesma janela MCP9876. Dois retornos envidraçados fecham as laterais ponte/saguão superior, preservando o portal de {q['portal_width_m']:.4f}m. Piso/teto e paredes do túnel prolongados até a reentrância existente da torre, com encontro local documentado de {q['connector_area_m2']:.4f}m² e remoção do tampão transversal prematuro. Seis meshes alteradas, seis componentes novos; núcleo/poço, terrain, SSOT e GAMEPLAY_PROXY B82 intactos. Salva/reaberta; QA de {q['objects_checked']} componentes, {len(q['surface_checks'])} sondagens de piso/teto, {len(q['wall_checks'])} de parede e {len(q['portal_checks'])} do portal. Janela final no mapa completo, terreno visível, sem alterações pendentes. Não certifica percurso/controller ou implantação absoluta; gates históricos, 27 testemunhas e movement_enabled=false preservados. Fonte authoring_source/validation_source B94; produção não promovida. Relatório: docs/LACERDA_CORRIDOR_CLOSURE_B94_2026-10-07.md. Próxima modelagem: demais encontros exteriores, preservando entradas e separando as pendências de circulação.

'''
for name in ('PROJECT_STATUS.md','CODEX_HANDOFF.md','CODEX_STRUCTURE_HANDOFF.md'):
    path=root/'docs'/name;t=path.read_text(encoding='utf8')
    if t.startswith('## 07/10/2026 — B94 ativa:'):
        i=t.find('\n## ',1);t=t[i+1:] if i>=0 else ''
    path.write_text((summary+t).rstrip()+'\n',encoding='utf8')
print(json.dumps({'report':doc.relative_to(root).as_posix(),'revision':'B94','production_ready':False},ensure_ascii=False))
