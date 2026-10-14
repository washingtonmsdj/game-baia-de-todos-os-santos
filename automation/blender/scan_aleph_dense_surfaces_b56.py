"""Procura superfícies densas em todos os .blend do projeto Aleph."""
import bpy,json
from pathlib import Path
adir=Path(r"C:\Users\TONECOS\Documents\github\Tom Oliver\projeto-salvador-elevador-lacerda\blender")
rows=[]
terms=("superfície integrada","superficie integrada","1.5m","1,5m","terreno corrigido","terreno dem","pistas do centro","caminhos e escadarias","calçadas indicativas")
for f in sorted(adir.glob("*.blend")):
    try:
        with bpy.data.libraries.load(str(f),link=True) as (src,dst):
            names=list(src.objects)
        hits=[n for n in names if any(t in n.lower() for t in terms)]
        if hits: rows.append({"file":f.name,"hits":hits})
    except Exception as e:
        rows.append({"file":f.name,"error":str(e)})
print(json.dumps(rows,ensure_ascii=False))
