"""Revalida todos os apoios após a limpeza do proxy, sem alterar o arquivo da cena."""
import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
rp=r/'docs/reports/blender/rondesp_driver_review_b39.json';report=json.loads(rp.read_text(encoding='utf8'))
audit=json.loads((r/'docs/reports/blender/rondesp_network_audit_b38.json').read_text(encoding='utf8'))
actor=s.objects['QA | RONDESP | veiculo na pista'];frame=s.frame_end
c=json.loads((r/'world/areas/mvp-centro-lacerda/production.json').read_text(encoding='utf8'))
terrain=s.objects[c['export']['road_object']];terrain.data.calc_loop_triangles()
ground=BVHTree.FromPolygons([terrain.matrix_world@v.co for v in terrain.data.vertices],[list(t.vertices) for t in terrain.data.loop_triangles],all_triangles=True)
proxy=s.objects[c['export']['terrain_proxy']];proxy.data.calc_loop_triangles()
ptree=BVHTree.FromPolygons([proxy.matrix_world@v.co for v in proxy.data.vertices],[list(t.vertices) for t in proxy.data.loop_triangles],all_triangles=True)
errors=[];proxy_errors=[];missing=0;maxstep=0;previous=None
for f in range(241,frame+1):
    s.frame_set(f);m=actor.matrix_world
    if previous is not None:maxstep=max(maxstep,(m.translation-previous).length)
    previous=m.translation.copy()
    for contact in audit['vehicle_contacts_asset_local']:
        p=m@Vector(contact);q=ground.ray_cast(p+Vector((0,0,.5)),Vector((0,0,-1)),1.)[0]
        pq=ptree.ray_cast(p+Vector((0,0,.5)),Vector((0,0,-1)),1.)[0]
        if q is None:missing+=1
        else:
            errors.append(abs(q.z-p.z))
            if pq is not None:proxy_errors.append(abs(q.z-pq.z))
assert not missing and max(errors)<.13,'Apoio interpolado não aceito; manter revisão pendente'
s.frame_set(s.frame_start)
report['continuous_preview']['verification_after_proxy_cleanup']={'wheel_samples':len(errors),'missing_support':missing,'maximum_wheel_plane_error_m':max(errors),'maximum_collision_visual_error_m':max(proxy_errors,default=None)}
assert len(proxy_errors)==len(errors),'Falta apoio no proxy após limpeza'
rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(report['continuous_preview']['verification_after_proxy_cleanup']))
