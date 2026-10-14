"""Registra B96 finalizada e limpa somente seu checkpoint intermediário obsoleto."""
import json,hashlib,shutil
from pathlib import Path
root=Path(__file__).resolve().parents[2];out=root/'docs/reports/blender/lacerda-body-b96'
r=json.loads((out/'application.json').read_text());q=json.loads((out/'validation.json').read_text());p=json.loads((out/'presentation.json').read_text())
assert r['reopened'] and q['reopened'] and q['body_checks']['passed'] and q['sha256']==r['sha256']
assert p['file']==r['file'] and not p['local_view'] and p['terrain_visible'] and not p['unsaved_changes']
with (root/r['file']).open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==r['sha256']
assert hashlib.sha256((root/'world/geographic-reference.json').read_bytes()).hexdigest()==r['ssot_sha256']
r['protection_scope']={'initial_alignment_changed':len(r['planned_changes']),'initial_alignment_protected':r['protected_object_count'],'final_changed':len(r['changes']),'final_outside_change_count':r['protected_object_count']-(len(r['changes'])-len(r['planned_changes']))}
q['protection_scope']=r['protection_scope']
(out/'application.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(out/'validation.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
catpath=root/'world/areas/mvp-centro-lacerda/blender-revisions.json';cat=json.loads(catpath.read_text())
checkpoint=(root/r['intermediate_checkpoint']['file']).resolve()
if checkpoint.exists() and shutil.disk_usage(root).free<200_000_000:
    assert checkpoint.parent==(root/'blender').resolve() and checkpoint.name=='salvador_lacerda_r30b96_encontro_corpo_cobertura.blend1'
    with checkpoint.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==r['intermediate_checkpoint']['sha256']
    cleanup={**r['intermediate_checkpoint'],'bytes_removed':checkpoint.stat().st_size,'final_file':r['file'],'final_sha256':r['sha256'],'reason':'Checkpoint automático de B96 em andamento, ainda com sobreposição no topo das laterais. Substituído pela B96 final salva/reaberta/validada; B95 e recuperação da sessão preservadas. Não é alegação de identidade geométrica.'}
    assert (root/r['session_recovery']['recovery_file']).exists()
    (out/'checkpoint-cleanup.json').write_text(json.dumps(cleanup,ensure_ascii=False,indent=2)+'\n',encoding='utf8');checkpoint.unlink()
    r['intermediate_checkpoint']['state']='REMOVED_OBSOLETE_AFTER_FINAL_VALIDATION'
    (out/'application.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    cat.setdefault('automatic_backup_cleanup',[]).append({'file':cleanup['file'],'sha256':cleanup['sha256'],'state':'removed_in_progress_checkpoint_after_final_validation','evidence':'docs/reports/blender/lacerda-body-b96/checkpoint-cleanup.json'})
    catpath.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
dx,_,dz=r['controls']['common_frame_delta'];doc=root/'docs/LACERDA_BODY_JOINTS_B96_2026-10-07.md'
doc.write_text(f'''# Lacerda — encontros do corpo superior B96 — 07/10/2026

B96 finalizada ao vivo, salva e reaberta na mesma janela PID {r['pid']}/MCP9876, cena `SALVADOR | ESBOCO OFICIAL`. Nove meshes alteradas; nenhum objeto novo, reparent ou alteração da geografia. B76–B95 preservadas. Fonte ativa: `{r['file']}`. SHA-256 `{r['sha256']}`.

## Correções e origem

- A face posterior usava a base legada 75,10 no mapper B88 que tomou 75,20 como origem do corpo elevado. O resultado ficou 0,08333m abaixo das outras faces e dos controles verticais. Parede e seis caixilhos foram reconciliados juntos: delta local X {dx:.8f}m, Z {dz:.8f}m, sem mudar tamanho ou relações das janelas. A quina oeste da parede agora pertence ao envelope do edifício, em vez de extrapolar a cobertura pela metade da espessura.
- **Z documental:** prancha23 informa cobertura da passarela +4,00 e cobertura do edifício +14,00. A face inferior da cobertura fica +13,75 pela espessura herdada/candidata 0,25m. As três paredes terminam nessa face inferior; o topo externo da cobertura permanece +14,00.
- **XY:** a quina vem do envelope B86 já usado por cobertura/alas. A reconciliação horizontal é `ADAPT_LOCAL / CANDIDATE_ENVELOPE_CONTINUITY`, para fechar a interface entre peças. Não é novo controle as-built, registro geográfico aceito ou dimensão levantada.
- A inspeção visual detectou faces exteriores coincidentes nos cantos e na faixa do teto, apesar de cada mesh ser manifold. A posterior foi recortada nos limites internos das laterais e na face inferior da cobertura; as duas laterais também terminam sob a cobertura. Juntas de contato entre peças foram preservadas, sem acrescentar volumes para esconder a cintilação. Janela e passagem não foram tampadas. Espessuras continuam candidatas.

## Conferência

- {q['objects_checked']} componentes comparados às assinaturas; {q['visible_objects_checked']} visíveis sem faces degeneradas, arestas não manifold, winding inconsistente ou faces duplicadas internas no escopo auditado.
- Seis janelas mantêm a mesma translação comum e a mesma topologia; máximo erro numérico {max(v['max_common_delta_error_m'] for v in q['body_checks']['common_group_translation']):.8f}m.
- Trinta sondagens sobre a espessura da posterior confirmam cobertura real acima dela. Duas junções laterais conferidas por contato e raio físico. Tangência é `EXPECTED_CONTACT`, não defeito automático.
- {len(q['surface_checks'])} sondagens de piso/teto dos encontros, {len(q['wall_checks'])} de parede e {len(q['portal_checks'])} de portal. Os fechamentos B94/B95 permanecem aprovados em seu escopo local. Isso não aprova o percurso completo, CCD da cabine ou controller.
- Terrain, SSOT e GAMEPLAY_PROXY B82 intactos. Poço, cabine, guias históricas, demais regiões e decoração não alterados. Prova visual real: `artifacts/lacerda-live-diagnostic/b96-rear-roof.png`; mapa completo: `b96-map.png`.
- A janela terminou com terreno visível, `local_view=false`, `unsaved_changes=false`. A sessão inicialmente não salva foi preservada em `{r['session_recovery']['recovery_file']}`. Os 603 componentes comparados antes da modelagem não apresentavam diferença geométrica contra B95; a recuperação não foi descartada por essa constatação.

## Espaço e preservação

Removido somente o backup automático pré-checkpoint final B92 após comparar geometria/transform/material de 542 componentes com a B92 oficial: zero diferenças. A B92 oficial permanece intacta; não houve alegação de identidade binária de todos os metadados. Evidência: `backup-comparison.json`/`space-recovery.json`.

Checkpoints de B96 em andamento foram substituídos após validar seus sucessores. O último backup temporário, se removido por espaço, tem hash e motivo em `checkpoint-cleanup.json`; ele ainda continha a sobreposição de topo corrigida. B95, B96 final e cópia de recuperação permanecem disponíveis. Não apagar revisões oficiais ou evidências.

`LACERDA_VERTICAL = BLOCKED_EXTERNAL_EVIDENCE`; `movement_enabled = false`; `27 testemunhas B80 = UNRESOLVED / PRESERVED`; `GAMEPLAY_PROXY B82 = PRESERVED / replacement_required: true`; `EXPANDED_MAP = GREYBOX`; `production_ready = false`.

Antes/depois e controles: `docs/reports/blender/lacerda-body-b96/{{before,mutation-journal,application,joint-finalization,roof-side-finalization,validation,presentation}}.json`. Implantação absoluta, acesso inferior ao terreno e guardas/interiores continuam candidatos ou pendentes conforme B93–B95; não foram escondidos com geometria fictícia.

Próximo cluster de modelagem: acesso superior e guardas dos vestíbulos, distinguindo áreas intencionalmente abertas de defeitos, antes de layout fino de janelas ou expansão territorial.
''',encoding='utf8')
provpath=root/'world/data-provenance.json';prov=json.loads(provpath.read_text())
resource={'resource_id':'derived:lacerda-upper-body-b96','provider':'Bay of All Saints / reconciliação autoral derivada SUCOP','dataset':'Encontros posteriores e laterais do corpo superior/cobertura','capture_date':'2026-10-07','bounds':None,'raw_files':[],'derived_files':[r['file'],doc.relative_to(root).as_posix(),'docs/reports/blender/lacerda-body-b96/application.json','docs/reports/blender/lacerda-body-b96/validation.json'],'usage_class':'PENDENTE_VERIFICACAO','release_status':'REPLACE_BEFORE_RELEASE','purpose':'Coerência do envelope candidato e cotas verticais relativas; sem certificação as-built, implantação ou controller','dependencies':['derived:lacerda-upper-enclosure-b95','source:lacerda-issue22-sucop-17','source:lacerda-issue22-sucop-23'],'kind':'geometry','accuracy':'DOCUMENT_RELATIVE_LEVELS_CANDIDATE_UPPER_ENVELOPE','replacement_required':True}
old=next((v for v in prov['resources'] if v['resource_id']==resource['resource_id']),None)
if old:old.update(resource)
else:prov['resources'].append(resource)
ids={v['resource_id'] for v in prov['resources']};assert all(v in ids for v in resource['dependencies'])
provpath.write_text(json.dumps(prov,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
summary=f'''## 07/10/2026 — B96 ativa: corpo superior/cobertura sem sobreposição exterior

B96 finalizada/reaberta na mesma janela MCP9876: posterior e seis caixilhos reconciliados juntos com envelope candidato/cotas; posterior e duas laterais terminam sob a cobertura, com cantos em contato sem faces exteriores coincidentes. Nove meshes alteradas, nenhum objeto novo; não muda poço, mapa, terreno ou SSOT. QA de {q['objects_checked']} componentes, {q['visible_objects_checked']} visíveis, 30 sondagens de cobertura posterior, dois cantos e encontros B94/B95 rechecados. Vistas reais sem a cintilação observada no estágio intermediário; mapa completo/terreno visíveis, memória sem edição pendente. B76–B95, recuperação B95, GAMEPLAY_PROXY B82, 27 testemunhas e bloqueio histórico preservados. X é ADAPT_LOCAL/envelope candidato, Z vem dos níveis +4/+14 da prancha23 e espessura herdada; não as-built/implantação/controller. Backups automáticos obsoletos removidos com hashes/evidência; nenhum snapshot oficial apagado. Relatório: docs/LACERDA_BODY_JOINTS_B96_2026-10-07.md. Próxima modelagem: acesso superior/guardas dos vestíbulos, sem fachadas finas ou expansão.

'''
for name in ('PROJECT_STATUS.md','CODEX_HANDOFF.md','CODEX_STRUCTURE_HANDOFF.md'):
    path=root/'docs'/name;t=path.read_text(encoding='utf8')
    if t.startswith('## 07/10/2026 — B96 ativa:'):
        i=t.find('\n## ',1);t=t[i+1:] if i>=0 else ''
    path.write_text((summary+t).rstrip()+'\n',encoding='utf8')
print(json.dumps({'report':doc.relative_to(root).as_posix(),'revision':'B96','free_bytes':shutil.disk_usage(root).free,'production_ready':False},ensure_ascii=False))
