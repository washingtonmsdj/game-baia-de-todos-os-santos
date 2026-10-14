"""Registra somente revisão B99 salva, reaberta e inspecionada ao vivo."""
import json,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[2];out=root/'docs/reports/blender/lacerda-structure-b99'
r=json.loads((out/'application.json').read_text());q=json.loads((out/'validation.json').read_text());p=json.loads((out/'presentation.json').read_text());cfg=json.loads((out/'controls.json').read_text())
assert r['reopened'] and q['reopened'] and r['sha256']==q['sha256']
assert not p['local_view'] and p['terrain_visible'] and not p['unsaved_changes'] and p['file']==r['file']
with (root/r['file']).open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==r['sha256']
assert hashlib.sha256((root/'world/geographic-reference.json').read_bytes()).hexdigest()==r['ssot_sha256']
acquisition=json.loads((out/'drawings-acquisition.json').read_text())
doc=root/'docs/LACERDA_BASEMENT_STRUCTURE_B99_2026-10-08.md'
doc.write_text(f'''# Lacerda — corpo dos subsolos da Cidade Alta B99 — 08/10/2026

## Base e causa comprovada da divergência

B98 inspecionada na única janela Blender PID{r['pid']}/MCP9876, sem edição pendente ou divergência nas614 assinaturas conhecidas. A B88 tinha criado `B88 | cidade alta | alas estruturais sob edifício` como prisma sólido retangular do contorno do andar superior: X[-10,198994637;5,50], Y[-5,502903938;5,455273628], Z[60,383007;69,793007]. A torre candidata terminava em X=-12,358242, deixando2,159247m até esse bloco. Não é prova de dimensão do poço; é uma incompatibilidade entre dois envelopes do modelo.

As plantas15/16 e o corte23 documentam um contorno de subsolo diferente do pavimento de cima, com recuos e ligação ao corpo antigo. Repetir a planta superior por extrusão era a causa do bloco indevido. Nenhuma torre foi movida para eliminar esse intervalo.

## Fontes recuperadas e registro

Recuperadas seis pranchas oficiais presentes no inventário SUCOP já catalogado:14(subsolo03/-19,85),15(subsolo02/-9,74),16(subsolo01/-4,97),18(1ºandar/+4,94),19(2ºandar/+9,42),20(cobertura/+14,00). PDFs e vistas integrais inspecionados; URL/hash/arquivo bruto/classificação centralizados em `world/data-provenance.json` e `drawings-acquisition.json`. Fonte oficial não autoriza automaticamente redistribuição: permanecem `DEV_REFERENCE_ONLY`.

Três quinas não colineares do mesmo imóvel permanente do levantamento-base registram cada folha contra a17; quarta quina verifica independentemente a transformação. Escala vem das cotas impressas usadas naB88, não da medida de pixels ou do carimbo conflitante. Ajuste entre exportações CAD limitado a similaridade, desvios documentados em `controls.json`; máximo residual de controle/checkpoint {max(max(c['residual_m'] for c in v['controls']) if v['controls'] else 0 for v in cfg['registration'].values()):.6f}m, sem alterar o SSOT.

Esse registro é **prancha→prancha**, subordinado ao referencial arquitetônico relativo já adotado; não corresponde a três controles físicos aceitos na cena/SSOT. Implantação absoluta continua pendente. Não usar o residual documental como certificado geográfico.

## Alterações reais da cena

- Substituído na apresentação ativa o bloco sólido retangular por envoltória **oca** nos recuos nativos da16; limites relativos X[-18,311844;-2,000931], Y[-5,521302;5,432198]. O objeto antigo continua íntegro como `SUPERSEDED_REFERENCE`, sem eliminação de malha.
- Parede contínua entre os níveis relativos -9,74 e face inferior da laje superior -0,33: Z60,383008728→69,793008728. Espessura uniforme0,15m é **candidata**, não levantamento de todas as paredes. O envelope16 foi conferido na15 em14 quinas; outras três correspondências continuam `NEEDS_REVIEW`, incluindo a busca documental com residual0,8703m. A extrapolação do contorno16 ao subsolo02 é **aproximada**, não as-built.
- Laje no nível -4,97 somente na superfície cinza documentada da16(curva335), respeitando recortes. Área86,4608m²; espessura0,25m candidata. O núcleo hachurado fica sem preenchimento novo. Não cria piso no poço ou mecanismos de elevador.
- Duas meshes novas e um objeto antigo preservado fora da apresentação ativa. As614 assinaturas anteriores, terreno, SSOT e GAMEPLAY_PROXY B82 intactos. Bindings atingidos desabilitados se existentes; não foi criado collider por cópia integral da geometria visual.
- Extensões do muro para a encosta e casa de máquinas antiga a-19,85 não foram inferidas por extrusão. As folhas18/19/20 ficam catalogadas para reconciliação posterior do edifício; não foram aplicadas automaticamente em fachadas.

## Verificação e limites

B99 salva em `{r['file']}`, hash `{r['sha256']}`, reaberta na mesma janela. QA de {q['objects_checked']} componentes de arquitetura; {q['visible_objects_checked']} visíveis sem faces degeneradas/arestas não manifold/winding inconsistente/duplicatas internas no escopo. Envoltória exterior/interior sem cruzamento 2D detectado; controle relativo máximo residual{q['basement_contour_residual_m']:.8f}m. {len(q['wall_closure_rays'])} sondagens de parede e {len(q['floor_support_probes'])} sondagens da nova laje. Núcleo hachurado conferido sem preenchimento. Cruzamentos de superfície com o núcleo existente:{q['existing_core_surface_overlap_pairs']} ({q['existing_core_surface_overlap_classification']}); não equivale a CCD da instalação.

Encontros da ponte, galeria e túnel B94/B95 rechecados pelas sondagens comuns. Contato com a laje superior é relatado por ponto, sem fechar automaticamente quinas/aberturas não comprovadas. Contact-only não vira penetração automaticamente.

Capturas reais da cena: `artifacts/lacerda-live-diagnostic/b99-subsolos.png`, `b99-conjunto.png`, `b99-map.png`. Janela final com mapa/terreno completos, sem edição pendente. Não há teste npm/build/engine; essa QA é de geometria e persistência, **não aprovação de controller/percurso**.

## Gates preservados

`LACERDA_VERTICAL=BLOCKED_EXTERNAL_EVIDENCE`,27 testemunhasB80 `UNRESOLVED`, `movement_enabled=false`; B82 `GAMEPLAY_PROXY/replacement_required=true` separado. B76–B98 preservadas. Interface inferior/datum3,857m daB93 e registro absoluto continuam pendentes. Não foram feitas novas buscas da instalação; contratoSEMOB151228/2023/008/2023 ou levantamento equivalente continua sendo evidência externa necessária.

O corpo de subsolo foi corrigido estruturalmente nesta revisão. Não declarar elevador todo finalizado/as-built nem promover produção. Lapa/Dique/Fonte Nova/terreno/ruas não alterados. Próxima reconciliação exterior: corpo superior/cobertura segundo18/19/20, distinguindo teto da galeria(+4,00) e primeiro pavimento(+4,94), sem escalar indiscriminadamente esquadrias ou o asset inteiro.
''',encoding='utf8')
provpath=root/'world/data-provenance.json';prov=json.loads(provpath.read_text());resource={'resource_id':'derived:lacerda-basement-envelope-b99','provider':'Bay of All Saints / modelagem derivada SUCOP2023','dataset':'Contorno do subsolo16 / conferência15 / níveis23','capture_date':'2026-10-08','bounds':{'frame':'B88_DOCUMENT_RELATIVE_NOT_ABSOLUTE_SSOT','x':[-18.31184439113541,-2.000930983193941],'y':[-5.521301955630671,5.432198101174975]},'raw_files':[],'derived_files':[r['file'],doc.relative_to(root).as_posix(),(out/'controls.json').relative_to(root).as_posix(),(out/'application.json').relative_to(root).as_posix(),(out/'validation.json').relative_to(root).as_posix()],'derived_objects':[v['object'] for v in r['added']],'usage_class':'PENDENTE_VERIFICACAO','release_status':'REPLACE_BEFORE_RELEASE','purpose':'Envoltória estrutural candidata; preserva núcleo/SSOT e bloqueio histórico','dependencies':cfg['source_ids'],'kind':'geometry','accuracy':'DOCUMENT_RELATIVE_CONTOUR_APPROXIMATE_SECTION_AND_LOWER_EXTRUSION','replacement_required':True}
assert all(v in {x['resource_id'] for x in prov['resources']} for v in resource['dependencies'])
old=next((v for v in prov['resources'] if v['resource_id']==resource['resource_id']),None)
if old:old.update(resource)
else:prov['resources'].append(resource)
provpath.write_text(json.dumps(prov,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
summary=f'''## 08/10/2026 — B99 ativa: subsolos e corpo da Cidade Alta

B98 inspecionada intacta na janela9876; B99 modelada/salva/reaberta na mesma instância. Bloco sólido baseado no andar de cima substituído por envoltória oca com recuos da16 e laje cinza documentada -4,97; duas meshes novas, antigo preservado. Seis pranchas oficiais recuperadas/catalogadas. Registro relativo entre folhas, seção0,15/laje0,25 e extrusão inferior candidatas; três correspondências15 NEEDS_REVIEW. QA de {q['objects_checked']} componentes, {len(q['wall_closure_rays'])} sondagens de fechamento e {len(q['floor_support_probes'])} da laje;614 assinaturas anteriores preservadas. Núcleo/terreno/SSOT/B82/B76–B98/27 testemunhas/bloqueio histórico intactos, movimento falso, sem produção. Relatório docs/LACERDA_BASEMENT_STRUCTURE_B99_2026-10-08.md. Próxima reconciliação exterior: corpo superior18/19/20, teto galeria+4 versus andar+4,94; não instalação ou expansão.

'''
for name in ('PROJECT_STATUS.md','CODEX_HANDOFF.md','CODEX_STRUCTURE_HANDOFF.md'):
 path=root/'docs'/name;s=path.read_text(encoding='utf8')
 if not s.startswith(summary):path.write_text(summary+s,encoding='utf8')
print(json.dumps({'revision':'B99','report':doc.relative_to(root).as_posix(),'production_ready':False},ensure_ascii=False))
