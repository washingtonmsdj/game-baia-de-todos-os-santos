"""Mede diferenças ground/proxy por roda no nó 5436479156 da B44."""
import bpy,json,runpy
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2]; s=bpy.context.scene
assert Path(bpy.data.filepath).name=="salvador_lacerda_r30b44_proxy_misericordia.blend"
c=json.loads((root/"world/areas/mvp-centro-lacerda/production.json").read_text(encoding="utf8"))
audit=json.loads((root/"artifacts/roads/rondesp/rondesp_network_b44_candidate.json").read_text(encoding="utf8"))
wm=runpy.run_path(str(root/"automation/blender/component_fingerprint.py"))["world_matrix"]
ground=s.objects[c["export"]["road_object"]]; proxy=s.objects[c["export"]["terrain_proxy"]]
vehicle=next(v for v in json.loads((root/"world/vehicles/catalog.json").read_text(encoding="utf8"))["vehicles"] if v["asset_id"]=="vehicle-rondesp-pickup")["authoring_base"]
before=set(bpy.data.objects)
with bpy.data.libraries.load(str(root/vehicle["file"]),link=True) as (a,r): r.objects=[n for n in a.objects if "Eixo giro roda" in n]
contacts=[list(wm(o).translation) for o in r.objects]; assert len(contacts)==4
for ob in set(bpy.data.objects)-before:
    if not ob.users_scene:bpy.data.objects.remove(ob,do_unlink=True)
midy=(max(x[1] for x in contacts)+min(x[1] for x in contacts))/2
def tree(ob):
    me=ob.data; me.calc_loop_triangles(); tri=list(me.loop_triangles)
    return BVHTree.FromPolygons([wm(ob)@v.co for v in me.vertices],[list(t.vertices) for t in tri],all_triangles=True),tri
gt,gtl=tree(ground); pt,ptl=tree(proxy)
def hit(t,x,y,z):
    return t.ray_cast(Vector((x,y,z+2)),Vector((0,0,-1)),4)[0]
roads={int(o["boas_osm_way_id"]):o for o in s.objects if o.name.startswith("R30A7 | ROAD |") and "boas_osm_way_id" in o}
rows=[]
for eid in ["way-803899198-seg-0","way-803899198-seg-1"]:
    rec=next(x for x in audit["segments"] if x["edge_id"]==eid)
    sm=next(x for x in rec["samples"] if "collision_visual_difference" in x.get("issues",[]))
    q=Vector(sm["point"]); pts=[wm(roads[rec["osm_way_id"]])@Vector(p.co[:3]) for sp in roads[rec["osm_way_id"]].data.splines for p in sp.points]
    best=None
    for a,b in zip(pts,pts[1:]):
        d=(b-a).to_2d(); L2=d.length_squared
        if L2<1e-9:continue
        t=max(0,min(1,(q.to_2d()-a.to_2d()).dot(d)/L2)); p=a.to_2d()+d*t; dist=(q.to_2d()-p).length
        if best is None or dist<best[0]:best=(dist,d.normalized())
    f=best[1]; sx=Vector((-f.y,f.x)); center=hit(gt,q.x,q.y,q.z); vals=[]
    for wi,(px,py,pz) in enumerate(contacts):
        xy=q.to_2d()+sx*px-f*(py-midy); gp=hit(gt,xy.x,xy.y,center.z); pp=hit(pt,xy.x,xy.y,center.z)
        vals.append({"wheel":wi,"xy":[float(xy.x),float(xy.y)],"ground_z":None if gp is None else float(gp.z),"proxy_z":None if pp is None else float(pp.z),"diff_m":None if gp is None or pp is None else abs(float(pp.z-gp.z))})
    rows.append({"edge_id":eid,"sample_fraction":sm["fraction"],"wheels":vals})
out=root/"artifacts/roads/rondesp/misericordia_proxy_node_b44.json";out.write_text(json.dumps({"schema":"boas/misericordia-proxy-node-b44-v1","rows":rows,"geometry_changed":False},ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps(rows,ensure_ascii=False))
