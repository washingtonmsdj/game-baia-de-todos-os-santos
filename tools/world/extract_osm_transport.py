"""Extrai sentidos, faixas, ônibus e restrições da captura OSM, sem inventar dados."""
from __future__ import annotations
import argparse
import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path


def extract(osm: Path, graph: dict) -> dict:
    way_ids = {int(w['osm_way_id']) for w in graph['ways']}
    ways, stops, routes, restrictions = [], [], [], []
    for _, element in ET.iterparse(osm, events=('end',)):
        if element.tag not in {'node', 'way', 'relation'}:
            continue
        tags = {c.attrib['k']: c.attrib['v'] for c in element if c.tag == 'tag'}
        oid = int(element.attrib['id'])
        members = [dict(c.attrib) for c in element if c.tag == 'member']
        if element.tag == 'way' and oid in way_ids:
            ways.append({'id': oid, 'tags': tags, 'node_refs': [c.attrib['ref'] for c in element if c.tag == 'nd']})
        if element.tag == 'node' and (tags.get('highway') == 'bus_stop' or tags.get('bus') == 'yes' and tags.get('public_transport') in {'platform', 'stop_position'}):
            stops.append({'id': oid, 'lat': float(element.attrib['lat']), 'lon': float(element.attrib['lon']), 'tags': tags})
        if element.tag == 'relation' and tags.get('route') == 'bus':
            routes.append({'id': oid, 'tags': tags, 'members': members})
        if element.tag == 'relation' and tags.get('type') == 'restriction':
            restrictions.append({'id': oid, 'tags': tags, 'members': members})
        element.clear()
    return {'schema': 'boas/osm-transport-source-v1', 'status': 'reference_not_current_operation_verified',
            'source': {'file_name': osm.name, 'sha256': hashlib.sha256(osm.read_bytes()).hexdigest(), 'license': 'OpenStreetMap ODbL; atribuição obrigatória', 'scope': 'Ways do grafo; relações e paradas da captura, não itinerários completos aprovados.'},
            'ways': ways, 'stops': stops, 'bus_routes': routes, 'restrictions': restrictions}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--osm', type=Path, required=True)
    parser.add_argument('--graph', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--capture-id', help='ID da captura registrada; ausente permanece null')
    args = parser.parse_args()
    result = extract(args.osm, json.loads(args.graph.read_text(encoding='utf8')))
    result['source']['capture_id'] = args.capture_id
    result['source']['graph_sha256'] = hashlib.sha256(args.graph.read_bytes()).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
    print(json.dumps({key: len(result[key]) for key in ('ways', 'stops', 'bus_routes', 'restrictions')}))
