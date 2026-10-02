"""Inspeciona o retorno real no grafo, sem criar conexões por proximidade."""
import runpy,json
from pathlib import Path
root=Path(__file__).resolve().parents[2];x=runpy.run_path(str(root/'tools/terrain/plan_real_road_circuit.py'))
g=x['g'];r=x['r'];nodes=x['nodes'];ways=x['ways'];edges=x['edges'];tested=x['tested'];tags=x['tags'];result=[]
for id in (r['replay_route_edges'][-1],r['replay_route_edges'][-2]):
    end=edges[id]['to'];reachable={end};queue=[end]
    while queue:
        node=queue.pop()
        for other,_,arc in x['adj'].get(node,[]):
            if other not in reachable:reachable.add(other);queue.append(other)
    border=[]
    for e in g['edges']:
        arcs=[]
        if e['direction'] in ('forward','both'):arcs.append((e['from'],e['to']))
        if e['direction'] in ('reverse','both'):arcs.append((e['to'],e['from']))
        for a,b in arcs:
            if a in reachable and b not in reachable:border.append({'edge':e,'name':ways[e['osm_way_id']]['name'],'highway':ways[e['osm_way_id']]['highway'],'a':nodes[a]['blender_xy'],'b':nodes[b]['blender_xy'],'tags':tags.get(e['osm_way_id']), 'test':tested.get(e['id'])})
    result.append({'end_after_edge':id,'node':nodes[end],'reachable_nodes':len(reachable),'border':border})
(root/'docs/reports/blender/real_road_return_gaps.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(result,ensure_ascii=False))
