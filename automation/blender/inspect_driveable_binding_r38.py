"""Inspeção pontual do binding de pista e collider; sem mutação de cena."""
import bpy,json,runpy,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2]
c=json.loads((root/'world/areas/mvp-centro-lacerda/production.json').read_text())
wm=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'))['world_matrix']
o=bpy.context.scene.objects.get('R30A7 | ROAD | 421206045')
r={'curve':None if o is None else {'type':o.type,'properties':dict(o.items()),'points':[[list(wm(o)@Vector(p.co[:3])) for p in s.points] for s in o.data.splines]}}
plan=json.loads((root/'artifacts/roads/r38/driveable_plan.json').read_text())
run=next(p for p in plan['paths'] if p['start_index']==57)
o=bpy.context.scene.objects[c['export']['terrain_proxy']];me=o.data;me.calc_loop_triangles()
a=np.empty(len(me.vertices)*3,dtype=np.float32);me.vertices.foreach_get('co',a);M=np.array(wm(o));xyz=a.reshape(-1,3)@M[:3,:3].T+M[:3,3]
a=np.empty(len(me.loop_triangles)*3,dtype=np.int32);me.loop_triangles.foreach_get('vertices',a)
tree=BVHTree.FromPolygons(xyz.tolist(),a.reshape(-1,3).tolist(),all_triangles=True)
errors=[]
for p in run['points']:
    x,y,z=p['point'];f=np.array(p['forward']);s=np.array([-f[1],f[0]])
    for u,v in [(-1.61,-.84),(-1.61,.84),(1.61,-.84),(1.61,.84),(0,0)]:
        q=np.array([x,y])+f*u+s*v;h=tree.ray_cast(Vector((*q,150)),Vector((0,0,-1)),350)[0]
        errors.append(None if h is None else abs(h.z-(z+u*p['grade']+v*p['bank'])))
r['verified_run_proxy']={'samples':len(errors),'missing':errors.count(None),'max_difference_from_wheel_plane':max(q for q in errors if q is not None)}
(root/'artifacts/roads/r38/binding_inspection.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(r,ensure_ascii=False))
