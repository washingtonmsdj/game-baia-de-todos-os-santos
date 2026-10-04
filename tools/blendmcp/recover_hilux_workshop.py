"""Recuperação restrita da oficina Hilux pelo MCP na janela já aberta."""
from pathlib import Path
import json
from healthcheck import request
r=Path(__file__).resolve().parents[2]
p=r/'automation/blender/recover_hilux_workshop_v20.py'
response=request('127.0.0.1',9876,{'type':'execute_code','params':{'code':'import runpy; runpy.run_path('+repr(str(p))+',run_name="__main__")'}},60)
print(json.dumps(response,ensure_ascii=False))
if response.get('status')!='success' or response.get('result',{}).get('executed') is False:raise SystemExit(1)
