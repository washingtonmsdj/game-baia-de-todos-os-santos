"""B42: densifica/triangula o proxy local da Misericórdia e reprojeta no pavimento corrigido."""
import bpy,bmesh,json,hashlib,runpy,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];scene=bpy.context.scene
registry_path=root/"world/areas/mvp-centro-lacerda/blender-revisions.json";reg=json.loads(registry_path.read_text(encoding="utf8"));src=reg["validation_source"]
assert src["revision"]=="R30B.42";assert Path(bpy.data.filepath).resolve()==(root/src["file"]).resolve()
rp=root/"docs/reports/blender/misericordia_surface_r30b42.json";report=json.loads(rp.read_text(encoding="utf8"))
c=json.loads((root/"world/areas/mvp-centro-lacerda/production.json").read_text(encoding="utf8"));wm=runpy.run_path(str(root/"automation/blender/component_fingerprint.py"))["world_matrix"]
g=scene.objects[c["export"]["road_object"]];p=scene.objects[c["export"]["terrain_proxy"]];road=scene.objects["R30A7 | ROAD | 803899198"]
pts=[wm(road)@Vector(x.co[:3]) for sp in road.data.splines for x in sp.points]
b41=json.loads((root/"docs/reports/blender/misericordia_profile_r30b41.json").read_text(encoding="utf8"));i0,i1=b41["source_node_profile_indices"][1],b41["source_node_profile_indices"][2]
p0,p1=pts[i0].to_2d(),pts[i1].to_2d();axis=p1-p0;L2=axis.length_squared;unit=axis.normalized();half=4.0
# Baseline topológico: nenhuma nova degeneração pode ser criada.
p.data.calc_loop_triangles();bxyz=np.array([list(v.co) for v in p.data.vertices],dtype=np.float64);btri=np.array([list(t.vertices) for t in p.data.loop_triangles],dtype=np.int32)
bareas=np.linalg.norm(np.cross(bxyz[btri[:,1]]-bxyz[btri[:,0]],bxyz[btri[:,2]]-bxyz[btri[:,0]]),axis=1)*.5
baseline_lt=int(np.sum(bareas<1e-10))
# Ground BVH/material.
g.data.calc_loop_triangles();gtris=list(g.data.loop_triangles);gtree=BVHTree.FromPolygons([wm(g)@v.co for v in g.data.vertices],[list(t.vertices) for t in gtris],all_triangles=True)
slots={i for i,m in enumerate(g.data.materials) if m and m.name in c["export"]["road_materials"]}
def ground_hit(world):
 hit,n,idx,_=gtree.ray_cast(Vector((world.x,world.y,world.z+8)),Vector((0,0,-1)),16)
 if hit is None or n.z<=.70 or gtris[idx].material_index not in slots:return None
 return hit
candidate=[]
for f in p.data.polygons:
 center=wm(p)@f.center;q=center.to_2d()-p0;t=q.dot(axis)/L2;lat=abs(q.cross(unit))
 if not(-.03<=t<=1.03 and lat<=half):continue
 if ground_hit(center) is not None:candidate.append(f.index)
assert candidate
before_v=len(p.data.vertices);before_f=len(p.data.polygons)
bm=bmesh.new();bm.from_mesh(p.data);bm.faces.ensure_lookup_table()
faces=[bm.faces[i] for i in candidate];edges={e for f in faces for e in f.edges}
res=bmesh.ops.subdivide_edges(bm,edges=list(edges),cuts=1,use_grid_fill=False)
region=set(f for f in faces if f.is_valid)
for item in res.get("geom_inner",[]):
 if isinstance(item,bmesh.types.BMFace) and item.is_valid:region.add(item)
 elif hasattr(item,"link_faces"):region.update(f for f in item.link_faces if f.is_valid)
region.update(f for e in edges if e.is_valid for f in e.link_faces if f.is_valid)
bmesh.ops.triangulate(bm,faces=list(region),quad_method='BEAUTY',ngon_method='BEAUTY')
pinv=wm(p).inverted();projected=0;max_move=0.0
for v in bm.verts:
 world=wm(p)@v.co;q=world.to_2d()-p0;t=q.dot(axis)/L2;lat=abs(q.cross(unit))
 if not(-.035<=t<=1.035 and lat<=half+.15):continue
 hit=ground_hit(world)
 if hit is None:continue
 move=abs(hit.z-world.z);max_move=max(max_move,move);world.z=hit.z;v.co=pinv@world;projected+=1
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(p.data);bm.free();p.data.update()
p.data.calc_loop_triangles();xyz=np.array([list(v.co) for v in p.data.vertices],dtype=np.float64);tri=np.array([list(t.vertices) for t in p.data.loop_triangles],dtype=np.int32)
areas=np.linalg.norm(np.cross(xyz[tri[:,1]]-xyz[tri[:,0]],xyz[tri[:,2]]-xyz[tri[:,0]]),axis=1)*.5
after_lt=int(np.sum(areas<1e-10));assert np.isfinite(xyz).all() and after_lt<=baseline_lt
after_v=len(p.data.vertices);after_f=len(p.data.polygons);assert after_v>before_v and after_f>before_f
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
sha=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()
report["source_after"]["sha256"]=sha
report["proxy_refinement"]={"method":"single-batch cuts=1 + local triangulation + vertical reprojection only on registered road material","candidate_faces":len(candidate),"candidate_edges":len(edges),"triangulated_region_faces":len(region),"cuts":1,"projected_vertices":projected,"vertices_before":before_v,"vertices_after":after_v,"faces_before":before_f,"faces_after":after_f,"maximum_projection_move_m":max_move,"corridor_half_width_selection_m":half,"degenerate_lt_1e10_before":baseline_lt,"degenerate_lt_1e10_after":after_lt}
report["pending"]=["Reabrir e repetir auditoria integral de 743 segmentos","Crossfall/envelope/física continuam gates separados","Largura real não verificada"]
rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
reg=json.loads(registry_path.read_text(encoding="utf8"));assert reg["authoring_source"]["revision"]=="R30B.41";reg["validation_source"]["sha256"]=sha
for row in reg["revisions"]:
 if row.get("revision")=="R30B.42":row["sha256"]=sha
registry_path.write_text(json.dumps(reg,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps({"sha256":sha,**report["proxy_refinement"]},ensure_ascii=False))
