"""Lista objetos de alta qualidade disponíveis no .blend Aleph sem importar/salvar."""
import bpy,json
from pathlib import Path
root=Path(__file__).resolve().parents[2]
aleph=Path(r"C:\Users\TONECOS\Documents\github\Tom Oliver\projeto-salvador-elevador-lacerda\blender\salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a_structure_ref.blend")
assert aleph.exists()
with bpy.data.libraries.load(str(aleph),link=True) as (src,dst):
    names=list(src.objects)
keep=[n for n in names if any(k in n.lower() for k in ("terreno","superf","via","encosta","dem","osm","cairu","mercado","lacerda"))]
print(json.dumps({"total_objects":len(names),"candidates":keep},ensure_ascii=False))
