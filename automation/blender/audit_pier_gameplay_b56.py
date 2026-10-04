"""Audita superfícies/colisão e grafos pedonais dos píeres B56."""
import bpy,json,hashlib,numpy as np
from pathlib import Path
root=Path(__file__).resolve().parents[2]
src=root/"blender/salvador_lacerda_r30b56_pieres_gameplay.blend"
assert Path(bpy.data.filepath).resolve()==src.resolve()
rep=json.loads((root/"docs/reports/blender/pier_gameplay_r30b56.json").read_text(encoding="utf8"))
assert hashlib.sha256(src.read_bytes()).hexdigest()==rep["source_after"]["sha256"]
rows=[]
for pid in [1426173139,1426173140]:
    s=bpy.context.scene.objects[f"B56 | WALKABLE PIER | {pid}"]
    c=bpy.context.scene.objects[f"B56 | COLLISION | PIER | {pid}"]
    sv=np.array([tuple(v.co) for v in s.data.vertices],dtype=float); cv=np.array([tuple(v.co) for v in c.data.vertices],dtype=float)
    same=len(sv)==len(cv) and len(s.data.polygons)==len(c.data.polygons) and float(np.max(np.linalg.norm(sv-cv,axis=1)))==0.0
    rows.append({"osm_id":pid,"same_geometry":same,"vertices":len(sv),"faces":len(s.data.polygons)})
graphs=[o for o in bpy.context.scene.objects if o.name.startswith("B56 | GRAPH WALK |")]
graph_ids=sorted(int(o["boas_osm_way_id"]) for o in graphs)
report={"schema":"boas/pier-gameplay-r30b56-audit-v1","source_reopened":True,"footprints":rows,"all_collision_identical":all(r["same_geometry"] for r in rows),"graph_count":len(graphs),"graph_ids":graph_ids,"expected_graph_ids":[1426173138,1426173325,1426173326,1426173327],"linear_piers_still_reference_only":all(o.get("boas_gameplay_status")=="centerline_only_width_unknown_not_walkable_surface" for o in bpy.context.scene.objects if o.name.startswith("PIER OSM |") and o.type=="CURVE"),"geometry_changed":False,"approved":False}
(root/"docs/reports/blender/pier_gameplay_r30b56_audit.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps(report,ensure_ascii=False))
