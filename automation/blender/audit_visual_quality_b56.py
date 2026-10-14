"""Audita quais superfícies de gameplay/visuais estão visíveis na B56."""
import bpy,json
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2]
assert Path(bpy.data.filepath).name=="salvador_lacerda_r30b56_pieres_gameplay.blend"
rows=[]
keys=("B55 | GAMEPLAY","B55 | COLLISION","B54 | GAMEPLAY","B54 | COLLISION",
      "EXPANSAO B49","PIER OSM","B56 | WALKABLE","B56 | COLLISION","MVP | terreno corrigido",
      "BAÍA DE TODOS-OS-SANTOS","CAIS |")
for o in bpy.context.scene.objects:
    if not any(o.name.startswith(k) for k in keys): continue
    b=None
    try:
        c=[o.matrix_world@Vector(x) for x in o.bound_box]
        b={"min":[min(p[i] for p in c) for i in range(3)],"max":[max(p[i] for p in c) for i in range(3)]}
    except: pass
    rows.append({
      "name":o.name,"type":o.type,"hide_viewport":o.hide_viewport,"hide_render":o.hide_render,
      "visible":o.visible_get(),"display_type":o.display_type,
      "verts":len(o.data.vertices) if o.type=="MESH" else None,
      "faces":len(o.data.polygons) if o.type=="MESH" else None,
      "materials":[m.name for m in o.data.materials if m] if o.type=="MESH" else [],
      "bounds":b,"collections":[c.name for c in o.users_collection],
      "props":{k:o[k] for k in o.keys() if k.startswith("boas_")}
    })
out=root/"artifacts/waterfront/visual_quality_b56.json"
out.write_text(json.dumps({"schema":"boas/visual-quality-b56-v1","rows":rows,"geometry_changed":False},ensure_ascii=False,indent=2)+"\n",encoding="utf8")
for r in rows:
    print(json.dumps({k:r[k] for k in ("name","hide_viewport","hide_render","visible","verts","faces","materials")},ensure_ascii=False))
