"""Inspeção read-only da frente costeira B47: água, píeres, cais e encostas."""
import bpy,json
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2]
assert Path(bpy.data.filepath).name=="salvador_lacerda_r30b47_coastline_sudoeste.blend"
rows=[]
for ob in bpy.context.scene.objects:
    n=ob.name.lower()
    if any(k in n for k in ("pier osm","baía de todos","cais |","encosta |","terreno corrigido","coast")):
        try:
            corners=[ob.matrix_world@Vector(c) for c in ob.bound_box]
            b={"min":[min(p[i] for p in corners) for i in range(3)],"max":[max(p[i] for p in corners) for i in range(3)]}
        except: b=None
        rows.append({"name":ob.name,"type":ob.type,"hide_viewport":ob.hide_viewport,"hide_render":ob.hide_render,"visible_get":ob.visible_get(),"bounds":b,"collections":[c.name for c in ob.users_collection],"props":{k:ob[k] for k in ob.keys() if not k.startswith("_")}})
out=root/"artifacts/waterfront/waterfront_scene_b47.json";out.write_text(json.dumps({"schema":"boas/waterfront-scene-b47-v1","rows":rows,"geometry_changed":False},ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps({"count":len(rows),"piers":[r for r in rows if r["name"].startswith("PIER OSM")],"water":[r for r in rows if "BAÍA DE TODOS" in r["name"]],"quay":[r for r in rows if r["name"].startswith("CAIS |")],"slope_count":sum(r["name"].startswith("Encosta |") for r in rows)},ensure_ascii=False))
