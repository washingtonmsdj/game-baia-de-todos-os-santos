"""R30B.45: corrige o último apoio divergente do proxy na Misericórdia."""
import bpy,bmesh,json,hashlib,runpy
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2]; s=bpy.context.scene
src=root/"blender/salvador_lacerda_r30b44_proxy_misericordia.blend"
assert Path(bpy.data.filepath).resolve()==src.resolve()
out=root/"blender/salvador_lacerda_r30b45_proxy_misericordia_final.blend"; assert not out.exists()
rep44=json.loads((root/"docs/reports/blender/misericordia_proxy_r30b44.json").read_text(encoding="utf8"))
assert hashlib.sha256(src.read_bytes()).hexdigest()==rep44["source_after"]["sha256"]
probe=json.loads((root/"artifacts/roads/rondesp/misericordia_proxy_node_b44.json").read_text(encoding="utf8"))
bad=[w for r in probe["rows"] for w in r["wheels"] if w.get("diff_m") and w["diff_m"]>.05]
# As duas ocorrências representam o mesmo apoio físico.
keys={(round(w["xy"][0],4),round(w["xy"][1],4),round(w["ground_z"],4)) for w in bad}; assert len(keys)==1
x,y,z=next(iter(keys)); target=Vector((x,y,z))
c=json.loads((root/"world/areas/mvp-centro-lacerda/production.json").read_text(encoding="utf8"))
api=runpy.run_path(str(root/"automation/blender/component_fingerprint.py")); sig=api["signature"]; wm=api["world_matrix"]
ground=s.objects[c["export"]["road_object"]]; proxy=s.objects[c["export"]["terrain_proxy"]]
ground_sig=sig(ground); road_sigs={o.name:sig(o) for o in s.objects if o.name.startswith("R30A7 | ROAD |")}
def tree(ob):
 me=ob.data; me.calc_loop_triangles(); tri=list(me.loop_triangles)
 return BVHTree.FromPolygons([wm(ob)@v.co for v in me.vertices],[list(t.vertices) for t in tri],all_triangles=True),tri
before_v=len(proxy.data.vertices); before_f=len(proxy.data.polygons)
pt,ptris=tree(proxy); hit,n,idx,_=pt.ray_cast(target+Vector((0,0,2)),Vector((0,0,-1)),4); assert hit is not None
before_error=abs(hit.z-target.z); assert before_error>.05
bm=bmesh.new(); bm.from_mesh(proxy.data); bm.faces.ensure_lookup_table(); face=bm.faces[ptris[idx].polygon_index]
local=wm(proxy).inverted()@target
# Preferir split exato se o alvo estiver numa aresta; caso contrário, poke local.
cands=[]
for e in face.edges:
 a,b=[v.co.to_2d() for v in e.verts]; d=b-a; t=max(0,min(1,(local.to_2d()-a).dot(d)/max(d.length_squared,1e-12))); q=a+d*t
 cands.append(((local.to_2d()-q).length,e,t))
dist,e,t=min(cands,key=lambda x:x[0]); mode=None
if dist<.003 and .0001<t<.9999:
 _,v=bmesh.utils.edge_split(e,e.verts[0],t); v.co=local; mode="edge_split"
else:
 created=bmesh.ops.poke(bm,faces=[face],offset=0,use_relative_offset=False); created["verts"][0].co=local; mode="poke"
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces)); bm.to_mesh(proxy.data); bm.free(); proxy.data.update()
assert sig(ground)==ground_sig
assert all(sig(s.objects[n])==v for n,v in road_sigs.items())
pt,_=tree(proxy); hit=pt.ray_cast(target+Vector((0,0,2)),Vector((0,0,-1)),4)[0]; assert hit is not None
after_error=abs(hit.z-target.z); assert after_error<.01
s["boas_authoring_revision"]="R30B.45"; s["boas_misericordia_proxy_status"]="final_local_proxy_support_candidate"
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
sha=hashlib.sha256(out.read_bytes()).hexdigest()
report={"schema":"boas/misericordia-proxy-r30b45-v1","source_before":rep44["source_after"],"source_after":{"file":out.relative_to(root).as_posix(),"revision":"R30B.45","sha256":sha},"classification":"ERROR","target_xy":[x,y],"target_ground_z":z,"before_error_m":before_error,"after_error_m":after_error,"mode":mode,"vertices_before":before_v,"vertices_after":len(proxy.data.vertices),"faces_before":before_f,"faces_after":len(proxy.data.polygons),"ground_changed":False,"road_helpers_changed":False,"visual_geometry_changed":False,"road_widths_changed":False,"runtime_exported":False,"approved":False,"pending":["Reabrir B45 e repetir auditoria integral de 743 segmentos","Crossfall/grade/largura real continuam gates separados"]}
(root/"docs/reports/blender/misericordia_proxy_r30b45.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps(report,ensure_ascii=False))
