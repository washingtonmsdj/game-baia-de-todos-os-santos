"""Registra B71 e revisão de acesso viário, mantendo histórico."""
import json,shutil,hashlib
from pathlib import Path
r=Path(__file__).resolve().parents[2];rp=r/'docs/reports/blender/north_junction_r30b71.json';report=json.loads(rp.read_text(encoding='utf8'))
vp=r/'docs/reports/blender/north_junction_r30b71_validation.json';val=json.loads(vp.read_text(encoding='utf8'));src=report['source_after']
assert val['source_reopened'] and val['local_geometry_checks_passed'] and val['floor']['above_200percent']==0
roads=json.loads((r/'docs/reports/blender/coastal_service_roads_b71_review.json').read_text(encoding='utf8'))
private=[row['osm_id'] for row in roads['roads'] if row['access_classification']=='private'];assert len(private)==3
backup=r/'artifacts/waterfront/b71-metadata-before';backup.mkdir(parents=True,exist_ok=True)
paths=['docs/PROJECT_STATUS.md','docs/CODEX_HANDOFF.md','docs/WATERFRONT_FIDELITY_REVIEW.md','world/areas/mvp-centro-lacerda/road-corrections.json']
for rel in paths:
 dest=backup/Path(rel).name
 if not dest.exists():shutil.copyfile(r/rel,dest)
block=f"""
## 04/10/2026 — B71: encontro norte corrigido; acesso privado nas vias revisadas

Fonte candidata salva/reaberta pelo MCP na mesma janela: `{src['file']}`, SHA-256 `{src['sha256']}`. B70 preservada; autoria B41/produção B30 mantidas. O canto do piso coincidia em XY com o núcleo, mas estava 1,8006 m acima; corrigido o vínculo ao vértice real da cena. Topo do cais e piso recompostos localmente até esse apoio: 12 vértices do cais alterados, 380 do piso acima de 0,00001 m; transição de 12 m é escolha candidata de modelagem, não dimensão real levantada. Núcleo, HQ, vias, píeres, água, XY e topologia preservados; visual/colisão iguais após reabrir.

Piso: dois → zero triângulos acima de 200%; inclinação máxima 259,49% → 63,85%, P95 23,35% → 21,82%; nenhum vértice abaixo do mar nominal. Máximo desencontro Z nos 23 vínculos norte: 0,0000003813 m (precisão numérica), canto a 0,0000305 m do controle. Zero triângulos degenerados/arestas com mais de duas faces. As superfícies abertas de piso e contenção não são volumes estanques; estes números não certificam caminhabilidade ou altimetria real.

Revisão das quatro vias: OSM 1004133492/3493 são acessos privados e 1004133494 é corredor privado de estacionamento; 778284292 é via de serviço com acesso pendente. 757 amostras dos eixos dentro da região, a cada até 1 m, com chão presente; isso não prova largura, conexão completa, material correto ou passagem das quatro rodas. Não usar esses acessos privados automaticamente como trajetos de ônibus. Larguras reais null.

Evidências: `docs/reports/blender/north_junction_r30b71.json`, `north_junction_r30b71_validation.json`, `coastal_service_roads_b71_review.json` no mesmo diretório; vista `artifacts/waterfront/b71-encontro-norte.png`. Próximo: perfis/encontros viários e encosta, com controles existentes e classificação explícita; acabamento regional/níveis absolutos/fonte Aleph original seguem pendentes. Sem aprovação integral ou exportação runtime.

"""
for rel in paths[:3]:
 p=r/rel;text=p.read_text(encoding='utf8')
 if '## 04/10/2026 — B71:' not in text:
  if text.startswith('# '):
   head,tail=text.split('\n',1);text=head+'\n'+block+tail
  else:text=block+text
  p.write_text(text,encoding='utf8')
p=r/paths[3];ledger=json.loads(p.read_text(encoding='utf8'));oldissues=ledger['issues']
if not any(x.get('cycle')=='2026-10-04-B71' for x in ledger['applied_corrections']):
 ledger['applied_corrections'].append({'cycle':'2026-10-04-B71','classification':'ADAPT_LOCAL','binding_error_classification':'ERROR','scope':'Encontro norte do piso/cais ao núcleo existente; sem alterar XY ou datum global','source_before':report['source_before'],'source_after':src,'source_reopened':True,'evidence':[rp.relative_to(r).as_posix(),vp.relative_to(r).as_posix(),'docs/reports/blender/coastal_service_roads_b71_review.json'],'control_xyz':report['candidate']['control_xyz'],'design_transition_radius_m':12,'real_transition_length_m':None,'real_altimetry_verified':False,'floor_steep_triangles_before':2,'floor_steep_triangles_after':0,'floor_max_grade':val['floor']['maximum_grade'],'floor_p95_grade':val['floor']['p95_grade'],'quay_changed_vertices':12,'floor_changed_vertices_above_1e_minus5_m':380,'north_max_height_difference_m':val['north_max_height_difference_m'],'road_width_changed':False,'source_dem_changed':False,'runtime_exported':False,'gameplay_approved':False})
ledger['waterfront_pending_checks']['north_junction_b71']={'status':'local_geometry_corrected_real_altimetry_pending','source':src,'supersedes_local_corner_pending':'coastal_junction_b70','floor_remaining_above_200percent':0,'real_altimetry_verified':False,'approved':False,'pending':report['pending']}
ledger['waterfront_pending_checks']['coastal_service_roads_b71']={'private_osm_ids':private,'parking_aisle_osm_id':1004133494,'access_pending_osm_ids':[778284292],'real_width_m':None,'bus_routes_approved':False,'evidence':'docs/reports/blender/coastal_service_roads_b71_review.json'}
for correction in ledger['applied_corrections']:
 if correction.get('cycle')=='2026-10-04-B71' and 'floor_changed_vertices_above_1e5_m' in correction:
  correction['floor_changed_vertices_above_1e_minus5_m']=correction.pop('floor_changed_vertices_above_1e5_m')
ledger['production_ready']=False
p.write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n',encoding='utf8');assert json.loads(p.read_text(encoding='utf8'))['issues']==oldissues
screen=Path(r'C:/Users/TONECOS/AppData/Local/Ordax/DevAgent/artifacts/bay-of-all-saints/c9663a01ab4447fd9a2d2bf1175b00cd/blender-live.png')
assert screen.is_file() and hashlib.sha256(screen.read_bytes()).hexdigest()=='60f15fb619339d2f1a389ddcf0320c5d62f08603c12c26ff6337302e75af6afd'
shutil.copyfile(screen,r/'artifacts/waterfront/b71-encontro-norte.png')
val['visual_evidence']='artifacts/waterfront/b71-encontro-norte.png';val['visual_review']='local_corner_continuous_regional_paving_material_and_geometry_finish_pending'
vp.write_text(json.dumps(val,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
assert hashlib.sha256((r/src['file']).read_bytes()).hexdigest()==src['sha256']
print(json.dumps({'revision':src['revision'],'issues_preserved':len(oldissues),'private_roads':private,'metadata_registered':True}))
