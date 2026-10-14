"""Ensaios funcionais negativos do protótipo; não certificam arquitetura histórica."""
import json, math
from pathlib import Path
from lacerda_gameplay_proxy import ProxyController
ROOT=Path(__file__).resolve().parents[2]


def validate(config,round_trip):
    results=[]
    def case(name,passed,detail):
        if not passed:raise AssertionError(name+': '+str(detail))
        results.append({'case':name,'passed':True,'detail':detail})
    c=ProxyController(config);c.player=[2.5,0.,config['levels']['upper']+.015]
    for _ in range(180):c.update(1/60);c.move(-2.5/60,0.,0.)
    case('closed_door_blocks_entry',c.player[0]>1.7,c.player)
    c=ProxyController(config);c.car_z=config['levels']['lower'];c.station='lower';c.mode='OPEN';c.openness=1.
    c.player=[2.5,0.,config['levels']['upper']+.015]
    for _ in range(180):c.update(1/60);c.move(-2.5/60,0.,0.)
    case('absent_cabin_shaft_inaccessible',c.player[0]>1.7 and c.player[2]>config['levels']['upper'],c.player)
    c=ProxyController(config);c.player=[1.7,0.,config['levels']['upper']+.015];c.mode='CLOSING';c.openness=1.;c.destination='lower'
    c.update(1/60)
    case('occupied_portal_prevents_close',c.mode=='OPEN' and c.openness==1. and c.car_z==config['levels']['upper'],c.message)
    c=ProxyController(config);c.player=[0.,0.,config['levels']['upper']+.015];c.mode='OPEN';c.openness=1.
    assert c.request();c.update(1/60)
    case('no_motion_with_open_doors',c.car_z==config['levels']['upper'] and c.mode=='CLOSING',c.openness)
    c=ProxyController(config);c.station=None;c.mode='OPENING';c.car_z=(config['levels']['upper']+config['levels']['lower'])/2;c.openness=.2
    c.update(1/60)
    case('no_opening_without_docked_cabin',c.mode=='CLOSED' and c.openness==0.,c.mode)
    c=ProxyController(config);c.player=[0.,0.,config['levels']['upper']+.015];c.mode='OPEN';c.openness=1.
    c.move(0.,4.,0.)
    case('cabin_wall_blocks_player',abs(c.player[1])<1.3,c.player)
    moving=[row for row in round_trip['trace'] if row['mode']=='TRAVELLING']
    error=max(abs(row['position'][2]-row['car_z']-.015) for row in moving)
    case('passenger_carried_continuously',error<1e-8,{'samples':len(moving),'maximum_relative_z_error':error})
    events=round_trip['events'];departures=[x for x in events if x['event']=='departure']
    case('departure_interlocks',len(departures)==2 and all(x['door_aperture']==0. and x['carrying'] for x in departures),departures)
    # Nenhuma realimentação da rota injeta posição ou muda a origem geográfica.
    max_horizontal=max(math.dist(a['position'][:2],b['position'][:2]) for a,b in zip(round_trip['trace'],round_trip['trace'][1:]))
    max_vertical=max(abs(a['position'][2]-b['position'][2]) for a,b in zip(round_trip['trace'],round_trip['trace'][1:]))
    case('no_position_teleport',max_horizontal<=2.5/60+1e-6 and max_vertical<.26,{'maximum_xy_frame_delta':max_horizontal,'maximum_z_frame_delta':max_vertical})
    return {'status':'PASS_PROXY_ONLY','cases':results,'historical_gates_resolved':False,'engine_certification':False}


if __name__=='__main__':
    config=json.loads((ROOT/'world/areas/mvp-centro-lacerda/lacerda-gameplay-proxy.json').read_text(encoding='utf8'))
    trip=json.loads((ROOT/'docs/reports/blender/lacerda-gameplay-proxy/round_trip_numeric.json').read_text(encoding='utf8'))
    result=validate(config,trip)
    (ROOT/'docs/reports/blender/lacerda-gameplay-proxy/interlocks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'status':result['status'],'cases':len(result['cases'])}))
