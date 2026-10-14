"""Provas dirigidas do gate e primitivas geométricas; não aprova controller de engine."""
import json,itertools,argparse
from pathlib import Path
import numpy as np
from elevator_controller import LandingState,boarding_allowed,departure_allowed,closing_allowed,find_path,validate_ride_contract,ElevatorService
from slice_geometry import capsule_distances,continuous_triangle_pair
ROOT=Path(__file__).resolve().parents[2]
parser=argparse.ArgumentParser()
parser.add_argument('--output',type=Path,default=ROOT/'docs/reports/blender/lacerda-controller/contract_proof_b79.json')
args=parser.parse_args()
p=ROOT/'world/areas/mvp-centro-lacerda/corridor-slice.json'
c=json.loads(p.read_text(encoding='utf8'));design=c['character_design']
checks=[]
for present,stationary,clear,supported in itertools.product((True,False,None),repeat=4):
    s=LandingState(present,stationary,1.2,1.2,0,clear,supported)
    expected=all(x is True for x in (present,stationary,clear,supported))
    assert boarding_allowed(s,design)==expected
    checks.append(expected)
assert not boarding_allowed(LandingState(True,True,0,1.2,0,True,True),design)
assert not boarding_allowed(LandingState(False,True,1.2,1.2,0,True,True),design)
assert not boarding_allowed(LandingState(True,True,1.2,1.2,.1,True,True),design)
assert not departure_allowed(doors_closed=True,portal_empty=True,cabin_sweep_clear=False,occupancy_supported=True)
assert not closing_allowed(portal_capsule_empty=False)
edges=c['controller']['edges'];validate_ride_contract(edges)
assert find_path(edges,'upper_foyer','mercado',{}) is None
assert find_path(edges,'upper_foyer','mercado',{'upper_boarding':False}) is None
permission={g:True for e in edges for g in e.get('gates',[])}
assert find_path(edges,'upper_foyer','mercado',permission)
reference_gate_checks=[]
if any('upper_reference_verified' in e.get('gates',[]) for e in edges):
    for value in (False,None):
        candidate=dict(permission);candidate['upper_reference_verified']=value
        assert find_path(edges,'upper_foyer','mercado',candidate) is None
        reference_gate_checks.append({'upper_reference_verified':value,'route_blocked':True})
permission['cabin_sweep']=False
assert find_path(edges,'upper_foyer','mercado',permission) is None
service=ElevatorService(design);open_state=LandingState(True,True,1.2,1.2,0,True,True)
assert not service.alight(open_state)
assert service.board(open_state)
assert not service.depart(doors_closed=False,portal_empty=True,cabin_sweep_clear=True,occupancy_supported=True)
assert service.depart(doors_closed=True,portal_empty=True,cabin_sweep_clear=True,occupancy_supported=True)
assert not service.alight(open_state)
assert not service.arrive(LandingState(False,True))
assert service.arrive(LandingState(True,True))
assert not service.alight(LandingState(True,True,0,0,0,True,True))
assert service.alight(open_state)
floor=np.array([[[-2,-2,0],[2,-2,0],[0,2,0]]],dtype=float)
assert abs(capsule_distances([0,0,0],floor)[0]-.3)<1e-12
wall=np.array([[[.2,-2,-1],[.2,2,-1],[.2,0,3]]],dtype=float)
assert abs(capsule_distances([0,0,0],wall)[0]-.2)<1e-12
a=np.array([[-1,-1,1],[1,-1,1],[0,1,1.]])
good,start,end=continuous_triangle_pair(a,floor,np.array([0,0,-2.]))
assert good[0] and abs(start[0]-.5)<1e-6 and abs(end[0]-.5)<1e-6
good,_,_=continuous_triangle_pair(a+np.array([10,0,0]),floor,np.array([0,0,-2.]))
assert not good[0]
report={'schema':'boas/controller-contract-proof-v1','landing_state_cases':len(checks),
        'closed_door_blocked':True,'absent_cabin_blocked':True,'unknown_state_blocked':True,
        'failed_cabin_sweep_blocks_service':True,'occupied_portal_blocks_closing':True,
        'planner_respects_gate':True,'analytic_geometry_cases':4,
        'synthetic_temporal_service_sequence_passed':True,
        'upper_reference_gate_checks':reference_gate_checks,
        'actual_engine_verified':False,'actual_trip_approved':False}
out=args.output
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(report))
