"""Contrato viário candidato e fila de correções reproduzível para qualquer área."""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import statistics
from collections import Counter
from pathlib import Path

try:
    from .build_road_graph import transform_point
    from .extract_osm_structure import mercator
except ImportError:
    from build_road_graph import transform_point
    from extract_osm_structure import mercator

MOTOR_ROADS = {'motorway','trunk','primary','secondary','tertiary','unclassified','residential','service','living_street','track','motorway_link','trunk_link','primary_link','secondary_link','tertiary_link'}


def positive_number(value, integer=False):
    if value is None:
        return None
    try:
        number = float(str(value).strip().removesuffix(' m').replace(',', '.'))
    except (ValueError, TypeError):
        return None
    if not math.isfinite(number) or number <= 0 or integer and not number.is_integer():
        return None
    return int(number) if integer else number


def semantics(tags):
    raw = str(tags.get('oneway','')).lower()
    if raw in {'yes','1','true'}:
        direction, basis = 'forward', 'oneway_explicit'
    elif raw == '-1':
        direction, basis = 'reverse', 'oneway_explicit'
    elif raw in {'no','0','false'}:
        direction, basis = 'both', 'oneway_explicit'
    elif tags.get('junction') == 'roundabout':
        direction, basis = 'forward', 'roundabout_osm_convention'
    else:
        direction, basis = None, 'missing_or_unsupported_tag'
    total = positive_number(tags.get('lanes'), integer=True)
    forward = positive_number(tags.get('lanes:forward'), integer=True)
    backward = positive_number(tags.get('lanes:backward'), integer=True)
    if direction == 'forward' and total is not None:
        forward, backward = total, 0
    elif direction == 'reverse' and total is not None:
        forward, backward = 0, total
    errors=[]
    if direction == 'both' and total is not None and total < 2:
        errors.append('single_lane_bidirectional_requires_passing_policy')
    if forward is not None and backward is not None and total is not None and forward+backward != total:
        errors.append('directional_lane_count_conflict')
    # A modal exception overrides general restrictions only for that mode.
    bus_access = next((tags[k] for k in ('bus','psv','motor_vehicle','vehicle','access') if k in tags), None)
    motor_access = next((tags[k] for k in ('motorcar','motor_vehicle','vehicle','access') if k in tags), None)
    motor_road = tags.get('highway') in MOTOR_ROADS
    return {'direction':direction,'direction_basis':basis,'direction_status':'source_tagged_not_field_verified' if direction else 'pending',
            'lanes_total_tagged':total,'lanes_forward':forward,'lanes_backward':backward,
            'lanes_allocation_status':'source_tagged' if forward is not None and backward is not None else 'pending',
            'width_tagged_m':positive_number(tags.get('width')),'real_width_verified_m':None,
            'motor_road_candidate':motor_road,'motor_access_raw':motor_access,'bus_access_raw':bus_access,
            'bus_candidate':motor_road and bus_access not in {'no','private'},
            'oneway_bus_raw':tags.get('oneway:bus',tags.get('oneway:psv')),
            'bus_lane_tags':{k:v for k,v in tags.items() if 'busway' in k or k.startswith(('bus:lanes','psv:lanes','lanes:bus'))},
            'conditional_tags':{k:v for k,v in tags.items() if ':conditional' in k},'issues':errors}


