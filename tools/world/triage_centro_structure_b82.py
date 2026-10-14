"""Triagem auditável dos alertas B41 contra inventário B82 e SSOT, sem mutação."""
import collections,json,math,re,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from tools.georef.world_reference import project_reference
OUT=ROOT/'docs/reports/world/centro-structural-triage'
CATEGORIES=['XY_OFFSET','TOPOLOGY','ROAD_ALIGNMENT','BUILDING_FOOTPRINT','TERRAIN_INTERSECTION','DUPLICATE','LEGACY_PROXY','HEIGHT_UNKNOWN','EXPECTED_OVERLAP','FALSE_POSITIVE','NEEDS_REVIEW']

def read(p):return json.loads((ROOT/p).read_text(encoding='utf8'))
def write(name,d):
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/name).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def average(pts):return [sum(p[i] for p in pts)/len(pts) for i in range(2)] if pts else None
def distance(p,a,b):
    dx,dy=b[0]-a[0],b[1]-a[1];t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/(dx*dx+dy*dy))) if dx*dx+dy*dy else 0
    return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)
def poly_distance(p,sp):return min((distance(p,a,b) for line in sp for a,b in zip(line,line[1:])),default=None)
def bounds(pts):return {'min':[min(p[i] for p in pts) for i in range(2)],'max':[max(p[i] for p in pts) for i in range(2)]}
def intersects(a,b):return all(a['min'][i]<b['max'][i] and b['min'][i]<a['max'][i] for i in range(2))
def inside(p,poly):
    if min(distance(p,a,b) for a,b in zip(poly,poly[1:]))<.01:return False
    result=False
    for a,b in zip(poly,poly[1:]):
        if (a[1]>p[1])!=(b[1]>p[1]) and p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0]:result=not result
    return result

