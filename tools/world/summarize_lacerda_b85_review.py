"""Fecha o registro documental B85 sem alterar qualquer arquivo Blender."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[2]
out = root/'docs/reports/blender/lacerda-proportions-b85'
inventory = json.loads((out/'four_elevators_inventory.json').read_text(encoding='utf8'))
objects = {row['object']: row for row in inventory['objects']}
cabins = [row for name,row in objects.items() if 'cabine' in name.casefold() or 'cabina' in name.casefold()]
summary = {'scene_changed':False,'inventory': 'docs/reports/blender/lacerda-proportions-b85/four_elevators_inventory.json',
           'unique_named_cabin_components':len(cabins),'named_cabin_components':[r['object'] for r in cabins],
           'functional_b82_cabin_count':1,'functional_count_evidence':'automation/blender/model_lacerda_gameplay_proxy_b82.py: único cabin_floor e conjunto de estados',
           'required_equipment_count':4,'historical_equipment_count_certified':None,
           'lower_tunnel_documented':True,'lower_tunnel_scene_correspondence':'NEEDS_REVIEW',
           'upper_hall_resized':False,'bridge_resized':False,'production_ready':False}
summary['legacy_cabin_floor_bounds']=[{'object':name,'bounds':row['bounds_local'],'collections':row['collections']} for name,row in objects.items() if name.startswith('CABINE ') and name.endswith('| piso')]
summary['legacy_tunnel_objects']=[{'object':name,'bounds':row['bounds_local'],'collections':row['collections']} for name,row in objects.items() if 'túnel' in name.casefold() or 'tunel' in name.casefold()]
(out/'four_elevators_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
for name,heading in [('CODEX_HANDOFF.md','## 07/10/2026 — B85 ativa: não declarar saguão corrigido'),
                     ('CODEX_STRUCTURE_HANDOFF.md','## 07/10/2026 — proporções Lacerda / B85')]:
    path=root/'docs'/name
    text=path.read_text(encoding='utf8')
    if text.startswith(heading):continue
    start=text.index(heading)
    section=text[start:]
    following=section.find('\n## ',len(heading))
    end=start+following if following>=0 else len(text)
    block=text[start:end].strip()
    remainder=(text[:start]+text[end:]).strip()
    path.write_text(block+'\n\n'+remainder+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in summary.items() if k!='named_cabin_components'},ensure_ascii=False))
