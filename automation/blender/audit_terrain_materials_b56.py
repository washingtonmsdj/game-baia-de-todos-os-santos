"""Lista materiais de terreno existentes para reutilização visual B57."""
import bpy,json
from pathlib import Path
assert Path(bpy.data.filepath).name=="salvador_lacerda_r30b56_pieres_gameplay.blend"
names=[
"GAL R34 | encosta localizada | MVP | terreno contínuo",
"ENV R35 | terreno e rocha junto ao apoio",
"RIO R36 | solo e vegetação baixa",
"Terreno | solo encosta",
"Terreno | cobertura vegetal baixa",
"Terreno | contenção",
"MVP | asfalto da ladeira",
"VIAS | pavimento de pedra Rua Chile",
"MVP | percurso pedonal",
"CAIS | pedra costeira"
]
rows=[]
for n in names:
    m=bpy.data.materials.get(n)
    if not m: continue
    rows.append({"name":n,"diffuse_color":[float(x) for x in m.diffuse_color],"use_nodes":m.use_nodes,"nodes":len(m.node_tree.nodes) if m.use_nodes and m.node_tree else 0})
print(json.dumps(rows,ensure_ascii=False))
