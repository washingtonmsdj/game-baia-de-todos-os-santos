"""Amostra a faixa oeste existente do terreno B47 para calibração local da expansão."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

root=Path(__file__).resolve().parents[2]; scene=bpy.context.scene
reg=json.loads((root/"world/areas/mvp-centro-lacerda/blender-revisions.json").read_text(encoding="utf8")); src=reg["validation_source"]
assert src["revision"]=="R30B.47"; assert Path(bpy.data.filepath).resolve()==(root/src["file"]).resolve()
prod=json.loads((root/"world/areas/mvp-centro-lacerda/production.json").read_text(encoding="utf8"))
ground=scene.objects[prod["export"]["road_object"]]
me=ground.data;me.calc_loop_triangles()
tree=BVHTree.FromPolygons([ground.matrix_world@v.co for v in me.vertices],[list(t.vertices) for t in me.loop_triangles],all_triangles=True)

rows=[]
for y in range(-280,-89,10):
    for x in (-285,-280,-275,-270,-265,-260,-255,-250,-245):
        p,n,i,d=tree.ray_cast(Vector((float(x),float(y),120)),Vector((0,0,-1)),200)
        if p is None:continue
        if p.z<1.0 or n.z<0.5:continue
        rows.append({"xy":[float(x),float(y)],"scene_z":float(p.z),"normal_z":float(n.z)})
report={"schema":"boas/west-seam-b47-v1","source":src,"rows":rows,"summary":{"samples":len(rows),"z_min":min(r["scene_z"] for r in rows),"z_max":max(r["scene_z"] for r in rows)},"geometry_changed":False}
out=root/"artifacts/waterfront/west_seam_b47.json";out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps(report["summary"],ensure_ascii=False))
