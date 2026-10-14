"""Registrar revisão salva para reabertura; concluir somente com prova de conservação."""
import json,hashlib,argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def read(p):return json.loads((ROOT/p).read_text(encoding='utf8'))
def write(p,d):(ROOT/p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--verified',action='store_true');args=parser.parse_args()
    report=read('docs/reports/blender/geographic-foundation/application_b76.json')
    with (ROOT/report['file']).open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==report['sha256']
    p='world/areas/mvp-centro-lacerda/blender-revisions.json';catalog=read(p)
    if args.verified:
        validation=read('docs/reports/blender/geographic-foundation/validation_b76.json')
        assert validation['source_reopened'] and validation['preserved_objects']==6068 and not validation['differences']
    else:assert catalog['validation_source']['revision']=='R30B.75'
    entry={'file':report['file'],'revision':'R30B.76','status':'geographic_foundation_candidate','parent_file':report['parent'],'sha256':report['sha256'],'evidence':'docs/reports/blender/geographic-foundation/application_b76.json','source_reopened':args.verified,'production_ready':False,'notes':'Contrato geográfico único e Campo da Pólvora real; geometrias anteriores preservadas. Datum e topografia ainda candidatos; autoria/produção mantidas.'}
    if args.verified:entry['validation_evidence']='docs/reports/blender/geographic-foundation/validation_b76.json'
    catalog['revisions']=[r for r in catalog['revisions'] if r['file']!=entry['file']]+[entry]
    catalog['validation_source']=entry;write(p,catalog)
    print(json.dumps({'revision':entry['revision'],'source_reopened':args.verified,'runtime_promoted':False}))
if __name__=='__main__':main()
