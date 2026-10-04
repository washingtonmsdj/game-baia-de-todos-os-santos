"""R30B.42: corrige o vale vertical artificial da Misericórdia usando a forma relativa do DEM, preservando XY/largura."""
import bpy,json,math,bisect,hashlib,runpy,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];scene=bpy.context.scene
reg=json.loads((root/"world/areas/mvp-centro-lacerda/blender-revisions.json").read_text(encoding="utf8"));source=reg["authoring_source"]
assert source["revision"]=="R30B.41"; assert Path(bpy.data.filepath).resolve()==(root/source["file"]).resolve()
out=root/"blender/salvador_lacerda_r30b42_superficie_misericordia.blend";assert not out.exists()
contract=json.loads((root/"world/areas/mvp-centro-lacerda/production.json").read_text(encoding="utf8"))
b41=json.loads((root/"docs/reports/blender/misericordia_profile_r30b41.json").read_text(encoding="utf8"))
dem=json.loads((root/"artifacts/roads/rondesp/misericordia_dem_profile.json").read_text(encoding="utf8"))
ground=scene.objects[contract["export"]["road_object"]];proxy=scene.objects[contract["export"]["terrain_proxy"]];road=scene.objects["R30A7 | ROAD | 803899198"]
api=runpy.run_path(str(root/"automation/blender/component_fingerprint.py"));signature=api["signature"];wm=api["world_matrix"]
protected={o.name:signature(o) for o in scene.objects if o.type in {"MESH","CURVE","FONT"} and o not in {ground,proxy,road}}
before={"ground":signature(ground),"proxy":signature(proxy),"road":signature(road)}
# Perfis atual B41 e alvo DEM relativo.
pts=[wm(road)@Vector(p.co[:3]) for sp in road.data.splines for p in sp.points]
i0,i1=b41["source_node_profile_indices"][1],b41["source_node_profile_indices"][2];segpts=pts[i0:i1+1]
p0,p1=segpts[0].to_2d(),segpts[-1].to_2d();axis=p1-p0;L2=axis.length_squared;unit=axis.normalized()
clear=float(b41["clearance_m"]);ct=[];cz=[]
for p in segpts:
 t=max(0.0,min(1.0,(p.to_2d()-p0).dot(axis)/L2));ct.append(t);cz.append(float(p.z-clear))
dr=[x for x in dem["rows"] if x["segment"]==1 and x["dem_m"] is not None];d0,d1=dr[0]["dem_m"],dr[-1]["dem_m"];dt=[];target=[]
for r in dr:
 t=float(r["fraction"]);dt.append(t);target.append(float(r["dem_m"]+(cz[0]-d0)*(1-t)+(cz[-1]-d1)*t))
def interp(xs,ys,t):
 j=bisect.bisect_right(xs,t)-1
 if j<0:return ys[0]
 if j>=len(xs)-1:return ys[-1]
 u=(t-xs[j])/(xs[j+1]-xs[j]);return ys[j]*(1-u)+ys[j+1]*u
def delta(t):return interp(dt,target,t)-interp(ct,cz,t)
# Cópias de datablocks: B41 em disco permanece imutável.
ground.data=ground.data.copy();ground.data.name="MVP_TERRENO_B42_MISERICORDIA"
proxy.data=proxy.data.copy();proxy.data.name="R30A5_PROXY_B42_MISERICORDIA"
road.data=road.data.copy();road.data.name="R30A7_ROAD_803899198_B42"
# Move somente vértices já pertencentes a material de via dentro do corredor existente.
me=ground.data;road_slots={i for i,m in enumerate(me.materials) if m and m.name in contract["export"]["road_materials"]}
road_verts=set()
for poly in me.polygons:
 if poly.material_index in road_slots:road_verts.update(poly.vertices)
half_width=3.25;ginv=wm(ground).inverted();changed_ground=[];xy_error=0.0
for vid in sorted(road_verts):
 v=me.vertices[vid];w=wm(ground)@v.co;q=w.to_2d()-p0;t=q.dot(axis)/L2;lateral=abs(q.cross(unit))
 if not(0<=t<=1 and lateral<=half_width):continue
 before_xy=(w.x,w.y);dd=delta(t);w.z+=dd;v.co=ginv@w
 w2=wm(ground)@v.co;xy_error=max(xy_error,math.hypot(w2.x-before_xy[0],w2.y-before_xy[1]))
 changed_ground.append((vid,t,lateral,dd))
