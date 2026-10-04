"""Auditoria read-only de gameplay da expansão costeira B51."""
import bpy,json,math,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

root=Path(__file__).resolve().parents[2]; scene=bpy.context.scene
reg=json.loads((root/"world/areas/mvp-centro-lacerda/blender-revisions.json").read_text(encoding="utf8")); src=reg["validation_source"]
assert src["revision"]=="R30B.51"; assert Path(bpy.data.filepath).resolve()==(root/src["file"]).resolve()
report51=json.loads((root/"docs/reports/blender/coastal_gameplay_r30b51.json").read_text(encoding="utf8"))

visuals={
 "land":scene.objects["EXPANSAO B49 | terra emersa costeira | candidata"],
 "shore_transition":scene.objects["EXPANSAO B49 | faixa de transicao costeira | candidata"],
 "underwater_seabed":scene.objects["EXPANSAO B49 | fundo submerso DEM relativo | candidato"],
}
collisions={
 "land":scene.objects["B51 | COLLISION | land"],
 "shore_transition":scene.objects["B51 | COLLISION | shore_transition"],
 "underwater_seabed":scene.objects["B51 | COLLISION | underwater_seabed"],
}
# prova de igualdade visual/colisão
collision_checks=[]
for role,v in visuals.items():
    c=collisions[role]
    vv=np.array([tuple(x.co) for x in v.data.vertices],dtype=float); cv=np.array([tuple(x.co) for x in c.data.vertices],dtype=float)
    collision_checks.append({"role":role,"visual_vertices":len(vv),"collision_vertices":len(cv),"polygons_visual":len(v.data.polygons),"polygons_collision":len(c.data.polygons),"max_vertex_delta_m":float(np.max(np.linalg.norm(vv-cv,axis=1))) if len(vv)==len(cv) else None})

# BVHs de colisão B51 + proxy histórico na costura
objs=list(collisions.values())
old=scene.objects.get("R30A5 | COLLISION | terrain proxy")
if old: objs.append(old)
trees=[]
for ob in objs:
    me=ob.data; me.calc_loop_triangles()
    trees.append((ob,BVHTree.FromPolygons([ob.matrix_world@v.co for v in me.vertices],[list(t.vertices) for t in me.loop_triangles],all_triangles=True)))
def ch(x,y,z):
    best=None
    for ob,t in trees:
        p,n,i,d=t.ray_cast(Vector((x,y,z+2)),Vector((0,0,-1)),5)
        if p is not None and (best is None or p.z>best[0].z): best=(p,ob.name)
    return best

road_rows=[]; totals={"grade_review":0,"crossfall_review":0,"collision_visual_difference":0,"missing_collision":0}
for rec in report51["roads"]:
    for name in rec.get("objects",[]):
        ob=scene.objects[name]; verts=[ob.matrix_world@v.co for v in ob.data.vertices]
        assert len(verts)%2==0
        pairs=[(verts[i],verts[i+1]) for i in range(0,len(verts),2)]
        centers=[(a+b)*.5 for a,b in pairs]
        width=float(rec["gameplay_width_m"])
        banks=[abs(float((b.z-a.z)/max(width,1e-6))) for a,b in pairs]
        grades=[]
        for a,b in zip(centers,centers[1:]):
            d=(b-a).to_2d().length
            if d>1e-6: grades.append(abs(float((b.z-a.z)/d)))
        colldiffs=[]; missing=0
        for a,b in pairs:
            for p in (a,b):
                h=ch(p.x,p.y,p.z)
                if h is None: missing+=1
                else: colldiffs.append(abs(float(p.z-h[0].z)))
        mxg=max(grades,default=0.0); mxb=max(banks,default=0.0); mxc=max(colldiffs,default=999.0)
        issues=[]
        if mxg>.30: issues.append("grade_review"); totals["grade_review"]+=1
        if mxb>.15: issues.append("crossfall_review"); totals["crossfall_review"]+=1
        if mxc>.05: issues.append("collision_visual_difference"); totals["collision_visual_difference"]+=1
        if missing: issues.append("missing_collision"); totals["missing_collision"]+=1
        road_rows.append({"osm_way_id":rec["osm_way_id"],"name":name,"role":rec["role"],"access":rec.get("access"),"width_m":width,"samples":len(pairs),"max_abs_grade":mxg,"max_abs_crossfall":mxb,"max_collision_visual_difference_m":mxc,"missing_collision_hits":missing,"issues":issues})

missing_graph=[r["osm_way_id"] for r in report51["roads"] if not r.get("graph_object")]
out={
 "schema":"boas/coastal-gameplay-r30b51-audit-v1","source_reopened":True,
 "collision_geometry_checks":collision_checks,
 "roads":road_rows,"issue_counts":totals,
 "missing_graph_way_ids":missing_graph,
 "road_surface_objects":len(road_rows),
 "all_collision_geometry_identical":all(r["max_vertex_delta_m"]==0.0 and r["polygons_visual"]==r["polygons_collision"] for r in collision_checks),
 "thresholds":{"grade_review":0.30,"crossfall_review":0.15,"collision_visual_difference_m":0.05},
 "geometry_changed":False,"approved":False
}
(root/"docs/reports/blender/coastal_gameplay_r30b51_audit.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps({"collision_identical":out["all_collision_geometry_identical"],"issues":totals,"missing_graph":missing_graph,"worst_grade":max((r["max_abs_grade"],r["osm_way_id"],r["name"]) for r in road_rows),"worst_crossfall":max((r["max_abs_crossfall"],r["osm_way_id"],r["name"]) for r in road_rows),"max_collision_diff":max(r["max_collision_visual_difference_m"] for r in road_rows)},ensure_ascii=False))
