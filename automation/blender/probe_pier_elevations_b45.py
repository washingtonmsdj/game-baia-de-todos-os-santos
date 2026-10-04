"""Mede cotas e proximidade de controles para os quatro píeres OSM na B45, sem editar."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2]; scene=bpy.context.scene
reg=json.loads((root/"world/areas/mvp-centro-lacerda/blender-revisions.json").read_text(encoding="utf8")); src=reg["validation_source"]
assert src["revision"]=="R30B.45"; assert Path(bpy.data.filepath).resolve()==(root/src["file"]).resolve()
ref=json.loads((root/"artifacts/structural-pipeline/mvp-centro-lacerda/structural_reference.json").read_text(encoding="utf8"))
ids={1321682676,1321682677,1426173139,1426173140}; features=[f for f in ref["features"] if int(f.get("osm_id",-1)) in ids]

def mesh_tree(name):
 ob=scene.objects.get(name)
 if not ob or ob.type!="MESH": return None,None
 me=ob.data; me.calc_loop_triangles()
 return ob,BVHTree.FromPolygons([ob.matrix_world@v.co for v in me.vertices],[list(t.vertices) for t in me.loop_triangles],all_triangles=True)

controls={}
for name in [
 "CAIS | contenção costeira alinhada à linha de costa",
 "CIDADE BAIXA | piso entorno Mercado Modelo",
 "MVP | terreno corrigido | colisão estática",
 "BAÍA DE TODOS-OS-SANTOS | superfície e recorte costeiro",
]:
 ob,tree=mesh_tree(name)
 if ob: controls[name]=(ob,tree)

def ray(tree,x,y):
 p,n,i,d=tree.ray_cast(Vector((x,y,120)),Vector((0,0,-1)),200)
 return None if p is None else {"z":float(p.z),"normal_z":float(n.z)}

curve_points={}
for name in ["REF_WATERFRONT","Terminal Turístico Náutico da Bahia.001"]:
 ob=scene.objects.get(name); pts=[]
 if ob and ob.type=="CURVE":
  for sp in ob.data.splines:
   if sp.type=="BEZIER": pts += [ob.matrix_world@p.co for p in sp.bezier_points]
   else: pts += [ob.matrix_world@Vector(p.co[:3]) for p in sp.points]
 curve_points[name]=pts

rows=[]
for f in features:
 verts=[]
 for xy in f["blender_xy"]:
  x,y=map(float,xy); hits={name:ray(tree,x,y) for name,(ob,tree) in controls.items()}
  near={}
  for name,pts in curve_points.items():
   if pts:
    p=min(pts,key=lambda q:math.hypot(q.x-x,q.y-y))
    near[name]={"distance_xy_m":math.hypot(p.x-x,p.y-y),"point":[float(p.x),float(p.y),float(p.z)]}
  verts.append({"xy":[x,y],"hits":hits,"nearest_curve_controls":near})
 rows.append({"osm_id":f["osm_id"],"closed":f["closed"],"vertices":verts})
out=root/"artifacts/waterfront/pier_elevations_b45.json";out.write_text(json.dumps({"schema":"boas/pier-elevations-b45-v1","source":src,"rows":rows,"geometry_changed":False},ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps(rows,ensure_ascii=False))
