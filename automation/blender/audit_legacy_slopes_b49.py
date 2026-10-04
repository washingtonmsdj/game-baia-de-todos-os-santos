"""Audita encostas/faixas antigas na B49 sem editar."""
import bpy,json
from pathlib import Path
assert Path(bpy.data.filepath).name=="salvador_lacerda_r30b49_costa_e_fundo_candidatos.blend"
rows=[]
for o in bpy.context.scene.objects:
    if not o.name.startswith("Encosta |"):continue
    rows.append({
      "name":o.name,"type":o.type,"verts":len(o.data.vertices) if o.type=="MESH" else None,
      "polys":len(o.data.polygons) if o.type=="MESH" else None,
      "hide_viewport":o.hide_viewport,"hide_render":o.hide_render,
      "collections":[c.name for c in o.users_collection],
      "materials":[m.name for m in o.data.materials if m] if o.type=="MESH" else [],
      "props":{k:o[k] for k in o.keys() if not k.startswith("_")}
    })
print(json.dumps(rows,ensure_ascii=False))
