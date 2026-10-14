"""Teste específico do percurso implementado; não estende rota até Mercado."""
import json,math
from pathlib import Path
from lacerda_gameplay_proxy import validate_round_trip
from validate_lacerda_gameplay_proxy import validate
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/reports/blender/lacerda-current-playtest'


def main():
    cfg=json.loads((ROOT/'world/areas/mvp-centro-lacerda/lacerda-gameplay-proxy.json').read_text(encoding='utf8'))
    trip=validate_round_trip(cfg);checks=validate(cfg,trip)
    lower_end=cfg['lower_route'][-1];a=cfg['local_frame']['angle'];ox,oy=cfg['local_frame']['origin_xy'];x,y=lower_end[:2]
    endpoint=[ox+math.cos(a)*x-math.sin(a)*y,oy+math.sin(a)*x+math.cos(a)*y]
    report={'status':'PASS_IMPLEMENTED_PROXY_ONLY','simulation_frames':len(trip['trace']),'interlocks':checks,'events':trip['events'],'implemented_endpoint_local':lower_end,'implemented_endpoint_world_xy':endpoint,'market_entrance_connector':'NOT_IMPLEMENTED_NOT_TESTABLE','full_city_high_to_market_route':'NOT_APPROVED','historical_gate':'BLOCKED_EXTERNAL_EVIDENCE','engine_certified':False,'traffic_scope':cfg['proxy_traffic_policy'],'scene_geometry_changed':False}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'numeric.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(report,ensure_ascii=False))


if __name__=='__main__':main()
