"""Gate fail-closed de um manifesto explícito de pacote; não cria build."""
import argparse,json,sys,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from tools.references.provenance import ROOT,load_policy,catalog,release_class,safe_path

def audit(manifest,records,policy,root=ROOT):
    errors=[];visited=set();raw={f['path'] for r in records.values() for f in r.get('raw_files',[])}
    raw_hashes={f['sha256'] for r in records.values() for f in r.get('raw_files',[]) if f.get('sha256')}
    def error(code,resource,detail):errors.append({'code':code,'resource':resource,'detail':detail})
    def visit(key,stack):
        if key in stack:error('DEPENDENCY_CYCLE',key,stack+[key]);return
        if key in visited:return
        visited.add(key);r=records.get(key)
        if not r:error('UNKNOWN_PROVENANCE',key,'Dependência não catalogada');return
        status=release_class(r,policy)
        if status is None:error('UNKNOWN_RELEASE_CLASS',key,'Classe ausente/desconhecida')
        elif not policy['classes'][status]['package_allowed']:error(status,key,'Recurso/dependência não autorizado para pacote final')
        elif policy['classes'][status]['attribution_required'] and not r.get('attribution'):error('MISSING_ATTRIBUTION',key,'Atribuição obrigatória não registrada')
        if not r.get('provider') or not r.get('dataset'):error('UNKNOWN_SOURCE',key,'Provider/dataset não conhecidos')
        for dep in r.get('dependencies',[]):visit(dep,stack+[key])
    if manifest.get('schema')!='boas/release-content-v1':error('INVALID_MANIFEST',None,'Schema de conteúdo não reconhecido')
    resources=manifest.get('resources');files=manifest.get('files')
    if not isinstance(resources,list) or not isinstance(files,list):error('INCOMPLETE_MANIFEST',None,'resources e files devem ser listas');resources=[];files=[]
    if not resources or not files:error('EMPTY_PACKAGE',None,'Não aprovar manifesto vazio')
    declared=set(resources)
    for key in resources:visit(key,[])
    seen=set()
    for entry in files:
        path=entry.get('path');ids=entry.get('resource_ids',[])
        if not path:error('INVALID_PATH',None,'Arquivo sem caminho');continue
        if path in seen:error('DUPLICATE_FILE',path,'Arquivo repetido')
        seen.add(path)
        try:resolved=safe_path(root,path)
        except ValueError as exc:error('INVALID_PATH',path,str(exc));continue
        if path in raw or any(path==p or path.startswith(p+'/') for p in policy['raw_roots']):error('RAW_SURVEY_PACKAGED',path,'Dado bruto/referência no pacote')
        if not ids:error('UNKNOWN_PROVENANCE',path,'Arquivo não vinculado a recursos')
        for key in ids:
            if key not in declared:error('UNDECLARED_RESOURCE',key,path)
            visit(key,[])
        if not resolved.is_file():error('MISSING_FILE',path,'Arquivo de pacote ausente');continue
        expected=entry.get('sha256')
        if not expected:error('MISSING_HASH',path,'Manifesto sem hash do conteúdo')
        else:
            with resolved.open('rb') as stream:actual=hashlib.file_digest(stream,'sha256').hexdigest()
            if actual!=expected:error('HASH_MISMATCH',path,'Conteúdo mudou desde a auditoria')
            if actual in raw_hashes:error('RAW_SURVEY_PACKAGED',path,'Hash corresponde a levantamento bruto, mesmo com nome diferente')
    if manifest.get('inventory_complete') is not True:error('INCOMPLETE_INVENTORY',None,'Gate exige inventário integral declarado')
    return {'schema':'boas/release-provenance-audit-v1','passed':not errors,'errors':errors,'resources_checked':len(visited),'files_checked':len(files),'scope':'Manifesto fornecido e dependências transitivas; requer exportador que gere inventário completo e vínculo de materiais/texturas. Não inspeciona binário glTF automaticamente.'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--manifest',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    result=audit(json.loads(args.manifest.read_text(encoding='utf8')),catalog(),load_policy());args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'passed':result['passed'],'errors':len(result['errors'])}));return 0 if result['passed'] else 2
if __name__=='__main__':raise SystemExit(main())
