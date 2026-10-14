"""Audita a fonte candidata sem criar pacote/build; deve continuar bloqueada."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from tools.references.audit_release_provenance import audit
from tools.references.provenance import catalog,load_policy
def main():
    source=json.loads((ROOT/'world/areas/mvp-centro-lacerda/blender-revisions.json').read_text(encoding='utf8'))['validation_source']
    manifest={'schema':'boas/release-content-v1','inventory_complete':False,'resources':['derived:lacerda-corridor-b77'],'files':[{'path':source['file'],'sha256':source['sha256'],'resource_ids':['derived:lacerda-corridor-b77']}]}
    result=audit(manifest,catalog(),load_policy());result['foundation_only']=True;result['package_created']=False;result['source_revision']=source['revision'];result['note']='Auditoria deliberadamente incompleta da cena candidata; não é pacote final. Exportador ainda deve gerar inventário completo.'
    (ROOT/'docs/reports/blender/lacerda-corridor/current_scene_release_gate.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    assert not result['passed'],'Legado pendente/inventário incompleto não podem passar'
    print(json.dumps({'release_blocked_as_expected':True,'errors':len(result['errors']),'package_created':False}))
if __name__=='__main__':main()
