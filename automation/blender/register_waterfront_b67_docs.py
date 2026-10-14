"""Registrar a revisão B67 e pendências verificadas, preservando histórico e produção."""
import json,shutil,hashlib
from pathlib import Path
r=Path(__file__).resolve().parents[2]
report=json.loads((r/'docs/reports/blender/waterfront_piers_r30b67.json').read_text(encoding='utf-8'))
validation=json.loads((r/'docs/reports/blender/waterfront_piers_r30b67_validation.json').read_text(encoding='utf-8'))
assert validation['source_reopened'] and validation['local_geometry_checks_passed']
note="## 04/10/2026 — B67: píeres reais e domínio da água\n\nCandidata de validação: `blender/salvador_lacerda_r30b67_pieres_e_dominio_oceanico.blend`, SHA-256 `e0fcda84e28adaf3161da7458195471511b00c2ef9e70fd42f6edc555188b412`. B66 preservada; autoria B41 e produção B30 continuam separadas. Aplicação MCP na única janela PID 22916/porta 9876, seguida de reabertura e conferência local.\n\nUma consulta oficial nova ao OSM foi preservada em `artifacts/waterfront/osm_coastal_check_20261004.osm.gz`, sem substituir silenciosamente a captura anterior. Seis controles de mesmas features confirmaram reutilização local da transformação XY. Dois contornos fechados ausentes, OSM 609043799 e 609043801, receberam decks visuais, referência e superfícies candidatas separadas de colisão. Contornos XY mantidos dentro de 0,0001 m de tolerância numérica da mesh; isso não certifica a precisão absoluta da fonte.\n\nAlturas dos novos decks: 2,9742 e 4,5861 unidades Blender, derivadas do piso da cena, classificadas ADAPT_LOCAL/candidate. Não são levantamento real. Ligação à margem, fundações, guarda-corpos e maré permanecem pendentes; o primeiro ponto de margem tem variação de 2,4814 unidades e exige revisão antes de criar acesso. Eixos adicionais 1321555661/1321717133, quebra-mar 217677378 e passarela 1426173324 permanecem somente referências ocultas, com largura/altura reais null.\n\nO volume de água foi reconstruído a partir do contorno da superfície atual, fechado e com normais coerentes. Espuma costeira derivada do mesmo limite, excluindo três bordas artificiais do recorte. Nível 0,35 preservado; fundo -16 é domínio de gameplay legado, não batimetria. Nos decks antigos há bordo livre candidato de 6,9057 unidades, portanto o encaixe vertical absoluto água–cais–píeres ainda não está aprovado. Não elevar o mar nem aplicar escala/offset Z global para ocultar isso.\n\nConferência após reabertura: volume fechado com zero arestas não manifold e zero triângulos degenerados; dois decks sólidos fechados, referências/superfícies sem degeneração, colisão igual e espuma coerente com a costa atual. Terrenos, água visual, cais, píeres anteriores e larguras de ruas preservados no passe. Sem exportação runtime ou aprovação global de cidade, tráfego, personagem/veículo.\n\nEvidências: `docs/reports/blender/coastal_osm_source_check.json`, `pier_land_contacts_b67_probe.json`, `waterfront_piers_r30b67.json` e `waterfront_piers_r30b67_validation.json` (estes três em `docs/reports/blender/`). No Blender ficam domínio/nível e prévia da água; renderização dinâmica, ondas, consultas de altura e flutuação exigem implementação na engine. A engine definitiva segue em aberto; o protótipo Three.js usa nível nominal 0,35.\n\nLimpeza autorizada adicional: perfis temporários inativos, três pacotes runtime antigos fora do ponteiro ativo, cache de downloads pip antigo e três autosaves temporários B56/B57/B62 substituídos. Fontes oficiais, bibliotecas instaladas, pacote ativo e recoveries manuais preservados. Relatórios de limpeza guardam escopo e hashes. A falta recorrente de espaço ainda limita novas revisões. Sem npm, build, instalação ou suíte geral.\n\n"
paths=['docs/PROJECT_STATUS.md','docs/CODEX_HANDOFF.md','docs/WATERFRONT_FIDELITY_REVIEW.md','world/areas/mvp-centro-lacerda/road-corrections.json','world/areas/mvp-centro-lacerda/blender-revisions.json']
backup=r/'artifacts/waterfront/b67-metadata-before';backup.mkdir(parents=True,exist_ok=True)
assert shutil.disk_usage(r).free>sum((r/p).stat().st_size for p in paths)*3+5*1024**2
for path in paths:
 p=r/path;b=backup/p.name
 if not b.exists():b.write_bytes(p.read_bytes())
