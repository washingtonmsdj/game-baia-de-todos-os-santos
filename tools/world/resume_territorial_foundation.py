"""Retoma fila estrutural existente, sem reconstruir B76 nem resolver alertas em massa."""
import json,hashlib,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]


def read(path):return json.loads((ROOT/path).read_text(encoding='utf8'))
def write(path,value):
    file=ROOT/path;file.parent.mkdir(parents=True,exist_ok=True)
    file.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')


def main():
    ssot=read('world/geographic-reference.json')
    reference=read('artifacts/structural-pipeline/centro-lapa-tororo-fontenova/structural_reference.json')
    fit=read('artifacts/structural-pipeline/centro-lapa-tororo-fontenova/georef_fit.json')['robust_fit']
    # Reutilizar guard existente: proíbe fit regional independente.
    import sys
    sys.path.insert(0,str(ROOT))
    from tools.georef.world_reference import project_reference
    project_reference(ROOT,fit)
    by_way={f['osm_id']:f for f in reference['features'] if f['osm_type']=='way'}
    by_feature={(f['osm_type'],f['osm_id']):f for f in reference['features']}
    ledgers={area:read(f'world/areas/{area}/road-corrections.json') for area in ['mvp-centro-lacerda','centro-lapa-tororo-fontenova']}
    priority=[{'order':1,'region':'Centro Histórico','area':'mvp-centro-lacerda','locations':[]},
              {'order':2,'region':'Lapa / Campo da Pólvora','area':'centro-lapa-tororo-fontenova','locations':['center-lapa','campo-da-polvora']},
              {'order':3,'region':'Dique do Tororó','area':'centro-lapa-tororo-fontenova','locations':['dique-do-tororo']},
              {'order':4,'region':'Arena Fonte Nova','area':'centro-lapa-tororo-fontenova','locations':['arena-fonte-nova']}]
    catalog=read('world/areas/centro-lapa-tororo-fontenova/locations.json')
    location_priority={key:p['order'] for p in priority for key in p['locations']}
    for location in catalog['locations']:
        if location['location_id'] in location_priority:
            location['priority']=location_priority[location['location_id']]
            location['production_rules']['current_stage']='STRUCTURAL_GREYBOX'
            location['production_rules']['detailed_architecture_allowed']=False
    write('world/areas/centro-lapa-tororo-fontenova/locations.json',catalog)
    stages=[]
    for group in priority:
        issues=[x for x in ledgers[group['area']]['issues'] if x.get('status')!='resolved' and (not group['locations'] or x.get('location_id') in group['locations'])]
        ways=[]
        for issue in issues:
            osm_id=issue.get('osm_way_id')
            if osm_id is None:
                match=re.search(r'/way-(\d+)/',issue['issue_id'])
                if match:osm_id=int(match[1])
            if osm_id is None:continue
            feature=by_way.get(osm_id)
            if osm_id not in [x['osm_way_id'] for x in ways]:
                ways.append({'osm_way_id':osm_id,'source_feature_found':feature is not None,
                             'name':feature.get('tags',{}).get('name') if feature else None,
                             'classification':'NEEDS_REVIEW','automatic_correction_allowed':False})
        controls=[]
        for location in catalog['locations']:
            if location['location_id'] not in group['locations']:continue
            key=(location['osm']['type'],location['osm']['id']);feature=by_feature.get(key)
            controls.append({'location_id':location['location_id'],'osm':location['osm'],
                             'source_found':feature is not None,'closed':feature.get('closed') if feature else None,
                             'missing_node_ref_count':feature.get('missing_node_ref_count') if feature else None,
                             'height_certified':False,'detailed_architecture_allowed':False})
        stages.append({**group,'phase':'STRUCTURAL_GREYBOX','blocked_by_lacerda_fidelity':False,
                       'existing_pending_alerts':len(issues),'existing_way_targets':ways,'landmark_controls':controls,
                       'first_issue_ids':[x['issue_id'] for x in issues[:12]],
                       'work_order':['XY / SSOT','relevo e apoio','vias e cruzamentos','calçadas / quadras','footprints / massing','marcos simples'],
                       'known_limits':['Triagem herdada não comprova bug; conferir objeto/camada antes de corrigir.',
                                       'Não alterar datum, DEM-fonte ou terreno global por redução de RMS.']})
    # Extensão do ledger existente, sem criar outra autoridade para os mesmos bugs.
    path='world/areas/centro-lapa-tororo-fontenova/road-corrections.json'
    ledger=ledgers['centro-lapa-tororo-fontenova']
    ledger['development_order']=[{'order':x['order'],'region':x['region']} for x in stages]
    ledger['current_focus']='STRUCTURAL_GREYBOX_CENTRO_FIRST'
    ledger['lacerda_fidelity_blocks_expansion']=False
    ledger['resumption_evidence']='docs/reports/world/territorial-resumption/priority_audit.json'
    write(path,ledger)
    result={'schema':'boas/territorial-resumption-v1','geographic_ssot':'world/geographic-reference.json',
            'ssot_sha256':hashlib.sha256((ROOT/'world/geographic-reference.json').read_bytes()).hexdigest(),
            'new_acquisition':False,'existing_aleph_osm_sources_reused':True,'geometry_changed':False,
            'stages':stages,'map_status':'GREYBOX','historical_lacerda_status':'FROZEN_BY_USER',
            'dique_shore_issue_preserved':True,'production_ready':False}
    write('docs/reports/world/territorial-resumption/priority_audit.json',result)
    print(json.dumps({'stages':len(stages),'pending_alerts':[x['existing_pending_alerts'] for x in stages],'ssot_changed':False}))


if __name__=='__main__':main()
