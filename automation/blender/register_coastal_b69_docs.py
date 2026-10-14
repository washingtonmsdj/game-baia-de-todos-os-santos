"""Registra B68/B69, prova de reabertura e pendências estruturais; não muda a cena."""
import json,hashlib,shutil
from pathlib import Path
r=Path(__file__).resolve().parents[2]
backup=r/'artifacts/waterfront/b69-metadata-before';backup.mkdir(parents=True,exist_ok=True)
paths=['docs/PROJECT_STATUS.md','docs/CODEX_HANDOFF.md','docs/WATERFRONT_FIDELITY_REVIEW.md','world/areas/mvp-centro-lacerda/blender-revisions.json','world/areas/mvp-centro-lacerda/road-corrections.json']
for path in paths:
 p=r/path;dst=backup/p.name
 if not dst.exists():dst.write_bytes(p.read_bytes())
rp=r/'docs/reports/blender/pier_land_contacts_r30b69.json';report=json.loads(rp.read_text(encoding='utf8'))
vp='docs/reports/blender/pier_land_contacts_r30b69_validation.json';validation=json.loads((r/vp).read_text(encoding='utf8'))
assert validation['source_reopened'] and validation['sampled_gap_coverage_passed']
src=report['source_after'];assert hashlib.sha256((r/src['file']).read_bytes()).hexdigest()==src['sha256']
report.update(source_reopened=True,validation_evidence=vp,local_geometry_checks_passed=True,sampled_gap_coverage_passed=True)
report['pending']=['Desnível do píer 609043799 de até 1,4774 m; sem ligação caminhável aprovada','Níveis absolutos água/cais/decks e fundações reais não certificados','Relevo artificial, encerramentos/continuidade das vias e cobertura urbana da região ainda pendentes','Fotografia regional capturada não enquadra os encontros dos dois píeres; passe visual específico pendente']
report['algorithm']='Subtração convexa XY das faces existentes de solo e água; CDT local, elimina resíduos de área projetada <1e-6 m2. Não usa área 3D para medir sobreposição XY.'
report['water_overlap_measurement']='Zero área projetada somada de triângulos com centroide dentro da água; não é prova integral de interseção poligonal.'
rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
cp=r/paths[3];cat=json.loads(cp.read_text(encoding='utf8'))
for entry in [cat['validation_source']]+cat['revisions']:
 if entry['file']==src['file']:entry.update(source_reopened=True,validation_evidence=vp,local_geometry_checks_passed=True,sampled_gap_coverage_passed=True)