for path in paths[:3]:
 p=r/path;text=p.read_text(encoding='utf-8-sig')
 assert '## 04/10/2026 — B67: píeres reais e domínio da água' not in text
 first,sep,rest=text.partition('\n')
 p.write_text(first+'\n\n'+note+rest,encoding='utf-8')
p=r/paths[3];ledger=json.loads(p.read_text(encoding='utf-8-sig'))
issues_before=hashlib.sha256(json.dumps(ledger['issues'],sort_keys=True).encode()).hexdigest()
assert not any(c['correction_id']=='waterfront-piers-water-domain-B67' for c in ledger['applied_corrections'])
ledger['applied_corrections'].append({'correction_id':'waterfront-piers-water-domain-B67','cycle':'2026-10-04-B67','classification':'ERROR','subclassifications':{'new_pier_xy':'KEEP_REAL_REFERENCE','new_pier_deck_z':'ADAPT_LOCAL','water_volume_and_foam':'ERROR','absolute_water_datum':'NEEDS_REVIEW','unknown_width_axes':'SOURCE_LIMITATION'},'source_after':report['source_after'],'source_reopened':True,'scope':'Dois contornos reais ausentes de píeres; volume/espuma derivados da água atual, sem mudar nível marítimo ou piso','evidence':'docs/reports/blender/waterfront_piers_r30b67.json','validation_evidence':'docs/reports/blender/waterfront_piers_r30b67_validation.json','new_pier_osm_ids':[609043799,609043801],'local_geometry_checks_passed':True,'road_width_changed':False,'source_dem_modified':False,'runtime_exported':False,'status':'local_geometry_corrected_fidelity_gameplay_pending','real_dimensions_verified':False})
pending=ledger['waterfront_pending_checks']
pending.update({'absolute_water_datum_verified':False,'water_level_m_candidate':.35,'legacy_pier_freeboard_candidate_m':report['legacy_pier_freeboard_candidate_m'],'additional_bridge_osm_ids':[1426173324],'pier_axes_width_unknown':[1321682676,1321682677,1321555661,1321717133],'breakwater_width_unknown':[217677378],'new_pier_connections':[{'osm_id':p['osm_id'],'deck_z_candidate_m':p['deck_z_candidate_m'],'real_deck_height_m':None,'foundation_verified':False,'connection_approved':False} for p in report['new_closed_piers']],'approved':False})
assert hashlib.sha256(json.dumps(ledger['issues'],sort_keys=True).encode()).hexdigest()==issues_before
p.write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=r/paths[4];catalog=json.loads(p.read_text(encoding='utf-8-sig'));assert catalog['validation_source']['sha256']==report['source_after']['sha256']
for entry in catalog['revisions']:
 if entry['file']==report['source_after']['file']:entry.update(source_reopened=True,validation_evidence='docs/reports/blender/waterfront_piers_r30b67_validation.json',local_geometry_checks_passed=True)
catalog['validation_source'].update(source_reopened=True,validation_evidence='docs/reports/blender/waterfront_piers_r30b67_validation.json',local_geometry_checks_passed=True)
p.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Identificação portátil dos temporários, sem caminhos absolutos versionados.
p=r/'docs/reports/blender/obsolete_blender_autosaves_cleanup.json';cleanup=json.loads(p.read_text(encoding='utf-8-sig'))
for row in cleanup['files']:row['path']='%LOCALAPPDATA%/Temp/'+Path(row['path']).name
p.write_text(json.dumps(cleanup,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for path in paths[3:]:json.loads((r/path).read_text(encoding='utf-8'))
print(json.dumps({'documents_updated':paths,'road_issues_preserved':len(ledger['issues']),'runtime_promoted':False,'source':report['source_after']}))
