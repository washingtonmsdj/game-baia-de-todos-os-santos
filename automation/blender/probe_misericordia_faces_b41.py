"""Inspeção read-only das faces viárias na junção Misericórdia/Ladeira B41."""
import bpy,json
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2]
scene=bpy.context.scene
reg=json.loads((root/"world/areas/mvp-centro-lacerda/blender-revisions.json").read_text(encoding="utf8"))
src=reg["authoring_source"]
assert src["revision"]=="R30B.41"
assert Path(bpy.data.filepath).resolve()==(root/src["file"]).resolve()
contract=json.loads((root/"world/areas/mvp-centro-lacerda/production.json").read_text(encoding="utf8"))
ground=scene.objects[contract["export"]["road_object"]]
road=scene.objects["R30A7 | ROAD | 803899198"]
authored=scene.objects["Rua da Misericórdia.002"]
pts=[road.matrix_world@Vector(p.co[:3]) for sp in road.data.splines for p in sp.points]
auth=[authored.matrix_world@Vector(p.co[:3]) for sp in authored.data.splines for p in sp.points]
me=ground.data
road_mats={i:m.name for i,m in enumerate(me.materials) if m and m.name in contract["export"]["road_materials"]}
rows=[]
for poly in me.polygons:
    if poly.material_index not in road_mats:
        continue
    c=ground.matrix_world@poly.center
    nearest=min(range(115,181),key=lambda i:(pts[i].to_2d()-c.to_2d()).length)
    dist=(pts[nearest].to_2d()-c.to_2d()).length
    if dist>6.5:
        continue
    vs=[ground.matrix_world@me.vertices[i].co for i in poly.vertices]
    rows.append({
        "poly":poly.index,
        "material":road_mats[poly.material_index],
        "center":[float(c.x),float(c.y),float(c.z)],
        "nearest_helper_index":nearest,
        "axis_distance_m":float(dist),
        "z_min":min(v.z for v in vs),
        "z_max":max(v.z for v in vs),
        "verts":[int(i) for i in poly.vertices]
    })
report={"schema":"boas/misericordia-faces-b41-v1","source":src,"authored_curve":[list(p) for p in auth],"critical_faces":rows,"geometry_changed":False}
out=root/"artifacts/roads/rondesp/misericordia_faces_b41.json"
out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
from collections import Counter
print(json.dumps({"faces":len(rows),"materials":dict(Counter(r["material"] for r in rows)),"z_min":min(r["z_min"] for r in rows),"z_max":max(r["z_max"] for r in rows),"authored_curve":[list(p) for p in auth]},ensure_ascii=False))
