"""Diagnóstico read-only dos quatro píeres OSM e waterfront atual na B45."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2]; scene=bpy.context.scene
reg=json.loads((root/"world/areas/mvp-centro-lacerda/blender-revisions.json").read_text(encoding="utf8")); src=reg["validation_source"]
assert src["revision"]=="R30B.45"; assert Path(bpy.data.filepath).resolve()==(root/src["file"]).resolve()
ref=json.loads((root/"artifacts/structural-pipeline/mvp-centro-lacerda/structural_reference.json").read_text(encoding="utf8"))
ids={1321682676,1321682677,1426173139,1426173140}
features=[f for f in ref["features"] if int(f.get("osm_id",-1)) in ids]
assert len(features)==4
# objetos da cena explicitamente vinculados aos IDs, se existirem
matches=[]
for ob in scene.objects:
    props={k:ob[k] for k in ob.keys() if k!="cycles"}
    vals={str(v) for v in props.values()}
    if any(str(i) in vals or str(i) in ob.name for i in ids):
        matches.append({"name":ob.name,"type":ob.type,"collections":[c.name for c in ob.users_collection],"props":props,
                        "hidden":bool(ob.hide_viewport or ob.hide_get())})
# superfícies/controles costeiros
names=[
"BAÍA DE TODOS-OS-SANTOS | superfície e recorte costeiro",
"CAIS | contenção costeira alinhada à linha de costa",
"REF_WATERFRONT",
"Terminal Turístico Náutico da Bahia.001",
"CAIS | rampa curta até plataforma flutuante",
"CAIS | plataforma flutuante de embarque aproximada",
]
controls=[]
for name in names:
    ob=scene.objects.get(name)
    if not ob: continue
    corners=[ob.matrix_world@Vector(c) for c in ob.bound_box]
    controls.append({"name":name,"type":ob.type,"bounds":{"min":[min(p.x for p in corners),min(p.y for p in corners),min(p.z for p in corners)],"max":[max(p.x for p in corners),max(p.y for p in corners),max(p.z for p in corners)]},
                     "collections":[c.name for c in ob.users_collection],"hidden":bool(ob.hide_viewport or ob.hide_get())})
report={"schema":"boas/piers-b45-probe-v1","source":src,"features":features,"scene_id_matches":matches,"controls":controls,"geometry_changed":False}
out=root/"artifacts/waterfront/piers_b45.json";out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,ensure_ascii=False,indent=2,default=str)+"\n",encoding="utf8")
print(json.dumps({"piers":[{"osm_id":f["osm_id"],"closed":f["closed"],"xy":f["blender_xy"],"metrics":f["metrics"]} for f in features],"scene_matches":matches,"controls":controls},ensure_ascii=False,default=str))
