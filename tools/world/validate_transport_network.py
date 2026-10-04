"""Valida contrato de vias e bloqueia promoção de tráfego sem evidência completa."""
import argparse
import json
import math
from pathlib import Path


def validate(network):
    errors=[];pending=[]
    roads={r['osm_way_id']:r for r in network['roads']}
    if len(roads)!=len(network['roads']):errors.append('OSM way duplicada')
    edges={e['id']:e for e in network['segments']}
    if len(edges)!=len(network['segments']):errors.append('Segmento duplicado')
    for edge in network['segments']:
        road=roads.get(edge['osm_way_id'])
        if road is None:errors.append(f"{edge['id']}: via sem fonte");continue
        direction=edge['direction_confirmed_from_source']
        if direction!=road['direction']:errors.append(f"{edge['id']}: sentido diverge da fonte")
        if direction is None:pending.append(f"{edge['id']}: sentido sem evidência")
        for lane in edge['lane_preview']:
            if lane['direction']!=direction:errors.append(f"{edge['id']}: faixa fora do sentido registrado")
            if not math.isfinite(lane['offset_osm_right_m']):errors.append(f"{edge['id']}: offset não finito")
            if lane['index_from_driver_right']<1:errors.append(f"{edge['id']}: índice de faixa inválido")
            if lane['bus_preferred'] and lane['index_from_driver_right']!=1:errors.append(f"{edge['id']}: preferência de ônibus fora da direita")
            if lane['approved']:errors.append(f"{edge['id']}: guia candidata promovida a faixa aprovada")
        if edge['traffic_ready']:
            if direction is None or edge['support_issues']:errors.append(f"{edge['id']}: tráfego pronto com sentido/apoio pendente")
            if road['width_status'] not in {'survey_verified','documented_gameplay_adaptation'}:errors.append(f"{edge['id']}: tráfego pronto sem largura justificada")
            if road['lanes_allocation_status'] not in {'verified','documented_gameplay_adaptation'}:errors.append(f"{edge['id']}: tráfego pronto sem distribuição de faixas validada")
        if edge['bus_ready'] and (not network['bus_policy'].get('boarding_side_asset_verified') or not network['bus_policy'].get('asset_front_axis_verified')):errors.append(f"{edge['id']}: lado das portas ou eixo dianteiro do asset não conferido")
        if edge['bus_ready'] and not edge['traffic_ready']:errors.append(f"{edge['id']}: ônibus aprovado sem tráfego aprovado")
        if not edge['traffic_ready']:pending.append(f"{edge['id']}: tráfego candidato")
    issue_ids=[i['issue_id'] for i in network['issues']]
    if len(issue_ids)!=len(set(issue_ids)):errors.append('IDs de falha duplicados')
    for route in network['bus_routes']:
        if route['approved'] and (route['missing_member_way_ids'] or route['missing_stop_member_ids']):errors.append(f"Rota {route['osm_relation_id']} aprovada com lacunas")
        if not route['approved']:pending.append(f"Rota {route['osm_relation_id']} não validada")
        for run in route['clipped_way_runs']:
            order=[m['source_member_index'] for m in run]
            if order!=sorted(order):errors.append('Ordem de membros do itinerário alterada')
    return {'schema':'boas/transport-gate-v1','schema_errors':errors,'pending_checks':len(pending),
            'contract_consistent':not errors,'production_ready':not errors and not pending and network['approved'],
            'checked_ways':len(roads),'checked_segments':len(edges),'status':'error' if errors else 'needs_review' if pending else 'candidate',
            'note':'Contrato consistente não equivale a aprovação das medidas, ruas ou rotas.'}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--network',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--require-production-ready',action='store_true')
    args=parser.parse_args();result=validate(json.loads(args.network.read_text(encoding='utf8')))
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(result,ensure_ascii=False))
    raise SystemExit(1 if result['schema_errors'] else 2 if args.require_production_ready and not result['production_ready'] else 0)
