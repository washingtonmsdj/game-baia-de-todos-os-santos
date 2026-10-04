"""Conectividade vertical read-only nos nós da Rua da Misericórdia B41."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2]; scene=bpy.context.scene
reg=json.loads((root/"world/areas/mvp-centro-lacerda/blender-revisions.json").read_text(encoding="utf8")); src=reg["authoring_source"]
assert src["revision"]=="R30B.41"; assert Path(bpy.data.filepath).resolve()==(root/src["file"]).resolve()
graph=json.loads((root/"docs/reports/blender/r30a7/road_graph.json").read_text(encoding="utf8"))
target=next(w for w in graph["ways"] if int(w["osm_way_id"])==803899198)
nodes=[str(x) for x in target["node_refs"]]
rows=[]
for nid in nodes:
    incident=[w for w in graph["ways"] if nid in [str(x) for x in w.get("node_refs",[])]]
    inc=[]
    for w in incident:
        name=f"R30A7 | ROAD | {w['osm_way_id']}"
        ob=scene.objects.get(name)
        match=[]
        if ob and ob.type=="CURVE":
            refs=[str(x) for x in w.get("node_refs",[])]
            for sp in ob.data.splines:
                pts=[ob.matrix_world@Vector(p.co[:3]) for p in sp.points]
                # B41 target has densified profile; use nearest XY to graph node.
                xy=w["blender_xy"][refs.index(nid)] if nid in refs else None
                if xy:
                    p=min(pts,key=lambda q:math.hypot(q.x-xy[0],q.y-xy[1]))
                    match=[float(p.x),float(p.y),float(p.z)]
        inc.append({"osm_way_id":w["osm_way_id"],"name":w.get("name"),"node_refs":[str(x) for x in w.get("node_refs",[])],"point":match})
    rows.append({"node_id":nid,"incident":inc})
out=root/"artifacts/roads/rondesp/misericordia_node_connectivity_b41.json"
out.write_text(json.dumps({"schema":"boas/misericordia-node-connectivity-b41-v1","rows":rows,"geometry_changed":False},ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps(rows,ensure_ascii=False))
