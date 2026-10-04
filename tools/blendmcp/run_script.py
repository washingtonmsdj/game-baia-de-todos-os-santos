"""Executa script versionável na janela BlendMCP existente; nunca abre Blender."""
import argparse
import json
from pathlib import Path
from healthcheck import request

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('script')
    parser.add_argument('--port', type=int, default=9876)
    parser.add_argument('--timeout', type=float, default=180)
    parser.add_argument('--source', choices=('authoring', 'validation', 'production'), default='authoring')
    parser.add_argument('--read-only', action='store_true', help='Inspeção, sem mutação de geometria/fonte')
    parser.add_argument('--source-operation', action='store_true', help='Somente abertura registrada ou cópia de recuperação')
    parser.add_argument('--adopt-session', action='store_true', help='Adotar a porta indicada, somente com inspect_authoring_session.py --read-only')
    parser.add_argument('--reopen', action='store_true', help='Reabrir o ponteiro para conferir persistência, somente no opener registrado')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    script = (root / args.script).resolve()
    script.relative_to(root / 'automation' / 'blender')
    if args.source_operation and script.name not in {'preserve_authoring_session.py','open_registered_source.py'}:
        parser.error('--source-operation é restrito à abertura registrada/recuperação')
    if args.adopt_session and (not args.read_only or script.name!='inspect_authoring_session.py'):
        parser.error('--adopt-session exige inspect_authoring_session.py --read-only')
    if args.reopen and (not args.source_operation or script.name!='open_registered_source.py'):
        parser.error('--reopen exige open_registered_source.py --source-operation')
    values={'BOAS_SOURCE_MODE':args.source,'BOAS_MCP_PORT':args.port,'BOAS_SOURCE_OPERATION':args.source_operation or args.read_only,'BOAS_FORCE_REOPEN':args.reopen}
    code = 'import runpy; '
    if not args.adopt_session:
        guard=root/'automation/blender/require_authoring_source.py'
        code+='runpy.run_path('+repr(str(guard))+', init_globals='+repr(values)+'); '
    code+='runpy.run_path('+repr(str(script))+', run_name="__main__", init_globals='+repr(values)+')'
    result = request('127.0.0.1', args.port, {'type':'execute_code','params':{'code':code}}, args.timeout)
    if script.name=='inspect_authoring_session.py' and result.get('status')=='success':
        observed=json.loads(result['result']['result'].strip())
        observed_path=Path(observed['file']).resolve()
        if not observed_path.is_relative_to(root/'blender'):
            raise ValueError('Janela de outro projeto; não adotar')
        session=root/'artifacts/blender-sessions/current-session.json'
        existing=json.loads(session.read_text(encoding='utf8')) if session.exists() else {}
        if 'source_file' in existing:existing['recovered_source_file']=existing.pop('source_file')
        if 'source_sha256' in existing:existing['recovered_source_sha256']=existing.pop('source_sha256')
        existing.update({'pid':observed['pid'],'mcp_port':args.port,'observed_file':observed_path.relative_to(root).as_posix(),'scene':observed['scene']})
        session.parent.mkdir(parents=True,exist_ok=True)
        session.write_text(json.dumps(existing,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(result, ensure_ascii=False))
    if result.get('status') != 'success':
        raise SystemExit(1)
