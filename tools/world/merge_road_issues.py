"""Atualiza fila por IDs OSM, preservando histórico e resoluções manuais."""
import argparse,json
from pathlib import Path


def merge(network, prior, cycle):
    records={item['issue_id']:item for item in prior.get('issues',[])}
    active={item['issue_id'] for item in network['issues']}
    for issue in network['issues']:
        key=issue['issue_id']
        if key not in records:
            records[key]={**issue,'first_seen_cycle':cycle,'last_seen_cycle':cycle,'history':[{'cycle':cycle,'event':'detected','evidence':issue['evidence']}]}
        else:
            old=records[key]
            previous_evidence=old.get('evidence')
            if old['status'] in {'resolved','not_observed_needs_confirmation'}:
                old['status']='pending'
                old['history'].append({'cycle':cycle,'event':'observed_again','evidence':issue['evidence']})
            elif previous_evidence != issue['evidence']:
                old['history'].append({'cycle':cycle,'event':'evidence_updated','before':previous_evidence,'after':issue['evidence']})
            old['last_seen_cycle']=cycle
            old['evidence']=issue['evidence']
            old['priority']=issue['priority']
            old['classification']=issue['classification']
            old['required_action']=issue['required_action']
    for key,item in records.items():
        if key not in active and item['status']=='pending':
            item['status']='not_observed_needs_confirmation'
            item['history'].append({'cycle':cycle,'event':'not_observed','note':'Ausência no relatório não aprova correção; conferir coverage e reabertura.'})
    return {'schema':'boas/road-corrections-ledger-v1','area_id':network['area_id'],'cycle':cycle,
            'issues':sorted(records.values(),key=lambda i:(i['priority'],i['issue_id'])),
            'applied_corrections':prior.get('applied_corrections',[]),'production_ready':False}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--network',type=Path,required=True);parser.add_argument('--ledger',type=Path,required=True);parser.add_argument('--cycle',required=True)
    args=parser.parse_args();network=json.loads(args.network.read_text(encoding='utf8'));prior=json.loads(args.ledger.read_text(encoding='utf8')) if args.ledger.exists() else {}
    assert not prior or prior['area_id']==network['area_id'],'Não misturar áreas no histórico'
    result=merge(network,prior,args.cycle);args.ledger.parent.mkdir(parents=True,exist_ok=True)
    args.ledger.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'issues':len(result['issues']),'applied_corrections':len(result['applied_corrections'])}))
