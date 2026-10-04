"""Valida topologia/costura da expansão costeira B48 sem editar."""
import bpy,json,math,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2]; scene=bpy.context.scene
reg=json.loads((root/"world/areas/mvp-centro-lacerda/blender-revisions.json").read_text(encoding="utf8")); src=reg["validation_source"]
assert src["revision"]=="R30B.48"; assert Path(bpy.data.filepath).resolve()==(root/src["file"]).resolve()
obj=scene.objects["EXPANSAO B48 | terreno costeiro DEM relativo | candidato"]
ground=scene.objects["MVP | terreno corrigido | colisão estática"]; water=scene.objects["BAÍA DE TODOS-OS-SANTOS | superfície e recorte costeiro"]
# degenerações
me=obj.data; me.calc_loop_triangles()
xyz=np.array([list(v.co) for v in me.vertices],dtype=float); tri=np.array([list(t.vertices) for t in me.loop_triangles],dtype=int)
areas=np.linalg.norm(np.cross(xyz[tri[:,1]]-xyz[tri[:,0]],xyz[tri[:,2]]-xyz[tri[:,0]]),axis=1)*.5
# costura contra terreno oficial
gme=ground.data; gme.calc_loop_triangles(); gtree=BVHTree.FromPolygons([ground.matrix_world@v.co for v in gme.vertices],[list(t.vertices) for t in gme.loop_triangles],all_triangles=True)
seam=[]; below_water=[]; wl=float(water.get("boas_water_level_m",water.location.z))
for v in me.vertices:
    p=obj.matrix_world@v.co
    if p.x>=-300:
        hit=gtree.ray_cast(Vector((p.x,p.y,200)),Vector((0,0,-1)),500)[0]
        if hit is not None: seam.append(abs(float(p.z-hit.z)))
    if p.z < wl-0.05: below_water.append([float(p.x),float(p.y),float(p.z)])
report={
 "schema":"boas/coastal-terrain-r30b48-validation-v1","source_reopened":True,
 "vertices":len(me.vertices),"polygons":len(me.polygons),"triangles":len(me.loop_triangles),
 "degenerate_triangles_lt_1e8":int(np.sum(areas<1e-8)),
 "seam_samples":len(seam),"seam_median_abs_error_m":None if not seam else float(np.median(seam)),
 "seam_max_abs_error_m":None if not seam else float(max(seam)),
 "water_level_m":wl,"vertices_below_water_minus_5cm":len(below_water),
 "below_water_examples":below_water[:20],"geometry_changed":False,"approved":False
}
(root/"docs/reports/blender/coastal_terrain_r30b48_validation.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps(report,ensure_ascii=False))
