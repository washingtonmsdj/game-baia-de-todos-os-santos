"""Script de asset de veículo na janela MCP existente, com arquivo/hash/PID explícitos.

Não abre Blender nem altera o contrato de produção da cidade. Suporta também
checkpoint de oficina cuja origem e identidade constem no relatório do asset.
"""
import argparse,json
from pathlib import Path
from healthcheck import request

def main():
 p=argparse.ArgumentParser()
 p.add_argument('script');p.add_argument('--file',required=True);p.add_argument('--sha256',required=True)
 p.add_argument('--pid',required=True,type=int);p.add_argument('--port',default=9877,type=int)
 p.add_argument('--timeout',default=90,type=float)
 a=p.parse_args();root=Path(__file__).resolve().parents[2]
 script=(root/a.script).resolve();script.relative_to(root/'automation/blender')
 source=(root/a.file).resolve();source.relative_to(root/'blender/assets/vehicles')
 assert script.is_file() and source.is_file()
 # Preflight no próprio processo visível, antes de qualquer script de modelagem.
 code=("import bpy,os,hashlib,runpy; from pathlib import Path; "
       "assert not bpy.app.background; "
       f"assert os.getpid()=={a.pid}, 'Janela diferente'; "
       f"assert Path(bpy.data.filepath).resolve()==Path({str(source)!r}).resolve(), 'Fonte diferente'; "
       f"assert hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()=={a.sha256!r}, 'Hash diferente'; "
       "assert not bpy.app.is_job_running('RENDER'), 'Render pendente'; "
       f"runpy.run_path({str(script)!r},run_name='__main__')")
 result=request('127.0.0.1',a.port,{'type':'execute_code','params':{'code':code}},a.timeout)
 print(json.dumps(result,ensure_ascii=False))
 return 0 if result.get('status')=='success' and result.get('result',{}).get('executed') is not False else 1

if __name__=='__main__':raise SystemExit(main())
