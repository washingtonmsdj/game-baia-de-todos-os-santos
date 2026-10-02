"""Catálogo explícito de revisões. Nunca seleciona pelo sufixo ou mtime."""
import argparse,hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
CATALOG=ROOT/'world/areas/mvp-centro-lacerda/blender-revisions.json'
REPORTS={24:'terrain_junction_correction',25:'terrain_junction_finish',26:'terrain_proxy_binding',27:'terrain_proxy_applied_transform',28:'terrain_proxy_refinement',29:'terrain_proxy_network_refinement',30:'terrain_real_boundary_extension',31:'cidade_baixa_r30b31',32:'cidade_baixa_r30b32',33:'cidade_baixa_r30b33'}

def digest(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--authoring-file');parser.add_argument('--parent-file');parser.add_argument('--evidence',help='Relatório de origem/conferência da nova revisão, relativo ao repositório.');args=parser.parse_args()
    prior=json.loads(CATALOG.read_text(encoding='utf8')) if CATALOG.exists() else {}
    chosen=args.authoring_file or prior.get('authoring_source',{}).get('file')
    if not chosen:raise SystemExit('Indique --authoring-file; não existe seleção automática.')
    selected=(ROOT/chosen).resolve()
    if not selected.is_relative_to(ROOT/'blender') or not selected.is_file():raise SystemExit('Fonte de trabalho fora de blender/ ou ausente')
    contract=json.loads((ROOT/'world/areas/mvp-centro-lacerda/production.json').read_text(encoding='utf8'));production=contract['world_source'];rows=[];choice=None
    for p in sorted((ROOT/'blender').glob('*.blend')):
        rel=p.relative_to(ROOT).as_posix();match=re.fullmatch(r'salvador_lacerda_r30b(\d+)_.*',p.stem);n=int(match[1]) if match else None
        status='historical';parent=None;evidence=None;changes=None
        if 'r30c' in p.name:status='rejected_experiment'
        if n==23:status='historical_baseline';changes='Base escolhida pelo usuário; antecessora da cadeia estrutural B24–B30.'
        if n in REPORTS:
            rp=ROOT/f'docs/reports/blender/{REPORTS[n]}.json';d=json.loads(rp.read_text(encoding='utf8'));parent=d['source_before']['file'];evidence=rp.relative_to(ROOT).as_posix()
        if rel==production['file']:status='registered_production';changes='Fonte registrada no contrato; aprovação estrutural parcial, não gameplay completo.'
        if p.resolve()==selected:
            status='authoring_candidate';changes='Revisão de trabalho explicitamente selecionada; não equivale a aprovação para exportação.'
            if n==31:changes='Passe dos prédios da Cidade Baixa e Mário Cravo; mantém a cadeia B23–B30; revisão parcial.'
            if args.evidence:
                rp=(ROOT/args.evidence).resolve()
                if not rp.is_relative_to(ROOT/'docs/reports/blender'):raise SystemExit('Evidência deve estar em docs/reports/blender/')
                d=json.loads(rp.read_text(encoding='utf8'));parent=d['source_before']['file'];evidence=rp.relative_to(ROOT).as_posix()
                after=d['source_after']
                if after['file']!=rel or after['sha256']!=digest(p):raise SystemExit('Relatório não corresponde à fonte salva')
            if args.parent_file and parent and args.parent_file!=parent:raise SystemExit('Pai explícito diverge do relatório de origem')
            if parent is None:
                old=next((r for r in prior.get('revisions',[]) if r['file']==rel),None)
                parent=args.parent_file or (old or {}).get('parent_file')
                if n!=23 and parent is None:raise SystemExit('Indique --parent-file para uma nova revisão sem relatório de origem.')
        old=next((r for r in prior.get('revisions',[]) if r['file']==rel),None)
        if old and parent is None:parent=old.get('parent_file');evidence=old.get('evidence')
        record={'file':rel,'revision':f'R30B.{n:02d}' if n else None,'status':status,'parent_file':parent,'evidence':evidence,'sha256':digest(p) if n and n>=23 else None,'notes':changes}
        rows.append(record)
        if p.resolve()==selected:choice=record.copy()
    if choice is None:raise SystemExit('A fonte selecionada deve estar no catálogo da composição')
    if digest(ROOT/production['file'])!=production['sha256']:raise SystemExit('Fonte de produção alterada sem atualização do contrato')
    data={'schema':'boas/blender-revisions-v1','area_id':'mvp-centro-lacerda','production_source_reference':'production.json#/world_source','authoring_source':{k:choice[k] for k in ('file','sha256','revision','status','parent_file','evidence')},'authoring_scene':production['scene'],'selection_policy':'explicit_pointer_never_filename_mtime_or_open_window','session_recovery_reference':'artifacts/blender-sessions/current-session.json','revisions':rows}
    CATALOG.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'production':production['file'],'authoring':choice['file'],'entries':len(rows)},ensure_ascii=False))
