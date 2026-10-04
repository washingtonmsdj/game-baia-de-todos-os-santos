"""Localiza o único crossfall residual da Rua Manoel Vitórino B54."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];scene=bpy.context.scene
assert Path(bpy.data.filepath).name=="salvador_lacerda_r30b54_plataformas_gameplay.blend"
contract=json.loads((root/"world/areas/mvp-centro-lacerda/coastal-gameplay-b51.json").read_text(encoding="utf8"))
rec=next(r for r in contract["roads"] if r["osm_way_id"]==456471269)
new=scene.objects["B54 | GAMEPLAY TERRAIN | costa + vias refinadas"];old=scene.objects["MVP | terreno corrigido | colisão estática"]
def mk(o):
 m=o.data;m.calc_loop_triangles()
 return BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[list(t.vertices) for t in m.loop_triangles],all_triangles=True)
nt,ot=mk(new),mk(old)
def ray(t,x,y):return t.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),500)[0]
def hit(x,y):
 a=ray(nt,x,y);b=ray(ot,x,y)
 if a is None:return (b,"official") if b else (None,None)
 if b is None:return a,"b54"
 return (a,"b54") if a.z>=b.z else (b,"official")
pts=[Vector((float(x),float(y),0)) for x,y in rec["blender_xy"]];w=float(rec["gameplay_width_m"]);rows=[]
for si,(a,b) in enumerate(zip(pts,pts[1:])):
 d=b-a;L=d.to_2d().length
 if L<.01:continue
 n=Vector((-d.y/L,d.x/L));count=max(1,math.ceil(L/2))
 for q in range(count+1):
  if si>0 and q==0:continue
  p=a+d*(q/count);cn,cs=hit(p.x,p.y)
  if cn is None or ray(nt,p.x,p.y) is None:continue
  l,ls=hit(p.x+n.x*w/2,p.y+n.y*w/2);r,rs=hit(p.x-n.x*w/2,p.y-n.y*w/2)
  if l and r:
   bank=abs(float((r.z-l.z)/w))
   if bank>.12:
    rows.append({"segment":si,"q":q,"xy":[float(p.x),float(p.y)],"center_z":float(cn.z),"center_source":cs,"left":[float(l.x),float(l.y),float(l.z),ls],"right":[float(r.x),float(r.y),float(r.z),rs],"crossfall":bank})
(root/"artifacts/waterfront/manoel_vitorino_crossfall_b54.json").write_text(json.dumps({"schema":"boas/manoel-vitorino-crossfall-b54-v1","rows":rows,"geometry_changed":False},ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps(rows,ensure_ascii=False))
