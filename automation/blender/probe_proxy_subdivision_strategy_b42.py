"""Testa subdivisão+triangulação local do proxy em mesh temporária."""
import bpy,bmesh,json,numpy as np,runpy
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];s=bpy.context.scene
c=json.loads((root/"world/areas/mvp-centro-lacerda/production.json").read_text(encoding="utf8"));wm=runpy.run_path(str(root/"automation/blender/component_fingerprint.py"))["world_matrix"]
g=s.objects[c["export"]["road_object"]];p=s.objects[c["export"]["terrain_proxy"]];road=s.objects["R30A7 | ROAD | 803899198"]
pts=[wm(road)@Vector(x.co[:3]) for sp in road.data.splines for x in sp.points];rep=json.loads((root/"docs/reports/blender/misericordia_profile_r30b41.json").read_text(encoding="utf8"));i0,i1=rep["source_node_profile_indices"][1],rep["source_node_profile_indices"][2]
p0,p1=pts[i0].to_2d(),pts[i1].to_2d();axis=p1-p0;L2=axis.length_squared;unit=axis.normalized()
g.data.calc_loop_triangles();gtris=list(g.data.loop_triangles);tree=BVHTree.FromPolygons([wm(g)@v.co for v in g.data.vertices],[list(t.vertices) for t in gtris],all_triangles=True);slots={i for i,m in enumerate(g.data.materials) if m and m.name in c["export"]["road_materials"]}
candidate=[]
for f in p.data.polygons:
 center=wm(p)@f.center;q=center.to_2d()-p0;t=q.dot(axis)/L2;lat=abs(q.cross(unit))
 if not(-.03<=t<=1.03 and lat<=4):continue
 h,n,idx,_=tree.ray_cast(Vector((center.x,center.y,center.z+8)),Vector((0,0,-1)),16)
 if h is not None and n.z>.70 and gtris[idx].material_index in slots:candidate.append(f.index)
bm=bmesh.new();bm.from_mesh(p.data);bm.faces.ensure_lookup_table();faces=[bm.faces[i] for i in candidate];edges={e for f in faces for e in f.edges}
res=bmesh.ops.subdivide_edges(bm,edges=list(edges),cuts=1,use_grid_fill=False)
region=set(f for f in faces if f.is_valid)
for item in res.get("geom_inner",[]):
 if isinstance(item,bmesh.types.BMFace) and item.is_valid:region.add(item)
 elif hasattr(item,"link_faces"):
  region.update(f for f in item.link_faces if f.is_valid)
region.update(f for e in edges if e.is_valid for f in e.link_faces if f.is_valid)
bmesh.ops.triangulate(bm,faces=list(region),quad_method='BEAUTY',ngon_method='BEAUTY')
tmp=bpy.data.meshes.new("TMP_B42_PROXY_SUBDIVISION_PROBE");bm.to_mesh(tmp);bm.free();tmp.calc_loop_triangles()
xyz=np.array([list(v.co) for v in tmp.vertices],dtype=np.float64);tri=np.array([list(t.vertices) for t in tmp.loop_triangles],dtype=np.int32);areas=np.linalg.norm(np.cross(xyz[tri[:,1]]-xyz[tri[:,0]],xyz[tri[:,2]]-xyz[tri[:,0]]),axis=1)*.5
out={"cuts":1,"candidate_faces":len(candidate),"candidate_edges":len(edges),"triangulated_region_faces":len(region),"vertices_after":len(tmp.vertices),"faces_after":len(tmp.polygons),"min_area":float(areas.min()),"lt_1e10":int(np.sum(areas<1e-10)),"lt_1e9":int(np.sum(areas<1e-9)),"finite":bool(np.isfinite(xyz).all())}
bpy.data.meshes.remove(tmp);print(json.dumps(out,ensure_ascii=False))
