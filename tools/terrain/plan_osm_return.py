"""Lista conexões reais necessárias ao retorno, sem criar geometria/conexões."""
import json, runpy, math, heapq, itertools
from pathlib import Path
root=Path(__file__).resolve().parents[2]
x=runpy.run_path(str(root/'tools/terrain/plan_real_road_circuit.py'))
g=x['g'];nodes=x['nodes'];tags=x['tags'];tested=x['tested'];ways=x['ways']
adj={}
for e in g['edges']:
    t=tags.get(e['osm_way_id'],{})
    if e.get('access')=='restricted' or any(t.get(k) in ('no','private') for k in ('motor_vehicle','motorcar','vehicle','access')):continue
    if t.get('highway') in ('footway','steps','pedestrian','cycleway','path'):continue
    for a,b,d in [(e['from'],e['to'],'forward'),(e['to'],e['from'],'reverse')]:
        if e['direction'] not in (d,'both'):continue
        adj.setdefault(a,[]).append((b,math.dist(nodes[a]['blender_xy'],nodes[b]['blender_xy']),{**e,'from':a,'to':b,'traversal':d}))
start=x['end'];end=x['start'];counter=itertools.count();q=[(0,next(counter),start,[])];seen=set();route=None
while q:
    cost,_,at,legs=heapq.heappop(q)
    if at==end:route=legs;break
    if at in seen:continue
    seen.add(at)
    for other,d,e in adj.get(at,[]):
        if other not in seen:heapq.heappush(q,(cost+d,next(counter),other,legs+[e]))
out={'capture_id':'aleph-20260924T205631Z-aqqo7pkx','geometry_audit_source':x['r']['source'],'synthetic_edges':0,'status':'real_topology_return_found' if route else 'no_return_in_source','length_m':cost if route else None,'route':[]}
for e in route or []:
    out['route'].append({'edge_id':e['id'],'osm_way_id':e['osm_way_id'],'name':ways[e['osm_way_id']]['name'],'from':e['from'],'to':e['to'],'traversal':e['traversal'],'xy':[nodes[e['from']]['blender_xy'],nodes[e['to']]['blender_xy']],'test':tested.get(e['id']),'width_verified_m':ways[e['osm_way_id']].get('width_m_tagged'),'tags':tags.get(e['osm_way_id'])})
(root/'docs/reports/blender/osm_real_return.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in out.items() if k!='route'},ensure_ascii=False))
print(json.dumps([{k:v for k,v in e.items() if k not in ('tags','test')}|{'geometry':'untested' if e['test'] is None else 'supported' if e['test']['replay_allowed'] else 'blocked'} for e in out['route']],ensure_ascii=False))
