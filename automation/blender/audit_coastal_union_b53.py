"""Auditoria read-only da união gameplay B53 + terreno/proxy oficiais."""
import bpy,json,math,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

root=Path(__file__).resolve().parents[2];scene=bpy.context.scene
reg=json.loads((root/"world/areas/mvp-centro-lacerda/blender-revisions.json").read_text(encoding="utf8"));src=reg["validation_source"]
assert src["revision"]=="R30B.53";assert Path(bpy.data.filepath).resolve()==(root/src["file"]).resolve()
contract=json.loads((root/"world/areas/mvp-centro-lacerda/coastal-gameplay-b51.json").read_text(encoding="utf8"))
seam=json.loads((root/"artifacts/waterfront/coastal_seam_controls_b52.json").read_text(encoding="utf8"))

new=scene.objects["B53 | GAMEPLAY TERRAIN | costa + vias | hard boundary"]
newcol=scene.objects["B53 | COLLISION | costa + vias | hard boundary"]
old=scene.objects["MVP | terreno corrigido | colisão estática"]
oldcol=scene.objects.get("R30A5 | COLLISION | terrain proxy")
assert oldcol is not None

def mk(ob):
    me=ob.data;me.calc_loop_triangles()
    return BVHTree.FromPolygons([ob.matrix_world@v.co for v in me.vertices],[list(t.vertices) for t in me.loop_triangles],all_triangles=True)
nt,ot,nct,oct=mk(new),mk(old),mk(newcol),mk(oldcol)
def ray(t,x,y,z=200):
    return t.ray_cast(Vector((x,y,z)),Vector((0,0,-1)),500)[0]
def union(t1,t2,x,y):
    a=ray(t1,x,y);b=ray(t2,x,y)
    if a is None:return b
    if b is None:return a
    return a if a.z>=b.z else b

vv=np.array([tuple(v.co) for v in new.data.vertices]);cv=np.array([tuple(v.co) for v in newcol.data.vertices])
collision_identical=len(vv)==len(cv) and len(new.data.polygons)==len(newcol.data.polygons) and float(np.max(np.linalg.norm(vv-cv,axis=1)))==0.0

rows=[];counts={"grade_review":0,"crossfall_review":0,"collision_visual_difference":0,"support_missing":0}
for rec in contract["roads"]:
    pts=[Vector((float(x),float(y),0)) for x,y in rec["blender_xy"]];width=float(rec["gameplay_width_m"]);samples=[]
    for a,b in zip(pts,pts[1:]):
        d=b-a;L=d.to_2d().length
        if L<.01:continue
        n=Vector((-d.y/L,d.x/L));count=max(1,math.ceil(L/2))
        for q in range(count+1):
            if samples and q==0:continue
            p=a+d*(q/count)
            c=union(nt,ot,p.x,p.y)
            if c is None:samples.append(None);continue
            l=union(nt,ot,p.x+n.x*width/2,p.y+n.y*width/2)
            r=union(nt,ot,p.x-n.x*width/2,p.y-n.y*width/2)
            cc=union(nct,oct,p.x,p.y)
            samples.append((c,l,r,cc))
    grades=[];banks=[];cd=[];missing=0;prev=None
    for s in samples:
        if s is None:prev=None;continue
        c,l,r,cc=s
        if prev is not None:
            dist=(c-prev).to_2d().length
            if dist>1e-6:grades.append(abs(float((c.z-prev.z)/dist)))
        prev=c
        if l is None or r is None:missing+=1
        else:banks.append(abs(float((r.z-l.z)/max(width,1e-6))))
        if cc is None:missing+=1
        else:cd.append(abs(float(c.z-cc.z)))
    mg=max(grades,default=0);mb=max(banks,default=0);mc=max(cd,default=0)
    limg=.45 if rec["role"]=="walkable" else .30;limb=.25 if rec["role"]=="walkable" else .15
    iss=[]
    if mg>limg:iss.append("grade_review");counts["grade_review"]+=1
    if mb>limb:iss.append("crossfall_review");counts["crossfall_review"]+=1
    if mc>.05:iss.append("collision_visual_difference");counts["collision_visual_difference"]+=1
    if missing:iss.append("support_missing");counts["support_missing"]+=1
    rows.append({"osm_way_id":rec["osm_way_id"],"name":rec["name"],"role":rec["role"],"max_abs_grade":mg,"max_abs_crossfall":mb,"max_collision_visual_difference_m":mc,"support_missing_count":missing,"issues":iss})

# hard-boundary exata em X=-284.
se=[]
for r in seam["rows"]:
    if float(r["x"])!=-284.0:continue
    p=ray(nt,float(r["x"]),float(r["y"]))
    if p is not None:se.append(abs(float(p.z)-float(r["z"])))

graphs=[o for o in scene.objects if o.name.startswith("B53 | GRAPH |")]
report={
 "schema":"boas/coastal-union-r30b53-audit-v1","source_reopened":True,
 "new_visual_collision_identical":collision_identical,
 "roads":rows,"issue_counts":counts,
 "graph_objects":len(graphs),"graph_way_ids":sorted({int(o.get("boas_osm_way_id")) for o in graphs if o.get("boas_osm_way_id") is not None}),
 "hard_boundary_samples":len(se),"hard_boundary_max_error_m":max(se,default=None),"hard_boundary_median_error_m":float(np.median(se)) if se else None,
 "thresholds":{"vehicle_grade":.30,"vehicle_crossfall":.15,"walk_grade":.45,"walk_crossfall":.25,"collision_diff":.05},
 "geometry_changed":False,"approved":False
}
(root/"docs/reports/blender/coastal_union_r30b53_audit.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps({
 "collision_identical":collision_identical,"issues":counts,"graphs":len(graphs),
 "boundary_max":report["hard_boundary_max_error_m"],
 "worst_grade":max((r["max_abs_grade"],r["osm_way_id"],r["name"]) for r in rows),
 "worst_crossfall":max((r["max_abs_crossfall"],r["osm_way_id"],r["name"]) for r in rows),
 "worst_collision":max((r["max_collision_visual_difference_m"],r["osm_way_id"],r["name"]) for r in rows)
},ensure_ascii=False))
