"""Auditoria final read-only da expansão jogável B54."""
import bpy,json,math,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

root=Path(__file__).resolve().parents[2]; scene=bpy.context.scene
reg=json.loads((root/"world/areas/mvp-centro-lacerda/blender-revisions.json").read_text(encoding="utf8")); src=reg["validation_source"]
assert src["revision"]=="R30B.54"; assert Path(bpy.data.filepath).resolve()==(root/src["file"]).resolve()
contract=json.loads((root/"world/areas/mvp-centro-lacerda/coastal-gameplay-b51.json").read_text(encoding="utf8"))
seam=json.loads((root/"artifacts/waterfront/coastal_seam_controls_b52.json").read_text(encoding="utf8"))

new=scene.objects["B54 | GAMEPLAY TERRAIN | costa + vias refinadas"]
newcol=scene.objects["B54 | COLLISION | costa + vias refinadas"]
official=scene.objects["MVP | terreno corrigido | colisão estática"]
officialcol=scene.objects["R30A5 | COLLISION | terrain proxy"]

def mk(ob):
    me=ob.data; me.calc_loop_triangles()
    return BVHTree.FromPolygons([ob.matrix_world@v.co for v in me.vertices],[list(t.vertices) for t in me.loop_triangles],all_triangles=True)
nt,nct,ot,oct=mk(new),mk(newcol),mk(official),mk(officialcol)
def ray(tree,x,y,z=200):
    return tree.ray_cast(Vector((x,y,z)),Vector((0,0,-1)),500)[0]
def union(tnew,told,x,y):
    a=ray(tnew,x,y); b=ray(told,x,y)
    if a is None:return b
    if b is None:return a
    return a if a.z>=b.z else b

# Visual/collision B54 idênticos.
vv=np.array([tuple(v.co) for v in new.data.vertices],dtype=float)
cv=np.array([tuple(v.co) for v in newcol.data.vertices],dtype=float)
collision_equal=(len(vv)==len(cv) and len(new.data.polygons)==len(newcol.data.polygons) and float(np.max(np.linalg.norm(vv-cv,axis=1)))==0.0)

bbox=contract["bbox_blender"]
rows=[]; counts={"grade_review":0,"crossfall_review":0,"collision_visual_difference":0,"support_missing":0}
for rec in contract["roads"]:
    pts=[Vector((float(x),float(y),0)) for x,y in rec["blender_xy"]]
    width=float(rec["gameplay_width_m"])
    centers=[]
    for si,(a,b) in enumerate(zip(pts,pts[1:])):
        d=b-a; L=d.to_2d().length
        if L<.01:continue
        n=Vector((-d.y/L,d.x/L)); count=max(1,math.ceil(L/2))
        for q in range(count+1):
            if si>0 and q==0:continue
            p=a+d*(q/count)
            # Audita apenas a expansão efetivamente gerada; suporte lateral pode vir do terreno oficial.
            center_new=ray(nt,p.x,p.y)
            if center_new is None:
                continue
            c=union(nt,ot,p.x,p.y)
            l=union(nt,ot,p.x+n.x*width/2,p.y+n.y*width/2)
            r=union(nt,ot,p.x-n.x*width/2,p.y-n.y*width/2)
            cc=union(nct,oct,p.x,p.y)
            centers.append({"p":p,"c":c,"l":l,"r":r,"cc":cc})
    grades=[];banks=[];coldiff=[];missing=0;prev=None
    for s in centers:
        c=s["c"]
        if prev is not None:
            dist=(c-prev).to_2d().length
            if dist>1e-6 and dist<4.5:
                grades.append(abs(float((c.z-prev.z)/dist)))
        prev=c
        if s["l"] is None or s["r"] is None:
            missing+=1
        else:
            banks.append(abs(float((s["r"].z-s["l"].z)/max(width,1e-6))))
        if s["cc"] is None:
            missing+=1
        else:
            coldiff.append(abs(float(c.z-s["cc"].z)))
    mg=max(grades,default=0.0); mb=max(banks,default=0.0); mc=max(coldiff,default=0.0)
    gl=.45 if rec["role"]=="walkable" else .30
    bl=.25 if rec["role"]=="walkable" else .15
    issues=[]
    if mg>gl:issues.append("grade_review");counts["grade_review"]+=1
    if mb>bl:issues.append("crossfall_review");counts["crossfall_review"]+=1
    if mc>.05:issues.append("collision_visual_difference");counts["collision_visual_difference"]+=1
    if missing:issues.append("support_missing");counts["support_missing"]+=1
    rows.append({"osm_way_id":rec["osm_way_id"],"name":rec["name"],"role":rec["role"],"sample_count":len(centers),"max_abs_grade":mg,"max_abs_crossfall":mb,"max_collision_visual_difference_m":mc,"support_missing_count":missing,"issues":issues})

# Validação da hard-boundary diretamente nos vértices salvos.
boundary={}
for v in new.data.vertices:
    p=new.matrix_world@v.co
    if abs(p.x+284.0)<1e-5:
        boundary[round(float(p.y),4)]=float(p.z)
seam_err=[]
for r in seam["rows"]:
    if abs(float(r["x"])+284.0)>1e-6:continue
    key=round(float(r["y"]),4)
    if key in boundary:
        seam_err.append(abs(boundary[key]-float(r["z"])))

graphs=[o for o in scene.objects if o.name.startswith("B54 | GRAPH |")]
report={
 "schema":"boas/coastal-platform-r30b54-audit-v1",
 "source_reopened":True,
 "visual_collision_geometry_identical":collision_equal,
 "visual_vertices":len(vv),"visual_faces":len(new.data.polygons),
 "collision_vertices":len(cv),"collision_faces":len(newcol.data.polygons),
 "roads":rows,"issue_counts":counts,
 "graph_objects":len(graphs),"graph_way_ids":sorted({int(o.get("boas_osm_way_id")) for o in graphs if o.get("boas_osm_way_id") is not None}),
 "hard_boundary_samples":len(seam_err),
 "hard_boundary_max_error_m":max(seam_err,default=None),
 "hard_boundary_median_error_m":float(np.median(seam_err)) if seam_err else None,
 "thresholds":{"vehicle_grade":.30,"vehicle_crossfall":.15,"walk_grade":.45,"walk_crossfall":.25,"collision_diff_m":.05},
 "scope":"Somente pontos cujo centro pertence à superfície B54; apoios laterais/collision podem usar a superfície oficial na costura.",
 "geometry_changed":False,
 "approved":False
}
(root/"docs/reports/blender/coastal_platform_r30b54_audit.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps({
 "collision_identical":collision_equal,
 "issues":counts,
 "graphs":len(graphs),
 "graph_way_ids":report["graph_way_ids"],
 "boundary_samples":len(seam_err),
 "boundary_max":report["hard_boundary_max_error_m"],
 "worst_grade":max((r["max_abs_grade"],r["osm_way_id"],r["name"]) for r in rows),
 "worst_crossfall":max((r["max_abs_crossfall"],r["osm_way_id"],r["name"]) for r in rows),
 "worst_collision":max((r["max_collision_visual_difference_m"],r["osm_way_id"],r["name"]) for r in rows)
},ensure_ascii=False))
