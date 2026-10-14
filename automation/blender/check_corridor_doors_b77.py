"""Verifica as portas animadas reais nas rotas previamente amostradas."""
import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2];out=ROOT/'docs/reports/blender/lacerda-corridor';scene=bpy.context.scene;frame=scene.frame_current
qa=json.loads((out/'walkability_candidate_b77.json').read_text(encoding='utf8'));report=json.loads((out/'scene_b77.json').read_text(encoding='utf8'));result=[]
for label,f in (('upper',report['timeline']['start']),('lower',report['timeline']['walk_out'])):
    scene.frame_set(f);dg=bpy.context.evaluated_depsgraph_get();trees=[]
    for ob in scene.objects:
        if ob.get('elevator_id')!=3 or ob.get('elevator_role') not in ('cabin_door','landing_door'):continue
        ev=ob.evaluated_get(dg);mesh=ev.to_mesh()
        try:
            mesh.calc_loop_triangles();trees.append((ob.name,BVHTree.FromPolygons([ev.matrix_world@v.co for v in mesh.vertices],[tuple(t.vertices) for t in mesh.loop_triangles],all_triangles=True)))
        finally:ev.to_mesh_clear()
    blocked=[]
    for index,p in enumerate(qa['routes'][label]['points']):
        for j in range(9):
            center=Vector((p[0],p[1],p[2]+.3+j*1.2/8))
            for name,tree in trees:
                hit=tree.find_nearest(center,.3)
                if hit[0] is not None and hit[3]<.285:blocked.append({'point':index,'door':name,'distance':hit[3]})
    result.append({'route':label,'frame':f,'points':len(qa['routes'][label]['points']),'blocked':blocked})
scene.frame_set(frame)
data={'cases':result,'passed':all(not c['blocked'] for c in result),'scope':'Portas reais abertas e poses de rota amostradas; não certifica folgas mecânicas/sweep integral ou interlocks da engine'}
(out/'doors_b77.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'passed':data['passed'],'blocked':[len(c['blocked']) for c in result]}));assert data['passed']
