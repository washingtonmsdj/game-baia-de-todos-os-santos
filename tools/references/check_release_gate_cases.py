"""Verificações dirigidas do novo gate, sem build ou suíte geral."""
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from tools.references.provenance import ROOT,load_policy
from tools.references.audit_release_provenance import audit
def main():
    folder=ROOT/'artifacts/provenance-gate-checks';folder.mkdir(parents=True,exist_ok=True)
    path=folder/'fixture.txt';path.write_text('fixture isolada do gate; não é asset do jogo',encoding='utf8')
    sha=hashlib.sha256(path.read_bytes()).hexdigest();logical=path.relative_to(ROOT).as_posix();policy=load_policy()
    base={'resource_id':'fixture:approved','provider':'fixture','dataset':'gate_case','release_status':'FINAL_ALLOWED','dependencies':[]}
    manifest={'schema':'boas/release-content-v1','inventory_complete':True,'resources':[base['resource_id']],'files':[{'path':logical,'resource_ids':[base['resource_id']],'sha256':sha}]}
    records={base['resource_id']:base};cases=[]
    def check(label,m,r,expected):
        result=audit(m,r,policy);assert result['passed']==expected,label
        cases.append({'case':label,'expected_pass':expected,'actual_pass':result['passed'],'codes':sorted({e['code'] for e in result['errors']})})
    check('recurso permitido com arquivo completo',manifest,records,True)
    for status in ('DEV_REFERENCE_ONLY','REPLACE_BEFORE_RELEASE'):
        item={**base,'release_status':status};check(status,manifest,{base['resource_id']:item},False)
    dep={'resource_id':'fixture:image-dev','provider':'fixture','dataset':'image','release_status':'DEV_REFERENCE_ONLY','dependencies':[]}
    material={**base,'dependencies':[dep['resource_id']]}
    check('material depende de imagem temporária',manifest,{base['resource_id']:material,dep['resource_id']:dep},False)
    check('asset sem proveniência',manifest,{},False)
    item={**base,'release_status':'FINAL_ALLOWED_WITH_ATTRIBUTION'};check('atribuição ausente',manifest,{base['resource_id']:item},False)
    check('atribuição registrada',manifest,{base['resource_id']:{**item,'attribution':'fixture attribution'}},True)
    source={'resource_id':'fixture:survey','provider':'fixture','dataset':'raw','release_status':'DEV_REFERENCE_ONLY','dependencies':[],'raw_files':[{'path':'world-reference/fixture/terrain.bin','sha256':sha}]}
    check('bruto copiado/renomeado detectado por hash',manifest,{**records,source['resource_id']:source},False)
    check('pacote vazio',{'schema':'boas/release-content-v1','inventory_complete':True,'resources':[],'files':[]},records,False)
    cyclic={**base,'dependencies':[base['resource_id']]};check('ciclo em dependências',manifest,{base['resource_id']:cyclic},False)
    out=ROOT/'docs/reports/blender/lacerda-corridor/release_gate_cases.json';out.write_text(json.dumps({'cases':cases,'all_expected_outcomes':True,'scope':'Verificações dirigidas; sem pacote real/release executado'},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'cases':len(cases),'expected_outcomes':True}))
if __name__=='__main__':main()
