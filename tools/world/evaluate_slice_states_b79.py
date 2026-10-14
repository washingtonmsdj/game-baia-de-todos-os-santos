"""Liga o gate aos estados e folhas reais exportados do Blender; não roda engine."""
import json,argparse
from pathlib import Path
import numpy as np
from elevator_controller import LandingState,boarding_allowed,find_path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/reports/blender/lacerda-controller'
parser=argparse.ArgumentParser()
parser.add_argument('--geometry',type=Path,default=ROOT/'artifacts/lacerda-controller/geometry_b77b.json')
parser.add_argument('--character-sweep',type=Path,default=OUT/'character_sweep_b77b.json')
parser.add_argument('--output',type=Path,default=OUT/'actual_states_b79.json')
args=parser.parse_args()
d=json.loads(args.geometry.read_text(encoding='utf8'))
c=json.loads((ROOT/'world/areas/mvp-centro-lacerda/corridor-slice.json').read_text(encoding='utf8'))
char=json.loads(args.character_sweep.read_text(encoding='utf8'));rows=d['objects']
def pair(role,landing):
    side=1 if landing=='upper' else -1
    return [r for r in rows if r['properties'].get('elevator_id')==3
            and r['properties'].get('elevator_role')==role
            and (r['properties'].get('landing')==landing if role=='landing_door' else r['door_side']==side)]
def aperture(parts,state):
    parts=sorted(parts,key=lambda r:r['properties']['door_leaf']);assert len(parts)==2
    initial=d['states']['closed_upper']['objects']
    centers=[np.asarray(initial[p['name']]['vertices']).mean(axis=0) for p in parts]
    axis=centers[1]-centers[0];axis[2]=0;axis/=np.linalg.norm(axis)
    leaves=[np.asarray(state['objects'][p['name']]['vertices'])@axis for p in parts]
    return max(0,float(leaves[1].min()-leaves[0].max()))
cases=[]
for label,state in d['states'].items():
    floor_z=max(p[2] for p in state['objects']['FUNCIONAL | 3 piso']['vertices'])
    for landing in ('upper','lower'):
        route=next(r for r in char['routes'] if r['route']==landing)
        portal_hits=[h for h in route['penetrations'] if (h['segment']>=len(d['qa']['routes'][landing]['points'])-5 if landing=='upper' else h['segment']<=4)]
        present=abs(floor_z-c['elevator'][landing+'_z'])<=c['character_design']['boarding_capsule_contact_max_drop']
        measured=LandingState(present,label!='moving_closed',aperture(pair('landing_door',landing),state),
            aperture(pair('cabin_door',landing),state),0 if present else None,not portal_hits,not route['unsupported'])
        geometry_candidate=boarding_allowed(measured,c['character_design'])
        reference_required=any(e['from']==landing+'_foyer' and 'upper_reference_verified' in e.get('gates',[]) for e in c['controller']['edges'])
        reference_verified=c['controller'].get('default_permissions',{}).get('upper_reference_verified')
        allowed=geometry_candidate and (not reference_required or reference_verified is True)
        assert not allowed # Medidas candidatas não autorizam o gate atual.
        permissions={landing+'_boarding':allowed,'cabin_sweep':False}
        cases.append({'state':label,'landing':landing,'measurements':measured.__dict__,'geometry_candidate':geometry_candidate,
            'reference_verified':reference_verified if reference_required else None,'boarding_allowed':allowed,
            'complete_route_available':find_path(c['controller']['edges'],'upper_foyer','mercado',permissions) is not None,
            'sill_delta_status':'zero apenas entre alvos animados; relação real soleira/piso e apoio contínuo exigem referência/engine'})
report={'source':d['source'],'cases':cases,'all_actual_states_fail_closed':True,'engine_verified':False,'trip_approved':False}
args.output.parent.mkdir(parents=True,exist_ok=True)
args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'actual_state_gate_cases':len(cases),'allowed':sum(x['boarding_allowed'] for x in cases)}))
