"""Amostra o terreno oficial em grade par de 2 m para a costura B52."""
import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2]
assert Path(bpy.data.filepath).name=="salvador_lacerda_r30b51_gameplay_costeiro.blend"
ob=bpy.context.scene.objects["MVP | terreno corrigido | colisão estática"]; me=ob.data; me.calc_loop_triangles()
tree=BVHTree.FromPolygons([ob.matrix_world@v.co for v in me.vertices],[list(t.vertices) for t in me.loop_triangles],all_triangles=True)
rows=[]
for y in range(-510,11,2):
  for x in range(-304,-259,2):
    p=tree.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),500)[0]
    if p is not None: rows.append({"x":x,"y":y,"z":float(p.z)})
out={"schema":"boas/coastal-seam-controls-b52-v2","spacing_m":2,"rows":rows,"geometry_changed":False}
(root/"artifacts/waterfront/coastal_seam_controls_b52.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps({"samples":len(rows),"x_range":[min(r["x"] for r in rows),max(r["x"] for r in rows)],"y_range":[min(r["y"] for r in rows),max(r["y"] for r in rows)]},ensure_ascii=False))