def main():
    ssot=project_reference(ROOT,read('artifacts/structural-pipeline/centro-lapa-tororo-fontenova/georef_fit.json')['robust_fit'])
    features=read('artifacts/structural-pipeline/centro-lapa-tororo-fontenova/structural_reference.json')['features']
    byway={f['osm_id']:f for f in features if f['osm_type']=='way'}
    graph=read('prototypes/threejs-water-lab/public/data/road_graph.json')
    ways={w['osm_way_id']:w for w in graph['ways']};nodes={str(n['id']):n['blender_xy'] for n in graph['nodes']}
    objects=read('docs/reports/world/centro-structural-triage/scene_b82.json')['objects']
    helpers={int(o['properties']['boas_osm_way_id']):o for o in objects if o['name'].startswith('R30A7 | ROAD |') and 'boas_osm_way_id' in o['properties']}
    # Áreas analíticas de proximidade, nunca limites administrativos ou novo SSOT.
    anchors={'TOME_RUA_CHILE':[30968017,231091547,258560240],
             'CAIRU_MERCADO':[59392558,312006925,1423065746],
             'PELOURINHO':[803899195,530127468,578704834],
             'BARROQUINHA':[390875490,562012564]}
    targets={key:[p for oid in ids if oid in byway for p in byway[oid]['blender_xy']] for key,ids in anchors.items()}
    def area(xy):
        if xy is None:return 'UNLOCATED'
        scores={k:min(math.dist(xy,p) for p in pts) for k,pts in targets.items() if pts}
        k=min(scores,key=scores.get)
        return k if scores[k]<=180 else 'OTHER_CENTRO_RECUT'
    ledger=read('world/areas/mvp-centro-lacerda/road-corrections.json')
    pending=[r for r in ledger['issues'] if r['status']!='resolved'];assert len(pending)==714
    records=[]
    road_kinds={'wheel_outside_pavement','center_outside_pavement','wheel_outside_pavement_or_layer','steering_radius_review','bus_lane_width_probe_review'}
    height_kinds={'crossfall_review','four_wheel_twist','grade_review','vertical_discontinuity'}
    for row in pending:
        iid=row['issue_id'];kind=iid.rsplit('/',1)[-1]
        match=re.search(r'/way-(\d+)',iid);oid=int(match[1]) if match else None
        refs=re.search(r'/nodes-(\d+)-(\d+)',iid);nids=list(refs.groups()) if refs else []
        if not nids:
            m=re.search(r'/node-(\d+)',iid);nids=[m[1]] if m else []
        xy=average([nodes[n] for n in nids if n in nodes]) or average(ways.get(oid,{}).get('blender_xy',[]))
        category='ROAD_ALIGNMENT' if kind in road_kinds else 'HEIGHT_UNKNOWN' if kind in height_kinds else 'LEGACY_PROXY' if kind in {'scene_binding_missing','unresolved_endpoint_binding'} else 'NEEDS_REVIEW'
        source=byway.get(oid);helper=helpers.get(oid);evidence={};root=None
        if kind=='unresolved_endpoint_binding' and helper and nids and all(n in nodes for n in nids):
            pts=[p for line in helper.get('splines',[]) for p in line]
            evidence={'node_vertex_distances': [min((math.dist(nodes[n],p[:2]) for p in pts),default=None) for n in nids],
                      'node_curve_distances':[poly_distance(nodes[n],helper.get('splines',[])) for n in nids],
                      'helper':helper['name'],'source_way_nodes_present':bool(source and source.get('missing_node_ref_count')==0),
                      'genealogy':'automation/blender/r30a7_road_graph.py#create_way'}
            if any(d is not None and d>.02 for d in evidence['node_vertex_distances']):root='LEGACY_HELPER_OMITS_SOURCE_NODES_WHEN_SUPPORT_MISSING'
        elif kind=='scene_binding_missing' and helper is None:
            root='LEGACY_HELPER_ABSENT_IN_AUDITOR_PREFIX'
            evidence={'helper_present':False,'source_way_present':source is not None,'genealogy':'automation/blender/audit_rondesp_network.py'}
        elif kind in {'real_width_source_missing','direction_source_missing'}:
            tag='width' if kind=='real_width_source_missing' else 'oneway';value=source.get('tags',{}).get(tag) if source else None
            evidence={'source_tag':tag,'value':value,'source_way_present':source is not None}
            if source and value is None:root='SOURCE_WIDTH_NOT_DOCUMENTED' if tag=='width' else 'SOURCE_DIRECTION_NOT_DOCUMENTED'
        records.append({'issue_id':iid,'original_kind':kind,'original_classification':row['classification'],
                        'category':category,'category_is_investigation_family':True,'confirmed_geometry_error':False,
                        'subarea':area(xy),'subarea_basis':'closest documented OSM controls within 180 Blender units; analytical only',
                        'xy':xy,'osm_way_id':oid,'node_ids':nids,'confirmed_root':root,'evidence':evidence,
                        'status':'pending','automatic_scene_correction_allowed':False})
    counts={k:sum(r['category']==k for r in records) for k in CATEGORIES}
    areas={a:{k:sum(r['subarea']==a and r['category']==k for r in records) for k in CATEGORIES} for a in sorted({r['subarea'] for r in records})}
    groups=[]
    for root in sorted({r['confirmed_root'] for r in records if r['confirmed_root']}):
        rs=[r for r in records if r['confirmed_root']==root]
        groups.append({'cause':root,'count':len(rs),'issue_ids':[r['issue_id'] for r in rs],
                       'geometry_error_proven':False,'resolution':'Review source metadata or helper coverage; do not move world geometry'})
    # Conferir XY dos helpers em todos os vértices existentes contra o SSOT já adotado.
    xy_checks=[]
    for oid,ob in helpers.items():
        f=byway.get(oid)
        if not f:continue
        sp=[f['blender_xy']];points=[p for line in ob.get('splines',[]) for p in line]
        errors=[poly_distance(p[:2],sp) for p in points];errors=[e for e in errors if e is not None]
        xy_checks.append({'osm_way_id':oid,'helper':ob['name'],'samples':len(errors),'max_distance_to_source':max(errors,default=None),'area':area(average(f['blender_xy']))})
    # Footprint/centerline: evidência 2D de fonte, NÃO colisão ou erro confirmado.
    buildings=[f for f in features if f['layer']=='buildings' and f.get('closed') and len(f['blender_xy'])>=4 and intersects(bounds(f['blender_xy']),{'min':[-450,-550],'max':[700,650]})]
    roads=[f for f in features if f['layer'] in {'roads','pedestrian','steps'} and len(f['blender_xy'])>=2 and intersects(bounds(f['blender_xy']),{'min':[-450,-550],'max':[700,650]})]
    overlap=[]
    for b in buildings:
        bb=bounds(b['blender_xy'])
        for road in roads:
            if not intersects(bb,bounds(road['blender_xy'])):continue
            if any(inside(p,b['blender_xy']) for p in road['blender_xy']):
                tags=road.get('tags',{});separated=bool(tags.get('tunnel') or tags.get('bridge') or tags.get('covered') or tags.get('layer'))
                overlap.append({'building':[b['osm_type'],b['osm_id']],'road':[road['osm_type'],road['osm_id']],
                                'road_name':tags.get('name'),'area':area(average(road['blender_xy'])),
                                'classification':'EXPECTED_OVERLAP' if separated else 'NEEDS_REVIEW','cause_confirmed':False,
                                'reason':'Source node strictly inside footprint; vertical layer and access must be checked'})
    topology=read('artifacts/structural-pipeline/centro-lapa-tororo-fontenova/osm_topology_audit.json')
    # Conectividade da referência por IDs compartilhados; sem ligar pontos próximos.
    adj=collections.defaultdict(set);nodeways=collections.defaultdict(set)
    for f in roads:
        refs=[str(n) for n in f['node_refs']]
        for n in refs:nodeways[n].add(f['osm_id'])
        for a,b in zip(refs,refs[1:]):adj[a].add(b);adj[b].add(a)
    comps=[];visited=set()
    for start in adj:
        if start in visited:continue
        todo=[start];visited.add(start);ns=[]
        while todo:
            n=todo.pop();ns.append(n)
            for other in adj[n]-visited:visited.add(other);todo.append(other)
        comps.append(ns)
    membership={n:i for i,c in enumerate(comps) for n in c}
    anchor_components={k:sorted({membership[str(n)] for oid in ids if oid in byway for n in byway[oid]['node_refs'] if str(n) in membership}) for k,ids in anchors.items()}
    shared=set(anchor_components['TOME_RUA_CHILE'])&set(anchor_components['PELOURINHO'])&set(anchor_components['BARROQUINHA'])
    summary={'schema':'boas/centro-structural-triage-v1','baseline_cycle':ledger['cycle'],'scene':'B82 read-only historical layer',
             'pending_alerts':len(records),'counts_by_category':counts,'counts_by_subarea':areas,'false_positives_proven':0,
             'root_groups':groups,'alerts_with_shared_confirmed_root':sum(g['count'] for g in groups),
             'ssot_sha256':hashlib.sha256((ROOT/'world/geographic-reference.json').read_bytes()).hexdigest(),
             'classification_note':'Investigation families are not confirmed geometric causes. Zero is no proof found, not certification of absence.',
             'xy_helper_checks':xy_checks,'source_topology_summary_full_extract':topology['summary'],
             'topology_anchor_components':anchor_components,'upper_reference_connected':bool(shared),
             'physical_pedestrian_continuity_certified':False,'b82_proxy_route_preserved':True,
             'footprint_centerline_candidates':len(overlap),'scene_changed':False,'new_revision':None,
             'expanded_map':'GREYBOX','lacerda_vertical':'BLOCKED_EXTERNAL_EVIDENCE','production_promoted':False,
             'next_cluster':'TOME_RUA_CHILE: fonte XY → helper parcial → superfície visual/collider → calçada, antes de Pelourinho/Barroquinha'}
    write('triage.json',{'summary':summary,'alerts':records})
    write('source_footprint_candidates.json',{'note':'Independent source-layer candidates; not included in the 714, not bugs, no Blender triangle-intersection approval','pairs':overlap})
    print(json.dumps({k:summary[k] for k in ['pending_alerts','counts_by_category','counts_by_subarea','alerts_with_shared_confirmed_root','upper_reference_connected','footprint_centerline_candidates']},ensure_ascii=False))

if __name__=='__main__':main()