cp.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
oldrp=r/'docs/reports/blender/pier_land_contacts_r30b68.json';old=json.loads(oldrp.read_text(encoding='utf8'))
old.update(source_reopened=True,validation_evidence='docs/reports/blender/pier_land_contacts_r30b68_validation.json',sampled_gap_coverage_passed=False,superseded_by=src['file'])
oldrp.write_text(json.dumps(old,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
capture=Path(r'C:\Users\TONECOS\AppData\Local\Ordax\DevAgent\artifacts\bay-of-all-saints\692ac4f57f3445bb8852d745df64ea0f\blender-live.png')
capture_dest=r/'artifacts/waterfront/b69-regiao-pendente.png';shutil.copyfile(capture,capture_dest)
coverage=json.loads((r/'docs/reports/blender/coastal_region_source_coverage_b69.json').read_text(encoding='utf8'))
ledgerp=r/paths[4];ledger=json.loads(ledgerp.read_text(encoding='utf8'));issues_before=len(ledger['issues'])
correction={'cycle':'2026-10-04-B69','classification':'ERROR','scope':'Encontros terrestres dos píeres OSM 609043799/609043801','source_after':src,'source_reopened':True,'evidence':[rp.relative_to(r).as_posix(),vp,'docs/reports/blender/coastal_region_source_coverage_b69.json','docs/reports/blender/coastal_floor_fairing_b69_probe.json'],'changes':'B68 criou preenchimentos mas deixou 45 apoios ausentes em 16000 sondagens. B69 recompôs os dois recortes por subtração XY e CDT local, sem mover costa/terrenos/decks.','areas_m2':[c['area_m2'] for c in report['contacts']],'coverage_samples':16000,'remaining_sampled_gaps':0,'road_width_changed':False,'source_dem_changed':False,'runtime_exported':False,'gameplay_approved':False,'height_classification':'NEEDS_REVIEW'}
ledger.setdefault('applied_corrections',[])
if not any(x.get('cycle')==correction['cycle'] for x in ledger['applied_corrections']):ledger['applied_corrections'].append(correction)
pending=ledger.setdefault('waterfront_pending_checks',{})
pending['regional_modeling_review_b69']={'status':'pending','source':src,'coastal_floor_steep_triangles_over_200percent':126,'floor_vertices_below_nominal_water_at_boundary':19,'smoothing_probe':'rejected_before_mutation_worsens_mesh','road_center_samples':coverage['totals'],'road_width_real':None,'relative_height_and_road_connections_approved':False,'original_aleph_files_available_at_registered_path':False,'available_reference':'structural_reference.json e derivados versionados; captura OSM costeira 20261004 preservada','visual_capture':capture_dest.relative_to(r).as_posix(),'next_priorities':['Recuperar fonte Aleph original verificando hashes e disponibilidade; não substituir silenciosamente','Recompor junção de alturas B62/B63/cais com controles locais; não aplicar alisamento isolado nem fit Z global','Identificar vias interrompidas por OSM ID/nó e validar encontros/eixos/colisor','Tratar relevo local artificial preservando Cidade Alta/Baixa, vias e arquitetura','Conferir limite terra/água e níveis absolutos antes de elevar o mar ou aprovar acesso aos píeres']}
pending['new_pier_connections_b69']={'status':'partial','sampled_land_gap_coverage':'passed','contacts':[{'osm_id':c['osm_id'],'deck_land_delta_m':c['max_deck_land_difference_m'],'real_height_m':None,'approved':False} for c in report['contacts']],'evidence':vp}
assert len(ledger['issues'])==issues_before
ledgerp.write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
note=f"""## 04/10/2026 — B69: encontros dos píeres corrigidos; região ainda incompleta

Candidata explícita: `{src['file']}`, SHA-256 `{src['sha256']}`. B67/B68 preservadas; autoria B41 e produção B30 inalteradas. MCP na única janela PID 22916/porta 9876; fonte salva, reaberta e conferida.

B68 criou dois preenchimentos terrestres, mas a sondagem posterior encontrou 24/21 lacunas nos encontros. B69 substituiu apenas suas malhas por recortes obtidos pela subtração XY do chão e da água existentes, com triangulação em coordenadas locais. Áreas planas: 4,0730 e 3,2009 m². Na conferência reaberta: 16.000 sondagens, zero apoio terrestre ausente no recorte examinado; sólidos com zero arestas/vértices não manifold, zero triângulos degenerados e colisão igual. As 24 assinaturas protegidas permaneceram iguais. Isso não aprova toda a costa nem acessibilidade.

Diferenças máximas deck/piso: 1,4774 m (609043799) e 0,0477 m (609043801). Alturas reais, fundações e maré continuam null/pending. Nível nominal 0,35 preservado; base dos volumes é domínio candidato, não fundação levantada. Área de sobreposição usa projeção XY/centroides, não a área inclinada 3D nem uma prova integral de interseção.

A imagem regional foi obtida novamente: `artifacts/waterfront/b69-regiao-pendente.png`. **O relevo, acabamento urbano, junções das vias e relação vertical terra/água continuam insatisfatórios.** O piso B63 tem 126 triângulos acima de 200% de inclinação e 19 vértices de fronteira abaixo do mar nominal. Um ensaio de alisamento interno com borda fixa piorou a malha e foi rejeitado sem aplicação. Não mascarar a causa com suavização/global Z.

Triagem regional OSM: 620 amostras de eixo a cada ≤10 m; 614 com material de via e seis com chão sem material viário. Isso NÃO demonstra conexão correta, largura, perfil, quatro rodas ou veículos. Os alertas de material abrangem IDs 778284292, 1004133492/3493/3494 e requerem inspeção; não alargar nem mover eixos automaticamente.

Originais Aleph `map.osm`/`terrain.tif` não estão disponíveis no caminho registrado do projeto auxiliar; busca limitada ao diretório Tom Oliver também não os encontrou. Referência estrutural derivada e demais derivados permanecem disponíveis. Não substituir fonte silenciosamente nem apresentar alturas candidatas como reais. Próximo passe: recuperar/provar fontes e corrigir a junção B62–B63–cais, depois perfis/conexões das vias e relevo local.

Evidências: `docs/reports/blender/pier_land_contacts_r30b69.json`, `pier_land_contacts_r30b69_validation.json`, `coastal_region_source_coverage_b69.json`, `coastal_region_b68_inventory.json` e `coastal_floor_fairing_b69_probe.json` (últimos quatro no mesmo diretório). Pendências preservadas no ledger; sem npm, build, instalação, suíte geral ou exportação runtime.

"""
for path in paths[:3]:
 p=r/path;text=p.read_text(encoding='utf8');assert note.splitlines()[0] not in text
 first,sep,rest=text.partition('\n');p.write_text(first+'\n\n'+note+rest.lstrip('\r\n'),encoding='utf8')
print(json.dumps({'source':src,'issue_count_preserved':issues_before,'docs_updated':paths,'source_reopened':True}))
