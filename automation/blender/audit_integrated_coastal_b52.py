"""Auditoria read-only da superfície integrada costeira B52."""
import bpy,json,math,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

root=Path(__file__).resolve().parents[2]
scene=bpy.context.scene
reg=json.loads((root/"world/areas/mvp-centro-lacerda/blender-revisions.json").read_text(encoding="utf8"))
src=reg["validation_source"]
assert src["revision"]=="R30B.52"
assert Path(bpy.data.filepath).resolve()==(root/src["file"]).resolve()
contract=json.loads((root/"world/areas/mvp-centro-lacerda/coastal-gameplay-b51.json").read_text(encoding="utf8"))
seam=json.loads((root/"artifacts/waterfront/coastal_seam_controls_b52.json").read_text(encoding="utf8"))

visual=scene.objects["B52 | GAMEPLAY TERRAIN | costa integrada + vias"]
collision=scene.objects["B52 | COLLISION | costa integrada + vias"]
official=scene.objects["MVP | terreno corrigido | colisão estática"]

vv=np.array([tuple(v.co) for v in visual.data.vertices],dtype=float)
cv=np.array([tuple(v.co) for v in collision.data.vertices],dtype=float)
collision_equal=(len(vv)==len(cv) and len(visual.data.polygons)==len(collision.data.polygons) and float(np.max(np.linalg.norm(vv-cv,axis=1)))==0.0)

def tree(ob):
    me=ob.data; me.calc_loop_triangles()
    return BVHTree.FromPolygons([ob.matrix_world@v.co for v in me.vertices],[list(t.vertices) for t in me.loop_triangles],all_triangles=True)
vt=tree(visual); ct=tree(collision); ot=tree(official)

def ray(t,x,y,z=200):
    return t.ray_cast(Vector((x,y,z)),Vector((0,0,-1)),500)[0]

road_rows=[]
issues={"grade_review":0,"crossfall_review":0,"collision_visual_difference":0,"support_missing":0}
for rec in contract["roads"]:
    pts=[Vector((float(x),float(y),0)) for x,y in rec["blender_xy"]]
    width=float(rec["gameplay_width_m"])
    samples=[]
    for a,b in zip(pts,pts[1:]):
        d=b-a;L=d.to_2d().length
        if L<.01:continue
        n2=Vector((-d.y/L,d.x/L))
        count=max(1,math.ceil(L/2))
        for q in range(count+1):
            if samples and q==0:continue
            p=a+d*(q/count)
            c=ray(vt,p.x,p.y)
            if c is None:
                samples.append(None);continue
            l=ray(vt,p.x+n2.x*width/2,p.y+n2.y*width/2)
            r=ray(vt,p.x-n2.x*width/2,p.y-n2.y*width/2)
            cp=ray(ct,p.x,p.y)
            samples.append({"center":c,"left":l,"right":r,"collision":cp})
    grades=[];banks=[];coldiff=[];missing=0;prev=None
    for s in samples:
        if s is None:
            prev=None;continue
        c=s["center"]
        if prev is not None:
            d=(c-prev).to_2d().length
            if d>1e-6:grades.append(abs(float((c.z-prev.z)/d)))
        prev=c
        if s["left"] is None or s["right"] is None:
            missing+=1
        else:
            banks.append(abs(float((s["right"].z-s["left"].z)/max(width,1e-6))))
        if s["collision"] is None:
            missing+=1
        else:
            coldiff.append(abs(float(c.z-s["collision"].z)))
    maxg=max(grades,default=0.0);maxb=max(banks,default=0.0);maxc=max(coldiff,default=0.0)
    rissues=[]
    grade_limit=.45 if rec["role"]=="walkable" else .30
    cross_limit=.25 if rec["role"]=="walkable" else .15
    if maxg>grade_limit:rissues.append("grade_review");issues["grade_review"]+=1
    if maxb>cross_limit:rissues.append("crossfall_review");issues["crossfall_review"]+=1
    if maxc>.05:rissues.append("collision_visual_difference");issues["collision_visual_difference"]+=1
    if missing:rissues.append("support_missing");issues["support_missing"]+=1
    road_rows.append({
        "osm_way_id":rec["osm_way_id"],"name":rec["name"],"role":rec["role"],
        "width_m":width,"max_abs_grade":maxg,"max_abs_crossfall":maxb,
        "max_collision_visual_difference_m":maxc,"support_missing_count":missing,
        "issues":rissues
    })

# costura: apenas controles dentro da malha integrada.
seam_err=[]
for r in seam["rows"]:
    p=ray(vt,float(r["x"]),float(r["y"]))
    if p is not None:
        seam_err.append(abs(float(p.z)-float(r["z"])))

graphs=[o for o in scene.objects if o.name.startswith("B52 | GRAPH |")]
report={
 "schema":"boas/coastal-integrated-r30b52-audit-v1",
 "source_reopened":True,
 "visual_collision_geometry_identical":collision_equal,
 "visual_vertices":len(vv),"collision_vertices":len(cv),
 "visual_faces":len(visual.data.polygons),"collision_faces":len(collision.data.polygons),
 "roads":road_rows,
 "issue_counts":issues,
 "road_graph_objects":len(graphs),
 "road_graph_way_ids":sorted({int(o.get("boas_osm_way_id")) for o in graphs if o.get("boas_osm_way_id") is not None}),
 "seam_samples":len(seam_err),
 "seam_median_abs_error_m":None if not seam_err else float(np.median(seam_err)),
 "seam_max_abs_error_m":None if not seam_err else float(max(seam_err)),
 "thresholds":{"vehicle_grade":.30,"vehicle_crossfall":.15,"walk_grade":.45,"walk_crossfall":.25,"collision_diff_m":.05},
 "geometry_changed":False,
 "approved":False
}
(root/"docs/reports/blender/coastal_integrated_r30b52_audit.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps({
 "collision_identical":collision_equal,
 "issues":issues,
 "graphs":len(graphs),
 "graph_way_ids":report["road_graph_way_ids"],
 "seam_max":report["seam_max_abs_error_m"],
 "worst_grade":max((r["max_abs_grade"],r["osm_way_id"],r["name"]) for r in road_rows),
 "worst_crossfall":max((r["max_abs_crossfall"],r["osm_way_id"],r["name"]) for r in road_rows)
},ensure_ascii=False))
