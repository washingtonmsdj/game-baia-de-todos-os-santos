"""Inventário read-only de água, costa, cais, encostas e limites da B45."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2]
scene=bpy.context.scene
reg=json.loads((root/"world/areas/mvp-centro-lacerda/blender-revisions.json").read_text(encoding="utf8"))
src=reg["validation_source"]
assert src["revision"]=="R30B.45"
assert Path(bpy.data.filepath).resolve()==(root/src["file"]).resolve()

terms=("baía","baia","agua","água","water","ocean","oceano","foam","cais","pier","porto","encosta","relevo","mercado","náutico","nautico","coste","shore")
rows=[]
for ob in scene.objects:
    name=ob.name.lower()
    if not any(t in name for t in terms): continue
    try:
        corners=[ob.matrix_world@Vector(c) for c in ob.bound_box]
        bounds={"min":[min(p.x for p in corners),min(p.y for p in corners),min(p.z for p in corners)],
                "max":[max(p.x for p in corners),max(p.y for p in corners),max(p.z for p in corners)]}
    except:
        bounds=None
    rows.append({"name":ob.name,"type":ob.type,"collection_names":[c.name for c in ob.users_collection],"bounds":bounds,
                 "hide_viewport":bool(ob.hide_viewport),"hide_render":bool(ob.hide_render),
                 "props":{k:ob[k] for k in ob.keys() if k!="cycles"}})
report={"schema":"boas/waterfront-expansion-probe-b45-v1","source":src,"scene_object_count":len(scene.objects),"matched_objects":rows,
        "geometry_changed":False,"saved_session":False}
out=root/"artifacts/waterfront/waterfront_expansion_b45.json";out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(report,ensure_ascii=False,indent=2,default=str)+"\n",encoding="utf8")
summary=[{"name":r["name"],"type":r["type"],"bounds":r["bounds"]} for r in rows]
print(json.dumps({"matched":len(rows),"objects":summary},ensure_ascii=False))
