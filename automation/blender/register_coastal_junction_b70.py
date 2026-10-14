"""Registra B70 conferida, preservando histórico e pendências."""
import json,shutil,hashlib
from pathlib import Path
r=Path(__file__).resolve().parents[2]
rp=r/'docs/reports/blender/coastal_junction_r30b70.json';report=json.loads(rp.read_text(encoding='utf8'))
vp=r/'docs/reports/blender/coastal_junction_r30b70_validation.json';val=json.loads(vp.read_text(encoding='utf8'))
assert val['source_reopened'] and val['local_geometry_checks_passed'] and report['source_after']==val['source']
backup=r/'artifacts/waterfront/b70-metadata-before';backup.mkdir(parents=True,exist_ok=True)
paths=['docs/PROJECT_STATUS.md','docs/CODEX_HANDOFF.md','docs/WATERFRONT_FIDELITY_REVIEW.md','world/areas/mvp-centro-lacerda/road-corrections.json']
for rel in paths:
 dest=backup/Path(rel).name
 if not dest.exists():shutil.copyfile(r/rel,dest)
src=report['source_after']
short=f"""
## 04/10/2026 — B70: junção terreno–piso–cais recomposta localmente

Candidata salva/reaberta pelo MCP na única janela PID 22916/porta 9876: `{src['file']}`, SHA-256 `{src['sha256']}`. B69 preservada; autoria B41/produção B30 mantidas. Corrigido o vínculo de alturas por arestas físicas entre B62/B63; adaptação local aos controles do cais existente, sem levantamento altimétrico. Piso: 126 → 2 triângulos acima de 200% de inclinação; 19 → 0 vértices abaixo do mar nominal. Conferência reaberta: 206 contatos com diferença Z zero, visual/colisão iguais, zero triângulos degenerados, XY/topologia preservados e 16.240 vértices de vias/passeios fixos. As superfícies de terreno permanecem abertas intencionalmente.

A faixa de contato de 2 m e transição até 30 m são escolhas de modelagem candidatas, não larguras reais medidas; maior alteração local Z: 7,5900 m. Altimetria absoluta continua não verificada. Restam dois triângulos no extremo norte (controles 7,2557 versus ~9,0563 m), transição diagonal, acabamento urbano/encosta e conexões viárias. Não aprovado para circulação integral nem promovido ao runtime. Originais Aleph ainda ausentes no caminho registrado.

Evidências: `docs/reports/blender/coastal_junction_r30b70.json`, `docs/reports/blender/coastal_junction_r30b70_validation.json` e `artifacts/waterfront/b70-juncao-cais.png`. Próximo passe: revisar o conflito local norte com controles verticais confiáveis e inspecionar conexões viárias OSM 778284292/1004133492/3493/3494, sem inventar larguras.

"""
extra="""
O erro de contato foi classificado ERROR: estimar altura por raios tangentes à borda não reproduzia a aresta física. O nivelamento local foi classificado ADAPT_LOCAL: utiliza cotas da cena atual, não altera o DEM-fonte e não certifica fidelidade altimétrica. Foram recompostas somente B62 visual/colisão e B63 piso visual/colisão, mantendo nomes e IDs. Cais, água, núcleo histórico, píeres, canteiros, meios-fios e navegação protegidos mantiveram suas assinaturas.

No piso, P95 de inclinação: 142,87% → 23,35%; máximo: 2541,82% → 259,49% nos dois triângulos de borda ainda pendentes. Na faixa HQ examinada, máximo: 83,22% → 78,89%, mas P95: 26,23% → 36,29%; portanto não interpretar a melhoria do piso como aprovação da caminhabilidade de toda a faixa adjacente. A inspeção visual continua parcial e mostra transição diagonal/acabamento e vias incompletos. Gameplay, personagem, quatro rodas, tráfego e câmera não foram aprovados por estas verificações.

"""
for rel in paths[:3]:
 p=r/rel;text=p.read_text(encoding='utf8')
 marker='## 04/10/2026 — B70:'
 if marker not in text:
  block=short+(extra if rel.endswith('WATERFRONT_FIDELITY_REVIEW.md') else '')
  if text.startswith('# '):
   head,tail=text.split('\n',1);text=head+'\n'+block+tail
  else:text=block+text
  p.write_text(text,encoding='utf8')
p=r/paths[3];ledger=json.loads(p.read_text(encoding='utf8'));issues_before=ledger['issues']
if not any(x.get('cycle')=='2026-10-04-B70' for x in ledger['applied_corrections']):
 ledger['applied_corrections'].append({'cycle':'2026-10-04-B70','classification':'ADAPT_LOCAL','binding_error_classification':'ERROR','scope':'Junção local HQ/piso/cais, mantendo XY/topologia e vias/passeios','source_before':report['source_before'],'source_after':src,'source_reopened':True,'evidence':[rp.relative_to(r).as_posix(),vp.relative_to(r).as_posix(),report['probe_evidence']],'hq_changed_vertices':report['probe']['hq_changed_vertices'],'hq_max_z_change_m':report['probe']['hq_max_z_change_m'],'locked_road_walkable_vertices':val['locked_road_walkable_vertices'],'locked_vertices_max_change_m':0,'floor_steep_triangles_before':126,'floor_steep_triangles_after':2,'floor_below_nominal_sea_before':19,'floor_below_nominal_sea_after':0,'boundary_bindings':206,'boundary_max_height_difference_m':0,'design_contact_band_m':2,'design_transition_limit_m':30,'real_transition_width_m':None,'real_altimetry_verified':False,'road_width_changed':False,'source_dem_changed':False,'runtime_exported':False,'gameplay_approved':False})
ledger['waterfront_pending_checks']['coastal_junction_b70']={'status':'partial','source':src,'remaining_steep_triangles':report['probe']['worst_remaining_triangles'],'remaining_height_classification':'NEEDS_REVIEW','absolute_altimetry_verified':False,'real_transition_width_m':None,'approved':False,'pending':report['pending'],'visual_evidence':val['visual_evidence']}
ledger['production_ready']=False
p.write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
assert json.loads(p.read_text(encoding='utf8'))['issues']==issues_before
screen=Path(r'C:/Users/TONECOS/AppData/Local/Ordax/DevAgent/artifacts/bay-of-all-saints/baf090ddd550456799eff6bb303c14eb/blender-live.png')
assert screen.is_file() and hashlib.sha256(screen.read_bytes()).hexdigest()=='67cc2dd31815803e4e0f7e0d517701b2ad540d923c138589eab8163ad3dd3997'
shutil.copyfile(screen,r/'artifacts/waterfront/b70-juncao-cais.png')
print(json.dumps({'revision':src['revision'],'issues_preserved':len(issues_before),'source_reopened':True,'metadata_registered':True}))
