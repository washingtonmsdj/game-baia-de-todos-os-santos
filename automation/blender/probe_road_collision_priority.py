"""Confere falhas do proxy em contatos do relatório atual, na camada local."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];scene=bpy.context.scene
c=json.loads((root/'world/areas/mvp-centro-lacerda/production.json').read_text(encoding='utf8'))
a=json.loads((root/'docs/reports/blender/rondesp_network_current.json').read_text(encoding='utf8'))
ground=scene.objects[c['export']['road_object']];proxy=scene.objects[c['export']['terrain_proxy']]
def tree(ob):
    ob.data.calc_loop_triangles();triangles=list(ob.data.loop_triangles)
    return BVHTree.FromPolygons([ob.matrix_world@v.co for v in ob.data.vertices],[list(t.vertices) for t in triangles],all_triangles=True),triangles
gt,triangles=tree(ground);pt,ptri=tree(proxy)
slots={i for i,m in enumerate(ground.data.materials) if m and m.name in c['export']['road_materials']}
points={};pending=[]
contacts=a['vehicle_contacts_asset_local'];mid=(min(p[1] for p in contacts)+max(p[1] for p in contacts))*.5
for row in a['segments']:
    if 'collision_visual_difference' not in row['issues']:continue
    samples=row['samples'];f=(Vector(samples[-1]['point'])-Vector(samples[0]['point'])).to_2d().normalized();side=Vector((-f.y,f.x))
    for sample in samples:
        if 'collision_visual_difference' not in sample['issues']:continue
        center=Vector(sample['point']);q=gt.ray_cast(center+Vector((0,0,2)),Vector((0,0,-1)),4)[0]
        if q is None:continue
        for px,py,_ in contacts:
            xy=center.to_2d()+side*px-f*(py-mid);probe=Vector((xy.x,xy.y,q.z))
            v,n,idx,_=gt.ray_cast(probe+Vector((0,0,.5)),Vector((0,0,-1)),1.)
            pv=pt.ray_cast(probe+Vector((0,0,.5)),Vector((0,0,-1)),1.)[0]
            if v is None or pv is None or n.z<.7 or triangles[idx].material_index not in slots:
                pending.append({'edge_id':row['edge_id'],'point':list(probe),'reason':'unsupported_or_ambiguous_layer'});continue
            error=abs(v.z-pv.z)
            if error>.05 and error<=.5:
                key=tuple(round(x,5) for x in v)
                points[key]={'point':list(v),'before_difference_m':error,'edge_id':row['edge_id'],'classification':'ERROR'}
            elif error>.5:pending.append({'edge_id':row['edge_id'],'point':list(v),'reason':'larger_difference_requires_layer_review','difference_m':error})
report={'source_before':a['source_before'],'targets':list(points.values()),'pending':pending,'method':'Contatos originais da auditoria; pavimento e proxy presentes na mesma faixa local ±0,5 m, normal Z>0,7. Não inclui outras camadas ou terreno sem material de pista.'}
(root/'artifacts/roads/rondesp/collision_priority_targets.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'safe_targets':len(points),'maximum_safe_difference_m':max((p['before_difference_m'] for p in points.values()),default=0),'pending':len(pending)}))