assert changed_ground and xy_error<1e-6
me.update()
# Atualiza o helper no mesmo perfil; nós e XY continuam idênticos.
flat=[p for sp in road.data.splines for p in sp.points];rinv=wm(road).inverted()
for idx in range(i0,i1+1):
 pworld=wm(road)@Vector(flat[idx].co[:3]);t=max(0.0,min(1.0,(pworld.to_2d()-p0).dot(axis)/L2))
 pworld.z=interp(dt,target,t)+clear;q=rinv@pworld;flat[idx].co=(*q,1.0)
road["boas_binding_revision"]="R30B.42";road["boas_surface_revision"]="R30B.42";road["boas_surface_method"]="DEM relative profile anchored to topological endpoints; XY preserved";road["boas_gameplay_approved"]=False
# Reprojeta apenas vértices do proxy cujo raio cai em pavimento dentro do corredor.
me.calc_loop_triangles();gverts=[wm(ground)@v.co for v in me.vertices];gtris=[list(t.vertices) for t in me.loop_triangles]
pm=[p.material_index for p in me.polygons];tm=[pm[t.polygon_index] for t in me.loop_triangles];gtree=BVHTree.FromPolygons(gverts,gtris,all_triangles=True)
pinv=wm(proxy).inverted();changed_proxy=[];max_proxy_delta=0.0
for v in proxy.data.vertices:
 w=wm(proxy)@v.co;q=w.to_2d()-p0;t=q.dot(axis)/L2;lateral=abs(q.cross(unit))
 if not(0<=t<=1 and lateral<=half_width+.35):continue
 hit,n,tri,_=gtree.ray_cast(Vector((w.x,w.y,w.z+8)),Vector((0,0,-1)),16)
 if hit is None or n.z<=.70 or tm[tri] not in road_slots:continue
 dd=float(hit.z-w.z);max_proxy_delta=max(max_proxy_delta,abs(dd));w.z=hit.z;v.co=pinv@w;changed_proxy.append(v.index)
proxy.data.update()
# Invariantes e sanidade geométrica.
changed_protected=[n for n,s in protected.items() if n not in scene.objects or signature(scene.objects[n])!=s];assert not changed_protected
newpts=[wm(road)@Vector(p.co[:3]) for sp in road.data.splines for p in sp.points][i0:i1+1]
grades=[]
for a,b in zip(newpts,newpts[1:]):
 d=(b.to_2d()-a.to_2d()).length
 if d>1e-6:grades.append(abs((b.z-a.z)/d))
assert max(grades)<.25
assert signature(ground)!=before["ground"] and signature(proxy)!=before["proxy"] and signature(road)!=before["road"]
scene["boas_authoring_revision"]="R30B.42";scene["boas_misericordia_surface_status"]="dem_relative_profile_candidate_gameplay_pending"
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);sha=hashlib.sha256(out.read_bytes()).hexdigest()
report={"schema":"boas/misericordia-surface-r30b42-v1","source_before":source,
"source_after":{"file":out.relative_to(root).as_posix(),"revision":"R30B.42","sha256":sha},"classification":"ERROR",
"osm_way_id":803899198,"method":"vertical correction of existing road-material vertices using bilinear DEM relative shape, linearly anchored to B41 topological endpoints",
"dem_capture_id":dem["capture_id"],"dem_sha256":dem["dem_sha256"],"half_width_selection_m":half_width,
"ground_vertices_changed":len(changed_ground),"proxy_vertices_reprojected":len(changed_proxy),"maximum_ground_raise_m":max(x[3] for x in changed_ground),"minimum_ground_delta_m":min(x[3] for x in changed_ground),
"maximum_proxy_adjustment_m":max_proxy_delta,"maximum_xy_error_m":xy_error,"helper_points_segment":len(newpts),"helper_max_abs_grade":max(grades),
"road_widths_changed":False,"source_xy_changed":False,"material_assignments_changed":False,"protected_components":len(protected),"protected_changes":changed_protected,
"runtime_exported":False,"approved":False,"pending":["Reabrir B42 e auditar 743 segmentos","Refinar proxy se contatos excederem tolerância","Crossfall/envelope/física continuam gates separados","Largura real não verificada"]}
(root/"docs/reports/blender/misericordia_surface_r30b42.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps({k:report[k] for k in ("source_after","ground_vertices_changed","proxy_vertices_reprojected","maximum_ground_raise_m","maximum_proxy_adjustment_m","helper_max_abs_grade","protected_changes")},ensure_ascii=False))
