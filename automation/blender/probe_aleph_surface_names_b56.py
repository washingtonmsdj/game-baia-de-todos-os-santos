"""Localiza superfícies densas no .blend Aleph."""
import bpy,json
from pathlib import Path
aleph=Path(r"C:\Users\TONECOS\Documents\github\Tom Oliver\projeto-salvador-elevador-lacerda\blender\salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a_structure_ref.blend")
with bpy.data.libraries.load(str(aleph),link=True) as (src,dst):
    names=list(src.objects)
terms=("superfície integrada","superficie integrada","1.5m","1,5m","terreno corrigido","colisão estática","pistas do centro","caminhos e escadarias","calçadas indicativas")
hits=[n for n in names if any(t in n.lower() for t in terms)]
print(json.dumps(hits,ensure_ascii=False))
