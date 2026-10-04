"""Planeja B42 sem mutar: perfil DEM relativo aplicado só ao corredor viário existente."""
import bpy,json,math,bisect
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2]; scene=bpy.context.scene
reg=json.loads((root/"world/areas/mvp-centro-lacerda/blender-revisions.json").read_text(encoding="utf8")); src=reg["authoring_source"]
assert src["revision"]=="R30B.41"; assert Path(bpy.data.filepath).resolve()==(root/src["file"]).resolve()
contract=json.loads((root/"world/areas/mvp-centro-lacerda/production.json").read_text(encoding="utf8"))
rep=json.loads((root/"docs/reports/blender/misericordia_profile_r30b41.json").read_text(encoding="utf8"))
dem=json.loads((root/"artifacts/roads/rondesp/misericordia_dem_profile.json").read_text(encoding="utf8"))
ground=scene.objects[contract["export"]["road_object"]]; road=scene.objects["R30A7 | ROAD | 803899198"]
pts=[road.matrix_world@Vector(p.co[:3]) for sp in road.data.splines for p in sp.points]
i0,i1=rep["source_node_profile_indices"][1],rep["source_node_profile_indices"][2]
segpts=pts[i0:i1+1]; p0=segpts[0].to_2d(); p1=segpts[-1].to_2d(); axis=p1-p0; L2=axis.length_squared
# current center surface from B41 helper minus its documented clearance.
clear=float(rep["clearance_m"])
ct=[];cz=[]
for p in segpts:
    t=max(0.0,min(1.0,(p.to_2d()-p0).dot(axis)/L2));ct.append(t);cz.append(float(p.z-clear))
# DEM target, linearly corrected so both topological endpoints are preserved.
dr=[x for x in dem["rows"] if x["segment"]==1 and x["dem_m"] is not None]
d0,d1=dr[0]["dem_m"],dr[-1]["dem_m"]; base0,base1=cz[0],cz[-1]
dt=[];dz=[]
for r in dr:
    t=float(r["fraction"]); target=float(r["dem_m"]+(base0-d0)*(1-t)+(base1-d1)*t)
    dt.append(t);dz.append(target)
def interp(xs,ys,t):
    j=bisect.bisect_right(xs,t)-1
    if j<0:return ys[0]
    if j>=len(xs)-1:return ys[-1]
    u=(t-xs[j])/(xs[j+1]-xs[j]);return ys[j]*(1-u)+ys[j+1]*u
def delta(t): return interp(dt,dz,t)-interp(ct,cz,t)
me=ground.data
road_slots={i for i,m in enumerate(me.materials) if m and m.name in contract["export"]["road_materials"]}
road_verts=set()
for poly in me.polygons:
    if poly.material_index in road_slots: road_verts.update(poly.vertices)
half_width=3.25
rows=[]; mats={}
for vid in sorted(road_verts):
    w=ground.matrix_world@me.vertices[vid].co; q=w.to_2d()-p0
    t=q.dot(axis)/L2
    lateral=abs(q.cross(axis.normalized()))
    if not (0<=t<=1 and lateral<=half_width): continue
    dd=delta(t)
    linked={me.polygons[p.index].material_index for p in me.vertices[vid].link_loops} if False else set()
    rows.append({"vertex":vid,"t":t,"lateral_m":lateral,"z_before":float(w.z),"delta_m":dd,"z_after_candidate":float(w.z+dd)})
# material attribution from polygons touching selected vertices
sel={r["vertex"] for r in rows}
for poly in me.polygons:
    if poly.material_index not in road_slots or not any(v in sel for v in poly.vertices):continue
    name=me.materials[poly.material_index].name if me.materials[poly.material_index] else str(poly.material_index)
    mats[name]=mats.get(name,0)+1
report={"schema":"boas/misericordia-surface-b42-plan-v1","source":src,"half_width_selection_m":half_width,
"selection_basis":"corredor apenas para seleção; largura/XY não serão alterados; 3.25 m cobre as estações autorais estáveis ~6.1 m",
"candidate_vertices":len(rows),"candidate_faces_by_material":mats,
"delta_summary":{"min_m":min(r["delta_m"] for r in rows),"max_m":max(r["delta_m"] for r in rows),"median_abs_m":sorted(abs(r["delta_m"]) for r in rows)[len(rows)//2]},
"target_profile":{"current_surface_start_z":base0,"current_surface_end_z":base1,"target_min_z":min(dz),"target_max_z":max(dz)},
"rows":rows,"geometry_changed":False,"saved_session":False}
(root/"artifacts/roads/rondesp/misericordia_surface_b42_plan.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps({k:report[k] for k in ("candidate_vertices","candidate_faces_by_material","delta_summary","target_profile")},ensure_ascii=False))
