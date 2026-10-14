"""Registrar B72/B73 verificadas e pendências, sem alterar a cena."""
import json,hashlib,shutil
from pathlib import Path
r=Path(__file__).resolve().parents[2]
b72p=r/'docs/reports/blender/city_seam_r30b72.json';b73p=r/'docs/reports/blender/terrain_tangent_r30b73.json'
a=json.loads(b72p.read_text(encoding='utf8'));b=json.loads(b73p.read_text(encoding='utf8'))
vp='docs/reports/blender/terrain_tangent_r30b73_validation.json';v=json.loads((r/vp).read_text(encoding='utf8'));assert v['source_reopened'] and v['local_geometry_checks_passed']
assert hashlib.sha256((r/b['source_after']['file']).read_bytes()).hexdigest()==b['source_after']['sha256']
a.update(source_reopened=True,validation_evidence='docs/reports/blender/city_seam_r30b72_validation.json');b.update(source_reopened=True,validation_evidence=vp)
for p,d in [(b72p,a),(b73p,b)]:p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
cp=r/'world/areas/mvp-centro-lacerda/blender-revisions.json';cat=json.loads(cp.read_text(encoding='utf8'))
for e in cat['revisions']:
 if e['file']==b['source_after']['file']:e.update(source_reopened=True,validation_evidence=vp,local_geometry_checks_passed=True)
cat['validation_source'].update(source_reopened=True,validation_evidence=vp,local_geometry_checks_passed=True);cp.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
lp=r/'world/areas/mvp-centro-lacerda/road-corrections.json';ledger=json.loads(lp.read_text(encoding='utf8'));assert len(ledger['issues'])==716
for cycle,report,evidence,scope in [('2026-10-05-B72',a,'city_seam_r30b72','Junção Manoel/Conceição e pavimento contínuo nos oito corredores OSM'),('2026-10-05-B73',b,'terrain_tangent_r30b73','Continuidade local da tangente na costura da encosta; vias/calçadas bloqueadas')]:
 if not any(x.get('cycle')==cycle for x in ledger['applied_corrections']):
  ledger['applied_corrections'].append({'cycle':cycle,'classification':'ADAPT_LOCAL','scope':scope,'source_before':report['source_before'],'source_after':report['source_after'],'source_reopened':True,'evidence':['docs/reports/blender/'+evidence+'.json','docs/reports/blender/'+evidence+'_validation.json'],'xy_changed':False,'road_width_changed':False,'source_dem_changed':False,'geographic_fit_verified':False,'runtime_exported':False,'gameplay_approved':False})
ledger['waterfront_pending_checks']['city_seam_b72']={'status':'partial','pavement_continuity_eight_roads_checked':True,'real_widths_verified':False,'road_edges_need_modeling':True,'reference_fit_status':'candidate','core_degenerate_triangles_pending':94}
ledger['waterfront_pending_checks']['terrain_tangent_b73']={'status':'partial','local_tangent_applied_verified':True,'design_transition_width_m':8,'real_transition_width_m':None,'real_altimetry_verified':False,'changed_vertices':2359,'max_delta_z_m':b['candidate']['max_delta_z_m'],'scope':'Encosta junto à borda antiga; não valida toda a cidade'}
ledger['production_ready']=False;lp.write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
section="""## 05/10/2026 — B72/B73: continuidade das vias e tangente local da encosta

Candidata ativa de validação: `blender/salvador_lacerda_r30b73_tangente_encosta_costura.blend`, SHA-256 `d49f9b35e00b292acdbd33028b58f8eaa52d71e9ba9fd232ba679190227e1f0b`. B71 e B72 preservadas. Ambas as revisões foram salvas/reabertas na mesma janela MCP. Autoria B41 e produção B30 permanecem separadas.

Os oito eixos conferidos coincidem exatamente com a referência OSM armazenada, pelos mesmos IDs. Isso não certifica o georreferenciamento da cidade: o fit permanece candidato. B72 continuou o pavimento nas superfícies existentes e recompôs a junção OSM 4527284526 entre Manoel Vitórino/Conceição: 1.286 vértices, delta Z máximo 0,5672 m. Inclinação transversal máxima: Manoel 12,97% → 3,77%; Conceição 6,92% → 3,77%. Longitudinal: Manoel 22,98% → 16,15%; Conceição 14,43% → 16,20% (tradeoff explícito). Os oito eixos e apoios laterais a ±0,825 m têm chão nas amostras a cada até 0,5 m; isso é leitura geométrica, não teste físico do veículo. Materiais contínuos nos eixos; o nó compartilhado da Manoel usa o pavimento de pedra da Conceição.

B73 modifica 2.359 vértices de terreno não viário numa faixa de transição de 8 m; escolha local de modelagem, não dimensão levantada. Preserva XY, topologia, extremos, vias/calçadas bloqueadas, núcleo, piso/cais, píeres e água; delta Z máximo 3,9890 m. Diferença de inclinação entre os lados, medida em segmentos de 1 m: P95 3,7581 → 0,3600. Diferença de cotas em pontos a ±0,01 m da borda: máxima 0,07884 → 0,00980 m. Valores de vários metros medidos em pontos separados por 2 m incluíam a própria descida da encosta; não eram um degrau medido no mesmo XY.

**Não concluído:** bordas serrilhadas do pavimento, acabamento da expansão, georreferenciamento/altimetria absolutos, larguras reais, 94 triângulos degenerados preexistentes no núcleo e travessia física na engine. A captura original Aleph ainda está ausente; não inventar sua altitude nem promover o fit por reduzir uma métrica. A cena continua parcial e não aprovada para produção/AAA.

Evidências: `docs/reports/blender/city_seam_r30b72{,_validation}.json`, `terrain_tangent_r30b73{,_validation}.json` e `terrain_tangent_b73_candidate.json`. Ledger preserva as 716 detecções existentes e registra os dois ciclos. Limpeza recuperável de caches/autosaves registrada em `storage_cleanup_b72_*.json` e `storage_cleanup_b73_browser_cache.json`; instalações e revisões oficiais preservadas.

Nova solicitação de 05/10: expandir até Dique do Tororó, Arena Fonte Nova e Center Lapa, adquirindo fontes reais, verificando anchors/overlap e só depois integrar terreno/vias e revisão cinemática com a Rondesp/câmera do motorista. Sem npm/build/suíte de testes.

"""
for name in ['PROJECT_STATUS.md','CODEX_HANDOFF.md','WATERFRONT_FIDELITY_REVIEW.md']:
 p=r/'docs'/name;old=p.read_text(encoding='utf8')
 if '## 05/10/2026 — B72/B73:' not in old:
  if old.startswith('# '):
   head,rest=old.split('\n',1);text=head+'\n\n'+section+rest.lstrip('\n')
  else:text=section+old
  p.write_text(text,encoding='utf8')
cleanup={'schema':'boas/storage-cleanup-b72-additional-v1','obsolete_autosaves_removed':[{'name':'salvador_lacerda_r30b67_pieres_e_dominio_oceanico_22916_autosave.blend','bytes':104526777},{'name':'hilux_portas_v18_16304_autosave.blend','bytes':3574647},{'name':'marrom_v25_lanternas_re_19576_autosave.blend','bytes':3748729}],'original_files_preserved':True,'free_at_registration':shutil.disk_usage(r).free}
(r/'docs/reports/blender/storage_cleanup_b72_additional.json').write_text(json.dumps(cleanup,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'registered':b['source_after'],'issues_preserved':len(ledger['issues'])}))
