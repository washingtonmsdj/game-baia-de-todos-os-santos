"""Procura retorno pela rede OSM existente; nunca acrescenta arestas fictícias."""
import json,math,heapq,itertools
from pathlib import Path
root=Path(__file__).resolve().parents[2];c=json.loads((root/'world/areas/mvp-centro-lacerda/production.json').read_text())
g=json.loads((root/c['staging']['roads']).read_text());nodes={n['id']:n for n in g['nodes']};ways={w['osm_way_id']:w for w in g['ways']};edges={e['id']:e for e in g['edges']}
r=json.loads((root/'docs/reports/blender/terrain_vehicle_replay_r30b29.json').read_text());tested={s['edge_id']:s for s in r['segments']}
st=json.loads((root/'artifacts/structural-pipeline/mvp-centro-lacerda/osm_structure.json').read_text());tags={f['osm_id']:f['tags'] for f in st['features'] if f['layer']=='roads'}
adj={};excluded=[]
for e in g['edges']:
    t=tags.get(e['osm_way_id'],{});s=tested.get(e['id'])
    if e.get('access')=='restricted' or any(t.get(k) in ('no','private') for k in ('motor_vehicle','motorcar','vehicle','access')):continue
    if not s or not s.get('replay_allowed'):excluded.append(e['id']);continue
    a=nodes[e['from']]['blender_xy'];b=nodes[e['to']]['blender_xy'];length=math.dist(a,b)
    if e['direction'] in ('forward','both'):
        adj.setdefault(e['from'],[]).append((e['to'],length,{'edge_id':e['id'],'from':e['from'],'to':e['to'],'traversal':'forward'}))
    if e['direction'] in ('reverse','both'):
        adj.setdefault(e['to'],[]).append((e['from'],length,{'edge_id':e['id'],'from':e['to'],'to':e['from'],'traversal':'reverse'}))
def path(start,end):
    counter=itertools.count();queue=[(0,next(counter),start,[])];best={start:0}
    while queue:
        cost,_,node,route=heapq.heappop(queue)
        if node==end:return route,cost
        if cost>best.get(node,float('inf')):continue
        for other,length,arc in adj.get(node,[]):
            d=cost+length
            if d<best.get(other,float('inf')):best[other]=d;heapq.heappush(queue,(d,next(counter),other,route+[arc]))
    return None,None
main=[]
for id in r['replay_route_edges']:
    e=edges[id]
    if e['direction']=='reverse':raise RuntimeError('Replay histórico contém sentido contrário ao OSM: '+id)
    main.append({'edge_id':id,'from':e['from'],'to':e['to'],'traversal':'forward'})
start=main[0]['from'];end=main[-1]['to'];back,cost=path(end,start);route=main+(back or [])
leg=[]
for arc in route:
    e=edges[arc['edge_id']];w=ways[e['osm_way_id']];leg.append({**arc,'osm_way_id':e['osm_way_id'],'street':w['name'],'direction':e['direction'],'width_verified_m':w.get('width_m_tagged'),'geometry_status':'existing_authored_pavement','source_access_status':e.get('access')})
out={'source':c['world_source'],'geometry_audit_source':r['source'],'source_capture_id':'aleph-20260924T205631Z-aqqo7pkx','source_graph':'prototypes/threejs-water-lab/public/data/road_graph.json','kind':'verification_circuit_on_existing_osm_roads; not a registered public bus line','status':'candidate_closed' if back else 'open_no_verified_geometric_return','synthetic_edges':0,'roads_added':False,'road_widths_changed':False,'start_node':start,'end_node':end,'return_length_m':cost,'total_length_m':sum(math.dist(nodes[i['from']]['blender_xy'],nodes[i['to']]['blender_xy']) for i in route),'route':leg,'excluded_uncovered_or_blocked_edges':excluded,'bus_clearance_tested':False,'public_bus_route_verified':False}
directory=root/'docs/reports/blender';(directory/'real_road_circuit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in out.items() if k not in ('route','excluded_uncovered_or_blocked_edges')},ensure_ascii=False));print(json.dumps([(v['street'],v['edge_id']) for v in leg[len(main):]],ensure_ascii=False))
