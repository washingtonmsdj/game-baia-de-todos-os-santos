from pathlib import Path
from tools.blendmcp.healthcheck import request
import json
path=Path('automation/blender/onibus_v03_frente_traseira.py')
code=path.read_text(encoding='utf-8')
code=code.replace("assert s.name=='ONIBUS | Torino 31065 v02',s.name", "assert s.name=='ONIBUS | Torino 31065 v03',s.name\nfor item in list(s.objects):\n    if item.name.startswith('BUS03 | '):bpy.data.objects.remove(item,do_unlink=True)")
code=code.replace("assert not out.exists(),'Preservar revisão existente'", "# Finalizar a mesma revisão recém-criada")
print(json.dumps(request('127.0.0.1',9877,{'type':'execute_code','params':{'code':code}},120)))
