import bpy,json,numpy as np
from pathlib import Path
root=Path(__file__).resolve().parents[2]
c=json.loads((root/"world/areas/mvp-centro-lacerda/production.json").read_text(encoding="utf8"))
p=bpy.context.scene.objects[c["export"]["terrain_proxy"]];p.data.calc_loop_triangles()
xyz=np.array([list(v.co) for v in p.data.vertices],dtype=np.float64);tri=np.array([list(t.vertices) for t in p.data.loop_triangles],dtype=np.int32)
areas=np.linalg.norm(np.cross(xyz[tri[:,1]]-xyz[tri[:,0]],xyz[tri[:,2]]-xyz[tri[:,0]]),axis=1)*.5
print(json.dumps({"vertices":len(p.data.vertices),"faces":len(p.data.polygons),"triangles":len(tri),"min_area":float(areas.min()),"lt_1e10":int(np.sum(areas<1e-10)),"lt_1e9":int(np.sum(areas<1e-9)),"lt_1e8":int(np.sum(areas<1e-8)),"finite":bool(np.isfinite(xyz).all())},ensure_ascii=False))
