"""Inventário read-only dos limites de terreno/encostas para expansão costeira B46."""
import bpy, json
from pathlib import Path
from mathutils import Vector

root=Path(__file__).resolve().parents[2]; scene=bpy.context.scene
reg=json.loads((root/"world/areas/mvp-centro-lacerda/blender-revisions.json").read_text(encoding="utf8")); src=reg["validation_source"]
assert src["revision"]=="R30B.46"
assert Path(bpy.data.filepath).resolve()==(root/src["file"]).resolve()

terms=("terreno","encosta","relevo","solo","cidade baixa","cidade alta","cais","orla")
rows=[]
for ob in scene.objects:
    if ob.type!="MESH": continue
    low=ob.name.lower()
    if not any(t in low for t in terms): continue
    corners=[ob.matrix_world@Vector(c) for c in ob.bound_box]
    b=[min(p.x for p in corners),max(p.x for p in corners),min(p.y for p in corners),max(p.y for p in corners),min(p.z for p in corners),max(p.z for p in corners)]
    rows.append({"name":ob.name,"bounds":b,"verts":len(ob.data.vertices),"polys":len(ob.data.polygons),"collections":[c.name for c in ob.users_collection]})
rows.sort(key=lambda r:(r["bounds"][0],r["bounds"][2],r["name"]))
report={"schema":"boas/terrain-expansion-b46-v1","source":src,"objects":rows,"geometry_changed":False}
out=root/"artifacts/waterfront/terrain_expansion_b46.json"; out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
# compact: objects that touch expansion-side x<-250 or coast y<0
sel=[r for r in rows if r["bounds"][0]<-250 or r["bounds"][2]<0]
print(json.dumps({"count":len(rows),"expansion_relevant":sel[:80]},ensure_ascii=False))
