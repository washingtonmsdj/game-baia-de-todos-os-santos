"""Documenta somente a B98 persistida e verificada na janela visível."""
import json,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[2];out=root/'docs/reports/blender/lacerda-completion-b98'
r=json.loads((out/'application.json').read_text());q=json.loads((out/'validation.json').read_text());p=json.loads((out/'presentation.json').read_text());cfg=json.loads((out/'controls.json').read_text())
assert r['reopened'] and q['reopened'] and q['sha256']==r['sha256']
assert not p['local_view'] and p['terrain_visible'] and not p['unsaved_changes'] and p['file']==r['file']
with (root/r['file']).open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==r['sha256']
assert hashlib.sha256((root/'world/geographic-reference.json').read_bytes()).hexdigest()==r['ssot_sha256']
doc=root/'docs/LACERDA_SUPERIOR_COMPLETION_B98_2026-10-07.md'
doc.write_text(f'''# Lacerda — reconciliação estrutural superior B98 — 07/10/2026

## Cena utilizada e preservação das modificações

Inspeção da janela existente PID{r['pid']}/MCP9876: B97 salva, hash igual ao catálogo, sem edição pendente; 605 componentes comparados, nenhuma divergência de geometria/transform/material. Não houve recarga nem substituição de trabalho do usuário antes da alteração. Depois da modelagem, B98 salva e reaberta na mesma janela, hash `{r['sha256']}`; arquivo `{r['file']}`. B76–B97 preservadas, SSOT inalterado.

## Correções efetivas

- A frente térrea anterior conservava seis pilares, cinco vãos e esquadrias/persianas na linha X quase constante, extrapolando os limites das circulações documentais. Foi substituída na apresentação ativa por quatro apoios derivados dos contornos estruturais da prancha17: curvas1751/1758/1738/1743. Agora acompanha a linha oblíqua da frente e os intervalos reais do desenho, em vez de escalar a frente antiga inteira.
- Três vãos entre os apoios reconstruídos: dois volumes simples de porta de rolo nas posições indicadas na17 e um vão central aberto. Cabeceiras segmentadas encostam nos apoios, sem uma barra atravessando as passagens. Não cria salão/interior novo por dedução de área.
- Apoios/cabeceiras reconciliados com piso70,123008728 e face inferior da cobertura73,873008728. Topo documental da cobertura +4,00m continua preservado. Contato entre peças é esperado, não interseção defeituosa automaticamente.
- A marquise antiga estava acima da cobertura em0,957m e mantinha uma extensão herdada incompatível com o conjunto atual. Preservada integralmente como referência substituída; não foi inventada projeção nova sem controle documental.
- Nove meshes novas; {len(r['archived'])} peças antigas preservadas com geometria/transform/material intactos e fora da apresentação ativa. Sem deslocar torre, geografia, terreno, Hero asset inteiro, poço, cabine ou B82. Bindings atingidos ficam invalidados/desabilitados, sem duplicação de collider.

## Precisão e limite da conclusão

XY usa vetores/cotas já catalogados da17 e o referencial arquitetônico relativo B88. Não constitui registro absoluto aceito no SSOT. Pequenos rebaixos das extremidades dos pilares foram simplificados para estrutura jogável e estão documentados nos controles. Não são seção de concreto/armadura ou as-built certificados.

Abertura vertical2,69m é candidata herdada das folhas antigas, não cota documental. Espessura de cobertura0,25m também herdada/candidata. As portas de rolo são massas simples: montagem e subdivisão fina não aprovadas. Todos os componentes têm `replacement_required=true`, `production_ready=false`, fonte/controle/proveniência registrados. Nenhuma medida desconhecida foi apresentada como real comprovada.

## Verificação

- {q['objects_checked']} componentes de arquitetura conferidos; {q['visible_objects_checked']} visíveis sem face degenerada/aresta não manifold/winding inconsistente/duplicata interna no escopo auditado. {q['preserved_component_signatures']} assinaturas anteriores intactas.
- Nove contornos/cotas conferidos contra os controles, máximo residual numérico {max(v['max_document_control_residual_m'] for v in q['front_control_residuals']):.8f}m. Esse residual prova aplicação relativa do controle, não erro real de implantação/as-built.
- {len(q['surface_checks'])} sondagens de superfícies, {len(q['wall_checks'])} de fechamentos e {len(q['portal_checks'])} de portal; interfaces B94–B97 preservadas.
- Cápsula raio0,30/altura1,80/skin0,015: CCD conservativo local do interior do novo vão, {len(q['local_capsule_ccd']['intervals'])} intervalos aprovados contra as nove peças. Apoio medido no piso real. Não é simulação de gravidade/controller, validação da praça inteira, acesso à cabine ou trajeto Tomé–Mercado.
- Capturas reais da mesma cena: `artifacts/lacerda-live-diagnostic/b98-frente.png`, `b98-conjunto.png`, `b98-map.png`. Janela final no mapa completo, terreno visível, sem edição pendente.

## Pendências que não podem ser declaradas finalizadas

`LACERDA_VERTICAL=BLOCKED_EXTERNAL_EVIDENCE`; 27 testemunhas B80 `UNRESOLVED`; `movement_enabled=false`; GAMEPLAY_PROXY B82 preservado e separado. Interface inferior/datum com terreno continua NEEDS_REVIEW, com divergência3,857m documentada naB93. Instalação atual depende de as-built/processoSEMOB151228/2023/Contrato008/2023 ou levantamento equivalente. Esta rodada não reabre essa investigação, não deforma terreno e não promove produção.

A frente superior foi reconciliada nesta rodada. O elevador completo **não está arquitetonicamente certificado nem liberado para controller**; chamá-lo de finalizado apagaria pendências reais. Lapa, Dique, Fonte Nova e demais regiões não alteradas. Auditoria aplicada em `docs/reports/blender/lacerda-completion-b98/`.
''',encoding='utf8')
provpath=root/'world/data-provenance.json';prov=json.loads(provpath.read_text());resource={'resource_id':'derived:lacerda-upper-completion-b98','provider':'Bay of All Saints / modelagem derivada SUCOP2023','dataset':'Frente térrea oblíqua, apoios e vãos da planta17 / níveis23','capture_date':'2026-10-07','bounds':None,'raw_files':[],'derived_files':[r['file'],doc.relative_to(root).as_posix(),(out/'controls.json').relative_to(root).as_posix(),(out/'application.json').relative_to(root).as_posix(),(out/'validation.json').relative_to(root).as_posix()],'derived_objects':[v['object'] for v in r['added']],'usage_class':'PENDENTE_VERIFICACAO','release_status':'REPLACE_BEFORE_RELEASE','purpose':'Reconciliação estrutural relativa da frente superior; não certifica implantação/instalação/controller','dependencies':['derived:lacerda-upper-vestibules-b97','source:lacerda-issue22-sucop-17','source:lacerda-issue22-sucop-23'],'kind':'geometry','accuracy':'DOCUMENT_RELATIVE_CONTOURS_CANDIDATE_HEIGHT','replacement_required':True}
assert all(v in {x['resource_id'] for x in prov['resources']} for v in resource['dependencies'])
old=next((v for v in prov['resources'] if v['resource_id']==resource['resource_id']),None)
if old:old.update(resource)
else:prov['resources'].append(resource)
provpath.write_text(json.dumps(prov,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
summary=f'''## 07/10/2026 — B98 ativa: frente superior reconciliada

B97 inspecionada intacta/sem alterações pendentes; B98 modelada/salva/reaberta na mesma janela9876. Frente antiga reta/cinco vãos substituída na apresentação por quatro apoios oblíquos CAD17, dois fechamentos de rolo e vão central; nove meshes novas e68 referências antigas preservadas. Marquise legada deslocada separada da apresentação, sem inventar projeção nova. QA de {q['objects_checked']} componentes e CCD local da frente, sem aprovação do controller. Altura de abertura/seções/implantação continuam candidatas; B76–B97, SSOT, proxyB82,27 testemunhas e movement_enabled=false preservados. Relatório docs/LACERDA_SUPERIOR_COMPLETION_B98_2026-10-07.md. Não afirmar elevador completo finalizado: instalação vertical bloqueada e datum/interface inferior continuam pendentes; sem produção.

'''
for name in ('PROJECT_STATUS.md','CODEX_HANDOFF.md','CODEX_STRUCTURE_HANDOFF.md'):
 path=root/'docs'/name;text=path.read_text(encoding='utf8')
 if not text.startswith(summary):path.write_text(summary+text,encoding='utf8')
print(json.dumps({'revision':'B98','report':doc.relative_to(root).as_posix(),'production_ready':False},ensure_ascii=False))
