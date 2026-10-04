"""Compara referência OSM do Terminal/Píeres com helper funcional e terreno B45."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2]; scene=bpy.context.scene
reg=json.loads((root/"world/areas/mvp-centro-lacerda/blender-revisions.json").read_text(encoding="utf8")); src=reg["validation_source"]
assert src["revision"]=="R30B.45"; assert Path(bpy.data.filepath).resolve()==(root/src["file"]).resolve()
graph=json.loads((root/"docs/reports/blender/r30a7/road_graph.json").read_text(encoding="utf8"))
way=next(w for w in graph["ways"] if int(w["osm_way_id"])==1150035141)
ob=scene.objects.get("R30A7 | ROAD | 1150035141"); assert ob
pts=[ob.matrix_world@Vector(p.co[:3]) for sp in ob.data.splines for p in sp.points]
source=scene.objects.get("Terminal Turístico Náutico da Bahia.001")
srcpts=[]
if source:
 for sp in source.data.splines:
  srcpts += [source.matrix_world@Vector(p.co[:3]) for p in sp.points] if sp.type!="BEZIER" else [source.matrix_world@p.co for p in sp.bezier_points]
report={"schema":"boas/terminal-pier-binding-b45-v1","source":src,"terminal_way":way,
 "helper_points":[list(p) for p in pts],"reference_curve_points":[list(p) for p in srcpts],
 "helper_z_range":[min(p.z for p in pts),max(p.z for p in pts)],
 "reference_z_range":[min(p.z for p in srcpts),max(p.z for p in srcpts)] if srcpts else None,
 "geometry_changed":False}
out=root/"artifacts/waterfront/terminal_pier_binding_b45.json";out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps({"way":way,"helper_points":[list(p) for p in pts],"helper_z_range":report["helper_z_range"],"reference_points":[list(p) for p in srcpts],"reference_z_range":report["reference_z_range"]},ensure_ascii=False))
