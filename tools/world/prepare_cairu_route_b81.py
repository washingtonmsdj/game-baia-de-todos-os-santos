"""Nova candidata XY por topologia, sem reutilizar rota antiga ou inventar entrada."""
import json
from pathlib import Path
import numpy as np
import audit_slice_volume_b79 as audit
from prepare_cairu_market_ground import ground_follow
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/reports/blender/cairu-market-b81'

def main():
 d=json.loads((ROOT/'artifacts/lacerda-controller/geometry_b80.json').read_text(encoding='utf8'))
 live=json.loads((OUT/'live_inspection_b80.json').read_text(encoding='utf8'))
 extras=json.loads((ROOT/'artifacts/lacerda-controller/external_live_supports_b80.json').read_text(encoding='utf8'))
 names={r['name'] for r in d['objects']};d['objects'] += [r for r in extras if r['name'] not in names]
 paint='LAC R30B06 | fundo verde travessia 3178050253'
 d['objects']=[r for r in d['objects'] if r['name']!=paint]
 seed=[n['blender_xy']+[7.255668640136719] for n in live['route_controls']]
 seed[0][2]=7.405999660491943
 skin=d['qa']['character_design']['contact_tolerance']
 points,samples,pending=ground_follow(d,seed,'closed_lower',skin=skin)
 route={'points':points,'control_nodes':live['route_controls'],'status':'candidate_blocked','terminus_osm_node':12229090827,'market_entrance_verified':False,'lower_foyer_connector_verified':False,'skin':skin,'samples':samples,'pending':pending,'source_geometry':'B80 + apoios R21 lidos na mesma janela','elevator_movement_enabled':False}
 (OUT/'route_candidate.json').write_text(json.dumps(route,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 d['qa']['routes']={'external':{'points':points}}
 for r in d['objects']:
  g=r['geometry'];r['tri']=np.asarray(g['vertices'])[np.asarray(g['triangles'],dtype=int)]
 audit.OUT=OUT;audit.SUFFIX='new_external_candidate'
 sweep=audit.character_sweep(d,[('external','closed_lower')],skin=skin)
 (ROOT/'artifacts/lacerda-controller/external_route_physics_b80.json').write_text(json.dumps({k:v for k,v in d.items() if k!='objects'}|{'objects':[{k:v for k,v in r.items() if k!='tri'} for r in d['objects']]},ensure_ascii=False),encoding='utf8')
 print(json.dumps({'points':len(points),'pending_supports':len(pending),'skin':skin,'penetrations':len(sweep['routes'][0]['penetrations']),'status':sweep['routes'][0]['status'],'market_entrance_verified':False}))
if __name__=='__main__':main()
