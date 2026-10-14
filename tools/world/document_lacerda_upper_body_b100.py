"""Resultado persistido da modelagem B100, sem nova investigação documental."""
import json,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[2];out=root/'docs/reports/blender/lacerda-upper-body-b100'
r=json.loads((out/'application.json').read_text());q=json.loads((out/'validation.json').read_text());p=json.loads((out/'presentation.json').read_text());cfg=json.loads((out/'controls.json').read_text())
assert r['reopened'] and q['reopened'] and q['sha256']==r['sha256'] and p['file']==r['file']
assert not p['local_view'] and p['terrain_visible'] and not p['unsaved_changes']
with (root/r['file']).open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==r['sha256']
assert hashlib.sha256((root/'world/geographic-reference.json').read_bytes()).hexdigest()==r['ssot_sha256']
doc=root/'docs/LACERDA_UPPER_BODY_B100_2026-10-08.md'
doc.write_text(f'''# Lacerda — corpo superior e cobertura B100 — 08/10/2026

B99 inspecionada na única janela Blender/MCP9876, sem alterações pendentes:616 componentes conhecidos intactos. Utilizados os vetores/cotas18/19/20/23 e o registro relativo já extraído naB99; não houve nova aquisição, novo SSOT ou nova pesquisa da instalação. B100 salva e reaberta nessa janela, arquivo `{r['file']}`, SHA256 `{r['sha256']}`.

## Modelagem aplicada

- Corpo superior retangular reconstruído como envoltória oca contínua de oito arestas, incluindo o prolongamento técnico voltado à torre. Pequenos rebaixos dos pilares/jambas simplificados, explicitamente candidatos; não extrudir o retângulo do administrativo como edifício inteiro.
- Cobertura existente substituída pelo contorno completo20/321, sem criar uma segunda laje. Platibanda contínua entre os contornos20/321 e20/326; topo relativo+15,40m. A primeira aplicação revelou erro de conversão entre espaço arquitetônico e espaço local do objeto reutilizado: corrigido no gerador e na mesh, preservando o checkpoint preliminar e sem deslocar mapa/objeto.
- Lajes administrativas nos níveis documentais+4,94m(Z75,063008728) e+9,42m(Z79,543008728), diferença4,48m. Teto da galeria continua em+4,00m; não confundir teto com piso do andar. Ala técnica/caixa dos elevadores/escada permanecem sem lajes inferidas. Limite administrativo derivado da parede18/563; não é detalhamento de interiores.
- {len(q['rigid_facade_checks'])} componentes de esquadrias migrados rigidamente para as fachadas correspondentes, preservando dimensões/topologia. Segunda fileira acompanha a diferença entre os níveis dos pavimentos(+0,896667m em relação ao espaçamento legado); peitoril, layout e dimensões das janelas continuam candidatos herdados, sem alegar comprovação as-built. Dezoito aberturas reconciliadas com os vidros existentes.
- Dezesseis tampões coincidentes removidos **antes** da soldagem dos oito trechos, produzindo um corpo único sem divisórias internas acidentais. Nenhum preenchimento para fazer controller passar.
- Quatro componentes novos,159 meshes alteradas(158 partes rígidas e a cobertura),19 peças antigas preservadas fora da apresentação ativa. {len(r['preserved_signatures'])} assinaturas anteriores intactas. Referências substituídas continuam com geometria/material/transform preservados; B99 e snapshots anteriores intactos.

## Verificação na cena reaberta

QA de {q['objects_checked']} componentes de arquitetura, {q['visible_objects_checked']} visíveis. Malhas do escopo sem faces degeneradas, arestas não manifold, winding inconsistente ou duplicatas internas. Erro máximo de aplicação rígida{max(x['control_residual_m'] for x in q['rigid_facade_checks']):.8f}m; alteração máxima de comprimento de aresta{max(x['max_edge_length_change_m'] for x in q['rigid_facade_checks']):.8f}m, compatível com precisão numérica e sem reescala.

{len(q['body_wall_probes'])} sondagens do corpo, {len(q['body_roof_contacts'])} contatos sob a cobertura,18 aberturas com vidro presente e peitoril acima do piso, {len(q['admin_floor_probes'])} sondagens dos pavimentos. Pontes/galerias/túnel anteriores rechecados pela QA comum. Essas verificações não aprovam instalação, CCD da cabine, navegação ou controller.

Capturas reais da única cena: `artifacts/lacerda-live-diagnostic/b100-corpo.png`, `b100-cobertura.png`, `b100-conjunto.png`, `b100-map.png`. Final no mapa completo, terreno visível, sem edição pendente. Não houve npm/build/testes gerais; somente QA delimitada de geometria/persistência.

## Precisão e preservação

Contornos são documentais relativos; implantação absoluta no SSOT continua pendente. Parede0,30m e lajes0,25m são seções candidatas. Migração das esquadrias conserva formas herdadas e não equivale a layout documental aprovado. Campo de precisão/proveniência/replacement_required acompanha os componentes; nenhuma promoção para produção.

B76–B99, SSOT, terreno, duas torres, passarela, túnel, subsolosB99 e GAMEPLAY_PROXY B82 preservados. `LACERDA_VERTICAL=BLOCKED_EXTERNAL_EVIDENCE`,27 testemunhasB80 `UNRESOLVED`, `movement_enabled=false`, `replacement_required=true`. Instalação vertical permanece congelada. Lapa/Dique/Fonte Nova e demais áreas não modificadas. Não representar o exterior candidato como elevador todo certificado ou controller final.
''',encoding='utf8')
provpath=root/'world/data-provenance.json';prov=json.loads(provpath.read_text());resource={'resource_id':'derived:lacerda-upper-body-b100','provider':'Bay of All Saints / modelagem derivada SUCOP2023','dataset':'Corpo19, pavimentos18/19, cobertura20, níveis23; esquadrias legadas candidatas','capture_date':'2026-10-08','bounds':None,'raw_files':[],'derived_files':[r['file'],doc.relative_to(root).as_posix(),(out/'controls.json').relative_to(root).as_posix(),(out/'application.json').relative_to(root).as_posix(),(out/'validation.json').relative_to(root).as_posix()],'derived_objects':[v['object'] for v in r['changes']+r['added']],'usage_class':'PENDENTE_VERIFICACAO','release_status':'REPLACE_BEFORE_RELEASE','purpose':'Reconstrução estrutural relativa do corpo superior/cobertura; não instalação ou implantação certificada','dependencies':cfg['source_ids']+['derived:lacerda-basement-envelope-b99'],'kind':'geometry','accuracy':cfg['accuracy'],'replacement_required':True}
assert all(v in {x['resource_id'] for x in prov['resources']} for v in resource['dependencies'])
old=next((v for v in prov['resources'] if v['resource_id']==resource['resource_id']),None)
if old:old.update(resource)
else:prov['resources'].append(resource)
provpath.write_text(json.dumps(prov,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
summary=f'''## 08/10/2026 — B100 ativa: corpo superior, cobertura e pavimentos

B99 íntegra confirmada; B100 aplicada/salva/reaberta na única janela9876. Corpo oco contínuo com ala técnica, cobertura no contorno completo20, platibanda e lajes+4,94/+9,42.158 peças de esquadria migradas rigidamente;19 referências preservadas,16 tampões internos removidos antes da soldagem. Conversão da cobertura corrigida no gerador/mesh, sem duplicação. QA de {q['objects_checked']} componentes, {len(q['body_wall_probes'])} sondagens de paredes, {len(q['body_roof_contacts'])} da cobertura e18 vãos envidraçados. Implantação/seções/layout de janelas candidatos; não controller ou as-built. B76–B99/SSOT/terreno/torres/passarela/túnel/subsolos/B82/27 testemunhas preservados, movimento falso, sem produção. Relatório docs/LACERDA_UPPER_BODY_B100_2026-10-08.md. Mapa completo aberto, sem edição pendente.

'''
for name in ('PROJECT_STATUS.md','CODEX_HANDOFF.md','CODEX_STRUCTURE_HANDOFF.md'):
 path=root/'docs'/name;s=path.read_text(encoding='utf8')
 if not s.startswith(summary):path.write_text(summary+s,encoding='utf8')
print(json.dumps({'revision':'B100','report':doc.relative_to(root).as_posix(),'production_ready':False},ensure_ascii=False))
