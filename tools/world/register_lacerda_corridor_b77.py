"""Registra revisão real; promoção de validação exige reabertura e conservação."""
import argparse,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def main():
    p=argparse.ArgumentParser();p.add_argument('--verified',action='store_true');args=p.parse_args()
    report=json.loads((ROOT/'docs/reports/blender/lacerda-corridor/scene_b77.json').read_text(encoding='utf8'))
    entry={**report['source_after'],'status':'corridor_slice_candidate','parent_file':report['source_before']['file'],'production_ready':False,'source_reopened':args.verified,'evidence':'docs/reports/blender/lacerda-corridor/scene_b77.json','notes':'Corredor candidato com colisões separadas, recorte local do consolo e demonstração do elevador. Datum/física na engine/volume varrido completo pendentes.'}
    with (ROOT/entry['file']).open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==entry['sha256']
    if args.verified:
        validation=json.loads((ROOT/'docs/reports/blender/lacerda-corridor/validation_b77.json').read_text(encoding='utf8'));assert validation['passed'] and validation['source_reopened'];assert validation['reopen_evidence']['file']==entry['file'] and validation['reopen_evidence']['sha256']==entry['sha256'];entry['validation_evidence']='docs/reports/blender/lacerda-corridor/validation_b77.json'
    path=ROOT/'world/areas/mvp-centro-lacerda/blender-revisions.json';catalog=json.loads(path.read_text(encoding='utf8'));assert catalog['validation_source']['revision'] in ('R30B.76','R30B.77','R30B.77B')
    if report.get('intermediate_revision'):
        entry['parent_file']=report['intermediate_revision']['file']
        for old in catalog['revisions']:
            if old['file']==entry['parent_file']:
                old['status']='superseded_door_demo';old['production_ready']=False;old['notes']='Revisão intermediária preservada; abertura das folhas e rota inferior corrigidas na B77B.';old['evidence']='docs/reports/blender/lacerda-corridor/scene_b77_initial.json';old.pop('validation_evidence',None)
    catalog['revisions']=[r for r in catalog['revisions'] if r['file']!=entry['file']]+[entry];catalog['validation_source']=entry
    path.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    registry=ROOT/'world/data-provenance.json';data=json.loads(registry.read_text(encoding='utf8'))
    item=next(r for r in data['resources'] if r['resource_id']=='derived:lacerda-corridor-b77');item['derived_objects']=report['added_objects']+report['animated_existing_objects']+[report['local_correction']['object']];item['source_scene']=report['source_before']
    qa=json.loads((ROOT/'docs/reports/blender/lacerda-corridor/walkability_candidate_b77.json').read_text(encoding='utf8'));points=[p for route in qa['routes'].values() if route.get('status')=='sampled_clear' for p in route['points']]
    item['derived_route_bounds']={'coordinate_reference':'world/geographic-reference.json','minimum':[min(p[i] for p in points) for i in range(3)],'maximum':[max(p[i] for p in points) for i in range(3)]}
    registry.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'revision':entry['revision'],'verified':args.verified,'runtime_promoted':False}))
if __name__=='__main__':main()
