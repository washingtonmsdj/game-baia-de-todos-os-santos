"""Extrai a borda topológica da água B46 para planejar correção costeira."""
import bpy,json
from pathlib import Path
from mathutils import Vector

root=Path(__file__).resolve().parents[2]; scene=bpy.context.scene
reg=json.loads((root/"world/areas/mvp-centro-lacerda/blender-revisions.json").read_text(encoding="utf8")); src=reg["validation_source"]
assert src["revision"]=="R30B.46"; assert Path(bpy.data.filepath).resolve()==(root/src["file"]).resolve()
wc=json.loads((root/"docs/reports/blender/r30a8/water_runtime_contract.json").read_text(encoding="utf8"))
ob=scene.objects[wc["surface_object"]]; me=ob.data
emap={tuple(sorted(e.vertices)):e.index for e in me.edges}; use=[0]*len(me.edges)
for p in me.polygons:
    for a,b in p.edge_keys: use[emap[tuple(sorted((a,b)))]]+=1
edges=[e for e,u in zip(me.edges,use) if u==1]
rows=[]
for e in edges:
    a=ob.matrix_world@me.vertices[e.vertices[0]].co; b=ob.matrix_world@me.vertices[e.vertices[1]].co
    rows.append({"edge":e.index,"verts":list(e.vertices),"a":[float(a.x),float(a.y),float(a.z)],"b":[float(b.x),float(b.y),float(b.z)]})
rows.sort(key=lambda r:min(r["a"][1],r["b"][1]))
out=root/"artifacts/waterfront/water_boundary_b46.json";out.write_text(json.dumps({"schema":"boas/water-boundary-b46-v1","source":src,"rows":rows},ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps(rows,ensure_ascii=False))