def build(area_id, graph, source, widths, supports, turns, bus_profile, fit):
    ways = {w['osm_way_id']:w for w in graph['ways']}
    tags = {w['id']:w['tags'] for w in source['ways']}
    width_edges = {e['edge_id']:e for e in widths['segments']}
    support_edges = {e['edge_id']:e for e in supports['segments']}
    nodes = {str(n['id']):n for n in graph['nodes']}
    issues=[]
    def issue(kind, entity, priority, classification, evidence, action):
        issues.append({'issue_id':f'{area_id}/{entity}/{kind}','priority':priority,'classification':classification,
                       'status':'pending','evidence':evidence,'required_action':action,'acceptance':None})
    road_records=[]
    for oid, way in ways.items():
        raw = tags.get(oid,{})
        sem = semantics(raw)
        rows = [e for e in widths['segments'] if e['osm_way_id']==oid]
        values = [s['width_m'] for e in rows for s in e['stations'] if s['width_m'] is not None]
        road_records.append({'osm_way_id':oid,'name':way.get('name'),'source_tags':raw,**sem,
                             'scene_width_summary_m':{'minimum':min(values),'median':statistics.median(values),'maximum':max(values),'stations':len(values)} if values else None,
                             'width_status':'scene_only_reference_missing' if sem['width_tagged_m'] is None else 'osm_tagged_not_surveyed',
                             'approved':False})
        if sem['width_tagged_m'] is None:
            issue('real_width_source_missing',f'way-{oid}',2,'SOURCE_LIMITATION',{'width_tag':None},'Obter largura útil entre bordos com fonte/licença e incerteza; separar calçadas, estacionamento e canteiro. Não usar classe highway para redimensionar.')
        if sem['direction'] is None:
            issue('direction_source_missing',f'way-{oid}',3,'SOURCE_LIMITATION',{'oneway':raw.get('oneway')},'Conferir sinalização/fonte de tráfego; ausência de oneway não comprova mão dupla.')
        for kind in sem['issues']:
            issue(kind,f'way-{oid}',3,'NEEDS_REVIEW',{'lanes':raw.get('lanes')},'Conferir distribuição de faixas e operação; não dividir automaticamente nem alargar.')
    road_lookup={w['osm_way_id']:w for w in road_records}
    segments=[]
    for edge in graph['edges']:
        eid=edge['id']; road=road_lookup[edge['osm_way_id']]; support=support_edges.get(eid)
        width=width_edges.get(eid); lanes=[]
        # Equal divisions are preview candidates, restricted to explicit one-way roads.
        # They never become traffic/runtime lanes or real-width evidence automatically.
        if road['direction'] in {'forward','reverse'} and road['lanes_total_tagged'] and width:
            for station in width['stations']:
                count=road['lanes_total_tagged']; total=station['width_m']
                if total is None or station['issues']:continue
                for lane in range(1,count+1):
                    right=station['right_from_osm_axis_m'];left=station['left_from_osm_axis_m']
                    offset=right-total*(lane-.5)/count if road['direction']=='forward' else -left+total*(lane-.5)/count
                    lanes.append({'fraction':station['fraction'],'index_from_driver_right':lane,'direction':road['direction'],
                                  'offset_osm_right_m':offset,'candidate_equal_lane_width_m':total/count,
                                  'bus_preferred':lane==1 and road['bus_candidate'],'status':'preview_candidate','approved':False})
        nominal_bus_width=bus_profile['width']
        right_samples=[p for p in lanes if p['index_from_driver_right']==1]
        narrow=[p for p in right_samples if p['candidate_equal_lane_width_m']<nominal_bus_width+.30]
        if narrow:
            issue('bus_lane_width_probe_review',f"way-{edge['osm_way_id']}/nodes-{edge['from']}-{edge['to']}",1,'NEEDS_REVIEW',{'minimum_candidate_lane_width_m':min(p['candidate_equal_lane_width_m'] for p in narrow),'nominal_bus_width_m':nominal_bus_width,'clearance_each_side_probe_m':.15},'Medir limite útil e faixas reais; testar envelope do ônibus e calçada. Não alargar por divisão igual candidata.')
        segment_issues=support['issues'] if support else {'support_audit_missing':1}
        for kind, count in segment_issues.items():
            priority=0 if kind in {'vertical_discontinuity','center_support_missing','wheel_support_missing','collision_support_missing'} else 1
            issue(kind,f"way-{edge['osm_way_id']}/nodes-{edge['from']}-{edge['to']}",priority,'NEEDS_REVIEW',{'occurrences':count,'support_report_edge':eid},'Inspecionar mesma camada e OSM ID; corrigir causa comprovada e repetir quatro apoios, colisor e limites. Não ligar através de lacuna.')
        segments.append({**edge,'direction_confirmed_from_source':road['direction'],'motor_road_candidate':road['motor_road_candidate'],
                         'bus_candidate':road['bus_candidate'],'support_issues':segment_issues,'lane_preview':lanes,
                         'bus_lane_width_probe_passed':bool(right_samples) and not narrow,'traffic_ready':False,'bus_ready':False})
    for turn in turns['turns']:
        for kind in turn['issues']:
            issue(kind,f"node-{turn['node_id']}/turn-{turn['from']}--{turn['to']}",1,'NEEDS_REVIEW',{'radius_m':turn.get('minimum_radius_m')},'Verificar raio e envelope completo de Rondesp e ônibus; preservar limites de pavimento, sentidos, restrições e cruzamento.')
    # Clip ordered route membership without joining across missing members.
    routes=[]
    for route in source['bus_routes']:
        ordered=[(i,m) for i,m in enumerate(route['members']) if m['type']=='way']
        runs=[];current=[];missing=[]
        for order,member in ordered:
            oid=int(member['ref'])
            if oid not in ways:
                missing.append(oid)
                if current:runs.append(current);current=[]
                continue
            current.append({'source_member_index':order,'osm_way_id':oid,'role':member.get('role',''),'direction':road_lookup[oid]['direction']})
        if current:runs.append(current)
        if not runs:continue
        known_stops={str(s['id']) for s in source['stops']}
        stop_members=[m for m in route['members'] if m.get('role','').startswith(('stop','platform'))]
        connections=[]
        for run in runs:
            for left,right in zip(run,run[1:]):
                a=ways[left['osm_way_id']]['node_refs'];b=ways[right['osm_way_id']]['node_refs']
                end=a[-1] if left['direction']=='forward' else a[0] if left['direction']=='reverse' else None
                start=b[0] if right['direction']=='forward' else b[-1] if right['direction']=='reverse' else None
                connections.append({'from_way':left['osm_way_id'],'to_way':right['osm_way_id'],'shared_directed_node':end if end is not None and end==start else None,'status':'source_endpoint_match_needs_scene_turn_qa' if end is not None and end==start else 'pending_direction_or_endpoint'})
        routes.append({'osm_relation_id':route['id'],'ref':route['tags'].get('ref'),'name':route['tags'].get('name'),
                       'source_tags':route['tags'],'clipped_way_runs':runs,'missing_member_way_ids':missing,
                       'directed_connections':connections,'stop_members':stop_members,'missing_stop_member_ids':[m['ref'] for m in stop_members if m['ref'] not in known_stops],
                       'status':'partial_source_not_current_itinerary_verified','approved':False})
    # Positions use the recorded transform; candidate proximity never binds a stop.
    stop_records=[]
    for stop in source['stops']:
        xy=transform_point(mercator(stop['lat'],stop['lon']),fit['robust_fit'])
        possible=[]
        for edge in graph['edges']:
            road=road_lookup[edge['osm_way_id']]
            if not road['bus_candidate'] or road['direction'] not in {'forward','reverse'}:continue
            a=nodes[edge['from']]['blender_xy'];b=nodes[edge['to']]['blender_xy']
            dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy)
            if length<.01:continue
            t=((xy[0]-a[0])*dx+(xy[1]-a[1])*dy)/(length*length)
            if not 0<=t<=1:continue
            q=(a[0]+dx*t,a[1]+dy*t);distance=math.dist(xy,q)
            if distance>20:continue
            side=((xy[0]-q[0])*dy-(xy[1]-q[1])*dx)/length
            if road['direction']=='reverse':side=-side
            possible.append({'edge_id':edge['id'],'osm_way_id':edge['osm_way_id'],'fraction':t,'distance_axis_m':distance,'side_in_travel_direction':'right' if side>0 else 'left','signed_right_distance_m':side,'status':'candidate_proximity_not_binding'})
        stop_records.append({**stop,'blender_xy_reference':xy,'bound_lane_id':None,'binding_status':'pending','candidate_road_bindings':sorted(possible,key=lambda c:c['distance_axis_m'])[:3]})
    restrictions=[]
    for item in source['restrictions']:
        relevant=any(m['type']=='way' and int(m['ref']) in ways for m in item['members'])
        if relevant:
            unresolved=[m for m in item['members'] if m['type']=='way' and int(m['ref']) not in ways or m['type']=='node' and m['ref'] not in nodes]
            restrictions.append({**item,'unresolved_members':unresolved,'status':'pending_binding' if unresolved else 'source_reference_requires_turn_binding'})
    return {'schema':'boas/transport-network-candidate-v1','area_id':area_id,'status':'candidate','approved':False,
            'source':source['source'],'bus_profile_nominal':bus_profile,'roads':road_records,'segments':segments,'bus_routes':routes,'stops':stop_records,
            'turn_restrictions':restrictions,'issues':issues,
            'bus_policy':{'preferred_lane':'rightmost_in_travel_direction','boarding_side':'right','boarding_side_asset_verified':False,'asset_front_axis_verified':False,'exception_policy':'Conversões, faixas exclusivas, obstáculos e terminais exigem exceções documentadas; preferência não obriga permanência absoluta à direita.',
                          'boarding_gates':['Continuidade dirigida do itinerário e conversões legais vinculadas','Portas à direita alinhadas com plataforma e calçada confirmadas','Aproximação e saída junto ao meio-fio, com envelope completo varrido','Quatro apoios, colisor e folga completa na via e cruzamentos','Acesso de pedestres sem atravessar a pista oposta','Evidência atual de itinerário e parada com proveniência'],
                          'stops_bound_to_roads':False,'routes_ready':False,'bus_swept_envelope_status':'pending_nominal_profile_only'},
            'summary':{'ways':len(road_records),'segments':len(segments),'explicit_forward_ways':sum(r['direction']=='forward' for r in road_records),
                       'explicit_bidirectional_ways':sum(r['direction']=='both' for r in road_records),'unknown_direction_ways':sum(r['direction'] is None for r in road_records),
                       'real_widths_verified':0,'lane_preview_samples':sum(len(e['lane_preview']) for e in segments),'bus_source_routes_in_graph':len(routes),'bus_source_stops':len(source['stops']),
                       'issue_counts':dict(Counter(i['priority'] for i in issues))},
            'limitations':['Centros de faixa candidatos por divisão igual do pavimento autoral; não são marcação medida ou tráfego aprovado.',
                           'A captura OSM não comprova sentidos/itinerários atuais. Dados desconhecidos permanecem null/pending.',
                           'Sem física veicular, varredura volumétrica de ônibus, exportação runtime ou ajuste por largura real.']}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for flag in ('graph','source','widths','supports','turns','output'):
        parser.add_argument('--'+flag,type=Path,required=True)
    parser.add_argument('--area-id',required=True)
    parser.add_argument('--production-contract',type=Path,required=True)
    parser.add_argument('--fit',type=Path,required=True)
    parser.add_argument('--preservation-report',type=Path,help='Prova de pavimento visual preservado entre revisões diferentes')
    args=parser.parse_args()
    inputs={k:json.loads(getattr(args,k).read_text(encoding='utf8')) for k in ('graph','source','widths','supports','turns')}
    assert hashlib.sha256(args.graph.read_bytes()).hexdigest()==inputs['source']['source']['graph_sha256'], 'Referência OSM pertence a outro grafo; reextrair'
    width_source=inputs['widths']['source'];support_source=inputs['supports']['source_before']
    if width_source['sha256']!=support_source['sha256']:
        assert args.preservation_report, 'Relatórios de cenas diferentes sem prova de preservação'
        preservation=json.loads(args.preservation_report.read_text(encoding='utf8'))
        assert preservation['source_before']['sha256']==width_source['sha256'] and preservation['source_after']['sha256']==support_source['sha256']
        assert not preservation['road_widths_changed'] and not preservation['protected_visual_differences'] and preservation['source_reopened']
    bus_profile=json.loads(args.production_contract.read_text(encoding='utf8'))['vehicle']['dimensions']
    assert positive_number(bus_profile['width']), 'Perfil nominal do ônibus sem largura'
    fit=json.loads(args.fit.read_text(encoding='utf8'))
    data=build(args.area_id,**inputs,bus_profile=bus_profile,fit=fit)
    data['georef_fit_sha256']=hashlib.sha256(args.fit.read_bytes()).hexdigest()
    data['georef_fit_quality']=fit.get('quality')
    data['input_hashes']={k:hashlib.sha256(getattr(args,k).read_bytes()).hexdigest() for k in inputs}
    data['input_hashes']['production_contract']=hashlib.sha256(args.production_contract.read_bytes()).hexdigest()
    data['scene_source']=support_source
    data['width_audit_source']=width_source
    data['width_geometry_preserved_report']=args.preservation_report.resolve().relative_to(Path(__file__).resolve().parents[2]).as_posix() if args.preservation_report else None
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(data['summary'],ensure_ascii=False))


if __name__=='__main__':main()
