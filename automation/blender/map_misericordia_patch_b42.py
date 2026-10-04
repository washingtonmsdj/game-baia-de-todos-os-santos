"""Mapeia candidatos de patch da Misericórdia B41 sem modificar a cena."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2]; scene=bpy.context.scene
reg=json.loads((root/"world/areas/mvp-centro-lacerda/blender-revisions.json").read_text(encoding="utf8")); src=reg["authoring_source"]
assert src["revision"]=="R30B.41"; assert Path(bpy.data.filepath).resolve()==(root/src["file"]).resolve()
contract=json.loads((root/"world/areas/mvp-centro-lacerda/production.json").read_text(encoding="utf8"))
ground=scene.objects[contract["export"]["road_object"]]; road=scene.objects["R30A7 | ROAD | 803899198"]
pts=[road.matrix_world@Vector(p.co[:3]) for sp in road.data.splines for p in sp.points]
# região crítica observada: índices 118..145
crit=pts[118:146]
rows=[]
for poly in ground.data.polygons:
    mat=ground.data.materials[poly.material_index].name if poly.material_index<len(ground.data.materials) and ground.data.materials[poly.material_index] else None
    if mat not in {"VIAS | pavimento de pedra Rua Chile","MVP | asfalto da ladeira"}: continue
    ws=[ground.matrix_world@ground.data.vertices[i].co for i in poly.vertices]
    cx=sum(p.x for p in ws)/len(ws); cy=sum(p.y for p in ws)/len(ws); cz=sum(p.z for p in ws)/len(ws)
    d=min(math.hypot(cx-q.x,cy-q.y) for q in crit)
    if d<=6.0:
        rows.append({"poly":poly.index,"material":mat,"center":[cx,cy,cz],"distance_to_axis_m":d,"verts":list(poly.vertices)})
out=root/"artifacts/roads/rondesp/misericordia_patch_candidates_b42.json"
out.write_text(json.dumps({"schema":"boas/misericordia-patch-map-b42-v1","source":src,"candidate_faces":rows,"geometry_changed":False},ensure_ascii=False,indent=2)+"\n",encoding="utf8")
from collections import Counter
print(json.dumps({"faces":len(rows),"materials":Counter(r["material"] for r in rows),"z_min":min(r["center"][2] for r in rows),"z_max":max(r["center"][2] for r in rows)},default=dict,ensure_ascii=False))
