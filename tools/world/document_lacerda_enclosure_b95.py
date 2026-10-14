"""Documenta a reconciliação superior B95 validada na sessão visível."""
import json,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[2];out=root/'docs/reports/blender/lacerda-enclosure-b95'
r=json.loads((out/'application.json').read_text());q=json.loads((out/'validation.json').read_text());p=json.loads((out/'presentation.json').read_text());enclosure=json.loads((out/'enclosure-before.json').read_text())
assert r['reopened'] and q['reopened'] and q['sha256']==r['sha256']
assert p['file']==r['file'] and not p['local_view'] and p['terrain_visible'] and not p['unsaved_changes']
with (root/r['file']).open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==r['sha256']
assert hashlib.sha256((root/'world/geographic-reference.json').read_bytes()).hexdigest()==r['ssot_sha256']
doc=root/'docs/LACERDA_UPPER_ENCLOSURE_B95_2026-10-07.md'
text=f'''# Lacerda — limites e encontros superiores B95 — 07/10/2026

B95 aplicada e reaberta na mesma janela Blender PID {r['pid']}, MCP9876, cena `SALVADOR | ESBOCO OFICIAL`. B76–B94 preservadas; authoring_source/validation_source agora apontam explicitamente para B95. Produção e gameplay anteriores não promovidos.

## Causa comum e correções

O piso superior foi reconstruído pelo contorno documental na B88, mas partes da envoltória conservaram limites do layout anterior. A B94 adicionou os dois retornos corretos sem separar os seis componentes antigos sobrepostos.

- **Circulação norte:** a parede envidraçada avançava até X local 5,50. A planta17 separa a circulação da área `SAÍDA 20,10m²` na quina X {r['controls']['north_glazing_end'][0]:.8f}, Y {r['controls']['north_glazing_end'][1]:.8f}. A parede foi recortada nesse limite, sem esticar caixilhos, deslocar o piso ou fechar o acesso aberto.
- **Circulação sul:** o mesmo erro terminava em X 5,50; a quina documental da área `ENTRADA 15,17m²` está em X {r['controls']['south_glazing_end'][0]:.8f}, Y {r['controls']['south_glazing_end'][1]:.8f}. Recorte no limite correspondente. As áreas de entrada/saída não foram tratadas como buracos a preencher.
- **Verga ponte/saguão:** o elemento antigo ocupava Z73,50–75,00, ultrapassando a cobertura atual. Reconstruído pelos endpoints CAD do portal e pelas faces da cobertura: Z {r['controls']['header_levels'][0]:.8f}–{r['controls']['header_levels'][1]:.8f}. Espessura 0,18m continua candidata/herdada. A passagem permanece livre abaixo da cobertura.
- **Retornos antigos:** seis componentes (duas paredes, dois lambris e dois rodapés) preservados sem alterar geometria, transform ou materiais, agora `SUPERSEDED_REFERENCE` fora da apresentação ativa. Sua substituição pelos retornos B94 é explícita. Nenhum objeto apagado, reparentado ou duplicado.

Três meshes alteradas, seis referências separadas e nenhum objeto novo. Controles relativos derivados da fonte catalogada SUCOP17 e do mesmo registro B88; não foi criado segundo SSOT. Não houve ajuste de datum, poço, cabine, terreno, ruas ou expansão.

## QA e limites da conclusão

- {q['objects_checked']} componentes comparados às assinaturas B88–B95; {q['visible_objects_checked']} visíveis sem faces degeneradas, arestas não manifold, winding inconsistente ou faces duplicadas no escopo auditado.
- Limites das duas paredes conferidos contra as quinas documentais: maior residual numérico {max(v['residual_m'] for v in q['enclosure_limits']):.8f}m. Mede consistência de aplicação, não precisão de levantamento.
- {len(q['surface_checks'])} sondagens de piso/teto, {len(q['wall_checks'])} de parede e {len(q['portal_checks'])} verificações do portal repetidas na B95, incluindo a nova verga. {len(q['structural_contacts'])} contatos verticais sem gap acima da tolerância numérica.
- Auditoria anterior dos limites laterais da ponte e da galeria: {len(enclosure['samples'])} raios horizontais, {len(enclosure['unclosed'])} pontos sem hit. Essas envoltórias não foram alteradas nesta rodada. Essa amostragem não comprova toda a arquitetura nem toda a navegação.
- {q['protected_before_application']} objetos protegidos durante a aplicação; {len(q['protected_scoped_after_reopen'])} assinaturas geométricas do inventário local preservadas após reabrir, incluindo os seis componentes agora arquivados cuja visibilidade mudou deliberadamente.
- Terrain, SSOT e GAMEPLAY_PROXY B82 geometricamente intactos. Bindings históricos afetados preservados e invalidados explicitamente; não foram regenerados ou aprovados como controller.
- Arquivo salvo e reaberto, hash conferido. Vistas reais em `artifacts/lacerda-live-diagnostic/b95-*.png`; janela final com mapa completo, terreno visível e nenhuma alteração pendente.

Guardas dos acessos, subdivisões interiores e interface do piso inferior com o terreno não foram aprovadas nesta revisão. Não confundir abertura arquitetônica correta com percurso completo seguro para personagem. As dimensões de instalação continuam congeladas e a implantação absoluta mantém a pendência B93.

`LACERDA_VERTICAL = BLOCKED_EXTERNAL_EVIDENCE`; `movement_enabled = false`; `27 testemunhas B80 = UNRESOLVED / PRESERVED`; `GAMEPLAY_PROXY B82 = PRESERVED / replacement_required: true`; `EXPANDED_MAP = GREYBOX`; `production_ready = false`.

Fonte ativa: `{r['file']}`. SHA-256 `{r['sha256']}`.

Antes/depois, controles e hashes: `docs/reports/blender/lacerda-enclosure-b95/{{before,mutation-journal,application,validation,presentation}}.json`. Próxima modelagem: conferir os encontros exteriores do corpo antigo/alas e os limites dos acessos, sem usar acabamento para esconder divergência nem reabrir investigação dos ascensores.
'''
doc.write_text(text,encoding='utf8')
provpath=root/'world/data-provenance.json';prov=json.loads(provpath.read_text())
resource={'resource_id':'derived:lacerda-upper-enclosure-b95','provider':'Bay of All Saints / modelagem autoral derivada SUCOP','dataset':'Limites das circulações superiores e portal da ponte','capture_date':'2026-10-07','bounds':None,'raw_files':[],'derived_files':[r['file'],doc.relative_to(root).as_posix(),'docs/reports/blender/lacerda-enclosure-b95/mutation-journal.json','docs/reports/blender/lacerda-enclosure-b95/application.json','docs/reports/blender/lacerda-enclosure-b95/validation.json'],'usage_class':'PENDENTE_VERIFICACAO','release_status':'REPLACE_BEFORE_RELEASE','purpose':'Reconciliação arquitetônica relativa; não certifica implantação, instalação, guarda de acessos ou controller','dependencies':['derived:lacerda-corridor-closure-b94','source:lacerda-issue22-sucop-17'],'kind':'geometry','accuracy':'DOCUMENT_CONTOURS_INHERITED_THICKNESS','replacement_required':True}
old=next((v for v in prov['resources'] if v['resource_id']==resource['resource_id']),None)
if old:old.update(resource)
else:prov['resources'].append(resource)
ids={v['resource_id'] for v in prov['resources']};assert all(v in ids for v in resource['dependencies'])
provpath.write_text(json.dumps(prov,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
summary=f'''## 07/10/2026 — B95 ativa: limites das circulações superiores

B95 continua B94: duas paredes envidraçadas recortadas nas quinas documentais da circulação/entrada/saída da planta17, sem esticar caixilhos; verga do portal reconciliada com a cobertura +4,00m; seis peças sobrepostas do retorno antigo preservadas como SUPERSEDED_REFERENCE. Três meshes alteradas, nenhum objeto novo. Salva/reaberta na mesma janela MCP9876, mapa completo/terreno visíveis e memória sem edição pendente. QA: {q['objects_checked']} componentes, {q['visible_objects_checked']} visíveis, {len(q['surface_checks'])} sondagens de piso/teto, {len(q['wall_checks'])} de parede e {len(q['portal_checks'])} do portal. Envoltórias ponte/galeria já tinham {len(enclosure['samples'])} sondagens sem abertura detectada; não preencher áreas de entrada/saída intencionalmente abertas. SSOT, terreno, proxy B82, B76–B94, 27 testemunhas e gates preservados. movement_enabled=false; sem produção. Relatório: docs/LACERDA_UPPER_ENCLOSURE_B95_2026-10-07.md. Próxima modelagem: corpo antigo/alas e limites dos acessos; não reabrir instalação dos ascensores.

'''
for name in ('PROJECT_STATUS.md','CODEX_HANDOFF.md','CODEX_STRUCTURE_HANDOFF.md'):
    path=root/'docs'/name;t=path.read_text(encoding='utf8')
    if t.startswith('## 07/10/2026 — B95 ativa:'):
        i=t.find('\n## ',1);t=t[i+1:] if i>=0 else ''
    path.write_text((summary+t).rstrip()+'\n',encoding='utf8')
print(json.dumps({'report':doc.relative_to(root).as_posix(),'revision':'B95','production_ready':False},ensure_ascii=False))
