"""Localiza falhas de grade/crossfall e sua superfície de origem na união B53."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];scene=bpy.context.scene
assert Path(bpy.data.filepath).name=="salvador_lacerda_r30b53_costura_gameplay.blend"
contract=json.loads((root/"world/areas/mvp-centro-lacerda/coastal-gameplay-b51.json").read_text(encoding="utf8"))
new=scene.objects["B53 | GAMEPLAY TERRAIN | costa + vias | hard boundary"]
old=scene.objects["MVP | terreno corrigido | colisão estática"]
def mk(o):
 m=o.data;m.calc_loop_triangles()
 return BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[list(t.vertices) for t in m.loop_triangles],all_triangles=True)
nt,ot=mk(new),mk(old)
def ray(t,x,y):
 return t.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),500)[0]
def union(x,y):
 a=ray(nt,x,y);b=ray(ot,x,y)
 if a is None:return (b,"official") if b else (None,None)
 if b is None:return a,"b53"
 return (a,"b53") if a.z>=b.z else (b,"official")
rows=[]
for rec in contract["roads"]:
 pts=[Vector((float(x),float(y),0)) for x,y in rec["blender_xy"]];width=float(rec["gameplay_width_m"]);prev=None;prev_src=None
 for a,b in zip(pts,pts[1:]):
  d=b-a;L=d.to_2d().length
  if L<.01:continue
  n=Vector((-d.y/L,d.x/L));count=max(1,math.ceil(L/2))
  for q in range(count+1):
   p=a+d*(q/count);c,src=union(p.x,p.y)
   if c is None:prev=None;continue
   l,ls=union(p.x+n.x*width/2,p.y+n.y*width/2);r,rs=union(p.x-n.x*width/2,p.y-n.y*width/2)
   grade=None if prev is None else abs(float((c.z-prev.z)/max((c-prev).to_2d().length,1e-6)))
   bank=None if l is None or r is None else abs(float((r.z-l.z)/width))
   gl=.45 if rec["role"]=="walkable" else .30;bl=.25 if rec["role"]=="walkable" else .15
   issues=[]
   if grade is not None and grade>gl:issues.append("grade_review")
   if bank is not None and bank>bl:issues.append("crossfall_review")
   if l is None or r is None:issues.append("support_missing")
   if issues:
    rows.append({"osm_way_id":rec["osm_way_id"],"name":rec["name"],"xy":[float(p.x),float(p.y)],"z":float(c.z),"source":src,"left_source":ls,"right_source":rs,"grade":grade,"crossfall":bank,"issues":issues})
   prev=c;prev_src=src
out={"schema":"boas/union-road-failures-b53-v1","rows":rows,"geometry_changed":False}
(root/"artifacts/waterfront/union_road_failures_b53.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
from collections import Counter
print(json.dumps({"count":len(rows),"by_source":Counter(r["source"] for r in rows),"by_way":Counter(str(r["osm_way_id"]) for r in rows),"worst":sorted(rows,key=lambda r:max(r["grade"] or 0,r["crossfall"] or 0),reverse=True)[:12]},default=dict,ensure_ascii=False))
